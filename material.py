import bpy

# def materials_grid():
#     """gridのマテリアルを定義"""
#     # # 新規マテリアルを作成
#     mat_el = bpy.data.materials.new('grid_material')
#
#     # Use Nodesをオンにする
#     mat_el.use_nodes = True
#
#     # Node Treeにアクセス
#     node_tree = mat_el.node_tree
#
#     # Material Outputノードにアクセス
#     output = node_tree.nodes['Material Output']
#
#     # Principled BSDFにアクセス
#     p_bsdf = node_tree.nodes['Principled BSDF']
#
#     # Blend ModeをAlpha Blendに設定
#     mat_el.blend_method = 'BLEND'
#
#     # # 色を茶色に設定
#     # # p_bsdf.inputs['Base Color'].default_value = (0.0, 0.0, 1.0, 1.0)
#     # p_bsdf.inputs['Base Color'].default_value = (0.367,0.123,0.012, 1.0)
#
#     #粗さ（地面は光が反射しないため粗い方(1に近い方)がよい）
#     p_bsdf.inputs[9].default_value = 1.
#
#     # # アルファチャンネル（透明度）の値を0.1に設定
#     # p_bsdf.inputs['Alpha'].default_value = 0.9
#
#     return mat_gl


def materials_elevation():
    """水の色や質感を定義"""
    # # 新規マテリアルを作成
    mat_el = bpy.data.materials.new('elevation')

    # Use Nodesをオンにする
    mat_el.use_nodes = True

    # Node Treeにアクセス
    node_tree = mat_el.node_tree

    # Material Outputノードにアクセス
    output = node_tree.nodes['Material Output']

    # Principled BSDFにアクセス
    p_bsdf = node_tree.nodes['Principled BSDF']

    # Blend ModeをAlpha Blendに設定
    mat_el.blend_method = 'BLEND'

    # 色を茶色に設定
    # p_bsdf.inputs['Base Color'].default_value = (0.0, 0.0, 1.0, 1.0)
    p_bsdf.inputs['Base Color'].default_value = (0.367,0.123,0.012, 1.0)

    #粗さ（地面は光が反射しないため粗い方(1に近い方)がよい）
    p_bsdf.inputs[9].default_value = 0.9

    # アルファチャンネル（透明度）の値を0.1に設定
    p_bsdf.inputs['Alpha'].default_value = 0.9

    return mat_el


def materials_watersurface():
    """水面の色や質感を定義"""
    # 新規マテリアルを作成
    mat_ws = bpy.data.materials.new('watersurface')

    # Use Nodesをオンにする
    mat_ws.use_nodes = True

    # Node Treeにアクセス
    node_tree = mat_ws.node_tree

    # Material Outputノードにアクセス
    output = node_tree.nodes['Material Output']

    # Principled BSDFにアクセス
    p_bsdf = node_tree.nodes['Principled BSDF']

    # Blend ModeをAlpha Blendに設定
    mat_ws.blend_method = 'BLEND'

    l_color = bpy.context.scene.water_color_prop_floatv

    # 色を青に設定
    p_bsdf.inputs['Base Color'].default_value = (l_color[0], l_color[1], l_color[2], 1.0) #青

    # p_bsdf.inputs['Base Color'].default_value = (0.0, 0.0, 1.0, 1.0)
    # p_bsdf.inputs['Base Color'].default_value = (0.6, 0.9, 1.0, 1.0) #青
    # p_bsdf.inputs['Base Color'].default_value = (0.303, 0.082, 0, 1.0)  #茶色
    # p_bsdf.inputs['Base Color'].default_value = (0.303, 0.127, 0, 1.0)  #茶色

    # import random
    # p_bsdf.inputs['Base Color'].default_value = (0.6-random.random()*0.5, 0.9-random.random()*0.5, 1.0-random.random()*0.5, 1.0)

    #metalic (水面は反射が多くなるようにメタリックを上げる)
    # p_bsdf.inputs[6].default_value = 0.7
    p_bsdf.inputs[6].default_value = bpy.context.scene.water_metalic_prop_float

    #粗さ(水面は反射面がきれいになるように粗さが少ない方がよい。)
    # p_bsdf.inputs[9].default_value = 0.1
    # p_bsdf.inputs[9].default_value = 0.5
    p_bsdf.inputs[9].default_value = bpy.context.scene.water_roughness_prop_float


    # アルファチャンネル（透明度）の値を0.1に設定
    # p_bsdf.inputs['Alpha'].default_value = 0.1
    # p_bsdf.inputs['Alpha'].default_value = 0.9
    p_bsdf.inputs['Alpha'].default_value = bpy.context.scene.water_alpha_prop_float

    return mat_ws

