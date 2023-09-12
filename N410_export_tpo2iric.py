import bpy
from bpy.props import FloatVectorProperty, StringProperty
import os
from os import path

# オブジェクトをiricの点群csvに書き出し


class ExportTpo2iRIC(bpy.types.Operator):
    # ラベル名の宣言
    bl_idname = "object.export_tpo2iric"
    bl_label = "4-1: 地形データをiRIC用にCSVで書き出し"
    bl_description = "4-1: 地形データをiRIC用にCSVで書き出し"
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

        # ファイルパスをフォルダパスとファイル名に分割する
        filepath_folder, filepath_name = os.path.split(self.filepath)
        # ファイルパスをフォルダ名の名称とファイル名の拡張子に分割する
        filepath_nameonly, filepath_ext = os.path.splitext(filepath_name)

        # 書き込み
        f = open(str(filepath_folder)+str("/out_tpo_blender2iric.csv"), 'w', encoding='UTF-8')

        i = 0
        write_list = []
        for v in active_obj.data.vertices:
            write_list.append(f"{v.co[0]},{v.co[1]},{v.co[2]}\n")
            i += 1
        # print(write_list)
        f.writelines(write_list)
        f.close()
        self.report({'INFO'}, str("地形データ(out_tpo_blender2iric.csv)を保存しました。")+str(filepath_folder))
        return {'FINISHED'}
