import bpy
import os
import time
from .functions import *


def select_a_mesh(layout):
    row = layout.row()
    row.label(text="Select a mesh to start")


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
        #        row.label(text="NOW Bake Diffuse, color only", icon='TPAINT_HLT')
                self.layout.operator("savepaint.cam", icon="IMAGE_COL", text='Save new textures')
                self.layout.operator("applynewtexset.material", icon="AUTOMERGE_ON", text='Use new tex set')
                self.layout.operator("applyoritexset.material", icon="RECOVER_LAST", text='Use original tex set')
                
                self.layout.operator("removeccnode.material", icon="CANCEL", text='remove cc node')
                self.layout.operator("removeorimage.material", icon="CANCEL", text='remove ori image')
                row = layout.row()     
                row.label(text="Switch engine")
                self.layout.operator("activatenode.material", icon="PMARKER_SEL", text='Activate cycles nodes')
                self.layout.operator("deactivatenode.material", icon="PMARKER", text='De-activate cycles nodes')
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
                remove_cc_node(mat)
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

#________________________________________________________

class OBJECT_OT_deactivatematerial(bpy.types.Operator):
    """De-activate node  materials for selected object"""
    bl_idname = "deactivatenode.material"
    bl_label = "De-activate cycles node materials for selected object and switch to BI"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        bpy.context.scene.render.engine = 'BLENDER_RENDER'
        for obj in bpy.context.selected_objects:
            for matslot in obj.material_slots:
                mat = matslot.material
                mat.use_nodes = False

        return {'FINISHED'}
    
#-------------------------------------------------------------

class OBJECT_OT_activatematerial(bpy.types.Operator):
    """Activate node materials for selected object"""
    bl_idname = "activatenode.material"
    bl_label = "Activate cycles node materials for selected object and switch to cycles"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        bpy.context.scene.render.engine = 'CYCLES'
        for obj in bpy.context.selected_objects:
            for matslot in obj.material_slots:
                mat = matslot.material
                mat.use_nodes = True

        return {'FINISHED'}
    
#-------------------------------------------------------------

class OBJECT_OT_createnewset(bpy.types.Operator):
    """Apply color correction to new texs"""
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

def bake_tex_set(type):
    scene = context.scene
    bpy.context.scene.render.engine = 'CYCLES'
    tot_time = 0
    ob_counter = 1
    scene.cycles.sample = 1
    scene.cycles.max_bounces = 1
    start_time = time.time()
    if type == "source":
        if len(bpy.context.selected_objects) > 1:
            bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'}, use_selected_to_active=True, use_clear=True, save_mode='INTERNAL')
        else:
            raise Exception("Select two ")
        tot_time += (time.time() - start_time)
    if type == "cc":
        tot_selected_ob = len(bpy.context.selected_objects)
        for ob in bpy.context.selected_objects:
            print('start baking "'+ob.name+'" (object '+str(ob_counter)+'/'+str(tot_selected_ob)+')')
            bpy.ops.object.select_all(action='DESELECT')
            ob.select = True
            bpy.context.scene.objects.active = ob
            bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'}, use_selected_to_active=False, use_clear=True, save_mode='INTERNAL')
            tot_time += (time.time() - start_time)
            print("--- %s seconds ---" % (time.time() - start_time))
            ob_counter += 1
    print("--- JOB complete in %s seconds ---" % tot_time)
    

class OBJECT_OT_bakecyclesdiffuse(bpy.types.Operator):
    """Color correction to new texture set"""
    bl_idname = "bake.cyclesdiffuse"
    bl_label = "Transfer new color correction to a new texture set"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bake_tex_set("cc")
        
        return {'FINISHED'}

####-----------------------------------------------------------


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

class OBJECT_OT_applynewtexset(bpy.types.Operator):
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