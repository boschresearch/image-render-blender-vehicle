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
class CPlanarSingleTrack4wModel:

    #############################################################
    def __init__(
        self,
        *,
        NurbsCurve,
        VectorUp,
        Speed_kmh,
        WheelRadius,
        FixedAxisOrigObj,
        FixedAxisLeftObj,
        FixedAxisRightObj,
        FixedAxisLeftSpinObj,
        FixedAxisRightSpinObj,
        SteerAxisOrigObj,
        SteerAxisLeftObj,
        SteerAxisRightObj,
        SteerAxisLeftSpinObj,
        SteerAxisRightSpinObj,
        RotOrigObj=None
    ):

        self.xCurve = NurbsCurve
        self.vZ = VectorUp
        self.dWheelRadius = WheelRadius
        self.dSpeed_ms = 0.0
        self.SetSpeed_kmh(Speed_kmh)

        self.objFAC = FixedAxisOrigObj
        self.objFAL = FixedAxisLeftObj
        self.objFAR = FixedAxisRightObj
        self.objFALS = FixedAxisLeftSpinObj
        self.objFARS = FixedAxisRightSpinObj

        self.objSAC = SteerAxisOrigObj
        self.objSAL = SteerAxisLeftObj
        self.objSAR = SteerAxisRightObj
        self.objSALS = SteerAxisLeftSpinObj
        self.objSARS = SteerAxisRightSpinObj

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

        self.lSALS_Pos = []
        self.dSALS_LenTotal = 0.0
        self.lSALS_Len = [0.0]

        self.lSARS_Pos = []
        self.dSARS_LenTotal = 0.0
        self.lSARS_Len = [0.0]

        self.lFALS_Pos = []
        self.dFALS_LenTotal = 0.0
        self.lFALS_Len = [0.0]

        self.lFARS_Pos = []
        self.dFARS_LenTotal = 0.0
        self.lFARS_Len = [0.0]

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

            vSALS_Pos = mWorld @ self.objSAL.matrix_local @ self.objSALS.location
            self.lSALS_Pos.append(vSALS_Pos)

            vSARS_Pos = mWorld @ self.objSAR.matrix_local @ self.objSARS.location
            self.lSARS_Pos.append(vSARS_Pos)

            vFALS_Pos = mWorld @ self.objFAL.matrix_local @ self.objFALS.location
            self.lFALS_Pos.append(vFALS_Pos)

            vFARS_Pos = mWorld @ self.objFAR.matrix_local @ self.objFARS.location
            self.lFARS_Pos.append(vFARS_Pos)

            if iPntIdx > 0:
                self.dSAC_LenTotal += (vSAC_Pos - self.lSAC_Pos[iPntIdx - 1]).length
                self.lSAC_Len.append(self.dSAC_LenTotal)

                self.dSALS_LenTotal += (vSALS_Pos - self.lSALS_Pos[iPntIdx - 1]).length
                self.lSALS_Len.append(self.dSALS_LenTotal)

                self.dSARS_LenTotal += (vSARS_Pos - self.lSARS_Pos[iPntIdx - 1]).length
                self.lSARS_Len.append(self.dSARS_LenTotal)

                self.dFALS_LenTotal += (vFALS_Pos - self.lFALS_Pos[iPntIdx - 1]).length
                self.lFALS_Len.append(self.dFALS_LenTotal)

                self.dFARS_LenTotal += (vFARS_Pos - self.lFARS_Pos[iPntIdx - 1]).length
                self.lFARS_Len.append(self.dFARS_LenTotal)
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
        vFAC_Pos_Orig = self.lFAC_Pos[0]

        vFAC_Pos = (
            self.lFAC_Pos[iPntIdx1] * (1.0 - dFac2) + self.lFAC_Pos[iPntIdx2] * dFac2
        )
        vFAC_Deriv = (
            self.lFAC_Deriv[iPntIdx1] * (1.0 - dFac2)
            + self.lFAC_Deriv[iPntIdx2] * dFac2
        )

        dSALS_Len = (
            self.lSALS_Len[iPntIdx1] * (1.0 - dFac2) + self.lSALS_Len[iPntIdx2] * dFac2
        )
        dSALS_SpinAngle_rad = dSALS_Len / self.dWheelRadius

        dSARS_Len = (
            self.lSARS_Len[iPntIdx1] * (1.0 - dFac2) + self.lSARS_Len[iPntIdx2] * dFac2
        )
        dSARS_SpinAngle_rad = dSARS_Len / self.dWheelRadius

        dFALS_Len = (
            self.lFALS_Len[iPntIdx1] * (1.0 - dFac2) + self.lFALS_Len[iPntIdx2] * dFac2
        )
        dFALS_SpinAngle_rad = dFALS_Len / self.dWheelRadius

        dFARS_Len = (
            self.lFARS_Len[iPntIdx1] * (1.0 - dFac2) + self.lFARS_Len[iPntIdx2] * dFac2
        )
        dFARS_SpinAngle_rad = dFARS_Len / self.dWheelRadius

        # print("dFALS_Len: {0}, angle: {1}".format(dFALS_Len, dFALS_SpinAngle_rad))

        vX = vFAC_Deriv.normalized()
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

        self._SetMatrixLocal(self.objSAL, vSAC_X, vSteer, self.vZ, mWorldInv, 0.0)
        self._SetMatrixLocal(self.objSAR, vSAC_X, vSteer, self.vZ, mWorldInv, 0.0)
        self.objSALS.rotation_euler = (0.0, dSALS_SpinAngle_rad, 0.0)
        self.objSARS.rotation_euler = (0.0, dSARS_SpinAngle_rad, 0.0)

        self._SetMatrixLocal(self.objFAL, vX, vY, self.vZ, mWorldInv, 0.0)
        self._SetMatrixLocal(self.objFAR, vX, vY, self.vZ, mWorldInv, 0.0)
        self.objFALS.rotation_euler = (0.0, dFALS_SpinAngle_rad, 0.0)
        self.objFARS.rotation_euler = (0.0, dFARS_SpinAngle_rad, 0.0)

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
