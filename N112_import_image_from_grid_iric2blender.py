# ライブラリの読み込み
import bpy
from bpy.props import FloatVectorProperty, StringProperty
import os
from os import path
import numpy as np
from mathutils import Vector
import pyproj
from staticmap import StaticMap
import matplotlib.pyplot as plt


# iricの計算結果をblenderのimport
class Import_Image_from_Grid_iRIC2blender(bpy.types.Operator):
    # ラベル名の宣言
    bl_idname = "object.import_image_from_grid_iric2blender"
    bl_label = "1-1-2: iRIC格子(csv)から画像をダウンロード"
    bl_description = "1-1-2: iRIC格子(csv)から画像をダウンロード"
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

        ######

        def read_file(readfile):
            # ３行目以降を読み込みdfとする
            df = np.loadtxt(readfile, delimiter=',', skiprows=3)
            # df = np.loadtxt(readfile, delimiter=',',skiprows=3, usecols=[0,1,2,3,4,5,6,7,8,9,10,11])
            return df

        def use_pyproj(x_lon, y_lat, EPSG_before, EPSG_after):
            # x_lon = a_np[:,:1] #35.6
            # y_lat = a_np[:,1:2] #139.7
            EPSG_before = pyproj.Proj(f"+init=EPSG:{EPSG_before}")
            EPSG_after = pyproj.Proj(f"+init=EPSG:{EPSG_after}")
            y_lat_a, x_lon_a = pyproj.transform(EPSG_before, EPSG_after, x_lon, y_lat)
            return x_lon_a, y_lat_a

        def center_lonlat(a_np):
            a_np_a = np.average(a_np, axis=0)
            center = [a_np_a[1], a_np_a[0]]
            return center

        def center_lonlat2(a_np):
            # [[x_max,y_max],[x_min,y_min]]
            # a_np_a = np.average(a_np, axis = 0)
            # center = [a_np_a[1],a_np_a[0]]
            center = [(a_np[0][0] + a_np[1][0])/2., (a_np[0][1] + a_np[1][1])/2.]
            return center

        def max_min_lonlat(a_np):
            y_max = np.max(a_np, axis=0)[0]
            y_min = np.min(a_np, axis=0)[0]
            x_max = np.max(a_np, axis=0)[1]
            x_min = np.min(a_np, axis=0)[1]

            a_np_a = np.array([[x_max, y_max], [x_min, y_min]])
            return a_np_a

        def max_min_tile(a_np_max_min, z):
            x_max, y_max = latlon2tile(x_lon=a_np_max_min[0][0], y_lat=a_np_max_min[0][1], zoom=z)
            x_min, y_min = latlon2tile(x_lon=a_np_max_min[1][0], y_lat=a_np_max_min[1][1], zoom=z)

            a_np_max_min = np.array([[x_max, y_max], [x_min, y_min]])
            return a_np_max_min

        def tile_lx_ly(a_np_max_min):
            lx = int(np.sqrt((a_np_max_min[0][0] - a_np_max_min[1][0])**2))
            ly = int(np.sqrt((a_np_max_min[0][1] - a_np_max_min[1][1])**2))
            return lx, ly

        def simple_map(np_center, zoom1, dpi1, x_tile, y_tile, filepath_folder, image_url):
            """https://blog.shikoan.com/gsi-tile/"""
            """https://maps.gsi.go.jp/development/ichiran.html"""
            # URL：https://cyberjapandata.gsi.go.jp/xyz/seamlessphoto/{z}/{x}/{y}.jpg

            # url=["https://cyberjapandata.gsi.go.jp/xyz/seamlessphoto/{z}/{x}/{y}.jpg",
            #      "http://cyberjapandata.gsi.go.jp/xyz/dem/{z}/{x}/{y}.txt",
            #      "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"]

            # url = {
            #        'chiriin_seamlessphoto'    : "https://cyberjapandata.gsi.go.jp/xyz/seamlessphoto/{z}/{x}/{y}.jpg",
            #        'chiriin_nendophoto'       : "https://cyberjapandata.gsi.go.jp/xyz/nendophoto2019/{z}/{x}/{y}.png",
            #        'gazo4'                    : "https://cyberjapandata.gsi.go.jp/xyz/gazo4/{z}/{x}/{y}.jpg",
            #        'ort_USA10'                : "https://cyberjapandata.gsi.go.jp/xyz/ort_USA10/{z}/{x}/{y}.png",
            #        'ort'                      : "https://cyberjapandata.gsi.go.jp/xyz/ort/{z}/{x}/{y}.jpg",
            #        'google_satellite'         : 'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
            #        'google_satellite_hybrid'  : 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
            #        }

            # 地理院地図タイル 横1280x縦720
            # map = StaticMap(x_tile, y_tile, url_template=url["chiriin_seamlessphoto"])
            # map = StaticMap(x_tile, y_tile, url_template=url["google_satellite"])
            map = StaticMap(x_tile, y_tile, url_template=image_url)

            # ズームレベル12、中心画像は「東経, 北緯」→PILのインスタンスとして返ってくる
            img = map.render(zoom=zoom1, center=np_center)
            # img = map.render(zoom=18, center=[143.202056, 42.918])

            # 表示
            plt.gca().spines['right'].set_visible(False)
            plt.gca().spines['top'].set_visible(False)
            plt.gca().spines['bottom'].set_visible(False)
            plt.gca().spines['left'].set_visible(False)

            plt.tick_params(labelbottom=False, labelleft=False, labelright=False, labeltop=False, bottom=False, left=False, right=False, top=False)
            plt.subplots_adjust(left=0, right=1, bottom=0, top=1)
            plt.imshow(img)
            # plt.show()
            save_filename = f"{filepath_folder}/iric_image_{zoom1}_{dpi1}.tiff"
            plt.savefig(save_filename, dpi=dpi1, bbox_inches='tight', pad_inches=0)

            self.report({'INFO'}, f"saved {save_filename}")

        def simple_map_dem(np_center, zoom1, x_tile, y_tile):
            """https://blog.shikoan.com/gsi-tile/"""
            """https://maps.gsi.go.jp/development/ichiran.html"""
            """https://cyberjapandata.gsi.go.jp/xyz/dem/14/14255/6519.txt"""
            # URL：https://cyberjapandata.gsi.go.jp/xyz/seamlessphoto/{z}/{x}/{y}.jpg

            url = {
                'chiriin_dem': "https://cyberjapandata.gsi.go.jp/xyz/dem/{z}/{x}/{y}.txt"
            }

            print(x_tile, y_tile)

            # 地理院地図タイル 横1280x縦720
            map = StaticMap(x_tile, y_tile, url_template=url["chiriin_dem"])
            print(map)

            # ズームレベル12、中心画像は「東経, 北緯」→PILのインスタンスとして返ってくる
            img = map.render(zoom=zoom1, center=np_center)
            print(img)

        def openstreetmap_building():
            """https://osmbuildings.org/documentation/data/"""
            """https://data.osmbuildings.org/0.2/anonymous/tile/15/17605/10743.json"""
            """https://data.osmbuildings.org/0.2/anonymous/tile/15/{x}/{y}.json"""

        def Lon2Tile(lon, zoom):
            """https://www.trail-note.net/tech/coordinate/"""
            """https://maps.multisoup.co.jp/blog/3944/"""
            """https://note.sngklab.jp/?p=72"""

            return ((lon + 180) / 360) * pow(2, zoom)

        def latlon2tile(x_lon, y_lat, zoom):
            # x = int((x_lon / 180 + 1) * 2**zoom / 2) # x座標
            # y = int(((-np.log(np.tan((45 + y_lat / 2) * np.pi / 180)) + np.pi) * 2**zoom / (2 * np.pi))) # y座標

            x = int((x_lon / 180 + 1) * 2**(zoom+8) / 2)  # x座標
            y = int(((-np.log(np.tan((45 + y_lat / 2) * np.pi / 180)) + np.pi) * 2**(zoom+8) / (2 * np.pi)))  # y座標

            return x, y

        def latlon2tile2(x_lon, y_lat, zoom):
            """openstreetmap用"""
            # x = int((x_lon / 180 + 1) * 2**zoom / 2) # x座標
            # y = int(((-np.log(np.tan((45 + y_lat / 2) * np.pi / 180)) + np.pi) * 2**zoom / (2 * np.pi))) # y座標

            x = int((x_lon / 180 + 1) * 2**(zoom) / 2)  # x座標
            y = int(((-np.log(np.tan((45 + y_lat / 2) * np.pi / 180)) + np.pi) * 2**(zoom) / (2 * np.pi)))  # y座標

            return x, y

        def tile2latlon(x, y, z):
            from math import pi
            from math import e
            from math import atan

            lon = (x / 2.0**z) * 360 - 180  # 経度（東経）
            mapy = (y / 2.0**z) * 2 * pi - pi
            lat = 2 * atan(e ** (- mapy)) * 180 / pi - 90  # 緯度（北緯）
            print(lon, lat)

        def get_satelite_image(zoom, dpi1, a_np_max_min, filepath_folder, image_url):
            # 中心点
            a_np_center = center_lonlat2(a_np_max_min)

            # 解像度の算出
            a_np_max_min = max_min_tile(a_np_max_min, z=zoom)
            lx, ly = tile_lx_ly(a_np_max_min)

            # 写真
            simple_map(a_np_center, zoom1=zoom, dpi1=dpi1, x_tile=lx, y_tile=ly, filepath_folder=filepath_folder, image_url=image_url)

        def get_dem(zoom, a_np_max_min):
            # 中心点
            a_np_center = center_lonlat2(a_np_max_min)

            # 解像度の算出
            a_np_max_min = max_min_tile(a_np_max_min, z=zoom)
            lx, ly = tile_lx_ly(a_np_max_min)
            print(a_np_max_min)
            # DEM
            simple_map_dem(a_np_center, zoom1=zoom, x_tile=lx, y_tile=ly)

        def return_a_np_max_min(filename, EPSG_before, EPSG_after):
            df = read_file(filename)
            df = np.array(df[:, 3:7])
            df = np.delete(df, 2, 1)
            a_np_max_min = max_min_lonlat(df)

            for i in a_np_max_min:
                i = i[::-1]

            for i in range(len(a_np_max_min)):
                a_np_max_min[i][1], a_np_max_min[i][0] = use_pyproj(a_np_max_min[i][1], a_np_max_min[i][0], EPSG_before, EPSG_after)
                # a_np_max_min[i][1],a_np_max_min[i][0] = use_pyproj(a_np_max_min[i][1],a_np_max_min[i][0], "32611", "4326")
                # a_np_max_min[i][1],a_np_max_min[i][0] = use_pyproj(a_np_max_min[i][1],a_np_max_min[i][0], "6676", "4326")

            print("###", a_np_max_min)
            return a_np_max_min

        def return_a_np_max_min_from_blender(filename):
            df = read_file(filename)
            # df = np.array(df[:,3:7])
            # df = np.delete(df, 2, 1)
            a_np_max_min = max_min_lonlat(df)
            print(a_np_max_min)

            # for i in a_np_max_min:
            #     i=i[::-1]

            for i in range(len(a_np_max_min)):
                a_np_max_min[i][1], a_np_max_min[i][0] = use_pyproj(a_np_max_min[i][1], a_np_max_min[i][0], "6680", "4326")
                # a_np_max_min[i][1],a_np_max_min[i][0] = use_pyproj(a_np_max_min[i][1],a_np_max_min[i][0], "6676", "4326")

            print("###", a_np_max_min)
            return a_np_max_min

        def load_osmbuildings_json(url):
            import json
            import requests

            # def config():
            #     url = f"https://data.osmbuildings.org/0.2/anonymous/tile/15/{x}/{y}.json"
            #     agentheader={'User-Agent': 'PostmanRuntime/7.28.4'}
            #     return url,agentheader
            #
            # url, agentheader = config()

            agentheader = {'User-Agent': 'PostmanRuntime/7.28.4'}
            response = requests.get(url, headers=agentheader)
            # print(response.status_code)
            # print(response.text)
            data = json.loads(response.text)
            # print(data["features"])
            return data

        def osmbuildings_json2building_npdata(data):
            array2 = np.empty(0)

            for i in range(len(data["features"])):
                try:
                    j1 = str(f'{data["features"][i]["id"]}({data["features"][i]["properties"]["name"]})')
                except:
                    j1 = str(f'{data["features"][i]["id"]}')

                j2 = str(f'{data["features"][i]["properties"]["height"]}')
                for j3 in data["features"][i]["geometry"]["coordinates"][0]:
                    array1 = np.array([i, j1, j2, j3[0], j3[1]])  # numpy配列に変換
                    array2 = np.append(array2, array1, axis=0)

            array2 = array2.reshape(-1, 5)  # 一次元配列から５次元配列へ変換（行数未指定-1）
            return array2

        ################
        # active_obj = context.active_object

        # ファイルパスをフォルダパスとファイル名に分割する
        filepath_folder, filepath_name = os.path.split(self.filepath)
        # ファイルパスをフォルダ名の名称とファイル名の拡張子に分割する
        filepath_nameonly, filepath_ext = os.path.splitext(filepath_name)

        # setting
        zoom = bpy.context.scene.dl_image_zoom_prop_int
        dpi = bpy.context.scene.dl_image_dpi_prop_int
        EPSG_before = bpy.context.scene.dl_image_epsg_prop_int
        EPSG_after = "4326"

        # url = {
        #         'chiriin_seamlessphoto'    : "https://cyberjapandata.gsi.go.jp/xyz/seamlessphoto/{z}/{x}/{y}.jpg",
        #         'chiriin_nendophoto'       : "https://cyberjapandata.gsi.go.jp/xyz/nendophoto2019/{z}/{x}/{y}.png",
        #         'gazo4'                    : "https://cyberjapandata.gsi.go.jp/xyz/gazo4/{z}/{x}/{y}.jpg",
        #         'ort_USA10'                : "https://cyberjapandata.gsi.go.jp/xyz/ort_USA10/{z}/{x}/{y}.png",
        #         'ort'                      : "https://cyberjapandata.gsi.go.jp/xyz/ort/{z}/{x}/{y}.jpg",
        #         'google_satellite'         : 'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        #         'google_satellite_hybrid'  : 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        #         }
        #
        # image_url=url["google_satellite"]

        url = {
            1: 'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
            2: 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
            3: "https://cyberjapandata.gsi.go.jp/xyz/seamlessphoto/{z}/{x}/{y}.jpg",
        }

        image_url = url[bpy.context.scene.dl_image_url_prop_int]

        self.report({'INFO'}, f"start downloading image {self.filepath}")
        self.report({'INFO'}, f"setting as zoom:{zoom}, dpi:{dpi}")

        # read file
        a_np_max_min = return_a_np_max_min(self.filepath, EPSG_before, EPSG_after)
        get_satelite_image(zoom, dpi, a_np_max_min, filepath_folder, image_url)

        return {'FINISHED'}
