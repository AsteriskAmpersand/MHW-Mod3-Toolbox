# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 18:32:19 2020

@author: AsteriskAmpersand
"""


# -*- coding: utf-8 -*-
"""
Created on Mon Oct 28 23:04:20 2019

@author: AsteriskAmpersand
"""
import bpy

def execute_operator(self, context):
    if self.add_rig != "pass":
        eval('bpy.ops.' + self.add_rig + '()')
    
class ImportPremade(bpy.types.PropertyGroup):
    mode_options = [
        ("pass", "Select Rig", '', 'EMPTY_DATA', 0),
        ("mod_tools.add_fplayer_rig", "Player Female Rig", "Statyk's Female Player Rig", 'POSE_DATA', 1),
        ("mod_tools.add_mplayer_rig", "Player Male Rig", "Statyk's Male Player Rig", 'POSE_DATA', 2),
        #("mesh.primitive_cube_add", "Cube", '', 'MESH_CUBE', 1),
    ]

    add_rig = bpy.props.EnumProperty(
        name = "Add Rig",
        items=mode_options,
        description="Imports the selected rigging setup",
        default="pass",
        update=execute_operator
    )

class ModTools(bpy.types.Panel):
    bl_category = "MHW Tools"
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
        #addon_props = self.addon_props
        col = layout.column(align = True)
        col.label("Custom Properties")
        row = col.row(align = True)
        row.operator("mod_tools.copy_prop", icon='MESH_DATA', text="Copy")
        row.operator("mod_tools.paste_prop", icon='MESH_DATA', text="Paste")
        #col.separator()
        
        col.separator()
        col.prop(context.scene.import_premade, "add_rig", text = "Add Rig")
        
        col.label("Rename Vertex Groups")
        row = col.row(align = True)
        row.operator("mod_tools.target_armature", icon='ARMATURE_DATA', text="To Armature")
        row.operator("mod_tools.target_weights", icon='EMPTY_DATA', text="To Empty")
        col.separator()
        
        col.operator("mod_tools.bone_to_id", icon='CONSTRAINT_BONE', text="Rename Bones to ID")
        col.operator("mod_tools.bone_rename", icon='CONSTRAINT_BONE', text="Rename Bones")
        col.operator("mod_tools.bone_merge", icon='CONSTRAINT_BONE', text="Merge Skeletons")
        
        #col.prop(addon_props, 'limit_application', text = 'Limit to Selection')
        col.operator("mod_tools.mark_uv_rep", icon='EDGESEL', text="Mark Repeated UVs")
        col.operator("mod_tools.solve_uv_rep", icon='SNAP_EDGE', text="Solve Repeated UVs")
        col.operator("mod_tools.solve_sharp_rep", icon='SNAP_EDGE', text="Split Sharp and Repeated UVs")
        col.operator("mod_tools.clean_uvs", icon='GROUP_UVS', text="Clean UV List")
        col.operator("mod_tools.clean_color", icon='COLOR', text="Clean Vertex Colors")
        col.operator("mod_tools.generate_color", icon='COLOR', text="Generate Vertex Colors")
        col.operator("mod_tools.set_color", icon='COLOR', text="Set Vertex Colors")
        col.operator("mod_tools.clean_materials", icon='GROUP_UVS', text="Clean Materials List")        
        col.operator("mod_tools.clean_weights", icon='GROUP_VERTEX', text="Remove Unweighted Groups")
        col.operator("mod_tools.limit_normalize", icon='GROUP_VERTEX', text="Limit Weights to Label")
        col.operator("mod_tools.mass_weight", icon='GROUP_VERTEX', text="Mass Weight to Bone")
        col.operator("mod_tools.nuke_weights", icon='GROUP_VERTEX', text="Delete Weights")
        col.operator("mod_tools.collapse_weights", icon='GROUP_VERTEX', text="Collapse Weights")
        col.operator('mod_tools.reindex_meshes', icon='GROUP_VERTEX', text="Reindex Meshes")
        col.operator("mod_tools.mass_triangulate", icon='GROUP_VERTEX', text="Triangulate")