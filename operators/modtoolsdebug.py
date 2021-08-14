# -*- coding: utf-8 -*-
"""
Created on Sat Aug 14 15:38:15 2021

@author: AsteriskAmpersand
"""

import bpy

def isEmptySkeletons(self,obj):
    return "Type" in obj and obj["Type"] == "MOD3_SkeletonRoot"

def isArmature(self,obj):
    return  obj.type == "ARMATURE"

class TransferTargets(bpy.types.PropertyGroup):            
    emptySkeleton = bpy.props.PointerProperty(name = "Empty Hierarchy", type = bpy.types.Object, poll = isEmptySkeletons)
    armatureSkeleton = bpy.props.PointerProperty(name = "Player Rig", type = bpy.types.Object, poll = isArmature)


class ModTools(bpy.types.Panel):
    bl_category = "MHW Tools Test"
    bl_idname = "panel.mhw_mod"
    bl_label = "MOD3 Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    # bl_category = "Tools"

    addon_key = __package__.split('.')[0]

    def draw(self, context):
        addon = context.user_preferences.addons[self.addon_key]
        self.addon_props = addon.preferences
        
        layout = self.layout
        #self.layout.label("CCL Capsule Tools")
        #self.layout.operator("ctc_tools.mesh_from_capsule", icon='MESH_CUBE', text="Mesh from Capsule")
        self.draw_mod_tools(context, layout)
        layout.separator()

        
    def draw_mod_tools(self, context, layout):
        col = layout.column(align = True)
        col.label("Rename Vertex Groups")
        row = col.row(align = True)
        row.operator("mod_tools.target_armature", icon='ARMATURE_DATA', text="To Armature")
        row.operator("mod_tools.target_weights", icon='EMPTY_DATA', text="To Empty")
        col.separator()
        
class transferOperator():
    def check(self,context):
        if self.properties.emptySkeleton is None:
            return False
        if self.properties.armatureSkeleton is None:
            return False
        return True
    
    def draw(self,context):
        layout = self.layout
        layout.prop(self.properties,"emptySkeleton")
        layout.prop(self.properties,"armatureSkeleton")       
    
    def getArmature(self,context):
        return context.scene.mod3toolbox_transfer_targets.armatureSkeleton
    
    def recursiveList(self,empty):
        deepChildren = [empty]
        for e in empty.children:
            deepChildren += self.recursiveList(e)
        return deepChildren
    
    def getEmptyHierarchy(self,context):        
        emptyRoot = self.properties.emptySkeleton
        ehierarchy = [e for e in self.recursiveList(emptyRoot) if e.type == "EMPTY" and "boneFunction" in e]
        return ehierarchy
    
    def generateEmptyMapFrom(self,context):
        fromEmpty = {}
        ehierarchy = self.getEmptyHierarchy(context)
        for ebone in ehierarchy:
            fromEmpty[ebone["boneFunction"]] = ebone
        return fromEmpty

class targetArmature(transferOperator,bpy.types.Operator):
    bl_idname = 'mod_tools.target_armature'
    bl_label = "Rename Groups to Armature Names"
    bl_description = "Renames every vertex group to it's Armature Target Name based on Current Bone Function ID."
    bl_options = {"REGISTER", "UNDO"}    

    properties =  bpy.props.PropertyGroup(type=TransferTargets)   

    def execute(self,context):
        if not self.check(context):
            return {'FINISHED'}
        fromEmpty = self.generateEmptyMapFrom(context)
        armature = self.getArmature(context)
        remapTable = {}        
        for bone in armature.pose.bones:
            if "boneFunction" in bone and bone["boneFunction"] in fromEmpty:
                remapTable[fromEmpty[bone["boneFunction"]].name] = bone.name
                
        for mesh in [o for o in bpy.context.scene.objects if o.type == "MESH"]:
            for group in mesh.vertex_groups:
                if group.name in remapTable:
                    group.name = remapTable[group.name]
            modifiers = mesh.modifiers
            if "Auxiliary Armature" not in modifiers:
                mod = modifiers.new("Auxiliary Armature","ARMATURE")
                mod.object = armature
            else:
                modifiers["Auxiliary Armature"].object = armature
        return {'FINISHED'}

class targetEmpties(transferOperator,bpy.types.Operator):
    bl_idname = 'mod_tools.target_weights'
    bl_label = "Rename Groups to Empty Names"
    bl_description = "Renames every vertex group to it's Empty Target Name based on Current Bone Function ID."
    bl_options = {"REGISTER", "UNDO"}    

    properties =  bpy.props.PropertyGroup(type=TransferTargets)   

    def execute(self,context):
        if not self.check(context):
            return {'FINISHED'}
        fromArmature = {}
        remapTable = {}
        
        armature = self.getArmature(context)
        empties = self.getEmptyHierarchy(context)
        
        for bone in armature.pose.bones:
            if "boneFunction" in bone:
                fromArmature[bone["boneFunction"]]=bone
        for ebone in empties:
            if ebone["boneFunction"] in fromArmature:
                remapTable[fromArmature[ebone["boneFunction"]].name] = ebone.name
                
        for mesh in [o for o in bpy.context.scene.objects if o.type == "MESH"]:
            for group in mesh.vertex_groups:
                if group.name in remapTable:
                    group.name = remapTable[group.name]
            #modifiers = mesh.modifiers
            #if not "Auxiliary Armature" not in modifiers:
            #    mod = modifiers.new("Auxiliary Armature","ARMATURE")
            #    mod.object = armature
            #else:
            #    modifiers["Auxiliary Armature"].object = armature
                
        return {'FINISHED'}