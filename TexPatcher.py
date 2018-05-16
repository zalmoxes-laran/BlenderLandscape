import bpy
import os
from .functions import *

class ToolsPanel1400(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "BL"
    bl_label = "Texture merger (Cycles)"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        obj = context.object
        scene = context.scene
        row = layout.row()
        if bpy.context.scene.render.engine != 'CYCLES':
            row.label(text="Please, activate cycles engine !")
        else:
            row = layout.row()
            self.layout.operator("texture.merger", icon="FULLSCREEN_EXIT", text='Texture Patcher')
        
class OBJECT_OT_texmerger(bpy.types.Operator):
    """Texture merger"""
    bl_idname = "texture.merger"
    bl_label = "Texture Merger"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_ob = bpy.context.selected_objects
        active_ob = bpy.context.scene.objects.active
        for matslot in active_ob.material_slots:
            mat = matslot.material
            mat.use_nodes = True
            for mat in active_ob.mat:
                source_paint_node = node_retriever(mat, "source_paint_node")
                if source_paint_node != None:
                    nodes.remove(source_paint_node)
                create_new_tex_set(mat, type)
            
#        aggiungere source paint slots
#        abiliater painting
#        set-up paint
#        PAINT
#        SAVE paint
        pass
        return {'FINISHED'}