import bpy
from bpy.props import FloatVectorProperty, StringProperty
import os
from os import path
import numpy as np
from . import N001_lib


# iricの計算結果をblenderのimport
class Import_Plataue_Obj_Buidling(bpy.types.Operator):
    # ラベル名の宣言
    bl_idname = "object.import_plataue_obj_building"
    bl_label = "2-2-2: Plateau 建物データ(obj)を読み込み"
    bl_description = "2-2-2: Plateau 建物データ(obj)を読み込み"
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

    # 実行ファイル（選択しているオブジェクトの地形データをiricの点群csvに書き出し）

    def execute(self, context):

        def read_obj_building(filepath_folder):

            def read_bldg(filepath_folder):
                files1 = os.listdir(filepath_folder)

                # collection 作成
                col_name = str(f'bldg_plataue')
                my_sub_coll = bpy.data.collections.new(col_name)
                bpy.context.scene.collection.children.link(my_sub_coll)

                # import obj
                for i in files1:
                    ob = bpy.ops.wm.obj_import(filepath=f'{filepath_folder}/{i}', forward_axis='Y_FORWARD', up_axis='Z_UP')

                    # # 現在のシーンにコレクションをリンク
                    ob = bpy.context.scene.collection.children[0].objects[0]

                    # my_sub_coll.objects.link(ob)
                    bpy.context.scene.collection.children['bldg_plataue'].objects.link(ob)

                    # 紐付ける前のコレクションへのリンクを解除
                    bpy.context.scene.collection.children[0].objects.unlink(ob)

            read_bldg(filepath_folder)

        ###############

        # ファイルパスをフォルダパスとファイル名に分割する
        filepath_folder, filepath_name = os.path.split(self.filepath)
        # ファイルパスをフォルダ名の名称とファイル名の拡張子に分割する
        filepath_nameonly, filepath_ext = os.path.splitext(filepath_name)

        # Plateau 建物データ(obj)を読み込み"
        read_obj_building(filepath_folder)

        # 3d View 範囲の終了設定
        N001_lib.config_viewports()

        return {'FINISHED'}
