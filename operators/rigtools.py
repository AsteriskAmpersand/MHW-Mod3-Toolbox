# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 12:36:19 2020

@author: AsteriskAmpersand
"""
import os
import bpy
from pathlib import Path
from .modtools import modTool

def getScriptPath():
    return os.path.dirname(os.path.abspath(__file__))

def getAssetPath():
    script = Path(getScriptPath()).parent
    return script.joinpath("assets")

class getRig(modTool):
    opname = "add_rig"
    rigname = "None"
    bl_idname = 'mod_tools.%s'%opname
    bl_label = "Adds %s"%rigname
    bl_description = "Adds %s to the scene."%rigname
    bl_options = {"REGISTER", "PRESET", "UNDO"}  
    
    #@classmethod
    #def poll(cls,context):
    #    return Path(getAssetPath().joinpath("%s.blend"%cls.rigpath)).exists()
    
    def execute(self,context):
        directory = str(getAssetPath().joinpath("%s.blend"%self.rigpath).joinpath("Object"))+"\\"
        filename = self.assetname
        bpy.ops.wm.append(directory = directory, filename = filename)
        return {"FINISHED"}

class getFPlayerRig(getRig):
    opname = "add_fplayer_rig"
    rigname = "Statyk's Female Player Rig"
    
    rigpath = "asset_library"
    assetname = "MHW Statyk Female Character Rig"
    
    bl_idname = 'mod_tools.%s'%opname
    bl_label = "Adds %s"%rigname
    bl_description = "Adds %s to the scene."%rigname
    bl_options = {"REGISTER", "PRESET", "UNDO"}  
    
class getMPlayerRig(getRig):
    opname = "add_mplayer_rig"
    rigname = "Statyk's Male Player Rig"
    
    rigpath = "asset_library"
    assetname = "MHW Statyk Male Character Rig"
    
    bl_idname = 'mod_tools.%s'%opname
    bl_label = "Adds %s"%rigname
    bl_description = "Adds %s to the scene."%rigname
    bl_options = {"REGISTER", "PRESET", "UNDO"}  