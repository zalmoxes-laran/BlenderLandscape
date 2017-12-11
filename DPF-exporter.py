bl_info = {
    "name": "DPF exporter",
    "author": "E. Demetrescu",
    "version": (0,1),
    "blender": (2, 7, 9),
    "location": "Tool Shelf panel",
    "description": "Exporter for DPF framework by Fanini, D'Annibale",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Tools"}


import bpy
import os
import numpy as np

class ToolsPanel4(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "BL"
    bl_label = "360 content creation"
     
    def draw(self, context):
        layout = self.layout
        obj = context.object
        scene = context.scene
        cam_ob = scene.camera
        row = layout.row()
        row.label(text="Active Cam: " + cam_ob.name)        
        self.layout.operator("360dpf.setupcamera", icon="WIRE", text='Set as 360 cam')
        row = layout.row()
        self.layout.operator("360dpf.renderdepth", icon="PREVIEW_RANGE", text='Export for DPF')
        row = layout.row()
        row.label(text="Resulting file: " + cam_ob.name + ".txt")        
        row = layout.row()

class OBJECT_OT_SETUPCAMERA(bpy.types.Operator):
    """set up a 360 camera"""
    bl_idname = "360dpf.setupcamera"
    bl_label = "Set selected as 360 camera"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        scene = context.scene
        scene.render.resolution_x = 8192
        scene.render.resolution_y = 4096        
#        bpy.context.scene.render.engine = 'CYCLES'
        selection = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')
        for obj in selection:
            obj.select = True
            obj.data.type = 'PANO'
            obj.rotation_euler[0] = 1.570796
#            obj.data.sensor_fit = 'HORIZONTAL'
#            obj.data.sensor_width = 35.8
#            obj.data.sensor_height = 23.9
        return {'FINISHED'}

class OBJECT_OT_material(bpy.types.Operator):
    """Create cycles materials for selected object"""
    bl_idname = "bi2cycles.material"
    bl_label = "Create cycles materials for selected object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
    
        bpy.context.scene.render.engine = 'CYCLES'

        for obj in bpy.context.selected_objects:

            # create a group
            active_object_name = bpy.context.scene.objects.active.name
            test_group = bpy.data.node_groups.new(active_object_name, 'ShaderNodeTree')
            
            # create group inputs
            group_inputs = test_group.nodes.new('NodeGroupInput')
            group_inputs.location = (-750,0)
            test_group.inputs.new('NodeSocketColor','tex')

            # create group outputs
            group_outputs = test_group.nodes.new('NodeGroupOutput')
            group_outputs.location = (300,0)
            test_group.outputs.new('NodeSocketColor','cortex')

            # create three math nodes in a group
            bricon = test_group.nodes.new('ShaderNodeBrightContrast')
            bricon.location = (-220, -100)
            bricon.label = 'bricon'

            sathue = test_group.nodes.new('ShaderNodeHueSaturation')
            sathue.location = (0, -100)
            sathue.label = 'sathue'
    
            RGBcurve = test_group.nodes.new('ShaderNodeRGBCurve')
            RGBcurve.location = (-500, -100)
            RGBcurve.label = 'RGBcurve'

            # link nodes together
            test_group.links.new(sathue.inputs[4], bricon.outputs[0])
            test_group.links.new(bricon.inputs[0], RGBcurve.outputs[0])

            # link inputs
            test_group.links.new(group_inputs.outputs['tex'], RGBcurve.inputs[1])
            
            #link output
            test_group.links.new(sathue.outputs[0], group_outputs.inputs['cortex'])
            
            for matslot in obj.material_slots:
                mat = matslot.material
                image = mat.texture_slots[0].texture.image
                mat.use_nodes = True
                mat.node_tree.nodes.clear()
                links = mat.node_tree.links
                nodes = mat.node_tree.nodes
                output = nodes.new('ShaderNodeOutputMaterial')
                output.location = (0, 0)
                mainNode = nodes.new('ShaderNodeBsdfDiffuse')
                mainNode.location = (-400, -50)
                teximg = nodes.new('ShaderNodeTexImage')
                teximg.location = (-1100, -50)
                teximg.image = image
                colcor = nodes.new(type="ShaderNodeGroup")
                colcor.node_tree = (bpy.data.node_groups[active_object_name])
                colcor.location = (-800, -50)
                links.new(teximg.outputs[0], colcor.inputs[0])
                links.new(colcor.outputs[0], mainNode.inputs[0])
                links.new(mainNode.outputs[0], output.inputs[0])
        return {'FINISHED'}

class OBJECT_OT_360CAMERA(bpy.types.Operator):
    """Set up a 360 camera"""
    bl_idname = "360dpf.setup"
    bl_label = "Set up camera"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
    
#        bpy.context.scene.render.engine = 'CYCLES'
#        for obj in bpy.context.selected_objects:
#            for matslot in obj.material_slots:
#                mat = matslot.material
#                mat.use_nodes = True

        bpy.context.scene.render.use_compositing = True
        bpy.context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree
        links = tree.links

        for n in tree.nodes:
            tree.nodes.remove(n)
        rl = tree.nodes.new('CompositorNodeRLayers')

        vl = tree.nodes.new('CompositorNodeViewer')
        vl.use_alpha = True
        links.new(rl.outputs[0], vl.inputs[0])  # link Renger Image to Viewer Image
        links.new(rl.outputs[2], vl.inputs[1])  # link Render Z to Viewer Alpha

        #render
        bpy.context.scene.render.resolution_percentage = 25 #make sure scene height and width are ok (edit)
        bpy.ops.render.render()
        bpy.context.scene.render.resolution_percentage = 100 #make sure scene height and width are ok (edit)



        #get the pixels and put them into a numpy array
        pixels = np.array(bpy.data.images['Viewer Node'].pixels)
        print(len(pixels))

        width = bpy.context.scene.render.resolution_x 
        height = bpy.context.scene.render.resolution_y

        #reshaping into image array 4 channel (rgbz)
        image = pixels.reshape(height,width,4)

        #depth analysis...
        z = image[:,:,3]
        zf = z[z<1000] #

        print(np.min(zf),np.max(zf))

        return {'FINISHED'}



class OBJECT_OT_360DPFRENDERDEPTH(bpy.types.Operator):
    """Activate node materials for selected object"""
    bl_idname = "360dpf.renderdepth"
    bl_label = "Set up camera and render"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
    
#        bpy.context.scene.render.engine = 'CYCLES'
#        for obj in bpy.context.selected_objects:
#            for matslot in obj.material_slots:
#                mat = matslot.material
#                mat.use_nodes = True

# this part from https://blender.stackexchange.com/questions/35191/how-to-get-color-and-z-depth-from-viewer-node

        bpy.context.scene.render.use_compositing = True
        bpy.context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree
        links = tree.links

        for n in tree.nodes:
            tree.nodes.remove(n)
        rl = tree.nodes.new('CompositorNodeRLayers')

        vl = tree.nodes.new('CompositorNodeViewer')
        vl.use_alpha = True
        links.new(rl.outputs[0], vl.inputs[0])  # link Renger Image to Viewer Image
        links.new(rl.outputs[2], vl.inputs[1])  # link Render Z to Viewer Alpha

        #render
        bpy.context.scene.render.resolution_percentage = 25 #make sure scene height and width are ok (edit)
        bpy.ops.render.render()
        bpy.context.scene.render.resolution_percentage = 100 #make sure scene height and width are ok (edit)



        #get the pixels and put them into a numpy array
        pixels = np.array(bpy.data.images['Viewer Node'].pixels)
        print(len(pixels))

        width = bpy.context.scene.render.resolution_x 
        height = bpy.context.scene.render.resolution_y

        #reshaping into image array 4 channel (rgbz)
        image = pixels.reshape(height,width,4)

        #depth analysis...
        z = image[:,:,3]
        zf = z[z<1000] #

        print(np.min(zf),np.max(zf))

        return {'FINISHED'}

def register():
    bpy.utils.register_class(ToolsPanel4)
    bpy.utils.register_class(OBJECT_OT_360DPFRENDERDEPTH) 
    bpy.utils.register_class(OBJECT_OT_SETUPCAMERA) 
    
def unregister():
    bpy.utils.unregister_class(ToolsPanel4)
    bpy.utils.unregister_class(OBJECT_OT_360DPFRENDERDEPTH)
    bpy.utils.unregister_class(OBJECT_OT_SETUPCAMERA)
            
if __name__ == "__main__":
    register()