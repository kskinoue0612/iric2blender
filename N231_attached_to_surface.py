import bpy
from bpy.props import FloatVectorProperty, StringProperty
from . import material
import os
from os import path
import numpy as np
from mathutils import Vector


class Attached_to_Surface(bpy.types.Operator):
    # ラベル名の宣言
    bl_idname = "object.attached_to_sureface"
    bl_label = "2-3-1: 選択したオブジェクトを接地"
    bl_description = "2-3-1: 選択したオブジェクトを接地"
    bl_options = {'REGISTER', 'UNDO'}

    # 実行ファイル（選択しているオブジェクトの地形データをiricの点群csvに書き出し）

    def execute(self, context):

        def raycast_attached_sureface_z_from_obs(obs):
            for ob in obs:
                # 初期化
                l = 0
                temp_h = 5000
                ray_distance = -10000

                h_brdg_list = []
                for v in ob.data.vertices:
                    brdg_location = ob.matrix_world.inverted() @ v.co
                    # brdg_location=ob.matrix_world.inverted() @v.co*-1

                    h_brdg_list.append(brdg_location[2])
                h_brdg = np.sqrt((max(h_brdg_list)-min(h_brdg_list))**2)

                obz_surface = []
                for v in ob.data.vertices:
                    # グローバル座標を指定オブジェクトのローカル座標に変換する
                    obx, oby, obz = ob.matrix_world.inverted() @ v.co

                    # raycastの起点とdiractionを設定
                    # オブジェクトを一時的に上空に上げる
                    ray_begin_local = Vector((obx, oby, obz+temp_h - 1))

                    # raycastの方向（下方向のベクトルを設定）
                    ray_direction = Vector((0, 0, ray_distance))

                    # raycast実行
                    raycast_result = bpy.context.scene.ray_cast(bpy.context.view_layer.depsgraph, ray_begin_local, ray_direction)

                    # オブジェクトの下に接地面がある場合の処理
                    if raycast_result[0] == True:
                        obz_surface.append(raycast_result[1][2])

                    # 接地座標の可視化
                    # bpy.ops.object.empty_add(type='PLAIN_AXES', radius=1.0, align='WORLD', location=raycast_result[1], rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0))

                # オブジェクトの高さを接地面の高さに反映
                try:
                    # ob.location[2]=min(obz_surface)+(h_brdg*0.5)
                    ob.location[2] = min(obz_surface)

                except:
                    pass
            return obs

        #####
        # active_obj = context.active_object

        obs = bpy.context.selected_objects  # 選択したオブジェクト

        # raycastの実行
        obs = raycast_attached_sureface_z_from_obs(obs)

        return {'FINISHED'}
