<p align="center">
  <img src="https://cdn.discordapp.com/attachments/679477019389591565/692639694206271518/ModTools.fw.png">
</p>

# A Collection of Editing Tools for MHW:IB Models.
A set of MHW tools for more convenient Mod3 Editing.

This is a blender plugin meant to compliment the MHW:IB Mod3 Importer Plugin for Blender which can be found here: https://github.com/AsteriskAmpersand/Mod3-MHW-Importer

This tools aren't meant to replace reading the documentation about the format or the mod3 exporter warnings and errors.

# Features
## Quick Property Transfers
Quickly copy the properties from the active object and paste them to the entire selection. Works for meshes, empties and more. 
 
Convenient when transferring properties to non-game meshes, or when creating new bones.

## Transfer Names to prepared Armatures
Rename vertex groups in your meshes instantly to match the names of bones on properly formatted blender armatures and back to the Mod3 Skeleton of Empties.

Compatible with Statyk's Player Body Armature.

## Rename Bones to their Function IDs
Rename bones to their function ID, simplifying copying mesh parts from one model to another. 

Also helps with identifying which bone functions are called by what mesh operations.

## Multiple UV, Seams and Sharp Edges Operators
Provides functions for identifying problematic vertices with multiple mappings to uv points. 

Automates the seam detection and edge splitting procedure and rips problematics remaining vertices, splits edges on edges set as sharp so sharpness is preserved on export.

With the option of preserving normals from before the split operators.

## Cleaning of Weights and Layers
Wipe unecessary and problematic layers en-masse. Weight entire sets of meshes to single bones, useful for weapons with simple weight schemes.

Mass limit and normalize mesh weights to accomodate their declared blocklabel.

Remove weight groups that have no vertex weighted to them.

Mass triangulate over the entire selection (or the entire scene) with a button.

# Credits
## Author
* **AsteriskAmpersand/\*&**

## Feature Requests
* **Lyraveil**
* **Statyk**
* **Nack**
