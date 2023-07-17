import bpy
from bpy.props import FloatVectorProperty, StringProperty
from . import material
from . import N001_lib
import os

# iricの計算結果をblenderのimport
class ImportResult2DH_Blue_iRIC2blender(bpy.types.Operator):
    #ラベル名の宣言
    bl_idname = "object.import_result2dh_blue_iric2blender"
    bl_label = "3-1-3: Nays2dhの計算結果(水深/Water)の読み込み"
    bl_description = "3-1-3: Nays2dhの計算結果(水深/Water)の読み込み"
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
        self.report({'INFO'}, "保存先のフォルダを指定してください")
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


    #実行ファイル（選択しているオブジェクトの地形データをiricの点群csvに書き出し）
    def execute(self, context):

        #### main ####
        # active_obj = context.active_object

        # ファイルパスをフォルダパスとファイル名に分割する
        filepath_folder, filepath_name = os.path.split(self.filepath)
        # ファイルパスをフォルダ名の名称とファイル名の拡張子に分割する
        # filepath_nameonly, filepath_ext = os.path.splitext(filepath_name)

        #3d View 範囲の終了設定
        N001_lib.config_viewports()

        #CSVの読み込み設定
        # df_col_list = [2, 3, 4, 5] #Nays2DH: x,y,depth,z
        df_col_list = [2, 3, 4, 5, 6] #Nays2DH: x,y,depth,z,dummy
        usecols     = [0,1,2,3,4,5,6,7,8,9,10,11,12]

        #カラーコンターの設定
        color_set = N001_lib.setting_color_contor()
        mat_list    = []
        mat_list    = material.set_material_blue(mat_list,color_set)
        result_type = "depth"

        ws = N001_lib.Make_WaterSurface_depth_velocity_from_iRIC_result(df_col_list,usecols,filepath_folder,mat_list,color_set,result_type)
        ws.create_mesh_result()

        return {'FINISHED'}