import os
import bpy

# svuotare il file blend da ogni risorsa

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=True)

# registro la posizione del file .blend (con verifica) 
path_to_obj_dir = os.path.dirname(bpy.data.filepath)
if not path_to_obj_dir:
    raise Exception("Il file Blender non è stato salvato, prima salvalo per la miseria !")

# metodi alternativi avendo un path preimpotato
#path_to_obj_dir = os.path.join('C:\\', 'Users', 'YOUR_NAME', 'Desktop', 'OBJS') #<-WINDOWS_OS
#path_to_obj_dir = bpy.path.abspath('//OBJ/')

# list of tutti i files in directory
file_list = sorted(os.listdir(path_to_obj_dir))

# get a list of files ending in 'obj'
obj_list = [item for item in file_list if item[-3:] == 'obj']

# loop through the strings in obj_list and add the files to the scene
for item in obj_list:
    path_to_file = os.path.join(path_to_obj_dir, item)
    bpy.ops.import_scene.obj(filepath = path_to_file, axis_forward='-Y', axis_up='Z')
    
basedir = os.path.dirname(bpy.data.filepath)

if not basedir:
    raise Exception("Il file Blender non è stato salvato, prima salvalo per la miseria !")

bpy.ops.object.select_all(action='SELECT')
for obj in bpy.context.selected_objects:
    baseobj = obj.name
bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})
for obj in bpy.context.selected_objects:
    obj.name = "LOD2_" + baseobj
    newobj = obj
for obj in bpy.context.selected_objects:
    lod2name = obj.name
#--------------------------------------------------------------------

for i in range(0,len(bpy.data.objects[lod2name].material_slots)):
    bpy.ops.object.material_slot_remove()
bpy.ops.object.editmode_toggle()
bpy.ops.uv.select_all(action='SELECT')
bpy.ops.mesh.remove_doubles()
bpy.ops.uv.pack_islands(margin=0.001)

# procedura di semplificazione mesh
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.mesh.select_non_manifold()
bpy.ops.object.vertex_group_add()
bpy.ops.object.vertex_group_assign()
bpy.ops.object.editmode_toggle()
bpy.data.objects[lod2name].modifiers.new("Decimate", type='DECIMATE')
bpy.context.object.modifiers["Decimate"].ratio = 0.1
bpy.context.object.modifiers["Decimate"].vertex_group = "Group"
bpy.context.object.modifiers["Decimate"].invert_vertex_group = True
bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Decimate")
# ora la mesh è semplificata
#------------------------------------------------------------------
bpy.ops.object.select_all(action='DESELECT')
oggetto = bpy.data.objects[lod2name]
oggetto.select = True

tempimage = bpy.data.images.new(name=lod2name, width=512, height=512, alpha=False)
tempimage.filepath_raw = "//"+lod2name+".jpg"
tempimage.file_format = 'JPEG'

for uv_face in oggetto.data.uv_textures.active.data:
    uv_face.image = tempimage

#--------------------------------------------------------------
bpy.context.scene.render.engine = 'BLENDER_RENDER'
bpy.context.scene.render.use_bake_selected_to_active = True
bpy.context.scene.render.bake_type = 'TEXTURE'

object = bpy.data.objects[baseobj]
object.select = True

bpy.context.scene.objects.active = bpy.data.objects[lod2name]
#--------------------------------------------------------------

bpy.ops.object.bake_image()
tempimage.save()

bpy.ops.object.select_all(action='DESELECT')
oggetto = bpy.data.objects[lod2name]
oggetto.select = True

#        basedir = os.path.dirname(bpy.data.filepath)
activename = bpy.path.clean_name(bpy.context.scene.objects.active.name)
fn = os.path.join(basedir, activename)
bpy.ops.export_scene.obj(filepath=fn + ".obj", use_selection=True, axis_forward='Y', axis_up='Z', path_mode='RELATIVE')

bpy.ops.object.move_to_layer(layers=(False, False, False, False, False, False, False, False, False, False, True, False, False, False, False, False, False, False, False, False))
bpy.context.scene.layers[10] = True
bpy.context.scene.layers[0] = False
bpy.ops.wm.save_mainfile()