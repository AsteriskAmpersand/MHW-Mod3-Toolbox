# -*- coding: utf-8 -*-
"""
Created on Tue Dec 15 00:41:30 2020

@author: AsteriskAmpersand
"""

import bpy
from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty, FloatProperty
from bpy.types import Operator
from mathutils import Vector, Matrix
from .modtools import getSelection

import sys
sys.path.append("..")

from collections import OrderedDict
try:
    from ..common.Cstruct import PyCStruct
except:
    import sys
    sys.path.insert(0, r'..\common')
    from Cstruct import PyCStruct, FileClass
    
class PLEntry(PyCStruct):
    fields = OrderedDict([
    	("index", "int"),#
    	("pos", "float[3]"),#
    ])

class PL(PyCStruct):
    fields = OrderedDict([
    	("sig", "ubyte[4]"),#
    	("EA15", "ubyte[4]"),#
        ("count","int")
    ])
    def marshall(self,data):
        super().marshall(data)
        self.entries = [PLEntry().marshall(data) for _ in range(self.count)]
        return self
    
    def construct(self,entrylist):
        self.sig = b"\x50\x4C\x00\x00"
        self.EA15 = b"\xEA\x15\x00\x00"
        self.count = len(entrylist)
        self.entries = [PLEntry().construct(entry) for entry in entrylist]
        return self
    
    def serialize(self):
        data = super().serialize()
        data += b''.join((entry.serialize() for entry in self.entries))
        return data

class PLFile():
    def __init__(self,path = None,pl=None):
        if path:
            self.marshall(path)
        if pl:
            self.PL = pl
    def marshall(self,path):
        with open(path,"rb") as inf:
                self.PL = PL().marshall(inf)
    def serialize(self,path):
        with open(path,"wb") as outf:
            outf.write(self.PL.serialize())

class ImportPL(Operator, ImportHelper):
    bl_idname = "custom_import.import_mhw_pl"
    bl_label = "Load MHW PL file (.pl)"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
 
    # ImportHelper mixin class uses this
    filename_ext = ".pl"
    filter_glob = StringProperty(default="*.pl", options={'HIDDEN'}, maxlen=255)

    def readPLData(self,pldata):
        listing = {}
        for entry in pldata:
            listing[entry.index] = Vector(entry.pos)
        for obj in bpy.context.scene.objects:
            if obj.type == "MESH" and "unknownIndex" in obj.data:
                ix = obj.data["unknownIndex"]-1
                if ix in listing:
                    obj.location += listing[ix]

    def execute(self,context):
        pldata = PLFile(self.filepath).PL.entries
        self.readPLData(pldata)
        return {'FINISHED'}

class ExportPL(Operator, ExportHelper):
    bl_idname = "custom_export.export_mhw_pl"
    bl_label = "Save MHW PL file (.pl)"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
 
    # ImportHelper mixin class uses this
    filename_ext = ".pl"
    filter_glob = StringProperty(default="*.pl", options={'HIDDEN'}, maxlen=255)
    
    limit_application = bpy.props.BoolProperty(
                        name = 'Limit to selected obejcts',
                        description = 'Limit operator actions to current selected objects',
                        default = False
                        )
    undo_transform = bpy.props.BoolProperty(
                        name = 'Untransform Objects during Export',
                        description = 'Untransform Objects during Export',
                        default = True
                        )
    
    def compilePLData(self,objs):
        listing = {}
        for obj in objs:
            if "unknownIndex" in obj.data:
                ix = obj.data["unknownIndex"]-1
                listing[ix] = obj.matrix_world.translation
        return listing
    
    def listingToPL(self,listing):
        return PL().construct([{"index" : ix, "pos" : list(pos)[:3]} for ix,pos in sorted(listing.items())])
            
    def destroyTransform(self,selection,listing):
        #print(selection)
        for mesh in selection:
            if "unknownIndex" in mesh.data:
                ix = mesh.data["unknownIndex"]-1
                if ix in listing:
                    print(mesh.name)
                    print(mesh.location)
                    mesh.location -= listing[ix]
                    print(mesh.location)
            
    def execute(self,context):
        select = list(getSelection(self.limit_application))
        listing = self.compilePLData(select)
        pl = self.listingToPL(listing)
        PLFile(pl=pl).serialize(self.filepath)
        if self.undo_transform:
            self.destroyTransform(select,listing)
        return {'FINISHED'}
    
    
    
def menu_func_import(self, context):
    self.layout.operator(ImportPL.bl_idname, text="MHW PL (.pl)")

def menu_func_export(self, context):
    self.layout.operator(ExportPL.bl_idname, text="MHW PL (.pl)")
    