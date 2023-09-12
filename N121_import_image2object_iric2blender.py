import bpy
from bpy.props import FloatVectorProperty, StringProperty
import os
from os import path
import numpy as np
import math
from . import N001_lib

# from . import material

# iricの計算結果をblenderのimport
class Import_Image2Object_iRIC2blender(bpy.types.Operator):
    #ラベル名の宣言
    bl_idname = "object.import_image_iric2blender"
    bl_label = "1-2-1: 画像をBlenderの格子に貼付"
    bl_description = "1-2-1: 画像をBlenderの格子に貼付"
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

        def image_test():
            """https://yuhoth.com/525/"""

            mat_name = "Grid_image"
            # MyMaterialが存在するかどうかを確認
            if bpy.data.materials.get(mat_name) is not None:
                # 存在する場合は削除
                bpy.data.materials.remove(bpy.data.materials[mat_name])


            material = bpy.data.materials.new(mat_name)
            material.use_nodes=True
            pic=material.node_tree.nodes["Principled BSDF"]

            #粗さ
            pic.inputs[9].default_value = 1.

            #スペキュラー
            pic.inputs[7].default_value = 0

            texImage=material.node_tree.nodes.new('ShaderNodeTexImage')
            texImage.image=bpy.data.images.load(self.filepath)#表示したい画像のパス
            material.node_tree.links.new(pic.inputs['Base Color'], texImage.outputs['Color'])
            # print(bpy.context.object.data.materials)
            bpy.context.object.data.materials.append(material) #材質の反映



        # スマートUV展開を実行する(デフォルト設定)
        def smartproject_UVmap_mesh(arg_objectname="Default") -> bool:
            """https://bluebirdofoz.hatenablog.com/entry/2020/05/26/203844"""
            """スマートUV展開を実行する(デフォルト設定)

            Keyword Arguments:
                arg_objectname {str} -- 指定オブジェクト名 (default: {"Default"})

            Returns:
                bool -- 実行正否
            """

            # 指定オブジェクトを取得する
            # (get関数は対象が存在しない場合 None が返る)
            selectob = bpy.data.objects.get(arg_objectname)

            # 指定オブジェクトが存在するか確認する
            if selectob == None:
                # 指定オブジェクトが存在しない場合は処理しない
                return False

            # オブジェクトがメッシュであるか確認する
            if selectob.type != 'MESH':
                # 指定オブジェクトがメッシュでない場合は処理しない
                return False

            # 不要なオブジェクトを選択しないように
            # 全てのオブジェクトを走査する
            for ob in bpy.context.scene.objects:
                # 非選択状態に設定する
                ob.select_set(False)

            # 指定のオブジェクトのみを選択状態にする
            selectob.select_set(True)

            # 対象オブジェクトをアクティブに変更する
            bpy.context.view_layer.objects.active = selectob

            # 元々の操作モードを記録する
            befmode = bpy.context.active_object.mode

            # 編集モードに移行する
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)

            # 頂点を全選択した状態とする
            bpy.ops.mesh.select_all(action='SELECT')

            # UV展開（ビュー投影バウンスあり）を実行する
            bpy.ops.uv.project_from_view(camera_bounds=False, correct_aspect=True, scale_to_bounds=True)

            # オブジェクトモードに移行する
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

            # 変更前のモードに移行する
            bpy.ops.object.mode_set(mode=befmode)

            return


        ##########

        # ファイルパスをフォルダパスとファイル名に分割する
        filepath_folder, filepath_name = os.path.split(self.filepath)
        # ファイルパスをフォルダ名の名称とファイル名の拡張子に分割する
        filepath_nameonly, filepath_ext = os.path.splitext(filepath_name)

        #3d View 範囲の終了設定
        N001_lib.config_viewports()


        #選択したオブジェクト視点をあわせる
        # N001_lib.framein_to_selected_object(obj_name ='iRIC_Grid_Elevation')

        #イメージの貼り付け
        image_test()

        #UV展開
        smartproject_UVmap_mesh(arg_objectname=context.active_object.name)


        return {'FINISHED'}
