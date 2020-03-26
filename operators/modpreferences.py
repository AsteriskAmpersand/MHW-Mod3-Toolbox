# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 02:47:01 2020

@author: AsteriskAmpersand
"""


import bpy


class ModPrefs(bpy.types.AddonPreferences):
    bl_idname = __package__.split('.')[0]

    data = {
            "properties_buffer" : {},
            "data_properties_buffer" : {},
            "properties_type" : "",
            }    