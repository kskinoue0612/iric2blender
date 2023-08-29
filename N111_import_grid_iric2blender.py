import bpy
from bpy.props import FloatVectorProperty, StringProperty
from . import N001_lib



# iricの計算結果をblenderのimport
class ImportGrid_iRIC2blender(bpy.types.Operator):
    #ラベル名の宣言
    bl_idname = "object.import_grid_iric2blender"
    bl_label = "1-1-1: iRIC格子(csv)の読み込み"
    bl_description = "1-1-1: iRIC格子(csv)の読み込み"
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




    # 実行時イベント(Gridの読み込みのフォルダの選択)
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
        


        def make_mesh_grid_from_iric_grid_csv(filepath):
            # iricのcsvファイル(地盤データ:elevation)からオブジェクトを作成
            df,MI,MJ = N001_lib.read_file(readfile=filepath,usecols=None)
            # obj= N001_lib.make_ojb_each_files(df,MI,MJ,df_row_n=6,obj_name=f"iRIC_Grid_Elevation")

            df = df[:, [3, 4, 6]] #grid
            obj_name=f"iRIC_Grid_Elevation"

            if obj_name in bpy.data.objects:
                self.report({'INFO'}, f"{obj_name}を削除します。")

                # 削除するコレクションとその名前を設定
                collection_name = "iRIC_Grid"
                # コレクションを取得
                collection = bpy.data.collections.get(collection_name)

                if collection:
                    # コレクション内のすべてのオブジェクトを削除
                    for obj in collection.objects:
                        bpy.data.objects.remove(obj, do_unlink=True)

                    # コレクションを削除
                    bpy.data.collections.remove(collection, do_unlink=True)


            ob = N001_lib.Make_mesh_object(df, MI, MJ, obj_name, obj_scale=1)
            obj = ob.make_obj_each_files()

            # 現在のシーンにコレクションをリンク
            # my_sub_coll.objects.link(obj)
            bpy.context.scene.collection.children['iRIC_Grid'].objects.link(obj)


            #シーンにあるオブジェクトを削除
            bpy.data.scenes['Scene'].collection.objects.unlink(bpy.data.objects[obj_name])

            return obj




        def export_cube_maxmin_surface_mesh(surface_mesh):
            #立方体の４隅の座標を取得
            vmaxmin=[]
            for v in surface_mesh.data.vertices:
                vmaxmin.append([v.co[0],v.co[1],0])

            grid_corner=[(max(vmaxmin)[0]-0.5,max(vmaxmin)[1]-0.5,0),(min(vmaxmin)[0]+0.5,min(vmaxmin)[1]+0.5,0),([max(vmaxmin)[0]-0.5,min(vmaxmin)[1]+0.5,0]),([min(vmaxmin)[0]+0.5,max(vmaxmin)[1]-0.5,0])]

            #立方体の生成
            for i in range(len(grid_corner)):
                bpy.ops.mesh.primitive_cube_add(size=1, enter_editmode=False, location=grid_corner[i])
                bpy.context.object.name=f"grid_corner{i}"

                # 現在のシーンにコレクションをリンク
                # my_sub_coll.objects.link(obj)
                bpy.context.scene.collection.children['iRIC_Grid'].objects.link(bpy.context.object)


                #Collectionにあるgridオブジェクトを削除
                bpy.context.scene.collection.children['Collection'].objects.unlink(bpy.context.object)


            #3dカーソルをグリッドの中心へ
            grid_center=((grid_corner[0][0]+grid_corner[1][0]+grid_corner[2][0]+grid_corner[3][0])/4.,(grid_corner[0][1]+grid_corner[1][1]+grid_corner[2][1]+grid_corner[3][1])/4.,0)
            bpy.context.scene.cursor.location=grid_center


        #### main ####
        active_obj = context.active_object

        # ファイルパスをフォルダパスとファイル名に分割する
        filepath_folder, filepath_name = os.path.split(self.filepath)
        # ファイルパスをフォルダ名の名称とファイル名の拡張子に分割する
        filepath_nameonly, filepath_ext = os.path.splitext(filepath_name)

        # Collrection(iRIC_Grid)を作成
        col_name=str(f'iRIC_Grid')

        #同じコレクション名がある場合は、そのコレクションとその階層以下のオブジェクトを削除する。
        N001_lib.delete_collection_and_objects(col_name)

        #コレクションにリンクする
        my_sub_coll = bpy.data.collections.new(col_name)
        bpy.context.scene.collection.children.link(my_sub_coll)


        #iRICのグリットからメッシュを生成
        ob1 = make_mesh_grid_from_iric_grid_csv(self.filepath)

        #メッシュの４隅に立方体を配置
        export_cube_maxmin_surface_mesh(ob1)


        #3d View 範囲の終了設定
        N001_lib.config_viewports()


        #選択したオブジェクト視点をあわせる
        N001_lib.framein_to_selected_object(obj_name ='iRIC_Grid_Elevation')

        return {'FINISHED'}
