import bpy
import numpy as np
from . import material
import os

# viewpointの設定


def config_viewports():
    D = bpy.data
    CLIP_END = 100000

    screens = D.screens
    viewareas = [area for screen in screens for area in screen.areas if area.type == 'VIEW_3D']
    for area in viewareas:
        # area.spaces.active.overlay.grid_scale = SCALE_LENGTH
        area.spaces.active.clip_end = CLIP_END


# ファイルの読み込み
def read_file(readfile, usecols):
    # ３行目以降を読み込みdfとする
    df = np.loadtxt(readfile, delimiter=',', skiprows=3, usecols=usecols)
    # df = np.loadtxt(readfile, delimiter=',',skiprows=3, usecols=[0,1,2,3,4,5,6,7,8,9,10,11,12])

    # １行目よりMI,MJを取得
    with open(readfile) as f:
        firstline = f.readlines()[1].split(",")
    MI = int(firstline[0])
    MJ = int(firstline[1])
    return df, MI, MJ


def setting_color_contor():
    num_color = 21
    color_max_depth = bpy.context.scene.max_depth_prop_float
    color_min_depth = bpy.context.scene.min_depth_prop_float
    color_set = [num_color, color_max_depth, color_min_depth]
    return color_set


def delete_collection_and_objects(name):
    # コレクションを検索
    coll = bpy.data.collections.get(name)
    if coll is not None:
        # コレクション内のオブジェクトを再帰的に処理
        for obj in coll.objects:
            # オブジェクトを削除
            bpy.data.objects.remove(obj, do_unlink=True)
        # コレクションを削除
        bpy.data.collections.remove(coll, do_unlink=True)


# 選択したオブジェクト視点をあわせる
def framein_to_selected_object(obj_name):
    # 3Dビューをアクティブにする
    bpy.context.window.scene = bpy.data.scenes['Scene']
    bpy.context.area.type = 'VIEW_3D'

    # # 視点をトップビューに変更する
    # bpy.ops.view3d.view_axis(type='TOP')

    # オブジェクトを選択する
    obj = bpy.data.objects[obj_name]
    obj.select_set(True)

    # ローカルビューに移行する
    bpy.ops.view3d.localview()


# iRICデータ(CSV)からのメッシュオブジェクトの生成
class Make_mesh_object:
    def __init__(self, df, MI, MJ, obj_name, obj_scale):
        self.df = df
        self.MI = MI
        self.MJ = MJ
        self.obj_name = obj_name
        self.obj_scale = obj_scale

    # 頂点(vert)の生成
    def set_vert(self):
        verts = []
        min_z = min(self.df[i][2] for i in range(self.MI*self.MJ))

        for k in range(self.MI*self.MJ):
            # verts.append([self.df[k][0]*self.obj_scale, self.df[k][1]*self.obj_scale, self.df[k][2]*self.obj_scale - min_z*self.obj_scale])
            x = self.df[k][0]*self.obj_scale
            y = self.df[k][1]*self.obj_scale
            # z = self.df[k][2]*self.obj_scale - min_z*self.obj_scale
            z = self.df[k][2]*self.obj_scale
            verts.append([x, y, z])

        return verts

    # 面(faces)の生成
    def set_faces(self):
        faces = []
        k = 1
        for j in range(self.MJ-1):
            for i in range(self.MI-1):
                k = i + self.MI*j
                faces.append([k, k+1, k+1+self.MI, k+self.MI])

        return faces

    # メッシュオブジェクトの生成
    def make_obj_each_files(self):
        verts = self.set_vert()
        faces = self.set_faces()
        msh = bpy.data.meshes.new(self.obj_name)
        msh.from_pydata(verts, [], faces)
        ob = bpy.data.objects.new(self.obj_name, msh)
        bpy.context.scene.collection.objects.link(ob)
        return ob


def return_max_file(path):
    import os

    max_file = 0
    files = os.listdir(path)
    files_file = [f for f in files if os.path.isfile(os.path.join(path, f))]
    for file_name in files_file:
        max_file += file_name.count("Result_")
    return max_file


########

# iRICデータ(CSV)からのメッシュオブジェクトの生成
class Make_mesh_object_depth_velocity:
    def __init__(self, df, MI, MJ, obj_name, obj_scale, min_depth):
        self.df = df
        # df=[x,y,z,depth]
        self.MI = MI
        self.MJ = MJ
        self.obj_name = obj_name
        self.obj_scale = obj_scale
        self.min_depth = min_depth

    # 頂点(vert)の生成
    def set_vert_depth(self):
        verts = []
        min_z = min(self.df[i][2] for i in range(self.MI*self.MJ))

        for k in range(self.MI*self.MJ):
            # verts.append([self.df[k][0]*self.obj_scale, self.df[k][1]*self.obj_scale, self.df[k][2]*self.obj_scale - min_z*self.obj_scale])
            x = self.df[k][0]*self.obj_scale
            y = self.df[k][1]*self.obj_scale
            z = (self.df[k][2] + self.df[k][3])*self.obj_scale
            verts.append([x, y, z])

        return verts

    # 面(faces)の生成
    # def set_faces_depth(self):
    def set_faces_velocity(self):
        faces = []
        faces_depth = []
        faces_velocity = []

        # min_depth = 0.1

        k = 1
        for j in range(self.MJ-1):
            for i in range(self.MI-1):
                k = i + self.MI*j
                if self.df[k][2] > self.min_depth:
                    faces.append([k, k+1, k+1+self.MI, k+self.MI])
                    faces_depth.append([k, k+1, k+1+self.MI, k+self.MI, self.df[k][2]])
                    faces_velocity.append([k, k+1, k+1+self.MI, k+self.MI, self.df[k][4]])

        return faces, faces_depth, faces_velocity

    # メッシュオブジェクトの生成
    def make_obj_each_files_depth_velocity(self):
        verts = self.set_vert_depth()
        # faces,faces_depth = self.set_faces_depth()
        faces, faces_depth, faces_velocity = self.set_faces_velocity()
        msh = bpy.data.meshes.new(self.obj_name)
        msh.from_pydata(verts, [], faces)
        ob = bpy.data.objects.new(self.obj_name, msh)
        bpy.context.scene.collection.objects.link(ob)

        return ob, faces_depth, faces_velocity


