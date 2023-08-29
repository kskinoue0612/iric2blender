import bpy
from bpy.props import FloatVectorProperty, StringProperty
from os import path

# BlenderGISをiricの障害物データに書き出し
class ExportBuilding2iRIC(bpy.types.Operator):
    #ラベル名の宣言
    bl_idname = "object.export_building2iric"
    bl_label = "4-2: OSMBuildingの建物をshpに書き出し"
    bl_description = "4-2: OSMBuildingの建物をshpに書き出し"
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

        def write_list2csv(write_list,filename):
            """書き込み"""
            f = open(filename, 'w', encoding='UTF-8')
            # print(write_list)
            f.writelines(write_list)
            f.close()

        def read_dae_building_iric_object(filepath_folder):

            #make write list
            write_list = []
            write_list_out = []
            write_list_out.append(f"pid,vid,x,y,name,value\n")

            for i in range(len(bpy.context.selected_objects)):
                v=bpy.context.selected_objects[i]
                # print(v.name)
                # print(bpy.data.objects[0].data.vertices[1].co)
                for j in range(int(len(v.data.vertices)/2.)):
                    vv=v.data.vertices[j]
                    # print(f"{i},{j},{vv.co[0]},{vv.co[1]},{v.name},1\n")
                    write_list_out.append(f"{i},{j},{vv.co[0]},{vv.co[1]},{v.name},1\n")

            #書き込み
            write_list2csv(write_list_out,filename=f'{filepath_folder}/out_building_polygon.csv')
            self.report({'INFO'}, f"書き込みを完了しました:{filepath_folder}/out_building_polygon.csv")

            return


        # ファイルパスをフォルダパスとファイル名に分割する
        filepath_folder, filepath_name = os.path.split(self.filepath)
        # ファイルパスをフォルダ名の名称とファイル名の拡張子に分割する
        filepath_nameonly, filepath_ext = os.path.splitext(filepath_name)

        #読み込みと処理
        read_dae_building_iric_object(filepath_folder)

        return {'FINISHED'}
