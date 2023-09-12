import bpy
from bpy.props import FloatVectorProperty, StringProperty
from . import material

# iricの計算結果をblenderのimport


class ImportResult2DH_DEM_iRIC2blender(bpy.types.Operator):
    # ラベル名の宣言
    bl_idname = "object.import_result_dem_iric2blender"
    bl_label = "3-1-4: Nays2dhの計算結果(河床変動)の読み込み"
    bl_description = "3-1-4: Nays2dhの計算結果(河床変動)の読み込み"
    bl_options = {'REGISTER', 'UNDO'}

    # ファイル指定のプロパティを定義する
    # filepath, filename, directory の名称のプロパティを用意しておくと
    # window_manager.fileselect_add 関数から情報が代入される
    filepath: StringProperty(
        name="File Path",      # プロパティ名
        default="",            # デフォルト値
        maxlen=1024,           # 最大文字列長
        subtype='FILE_PATH',   # サブタイプ
        description="",        # 説明文
    )
    filename: StringProperty(
        name="File Name",      # プロパティ名
        default="",            # デフォルト値
        maxlen=1024,           # 最大文字列長
        description="",        # 説明文
    )
    directory: StringProperty(
        name="Directory Path",  # プロパティ名
        default="",             # デフォルト値
        maxlen=1024,            # 最大文字列長
        subtype='FILE_PATH',    # サブタイプ
        description="",         # 説明文
    )

    # 実行時イベント(保存先のフォルダの選択)

    def invoke(self, context, event):
        # ファイルエクスプローラーを表示する
        # 参考URL:https://docs.blender.org/api/current/bpy.types.WindowManager.html#bpy.types.WindowManager.fileselect_add
        self.report({'INFO'}, "保存先のフォルダを指定してください")
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    # 実行ファイル（選択しているオブジェクトの地形データをiricの点群csvに書き出し）
    def execute(self, context):

        active_obj = context.active_object
        import os
        from os import path
        import numpy as np

        # ファイルパスをフォルダパスとファイル名に分割する
        filepath_folder, filepath_name = os.path.split(self.filepath)
        # ファイルパスをフォルダ名の名称とファイル名の拡張子に分割する
        filepath_nameonly, filepath_ext = os.path.splitext(filepath_name)

        def config_viewports():
            D = bpy.data
            CLIP_END = 100000

            screens = D.screens
            viewareas = [area for screen in screens for area in screen.areas if area.type == 'VIEW_3D']
            for area in viewareas:
                # area.spaces.active.overlay.grid_scale = SCALE_LENGTH
                area.spaces.active.clip_end = CLIP_END

        def return_max_file(path):
            import os
            # path="in"
            max_file = 0
            files = os.listdir(path)
            files_file = [f for f in files if os.path.isfile(os.path.join(path, f))]
            for file_name in files_file:
                max_file += file_name.count("Result_")
            return max_file

        def make_verts_numpy(readfile):
            # ３行目以降を読み込みdfとする
            # df = np.loadtxt(readfile, delimiter=',',skiprows=3)
            df = np.loadtxt(readfile, delimiter=',', skiprows=3, usecols=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
            return df

        def read_MI_MJ(readfile):
            # ファイルの1行目を読み込み、コンマで分離
            with open(readfile) as f:
                firstline = f.readlines()[1].split(",")
            MI = int(firstline[0])
            MJ = int(firstline[1])
            return MI, MJ

        # vertsの作成
        def make_vert(MI, MJ, df, df_row_n, obj_scale):
            """ df_row_n = 4:Depth(Max), 5:Depth, 6:Elevation, 7:WaterSurfaceElevation """
            verts = []

            k = 1
            min_z = df[1][df_row_n]
            for j in range(MJ):
                for i in range(MI):
                    k = i+MI*j
                    if df[k][df_row_n] < min_z:
                        min_z = df[k][df_row_n]

            k = 1
            for j in range(MJ):
                for i in range(MI):
                    k = i+MI*j
                    # 原点補正なし
                    verts.append([df[k][2]*obj_scale, df[k][3]*obj_scale, df[k][df_row_n]*obj_scale])
                    # 原点補正あり(原点に近づける)
                    # verts.append([(df[k][2]-df[1][2])*obj_scale,(df[k][3]-df[1][3])*obj_scale,(df[k][df_row_n]-min_z)*obj_scale])

            # print(verts)
            return verts

        def make_obj(verts, faces, readfile, obj_name):
            msh = bpy.data.meshes.new("cubemesh")  # Meshデータの宣言
            msh.from_pydata(verts, [], faces)  # 頂点座標と各面の頂点の情報でメッシュを作成
            cube_obj = bpy.data.objects.new(obj_name, msh)  # メッシュデータでオブジェクトを作成

            return cube_obj

        def set_faces(MI, MJ):
            faces = []
            k = 1
            for j in range(MJ-1):
                for i in range(MI-1):
                    k = i+MI*j
                    # print([k,k+1,k+1+MI,k+MI],k,i,j)
                    faces.append([k, k+1, k+1+MI, k+MI])
            return faces

        def make_ojb_each_files(readfile, df_row_n, obj_name):
            df = make_verts_numpy(readfile)
            MI, MJ = read_MI_MJ(readfile)

            # set faces & verts
            verts = make_vert(MI, MJ, df, df_row_n, obj_scale=1)
            # verts = make_vert(MI,MJ,df,df_row_n,obj_scale=0.01)
            # verts = make_vert_depth(MI,MJ,df,df_row_n,obj_scale=0.01)

            faces = set_faces(MI, MJ)
            # faces=set_faces_depth(MI,MJ,df)

            cube_obj = make_obj(verts, faces, readfile, obj_name)
            # local_loc = cube_obj.matrix_world.inverted() @ Vector((1,5,3)) #座標の移動

            return cube_obj

        def make_elecation_ob(filepath_folder):
            # iricのcsvファイル(地盤データ:elevation)からオブジェクトを作成
            # ob1 = make_ojb_each_files(readfile=f'{filepath_folder}/Result_{i}.csv',df_row_n=6,obj_name=f"cube_{i}_Elevation")
            ob1 = make_ojb_each_files(readfile=f'{filepath_folder}/Result_{i}.csv', df_row_n=5, obj_name=f"cube_{i}_Elevation")

            # 地盤データ用のマテリアルをセット
            mat_el = material.materials_elevation()

            # 地盤データから生成したオブジェクトと地盤データ用のマテリアルを統合
            ob1.data.materials.append(mat_el)

            # モディファイヤーを追加。今回はサブディビジョンサーフェスを適応。（ポリゴンが細分化されて表面がなめらかになる）
            ob1.modifiers.new("subd", type='SUBSURF')
            ob1.modifiers['subd'].levels = 3

            # 現在のシーンにコレクションをリンク
            my_sub_coll.objects.link(ob1)

            return ob1

        # ファイル数の確認
        max_file = return_max_file(path=filepath_folder)
        max_file = max_file - 1

        self.report({'INFO'}, str("読み込みファイル数:")+str(max_file))

        # 3d View 範囲の終了設定
        config_viewports()

        # フレーム数設定
        frame_number_input = 10

        # フレームのスタートとエンドを設定する
        bpy.context.scene.frame_start = 0
        bpy.context.scene.frame_end = (max_file-2)*frame_number_input

        l_sub_coll = []
        l_sub_coll2 = []

        for i in range(1, max_file):

            #####
            # 新しいCollrectionを作成
            col_name = str(f'Result_{i}')
            my_sub_coll = bpy.data.collections.new(col_name)
            bpy.context.scene.collection.children.link(my_sub_coll)
            l_sub_coll.append(my_sub_coll)

            # elevation
            ob1 = make_elecation_ob(filepath_folder)

            #####
            # watersurface
            # ob2 = watersurface_make_ob(filepath_folder)

            # 頂点カラー
            # ob2 = add_color(ob2)

        #######
        frame_number = 0

        # 処理を50回繰り返す
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

            print("####", tt)

            # オブジェクトを順番に表示
            if j < max_file - 1:
                if frame_number >= 0*(j-1) and frame_number < 20*(j):
                    for ob in l_sub_coll[j].objects:

                        bpy.context.scene.frame_set(frame_number)
                        ob.hide_viewport = False
                        ob.hide_render = False
                        ob.keyframe_insert(data_path="hide_viewport", index=-1)
                        ob.keyframe_insert(data_path="hide_render", index=-1)

            j += 1

            frame_number += frame_number_input

        return {'FINISHED'}
