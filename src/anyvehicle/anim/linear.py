#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: /linear.py
# Created Date: Thursday, October 22nd 2020, 1:20:23 pm
# Author: Christian Perwass
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
import math


def AnimConstVelX(_sOrigName, _dicAnim):

    dVel_kmh = _dicAnim.get("dVel_kmh")

    def handler(xScene, xDepsGraph):
        objOrig = bpy.data.objects.get(_sOrigName)
        if objOrig is None:
            return
        # endif

        dTime_s = xScene.frame_current * xScene.render.fps_base / xScene.render.fps
        dDist_m = dTime_s * dVel_kmh / 3.6

        dWheelDia_m = objOrig.get("WheelDiameter_m")
        objWheelRot = next(
            (x for x in objOrig.children if x.name.startswith("Wheel.Rotate.All")), None
        )

        objOrig.delta_location.x = dDist_m

        if dWheelDia_m is not None and objWheelRot is not None:
            dWheelRot_rad = 2.0 * dDist_m / dWheelDia_m
            objWheelRot.delta_rotation_euler.y = dWheelRot_rad
        # endif

    # enddef

    return {"handler": handler}


# enddef
