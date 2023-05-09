#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \modules\anyblend\anim\vehicle\path.py
# Created Date: Wednesday, February 17th 2021, 7:45:26 am
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
import mathutils
import pyjson5 as json

from . import util
from .cls_planar_single_track_2w_model import CPlanarSingleTrack2wModel
from .cls_planar_single_track_4w_model import CPlanarSingleTrack4wModel

dicModels = {}


###############################################################################
def GetAnimModel(_sObj):

    global dicModels
    return dicModels.get(_sObj)


# enddef


###############################################################################
# if _dicAnim is None, the animation specifications are taken from the Blender
# object's custom property "AnyVehicle".
def CreateAnimHandler(_sObj, _dicAnim):

    global dicModels

    # get object
    objAnim = bpy.data.objects.get(_sObj)
    if objAnim is None:
        raise Exception("Object '{0}' not found for vehicle animation.".format(_sObj))
    # endif

    sObjAnim = objAnim.get("AnyVehicle")
    if sObjAnim is None and _dicAnim is None:
        raise Exception(
            "No vehicle animation specification available for object '{0}'.".format(
                _sObj
            )
        )
    # endif

    dicObjAnim = None
    if sObjAnim is not None:
        dicObjAnim = json.loads(sObjAnim)

        if _dicAnim is not None:
            dicObjAnim.update(_dicAnim)
        # endif
    else:
        dicObjAnim = _dicAnim
    # endif

    sType = dicObjAnim.get("sDTI", dicObjAnim.get("sType"))
    funcFactory = util.GetAnimHandlerFactory(
        sType, "/catharsys/blender/animate/vehicle/path/*:1.0"
    )
    if funcFactory is None:
        raise Exception("Vehicle animation type '{0}' not supported.".format(sType))
    # endif

    return funcFactory(objAnim, dicObjAnim)


# enddef


###############################################################################
def RemoveAnimHandler(_sObj):

    global dicModels

    if dicModels.get(_sObj) is not None:
        del dicModels[_sObj]
    # endif


# enddef


###############################################################################
def _GetObject(_sId, _dicAnim, bDoThrow=True):

    sObj = _dicAnim.get(_sId)
    if sObj is None:
        if bDoThrow:
            raise Exception(
                "Expected element '{0}' does not exist in animation specification.".format(
                    _sId
                )
            )
        else:
            return None
        # endif
    # endif

    objX = bpy.data.objects.get(sObj)
    if objX is None:
        if bDoThrow:
            raise Exception("Object '{0}' does not exist.".format(sObj))
        else:
            return None
        # endif
    # endif

    return objX


# enddef


###############################################################################
def _GetPar(_sId, _dicAnim, _sObj):
    xVal = _dicAnim.get(_sId)
    if xVal is None:
        raise Exception(
            "Animation parameter '{0}' missing for object '{1}'.".format(_sId, _sObj)
        )
    # endif
    return xVal


# endif


###############################################################################
def CreatePlanarSingleTrack2wHandler(_objAnim, _dicAnim):

    global dicModels

    sObj = _objAnim.name
    vZ = mathutils.Vector((0, 0, 1))

    xModel = CPlanarSingleTrack2wModel(
        FixedAxisOrigObj=_GetObject("sObjFAC", _dicAnim),
        FixedAxisRollObj=_GetObject("sObjFAR", _dicAnim),
        FixedAxisSpinObj=_GetObject("sObjFAS", _dicAnim),
        SteerAxisOrigObj=_GetObject("sObjSAC", _dicAnim),
        SteerAxisTiltObj=_GetObject("sObjSAT", _dicAnim),
        SteerAxisOrientObj=_GetObject("sObjSATO", _dicAnim),
        SteerAxisSpinObj=_GetObject("sObjSATS", _dicAnim),
        RotOrigObj=_GetObject("sObjRot", _dicAnim, bDoThrow=False),
        NurbsCurve=_GetObject("sObjNurbsPath", _dicAnim),
        VectorUp=vZ,
        Speed_kmh=_GetPar("fMeanSpeed", _dicAnim, sObj),
        WheelRadius=_GetPar("fWheelRadius", _dicAnim, sObj),
    )

    xModel.EvalTrack(Resolution=_GetPar("iResolution", _dicAnim, sObj))

    dicModels[sObj] = xModel

    return _CreateModelHandler(sObj)


# enddef


###############################################################################
def CreatePlanarSingleTrack4wHandler(_objAnim, _dicAnim):

    global dicModels

    sObj = _objAnim.name
    vZ = mathutils.Vector((0, 0, 1))

    xModel = CPlanarSingleTrack4wModel(
        FixedAxisOrigObj=_GetObject("sObjFAC", _dicAnim),
        FixedAxisLeftObj=_GetObject("sObjFAL", _dicAnim),
        FixedAxisRightObj=_GetObject("sObjFAR", _dicAnim),
        FixedAxisLeftSpinObj=_GetObject("sObjFALS", _dicAnim),
        FixedAxisRightSpinObj=_GetObject("sObjFARS", _dicAnim),
        SteerAxisOrigObj=_GetObject("sObjSAC", _dicAnim),
        SteerAxisLeftObj=_GetObject("sObjSAL", _dicAnim),
        SteerAxisRightObj=_GetObject("sObjSAR", _dicAnim),
        SteerAxisLeftSpinObj=_GetObject("sObjSALS", _dicAnim),
        SteerAxisRightSpinObj=_GetObject("sObjSARS", _dicAnim),
        RotOrigObj=_GetObject("sObjRot", _dicAnim, bDoThrow=False),
        NurbsCurve=_GetObject("sObjNurbsPath", _dicAnim),
        VectorUp=vZ,
        Speed_kmh=_GetPar("fMeanSpeed", _dicAnim, sObj),
        WheelRadius=_GetPar("fWheelRadius", _dicAnim, sObj),
    )

    xModel.EvalTrack(Resolution=_GetPar("iResolution", _dicAnim, sObj))

    dicModels[sObj] = xModel

    return _CreateModelHandler(sObj)


# enddef


###############################################################################
def _CreateModelHandler(_sId):

    ##############################################
    def handler(xScene, xDepsGraph):

        global dicModels
        xModel = dicModels.get(_sId)
        if xModel is None:
            raise Exception(
                "Vehicle animation model with '{0}' not available.".format(_sId)
            )
        # endif

        dFps = xScene.render.fps / xScene.render.fps_base
        dTime = xScene.frame_current / dFps
        xModel.SetObjectToTime(dTime)

    # enddef

    ##############################################
    def finalizer():

        global dicModels
        if dicModels.get(_sId):
            del dicModels[_sId]
        # endif

    # enddef

    return {"handler": handler, "finalizer": finalizer}


# endif
