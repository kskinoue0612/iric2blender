import bpy
from bpy.props import FloatVectorProperty, StringProperty
import os
from os import path
import numpy as np

# from . import material

# iricの計算結果をblenderのimport
class Import_Plataue_Obj_Dem(bpy.types.Operator):
    #ラベル名の宣言
    bl_idname = "object.import_plataue_obj_dem"
    bl_label = "2-2-1: Plateau DEMデータ(obj)を読み込み"
    bl_description = "2-2-1: Plateau DEMデータ(obj)を読み込み"
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

        def config_viewports():
            D = bpy.data
            CLIP_END = 100000

            screens = D.screens
            viewareas = [area for screen in screens for area in screen.areas if area.type == 'VIEW_3D']
            for area in viewareas:
                # area.spaces.active.overlay.grid_scale = SCALE_LENGTH
                area.spaces.active.clip_end = CLIP_END


        def read_dem(filepath_folder):
            # path = "./obj/dem"
            files = os.listdir(filepath_folder)

            col_name=str(f'dem_plataue')
            my_sub_coll = bpy.data.collections.new(col_name)
            bpy.context.scene.collection.children.link(my_sub_coll)


            for i in files:
                ob = bpy.ops.wm.obj_import(filepath=f'{filepath_folder}/{i}',forward_axis='Y_FORWARD', up_axis='Z_UP')

                # # 現在のシーンにコレクションをリンク
                ob = bpy.context.scene.collection.children[0].objects[0]

                # my_sub_coll.objects.link(ob)
                bpy.context.scene.collection.children['dem_plataue'].objects.link(ob)

                # 紐付ける前のコレクションへのリンクを解除
                bpy.context.scene.collection.children[0].objects.unlink(ob)


        #######

        # ファイルパスをフォルダパスとファイル名に分割する
        filepath_folder, filepath_name = os.path.split(self.filepath)
        # ファイルパスをフォルダ名の名称とファイル名の拡張子に分割する
        filepath_nameonly, filepath_ext = os.path.splitext(filepath_name)

        #
        read_dem(filepath_folder)

        return {'FINISHED'}
