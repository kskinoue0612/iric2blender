# -*- coding:utf-8 -*-

#  ***** GPL LICENSE BLOCK *****
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#  ***** GPL LICENSE BLOCK *****


# Blenderアドオンに関する情報の宣言・設定
bl_info = {
    "name": "iric2blender",
    "author": "Toshiyuki Tanaka",
    "version": (3, 0),
    "blender": (3, 2, 2),
    "location": "3Dビュー > オブジェクト",
    "description": "iRICとblenderの相互連携用アドオン",
    "warning": "",
    "support": "TESTING",
    "wiki_url": "",
    "tracker_url": "",
	'category': '3D View'
}




#iRIC2Blenderの各種ライブラリの読み込み
if "bpy" in locals():
    import imp
    imp.reload(N111_import_grid_iric2blender)
    imp.reload(N112_import_image_from_grid_iric2blender)
    imp.reload(N121_import_image2object_iric2blender)
    imp.reload(N131_import_grid_tree_iric2blender)
    imp.reload(N211_download_osm_building)
    imp.reload(N212_import_osm_building2blender)
    imp.reload(N221_import_plataue_obj_dem)
    imp.reload(N222_import_plataue_obj_building)
    imp.reload(N231_attached_to_surface)
    imp.reload(N311_import_result2DH_color_iric2blender)
    imp.reload(N312_import_result2DH_velocity_color_iric2blender)
    imp.reload(N313_import_result2DH_blue_iric2blender)
    imp.reload(N314_import_result2DH_dem_iric2blender)
    imp.reload(N321_import_resultFLOOD_iric2blender_color)
    imp.reload(N322_import_resultFLOOD_iric2blender_velocity_color)
    imp.reload(N323_import_resultFLOOD_iric2blender_blue)
    imp.reload(N410_export_tpo2iric)
    imp.reload(N420_export_building2iric)
    imp.reload(material)

else:
    from . import N111_import_grid_iric2blender
    from . import N112_import_image_from_grid_iric2blender
    from . import N121_import_image2object_iric2blender
    from . import N131_import_grid_tree_iric2blender
    from . import N211_download_osm_building
    from . import N212_import_osm_building2blender
    from . import N221_import_plataue_obj_dem
    from . import N222_import_plataue_obj_building
    from . import N311_import_result2DH_color_iric2blender
    from . import N312_import_result2DH_velocity_color_iric2blender
    from . import N313_import_result2DH_blue_iric2blender
    from . import N314_import_result2DH_dem_iric2blender
    from . import N321_import_resultFLOOD_iric2blender_color
    from . import N322_import_resultFLOOD_iric2blender_velocity_color
    from . import N323_import_resultFLOOD_iric2blender_blue
    from . import N231_attached_to_surface
    from . import N410_export_tpo2iric
    from . import N420_export_building2iric
    from . import material



#### main ####
import bpy
from bpy.props import *


# サイドパネル(iRIC_setting)のインタフェース等の設定
class IRICSETTING_PT_CustomPanel(bpy.types.Panel):

    bl_label = "iRIC2blender_setting"         # パネルのヘッダに表示される文字列
    bl_space_type = 'VIEW_3D'           # パネルを登録するスペース
    bl_region_type = 'UI'               # パネルを登録するリージョン
    bl_category = "iRIC_setting"        # パネルを登録するタブ名
    bl_context = "objectmode"           # パネルを表示するコンテキスト



    # ヘッダーのカスタマイズ
    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='PLUGIN')

    # メニューの描画処理
    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # 閾値の設定
        layout.separator()
        layout.label(text="閾値の設定:")
        layout.prop(scene, "para_prop_float", text="para")
        
        # 植生描画量の設定
        layout.separator()
        layout.label(text="植生描画量の設定:")
        layout.label(text="1:All")
        layout.label(text="0:Random")
        layout.label(text="2~100:n個に一度描画")
        layout.prop(scene, "va_prop_int", text="v_amount")
        
        # 植生の3Dモデルの設定
        layout.separator()
        layout.label(text="植生3Dモデルの設定:")
        layout.label(text="1:light")
        layout.label(text="2:heavy")
        layout.prop(scene, "vm_prop_int", text="v_model")

        # コンターの水深の設定
        layout.separator()
        layout.label(text="コンター水深の設定:")
        layout.prop(scene, "max_depth_prop_float", text="max_depth")
        layout.prop(scene, "min_depth_prop_float", text="min_depth")

        # コンターの流速の設定
        layout.separator()
        layout.label(text="コンターの流速の設定:")
        layout.prop(scene, "max_velocity_prop_float", text="max_velocity")
        layout.prop(scene, "min_velocity_prop_float", text="min_velocity")


        # 水の色の設定
        layout.separator()
        layout.label(text="水の色の設定:")
        layout.prop(scene, "water_color_prop_floatv", text="water_color")
        layout.separator()

        # 水の粗さの設定
        layout.separator()
        layout.label(text="水面の粗さの設定:")
        layout.prop(scene, "water_roughness_prop_float", text="water_roughness")

        # 水の反射の設定
        layout.separator()
        layout.label(text="水面の反射の設定:")
        layout.prop(scene, "water_metalic_prop_float", text="water_metalic")

        # 水の透過の設定
        layout.separator()
        layout.label(text="水面の透過の設定:")
        layout.prop(scene, "water_alpha_prop_float", text="water_alpha")

        # 画像読み込み設定
        layout.separator()
        layout.separator()
        layout.label(text="画像読み込み関係")
        layout.label(text="DL画像のzoomの設定:")
        layout.prop(scene, "dl_image_zoom_prop_int", text="zoom")

        layout.separator()
        layout.label(text="DL画像の解像度の設定:")
        layout.prop(scene, "dl_image_dpi_prop_int", text="dpi")

        layout.separator()
        layout.label(text="格子のEPSGの設定:")
        layout.prop(scene, "dl_image_epsg_prop_int", text="epsg")

        layout.separator()
        layout.label(text="読み込み画像の設定:")
        layout.label(text="1:google衛星画像")
        layout.label(text="2:google hybrid")
        layout.label(text="3:国土地理院オルソ画像")
        layout.prop(scene, "dl_image_url_prop_int", text="url")

        layout.separator()
        layout.label(text="木の種類の設定:")
        layout.prop(scene, "dl_tree_type_prop_int", text="tree")