class Make_WaterSurface_depth_velocity_from_iRIC_result:

    def __init__(self, df_col_list, usecols, filepath_folder, mat_list, color_set, result_type):
        self.df_col_list = df_col_list
        self.usecols = usecols
        self.filepath_folder = filepath_folder
        self.mat_list = mat_list
        self.color_set = color_set
        self.result_type = result_type

    def read_file(self, readfile, usecols):
        df = np.loadtxt(readfile, delimiter=',', skiprows=3, usecols=usecols)
        with open(readfile) as f:
            firstline = f.readlines()[1].split(",")
        MI = int(firstline[0])
        MJ = int(firstline[1])
        return df, MI, MJ

    def return_max_file(self, path):
        max_file = 0
        files = os.listdir(path)
        files_file = [f for f in files if os.path.isfile(os.path.join(path, f))]
        for file_name in files_file:
            max_file += file_name.count("Result_")
        return max_file

    def display_on_off(self, max_file, l_sub_coll, frame_number_input):
        frame_number = 0
        j = 1
        for tt in range(0, max_file):
            for i in range(len(l_sub_coll)):

                # オブジェクトを非表示
                for ob in l_sub_coll[i].objects:
                    bpy.context.scene.frame_set(frame_number)
                    ob.hide_viewport = True
                    ob.hide_render = True
                    ob.keyframe_insert(data_path="hide_viewport", index=-1)
                    ob.keyframe_insert(data_path="hide_render", index=-1)

            # オブジェクトを順番に表示
            if j < max_file - 1:
                if frame_number >= 0 * (j - 1) and frame_number < 20 * (j):
                    for ob in l_sub_coll[j].objects:
                        bpy.context.scene.frame_set(frame_number)
                        ob.hide_viewport = False
                        ob.hide_render = False
                        ob.keyframe_insert(data_path="hide_viewport", index=-1)
                        ob.keyframe_insert(data_path="hide_render", index=-1)
            j += 1
            frame_number += frame_number_input

    def watersurface_make_ob_color(self, readfile, obj_name, my_sub_coll):
        df, MI, MJ = self.read_file(readfile, self.usecols)
        df = df[:, self.df_col_list]

        # クラスの呼び出し
        ob = Make_mesh_object_depth_velocity(df, MI, MJ, obj_name, obj_scale=1, min_depth=0.1)

        obj, faces_depth, faces_velocity = ob.make_obj_each_files_depth_velocity()

        # カラーコンター用のマテリアルの作成
        if self.result_type == "depth":
            material.color_mesh(obj, faces_depth, self.mat_list, self.color_set)

        elif self.result_type == "velocity":
            material.color_mesh(obj, faces_velocity, self.mat_list, self.color_set)

        # モディファイア設定
        material.mofifiers_on(obj)

        # voronoi設定
        # material.voronoi_on(obj)

        # 現在のシーンにコレクションをリンク
        my_sub_coll.objects.link(obj)

    def create_mesh_result(self):
        # フレーム数設定
        frame_number_input = 10

        # ファイル数の確認
        max_file = self.return_max_file(self.filepath_folder)
        max_file = max_file - 1

        # フレームのスタートとエンドを設定する
        bpy.context.scene.frame_start = 0
        bpy.context.scene.frame_end = (max_file - 2) * frame_number_input

        # タイムステップ毎(ファイル毎)に読み込み
        l_sub_coll = []
        for i in range(1, max_file):
            # 新しいCollrectionを作成
            col_name = f'Result_{i}'
            my_sub_coll = bpy.data.collections.new(col_name)
            bpy.context.scene.collection.children.link(my_sub_coll)
            l_sub_coll.append(my_sub_coll)

            # 水深メッシュ（カラーコンター）の作成
            obj_name = f"{i}_iRIC_result"
            readfile = f'{self.filepath_folder}/Result_{i}.csv'
            # bpy.data.scenes['Scene'].collection.objects.unlink(bpy.data.objects['2_iRIC_result'])

            # self.watersurface_make_ob_color(readfile, self.mat_list, self.color_set, self.df_col_list, self.usecols, obj_name, my_sub_coll)
            self.watersurface_make_ob_color(readfile, obj_name, my_sub_coll)
            bpy.data.scenes['Scene'].collection.objects.unlink(bpy.data.objects[obj_name])

        # 表示・非表示の設定
        self.display_on_off(max_file, l_sub_coll, frame_number_input)
