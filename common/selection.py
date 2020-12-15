# -*- coding: utf-8 -*-
# #####BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# #####END GPL LICENSE BLOCK #####
#	"author": "Alfonso Serra",

import bpy

bpy.selection=[]

def select():
	#print(bpy.context.mode)
	if bpy.context.mode=="OBJECT":
		obj = bpy.context.object
		sel = len(bpy.context.selected_objects)
		
		if sel==0:
			bpy.selection=[]
		else:
			if sel==1:
				bpy.selection=[]
				bpy.selection.append(obj)
			elif sel>len(bpy.selection):
				for sobj in bpy.context.selected_objects:
					if (sobj in bpy.selection)==False:
						bpy.selection.append(sobj)
			
			elif sel<len(bpy.selection):
				for it in bpy.selection:
					if (it in bpy.context.selected_objects)==False:
						bpy.selection.remove(it)		
	#on edit mode doesnt work well
	
#executes selection by order at 3d view
class Selection(bpy.types.Header):
	bl_label = "Selection"
	bl_space_type = "VIEW_3D"
	
	def __init__(self):
		#print("hey")
		select()

	def draw(self, context):
		layout = self.layout
		row = layout.row()
		row.label("Sel: "+str(len(bpy.selection)))