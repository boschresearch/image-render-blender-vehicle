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

    xAbProps = context.window_manager.AbVehicleProps2w
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
    if (
        dicData.get("sType")
        != "/catharsys/blender/animate/vehicle/path/2w/singletrack/planar:1.0"
    ):
        xAbProps.bLockLoad = False
        return
    # endif

    bUpdateData = False

    sObjFAC = dicData.get("sObjFAC")
    print("--")
    print(sObjFAC)
    print(xAbProps.objFAC.name)

    if sObjFAC != xAbProps.objFAC.name:
        dicData["sObjFAC"] = xAbProps.objFAC.name
        bUpdateData = True
    # endif

    xAbProps.bLockSave = True

    lProps = [
        ("objFAS", "sObjFAS"),
        ("objFAR", "sObjFAR"),
        ("objSAC", "sObjSAC"),
        ("objSAT", "sObjSAT"),
        ("objSATO", "sObjSATO"),
        ("objSATS", "sObjSATS"),
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
        ("objFAR", "sObjFAR"),
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

    lChildren = [
        ("objFAS", "sObjFAS"),
        ("objSAT", "sObjSAT"),
    ]

    for tChild in lChildren:
        objX = getattr(xAbProps, tChild[0])
        if objX is not None and objX.parent != xAbProps.objFAR:
            setattr(xAbProps, tChild[0], None)
            dicData[tChild[1]] = ""
            bUpdateData = True
        # endif
    # endfor

    if xAbProps.objSATO is None or (
        xAbProps.objSATO is not None and xAbProps.objSATO.parent != xAbProps.objSAT
    ):
        xAbProps.objSATO = None
        dicData["sObjSATO"] = ""
        bUpdateData = True
    # endif

    if xAbProps.objSATS is None or (
        xAbProps.objSATS is not None and xAbProps.objSATS.parent != xAbProps.objSATO
    ):
        xAbProps.objSATS = None
        dicData["sObjSATS"] = ""
        bUpdateData = True
    # endif

    # if a previously selected object does not exist anymore,
    # update the stored dictionary.
    if bUpdateData:
        xAbProps.objFAC["AnyVehicle"] = json.dumps(dicData)
    # endif

    xAbProps.sType = dicData.get("sType", "vehicle.path.2w.singletrack.planar.v1")
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
    xAbProps = context.window_manager.AbVehicleProps2w
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
        ("objFAS", "sObjFAS"),
        ("objFAR", "sObjFAR"),
        ("objSAC", "sObjSAC"),
        ("objSAT", "sObjSAT"),
        ("objSATO", "sObjSATO"),
        ("objSATS", "sObjSATS"),
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
    xAbProps = bpy.context.window_manager.AbVehicleProps2w

    return (
        xAbProps.objFAC is not None
        and object.parent == xAbProps.objFAC
        and object.type == "EMPTY"
    )


# enddef

###########################################################################
def PollObjectChildOfFAR(self, object):
    xAbProps = bpy.context.window_manager.AbVehicleProps2w

    return (
        xAbProps.objFAR is not None
        and object.parent == xAbProps.objFAR
        and object.type == "EMPTY"
    )


# enddef

###########################################################################
def PollObjectChildOfSAT(self, object):
    xAbProps = bpy.context.window_manager.AbVehicleProps2w

    return (
        xAbProps.objSAT is not None
        and object.parent == xAbProps.objSAT
        and object.type == "EMPTY"
    )


# enddef

###########################################################################
def PollObjectChildOfSATO(self, object):
    xAbProps = bpy.context.window_manager.AbVehicleProps2w

    return (
        xAbProps.objSATO is not None
        and object.parent == xAbProps.objSATO
        and object.type == "EMPTY"
    )


# enddef

###########################################################################
class AV_PG_Vehicle_2w(bpy.types.PropertyGroup):
    """Class to register properties to window, not saved with settings or file"""

    bIsValid: bpy.props.BoolProperty(default=False)
    bLockLoad: bpy.props.BoolProperty(default=False)
    bLockSave: bpy.props.BoolProperty(default=False)

    sType: bpy.props.StringProperty(
        default="/catharsys/blender/animate/vehicle/path/2w/singletrack/planar:1.0"
    )

    objFAC: bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="Fixed-axis ground center",
        description="The fixed axis' center projected on the ground plane.",
        update=LoadModelData,
    )

    objFAR: bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="Fixed-axis roll",
        description="Origin on about which the vehicle rolls in curves.",
        poll=PollObjectChildOfFAC,
        update=SaveModelData,
    )

    objFAS: bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="Fixed-axis spin",
        description="Origin of wheel attached to the fixed axis.",
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

    objSAT: bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="Steering-axis tilt",
        description="Origin of tilted steering axis",
        poll=PollObjectChildOfFAR,
        update=SaveModelData,
    )

    objSATO: bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="Steering-axis tilt orientation",
        description="Origin orientation axis. The steering is applied to this axis. It must be a child of steering tilt axis",
        poll=PollObjectChildOfSAT,
        update=SaveModelData,
    )

    objSATS: bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="Steering-axis tilt orientation spin",
        description="Origin of spinning wheel part of steering axis. Must be a child of the steering orientation axis.",
        poll=PollObjectChildOfSATO,
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
        self.objFAR = None
        self.objFAS = None

        self.objSAC = None
        self.objSAT = None
        self.objSATO = None
        self.objSATS = None

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
            and self.objFAR is not None
            and self.objFAS is not None
            and self.objSAC is not None
            and self.objSAT is not None
            and self.objSATO is not None
            and self.objSATS is not None
            and self.objNurbsPath is not None
            and self.bIsValid
        )

    # enddef


# endclass

#######################################################################################
# Register


def register():
    bpy.utils.register_class(AV_PG_Vehicle_2w)

    bpy.types.WindowManager.AbVehicleProps2w = bpy.props.PointerProperty(
        type=AV_PG_Vehicle_2w
    )


# enddef


def unregister():
    # Clear all window properties, to start fresh, when registering again.
    bpy.context.window_manager.AbVehicleProps2w.clear()

    del bpy.types.WindowManager.AbVehicleProps2w

    bpy.utils.unregister_class(AV_PG_Vehicle_2w)


# enddef
