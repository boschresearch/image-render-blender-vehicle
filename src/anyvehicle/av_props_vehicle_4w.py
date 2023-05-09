#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \modules\anyblend\av_props_vehicle.py
# Created Date: Tuesday, February 16th 2021, 10:33:16 am
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

###########################################################################
def LoadModelData(self, context):

    xAbProps = context.window_manager.AbVehicleProps4w
    if xAbProps.bLockLoad:
        return
    # endif

    xAbProps.bLockLoad = True
    xAbProps.bIsValid = False

    if xAbProps.objFAC is None:
        xAbProps.bLockLoad = False
        return
    # endif

    sData = xAbProps.objFAC.get("AnyVehicle")
    if sData is None:
        xAbProps.bLockLoad = False
        return
    # endif

    dicData = json.loads(sData)
    sType = dicData.get("sType")
    if (
        sType != "/catharsys/blender/animate/vehicle/path/4w/singletrack/planar:1.0"
        and sType != "vehicle.path.4w.singletrack.planar.v1"
        and sType != "vehicle.path.singletrack.planar.v1"
    ):
        xAbProps.bLockLoad = False
        return
    # endif

    bUpdateData = False

    # Convert old type id to new type id
    sModelType = dicData.get("sType")
    if (
        sModelType
        != "/catharsys/blender/animate/vehicle/path/4w/singletrack/planar:1.0"
    ):
        sModelType = "/catharsys/blender/animate/vehicle/path/4w/singletrack/planar:1.0"
        dicData["sType"] = sModelType
        bUpdateData = True
    # endif

    sObjFAC = dicData.get("sObjFAC")
    if sObjFAC != xAbProps.objFAC.name:
        dicData["sObjFAC"] = xAbProps.objFAC.name
        bUpdateData = True
    # endif

    xAbProps.bLockSave = True

    lProps = [
        ("objFAL", "sObjFAL"),
        ("objFAR", "sObjFAR"),
        ("objFALS", "sObjFALS"),
        ("objFARS", "sObjFARS"),
        ("objSAL", "sObjSAL"),
        ("objSAR", "sObjSAR"),
        ("objSAC", "sObjSAC"),
        ("objSALS", "sObjSALS"),
        ("objSARS", "sObjSARS"),
        ("objRot", "sObjRot"),
        ("objNurbsPath", "sObjNurbsPath"),
    ]

    for tProp in lProps:
        sName = dicData.get(tProp[1], "")
        objX = bpy.context.scene.objects.get(sName)
        if objX is None and sName != "" and sName is not None:
            dicData[tProp[1]] = ""
            bUpdateData = True
        # endif
        setattr(xAbProps, tProp[0], objX)
    # endfor

    lChildren = [
        ("objFAL", "sObjFAL"),
        ("objFAR", "sObjFAR"),
        ("objSAL", "sObjSAL"),
        ("objSAR", "sObjSAR"),
        ("objSAC", "sObjSAC"),
    ]

    for tChild in lChildren:
        objX = getattr(xAbProps, tChild[0])
        if objX is not None and objX.parent != xAbProps.objFAC:
            setattr(xAbProps, tChild[0], None)
            dicData[tChild[1]] = ""
            bUpdateData = True
        # endif
    # endfor

    if xAbProps.objFAL is None or (
        xAbProps.objFALS is not None and xAbProps.objFALS.parent != xAbProps.objFAL
    ):
        xAbProps.objFALS = None
        dicData["sObjFALS"] = ""
        bUpdateData = True
    # endif

    if xAbProps.objFAR is None or (
        xAbProps.objFARS is not None and xAbProps.objFARS.parent != xAbProps.objFAR
    ):
        xAbProps.objFARS = None
        dicData["sObjFARS"] = ""
        bUpdateData = True
    # endif

    if xAbProps.objSAL is None or (
        xAbProps.objSALS is not None and xAbProps.objSALS.parent != xAbProps.objSAL
    ):
        xAbProps.objSALS = None
        dicData["sObjSALS"] = ""
        bUpdateData = True
    # endif

    if xAbProps.objSAR is None or (
        xAbProps.objSARS is not None and xAbProps.objSARS.parent != xAbProps.objSAR
    ):
        xAbProps.objSARS = None
        dicData["sObjSARS"] = ""
        bUpdateData = True
    # endif

    # if a previously selected object does not exist anymore,
    # update the stored dictionary.
    if bUpdateData:
        xAbProps.objFAC["AnyVehicle"] = json.dumps(dicData)
    # endif

    xAbProps.sType = dicData.get(
        "sType", "/catharsys/blender/animate/vehicle/path/4w/singletrack/planar:1.0"
    )
    xAbProps.iResolution = dicData.get("iResolution", 10)
    xAbProps.fWheelRadius = dicData.get("fWheelRadius", 1.0)
    xAbProps.fTimeOffset = dicData.get("fTimeOffset", 0.0)
    xAbProps.fMeanSpeed = dicData.get("fMeanSpeed", 1.0)

    xAbProps.bLockSave = False
    xAbProps.bIsValid = True

    xAbProps.bLockLoad = False