#############
# サイドパネル(iRIC_setting)のプロパティの初期化
def init_props():
    scene = bpy.types.Scene

    scene.para_prop_float = FloatProperty(
        name="para",
        description="プロパティ（float）",
        default=0.5,
        min=0.01,
        max=1.0
    )
    
    scene.va_prop_int = IntProperty(
        name="v_amount",
        description="プロパティ（int）",
        default=1,
        min=0,
        max=100
    )

    scene.vm_prop_int = IntProperty(
        name="v_model",
        description="プロパティ（int）",
        default=1,
        min=1,
        max=2
    )

    scene.max_depth_prop_float = FloatProperty(
        name="max_depth",
        description="プロパティ（float）",
        default=4.0,
        min=0.01,
        max=50.0
    )
    scene.min_depth_prop_float = FloatProperty(
        name="min_depth",
        description="プロパティ（float）",
        default=0.1,
        min=0.01,
        max=50.0
    )
    scene.max_velocity_prop_float = FloatProperty(
        name="max_depth",
        description="プロパティ（float）",
        default=5.,
        min=0.01,
        max=50.0
    )
    scene.min_velocity_prop_float = FloatProperty(
        name="min_depth",
        description="プロパティ（float）",
        default=0.1,
        min=0.01,
        max=50.0
    )

    scene.water_color_prop_floatv = FloatVectorProperty(
        name="プロパティ 3",
        description="プロパティ（float vector）",
        subtype='COLOR_GAMMA',
        # default=(0., 0., 1.0),
        default=(0,0,0.15),
        min=0.0,
        max=1.0
    )
    scene.water_roughness_prop_float = FloatProperty(
        name="roughness",
        description="プロパティ（float）",
        default=0.02,
        min=0.,
        max=1.
    )
    scene.water_metalic_prop_float = FloatProperty(
        name="metalic",
        description="プロパティ（float）",
        default=0.9,
        min=0.,
        max=1.
    )
    scene.water_alpha_prop_float = FloatProperty(
        name="alpha",
        description="プロパティ（float）",
        default=0.6,
        min=0.,
        max=1.
    )

    scene.dl_image_zoom_prop_int = IntProperty(
        name="zoom",
        description="プロパティ（int）",
        default=13,
        min=1,
        max=21
    )

    scene.dl_image_dpi_prop_int = IntProperty(
        name="dpi",
        description="プロパティ（int）",
        default=1000,
        min=10,
        max=8000
    )

    scene.dl_image_epsg_prop_int = IntProperty(
        name="epsg",
        description="プロパティ（int）",
        default=4326,
        min=0,
        max=100000
    )
    scene.dl_image_url_prop_int = IntProperty(
        name="url",
        description="プロパティ（int）",
        default=1,
        min=1,
        max=3
    )

    scene.dl_tree_type_prop_int = IntProperty(
        name="tree",
        description="プロパティ（int）",
        default=4,
        min=0,
        max=5
    )




# プロパティを削除
def clear_props():
    scene = bpy.types.Scene
    del scene.para_prop_float
    del scene.va_prop_int
    del scene.vm_prop_int
    del scene.max_depth_prop_float
    del scene.min_depth_prop_float
    del scene.max_velocity_prop_float
    del scene.min_velocity_prop_float
    del scene.water_color_prop_floatv
    del scene.water_roughness_prop_float
    del scene.water_metalic_prop_float
    del scene.water_alpha_prop_float
    del scene.dl_image_zoom_prop_int
    del scene.dl_image_dpi_prop_int
    del scene.dl_image_epsg_prop_int
    del scene.dl_image_url_prop_int
    del scene.dl_tree_type_prop_int


#############



