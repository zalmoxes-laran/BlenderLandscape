import bpy
import bmesh
import operator
import time
import math
from mathutils import Vector

def get_selected_object_faces():
	object_faces_indexies = {}

	previous_mode = bpy.context.object.mode

	if bpy.context.object.mode == 'EDIT':
		# Only selected Mesh faces
		obj = bpy.context.active_object
		if obj.type == 'MESH' and obj.data.uv_layers:
			bm = bmesh.from_edit_mesh(obj.data)
			bm.faces.ensure_lookup_table()
			object_faces_indexies[obj] = [face.index for face in bm.faces if face.select]
	else:
		# Selected objects with all faces each
		selected_objects = [obj for obj in bpy.context.selected_objects]
		for obj in selected_objects:
			if obj.type == 'MESH' and obj.data.uv_layers:
				bpy.ops.object.mode_set(mode='OBJECT')
				bpy.ops.object.select_all(action='DESELECT')
				bpy.context.scene.objects.active = obj
				obj.select = True

				bpy.ops.object.mode_set(mode='EDIT')
				bm = bmesh.from_edit_mesh(obj.data)
				bm.faces.ensure_lookup_table()
				object_faces_indexies[obj] = [face.index for face in bm.faces]

	bpy.ops.object.mode_set(mode=previous_mode)

	return object_faces_indexies

def get_object_texture_image(obj):

	previous_mode = bpy.context.active_object.mode
	bpy.ops.object.mode_set(mode='OBJECT')

	if bpy.context.scene.render.engine == 'BLENDER_RENDER':
		# Search in UV editor background image
		if len(obj.data.uv_textures) > 0:
			if len(obj.data.uv_textures[0].data) > 0:
				if obj.data.uv_textures[0].data[0].image:
					return obj.data.uv_textures[0].data[0].image
	else:
		# Search in material & texture slots
		for slot_mat in obj.material_slots:

			if slot_mat.material:

				# Check for traditional texture slots in material
				for slot_tex in slot_mat.material.texture_slots:
					if slot_tex and slot_tex.texture and hasattr(slot_tex.texture , 'image'):
						return slot_tex.texture.image

				# Check if material uses Nodes
				if hasattr(slot_mat.material , 'node_tree'):
					if slot_mat.material.node_tree:
						for node in slot_mat.material.node_tree.nodes:
							if type(node) is bpy.types.ShaderNodeTexImage:
								if node.image:
									return node.image

	return None

def image_resize(image, size_x, size_y):
	if image and image.source == 'FILE' or image.source == 'GENERATED':
		image.generated_width = int(size_x)
		image.generated_height = int(size_y)
		image.scale( int(size_x), int(size_y) )
	
	

def checker_images_cleanup():
	# Clean up unused images
	for image in bpy.data.images:
		if image and image_material_prefix in image.name:
			# Remove unused images
			if not image.users:
				image.user_clear()
				bpy.data.images.remove(image)
				return

			# Check if name missmatches size
			name = get_checker_name(image.generated_type , image.size[0], image.size[1])
			if image.name != name:
				# In cycles find related material as well
				if image.name in bpy.data.materials:
					bpy.data.materials[image.name].name = name
				image.name = name

	for material in bpy.data.materials:
		if material and image_material_prefix in material.name:
			# Remove unused images
			if not material.users:
				material.user_clear()
				bpy.data.materials.remove(material)



def get_checker_name(mode, size_x, size_y):
	return (image_material_prefix+"{1}x{2}_{0}").format(mode, size_x, size_y)



def get_area_triangle_uv(A,B,C, size_x, size_y):
	scale_x = size_x / max(size_x, size_y)
	scale_y = size_y / max(size_x, size_y)
	A.x/=scale_x
	B.x/=scale_x
	C.x/=scale_x
	
	A.y/=scale_y
	B.y/=scale_y
	C.y/=scale_y

	return get_area_triangle(A,B,C)


def get_area_triangle(A,B,C):
	# Heron's formula: http://www.1728.org/triang.htm
	# area = square root (s • (s - a) • (s - b) • (s - c))
	a = (B-A).length
	b = (C-B).length
	c = (A-C).length
	s = (a+b+c)/2

	# Use abs(s-a) for values that otherwise generate negative values e.g. pinched UV verts, otherwise math domain error
	return math.sqrt(s * abs(s-a) * abs(s-b) * abs(s-c))


def get_texel_density(self, context):
	print("Get texel density")

	edit_mode = bpy.context.object.mode == 'EDIT'
	object_faces = get_selected_object_faces()

	# Warning: No valid input objects
	if len(object_faces) == 0:
		self.report({'ERROR_INVALID_INPUT'}, "No UV maps or meshes selected" )
		return

	print("obj faces groups {}".format(len(object_faces)))

	# Collect Images / textures
	object_images = {}
	for obj in object_faces:
		image = get_object_texture_image(obj)
		if image:
			object_images[obj] = image

	# Warning: No valid images
	if len(object_images) == 0:
		self.report({'ERROR_INVALID_INPUT'}, "No Texture found. Assign Checker map or texture first." )
		return

	sum_area_vt = 0
	sum_area_uv = 0

	# Get area for each triangle in view and UV
	for obj in object_faces:
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')
		bpy.context.scene.objects.active = obj
		obj.select = True

		# Find image of object
		image = object_images[obj]
		if image:
			bpy.ops.object.mode_set(mode='EDIT')
			bm = bmesh.from_edit_mesh(obj.data)
			uvLayer = bm.loops.layers.uv.verify()
			bm.faces.ensure_lookup_table()
			
			for index in object_faces[obj]:
				face = bm.faces[index]

				# Triangle Verts
				triangle_uv = [loop[uvLayer].uv for loop in face.loops ]
				triangle_vt = [vert.co for vert in face.verts]

				#Triangle Areas
				face_area_vt = get_area_triangle(
					triangle_vt[0], 
					triangle_vt[1], 
					triangle_vt[2] 
				)
				face_area_uv = get_area_triangle_uv(
					triangle_uv[0], 
					triangle_uv[1], 
					triangle_uv[2],
					image.size[0],
					image.size[1]
				)
				sum_area_vt+= math.sqrt( face_area_vt )
				sum_area_uv+= math.sqrt( face_area_uv ) * min(image.size[0], image.size[1])

	# Restore selection
	bpy.ops.object.mode_set(mode='OBJECT')
	bpy.ops.object.select_all(action='DESELECT')
	for obj in object_faces:
		obj.select = True
	bpy.context.scene.objects.active = list(object_faces.keys())[0]
	if edit_mode:
		bpy.ops.object.mode_set(mode='EDIT')

	# print("Sum verts area {}".format(sum_area_vt))
	# print("Sum texture area {}".format(sum_area_uv))

	if sum_area_uv == 0 or sum_area_vt == 0:
		bpy.context.scene.texToolsSettings.texel_density = 0
	else:
		bpy.context.scene.texToolsSettings.texel_density = sum_area_uv / sum_area_vt