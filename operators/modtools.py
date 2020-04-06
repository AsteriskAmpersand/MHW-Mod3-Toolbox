# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 21:26:53 2020

@author: AsteriskAmpersand
"""
import bpy
import bmesh
import re

class modTool(bpy.types.Operator):
    addon_key = __package__.split('.')[0]
    #addon = bpy.context.user_preferences.addons[addon_key]    
    def __init__(self):
        self.addon = bpy.context.user_preferences.addons[self.addon_key]

class copyProp(modTool):
    bl_idname = 'mod_tools.copy_prop'
    bl_label = "Copy Mesh Properties"
    bl_description = 'Copy the Custom Properties of the Active Mesh'
    bl_options = {"REGISTER", "PRESET", "UNDO"}        
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
    bl_options = {"REGISTER", "PRESET", "UNDO"}    
    
    @classmethod
    def poll(cls, context):
        return bpy.context.user_preferences.addons[cls.addon_key].preferences.data["properties_buffer"] != {} and len(bpy.context.selected_objects) > 0
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

class boneToID(modTool):
    bl_idname = 'mod_tools.bone_to_id'
    bl_label = "Rename Bones to Function"
    bl_description = 'Renames every bone to their Bone Function ID.'
    bl_options = {"REGISTER", "PRESET", "UNDO"}    

    def execute(self,context):
        renameTable = {}
        for bone in [o for o in bpy.context.scene.objects if o.type == "EMPTY" and "boneFunction" in o]:
            newname = "BoneFunction%03d"%bone["boneFunction"]
            renameTable[bone .name] = newname 
            bone.name = newname        
        for mesh in [o for o in bpy.context.scene.objects if o.type == "MESH"]:
            for group in mesh.vertex_groups:
                if group.name in renameTable:
                    group.name = renameTable[group.name]
        return {'FINISHED'}  
    
        #col.operator("mod_tools.bone_to_id", icon='COSNTRAINT_BONE', text="Rename Bones to ID")

        #col.prop(addon_props, 'only_selection', text = 'Limit to Selection')

def getSelection(onlySelection, selectionType = "MESH"):
    return [obj for obj in (bpy.context.selected_objects if onlySelection else bpy.context.scene.objects) 
            if obj.type == selectionType and not obj.hide and not obj.hide_select]
    
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
            for group in weights:
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
        
        bpy.ops.object.vertex_group_limit_total(limit = max(count-1,0))
        bpy.ops.object.vertex_group_normalize_all(lock_active = False)
        
        bpy.ops.object.mode_set(mode=oldmode)
        bpy.context.scene.objects.active = old_active
        
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

class targetArmature(modTool):
    bl_idname = 'mod_tools.target_armature'
    bl_label = "Rename Groups to Armature Names"
    bl_description = "Renames every vertex group to it's Armature Target Name based on Current Bone Function ID."
    bl_options = {"REGISTER", "PRESET", "UNDO"}    

    def execute(self,context):
        fromEmpty = {}
        remapTable = {}
        for ebone in [o for o in bpy.context.scene.objects if o.type == "EMPTY" and "boneFunction" in o]:
            fromEmpty[ebone["boneFunction"]] = ebone
        armature = getArmature()
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

class targetEmpties(modTool):
    bl_idname = 'mod_tools.target_weights'
    bl_label = "Rename Groups to Empty Names"
    bl_description = "Renames every vertex group to it's Empty Target Name based on Current Bone Function ID."
    bl_options = {"REGISTER", "PRESET", "UNDO"}    

    def execute(self,context):
        fromArmature = {}
        remapTable = {}
        armature = getArmature()
        for bone in armature.pose.bones:
            if "boneFunction" in bone:
                fromArmature[bone["boneFunction"]]=bone
        for ebone in [o for o in bpy.context.scene.objects if o.type == "EMPTY" and "boneFunction" in o]:
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
    bl_description = "Renames every vertex group to it's Empty Target Name based on Current Bone Function ID."
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
        deleteTag = []
        combiner = {}
        active = bpy.context.active_object
        meshes = getSelection(self.limit_application)
        for mesh in meshes:
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
            print ([g.name for g in deleteTag])
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
    