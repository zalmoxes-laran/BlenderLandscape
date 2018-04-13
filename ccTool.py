import bpy

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

        row.label(text="Step by step procedure")
        row = layout.row()
        row.label(text="for selected object(s):")

        self.layout.operator("bi2cycles.material", icon="SMOOTH", text='Create correction nodes')
        self.layout.operator("apply.cc", icon="FILE_TICK", text='Create new texture set')
        row = layout.row()
        self.layout.operator("bake.cyclesdiffuse", icon="TPAINT_HLT", text='Bake CC to texture set')
        row = layout.row()
#        row.label(text="NOW Bake Diffuse, color only", icon='TPAINT_HLT')
        self.layout.operator("savepaint.cam", icon="IMAGE_COL", text='Save new textures')
        self.layout.operator("remove.cc", icon="CANCEL", text='Use new textures (yoo-hoo!)')
        row = layout.row()
        row.label(text="Switch engine")
        self.layout.operator("activatenode.material", icon="PMARKER_SEL", text='Activate cycles nodes')
        self.layout.operator("deactivatenode.material", icon="PMARKER", text='De-activate cycles nodes')

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

def substring_after(s, delim):
    return s.partition(delim)[2]

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
                o_image = mat.texture_slots[0].texture.image
                x_image = mat.texture_slots[0].texture.image.size[0]
                y_image = mat.texture_slots[0].texture.image.size[1]
                o_imagepath = mat.texture_slots[0].texture.image.filepath
                o_imagepath_abs = bpy.path.abspath(o_imagepath)
                o_imagedir, o_filename = os.path.split(o_imagepath_abs)
                o_filename_no_ext = os.path.splitext(o_filename)[0]
#				o_imagedir_rel = bpy.path.relpath(o_imagedir)
                # new image
                nodes = mat.node_tree.nodes
                node_tree = bpy.data.materials[mat.name].node_tree
                if o_filename_no_ext.startswith("cc_"):
                    print(substring_after(o_filename, "cc_"))
                    t_image_name = "cc_2_"+o_filename_no_ext
                else:
                    t_image_name = "cc_"+o_filename_no_ext
                    print(substring_after(o_filename, "cc_"))
                t_image = bpy.data.images.new(name=t_image_name, width=x_image, height=y_image, alpha=False)
                # set path to new image
                fn = os.path.join(o_imagedir, t_image_name)
                t_image.filepath_raw = fn+".png"
                t_image.file_format = 'PNG'

                tteximg = nodes.new('ShaderNodeTexImage')
                tteximg.location = (-1100, -400)
                tteximg.image = t_image

                for currnode in nodes:
                    currnode.select = False

                # node_tree.nodes.select_all(action='DESELECT')
                tteximg.select = True
                node_tree.nodes.active = tteximg
                mat.texture_slots[0].texture.image = t_image

        #active_object_name = bpy.context.scene.objects.active.name

#            bpy.context.scene.cycles.samples = 1
#            bpy.context.scene.cycles.max_bounces = 7
#            bpy.context.scene.cycles.bake_type = 'DIFFUSE'
#            #    bpy.context.scene.use_pass_color = True
#            #    bpy.context.scene.use_pass_indirect = False
#            #    bpy.context.scene.use_pass_direct = False
#            #    bpy.context.scene.use_selected_to_active = False

#            bpy.ops.object.bake(type='DIFFUSE', use_clear=True, margin=16)
#            bpy.ops.image.save_dirty()

#
#            remove.cc()
#            for matslot in obj.material_slots:
#                mat = matslot.material
#                t_image = mat.texture_slots[0].texture.image
#                t_image.save()
#
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

