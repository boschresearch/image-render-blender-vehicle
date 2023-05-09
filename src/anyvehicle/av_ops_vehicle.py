#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \modules\anyblend\av_ops_vehicle.py
# Created Date: Tuesday, February 16th 2021, 11:11:18 am
# Author: Christian Perwass (CR/AEC5)
# <LICENSE id="GPL-3.0">
#
#   Image-Render Blender Vehicle Animation add-on module
#   Copyright (C) 2022 Robert Bosch GmbH and its subsidiaries
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#
# </LICENSE>
###

import bpy
from bpy.app.handlers import persistent

import mathutils
import pyjson5 as json
from . import av_global
from .anim import path as animpath
import anyblend

#######################################################################################
class AV_OP_Vehicle_CreateModel_4w(bpy.types.Operator):
    bl_idname = "av.vehicle_create_model_4w"
    bl_label = "Create 4 wheel model"
    bl_description = (
        "Click to create a vehicle model with origin at the currently active object."
    )

    def execute(self, context):
        objSel = bpy.context.active_object
        if objSel is not None:
            dicData = {
                "sType": "/catharsys/blender/animate/vehicle/path/4w/singletrack/planar:1.0",
                "sObjFAC": objSel.name,
                "sObjFAL": "",
                "sObjFAR": "",
                "sObjFALS": "",
                "sObjFARS": "",
                "sObjSAC": "",
                "sObjSAL": "",
                "sObjSAR": "",
                "sObjSALS": "",
                "sObjSARS": "",
                "sObjRot": "",
                "sObjNurbsPath": "",
                "iResolution": 10,
                "fWheelRadius": 1.0,
                "fMeanSpeed": 1.0,
                "fTimeOffset": 0.0,
            }

            objSel["AnyVehicle"] = json.dumps(dicData)
        # endif

        return {"FINISHED"}

    # enddef


# endclass


#######################################################################################
class AV_OP_Vehicle_CreateModel_2w(bpy.types.Operator):
    bl_idname = "av.vehicle_create_model_2w"
    bl_label = "Create 2 wheel model"
    bl_description = (
        "Click to create a vehicle model with origin at the currently active object."
    )

    def execute(self, context):
        objSel = bpy.context.active_object
        if objSel is not None:
            dicData = {
                "sType": "/catharsys/blender/animate/vehicle/path/2w/singletrack/planar:1.0",
                "sObjFAC": objSel.name,
                "sObjFAR": "",
                "sObjFAS": "",
                "sObjSAC": "",
                "sObjSAT": "",
                "sObjSATO": "",
                "sObjSATS": "",
                "sObjRot": "",
                "sObjNurbsPath": "",
                "iResolution": 10,
                "fWheelRadius": 1.0,
                "fMeanSpeed": 1.0,
                "fTimeOffset": 0.0,
            }

            objSel["AnyVehicle"] = json.dumps(dicData)
        # endif

        return {"FINISHED"}

    # enddef


# endclass


#######################################################################################
class AV_OP_Vehicle_RemoveModel(bpy.types.Operator):
    bl_idname = "av.vehicle_remove_model"
    bl_label = "Remove vehicle model"
    bl_description = "Click to remove the vehicle model."

    def execute(self, context):
        objSel = bpy.context.active_object
        if objSel is not None and objSel.get("AnyVehicle") is not None:
            del objSel["AnyVehicle"]
        # endif

        return {"FINISHED"}

    # enddef


# endclass


#######################################################################################
def handle_track(xScene, xDepsGraph):
    dFps = xScene.render.fps
    dTime = xScene.frame_current / dFps

    for sModel in av_global.dicVehicleModels:
        av_global.dicVehicleModels.get(sModel).SetObjectToTime(dTime)
    # endfor


# enddef


