import bpy
import time
import bmesh
from random import randint, choice

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