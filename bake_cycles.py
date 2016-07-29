import bpy, os


bpy.context.scene.render.engine = 'CYCLES'

for obj in bpy.context.selected_objects:
    for matslot in obj.material_slots:
        mat = matslot.material
        o_image = mat.texture_slots[0].texture.image
# da commentare
        o_imagepath = mat.texture_slots[0].texture.image.filepath
        o_imagedir = os.path.dirname(o_imagepath)

#        basedir = os.path.dirname(bpy.data.filepath)

#        if not basedir:
#            raise Exception("Il file Blender non è stato salvato, prima salvalo per la miseria !")

#        activename = bpy.path.clean_name(timagepath)
#        fn = os.path.join(basedir, activename)
#        o_activename = bpy.path.clean_name(o_image)
        nodes = mat.node_tree.nodes
        node_tree = bpy.data.materials[mat.name].node_tree
        t_image_name = "cc_"+o_image.name
        t_image = bpy.data.images.new(name=t_image_name, width=2048, height=2048, alpha=False)
        
#        t_image.filepath_raw = '\\'+t_image_name+".png"
# da commentare
        fn = os.path.join(o_imagedir, t_image_name)
        t_image.filepath_raw = fn+".png"
        
        t_image.file_format = 'PNG'

        tteximg = nodes.new('ShaderNodeTexImage')
        tteximg.location = (-1100, -400)
        tteximg.image = t_image
        
        for currnode in nodes:
            currnode.select = False

#        node_tree.nodes.select_all(action='DESELECT')
        tteximg.select = True
        node_tree.nodes.active = tteximg

#active_object_name = bpy.context.scene.objects.active.name

    bpy.context.scene.cycles.samples = 1
    bpy.context.scene.cycles.max_bounces = 7
    bpy.context.scene.cycles.bake_type = 'DIFFUSE'
#    bpy.context.scene.use_pass_color = True
#    bpy.context.scene.use_pass_indirect = False
#    bpy.context.scene.use_pass_direct = False
#    bpy.context.scene.use_selected_to_active = False
    
    bpy.ops.object.bake(type='DIFFUSE', use_clear=True, margin=16)
    t_image.save()
    mat.texture_slots[0].texture.image = t_image