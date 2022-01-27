# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 21:26:53 2020

@author: AsteriskAmpersand
"""
import bpy
import bmesh
import re
import random
from collections import OrderedDict

class modTool(bpy.types.Operator):
    addon_key = __package__.split('.')[0]
    #addon = bpy.context.user_preferences.addons[addon_key]    
    def __init__(self):
        self.addon = bpy.context.user_preferences.addons[self.addon_key]

class copyProp(modTool):
    bl_idname = 'mod_tools.copy_prop'
    bl_label = "Copy Mesh Properties"
    bl_description = 'Copy the Custom Properties of the Active Mesh'
    bl_options = {"REGISTER"}        
    @classmethod
    def poll(cls, context):
        return (bpy.context.active_object is not None)
    
    def execute(self,context):
        active_object = bpy.context.active_object
        self.addon.preferences.data["properties_buffer"] = {prop:active_object[prop] for prop in active_object.keys()}
        #print({prop:active_object[prop] for prop in active_object.keys()})
        #print(self.addon.preferences.properties_buffer)
        try:
            self.addon.preferences.data["data_properties_buffer"] = {prop:active_object.data[prop] for prop in active_object.data.keys()}
        except:
            self.addon.preferences.data["data_properties_buffer"] = {}
        self.addon.preferences.data["properties_type"] = active_object.type
        return {'FINISHED'}

        #row.operator("mod_tools.copy_mesh_prop", icon='MESH_DATA', text="Copy")
        
class pasteProp(modTool):
    bl_idname = 'mod_tools.paste_prop'
    bl_label = "Paste Mesh Properties"
    bl_description = 'Paste the Custom Properties of the Active Mesh'
    bl_options = {"REGISTER"}    
    
    @classmethod
    def poll(cls, context):
        return ((bpy.context.user_preferences.addons[cls.addon_key].preferences.data["properties_buffer"] != {} or 
                 bpy.context.user_preferences.addons[cls.addon_key].preferences.data["data_properties_buffer"] != {}) and
                 len(bpy.context.selected_objects) > 0)
    #Check there's property on buffer and selection is non null
    
    def execute(self,context):
        for obj in bpy.context.selected_objects:
            if obj.type == self.addon.preferences.data["properties_type"]:
                for prop in self.addon.preferences.data["properties_buffer"]:
                    obj[prop] = self.addon.preferences.data["properties_buffer"][prop]
                for prop in self.addon.preferences.data["data_properties_buffer"]:
                    obj.data[prop] = self.addon.preferences.data["data_properties_buffer"][prop]
        return {'FINISHED'}
        
        #row.operator("mod_tools.paste_mesh_prop", icon='MESH_DATA', text="Paste")

def remapMeshBones(renameTable):
    for mesh in [o for o in bpy.context.scene.objects if o.type == "MESH"]:
        for group in mesh.vertex_groups:
            if group.name in renameTable:
                group.name = renameTable[group.name]

class boneToID(modTool):
    bl_idname = 'mod_tools.bone_to_id'
    bl_label = "Rename Bones to Function"
    bl_description = 'Renames every bone to their Bone Function ID.'
    bl_options = {"REGISTER", "PRESET", "UNDO"}    

    def execute(self,context):
        renameTable = {}
        for bone in [o for o in bpy.context.scene.objects if o.type == "EMPTY" and "boneFunction" in o]:
            newname = "BoneFunction.%03d"%bone["boneFunction"]
            renameTable[bone .name] = newname 
            bone.name = newname        
        remapMeshBones(renameTable)
        return {'FINISHED'}  

class boneToIndex(modTool):
    bl_idname = 'mod_tools.bone_to_ix'
    bl_label = "Rename Bones to Index"
    bl_description = 'Renames every bone to their Order Index.'
    bl_options = {"REGISTER", "PRESET", "UNDO"}    

    def execute(self,context):
        renameTable = {}
        for bone in [o for o in bpy.context.scene.objects if o.type == "EMPTY" and "boneFunction" in o]:
            if "indexHint" not in bone:
                index = 1024
            else:
                index = bone["indexHint"]
            newname = "Bone.%03d"%index
            renameTable[bone .name] = newname 
            bone.name = newname        
        remapMeshBones(renameTable)
        return {'FINISHED'}  

class boneRename(modTool):
    bl_idname = 'mod_tools.bone_rename'
    bl_label = "Rename Bones"
    bl_description = 'Mass Renames Bones.'
    bl_options = {"REGISTER", "PRESET", "UNDO"}    

    searchReplace = bpy.props.BoolProperty(
                        name = "Search and Replace Bone Names",
                        description = 'Change Mode to Search and Replace',
                        default = False,
            )
    prepend = bpy.props.StringProperty(
                        name = 'Prepend Text',
                        description = 'Text to prepend to the groups.',
                        default = "",
                        )
    append = bpy.props.StringProperty(
                        name = 'Append Text',
                        description = 'Text to append to the groups.',
                        default = "",
                        )
    randomize = bpy.props.BoolProperty(
                        name = "Randomize ID",
                        description = 'Add Randomized ID to Bone Name String',
                        default = True,
            )
    find = bpy.props.StringProperty(
                        name = 'Text to Find',
                        description = 'Text to find on the groups.',
                        default = "",
                        )
    replace = bpy.props.StringProperty(
                        name = 'Text to Replace',
                        description = 'Text to replace on the groups.',
                        default = "",
                        )
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self, "searchReplace")
        if self.searchReplace:
            col.prop(self, "find")
            col.prop(self, "replace")
        else:
            col.prop(self, "prepend")
            col.prop(self, "append")
            col.prop(self, "randomize")            
    
    def replacementFunction(self,bone):
        if not self.searchReplace:
            return self.prepend + ("-"+("%1.8f"%random.random())[2:]+"-" if self.randomize else "") + bone.name + self.append
        else:
            return re.sub(self.find, self.replace, bone.name)
    
    def execute(self,context):
        renameTable = {}
        for bone in [o for o in bpy.context.scene.objects if o.type == "EMPTY" and "boneFunction" in o]:
            newname = self.replacementFunction(bone)
            renameTable[bone .name] = newname 
            bone.name = newname        
        remapMeshBones(renameTable)
        return {'FINISHED'}

        #col.operator("mod_tools.bone_rename", icon='CONSTRAINT_BONE', text="Rename Bones")

class skeletonMerge(modTool):
    bl_idname = 'mod_tools.bone_merge'
    bl_label = "Merge Selected Skeleton into Active Skeleton"
    bl_description = 'Merges Selected Skeleton into Active Skeleton fusing similar bone functions and reparenting physics entries.'
    bl_options = {"REGISTER", "PRESET", "UNDO"}
    
    #ignoreDistance = bpy.props.BoolProperty(
    #                    name = "Ignore Match Distance",
    #                    description = 'Ignores if the distance between identical functions is above threshold',
    #                    default = True,
    #        )
    #threshold = bpy.props.FloatProperty(
    #                    name = 'Match Distance',
    #                    description = 'Distance tolerance for identical functions to not stop and error out.',
    #                    default = 0.01,
    #                    )
    
    @classmethod
    def poll(cls, context):
        try:
            result = all(("Type" in root and root["Type"] == "MOD3_SkeletonRoot" for root in bpy.selection)) and context.active_object
        except:
            result = all(("Type" in root and root["Type"] == "MOD3_SkeletonRoot" for root in bpy.context.selected_objects)) and context.active_object
        return result

    def execute(self,context):
        target = context.active_object   
        try:
            sources = [x for x in bpy.selection]
        except:
            sources = [x for x in bpy.context.selected_objects]
        for source in sources:
            if source != target:
                targetMapping = self.generateMapping(target)
                sourceMapping = self.generateMapping(source)
                ctcDependants = self.generateCTCDependencies(source)
                self.mergeMappings(sourceMapping,ctcDependants,targetMapping)            
                #self.cleanSource(source,target)
        return {'FINISHED'}
    
    def checkNode(self,node):
        return "Type" in node and node["Type"] == "CTC_Node" and "Bone Function" in node.constraints
    
    def examineNode(self,node,mapping):
        if not self.checkNode(node):
            return mapping
        if node.constraints["Bone Function"].target in mapping:
            mapping[node.constraints["Bone Function"].target].append(node)
        for child in node.children:
            self.examineNode(child,mapping)
        return mapping
    
    def expandSource(self,source):
        mapping = {source:list()}
        for children in source.children:
            mapping.update(self.expandSource(children))
        return mapping
    
    def generateCTCDependencies(self,source):
        dependencyMap = self.expandSource(source)
        for root in [obj for obj in bpy.context.scene.objects if "Type" in obj and obj["Type"] == "CTC"]:
            for chain in root.children:
                for node in chain.children:
                    self.examineNode(node,dependencyMap)
        return dependencyMap
                    
            
    def generateMapping(self,root):
        mapping = OrderedDict()
        try:
            mapping[int(root["boneFunction"])] = root
        except:
            pass
        for c in root.children:
            mapping.update(self.generateMapping(c))
        return mapping

    def mergeMappings(self,source,sourceCtcDependants,target):
        mergeTable = {}
        for function in source:
            if function in target:
                for children in source[function].children:
                    children.parent = target[function]
                    if source[function] in sourceCtcDependants:
                        for dependent in sourceCtcDependants[source[function]]:
                            dependent.constraints["Bone Function"].target = target[function]
                    mergeTable[source[function].name]=target[function].name                
                bpy.data.objects.remove(source[function], do_unlink=True)
        remapMeshBones(mergeTable)
    #col.operator("mod_tools.bone_rename", icon='CONSTRAINT_BONE', text="Rename Bones")

    def meshReplace(sourceName,targetName):
        pass

def getSelection(onlySelection, selectionType = "MESH"):
    return [obj for obj in (bpy.context.selected_objects if onlySelection else bpy.context.scene.objects) 
            if obj.type == selectionType and not obj.hide and not obj.hide_select]
  
class reindexMeshes(modTool):
    bl_idname = 'mod_tools.reindex_meshes'
    bl_label = "Reindex Meshes"
    bl_description = 'Reindexes meshes with mod3 properties.'
    bl_options = {"REGISTER", "PRESET", "UNDO"}    
    limit_application = bpy.props.BoolProperty(
                        name = 'Limit to selected obejcts',
                        description = 'Limit operator actions to current selected objects',
                        default = True
                        )

    def execute(self,context):
        meshes = getSelection(self.limit_application)
        for ix,mesh in enumerate((m for m in meshes if "unknownIndex" in m.data)):
            mesh.data["unknownIndex"] = ix+1
    
def detectRepeatedUV(mesh):
    mesh = mesh.data
    uvList = []
    offendingIndices = set()
    for layer in mesh.uv_layers:
        uvMap = {}
        for loop,loopUV in zip(mesh.loops, layer.data):
            uvPoint = (loopUV.uv[0],1-loopUV.uv[1])
            if loop.vertex_index in uvMap and uvMap[loop.vertex_index] != uvPoint:
                offendingIndices.add(loop.vertex_index)
            else:
                uvMap[loop.vertex_index] = uvPoint
        uvList.append(uvMap)
    return offendingIndices

class markUV(modTool):
    bl_idname = 'mod_tools.mark_uv_rep'
    bl_label = "Mark Repeated UVs"
    bl_description = 'Mark repeated UVs with empties.'
    bl_options = {"REGISTER", "PRESET", "UNDO"}    
    limit_application = bpy.props.BoolProperty(
                        name = 'Limit to selected obejcts',
                        description = 'Limit operator actions to current selected objects',
                        default = True
                        )

    def execute(self,context):
        meshes = getSelection(self.limit_application)
        for mesh in meshes:
            repeatedVertices = detectRepeatedUV(mesh)
            for vertIndex in repeatedVertices:
                o = bpy.data.objects.new("YAVP-%s"%mesh.name, None )
                bpy.context.scene.objects.link( o )
                o.location = mesh.matrix_world * mesh.data.vertices[vertIndex].co
                o.show_x_ray = True
                o.empty_draw_size = .5
        return {'FINISHED'}
    
        #col.operator("mod_tools.mark_uv_rep", icon='EDGESEL', text="Mark Repeated UVs")


def solveRepeatedEdge(op,mesh):
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.uv.seams_from_islands()
    #
    me = mesh.data    
    bm = bmesh.from_edit_mesh(me)
    for e in bm.edges:
        if e.seam:
            e.select = True    
    bmesh.update_edit_mesh(me, False)
    bpy.ops.mesh.edge_split()
    bpy.ops.mesh.select_all(action='DESELECT')
    """
    bpy.ops.mesh.select_all(action='DESELECT')
    bm = bmesh.from_edit_mesh(mesh.data)
    oldmode = bm.select_mode
    bm.select_mode = {'FACE'}
    faceGroups = []
    bm.faces.ensure_lookup_table()
    
    bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
    save_sync = bpy.context.scene.tool_settings.use_uv_select_sync
    bpy.context.scene.tool_settings.use_uv_select_sync = True
    faces = set(bm.faces[:])
    while faces:
        bpy.ops.mesh.select_all(action='DESELECT')  
        face = faces.pop() 
        face.select = True
        bpy.ops.uv.select_linked()
        selected_faces = {f for f in faces if f.select}
        selected_faces.add(face) # this or bm.faces above?
        faceGroups.append(selected_faces)
        faces -= selected_faces
    
    bpy.context.scene.tool_settings.use_uv_select_sync = save_sync
    
    for g in faceGroups:
        bpy.ops.mesh.select_all(action='DESELECT')
        for f in g:
            f.select = True
        bpy.ops.mesh.split()
    bpy.ops.mesh.select_all(action='DESELECT')
    bm.select_mode = oldmode
    bm.verts.ensure_lookup_table()
    bm.verts.index_update()
    bmesh.update_edit_mesh(mesh.data) 
    mesh.data.update()    
    return
    """

def bad_iter(blenderCrap):
    i = 0
    while (True):
        try:
            yield(blenderCrap[i])
            i+=1
        except:
            return
            
def selectRepeated(bm):
    bm.verts.index_update()
    bm.verts.ensure_lookup_table()
    targetVert = set()
    for uv_layer in bad_iter(bm.loops.layers.uv):
        uvMap = {}
        for face in bm.faces:
            for loop in face.loops:
                uvPoint = tuple(loop[uv_layer].uv)
                if loop.vert.index in uvMap and uvMap[loop.vert.index] != uvPoint:
                    targetVert.add(bm.verts[loop.vert.index])
                else:
                    uvMap[loop.vert.index] = uvPoint
    return targetVert

def solveRepeatedVertex(op,mesh):
    bpy.ops.mesh.select_all(action='DESELECT')
    bm = bmesh.from_edit_mesh(mesh.data)
    oldmode = bm.select_mode
    bm.select_mode = {'VERT'}    
    targets = selectRepeated(bm)
    for target in targets:
        bmesh.utils.vert_separate(target,target.link_edges)
        bm.verts.ensure_lookup_table()    
    bpy.ops.mesh.select_all(action='DESELECT')
    bm.select_mode = oldmode
    bm.verts.ensure_lookup_table()
    bm.verts.index_update()
    bmesh.update_edit_mesh(mesh.data) 
    mesh.data.update()       
    return

def solveRepeatedUV(op,mesh):
    solveRepeatedEdge(op,mesh)
    solveRepeatedVertex(op,mesh)

def cloneMesh(mesh):
    new_obj = mesh.copy()
    new_obj.data = mesh.data.copy()
    bpy.context.scene.objects.link(new_obj)
    return new_obj

def transferNormals(clone,mesh):
    m = mesh.modifiers.new("Normals Transfer","DATA_TRANSFER")
    m.use_loop_data = True
    m.loop_mapping = "NEAREST_POLYNOR"#"POLYINTERP_NEAREST"#
    m.data_types_loops = {'CUSTOM_NORMAL'}
    m.object = clone
    bpy.ops.object.modifier_apply(modifier = m.name)
    

def deleteClone(clone):
    objs = bpy.data.objects
    objs.remove(objs[clone.name], do_unlink=True)

class solveUV(modTool):
    bl_idname = 'mod_tools.solve_uv_rep'
    bl_label = "Solve repeated UVs"
    bl_description = 'Fixes the issue with Repeated UVs by Edge Splitting'
    bl_options = {"REGISTER", "PRESET", "UNDO"}    
    limit_application = bpy.props.BoolProperty(
                        name = 'Limit to selected obejcts',
                        description = 'Limit operator actions to current selected objects',
                        default = True
                        )
    smooth_normals = bpy.props.BoolProperty(
                        name = 'Tranfer old normals',
                        description = 'Transfers previous normals',
                        default = True
                        )
    solver = solveRepeatedUV
    
    def execute(self,context):
        old_active = bpy.context.scene.objects.active
        meshes = getSelection(self.limit_application)
        for mesh in meshes:
            repeatedVertices = detectRepeatedUV(mesh)
            if repeatedVertices:
                bpy.context.scene.objects.active = mesh  
                oldmode = mesh.mode
                bpy.ops.object.mode_set(mode='OBJECT')
                clone = cloneMesh(mesh)
                bpy.context.scene.objects.active = mesh  
                bpy.ops.object.mode_set(mode='EDIT')
                self.solver(mesh)
                bpy.ops.object.mode_set(mode='OBJECT')
                if self.smooth_normals:
                    transferNormals(clone,mesh)
                deleteClone(clone)
                bpy.ops.object.mode_set(mode=oldmode)            
        bpy.context.scene.objects.active = old_active
        return {'FINISHED'}
    
        #col.operator("mod_tools.solve_uv_rep", icon='SNAP_EDGE', text="Solve Repeated UVs")

def solveSharpUV(op,mesh):
    obj = mesh
    me = obj.data
    bpy.ops.mesh.select_all(action='DESELECT')
    bm = bmesh.from_edit_mesh(me)
    for e in bm.edges:
        if not e.smooth:
            e.select = True
    bpy.ops.mesh.edge_split()
    bpy.ops.mesh.select_all(action='DESELECT')
    bmesh.update_edit_mesh(me, False)
    return
        
def solveSharpRepeatedUV(op,mesh):
    solveSharpUV(op,mesh)
    solveRepeatedUV(op,mesh)
    
    
class solveUVSharp(solveUV):
    bl_idname = 'mod_tools.solve_sharp_rep'
    bl_label = "Splits Sharp Edges and Repeated UVs"
    bl_description = 'Pre-emptively splits Sharp Edges and Repeated Seams preserving shading.'
    limit_application = bpy.props.BoolProperty(
                        name = 'Limit to selected obejcts',
                        description = 'Limit operator actions to current selected objects',
                        default = True
                        )
    smooth_normals = bpy.props.BoolProperty(
                        name = 'Tranfer old normals',
                        description = 'Transfers previous normals',
                        default = True
                        )
    solver = solveSharpRepeatedUV        
        #col.operator("mod_tools.solve_sharp_rep", icon='SNAP_EDGE', text="Split Sharp and Repeated UVs")
        
class cleanColor(modTool):
    bl_idname = 'mod_tools.clean_color'
    bl_label = "Removes Colour"
    bl_description = 'Mass Deletes the Colour Channels.'
    bl_options = {"REGISTER", "PRESET", "UNDO"}
    limit_application = bpy.props.BoolProperty(
                        name = 'Limit to selected obejcts',
                        description = 'Limit operator actions to current selected objects',
                        default = True
                        )
    def execute(self,context):
        meshes = getSelection(self.limit_application)
        for obj in meshes:
            colors = list(obj.data.vertex_colors)
            for c in colors:
                obj.data.vertex_colors.remove(c)
        return {'FINISHED'}
    
        #col.operator("mod_tools.clean_color", icon='COLOR', text="Clean Vertex Colors")

class generateColor(modTool):
    bl_idname = 'mod_tools.generate_color'
    bl_label = "Generates Colour"
    bl_description = 'Generates Colour Channel from Baked Normals.'
    bl_options = {"REGISTER", "PRESET", "UNDO"}
    limit_application = bpy.props.BoolProperty(
                        name = 'Limit to selected obejcts',
                        description = 'Limit operator actions to current selected objects',
                        default = True
                        )
    
    def setRenderSetttings(self):
        bpy.context.scene.render.engine = "BLENDER_RENDER"
        bpy.context.scene.render.bake_type = "NORMALS"
        bpy.context.scene.render.use_bake_multires = False
        bpy.context.scene.render.bake_normal_space = "WORLD"
        bpy.context.scene.render.use_bake_to_vertex_color = True
        bpy.context.scene.render.use_bake_selected_to_active = True 
    
    def invert(self,obj):
        for ipoly in range(len(obj.data.polygons)):
            for idx, ivertex in enumerate(obj.data.polygons[ipoly].loop_indices):
                ivert = obj.data.polygons[ipoly].vertices[idx]
                col = obj.data.vertex_colors.active.data[ivertex].color
                obj.data.vertex_colors.active.data[ivertex].color = tuple(1-x if (i != 0 and i != 3) else x for i,x in enumerate(col))
    
    def generate(self,obj):
        bpy.context.scene.objects.active = obj
        obj.select = True            
        h,r =obj.hide, obj.hide_render
        obj.hide_render = False
        
        ix = len(obj.data.vertex_colors)
        obj.data.vertex_colors.new("World Space Normals")
        obj.data.vertex_colors.active_index = ix
        bpy.ops.object.bake_image()
        self.invert(obj)
        
        obj.select = False
        obj.hide_render = r
        obj.hide = h
    
    def execute(self,context):
        engine = bpy.context.scene.render.engine
        active = bpy.context.active_object
        
        self.setRenderSetttings()
        
        meshes = getSelection(self.limit_application)
        selection = [m for m in bpy.context.scene.objects if m.select ]
        for s in selection:
            s.select = False
            
        for obj in meshes:
            self.generate(obj)
        bpy.context.scene.render.engine = engine
        
        for s in selection:
            s.select = True
        bpy.context.scene.objects.active = active
        return {'FINISHED'}

class setColour(modTool):
    bl_idname = 'mod_tools.set_color'
    bl_label = "Set Colour Alpha"
    bl_description = 'Set Colour Channel Alpha to Value.'
    bl_options = {"REGISTER", "PRESET", "UNDO"}

    fixed_value = bpy.props.FloatProperty(
            name = "Alpha Value",
            description = "Value to set the alpha of all vertices [0,1]",
            default = 0.0
        )
    
    @classmethod
    def poll(cls,context):
        if bpy.context.active_object:
            if bpy.context.active_object.type == "MESH":
                if len(bpy.context.active_object.data.vertex_colors):
                    return True                    
        return False
    
    def execute(self,context):
        for v in  bpy.context.active_object.data.vertex_colors.active.data:
            if len(v.color) < 4:
                v.color = list(v.color)+ [1.0]
            v.color[3] = max(min(self.fixed_value,1),0)
        return {'FINISHED'}

class cleanGroups(modTool):
    bl_idname = 'mod_tools.clean_weights'
    bl_label = "Remove Unweighted Groups"
    bl_description = 'Removes groups without vertices in them.'
    bl_options = {"REGISTER", "PRESET", "UNDO"}    
    limit_application = bpy.props.BoolProperty(
                        name = 'Limit to selected obejcts',
                        description = 'Limit operator actions to current selected objects',
                        default = True
                        )
    def execute(self,context):
        meshes = getSelection(self.limit_application)
        for obj in meshes:
            usedGroups = set()
            for v in obj.data.vertices:
                for vg in v.groups:
                    usedGroups.add(vg.group)            
            weights = list(obj.vertex_groups)
            for group in sorted(weights,key = lambda x: x.index,reverse=True):
                if group.index not in usedGroups:
                    obj.vertex_groups.remove(group)
        return {'FINISHED'}
        
        #col.operator("mod_tools.clean_weights", icon='GROUP_VERTEX', text="Remove Unweighted Groups")
        
class limitWeights(modTool):
    bl_idname = 'mod_tools.limit_normalize'
    bl_label = "Limit Weights to Label"
    bl_description = 'Limit weights to the corresponding blocklabel.'
    bl_options = {"REGISTER", "PRESET", "UNDO"}    
    limit_application = bpy.props.BoolProperty(
                        name = 'Limit to selected obejcts',
                        description = 'Limit operator actions to current selected objects',
                        default = True
                        )
    explicit_4th = bpy.props.BoolProperty(
                        name = 'Allow Implicit Weight',
                        description = 'Allow the implicit weight (otherwise limits to label -1)',
                        default = True
                        )
   
    def execute(self,context):
        meshes = getSelection(self.limit_application)
        for obj in meshes:
            if "blockLabel" not in obj.data:
                continue
            label = obj.data["blockLabel"]
            self.determineLabelOp(label,obj)           
        return {'FINISHED'}     
        #col.operator("mod_tools.limit_normalize", icon='GROUP_VERTEX', text="Limit Weights to Label")
        
    def determineLabelOp(self,label,mesh):
        if "wt" not in label:
            return self.removeWeights(mesh,0)
        if "4wt" in label:
            return self.limitWeights(mesh,4)
        if "8wt" in label:
            return self.limitWeights(mesh,8)
        
    def limitWeights(self,mesh,count):
        old_active = bpy.context.scene.objects.active
        oldmode = mesh.mode
        bpy.context.scene.objects.active = mesh
        bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
        
        lim = count - (1*(not self.explicit_4th))
        bpy.ops.object.vertex_group_limit_total(limit = max(lim,0))
        bpy.ops.object.vertex_group_normalize_all(lock_active = False)
        
        bpy.ops.object.mode_set(mode=oldmode)
        bpy.context.scene.objects.active = old_active

def walk_island(vert):
    ''' walk all un-tagged linked verts '''    
    vert.tag = True
    yield(vert)
    linked_verts = [e.other_vert(vert) for e in vert.link_edges
            if not e.other_vert(vert).tag]
    for v in linked_verts:
        if v.tag:
            continue
        yield from walk_island(v)

def get_islands(ob):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    verts=bm.verts
    def tag(verts, switch):
        for v in verts:
            v.tag = switch
    tag(bm.verts, True)
    tag(verts, False)
    ret = {"islands" : []}
    verts = set(verts)
    while verts:
        v = verts.pop()
        verts.add(v)
        island = set(walk_island(v))
        ret["islands"].append(list(map(lambda vert: vert.index,island)))
        tag(island, False) # remove tag = True
        verts -= island
    return ret["islands"]

class weightDiscretization(bpy.types.Operator):
    """Add a new item to the list."""
    bl_idname = "mod_tools.componentwise_discretization"
    bl_label = 'Average Weight per Island'
    bl_description = "Discretize Weight Group per Selected Meshpart on Selected Mesh"
    bl_options = {"REGISTER", "PRESET", "UNDO"}   
    def execute(self, context):
        ob = context.active_object
        group = ob.vertex_groups.active_index        
        components = [island for island in get_islands(ob)]
        for component in components:
            weightSum = 0
            for vert in component:
                try:
                    weightSum += ob.vertex_groups[group].weight(vert)
                except:
                    pass
            weightAvg = weightSum / len(component)
            ob.vertex_groups[group].add(list(component), weightAvg, 'REPLACE')
        return{'FINISHED'}

class nukeWeights(modTool):
    bl_idname = 'mod_tools.nuke_weights'
    bl_label = "Remove all Vertex Groups"
    bl_description = 'Remove all Vertex Groups.'
    bl_options = {"REGISTER", "PRESET", "UNDO"}      
    limit_application = bpy.props.BoolProperty(
                        name = 'Limit to selected obejcts',
                        description = 'Limit operator actions to current selected objects',
                        default = True
                        )
    def execute(self,context):
        meshes = getSelection(self.limit_application)
        for obj in meshes:
            weights = list(obj.vertex_groups)
            for w in weights:
                obj.vertex_groups.remove(w)
        return {"FINISHED"}

        #col.operator("mod_tools.nuke_weights", icon='GROUP_VERTEX', text="Delete Weights")

def triangulateObject(obj):
    me = obj.data
    # Get a BMesh representation
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method=0, ngon_method=0)
    # Finish up, write the bmesh back to the mesh
    bm.to_mesh(me)
    bm.free()     
    
class massTriangulate(modTool):
    bl_idname = 'mod_tools.mass_triangulate'
    bl_label = "Triangulates all meshes"
    bl_description = 'Triangulates all meshes.'
    bl_options = {"REGISTER", "PRESET", "UNDO"}
    limit_application = bpy.props.BoolProperty(
                        name = 'Limit to selected obejcts',
                        description = 'Limit operator actions to current selected objects',
                        default = True
                        )
    def execute(self,context):
        meshes = getSelection(self.limit_application)
        old_active = bpy.context.scene.objects.active
        for obj in meshes:
            oldmode = obj.mode
            bpy.context.scene.objects.active = obj
            bpy.ops.object.mode_set(mode='OBJECT')
            triangulateObject(obj)
            bpy.ops.object.mode_set(mode = oldmode)
        bpy.context.scene.objects.active = old_active
        return {'FINISHED'}
        #col.operator("mod_tools.mass_triangulate", icon='GROUP_VERTEX', text="Triangulate")

def getArmature():
    arma = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"]
    if len(arma) != 1:
        raise ValueError("Can't find canonical armature for the transfer to work on. There are %d/1 targets."%len(arma))
    return arma[0]

def isEmptySkeleton(obj):
    return "Type" in obj and obj["Type"] == "MOD3_SkeletonRoot"

def isArmature(obj):
    return  obj.type == "ARMATURE"

def metaBuildEnum(checkFunc):
    def buildEnum(self,context):
        enumItems = []# [("None","None","None","",0)]
        for obj in bpy.context.scene.objects:
            try:
                if checkFunc(obj):
                    enumItems.append((obj.name,obj.name,""))#,"","",hash(obj.name)&0x7FFFFFFF))
            except:
                raise
        return list(reversed(enumItems))
    return buildEnum

emptyEnum = metaBuildEnum(isEmptySkeleton)
armatureEnum = metaBuildEnum(isArmature)
          
class transferOperator():
    
    def getObject(self,objectName):
        if objectName not in bpy.data.objects:
            return None
        return bpy.data.objects[objectName]
    
    def check(self,context):
        if self.getObject(self.emptySkeleton) is None:
            return False
        if self.getObject(self.armatureSkeleton) is None:
            return False
        return True
    
    #def draw(self,context):
    #    layout = self.layout
    #    layout.prop(bpy.context.scene.mod3toolbox_transfer_targets,"emptySkeleton")
    #    layout.prop(bpy.context.scene.mod3toolbox_transfer_targets,"armatureSkeleton")       
    
    def getArmature(self,context):
        return self.getObject(self.armatureSkeleton)
    
    def recursiveList(self,empty):
        deepChildren = [empty]
        for e in empty.children:
            deepChildren += self.recursiveList(e)
        return deepChildren
    
    def getEmptyHierarchy(self,context):        
        emptyRoot = self.getObject(self.emptySkeleton)
        ehierarchy = [e for e in self.recursiveList(emptyRoot) if e.type == "EMPTY" and "boneFunction" in e]
        return ehierarchy
    
    def generateEmptyMapFrom(self,context):
        fromEmpty = {}
        ehierarchy = self.getEmptyHierarchy(context)
        for ebone in ehierarchy:
            fromEmpty[ebone["boneFunction"]] = ebone
        return fromEmpty

class targetArmature(transferOperator,modTool):
    bl_idname = 'mod_tools.target_armature'
    bl_label = "Rename Groups to Armature Names"
    bl_description = "Renames every vertex group to it's Armature Target Name based on Current Bone Function ID."
    bl_options = {"REGISTER", "UNDO"}    
    emptySkeleton = bpy.props.EnumProperty(name = "Empty Hierarchy Skeleton", items = emptyEnum)
    armatureSkeleton = bpy.props.EnumProperty(name = "Armature Skeleton", items = armatureEnum)

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

class targetEmpties(transferOperator,modTool):
    bl_idname = 'mod_tools.target_weights'
    bl_label = "Rename Groups to Empty Names"
    bl_description = "Renames every vertex group to it's Empty Target Name based on Current Bone Function ID."
    bl_options = {"REGISTER", "UNDO"}    
    emptySkeleton = bpy.props.EnumProperty(name = "Empty Hierarchy Skeleton", items = metaBuildEnum(isEmptySkeleton))
    armatureSkeleton = bpy.props.EnumProperty(name = "Armature Skeleton", items = metaBuildEnum(isArmature))
    
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

class massWeight(modTool):
    bl_idname = 'mod_tools.mass_weight'
    bl_label = "Weights Selection to Group"
    bl_description = "Weights all objects in the selection to a single bone."
    bl_options = {"REGISTER", "PRESET", "UNDO"}  
    
    limit_application = bpy.props.BoolProperty(
                        name = 'Limit to selected obejcts',
                        description = 'Limit operator actions to current selected objects',
                        default = True
                        )
    vertex_group = bpy.props.StringProperty(
                        name = 'Group to Weight To',
                        description = 'The group that the targets will be weighted to.',
                        default = "Bone.000"
                        )

    def execute(self,context):
        meshes = getSelection(self.limit_application)
        for obj in meshes:
            weights = obj.vertex_groups
            group = weights.new(self.vertex_group)
            group.add([i for i in range(len(obj.data.vertices))],1.0,'REPLACE')
        return {"FINISHED"}
    
def cannonicalName(wgroup):
    weightCaptureGroup = r"(.*)\( *([^,]*) *, *([-+]?[0-9]+)(/[0-9]+)? *\)$"
    match = re.match(weightCaptureGroup,wgroup)
    if not match: return wgroup
    group = match.group
    weightName = group(1)+group(2)
    print("%s -> %s" %(wgroup, weightName))
    weightIndex = int(group(3))
    if weightIndex == -1:return None
    else: return weightName

class collapseWeights(modTool):
    bl_idname = 'mod_tools.collapse_weights'
    bl_label = "Collapses Split Groups and Removes Negative Weights"
    bl_description = "Adds up the weights belonging to the same bone and removes negative weights."
    bl_options = {"REGISTER", "PRESET", "UNDO"}  
    
    limit_application = bpy.props.BoolProperty(
                        name = 'Limit to selected obejcts',
                        description = 'Limit operator actions to current selected objects',
                        default = True
                        )
    clear = bpy.props.BoolProperty(
                        name = 'Delete Negative Weights',
                        description = 'Delete groups corresponding to negative groups.',
                        default = True
                        )
    def execute(self,context):
        active = bpy.context.active_object
        meshes = getSelection(self.limit_application)
        for mesh in meshes:
            deleteTag = []
            combiner = {}
            bpy.context.scene.objects.active = mesh
            mode = mesh.mode
            if mode != "OBJECT":
                bpy.ops.object.mode_set(mode = 'OBJECT')
            for group in mesh.vertex_groups:
                cname = cannonicalName(group.name)
                if cname is None:
                    if self.clear:
                        deleteTag.append(group)
                else:
                    #group.name = cname
                    if cname not in combiner:
                        combiner[cname] = []
                    combiner[cname].append(group.name)
            #print ([g.name for g in deleteTag])
            for name, groups in combiner.items():
                base = groups[0]
                for ix, group in enumerate(groups[1:]):
                    m = mesh.modifiers.new("Combinator %03d",type = "VERTEX_WEIGHT_MIX")
                    m.vertex_group_a = base
                    m.vertex_group_b = group
                    m.mix_mode = "ADD"
                    m.mix_set = "OR"
                    bpy.ops.object.modifier_apply(modifier = m.name)
                    deleteTag.append(mesh.vertex_groups[group])
                mesh.vertex_groups[base].name = name
            for d in deleteTag:
                mesh.vertex_groups.remove(d)
            if mode != "OBJECT":
                bpy.ops.object.mode_set(mode = mode)
        bpy.context.scene.objects.active = active
        return {"FINISHED"}
    
class cleanMaterials(modTool):
    bl_idname = 'mod_tools.clean_materials'
    bl_label = "Removes unused materials from the material list"
    bl_description = "Deletes all unassigned MRL3 materials from the header."
    bl_options = {"REGISTER", "PRESET", "UNDO"}  

    def execute(self,context):
        bpy.context.scene["materialCount"] = 0
        i = 0
        while("MaterialName%d"%i in bpy.context.scene):
            del bpy.context.scene["MaterialName%d"%i]
            i+=1
        return {"FINISHED"}
    
class cleanUVs(modTool):
    bl_idname = 'mod_tools.clean_uvs'
    bl_label = "Removes secondary and tertiary uv maps"
    bl_description = "Deletes all extraneous uv maps."
    bl_options = {"REGISTER", "PRESET", "UNDO"}  
    
    limit_application = bpy.props.BoolProperty(
                        name = 'Limit to selected obejcts',
                        description = 'Limit operator actions to current selected objects',
                        default = True
                        )
    def execute(self,context):
        meshes = getSelection(self.limit_application)
        for mesh in meshes:
            uv_textures = mesh.uv_textures
            for ix,tex in reversed(list(enumerate(uv_textures))):
                if ix != 0:
                    uv_textures.remove(uv_textures[ix])
        return {"FINISHED"}