# enddef

###########################################################################
def SaveModelData(self, context):
    xAbProps = context.window_manager.AbVehicleProps4w
    if xAbProps.bIsValid is False:
        return
    # endif

    if xAbProps.bLockSave:
        return
    # endif
    xAbProps.bLockSave = True

    if xAbProps.objFAC is None:
        xAbProps.bLockSave = False
        return
    # endif

    sData = xAbProps.objFAC.get("AnyVehicle")
    if sData is None:
        xAbProps.bLockSave = False
        return
    # endif

    dicData = json.loads(sData)

    lProps = [
        ("objFAC", "sObjFAC"),
        ("objFAL", "sObjFAL"),
        ("objFAR", "sObjFAR"),
        ("objFALS", "sObjFALS"),
        ("objFARS", "sObjFARS"),
        ("objSAL", "sObjSAL"),
        ("objSAR", "sObjSAR"),
        ("objSALS", "sObjSALS"),
        ("objSARS", "sObjSARS"),
        ("objSAC", "sObjSAC"),
        ("objRot", "sObjRot"),
        ("objNurbsPath", "sObjNurbsPath"),
    ]

    for tProp in lProps:
        objX = getattr(xAbProps, tProp[0])
        if objX is not None:
            sName = objX.name
        else:
            sName = ""
        # endif
        dicData[tProp[1]] = sName
    # endfor

    dicData["sType"] = xAbProps.sType
    dicData["iResolution"] = xAbProps.iResolution
    dicData["fWheelRadius"] = xAbProps.fWheelRadius
    dicData["fMeanSpeed"] = xAbProps.fMeanSpeed
    dicData["fTimeOffset"] = xAbProps.fTimeOffset

    xAbProps.objFAC["AnyVehicle"] = json.dumps(dicData)
    xAbProps.bLockSave = False


# enddef

###########################################################################

###########################################################################
def PollObjectTypeCurve(self, object):
    return object.type == "CURVE" and object.data.splines[0].type == "NURBS"


# enddef

###########################################################################
def PollObjectChildOfFAC(self, object):
    xAbProps = bpy.context.window_manager.AbVehicleProps4w

    return (
        xAbProps.objFAC is not None
        and object.parent == xAbProps.objFAC
        and object.type == "EMPTY"
    )


# enddef

###########################################################################
def PollObjectChildOfSAL(self, object):
    xAbProps = bpy.context.window_manager.AbVehicleProps4w

    return (
        xAbProps.objSAL is not None
        and object.parent == xAbProps.objSAL
        and object.type == "EMPTY"
    )


# enddef

###########################################################################
def PollObjectChildOfSAR(self, object):
    xAbProps = bpy.context.window_manager.AbVehicleProps4w

    return (
        xAbProps.objSAR is not None
        and object.parent == xAbProps.objSAR
        and object.type == "EMPTY"
    )


# enddef

###########################################################################
def PollObjectChildOfFAL(self, object):
    xAbProps = bpy.context.window_manager.AbVehicleProps4w

    return (
        xAbProps.objFAL is not None
        and object.parent == xAbProps.objFAL
        and object.type == "EMPTY"
    )


# enddef

###########################################################################
def PollObjectChildOfFAR(self, object):
    xAbProps = bpy.context.window_manager.AbVehicleProps4w

    return (
        xAbProps.objFAR is not None
        and object.parent == xAbProps.objFAR
        and object.type == "EMPTY"
    )


# enddef