def color_contor_from_depth(depth, max_depth, min_depth):
    #RGBの区切りごとに水深を分ける
    mid_depth1 = (max_depth - min_depth)/4
    mid_depth2 = (max_depth - min_depth)/4*2
    mid_depth3 = (max_depth - min_depth)/4*3

    #水深別に色を設定
    if depth >= min_depth and depth < mid_depth1:
        l_color = (0, (depth - min_depth)/(mid_depth1 - min_depth),1) #青(0,0,1)
    if depth >= mid_depth1 and depth < mid_depth2:
        l_color = (0, 1, 1+ (mid_depth1-depth)/(mid_depth2 - mid_depth1)) #水(0,1,1)
    if depth >= mid_depth2 and depth < mid_depth3:
        l_color = (-(mid_depth2 - depth)/(mid_depth3 - mid_depth2), 1, 0) #緑(0,1,0)
    if depth >= mid_depth3 and depth < max_depth:
        l_color = (1,1+(mid_depth3 - depth)/(max_depth - mid_depth3), 0) #黄(1,1,0)
    if depth >= max_depth:
        l_color = (1, 0, 0)  #赤(1,0,0)
    if depth < min_depth:
        l_color = (0., 0., 1.0) #青

    return l_color

def set_material(mat_list,color_set):
    j=0

    # カラーコンターの分割数定義
    num_color = color_set[0]

    #カラーコンターマテリアル名を設定
    for j in range(num_color):
        mat_name = f"mat{j}"
        material = bpy.data.materials.get(mat_name)

        #マテリアルの設定がない場合（初回のみ設定する用）
        if material is None:
            material = bpy.data.materials.new(mat_name)

            # マテリアルをオブジェクトに設定する
            material.use_nodes = True

            #depthからcolorをセット
            # depth = j*(color_max_depth-color_min_depth)/(num_color-2)
            depth = j*(color_set[1]-color_set[2])/(color_set[0]-2)
            l_color = color_contor_from_depth(depth, color_set[1], color_set[2])

            # Principal BSDFの立ち上げ
            pBSDF = material.node_tree.nodes["Principled BSDF"]

            # 色を設定
            pBSDF.inputs[0].default_value = (l_color[0],l_color[1],l_color[2],1)

            #metalic (水面は反射が多くなるようにメタリックを上げる)
            # pBSDF.inputs[6].default_value = 0.7
            pBSDF.inputs[6].default_value = bpy.context.scene.water_metalic_prop_float

            #粗さ（地面は光が反射しないため粗い方(1に近い方)がよい）
            # pBSDF.inputs[9].default_value = 0.3
            pBSDF.inputs[9].default_value = bpy.context.scene.water_roughness_prop_float

            # アルファチャンネル（透明度）の値を0.1に設定
            # pBSDF.inputs['Alpha'].default_value = 0.5
            pBSDF.inputs['Alpha'].default_value = bpy.context.scene.water_alpha_prop_float

            #カラーコンター用のマテリアルリストに追加
            mat_list.append(mat_name)


    return mat_list


def set_material_v(mat_list_v,color_set_v):
    j=0

    # カラーコンターの分割数定義
    num_color = color_set_v[0]

    #カラーコンターマテリアル名を設定
    for j in range(num_color):
        mat_name = f"mat{j}"
        material = bpy.data.materials.get(mat_name)

        #マテリアルの設定がない場合（初回のみ設定する用）
        if material is None:
            material = bpy.data.materials.new(mat_name)

            # マテリアルをオブジェクトに設定する
            material.use_nodes = True

            #depthからcolorをセット
            # depth = j*(color_set[1]-color_set[2])/(color_set[0]-2)
            velocity = j*(color_set_v[1]-color_set_v[2])/(color_set_v[0]-2)

            l_color = color_contor_from_depth(velocity, color_set_v[1], color_set_v[2])

            # Principal BSDFの立ち上げ
            pBSDF = material.node_tree.nodes["Principled BSDF"]

            # 色を設定
            pBSDF.inputs[0].default_value = (l_color[0],l_color[1],l_color[2],1)

            #metalic (水面は反射が多くなるようにメタリックを上げる)
            # pBSDF.inputs[6].default_value = 0.7
            pBSDF.inputs[6].default_value = bpy.context.scene.water_metalic_prop_float


            #粗さ（地面は光が反射しないため粗い方(1に近い方)がよい）
            # pBSDF.inputs[9].default_value = 0.3
            pBSDF.inputs[9].default_value = bpy.context.scene.water_roughness_prop_float

            # アルファチャンネル（透明度）の値を0.1に設定
            # pBSDF.inputs['Alpha'].default_value = 0.5
            pBSDF.inputs['Alpha'].default_value = bpy.context.scene.water_alpha_prop_float

            #カラーコンター用のマテリアルリストに追加
            mat_list_v.append(mat_name)


    return mat_list_v

