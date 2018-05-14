import bpy
import os
import time
import bmesh
from random import randint, choice


def substring_after(s, delim):
    return s.partition(delim)[2]


def create_new_tex_set(mat, type):
    
    #retrieve image specs and position from material
    o_image = mat.texture_slots[0].texture.image
    x_image = mat.texture_slots[0].texture.image.size[0]
    y_image = mat.texture_slots[0].texture.image.size[1]
    o_imagepath = mat.texture_slots[0].texture.image.filepath
    o_imagepath_abs = bpy.path.abspath(o_imagepath)
    o_imagedir, o_filename = os.path.split(o_imagepath_abs)
    o_filename_no_ext = os.path.splitext(o_filename)[0]

    nodes = mat.node_tree.nodes
    node_tree = bpy.data.materials[mat.name].node_tree
    if type == "cc":
        if o_filename_no_ext.startswith("cc_"):
            print(substring_after(o_filename, "cc_"))
            t_image_name = "cc_2_"+o_filename_no_ext
        else:
            t_image_name = "cc_"+o_filename_no_ext
            print(substring_after(o_filename, "cc_"))
    if type == "source_paint":
        t_image_name = "sp_"+o_filename_no_ext
    
    t_image = bpy.data.images.new(name=t_image_name, width=x_image, height=y_image, alpha=False)
    # set path to new image
    fn = os.path.join(o_imagedir, t_image_name)
    t_image.filepath_raw = fn+".png"
    t_image.file_format = 'PNG'

    tteximg = nodes.new('ShaderNodeTexImage')
    tteximg.location = (-1100, -450)
    tteximg.image = t_image
    tteximg.name = type 

    for currnode in nodes:
        currnode.select = False

    # node_tree.nodes.select_all(action='DESELECT')
    tteximg.select = True
    node_tree.nodes.active = tteximg
    mat.texture_slots[0].texture.image = t_image

def node_retriever(mat):

    mat_nodes = mat.node_tree.nodes
    for node in mat_nodes:
        if node.name == "colcornode":
            cc_node = node
            pass
        else:
            cc_node = None
    for node in mat_nodes:
        if node.name == "original":
            original_node = node
            pass
        else:
            original_node = None
    for node in mat_nodes:
        if node.name == "diffuse":
            diffuse_node = node
            pass
        else:
            diffuse_node = None
    for node in mat_nodes:
        if node.name == "cc_image":
            cc_image_node = node
            pass
        else:
            cc_image_node = None
    for node in mat_nodes:
        if node.name == "source_paint_node":
            source_paint_node = node
            pass
        else:
            source_paint_node = None                     
    return original_node, cc_node, diffuse_node, cc_image_node, source_paint_node


def add_source_paint_slot(active_ob):
    
    for matslot in active_ob.material_slots:
        mat = matslot.material
#   force node use (to be removed in future versiones)
        mat.use_nodes = True
        for mat in active_ob.mat:
            nodes = mat.node_tree.nodes
            original_node, cc_node, diffuse_node, cc_image_node, source_paint_node = node_retriever(mat)
            if source_paint_node != None:
                nodes.remove(source_paint_node)
            teximg = nodes.new('ShaderNodeTexImage')
            teximg.location = (-1100, -50)
            teximg.image = image
            teximg.name = "source_paint_node"

# for cycles material

def create_correction_nodegroup(name):

    # create a group
#    active_object_name = bpy.context.scene.objects.active.name
    test_group = bpy.data.node_groups.new(name, 'ShaderNodeTree')
#    test_group.label = label

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

def find_cc_node(mat):
    mat_nodes = mat.node_tree.nodes
    for node in mat_nodes:
        if node.name == "colcornode":
            cc_node = node
            pass
        else:
            cc_node = None
    return cc_node

def create_texture_set():#(ob,context):
    
    for obj in bpy.context.selected_objects:
        active_object_name = bpy.context.scene.objects.active.name
        create_correction_nodegroup(active_object_name)

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
            teximg.name = "original"
            colcor = nodes.new(type="ShaderNodeGroup")
            colcor.node_tree = (bpy.data.node_groups[active_object_name])
            colcor.location = (-800, -50)
            links.new(teximg.outputs[0], colcor.inputs[0])
            links.new(colcor.outputs[0], mainNode.inputs[0])
            links.new(mainNode.outputs[0], output.inputs[0])
            colcor.name = "colcornode"

def remove_cc_node(mat):
    cc_node = find_cc_node(mat)
    if cc_node is not None:
        mat.node_tree.nodes.remove(cc_node)

# for quick utils____________________________________________
def make_group(ob,context):
    nomeoggetto = str(ob.name)
    if bpy.data.groups.get(nomeoggetto) is not None:
        currentgroup = bpy.data.groups.get(nomeoggetto)
        bpy.ops.group.objects_remove_all()
#        for object in currentgroup.objects:
#            bpy.ops.group.objects_remove(group=currentgroup)
    else:
        bpy.ops.group.create(name=nomeoggetto)
    ob.select = True
    bpy.ops.object.group_link(group=nomeoggetto)


def getnextobjname(name):
#    print("prendo in carico l'oggetto: "+name)
    #lst = ['this','is','just','a','test']
#    if fnmatch.filter(name, '.0*'):
    if name.endswith(".001") or name.endswith(".002") or name.endswith(".003") or name.endswith(".004") or name.endswith(".005"):
        current_nonumber = name[:-3]
#        print("ho ridotto il nome a :"+current_nonumber)
        current_n_integer = int(name[-3:])
#        print("aggiungo un numero")
        current_n_integer +=1
#        print(current_n_integer)
        if current_n_integer > 9:
            nextname = current_nonumber+'0'+str(current_n_integer)
        else:
            nextname = current_nonumber+'00'+str(current_n_integer)
    else:
        nextname = name+'.001'
#    print(nextname)
    return nextname

def newimage2selpoly(ob, nametex):
#    objectname = ob.name
    print("I'm creating texture: T_"+nametex+".png")
    me = ob.data
    tempimage = bpy.data.images.new(name=nametex, width=4096, height=4096, alpha=False)
    tempimage.filepath_raw = "//T_"+nametex+".png"
    tempimage.file_format = 'PNG'
    for uv_face in me.uv_textures.active.data:
        uv_face.image = tempimage
    return

def clean_name(name):
    if name.endswith(".001") or name.endswith(".002") or name.endswith(".003") or name.endswith(".004") or name.endswith(".005")or name.endswith(".006")or name.endswith(".007")or name.endswith(".008")or name.endswith(".009"):
        cname = name[:-4]
    else:
        cname = name
    return cname

def areamesh(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    area = sum(f.calc_area() for f in bm.faces)
#    print(area)
    bm.free()
    return area

def desiredmatnumber(ob):
    area = areamesh(ob)
    if area > 21:
        if area <103:
            desmatnumber = 6
            if area < 86:
                desmatnumber = 5
                if area < 68:
                    desmatnumber = 4
                    if area < 52:
                        desmatnumber = 3
                        if area < 37:
                            desmatnumber = 2
        else:
            desmatnumber = 6
            print("Be carefull ! the mesh is "+str(area)+" square meters is too big, consider to reduce it under 100. I will use six 4096 texture to describe it.")

    else:
        desmatnumber = 1

    return desmatnumber

# for 