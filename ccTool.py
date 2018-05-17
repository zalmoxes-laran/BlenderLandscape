import bpy
import os
import time
from .functions import *


class ToolsPanel9(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "BL"
    bl_label = "Color Correction tool (cycles)"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        obj = context.object
        scene = context.scene
        row = layout.row()
        if bpy.context.scene.render.engine != 'CYCLES':
            row.label(text="Please, activate cycles engine !")
        else:
            if scene.objects.active:
                if obj.type not in ['MESH']:
                    select_a_mesh(layout)
                else:    
                    row.label(text="Step by step procedure")
                    row = layout.row()
                    row.label(text="for selected object(s):")
                    self.layout.operator("bi2cycles.material", icon="SMOOTH", text='Create cycles nodes')
                    self.layout.operator("create.ccnode", icon="ASSET_MANAGER", text='Create correction node')
                    self.layout.operator("create.newset", icon="FILE_TICK", text='Create new texture set')
                    row = layout.row()
                    self.layout.operator("bake.cyclesdiffuse", icon="TPAINT_HLT", text='Bake CC to texture set')
                    row = layout.row()
                    self.layout.operator("savepaint.cam", icon="IMAGE_COL", text='Save new textures')
                    self.layout.operator("applynewtexset.material", icon="AUTOMERGE_ON", text='Use new tex set')
                    self.layout.operator("applyoritexset.material", icon="RECOVER_LAST", text='Use original tex set')
                    
                    self.layout.operator("removeccnode.material", icon="CANCEL", text='remove cc node')
                    self.layout.operator("removeorimage.material", icon="CANCEL", text='remove ori image')
                    row = layout.row() 
            else:
                select_a_mesh(layout)


class OBJECT_OT_removeccnode(bpy.types.Operator):
    """Remove cc node for selected objects"""
    bl_idname = "removeccnode.material"
    bl_label = "Remove  cycles cc node for selected object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            for matslot in obj.material_slots:
                mat = matslot.material
                remove_node(mat, "cc_node")
        return {'FINISHED'}
    
class OBJECT_OT_removeorimage(bpy.types.Operator):
    """Remove oiginal image for selected objects"""
    bl_idname = "removeorimage.material"
    bl_label = "Remove oiginal image for selected objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            for matslot in obj.material_slots:
                mat = matslot.material
                remove_ori_image(mat)
        return {'FINISHED'}

class OBJECT_OT_createcyclesmat(bpy.types.Operator):
    """Create cycles materials for selected objects"""
    bl_idname = "bi2cycles.material"
    bl_label = "Create cycles materials for selected object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.context.scene.render.engine = 'CYCLES'
        bi2cycles()
        return {'FINISHED'}
    
class OBJECT_OT_createccnode(bpy.types.Operator):
    """Create a color correction node for selected objects"""
    bl_idname = "create.ccnode"
    bl_label = "Create cycles materials for selected object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        bpy.context.scene.render.engine = 'CYCLES'
        create_cc_node()

        return {'FINISHED'}

#-------------------------------------------------------------

class OBJECT_OT_createnewset(bpy.types.Operator):
    """Create new texture set for corrected mats"""
    bl_idname = "create.newset"
    bl_label = "Create new texture set for corrected mats (cc_ + previous tex name)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.context.scene.render.engine = 'CYCLES'
        for obj in bpy.context.selected_objects:
            for matslot in obj.material_slots:
                mat = matslot.material
                create_new_tex_set(mat,"cc_image")
        return {'FINISHED'}

#-------------------------------------------------------------


class OBJECT_OT_bakecyclesdiffuse(bpy.types.Operator):
    """Color correction to new texture set"""
    bl_idname = "bake.cyclesdiffuse"
    bl_label = "Transfer new color correction to a new texture set"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bake_tex_set("cc")
        
        return {'FINISHED'}

####-----------------------------------------------------------


class OBJECT_OT_applyoritexset(bpy.types.Operator):
    """Use original textures in mats"""
    bl_idname = "applyoritexset.material"
    bl_label = "Use original textures in mats"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        bpy.context.scene.render.engine = 'CYCLES'

        for obj in bpy.context.selected_objects:
            for matslot in obj.material_slots:
                mat = matslot.material
                set_texset(mat, "original")
                
        return {'FINISHED'}
    
class OBJECT_OT_applynewtexset(bpy.types.Operator):
    """Use new textures in mats"""
    bl_idname = "applynewtexset.material"
    bl_label = "Use new textures in mats"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        bpy.context.scene.render.engine = 'CYCLES'

        for obj in bpy.context.selected_objects:
            for matslot in obj.material_slots:
                mat = matslot.material
                set_texset(mat, "cc_image")
                
        return {'FINISHED'}