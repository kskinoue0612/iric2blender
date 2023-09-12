import bpy
import numpy as np
import pyproj
from bpy.props import FloatVectorProperty, StringProperty
import json
import requests
import os
from os import path


# from . import material

# iricの計算結果をblenderのimport
class Download_OsmBuilding(bpy.types.Operator):
    # ラベル名の宣言
    bl_idname = "object.download_osm_building"
    bl_label = "2-1-1: OSMBuildingから建物データをダウンロード"
    bl_description = "2-1-1: OSMBuildingから建物データをダウンロード"
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

        def return_a_np_max_min(filename, EPSG_before, EPSG_after):
            df = read_file(filename)
            df = np.array(df[:, 3:7])
            df = np.delete(df, 2, 1)
            a_np_max_min = max_min_lonlat(df)

            for i in a_np_max_min:
                i = i[::-1]

            for i in range(len(a_np_max_min)):
                # a_np_max_min[i][1],a_np_max_min[i][0] = use_pyproj(a_np_max_min[i][1],a_np_max_min[i][0], "6677", "4326")
                a_np_max_min[i][1], a_np_max_min[i][0] = use_pyproj(a_np_max_min[i][1], a_np_max_min[i][0], EPSG_before, EPSG_after)

            return a_np_max_min

        def read_file(readfile):
            # ３行目以降を読み込みdfとする
            df = np.loadtxt(readfile, delimiter=',', skiprows=3)
            # df = np.loadtxt(readfile, delimiter=',',skiprows=3, usecols=[0,1,2,3,4,5,6,7,8,9,10,11])
            return df

        def max_min_lonlat(a_np):
            y_max = np.max(a_np, axis=0)[0]
            y_min = np.min(a_np, axis=0)[0]
            x_max = np.max(a_np, axis=0)[1]
            x_min = np.min(a_np, axis=0)[1]
            a_np_a = np.array([[x_max, y_max], [x_min, y_min]])
            return a_np_a

        def use_pyproj(x_lon, y_lat, EPSG_before, EPSG_after):
            EPSG_before = pyproj.Proj(f"+init=EPSG:{EPSG_before}")
            EPSG_after = pyproj.Proj(f"+init=EPSG:{EPSG_after}")
            y_lat_a, x_lon_a = pyproj.transform(EPSG_before, EPSG_after, x_lon, y_lat)
            return x_lon_a, y_lat_a

        def make_out_building_obs_iric(a_np_max_min, zoom, filepath_folder, EPSG_before, EPSG_after):
            xy_max_min = return_xy_max_min(a_np_max_min)
            read_url = make_url_list(xy_max_min, zoom)
            array2 = make_building_data(read_url, EPSG_before, EPSG_after)
            array2 = np.append(np.array(["pid", "vid", "x", "y", "name", "value"]), array2, axis=0)
            array2 = array2.reshape(-1, 6)  # 一次元配列から6次元配列へ変換（行数未指定-1）
            np.savetxt(f'{filepath_folder}/out_building_obs_iric.csv', array2, fmt="%s", delimiter=',', encoding='utf-8')  # 文字列が含まれているため fmt="%s"

        def return_xy_max_min(a_np_max_min):
            x1, y1 = latlon2tile2(a_np_max_min[0][0], a_np_max_min[0][1], zoom)
            x2, y2 = latlon2tile2(a_np_max_min[1][0], a_np_max_min[1][1], zoom)
            xy_max_min = np.array([[x1, x2], [y1, y2]])  # numpy配列に変換
            xy_max_min = np.sort(xy_max_min, axis=1)  # 行ごとにソート
            print(xy_max_min)
            # xy_max_min = [[29240,29244],[12021,12022]]
            return xy_max_min

        def latlon2tile2(x_lon, y_lat, zoom):
            """openstreetmap用"""
            # x = int((x_lon / 180 + 1) * 2**zoom / 2) # x座標
            # y = int(((-np.log(np.tan((45 + y_lat / 2) * np.pi / 180)) + np.pi) * 2**zoom / (2 * np.pi))) # y座標

            x = int((x_lon / 180 + 1) * 2**(zoom) / 2)  # x座標
            y = int(((-np.log(np.tan((45 + y_lat / 2) * np.pi / 180)) + np.pi) * 2**(zoom) / (2 * np.pi)))  # y座標

            return x, y

        def make_url_list(array1, zoom):
            read_url = []
            for x in range(array1[0][0], array1[0][1]):
                for y in range(array1[1][0], array1[1][1]):
                    # print(x,y)
                    read_url.append(f"https://data.osmbuildings.org/0.2/anonymous/tile/{zoom}/{x}/{y}.json")
            # print(read_url)
            self.report({'INFO'}, f"read_url:{read_url}")
            return read_url

        def make_building_data(read_url, EPSG_before, EPSG_after):
            n = 0
            array2 = np.empty(0)
            # bar = tqdm(total = len(read_url))

            for url in read_url:
                try:
                    # print(f"reading {url}")
                    json_data = load_osmbuildings_json(url)
                    array1, n = osmbuildings_json2building_npdata(json_data, n, EPSG_before, EPSG_after)
                    # print(array1)
                except:
                    print(f"read error {url}")
                    array1 = np.empty(0)
                    # print(array1)

                array2 = np.append(array2, array1, axis=0)
                # bar.update(1)

            # print("##",array2)
            self.report({'INFO'}, f"array2:{array2}")
            return array2

        def load_osmbuildings_json(url):
            agentheader = {'User-Agent': 'PostmanRuntime/7.28.4'}
            response = requests.get(url, headers=agentheader)
            data = json.loads(response.text)
            self.report({'INFO'}, f"data:{data}")

            return data

        def osmbuildings_json2building_npdata(data, n, EPSG_before, EPSG_after):
            array2 = np.empty(0)
            for i in range(len(data["features"])):

                try:
                    j1 = str(f'{data["features"][i]["id"]}')
                except:
                    j1 = str(f'{data["features"][i]["id"]}')

                j2 = str(f'{data["features"][i]["properties"]["height"]}')

                k = 0
                for j3 in data["features"][i]["geometry"]["coordinates"][0]:
                    j3[1], j3[0] = use_pyproj(j3[0], j3[1], EPSG_after, EPSG_before)
                    array1 = np.array([n, k, j3[0], j3[1], j1, 1])  # iric用
                    array2 = np.append(array2, array1, axis=0)
                    k += 1
                n += 1
            # pid	vid	x	y	name	value
            # 1	0	-77490.03125	-108975.7031	obj_1	1
            # 1	1	-77496.78125	-108979.8047	obj_1	1

            # 0	202548889	10.8	141.247742	43.149507
            # 0	202548889	10.8	141.247428	43.149732

            # array2 = array2.reshape(-1, 5) #一次元配列から５次元配列へ変換（行数未指定-1）
            return array2, n

        #######################
        # ファイルパスをフォルダパスとファイル名に分割する
        filepath_folder, filepath_name = os.path.split(self.filepath)
        # ファイルパスをフォルダ名の名称とファイル名の拡張子に分割する
        filepath_nameonly, filepath_ext = os.path.splitext(filepath_name)

        # zoom = 16 #1~18, #DEMは1~14
        zoom = bpy.context.scene.dl_image_zoom_prop_int
        EPSG_before = bpy.context.scene.dl_image_epsg_prop_int
        EPSG_after = "4326"

        a_np_max_min = return_a_np_max_min(self.filepath, EPSG_before, EPSG_after)

        self.report({'INFO'}, f"a_np_max_min:{a_np_max_min}")
        self.report({'INFO'}, f"EPSG_before:{EPSG_before}")
        self.report({'INFO'}, f"EPSG_after:{EPSG_after}")
        self.report({'INFO'}, f"ZOOM:{zoom}")

        make_out_building_obs_iric(a_np_max_min, zoom, filepath_folder, EPSG_before, EPSG_after)

        return {'FINISHED'}
