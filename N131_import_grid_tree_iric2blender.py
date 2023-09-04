import bpy
from   bpy.props import FloatVectorProperty, StringProperty
import numpy as np
import math
import random
import os
from   os import path
from . import N001_lib

# iricの計算結果をblenderのimport
class ImportGridTree_iRIC2blender(bpy.types.Operator):
    #ラベル名の宣言
    bl_idname = "object.import_grid_tree_iric2blender"
    bl_label = "1-3-1: iRIC格子(Nays2dh/植生データ)を読み込み"
    bl_description = "1-3-1: iRIC格子(Nays2dh/植生データ)を読み込み"
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

        def make_verts_numpy(readfile):
            #３行目以降を読み込みdfとする
            df = np.loadtxt(readfile, delimiter=',',skiprows=3)
            # df = np.loadtxt(readfile, delimiter=',',skiprows=3, usecols=[0,1,2,3,4,5,6,7,8,9,10,11,12])
            return df

        def read_MI_MJ(readfile):
            #ファイルの1行目を読み込み、コンマで分離
            with open(readfile) as f:
                firstline = f.readlines()[1].split(",")
            MI=int(firstline[0])
            MJ=int(firstline[1])
            return MI,MJ


        # vertsの作成
        def make_vert(MI,MJ,df,df_row_n,obj_scale):
            """ df_row_n = 4:Depth(Max), 5:Depth, 6:Elevation, 7:WaterSurfaceElevation """
            verts=[]

            k=1
            min_z = df[1][df_row_n]
            for j in range(MJ):
                for i in range(MI):
                    k=i+MI*j
                    if df[k][df_row_n] < min_z:
                        min_z = df[k][df_row_n]

            k=1
            for j in range(MJ):
                for i in range(MI):
                    k=i+MI*j
                    verts.append([df[k][3]*obj_scale,df[k][4]*obj_scale,df[k][df_row_n]*obj_scale])

            return verts


        def make_obj(verts,faces,readfile,obj_name):
            msh = bpy.data.meshes.new("cubemesh") #Meshデータの宣言
            msh.from_pydata(verts, [], faces) # 頂点座標と各面の頂点の情報でメッシュを作成
            cube_obj = bpy.data.objects.new(obj_name, msh) # メッシュデータでオブジェクトを作成
            return cube_obj


        def set_faces_trees(MI,MJ,df):
            faces=[]
            faces_tree=[]
            ts=bpy.context.scene.type_of_solver_prop_int

            k=1
            for j in range(MJ-1):
                for i in range(MI-1):
                    k=i+MI*j
                    if df[k][10] > 0:
                        faces.append([k,k+1,k+1+MI,k+MI])
                        if ts == 1:
                            faces_tree.append([k,k+1,k+1+MI,k+MI,df[k][10],df[k][11],int(df[k][13]),df[k][14]])
                        else:
                            faces_tree.append([k,k+1,k+1+MI,k+MI,df[k][7],df[k][8],int(df[k][9]),df[k][10]])
            return faces,faces_tree



        def make_ojb_each_files(readfile,df_row_n,obj_name):
            df = make_verts_numpy(readfile)
            MI,MJ = read_MI_MJ(readfile)

            #set faces & verts
            verts = make_vert(MI,MJ,df,df_row_n,obj_scale=1)
            faces,faces_tree=set_faces_trees(MI,MJ,df)
            cube_obj=make_obj(verts,faces,readfile,obj_name)
            return cube_obj,faces_tree


        def set_trees_into_cell(tree_cell_maxmin,tree_n,tree_name):

            # 指定された本数分、植生を植える
            for i in range(tree_n):
                # X,Y座標をランダムに決める
                xr  = random.uniform(tree_cell_maxmin[0][0], tree_cell_maxmin[0][1])
                yr  = random.uniform(tree_cell_maxmin[1][0], tree_cell_maxmin[1][1])

                # 回転角度をランダムに決める
                xro = random.random()
                yro = random.random()

                # 植生メッシュをコピーする
                obj    = bpy.context.object
                co     = bpy.context.collection
                tree2  = bpy.data.meshes[tree_name].copy()

                # 新しい植生オブジェクトを作成し、位置、回転、スケールを設定する
                o1               = bpy.data.objects.new(name='tree', object_data=tree2)
                o1.location      = (xr,yr,tree_cell_maxmin[2])
                o1.rotation_euler= (0,0,random.random())
                o1.scale         = (1*tree_cell_maxmin[3],1*tree_cell_maxmin[3],1*tree_cell_maxmin[3])

                # オブジェクトをシーンにリンクする
                bpy.data.collections["iRIC_trees"].objects.link(o1)




        # マテリアルのalpha値のテクスチャとプリンシプルBSDFのalpha値をリンクし、低ポリゴンの木が透明になるようにする
        def material_tree_link_alpha(material_name):
           # マテリアルを取得
            mat_el   = bpy.data.materials[material_name]

            # マテリアルのノードツリーを取得
            mat_node = mat_el.node_tree

            #base colorのalphaとプリンシプルBSDFのalphaのノードを結合する
            mat_node.links.new(mat_node.nodes["画像テクスチャ"].outputs[1], mat_node.nodes["プリンシプルBSDF"].inputs[21])



        # 木を配置する
        def grow_tree(ob1,faces_tree,addon_dirpath):

            # 読み込む植生モデルの整理
            low_poly_trees     = ["pine_tree_lite","yoshi_lite"]
            mat_low_poly_trees = ['pine-leaf',"mat_yoshi"]
            high_poly_trees    = ["willow","pine","maple","broadleaf_tree"]
            new_trees           = ["normal","hardwood","conifer","grass"]

            # # 低ポリゴンの木をインポート
            # for tree_name in low_poly_trees:
            #     # bpy.ops.wm.collada_import(filepath='tree_data/low_poly_tree/pine_tree_lite/pine_tree_lite.dae')
            #     bpy.ops.wm.collada_import(filepath=f'{addon_dirpath}/tree_data/low_poly_tree/{tree_name}/{tree_name}.dae')

            # # 低ポリゴンの木にマテリアルを適用
            #for mat_name in mat_low_poly_trees:
            #    material_tree_link_alpha(material_name=f'{mat_name}')

            # 高ポリゴンの木をもしくは低ポリゴンのnewdataの木をインポート 
            vm=bpy.context.scene.vm_prop_int
            if vm==1:
                for tree_name in new_trees:
                    bpy.ops.import_scene.fbx(filepath=f'{addon_dirpath}/tree_data/new_tree_one/{tree_name}.fbx')
                # 全ての植生を格納するリストを作成
                trees_all=new_trees
                trees_all.extend(low_poly_trees)
                #trees_all.extend(new_trees)
                self.report({'INFO'}, f"trees_all:{trees_all}")
                
            else :
                for tree_name in high_poly_trees:
                    bpy.ops.import_scene.fbx(filepath=f'{addon_dirpath}/tree_data/high_poly_tree/{tree_name}.fbx')
                # 全ての植生を格納するリストを作成
                trees_all=high_poly_trees
                trees_all.extend(low_poly_trees)
                #trees_all.extend(new_trees)
                self.report({'INFO'}, f"trees_all:{trees_all}")
                
            
            #for tree_name in high_poly_trees:
            #    bpy.ops.import_scene.fbx(filepath=f'{addon_dirpath}/tree_data/high_poly_tree/{tree_name}.fbx')
            

            mesh = ob1.data
            j=0
            lista=[]
            for face in mesh.polygons:

                tree_density = 0.01

                #各メッシュの４隅の座標を取得
                xmin = min([mesh.vertices[faces_tree[j][0]].co[0],mesh.vertices[faces_tree[j][1]].co[0],mesh.vertices[faces_tree[j][2]].co[0],mesh.vertices[faces_tree[j][3]].co[0]])
                xmax = max([mesh.vertices[faces_tree[j][0]].co[0],mesh.vertices[faces_tree[j][1]].co[0],mesh.vertices[faces_tree[j][2]].co[0],mesh.vertices[faces_tree[j][3]].co[0]])
                ymin = min([mesh.vertices[faces_tree[j][0]].co[1],mesh.vertices[faces_tree[j][1]].co[1],mesh.vertices[faces_tree[j][2]].co[1],mesh.vertices[faces_tree[j][3]].co[1]])
                ymax = max([mesh.vertices[faces_tree[j][0]].co[1],mesh.vertices[faces_tree[j][1]].co[1],mesh.vertices[faces_tree[j][2]].co[1],mesh.vertices[faces_tree[j][3]].co[1]])

                # メッシュの面積を算出
                ss   = math.sqrt(math.sqrt((xmax-xmin)**2)*math.sqrt((ymax-ymin)**2))

                # 植生密度と各メッシュの面積から植える木の本数を算出
                ass  = faces_tree[j][4]*0.01
                ds   = 0.3
                ns   = ass*ss/ds
                grow_tree = ns

                # 確率から植生を植えるかどうかランダムに決める。
                #grow_tree = random.randrange(1,int(1/grow_tree),1)
                #grow_tree =bpy.types.Scene.para_prop_float = FloatProperty(name="para",description="プロパティ（float）", default=0.5,min=0.01,max=1.0)
                
                # 設定した閾値より植生密生度が大きい場合植生を植える(そのときにすべて生やすかランダムか)
                para=bpy.context.scene.para_prop_float
                ratio=bpy.context.scene.v_ratio_prop_int
                zratio = bpy.context.scene.z_ratio_prop_int
                print(zratio)
                print("プリント文")
                # 現在の植生を描画する(密生度が0.01以上は割合で描画)
                if zratio == 0:
                    if faces_tree[j][4] >= 0.01:
                        if random.random() < (ratio/100):
                            grow_tree = 1
                        else:grow_tree = 0
                # 将来の植生を描画する(予測値が閾値以上は割合で描画)
                else:
                    if ratio==100:
                        if faces_tree[j][7] >= para:
                            grow_tree = 1
                        else:grow_tree = 0
                    elif ratio==0:
                        if faces_tree[j][7] >= para:
                            grow_tree=random.randint(0 ,1)
                        else:grow_tree = 0
                    # 閾値を超えた値のセルは ratio の割合で生やす
                    else:
                        if faces_tree[j][7] >= para:
                            if random.random() < (ratio/100):
                                grow_tree = 1
                            else:grow_tree=0
                

                # 植生を植える場合
                if grow_tree==1:
                    # 植生の位置座標zを決める。（根本の位置）＋　植生の高さ
                    # 現在の植生の場合：植生高さ通り
                    if zratio==0:
                        zmin =min([mesh.vertices[faces_tree[j][0]].co[2],mesh.vertices[faces_tree[j][1]].co[2],mesh.vertices[faces_tree[j][2]].co[2],mesh.vertices[faces_tree[j][3]].co[2]])
                        ztree =faces_tree[j][5]
                        # 植生を植えるxy座標を定義
                        tree_cell_maxmin=([xmin,xmax],[ymin,ymax],zmin,ztree)

                        # max_tree_n=1
                        tree_n =int(math.sqrt(math.sqrt((xmax-xmin)**2)*math.sqrt((ymax-ymin)**2))/6.25)

                        # 植生の種類を定義
                        tree_name=trees_all[faces_tree[j][6]+1]

                        # 植生を配置する
                        set_trees_into_cell(tree_cell_maxmin,tree_n,tree_name)
                        
                    # 予測の植生の場合：予測される値がn日後どうなるか(植生が生えていく描画)
                    else:
                        if faces_tree[j][4] >= 0.01:
                            zmin =min([mesh.vertices[faces_tree[j][0]].co[2],mesh.vertices[faces_tree[j][1]].co[2],mesh.vertices[faces_tree[j][2]].co[2],mesh.vertices[faces_tree[j][3]].co[2]])
                            ztree =faces_tree[j][5]
                            # 植生を植えるxy座標を定義
                            tree_cell_maxmin=([xmin,xmax],[ymin,ymax],zmin,ztree)

                            # max_tree_n=1
                            tree_n =int(math.sqrt(math.sqrt((xmax-xmin)**2)*math.sqrt((ymax-ymin)**2))/6.25)

                            # 植生の種類を定義
                            tree_name=trees_all[faces_tree[j][6]+1]

                            # 植生を配置する
                            set_trees_into_cell(tree_cell_maxmin,tree_n,tree_name)
                            
                        else:
                            zmin =min([mesh.vertices[faces_tree[j][0]].co[2],mesh.vertices[faces_tree[j][1]].co[2],mesh.vertices[faces_tree[j][2]].co[2],mesh.vertices[faces_tree[j][3]].co[2]])
                            ztree  =faces_tree[j][5]*(zratio/365)
                    
                            # 植生を植えるxy座標を定義
                            tree_cell_maxmin=([xmin,xmax],[ymin,ymax],zmin,ztree)

                            # max_tree_n=1
                            tree_n =int(math.sqrt(math.sqrt((xmax-xmin)**2)*math.sqrt((ymax-ymin)**2))/6.25)

                            # 植生の種類を定義
                            tree_name=trees_all[faces_tree[j][6]+1]

                            # 植生を配置する
                            set_trees_into_cell(tree_cell_maxmin,tree_n,tree_name)
                    
                # 植生を植えない場合       
                if grow_tree==0: 
                    # 予測の植生の場合：予測される値がn日後どうなるか(植生がなくなる描画)
                    if zratio > 0:
                        zmin=min([mesh.vertices[faces_tree[j][0]].co[2],mesh.vertices[faces_tree[j][1]].co[2],mesh.vertices[faces_tree[j][2]].co[2],mesh.vertices[faces_tree[j][3]].co[2]])
                        #現在植生が生えている:365日後なくなる　
                        if faces_tree[j][4] >= 0.01:
                            ztree  =faces_tree[j][5]*((365-zratio)/365)
                            
                            # 現在の植生の場合：無視

                            # 植生を植えるxy座標を定義
                            tree_cell_maxmin=([xmin,xmax],[ymin,ymax],zmin,ztree)

                            # max_tree_n=1
                            tree_n =int(math.sqrt(math.sqrt((xmax-xmin)**2)*math.sqrt((ymax-ymin)**2))/6.25)

                            # 植生の種類を定義
                            tree_name=trees_all[faces_tree[j][6]+1]

                            # 植生を配置する
                            set_trees_into_cell(tree_cell_maxmin,tree_n,tree_name)

                j+=1
   

            #木のサンプルを削除　
            for tree_name in trees_all:
                try:
                    bpy.data.meshes.remove(bpy.data.meshes[f"{tree_name}"])
                except:
                    pass


        ###########

        # ファイルパスをフォルダパスとファイル名に分割する
        filepath_folder, filepath_name = os.path.split(self.filepath)
        # ファイルパスをフォルダ名の名称とファイル名の拡張子に分割する
        filepath_nameonly, filepath_ext = os.path.splitext(filepath_name)

        # 新しいCollrectionを作成
        col_name=str(f'iRIC_trees')
        my_sub_coll = bpy.data.collections.new(col_name)
        bpy.context.scene.collection.children.link(my_sub_coll)

        #植生のあるメッシュを整理する
        # ob1,faces_tree = make_elecation_ob_and_tree(self.filepath)
        ob1,faces_tree = make_ojb_each_files(readfile=self.filepath,df_row_n=6,obj_name=f"iRIC_Grid_Elevation")

        # 植生のあるメッシュに対して木を配置する
        addon_dirpath = os.path.dirname(__file__)
        grow_tree(ob1,faces_tree,addon_dirpath)

        #viewportの設定    
        N001_lib.config_viewports()

        return {'FINISHED'}