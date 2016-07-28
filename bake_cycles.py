import bpy


basedir = os.path.dirname(bpy.data.filepath)

if not basedir:
    raise Exception("Il file Blender non è stato salvato, prima salvalo per la miseria !")

selection = bpy.context.selected_objects
bpy.ops.object.select_all(action='DESELECT')
activename = bpy.path.clean_name(bpy.context.scene.objects.active.name)
fn = os.path.join(basedir, activename)

tempimage = bpy.data.images.new(name=lod2name, width=2048, height=2048, alpha=False)
tempimage.filepath_raw = "//"+lod2name+".png"
tempimage.file_format = 'PNG'


bpy.context.scene.cycles.samples = 1
bpy.context.scene.cycles.max_bounces = 4
bpy.context.scene.cycles.bake_type = 'DIFFUSE'
bpy.context.scene.use_pass_color = True
bpy.context.scene.use_pass_indirect = False
bpy.context.scene.use_pass_direct = False
bpy.context.scene.use_selected_to_active = False


bpy.ops.object.bake_image()
tempimage.save()