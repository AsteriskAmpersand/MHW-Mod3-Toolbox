# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 18:28:15 2020

@author: AsteriskAmpersand
"""


# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 13:38:47 2019

@author: AsteriskAmpersand
"""
#from .dbg import dbg_init
#dbg_init()

content=bytes("","UTF-8")
bl_info = {
    "name": "MHW Mod3 Tools",
    "category": "Game Engine",
    "author": "AsteriskAmpersand",
    "location": "View3D > MHW Tools > Mod3/MHW",
    "version": (1,0,0)
}
 
import bpy

from .operators.modtools import (massTriangulate,nukeWeights,limitWeights,
                                 cleanGroups,cleanColor,generateColor,setColour,
                                 solveUVSharp,solveUV,markUV,boneToID,pasteProp,copyProp,
                                 targetArmature, targetEmpties, massWeight, collapseWeights,
                                 boneRename, boneToIndex, skeletonMerge, reindexMeshes,reindexBones,
                                 cleanMaterials,cleanUVs, weightDiscretization)
from .operators.rigtools import (getFPlayerRig, getMPlayerRig)
from .operators.modtoolspanel import ModTools, ImportPremade
from .operators.modpreferences import ModPrefs
from .operators.plimportexport import ImportPL,ExportPL
from .operators.plimportexport import menu_func_import as import_func
from .operators.plimportexport import menu_func_export as export_func


from .operators.selection import Selection


classes = [Selection,
             massTriangulate,
             nukeWeights,limitWeights,cleanGroups,cleanColor,generateColor,setColour,
             solveUVSharp,solveUV,markUV,boneToID,boneToIndex,pasteProp,copyProp,
             targetArmature, targetEmpties, massWeight, collapseWeights, weightDiscretization,
             boneRename, skeletonMerge, reindexMeshes,reindexBones,
             cleanMaterials,cleanUVs,
             getFPlayerRig,getMPlayerRig,
             ModTools,ImportPremade,
             ModPrefs,
             #ImportPL,ExportPL,
           ]

def register():
    for cl in classes:
        bpy.utils.register_class(cl)
    bpy.types.INFO_MT_file_import.append(import_func)
    bpy.types.INFO_MT_file_export.append(export_func)
    bpy.types.Scene.import_premade = bpy.props.PointerProperty(type=ImportPremade)
    
def unregister():
    for cl in classes:
        bpy.utils.unregister_class(cl)
    del bpy.types.Scene.import_premade
    bpy.types.INFO_MT_file_import.remove(import_func)
    bpy.types.INFO_MT_file_export.remove(export_func)
    
if __name__ == "__main__":
    try:
        unregister()
    except:
        pass
    register()
