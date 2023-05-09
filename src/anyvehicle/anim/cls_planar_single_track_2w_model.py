#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \modules\anyblend\anim\vehicle\planar_single_track.py
# Created Date: Tuesday, February 16th 2021, 4:35:28 pm
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

import copy
import bpy
import math
import mathutils
import anyblend

####################################################################
class CPlanarSingleTrack2wModel:

    #############################################################
    def __init__(
        self,
        *,
        NurbsCurve,
        VectorUp,
        Speed_kmh,
        WheelRadius,
        FixedAxisOrigObj,
        FixedAxisRollObj,
        FixedAxisSpinObj,
        SteerAxisOrigObj,
        SteerAxisTiltObj,
        SteerAxisOrientObj,
        SteerAxisSpinObj,
        RotOrigObj=None
    ):

        self.xCurve = NurbsCurve
        self.vZ = VectorUp
        self.dWheelRadius = WheelRadius
        self.dSpeed_ms = 0.0
        self.SetSpeed_kmh(Speed_kmh)

        self.objFAC = FixedAxisOrigObj
        self.objFAR = FixedAxisRollObj
        self.objFAS = FixedAxisSpinObj

        self.objSAC = SteerAxisOrigObj
        self.objSAT = SteerAxisTiltObj
        self.objSATO = SteerAxisOrientObj
        self.objSATS = SteerAxisSpinObj

        self.objRot = RotOrigObj

        self.bTrackDataAvailable = False

        self.dAxisSep = None
        self.dCurveTimeStep = None
        self.dCurveTimeTotal = None

        self.lFAC_Pos = None
        self.dFAC_LenTotal = None
        self.lFAC_Len = None
        self.lFAC_Deriv2 = None
        self.lFAC_Curv = None
        self.lFAC_CurvN = None

        self.lSAC_Pos = None

        self.lRC_Pos = None

    # enddef

    #############################################################
    def IsTrackAvailable(self):
        return self.bTrackDataAvailable

    # enddef

    #############################################################
    def SetSpeed_mps(self, dSpeed_ms):
        self.dSpeed_ms = dSpeed_ms

    # enddef

    #############################################################
    def SetSpeed_kmh(self, dSpeed_kmh):
        self.dSpeed_ms = dSpeed_kmh / 3.6

    # enddef

    #############################################################
    def EvalTrack(self, *, Resolution):

        vFAC = self.objFAC.matrix_world.translation

        self.dAxisSep = (self.objSAC.matrix_world.translation - vFAC).length

        if self.xCurve.data.splines[0].type != "NURBS":
            raise Exception(
                "Expect a 'NURBS' type curve for the vehicle planar single track model."
            )
        # endif

        self.xCurve.data.resolution_u = Resolution
        self.xCurve.data.render_resolution_u = 0

        # we need to transform the curve to a mesh with all modifiers applied
        xDepsGraph = bpy.context.evaluated_depsgraph_get()
        xCurveEval = self.xCurve.evaluated_get(xDepsGraph)
        meshCurve = xCurveEval.to_mesh()

        # IMPORTANT: the "x.co" elements are stored in a list by reference,
        # and thus become invalid after the call "to_mesh_clear()".
        # Do not apply world matrix of curve at this point, because
        # the following calculations assume that the curve is in XY-plane,
        # with Z-axis pointing up.
        self.lFAC_Pos = [x.co.copy() for x in meshCurve.vertices]
        xCurveEval.to_mesh_clear()

        # print(len(lPnts))
        # print(lPnts[0])

        # Evaluate length of curve traced by fixed axis origin
        # and calculate the derivative of the curve
        iPntCnt = len(self.lFAC_Pos)

        self.dCurveTimeStep = 1
        self.dCurveTimeTotal = (iPntCnt - 1) * self.dCurveTimeStep
        self.dFAC_LenTotal = 0.0

        self.lFAC_Deriv = []
        self.lFAC_Len = [0.0]
        for iPntIdx in range(iPntCnt - 1):
            vD = self.lFAC_Pos[iPntIdx + 1] - self.lFAC_Pos[iPntIdx]
            self.dFAC_LenTotal += vD.length
            self.lFAC_Len.append(self.dFAC_LenTotal)
            self.lFAC_Deriv.append(vD / self.dCurveTimeStep)
        # endfor

        # Calculate the curve's second derivative and curvature
        self.lFAC_Deriv2 = []
        self.lFAC_Curv = []
        self.lFAC_CurvN = []

        for iPntIdx in range(iPntCnt - 2):
            vD = self.lFAC_Deriv[iPntIdx]
            vD2 = (self.lFAC_Deriv[iPntIdx + 1] - vD) / self.dCurveTimeStep
            self.lFAC_Deriv2.append(vD2)

            # Curvature
            vA = vD.cross(vD2)
            dDl = vD.length
            dC = vA.length / (dDl * dDl * dDl)
            self.lFAC_Curv.append(dC)

            if dC < 1e-8:
                vN = None
            else:
                vN = vA.normalized()
            # endif
            self.lFAC_CurvN.append(vN)
        # endfor

        # Create world matrices for front and back
        self.lSAC_Pos = []
        self.dSAC_LenTotal = 0.0
        self.lSAC_Len = [0.0]

        self.lRC_Pos = []

        for iPntIdx in range(iPntCnt - 2):
            vD = self.lFAC_Deriv[iPntIdx]
            # print("vD: {0}".format(vD))

            vFAC_Pos = self.lFAC_Pos[iPntIdx]
            # print("vPnt: {0}".format(vPnt))

            vX = vD.normalized()
            vY = self.vZ.cross(vX)
            mWorld = mathutils.Matrix([vX, vY, self.vZ, vFAC_Pos])
            mWorld = mWorld.to_4x4()
            mWorld.transpose()

            vSAC_Pos = vFAC_Pos + self.dAxisSep * vX
            self.lSAC_Pos.append(vSAC_Pos)

            if iPntIdx > 0:
                self.dSAC_LenTotal += (vSAC_Pos - self.lSAC_Pos[iPntIdx - 1]).length
                self.lSAC_Len.append(self.dSAC_LenTotal)
            # endif

            # Eval rotation center
            dC = self.lFAC_Curv[iPntIdx]
            if dC > 1e-8:
                vN = self.lFAC_CurvN[iPntIdx]
                vR = vN.cross(vX)
                dR = 1.0 / dC
                vRot = dR * vR + vFAC_Pos
                self.lRC_Pos.append(vRot)
            else:
                self.lRC_Pos.append(None)
            # endif
        # endfor

    # enddef

    #############################################################
    def _GetSteerDir(self, _iIdx, _vY, _vSAC_Pos):

        vSteer = _vY
        vRC_Pos = self.lRC_Pos[_iIdx]

        if vRC_Pos is not None:
            vN = self.lFAC_CurvN[_iIdx]
            vSteer = (vRC_Pos - _vSAC_Pos).normalized()
            if vN.dot(self.vZ) < 0.0:
                vSteer = -vSteer
            # endif
        # endif

        return vSteer

    # enddef

    #############################################################
    def _SetMatrixLocal(self, _objX, _vX, _vY, _vZ, _mWorldInv, _dSpinAngle_rad):

        dC = math.cos(_dSpinAngle_rad)
        dS = math.sin(_dSpinAngle_rad)

        mB = mathutils.Matrix([dC * _vX - dS * _vZ, _vY, dC * _vZ + dS * _vX])
        mB.transpose()
        mC = _mWorldInv @ mB
        mD = mC.to_4x4()
        mD[0][3] = _objX.location[0]
        mD[1][3] = _objX.location[1]
        mD[2][3] = _objX.location[2]
        _objX.matrix_local = mD

    # enddef

    #############################################################
    def SetObjectToTime(self, dT):

        dTimeForCurve = self.dFAC_LenTotal / self.dSpeed_ms
        dTimeRatio = self.dCurveTimeTotal / dTimeForCurve
        dCurveIdx = (dTimeRatio * dT) / self.dCurveTimeStep

        dTimeDelta = self.dCurveTimeStep / dTimeRatio

        iPntIdx1 = int(math.floor(dCurveIdx))
        iPntIdx2 = iPntIdx1 + 1

        # print("")
        # print("iIdx1: {0}, iIdx2: {1}, len(pos): {2}, len(deriv): {3}".format(
        #           iPntIdx1, iPntIdx2, len(self.lFAC_Pos), len(self.lFAC_Deriv)))

        if iPntIdx1 < 0:
            iPntIdx1 = 0
            iPntIdx2 = 0
            dFac2 = 0.0
        elif iPntIdx1 >= len(self.lFAC_Pos) - 3:
            iPntIdx1 = len(self.lFAC_Pos) - 3
            iPntIdx2 = len(self.lFAC_Pos) - 3
            dFac2 = 0.0
        else:
            dFac2 = dCurveIdx - iPntIdx1
        # endif

        # print("iIdx1: {0}, iIdx2: {1}, len(pos): {2}, len(deriv): {3}".format(
        #        iPntIdx1, iPntIdx2, len(self.lFAC_Pos), len(self.lFAC_Deriv)))
        # vFAC_Pos_Orig = self.lFAC_Pos[0]

        vFAC_Pos = (
            self.lFAC_Pos[iPntIdx1] * (1.0 - dFac2) + self.lFAC_Pos[iPntIdx2] * dFac2
        )
        vFAC_Deriv = (
            self.lFAC_Deriv[iPntIdx1] * (1.0 - dFac2)
            + self.lFAC_Deriv[iPntIdx2] * dFac2
        )

        dFAC_Len = (
            self.lFAC_Len[iPntIdx1] * (1.0 - dFac2) + self.lFAC_Len[iPntIdx2] * dFac2
        )
        dFAC_SpinAngle_rad = dFAC_Len / self.dWheelRadius

        dSAC_Len = (
            self.lSAC_Len[iPntIdx1] * (1.0 - dFac2) + self.lSAC_Len[iPntIdx2] * dFac2
        )
        dSAC_SpinAngle_rad = dSAC_Len / self.dWheelRadius

        dC1 = self.lFAC_Curv[iPntIdx1]
        if dC1 > 1e-8:
            vN = self.lFAC_CurvN[iPntIdx1]
            dC1 *= 1.0 if vN.dot(self.vZ) >= 0 else -1.0
        # endif

        dC2 = self.lFAC_Curv[iPntIdx2]
        if dC2 > 1e-8:
            vN = self.lFAC_CurvN[iPntIdx2]
            dC2 *= 1.0 if vN.dot(self.vZ) >= 0 else -1.0
        # endif

        dFAC_Curv = dC1 * (1.0 - dFac2) + dC2 * dFac2
        dFAC_Vel = vFAC_Deriv.length / dTimeDelta
        dFAC_Roll_rad = -math.atan(dFAC_Vel * dFAC_Vel * dFAC_Curv / 9.81)
        # mRoll = mathutils.Matrix.Rotation(dFAC_Roll_rad, 4, 'X')

        vX = vFAC_Deriv.normalized()
        # vFAC_Z = mathutils.Vector((0.0, -math.sin(dFAC_Roll_rad), math.cos(dFAC_Roll_rad)))
        # vFAC_Y = vFAC_Z.cross(vX)
        vY = self.vZ.cross(vX)

        mA = mathutils.Matrix([vX, vY, self.vZ, vFAC_Pos])
        mA = mA.to_4x4()
        mA.transpose()

        # Apply the full world matrix
        self.objFAC.matrix_world = mA

        vSAC_Pos = vFAC_Pos + self.dAxisSep * vX

        vRC_Pos1 = self.lRC_Pos[iPntIdx1]
        vRC_Pos2 = self.lRC_Pos[iPntIdx2]
        vRC_Pos = None

        if vRC_Pos1 is not None and vRC_Pos2 is not None:
            dSign = (vRC_Pos1 - vFAC_Pos).dot(vRC_Pos2 - vFAC_Pos)
            if dSign > 0.0:
                vRC_Pos = vRC_Pos1 * (1.0 - dFac2) + vRC_Pos2 * dFac2
            # endif
        # endif

        mWorldInv = self.objFAC.matrix_world.to_3x3().inverted()

        vSteer1 = self._GetSteerDir(iPntIdx1, vY, vSAC_Pos)
        vSteer2 = self._GetSteerDir(iPntIdx2, vY, vSAC_Pos)
        vSteer = (vSteer1 * (1.0 - dFac2) + vSteer2 * dFac2).normalized()
        vSAC_X = vSteer.cross(self.vZ)

        self._SetMatrixLocal(self.objSAC, vSAC_X, vSteer, self.vZ, mWorldInv, 0.0)

        dSteerAngle_rad = math.acos(vY.dot(vSteer))
        dSign = (vY.cross(vSteer)).dot(self.vZ)
        dSign = 1.0 if dSign >= 0.0 else -1.0
        dSteerAngle_rad *= dSign

        self.objSATO.rotation_euler = (0.0, 0.0, dSteerAngle_rad)
        self.objSATS.rotation_euler = (0.0, dSAC_SpinAngle_rad, 0.0)
        self.objFAS.rotation_euler = (0.0, dFAC_SpinAngle_rad, 0.0)
        self.objFAR.rotation_euler = (dFAC_Roll_rad, 0.0, 0.0)

        if self.objRot is not None:
            if vRC_Pos is not None:
                self.objRot.location = vRC_Pos
            else:
                self.objRot.location = 10000.0 * vY
            # endif
        # endif

        # Apply the world matrix of the curve object
        # to place vehicle at correct world position.
        self.objFAC.matrix_world = self.xCurve.matrix_world @ self.objFAC.matrix_world

        # Ensure that location and matrix_world properties are consistent
        anyblend.viewlayer.Update()

    # enddef


# endclass
