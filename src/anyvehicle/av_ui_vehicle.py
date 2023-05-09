#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \modules\anyblend\av_ui_vehicle.py
# Created Date: Tuesday, February 16th 2021, 10:04:27 am
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
import pyjson5 as json

import anyblend

# from . import av_global


##############################################################################
# The create camera panel, where cameras can be added to the scene


class AV_PT_CreateVehicleModel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""

    bl_label = "Single Track Vehicle Model"
    bl_idname = "AV_PT_CreateVehicleModel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "AnyVehicle"

    bLockDraw = False

    ##########################################################################
    def InvalidateProps(self, context):
        xAbProps2w = context.window_manager.AbVehicleProps2w
        xAbProps4w = context.window_manager.AbVehicleProps4w

        xAbProps2w.bIsValid = False
        xAbProps4w.bIsValid = False

    # enddef

    ##########################################################################
    def draw(self, context):
        if self.bLockDraw:
            return
        # endif
        self.bLockDraw = True

        layout = self.layout
        objSel = bpy.context.active_object

        # layout.row().box().label(text="Hello World")
        yRow = layout.row()
        yRow.operator("av.vehicle_eval_all_model_paths", icon="FILE_REFRESH")

        yRow = layout.row()
        yRow.label(text="Fixed-Axis Center")

        yRow = layout.row()
        yBox = yRow.box()
        if objSel is None or objSel.type != "EMPTY":
            self.InvalidateProps(context)
            yBox.label(text="[No Empty selected]")
            self.bLockDraw = False
            return
        # endif

        sObjFAC = objSel.name
        yBox.label(text="{0}".format(sObjFAC))
        sModelData = objSel.get("AnyVehicle")
        if sModelData is None:
            yRow = layout.row()
            yRow.operator("av.vehicle_create_model_4w", icon="PLUS")
            yRow = layout.row()
            yRow.operator("av.vehicle_create_model_2w", icon="PLUS")
            self.InvalidateProps(context)
            self.bLockDraw = False
            return
        # endif

        # Convert model data string to dictionary
        dicModel = json.loads(sModelData)
        sModelType = dicModel.get("sType")
        if (
            sModelType
            == "/catharsys/blender/animate/vehicle/path/2w/singletrack/planar:1.0"
            or sModelType == "vehicle.path.2w.singletrack.planar.v1"
        ):
            self.draw_2w(context, objSel)

        elif (
            sModelType
            == "/catharsys/blender/animate/vehicle/path/4w/singletrack/planar:1.0"
            or sModelType == "vehicle.path.4w.singletrack.planar.v1"
            or sModelType == "vehicle.path.singletrack.planar.v1"
        ):
            self.draw_4w(context, objSel)

        else:
            yRow = layout.row()
            yRow.alert = True
            yRow.label(text="Unknown vehicle model type")
            yRow = layout.row()
            yRow.label(text="['{0}']".format(sModelType))
            yRow = layout.row()
            yRow.operator("av.vehicle_remove_model", icon="CANCEL")
        # endif

        self.bLockDraw = False

    # enddef

    ##########################################################################
    def draw_2w(self, context, objSel):
        layout = self.layout

        xAbProps = context.window_manager.AbVehicleProps2w
        sObjFAC = objSel.name

        # xAbProps.objFAC = objSel
        if xAbProps.objFAC is None:
            xAbProps.objFAC = objSel
        elif xAbProps.objFAC.name != sObjFAC or xAbProps.bIsValid == False:
            xAbProps.objFAC = objSel
        # endif

        yRow = layout.row()
        yRow.prop(xAbProps, "objFAR", text="FAR", icon="OUTLINER_DATA_EMPTY")
        yRow = layout.row()
        yRow.prop(xAbProps, "objFAS", text="FAS", icon="OUTLINER_DATA_EMPTY")

        yRow = layout.row()
        yRow.prop(xAbProps, "objSAC", text="SAC", icon="OUTLINER_DATA_EMPTY")
        yRow = layout.row()
        yRow.prop(xAbProps, "objSAT", text="SAT", icon="OUTLINER_DATA_EMPTY")
        yRow = layout.row()
        yRow.prop(xAbProps, "objSATO", text="SATO", icon="OUTLINER_DATA_EMPTY")
        yRow = layout.row()
        yRow.prop(xAbProps, "objSATS", text="SATS", icon="OUTLINER_DATA_EMPTY")

        yRow = layout.row()
        yRow.prop(xAbProps, "objRot", text="Rot")
        yRow = layout.row()
        yRow.prop(xAbProps, "objNurbsPath", text="Path", icon="MOD_CURVE")

        yRow = layout.row()
        yRow.prop(xAbProps, "iResolution", text="Resolution")
        yRow = layout.row()
        yRow.prop(xAbProps, "fWheelRadius", text="Wheel Radius")
        yRow = layout.row()
        yRow.prop(xAbProps, "fMeanSpeed", text="Mean Speed")
        yRow = layout.row()
        yRow.prop(xAbProps, "fTimeOffset", text="Time Offset")

        xAbProps.bIsValid = True

        if not xAbProps.IsComplete():
            return
        # endif

        yRow = layout.row()
        yRow.operator("av.vehicle_eval_model_path")

    # enddef

    ##########################################################################
    def draw_4w(self, context, objSel):
        layout = self.layout

        xAbProps = context.window_manager.AbVehicleProps4w
        sObjFAC = objSel.name

        if xAbProps.objFAC is None:
            xAbProps.objFAC = objSel
        elif xAbProps.objFAC.name != sObjFAC or xAbProps.bIsValid == False:
            xAbProps.objFAC = objSel
        # endif

        yRow = layout.row()
        yRow.prop(xAbProps, "objFAL", text="FAL", icon="OUTLINER_DATA_EMPTY")
        yRow = layout.row()
        yRow.prop(xAbProps, "objFALS", text="FALS", icon="OUTLINER_DATA_EMPTY")
        yRow = layout.row()
        yRow.prop(xAbProps, "objFAR", text="FAR", icon="OUTLINER_DATA_EMPTY")
        yRow = layout.row()
        yRow.prop(xAbProps, "objFARS", text="FARS", icon="OUTLINER_DATA_EMPTY")

        yRow = layout.row()
        yRow.prop(xAbProps, "objSAC", text="SAC", icon="OUTLINER_DATA_EMPTY")
        yRow = layout.row()
        yRow.prop(xAbProps, "objSAL", text="SAL", icon="OUTLINER_DATA_EMPTY")
        yRow = layout.row()
        yRow.prop(xAbProps, "objSALS", text="SALS", icon="OUTLINER_DATA_EMPTY")
        yRow = layout.row()
        yRow.prop(xAbProps, "objSAR", text="SAR", icon="OUTLINER_DATA_EMPTY")
        yRow = layout.row()
        yRow.prop(xAbProps, "objSARS", text="SARS", icon="OUTLINER_DATA_EMPTY")

        yRow = layout.row()
        yRow.prop(xAbProps, "objRot", text="Rot")
        yRow = layout.row()
        yRow.prop(xAbProps, "objNurbsPath", text="Path", icon="MOD_CURVE")

        yRow = layout.row()
        yRow.prop(xAbProps, "iResolution", text="Resolution")
        yRow = layout.row()
        yRow.prop(xAbProps, "fWheelRadius", text="Wheel Radius")
        yRow = layout.row()
        yRow.prop(xAbProps, "fMeanSpeed", text="Mean Speed")
        yRow = layout.row()
        yRow.prop(xAbProps, "fTimeOffset", text="Time Offset")

        xAbProps.bIsValid = True

        if not xAbProps.IsComplete():
            return
        # endif

        yRow = layout.row()
        yRow.operator("av.vehicle_eval_model_path")

    # enddef


# endclass

##############################################################################
# Register


def register():
    anyblend.anim.util.ClearAnim()
    bpy.utils.register_class(AV_PT_CreateVehicleModel)


# enddef

##############################################################################
# Unregister


def unregister():
    anyblend.anim.util.ClearAnim()
    bpy.utils.unregister_class(AV_PT_CreateVehicleModel)


# enddef
