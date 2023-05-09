#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: /__init__.py
# Created Date: Thursday, October 22nd 2020, 1:52:43 pm
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

bl_info = {
    "name": "AnyVehicle",
    "description": "Vehicle animation.",
    "author": "Christian Perwass",
    # "version": (settings.VERSION_MAJOR, settings.VERSION_MINOR),
    "version": (1, 1),
    "blender": (2, 80, 0),
    "location": "View3D > Toolshelf > AnyVehicle",
    "warning": "",  # used for warning icon and text in addons panel
    # "wiki_url": "https://docs.google.com/document/d/15iQoycej0DfRhtZTpLxPe6VaAN4Ro5WOmv18fTWN0cY",
    # "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/"
    #            "Scripts/My_Script",
    # "tracker_url": "http://google.com", <-- a bit rude don't you think?
    # "tracker_url": "https://blenderartists.org/t/graswald/678219",
    "support": "COMMUNITY",
    "category": "Object",
}


##################################################################
try:
    import _bpy

    bInBlenderContext = True

except Exception:
    bInBlenderContext = False
# endtry

if bInBlenderContext is True:
    try:

        import importlib

        if "anim" in locals():
            importlib.reload(anim)
        else:
            from . import anim
        # endif

        if "av_ui_vehicle" in locals():
            importlib.reload(av_ui_vehicle)
        else:
            from . import av_ui_vehicle
        # endif

        if "av_props_vehicle_4w" in locals():
            importlib.reload(av_props_vehicle_4w)
        else:
            from . import av_props_vehicle_4w
        # endif

        if "av_props_vehicle_2w" in locals():
            importlib.reload(av_props_vehicle_2w)
        else:
            from . import av_props_vehicle_2w
        # endif

        if "av_ops_vehicle" in locals():
            importlib.reload(av_ops_vehicle)
        else:
            from . import av_ops_vehicle
        # endif
    except Exception as xEx:
        # pass
        print(">>>> Exception importing libs:\n{}".format(str(xEx)))
    # endif
# endif in Blender Context


##################################################################
# Register function
def register():
    try:
        av_ui_vehicle.register()
        av_props_vehicle_2w.register()
        av_props_vehicle_4w.register()
        av_ops_vehicle.register()

    except Exception as Ex:
        print("Error registering AnyBlend plugin classes.")
        print(Ex)
    # endtry


# enddef


##################################################################
# Unregister function
def unregister():
    av_ops_vehicle.unregister()
    av_props_vehicle_2w.unregister()
    av_props_vehicle_4w.unregister()
    av_ui_vehicle.unregister()


# enddef
