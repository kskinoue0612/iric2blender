import bpy
from bpy.props import FloatVectorProperty, StringProperty
from . import N001_lib
# from . import material

# iricの計算結果をblenderのimport
class Import_OsmBuilding2blender(bpy.types.Operator):
    #ラベル名の宣言
    bl_idname = "object.import_osm_building2blender"
    bl_label = "2-1-2: OSMBuildingから建物データを読み込み"
    bl_description = "2-1-2: OSMBuildingから建物データを読み込み"
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
        name="Directory Path", # プロパティ名
        default="",            # デフォルト値
        maxlen=1024,           # 最大文字列長
        subtype='FILE_PATH',   # サブタイプ
        description="",        # 説明文
    )




    # 実行時イベント(保存先のフォルダの選択)
    def invoke(self, context, event):
        # ファイルエクスプローラーを表示する
        # 参考URL:https://docs.blender.org/api/current/bpy.types.WindowManager.html#bpy.types.WindowManager.fileselect_add
        self.report({'INFO'}, "保存先のフォルダを指定してください")
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


    #実行ファイル（選択しているオブジェクトの地形データをiricの点群csvに書き出し）
    def execute(self, context):
        import os
        from os import path
        import numpy as np

        # ファイルパスをフォルダパスとファイル名に分割する
        filepath_folder, filepath_name = os.path.split(self.filepath)
        # ファイルパスをフォルダ名の名称とファイル名の拡張子に分割する
        filepath_nameonly, filepath_ext = os.path.splitext(filepath_name)


        def make_verts_from_bldg_data(i):
            verts=[]
            z=0.
            for j in range(len(i)-1):
                verts.append([i[j][0],i[j][1],z])
            for j in range(len(i)-1):
                verts.append([i[j][0],i[j][1],i[j][2]])
            return verts


        def make_faces_from_bldg_data(i):
            faces=[]
            n_angle = int((len(i)-1)) #何角形か

            #上下の面
            faces.append([i for i in range(n_angle)]) #下
            faces.append([i+n_angle for i in range(n_angle)]) #上

            #側面
            for i in range(n_angle-1):
                faces.append([i,i+1,i+1+n_angle,i+n_angle])

            #最後の側面
            faces.append([n_angle-1,n_angle*2-1,n_angle,0])

            return faces


        def make_building():
            df = np.loadtxt(self.filepath, delimiter=',', skiprows=1, usecols=[0,1,2,3,4,5], dtype={'names': ('col1', 'col2', 'col3', 'col4', 'col5', 'col6'), 'formats': ('f8', 'f8', 'f8', 'f8', 'U50', 'f8')})

            #
            obj_list,bld_name = make_obj_list(df)

            #collection 作成
            col_name=str(f'bldg_osm')
            my_sub_coll = bpy.data.collections.new(col_name)
            bpy.context.scene.collection.children.link(my_sub_coll)

            j=0
            for i in obj_list:
                # obj_name=f"bdg_{j}_{df[j][4]}"
                obj_name=f"bdg_{j}_{bld_name[j]}"

                #建物objectの生成
                verts = make_verts_from_bldg_data(i)
                faces = make_faces_from_bldg_data(i)
                ob    = make_obj(verts,faces,obj_name)

                # 現在のシーンにコレクションをリンク
                my_sub_coll.objects.link(ob)
                j+=1


        def make_obj(verts,faces,obj_name):
            msh = bpy.data.meshes.new("cubemesh") #Meshデータの宣言
            msh.from_pydata(verts, [], faces) # 頂点座標と各面の頂点の情報でメッシュを作成
            cube_obj = bpy.data.objects.new(obj_name, msh) # メッシュデータでオブジェクトを作成
            return cube_obj


        def make_obj_list(df):
            same_obj=0
            obj2=[]
            obj3=[]
            min_building_h = 10
            bld_name=[]

            for i in range(len(df)):
                if same_obj!=int(df[i][0]):
                    same_obj=int(df[i][0])
                    obj3.append(obj2)
                    obj2=[]
                    bld_name.append(df[i][4])
                    # print("#####")

                if df[i][5] >= min_building_h:
                    obj1=[df[i][2],df[i][3],df[i][5]]
                elif df[i][5] < min_building_h:
                    obj1=[df[i][2],df[i][3],min_building_h]

                    obj2.append(obj1)
            return obj3,bld_name


        #######################
        #3d View 範囲の終了設定
        N001_lib.config_viewports()


        #objectの生成
        make_building()


        return {'FINISHED'}