###########################################################################
class AV_PG_Vehicle_4w(bpy.types.PropertyGroup):
    """Class to register properties to window, not saved with settings or file"""

    bIsValid: bpy.props.BoolProperty(default=False)
    bLockLoad: bpy.props.BoolProperty(default=False)
    bLockSave: bpy.props.BoolProperty(default=False)

    sType: bpy.props.StringProperty(default="vehicle.path.4w.singletrack.planar.v1")

    objFAC: bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="Fixed-axis ground center",
        description="The fixed axis' center projected on the ground plane.",
        update=LoadModelData,
    )

    objFAL: bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="Fixed-axis left",
        description="Origin of wheel attached to the left end of the fixed axis.",
        poll=PollObjectChildOfFAC,
        update=SaveModelData,
    )

    objFAR: bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="Fixed-axis right",
        description="Origin of wheel attached to the right end of the fixed axis.",
        poll=PollObjectChildOfFAC,
        update=SaveModelData,
    )

    objFALS: bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="Fixed-axis left spin",
        description="Origin of spinning wheel part attached to the left end of the fixed axis. Must be a child of fixed-axis left.",
        poll=PollObjectChildOfFAL,
        update=SaveModelData,
    )

    objFARS: bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="Fixed-axis right spin",
        description="Origin of spinning wheel part attached to the right end of the fixed axis. Must be a child of fixed-axis right.",
        poll=PollObjectChildOfFAR,
        update=SaveModelData,
    )

    objSAC: bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="Steering-axis ground center",
        description="The steering axis' center projected on the ground plane.",
        poll=PollObjectChildOfFAC,
        update=SaveModelData,
    )

    objSAL: bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="Steering-axis left",
        description="Origin of not spinning wheel part attached to the left end of the steering axis.",
        poll=PollObjectChildOfFAC,
        update=SaveModelData,
    )

    objSAR: bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="Steering-axis right",
        description="Origin of wheel attached to the right end of the steering axis.",
        poll=PollObjectChildOfFAC,
        update=SaveModelData,
    )

    objSALS: bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="Steering-axis left spin",
        description="Origin of spinning wheel part attached to the left end of the steering axis. Must be a child of steering-axis left.",
        poll=PollObjectChildOfSAL,
        update=SaveModelData,
    )

    objSARS: bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="Steering-axis right spin",
        description="Origin of spinning wheel part attached to the right end of the steering axis. Must be a child of steering-axis right.",
        poll=PollObjectChildOfSAR,
        update=SaveModelData,
    )

    objRot: bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="Rotation center origin",
        description="If defined, this object will be placed at the rotation center of the single track model.",
        update=SaveModelData,
    )

    objNurbsPath: bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="Planar NURBS path",
        description="The path along which the vehicle is moved. Must be a planar NURBS path.",
        poll=PollObjectTypeCurve,
        update=SaveModelData,
    )

    iResolution: bpy.props.IntProperty(
        default=10,
        update=SaveModelData,
        min=2,
        max=110,
        soft_min=5,
        soft_max=100,
        description="The resolution the nurbs path is sampled with",
    )

    fWheelRadius: bpy.props.FloatProperty(
        default=1.0,
        update=SaveModelData,
        min=0.01,
        max=1000,
        soft_min=0.05,
        soft_max=900,
        description="Wheel radius",
    )

    fMeanSpeed: bpy.props.FloatProperty(
        default=1.0,
        update=SaveModelData,
        min=0.01,
        max=1000,
        soft_min=0.05,
        soft_max=900,
        description="Mean speed (km/h)",
    )

    fTimeOffset: bpy.props.FloatProperty(
        default=0.0,
        update=SaveModelData,
        description="Time offset in seconds for start of path",
    )

    ##########################################################################
    def clear(self):
        self.bIsValid = False
        self.bLockLoad = True
        self.bLockSave = True

        self.sType = ""

        self.objFAC = None
        self.objFAL = None
        self.objFAR = None
        self.objFALS = None
        self.objFARS = None

        self.objSAC = None
        self.objSAL = None
        self.objSAR = None
        self.objSALS = None
        self.objSARS = None

        self.objRot = None
        self.objNurbsPath = None

        self.iResolution = 10
        self.fWheelRadius = 1.0
        self.fMeanSpeed = 1.0
        self.fTimeOffset = 0.0

        self.bLockLoad = False
        self.bLockSave = False

    # enddef

    ##########################################################################
    def IsComplete(self):
        return (
            self.objFAC is not None
            and self.objFAL is not None
            and self.objFAR is not None
            and self.objFALS is not None
            and self.objFARS is not None
            and self.objSAC is not None
            and self.objSAL is not None
            and self.objSAR is not None
            and self.objSALS is not None
            and self.objSARS is not None
            and self.objNurbsPath is not None
            and self.bIsValid
        )

    # enddef


# endclass

#######################################################################################
# Register


def register():
    bpy.utils.register_class(AV_PG_Vehicle_4w)

    bpy.types.WindowManager.AbVehicleProps4w = bpy.props.PointerProperty(
        type=AV_PG_Vehicle_4w
    )


# enddef


def unregister():
    # Clear all window properties, to start fresh, when registering again.
    bpy.context.window_manager.AbVehicleProps4w.clear()

    del bpy.types.WindowManager.AbVehicleProps4w

    bpy.utils.unregister_class(AV_PG_Vehicle_4w)


# enddef
