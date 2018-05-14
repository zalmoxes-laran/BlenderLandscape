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
        if obj.type not in ['MESH'] or obj == None:
#        if bpy.context.selected_objects == None or bpy.context.scene.objects.active == None:
            row = layout.row()
            row.label(text="Select a mesh to start")
        else:    
            row.label(text="Step by step procedure")
            row = layout.row()
            row.label(text="for selected object(s):")
            self.layout.operator("bi2cycles.material", icon="SMOOTH", text='Create cycles nodes')
            self.layout.operator("ccnode.material", icon="ASSET_MANAGER", text='Create correction node')
            self.layout.operator("apply.cc", icon="FILE_TICK", text='Create new texture set')
            row = layout.row()
            self.layout.operator("bake.cyclesdiffuse", icon="TPAINT_HLT", text='Bake CC to texture set')
            row = layout.row()
    #        row.label(text="NOW Bake Diffuse, color only", icon='TPAINT_HLT')
            self.layout.operator("savepaint.cam", icon="IMAGE_COL", text='Save new textures')
            self.layout.operator("remove.cc", icon="CANCEL", text='Use new textures (yoo-hoo!)')
            self.layout.operator("removeccnode.material", icon="CANCEL", text='remove cc node')   
            row = layout.row()     
            row.label(text="Switch engine")
            self.layout.operator("activatenode.material", icon="PMARKER_SEL", text='Activate cycles nodes')
            self.layout.operator("deactivatenode.material", icon="PMARKER", text='De-activate cycles nodes')

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

class OBJECT_OT_createcyclesmat(bpy.types.Operator):
    """Create cycles materials for selected objects"""
    bl_idname = "bi2cycles.material"
    bl_label = "Create cycles materials for selected object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        pass
        return {'FINISHED'}
    
    
class OBJECT_OT_material(bpy.types.Operator):
    """Create a color correction node for selected objects"""
    bl_idname = "ccnode.material"
    bl_label = "Create cycles materials for selected object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        bpy.context.scene.render.engine = 'CYCLES'
        
        create_texture_set()

#        for obj in bpy.context.selected_objects:

#            # create a group
#            active_object_name = bpy.context.scene.objects.active.name
#            test_group = bpy.data.node_groups.new(active_object_name, 'ShaderNodeTree')

#            # create group inputs
#            group_inputs = test_group.nodes.new('NodeGroupInput')
#            group_inputs.location = (-750,0)
#            test_group.inputs.new('NodeSocketColor','tex')

#            # create group outputs
#            group_outputs = test_group.nodes.new('NodeGroupOutput')
#            group_outputs.location = (300,0)
#            test_group.outputs.new('NodeSocketColor','cortex')

#            # create three math nodes in a group
#            bricon = test_group.nodes.new('ShaderNodeBrightContrast')
#            bricon.location = (-220, -100)
#            bricon.label = 'bricon'

#            sathue = test_group.nodes.new('ShaderNodeHueSaturation')
#            sathue.location = (0, -100)
#            sathue.label = 'sathue'

#            RGBcurve = test_group.nodes.new('ShaderNodeRGBCurve')
#            RGBcurve.location = (-500, -100)
#            RGBcurve.label = 'RGBcurve'

#            # link nodes together
#            test_group.links.new(sathue.inputs[4], bricon.outputs[0])
#            test_group.links.new(bricon.inputs[0], RGBcurve.outputs[0])

#            # link inputs
#            test_group.links.new(group_inputs.outputs['tex'], RGBcurve.inputs[1])

#            #link output
#            test_group.links.new(sathue.outputs[0], group_outputs.inputs['cortex'])

#            for matslot in obj.material_slots:
#                mat = matslot.material
#                image = mat.texture_slots[0].texture.image
#                mat.use_nodes = True
#                mat.node_tree.nodes.clear()
#                links = mat.node_tree.links
#                nodes = mat.node_tree.nodes
#                output = nodes.new('ShaderNodeOutputMaterial')
#                output.location = (0, 0)
#                mainNode = nodes.new('ShaderNodeBsdfDiffuse')
#                mainNode.location = (-400, -50)
#                teximg = nodes.new('ShaderNodeTexImage')
#                teximg.location = (-1100, -50)
#                teximg.image = image
#                colcor = nodes.new(type="ShaderNodeGroup")
#                colcor.node_tree = (bpy.data.node_groups[active_object_name])
#                colcor.location = (-800, -50)
#                links.new(teximg.outputs[0], colcor.inputs[0])
#                links.new(colcor.outputs[0], mainNode.inputs[0])
#                links.new(mainNode.outputs[0], output.inputs[0])
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


class OBJECT_OT_applycc(bpy.types.Operator):
    """Apply color correction to new texs"""
    bl_idname = "apply.cc"
    bl_label = "Create new texture set for corrected mats (cc_ + previous tex name)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        bpy.context.scene.render.engine = 'CYCLES'

        for obj in bpy.context.selected_objects:
            for matslot in obj.material_slots:
                mat = matslot.material
                create_new_tex_set(mat,"cc")

        return {'FINISHED'}


#-------------------------------------------------------------


class OBJECT_OT_bakecyclesdiffuse(bpy.types.Operator):
    """Color correction to new texture set"""
    bl_idname = "bake.cyclesdiffuse"
    bl_label = "Transfer new color correction to a new texture set"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        bpy.context.scene.render.engine = 'CYCLES'
        tot_time = 0
        ob_counter = 1
        tot_selected_ob = len(bpy.context.selected_objects)
        for ob in bpy.context.selected_objects:
            start_time = time.time()
            print('start baking "'+ob.name+'" (object '+str(ob_counter)+'/'+str(tot_selected_ob)+')')
            bpy.ops.object.select_all(action='DESELECT')
            ob.select = True
            bpy.context.scene.objects.active = ob
            bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'}, use_clear=True, save_mode='INTERNAL')
            tot_time += (time.time() - start_time)
            print("--- %s seconds ---" % (time.time() - start_time))
            ob_counter += 1
        print("--- JOB complete in %s seconds ---" % tot_time)

        return {'FINISHED'}

####-----------------------------------------------------------

class OBJECT_OT_removecc(bpy.types.Operator):
    """Remove color correction nodes"""
    bl_idname = "remove.cc"
    bl_label = "Use new textures in mats and detach color correction nodes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        bpy.context.scene.render.engine = 'CYCLES'

        for obj in bpy.context.selected_objects:
        #    for matslot in obj.material_slots:
        #        mat = matslot.material
        #        nodes = mat.node_tree.nodes
        #        cc_node = nodes.get(mat.name)
        #        bpy.ops.node.delete_reconnect(cc_node)
        #
            for matslot in obj.material_slots:
                mat = matslot.material
                nodes = mat.node_tree.nodes
                links = mat.node_tree.links
                for mat_node in mat.node_tree.nodes:
                    if mat_node.type == 'GROUP' and mat_node.node_tree.name == obj.name:
        #                print ("nodegroup"+mat_node.name+" in "+mat.name)
                        nodes.remove(mat_node)
                for mat_node in mat.node_tree.nodes:
                    if mat_node.type == 'TEX_IMAGE':
                        imagenode = mat_node
                    if mat_node.type == 'BSDF_DIFFUSE':
                        diffusenode = mat_node
                links.new(imagenode.outputs[0], diffusenode.inputs[0])

        return {'FINISHED'}