#######################################################################################
class AV_OP_Vehicle_EvalModelPath(bpy.types.Operator):

    bl_idname = "av.vehicle_eval_model_path"
    bl_label = "Evaluate Model Path"
    bl_description = "Click to evaluate the model movement along the path."

    def execute(self, context):
        objSel = bpy.context.active_object
        if objSel is None:
            return {"FINISHED"}
        # endif

        sName = objSel.name
        sModelData = objSel.get("AnyVehicle")
        if sModelData is None:
            self.report(
                {"ERROR"}, "Object '{0}' has no vehicle animation data.".format(sName)
            )
            return {"FINISHED"}
        # endif

        dicModel = json.loads(sModelData)
        sModelType = dicModel.get("sType")
        if sModelType is None:
            self.report(
                {"ERROR"},
                "Object '{0}' has invalid vehicle animation data.".format(sName),
            )
            return {"FINISHED"}
        # endif

        anyblend.anim.util.RegisterAnimObject(
            sName, dicModel, animpath.CreateAnimHandler
        )

        return {"FINISHED"}

    # enddef


# endclass


#######################################################################################
class AV_OP_Vehicle_EvalAllModelPaths(bpy.types.Operator):

    bl_idname = "av.vehicle_eval_all_model_paths"
    bl_label = "Evaluate all model paths"
    bl_description = "Click to evaluate all model paths."

    def execute(self, context):

        for objSel in bpy.data.objects:

            if objSel.type != "EMPTY":
                continue
            # endif

            sModelData = objSel.get("AnyVehicle")
            if sModelData is None:
                continue
            # endif

            sName = objSel.name
            dicModel = json.loads(sModelData)
            sModelType = dicModel.get("sType")
            if sModelType is None:
                self.report(
                    {"ERROR"},
                    "Object '{0}' has invalid vehicle animation data.".format(sName),
                )
                return {"FINISHED"}
            # endif

            anyblend.anim.util.RegisterAnimObject(
                sName, dicModel, animpath.CreateAnimHandler
            )
        # endfor

        return {"FINISHED"}

    # enddef


# endclass


###################################################################################
# Handler
@persistent
def AnyVehicle_UpdateRigs(_xScene):

    # Update vehicle rig data to new version
    for objX in bpy.data.objects:
        if objX.get("AnyBlend.Vehicle") is not None:
            objX["AnyVehicle"] = objX["AnyBlend.Vehicle"]
            del objX["AnyBlend.Vehicle"]

            dicData = json.loads(objX["AnyVehicle"])
            sType = dicData.get("sType")
            if sType == "vehicle.path.4w.singletrack.planar.v1":
                dicData[
                    "sType"
                ] = "/catharsys/blender/animate/vehicle/path/4w/singletrack/planar:1.0"

            elif sType == "vehicle.path.2w.singletrack.planar.v1":
                dicData[
                    "sType"
                ] = "/catharsys/blender/animate/vehicle/path/2w/singletrack/planar:1.0"

            # endif
            objX["AnyVehicle"] = json.dumps(dicData)
        # endif
    # endfor


# enddef


#######################################################################################
# Register
def register():
    # add handler if not in app.handlers
    if AnyVehicle_UpdateRigs not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(AnyVehicle_UpdateRigs)
    # endif

    bpy.utils.register_class(AV_OP_Vehicle_CreateModel_2w)
    bpy.utils.register_class(AV_OP_Vehicle_CreateModel_4w)
    bpy.utils.register_class(AV_OP_Vehicle_EvalModelPath)
    bpy.utils.register_class(AV_OP_Vehicle_EvalAllModelPaths)
    bpy.utils.register_class(AV_OP_Vehicle_RemoveModel)


# enddef


def unregister():

    # remove handler if not in app.handlers
    if AnyVehicle_UpdateRigs in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(AnyVehicle_UpdateRigs)
    # endif

    bpy.utils.unregister_class(AV_OP_Vehicle_CreateModel_2w)
    bpy.utils.unregister_class(AV_OP_Vehicle_CreateModel_4w)
    bpy.utils.unregister_class(AV_OP_Vehicle_EvalModelPath)
    bpy.utils.unregister_class(AV_OP_Vehicle_EvalAllModelPaths)
    bpy.utils.unregister_class(AV_OP_Vehicle_RemoveModel)


# enddef