def set_material_blue(mat_list,color_set):
    j=0

    # カラーコンターの分割数定義
    num_color = color_set[0]

    #カラーコンターマテリアル名を設定
    for j in range(num_color):
        mat_name = f"mat{j}"
        material = bpy.data.materials.get(mat_name)

        #マテリアルの設定がない場合（初回のみ設定する用）
        if material is None:
            material = bpy.data.materials.new(mat_name)

            # マテリアルをオブジェクトに設定する
            material.use_nodes = True

            #depthからcolorをセット
            # depth = j*(color_max_depth-color_min_depth)/(num_color-2)
            depth = j*(color_set[1]-color_set[2])/(color_set[0]-2)

            # l_color=(0,0,0.15)
            l_color = bpy.context.scene.water_color_prop_floatv
            # report({'INFO'}, str("l_color:")+str(l_color))

            # Principal BSDFの立ち上げ
            pBSDF = material.node_tree.nodes["Principled BSDF"]

            # 色を設定
            pBSDF.inputs[0].default_value = (l_color[0],l_color[1],l_color[2],1)

            #metalic (水面は反射が多くなるようにメタリックを上げる)
            # pBSDF.inputs[6].default_value = 0.9
            pBSDF.inputs[6].default_value = bpy.context.scene.water_metalic_prop_float

            #粗さ（地面は光が反射しないため粗い方(1に近い方)がよい）
            # pBSDF.inputs[9].default_value = 0.02
            pBSDF.inputs[9].default_value = bpy.context.scene.water_roughness_prop_float

            # アルファチャンネル（透明度）の値を0.1に設定
            # pBSDF.inputs['Alpha'].default_value = 0.9

            set_alpha=bpy.context.scene.water_alpha_prop_float+(color_set[2] + depth)/((color_set[1] - color_set[2])*3)
            # set_alpha=0.6+(color_set[2] + depth)/((color_set[1] - color_set[2])*3)
            pBSDF.inputs['Alpha'].default_value = set_alpha
            print(set_alpha)

            #カラーコンター用のマテリアルリストに追加
            mat_list.append(mat_name)

    return mat_list


#カラーコンター用のマテリアルの作成
def color_mesh(obj,faces_depth,mat_list,color_set):
    mesh = obj.data
    d_depth=(color_set[1]-color_set[2])/(color_set[0]-2)

    #マテリアルをオブジェクトの設定
    for mat_name in mat_list:
        material = bpy.data.materials.get(mat_name)
        obj.data.materials.append(material)

    #水深によってセル(face)に設定する色を変える
    j=0
    for face in mesh.polygons:
        for k in range(1,len(mat_list)-1):
            if faces_depth[j][4] > d_depth*k+color_set[2] and faces_depth[j][4]<=d_depth*k+1+color_set[2]:
                matindex=k

        if faces_depth[j][4] <= d_depth*1+color_set[2]:
            matindex=0

        if faces_depth[j][4] >  d_depth*(len(mat_list)-2)+color_set[2]:
            matindex=20

        # 面に使用するマテリアルを設定する
        face.material_index = matindex

        j+=1



def mofifiers_on(obj):
    #モディファイヤーを追加。今回はサブディビジョンサーフェスを適応。（ポリゴンが細分化されて表面がなめらかになる）
    obj.modifiers.new("subd", type='SUBSURF')
    obj.modifiers['subd'].levels = 3
    

def voronoi_on(obj):
    #モディファイヤーを追加。DISPLACEのVoronoiを追加。水面のさざなみを表現
    """https://ja.blingin.in/blender_threads/questions/118250/link-a-texture-to-displace-modifier-using-python"""
    tex = bpy.data.textures.new("Voronoi", 'VORONOI')
    tex.distance_metric = 'DISTANCE_SQUARED'
    modifier = obj.modifiers.new(name="Displace", type='DISPLACE')
    modifier.texture = bpy.data.textures['Voronoi']
    
    # import random
    # """ゆらめき用"""
    # # modifier.strength = 0.05 +random.random()*0.01
    # modifier.strength = 0.3 +random.random()*0.1
    # modifier.mid_level = 0.

    modifier.strength = 3
    modifier.mid_level = 0.
    # modifier.noise_scale = 10
    bpy.data.textures["Voronoi"].noise_intensity = 1
    bpy.data.textures["Voronoi"].noise_scale = 10