###############
#iRICタブのインタフェース等の設定
class VIEW3D_MT_menu_iric(bpy.types.Menu):
	bl_label = "iRIC"
	# Set the menu operators and draw functions
	def draw(self, context):
		layout = self.layout

		#メニューに表示するclass名の登録
		for c in clases:
			if c == "separator":
				layout.separator()
			else:
				self.layout.operator(c.bl_idname)

		layout.separator()
		#メニューに表示するclass名の登録
		for c in clases:
			# self.layout.operator(c.bl_idname)
			if c == "separator":
				layout.separator()
			else:
				self.layout.menu(c.bl_idname)
		layout.separator()


# class登録
clases=[N111_import_grid_iric2blender.ImportGrid_iRIC2blender,
        N112_import_image_from_grid_iric2blender.Import_Image_from_Grid_iRIC2blender,
        N121_import_image2object_iric2blender.Import_Image2Object_iRIC2blender,
        N131_import_grid_tree_iric2blender.ImportGridTree_iRIC2blender,
		"separator",
        N211_download_osm_building.Download_OsmBuilding,
        N212_import_osm_building2blender.Import_OsmBuilding2blender,
        N221_import_plataue_obj_dem.Import_Plataue_Obj_Dem,
        N222_import_plataue_obj_building.Import_Plataue_Obj_Buidling,
        N231_attached_to_surface.Attached_to_Surface,
        "separator",
        N311_import_result2DH_color_iric2blender.ImportResult2DH_Color_iRIC2blender,
        N312_import_result2DH_velocity_color_iric2blender.ImportResult2DH_velocity_Color_iRIC2blender,
        N313_import_result2DH_blue_iric2blender.ImportResult2DH_Blue_iRIC2blender,
        N314_import_result2DH_dem_iric2blender.ImportResult2DH_DEM_iRIC2blender,
		"separator",
        N321_import_resultFLOOD_iric2blender_color.ImportResult_iRIC2blender_color,
        N322_import_resultFLOOD_iric2blender_velocity_color.ImportResult_iRIC2blender_velocity_color,
        N323_import_resultFLOOD_iric2blender_blue.ImportResult_iRIC2blender_blue,
		"separator",
        N410_export_tpo2iric.ExportTpo2iRIC,
        N420_export_building2iric.ExportBuilding2iRIC
		]


clases_panel=[IRICSETTING_PT_CustomPanel
			  ]


menus=[VIEW3D_MT_menu_iric,
        N111_import_grid_iric2blender.ImportGrid_iRIC2blender,
        N112_import_image_from_grid_iric2blender.Import_Image_from_Grid_iRIC2blender,
        N121_import_image2object_iric2blender.Import_Image2Object_iRIC2blender,
        N131_import_grid_tree_iric2blender.ImportGridTree_iRIC2blender,
        N211_download_osm_building.Download_OsmBuilding,
        N212_import_osm_building2blender.Import_OsmBuilding2blender,
        N221_import_plataue_obj_dem.Import_Plataue_Obj_Dem,
        N222_import_plataue_obj_building.Import_Plataue_Obj_Buidling,
        N231_attached_to_surface.Attached_to_Surface,
        N311_import_result2DH_color_iric2blender.ImportResult2DH_Color_iRIC2blender,
        N312_import_result2DH_velocity_color_iric2blender.ImportResult2DH_velocity_Color_iRIC2blender,
        N313_import_result2DH_blue_iric2blender.ImportResult2DH_Blue_iRIC2blender,
        N314_import_result2DH_dem_iric2blender.ImportResult2DH_DEM_iRIC2blender,
        N321_import_resultFLOOD_iric2blender_color.ImportResult_iRIC2blender_color,
        N322_import_resultFLOOD_iric2blender_velocity_color.ImportResult_iRIC2blender_velocity_color,
        N323_import_resultFLOOD_iric2blender_blue.ImportResult_iRIC2blender_blue,
        N410_export_tpo2iric.ExportTpo2iRIC,
        N420_export_building2iric.ExportBuilding2iRIC
		]




def add_gis_menu(self, context):
	if context.mode == 'OBJECT':
		self.layout.menu('VIEW3D_MT_menu_iric')


#アドオンの登録設定
def register():
    init_props()

    for menu in menus:
        try:
            bpy.utils.register_class(menu)
        except ValueError as e:
            logger.warning('{} is already registered, now unregister and retry... '.format(menu))
            bpy.utils.unregister_class(menu)
            bpy.utils.register_class(menu)
    for c in clases_panel:
        try:
            bpy.utils.register_class(c)
        except ValueError as e:
            logger.warning('{} is already registered, now unregister and retry... '.format(menu))
            bpy.utils.unregister_class(c)
            bpy.utils.register_class(c)

    #menus
    bpy.types.VIEW3D_MT_editor_menus.append(add_gis_menu)



def unregister():
    bpy.types.VIEW3D_MT_editor_menus.remove(add_gis_menu)
    clear_props()

    for menu in menus:
        bpy.utils.unregister_class(menu)
    for c in clases_panel:
        bpy.utils.unregister_class(c)


######
if __name__ == "__main__":
	register()
