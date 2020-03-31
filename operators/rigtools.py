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
        #directory = str(getAssetPath().joinpath("%s.blend"%self.rigpath).joinpath("Object"))+"\\"
        #filename = self.assetname
        #bpy.ops.wm.append(directory = directory, filename = filename)
        #
        filepath = str(getAssetPath().joinpath("%s.blend"%self.rigpath))
        #append object from .blend file
        with bpy.data.libraries.load(filepath) as (data_from, data_to):
            data_to.objects = data_from.objects
        
        #link object to current scene
        for obj in data_to.objects:
            if obj is not None:
                bpy.context.scene.objects.link(obj)
        return {"FINISHED"}

class getFPlayerRig(getRig):
    opname = "add_fplayer_rig"
    rigname = "Statyk's Female Player Rig"
    
    rigpath = "statyk_female_rig"
    assetname = "MHW Statyk Female Character Rig"
    
    bl_idname = 'mod_tools.%s'%opname
    bl_label = "Adds %s"%rigname
    bl_description = "Adds %s to the scene."%rigname
    bl_options = {"REGISTER", "PRESET", "UNDO"}  
    
class getMPlayerRig(getRig):
    opname = "add_mplayer_rig"
    rigname = "Statyk's Male Player Rig"
    
    rigpath = "statyk_male_rig"
    assetname = "MHW Statyk Male Character Rig"
    
    bl_idname = 'mod_tools.%s'%opname
    bl_label = "Adds %s"%rigname
    bl_description = "Adds %s to the scene."%rigname
    bl_options = {"REGISTER", "PRESET", "UNDO"}  