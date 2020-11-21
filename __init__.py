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

from .operators.modtools import (massTriangulate,
                                 nukeWeights,limitWeights,cleanGroups,cleanColor,generateColor,
                                 solveUVSharp,solveUV,markUV,boneToID,pasteProp,copyProp,
                                 targetArmature, targetEmpties, massWeight, collapseWeights,
                                 boneRename, skeletonMerge,
                                 cleanMaterials)
from .operators.rigtools import (getFPlayerRig, getMPlayerRig)
from .operators.modtoolspanel import ModTools, ImportPremade
from .operators.modpreferences import ModPrefs

from .operators.selection import Selection


classes = [Selection,
             massTriangulate,
             nukeWeights,limitWeights,cleanGroups,cleanColor,generateColor,
             solveUVSharp,solveUV,markUV,boneToID,pasteProp,copyProp,
             targetArmature, targetEmpties, massWeight, collapseWeights,
             boneRename, skeletonMerge,
             cleanMaterials,
             getFPlayerRig,getMPlayerRig,
             ModTools,ImportPremade,
             ModPrefs
           ]

def register():
    for cl in classes:
        bpy.utils.register_class(cl)
    bpy.types.Scene.import_premade = bpy.props.PointerProperty(type=ImportPremade)
    
def unregister():
    for cl in classes:
        bpy.utils.unregister_class(cl)
    del bpy.types.Scene.import_premade
    
if __name__ == "__main__":
    try:
        unregister()
    except:
        pass
    register()
