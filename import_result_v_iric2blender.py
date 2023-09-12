import bpy
from bpy.props import FloatVectorProperty, StringProperty

class ImportResult_velocity_iRIC2blender(bpy.types.Operator):
    #ラベル名の宣言
    bl_idname = "object.import_result_velocity_iric2blender"
    bl_label = "iRICの計算結果より流速ベクトルをblenderに読み込み"
    bl_description = "iRICの計算結果より流速ベクトルをblenderに読み込み"
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
                max_file+=file_name.count("Result_")
            return max_file


        def make_verts_numpy(readfile):
            #３行目以降を読み込みdfとする
            # df = np.loadtxt(readfile, delimiter=',',skiprows=3)
            df = np.loadtxt(readfile, delimiter=',',skiprows=3, usecols=[0,1,2,3,4,5,6,7,8,9,10,11,12])
            return df

        def read_MI_MJ(readfile):
            #ファイルの1行目を読み込み、コンマで分離
            with open(readfile) as f:
                firstline = f.readlines()[1].split(",")
            MI=int(firstline[0])
            MJ=int(firstline[1])
            return MI,MJ


        def add_vector(readfile,obj_name,t,mabiki):
            #collection 作成
            l_sub_coll = []
            col_name=str(f'Result_vector_{t}')
            my_sub_coll = bpy.data.collections.new(col_name)
            bpy.context.scene.collection.children.link(my_sub_coll)
            l_sub_coll.append(my_sub_coll)

            df = make_verts_numpy(readfile)
            MI,MJ = read_MI_MJ(readfile)

            import math
            k = 0

            for i in range(1,MI,mabiki):
                for j in range(1,MJ,mabiki):
                    # print(i,j,k,mabiki)
                    try:
                        vx = df[k][2]
                        vy = df[k][3]
                        vz = df[k][7]
                        vvx = df[k][10]
                        vvy = df[k][11]


                        v = math.sqrt(vvx**2+vvy**2)
                        # print(i,j,df[k][2],df[k][3],df[k][7],df[k][10],df[k][11],v)
                        if v > 0:
                            r_degree = math.degrees(math.atan(vvy/vvx))
                            # bpy.ops.object.empty_add(type='SINGLE_ARROW', align='WORLD', location=(vx,vy,vz), scale = ( v, v, v), rotation=( math.radians(90.0),  math.radians(45.0), math.radians(90.0)+r_degree))
                            bpy.ops.object.empty_add(type='SINGLE_ARROW', align='WORLD', location=(vx,vy,vz), rotation=( math.radians(90.0),  math.radians(45.0), math.radians(90.0-r_degree)))

                            ob = bpy.context.object
                            ob.name=f"empty_{t}_{i}_{j}"
                            ob.scale[0] = v
                            ob.scale[1] = v
                            ob.scale[2] = v

                            # print("v",v,r_degree)

                            # # 現在のシーンにコレクションをリンク
                            my_sub_coll.objects.link(ob)

                            # 紐付ける前のコレクションへのリンクを解除
                            bpy.context.scene.collection.children[0].objects.unlink(ob)


                            # print(f"{k}/{MI*MJ},{v}")
                        k += (1 + mabiki*mabiki)
                    except:
                        k += (1 + mabiki*mabiki)

            return my_sub_coll


        #ファイル数の確認
        # max_file = return_max_file(path="in")
        max_file = return_max_file(path=filepath_folder)
        max_file = max_file -1

        self.report({'INFO'}, str("読み込みファイル数:")+str(max_file))

        #3d View 範囲の終了設定
        config_viewports()


        #フレーム数設定
        frame_number_input = 10

        # フレームのスタートとエンドを設定する
        bpy.context.scene.frame_start = 0
        bpy.context.scene.frame_end = (max_file-2)*frame_number_input



        l_sub_coll2 = []
        for i in range(1,max_file):

            #ベクトル生成
            my_sub_coll2 = add_vector(readfile=f'{filepath_folder}/Result_{i}.csv',obj_name=f"{i}_vector",t=i,mabiki=2)
            l_sub_coll2.append(my_sub_coll2)



        #######
        frame_number = 0

        #処理を50回繰り返す
        j=1
        for tt in range(0,max_file):

           print("####",tt)
           for ii in range(len(l_sub_coll2)):
               # print("####",list(ii))
               # オブジェクトを非表示
               for ob in l_sub_coll2[ii].objects:
                   # print(ob)
                   bpy.context.scene.frame_set(frame_number)
                   ob.hide_viewport  = True
                   ob.hide_render    = True

                   # ob.keyframe_insert(data_path = "location",index = -1)
                   # ob.keyframe_insert(data_path = "scale",index = -1)
                   ob.keyframe_insert(data_path = "hide_viewport",index = -1)
                   ob.keyframe_insert(data_path = "hide_render",index = -1)

           # オブジェクトを順番に表示
           if j < max_file -1:
               if frame_number >= 0*(j-1) and frame_number < 20*(j):

                   for ob in l_sub_coll2[j].objects:
              # if frame_number >= 20 and frame_number < 40:
              #     for ob in l_sub_coll[1].objects:

                       bpy.context.scene.frame_set(frame_number)
                       ob.hide_viewport  = False
                       ob.hide_render    = False
                       ob.keyframe_insert(data_path = "hide_viewport",index = -1)
                       ob.keyframe_insert(data_path = "hide_render",index = -1)

           j+=1

           # print_objects()

           frame_number += frame_number_input



        return {'FINISHED'}
