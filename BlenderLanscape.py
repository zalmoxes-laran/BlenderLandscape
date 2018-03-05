bl_info = {
    "name": "BlenderLandscape",
    "author": "E. Demetrescu",
    "version": (1,3.6),
    "blender": (2, 7, 9),
    "location": "Tool Shelf panel",
    "description": "Blender tools for Landscape reconstruction",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Tools"}


import bpy
import os
import time

from mathutils import Vector
from bpy_extras.io_utils import ImportHelper

from bpy.props import (BoolProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
                       CollectionProperty
                       )

import bmesh
from random import randint, choice

# Panel creation in the toolshelf, category B2osg

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
        

#### start of funcions for multi-material baking #####

def clean_name(name):
    if name.endswith(".001") or name.endswith(".002") or name.endswith(".003") or name.endswith(".004") or name.endswith(".005")or name.endswith(".006")or name.endswith(".007")or name.endswith(".008")or name.endswith(".009"):
        cname = name[:-4]
    else:
        cname = name   
    return cname

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
        print(current_n_integer)
        if current_n_integer > 9:
            nextname = current_nonumber+'0'+str(current_n_integer)
        else:
            nextname = current_nonumber+'00'+str(current_n_integer)
    else:
        nextname = name+'.001'    
    print(nextname)
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

#### end of funcions for multi-material baking #####

class ToolsPanel4(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "BL"
    bl_label = "Importer"

    def draw(self, context):
        layout = self.layout
        obj = context.object
        row = layout.row()
        self.layout.operator("import_scene.multiple_objs", icon="WORLD_DATA", text='Import multiple objs')
#        row = layout.row()

class ToolsPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "BL"
    bl_label = "Exporters"

    def draw(self, context):
        layout = self.layout
        obj = context.object
        row = layout.row()
        if obj is not None:
            row.label(text="Active object is: " + obj.name)
            row = layout.row()
            row.label(text="Override")
            row = layout.row()
            row.prop(obj, "name")
            row = layout.row()
    #        self.layout.operator("export.coord", icon="WORLD_DATA", text='Coordinates of selected')
    #        row = layout.row()
            self.layout.operator("export.coordname", icon="WORLD_DATA", text='position-name of selected')
            row = layout.row()
            self.layout.operator("export.abscoordname", icon="WORLD_DATA", text='georef position-name')
            row = layout.row()
            row.label(text="Resulting file: " + obj.name + ".txt")
            row = layout.row()
            self.layout.operator("export.object", icon="OBJECT_DATA", text='Export selected in one file')
            row = layout.row()
            row.label(text="Resulting file: " + obj.name + ".obj")
            row = layout.row()
            self.layout.operator("obj.exportbatch", icon="OBJECT_DATA", text='Export selected in several obj files')
            row = layout.row()
            self.layout.operator("fbx.exportbatch", icon="OBJECT_DATA", text='Export selected in several fbx for UE4')
            row = layout.row()
            self.layout.operator("fbx.exp", icon="OBJECT_DATA", text='Export selected in fbx for UE4')
            row = layout.row()
            self.layout.operator("osgt.exportbatch", icon="OBJECT_DATA", text='Export selected in several osgt files')
            row = layout.row()
        else:
            row.label(text="Select object(s) to see tools here.")
            row = layout.row()
        self.layout.operator("export.camdata", icon="OBJECT_DATA", text='Export cameras')
        row = layout.row()
        self.layout.operator("export.coordnamelens", icon="WORLD_DATA", text='Name-position-lens (selected cams)')
        row = layout.row()
        row.label(text="Resulting file: cams.csv")
        row = layout.row()

class ToolsPanel3(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "BL"
    bl_label = "Quick Utils"
#    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        layout = self.layout
        obj = context.object
        scene = context.scene
        row = layout.row()
        self.layout.operator("center.mass", icon="DOT", text='Center of Mass')
        row = layout.row()
        self.layout.operator("local.texture", icon="TEXTURE", text='Local texture mode ON')
        row = layout.row()
        self.layout.operator("create.personalgroups", icon="GROUP", text='Create per-object groups')
        row = layout.row()
        self.layout.operator("remove.alluvexcept1", icon="GROUP", text='Only UV0 will survive')
        row = layout.row()
        self.layout.operator("remove.fromallgroups", icon="LIBRARY_DATA_BROKEN", text='Remove from all groups')
        row = layout.row()
        self.layout.operator("multimaterial.layout", icon="IMGDISPLAY", text='Multimaterial layout')
        row = layout.row()


# DA TROVARE IL MODO DI FARLO FUNZIONARE FUORI DALL'OUTLINER
#        self.layout.operator("purge.resources", icon="LIBRARY_DATA_BROKEN", text='Purge unused resources')
#        box = layout.box()
        row = layout.row()
#        box.

class ToolsPanel9(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "BL"
    bl_label = "Color Correction tool (cycles)"
#    bl_options = {'REGISTER', 'UNDO'}

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

class ToolsPanel5(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
#    bl_context = "objectmode"
    bl_category = "BL"
    bl_label = "Photogrammetry tool"
#    bpy.types.Scene.scn_property = bpy.props.StringProperty(name = "UndistortedPath")

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        obj = context.object

        obj_selected = scene.objects.active
        row = layout.row()
        row.label(text="Set up scene", icon='RADIO')
        row = layout.row()
        self.layout.operator("correct.material", icon="NODE", text='Correct Photoscan mats')
        self.layout.operator("isometric.scene", icon="RENDER_REGION", text='Isometric scene')
        self.layout.operator("canon6d.scene", icon="RENDER_REGION", text='CANON 6D scene')
        row = layout.row()
        row.label(text="Set selected cams as:", icon='RENDER_STILL')
        self.layout.operator("canon6d35mm.camera", icon="RENDER_REGION", text='Canon6D 35mm')
        self.layout.operator("canon6d24mm.camera", icon="RENDER_REGION", text='Canon6D 24mm')
        self.layout.operator("canon6d14mm.camera", icon="RENDER_REGION", text='Canon6D 14mm')
        row = layout.row()
        row.label(text="Visual mode for selected cams:", icon='NODE_SEL')
        self.layout.operator("better.cameras", icon="NODE_SEL", text='Better Cams')
        self.layout.operator("nobetter.cameras", icon="NODE_SEL", text='Disable Better Cams')
        row = layout.row()
        row = layout.row()
        row.label(text="Painting Toolbox", icon='TPAINT_HLT')
        row = layout.row()
        row.label(text="Folder with undistorted images:")
        row = layout.row()
        row.prop(context.scene, 'BL_undistorted_path', toggle = True)
        row = layout.row()

        if bpy.context.scene.camera is not None:
            cam_ob = scene.camera
            cam_cam = scene.camera.data
            row.label(text="Active Cam: " + cam_ob.name)
            self.layout.operator("object.createcameraimageplane", icon="IMAGE_COL", text='Photo to camera')
            row = layout.row()
            row = layout.row()
            row.prop(cam_cam, "lens")
            row = layout.row()
            row.label(text="Active object: " + obj.name)
            self.layout.operator("paint.cam", icon="IMAGE_COL", text='Paint active from cam')
            self.layout.operator("applypaint.cam", icon="IMAGE_COL", text='Apply paint')
            self.layout.operator("savepaint.cam", icon="IMAGE_COL", text='Save modified texs')
            row = layout.row()
        else:
            row.label(text="!!! Import some cams to start !!!")

#        self.layout.operator("cam.visibility", icon="RENDER_REGION", text='Cam visibility')

class ToolsPanel100(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
#    bl_context = "objectmode"
    bl_category = "BL"
    bl_label = "Spherical Photogrammetry tool"
#    bpy.types.Scene.scn_property = bpy.props.StringProperty(name = "UndistortedPath")

    def draw(self, context):
        layout = self.layout
        obj = context.object
        row = layout.row()
        row.label(text="Folder with the oriented 360 collection")
        row = layout.row()
        row.prop(context.scene, 'BL_oriented360_path', toggle = True)
        row = layout.row()
        row.label(text="Painting Toolbox", icon='TPAINT_HLT')
        row = layout.row()
        self.layout.operator("paint.cam", icon="IMAGE_COL", text='Paint selected from cam')

class ToolsPanel2(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "BL"
    bl_label = "LOD generator"

    def draw(self, context):
        layout = self.layout
        obj = context.object
        row = layout.row()
        if obj:
            row.label(text="Override name:")
            row = layout.row()
            row.prop(obj, "name", text='')
            row = layout.row()
        row.label(text="Actions on selected objects:")
        row = layout.row()
        self.layout.operator("lod0.b2osg", icon="MESH_UVSPHERE", text='LOD 0 (set as)')
        row = layout.row()
        row.label(text="Start always selecting LOD0 objs")
        self.layout.operator("lod1.b2osg", icon="MESH_ICOSPHERE", text='LOD 1 (creation)')
        self.layout.operator("lod2.b2osg", icon="MESH_CUBE", text='LOD 2 (creation)')
        row = layout.row()
        if obj:
            row.label(text="Resulting files: ")
            row = layout.row()
            row.label(text= "LOD1/LOD2_"+ obj.name + ".obj" )
            row = layout.row()
        self.layout.operator("create.grouplod", icon="OOPS", text='Create LOD cluster(s)')
        row = layout.row()
        self.layout.operator("remove.grouplod", icon="CANCEL", text='Remove LOD cluster(s)')
        row = layout.row()
        self.layout.operator("exportfbx.grouplod", icon="MESH_GRID", text='FBX Export LOD cluster(s)')
        row = layout.row()

class OBJECT_OT_ExportButtonName(bpy.types.Operator):
    bl_idname = "export.coordname"
    bl_label = "Export coord name"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        basedir = os.path.dirname(bpy.data.filepath)

        if not basedir:
            raise Exception("Il file Blender non è stato salvato, prima salvalo per la miseria !")

        selection = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')
        activename = bpy.path.clean_name(bpy.context.scene.objects.active.name)
        fn = os.path.join(basedir, activename)
        file = open(fn + ".txt", 'w')

        # write selected objects coordinate
        for obj in selection:
            obj.select = True
            file.write("%s %s %s %s\n" % (obj.name, obj.location[0], obj.location[1], obj.location[2]))
        file.close()
        return {'FINISHED'}

class OBJECT_OT_ExportButtonName(bpy.types.Operator):
    bl_idname = "export.coordname"
    bl_label = "Export coord name"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        basedir = os.path.dirname(bpy.data.filepath)

        if not basedir:
            raise Exception("Il file Blender non è stato salvato, prima salvalo per la miseria !")

        selection = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')
        activename = bpy.path.clean_name(bpy.context.scene.objects.active.name)
        fn = os.path.join(basedir, activename)
        file = open(fn + ".txt", 'w')

        # write selected objects coordinate
        for obj in selection:
            obj.select = True
            file.write("%s %s %s %s\n" % (obj.name, obj.location[0], obj.location[1], obj.location[2]))
        file.close()
        return {'FINISHED'}

class OBJECT_OT_ExportabsButtonName(bpy.types.Operator):
    bl_idname = "export.abscoordname"
    bl_label = "Export abs coord name"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        basedir = os.path.dirname(bpy.data.filepath)

        if not basedir:
            raise Exception("Il file Blender non è stato salvato, prima salvalo per la miseria !")

        selection = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')
        activename = bpy.path.clean_name(bpy.context.scene.objects.active.name)
        fn = os.path.join(basedir, activename)
        file = open(fn + ".txt", 'w')

        # write selected objects coordinate
        for obj in selection:
            obj.select = True
            x_abs = obj.location[0] + bpy.data.window_managers['WinMan'].crsx
            y_abs = obj.location[1] + bpy.data.window_managers['WinMan'].crsy
            file.write("%s %s %s %s\n" % (obj.name, x_abs, y_abs, obj.location[2]))
        file.close()
        return {'FINISHED'}

class OBJECT_OT_ExportButton(bpy.types.Operator):
    bl_idname = "export.coordnamelens"
    bl_label = "Export coord name lens"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        basedir = os.path.dirname(bpy.data.filepath)

        if not basedir:
            raise Exception("Il file Blender non è stato salvato, prima salvalo per la miseria !")

        selection = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')
        activename = bpy.path.clean_name(bpy.context.scene.objects.active.name)
#        fn = os.path.join(basedir, activename)
        fn = os.path.join(basedir, 'cams')
        file = open(fn + ".csv", 'w')

        # write selected objects coordinate
        for obj in selection:
            obj.select = True
            file.write("%s %s %s %s %s\n" % (obj.name, obj.location[0], obj.location[1], obj.location[2], obj.data.lens))
            file.close()
        return {'FINISHED'}



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

class OBJECT_OT_createpersonalgroups(bpy.types.Operator):
    bl_idname = "create.personalgroups"
    bl_label = "Create groups per single object"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        for ob in bpy.context.selected_objects:
            bpy.ops.object.select_all(action='DESELECT')
            ob.select = True
            bpy.context.scene.objects.active = ob
            make_group(ob,context)
        return {'FINISHED'}


class OBJECT_OT_removealluvexcept1(bpy.types.Operator):
    bl_idname = "remove.alluvexcept1"
    bl_label = "Remove all the UVs except the first one"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        for ob in bpy.context.selected_objects:
            if ob.data.uv_textures[1]:
                uv_textures = ob.data.uv_textures
                uv_textures.remove(uv_textures[1])
        return {'FINISHED'}

class OBJECT_OT_removefromallgroups(bpy.types.Operator):
    bl_idname = "remove.fromallgroups"
    bl_label = "Remove the object(s) from all the Groups"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        for ob in bpy.context.selected_objects:
            bpy.ops.group.objects_remove_all()
        return {'FINISHED'}


class OBJECT_OT_ExportCamButton(bpy.types.Operator):
    bl_idname = "export.camdata"
    bl_label = "Export cam data"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        basedir = os.path.dirname(bpy.data.filepath)

        if not basedir:
            raise Exception("Il file Blender non è stato salvato, prima salvalo per la miseria !")
        selection = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')
        activename = bpy.path.clean_name(bpy.context.scene.objects.active.name)
        fn = os.path.join(basedir, activename)
        file = open(fn + ".txt", 'w')

        # write selected objects coordinate
        for obj in selection:
            obj.select = True
            file.write("%s %s %s %s %s %s %s %s\n" % (obj.name, obj.location[0], obj.location[1], obj.location[2], obj.rotation_euler[0], obj.rotation_euler[1], obj.rotation_euler[2], obj.data.lens))
        file.close()
        return {'FINISHED'}

class OBJECT_OT_CenterMass(bpy.types.Operator):
    bl_idname = "center.mass"
    bl_label = "Center Mass"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        selection = bpy.context.selected_objects
#        bpy.ops.object.select_all(action='DESELECT')

        # translate objects in SCS coordinate
        for obj in selection:
            obj.select = True
            bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')
        return {'FINISHED'}

class OBJECT_OT_LocalTexture(bpy.types.Operator):
    bl_idname = "local.texture"
    bl_label = "Local texture mode ON"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.ops.file.autopack_toggle()
        bpy.ops.file.autopack_toggle()
        bpy.ops.file.unpack_all(method='WRITE_LOCAL')
        bpy.ops.file.make_paths_relative()
        return {'FINISHED'}

class OBJECT_OT_CorrectMaterial(bpy.types.Operator):
    bl_idname = "correct.material"
    bl_label = "Correct photogr. mats"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        selection = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')
        for obj in selection:
            obj.select = True
            for i in range(0,len(obj.material_slots)):
#                bpy.ops.object.material_slot_remove()
                obj.active_material_index = i
                ma = obj.active_material
                ma.specular_intensity = 0
                ma.alpha = 1.0
                ma.use_transparency = False
                ma.transparency_method = 'Z_TRANSPARENCY'
                ma.use_transparent_shadows = True
                ma.ambient = 0.0
                image = ma.texture_slots[0].texture.image
                image.use_alpha = False
        return {'FINISHED'}


class OBJECT_OT_IsometricScene(bpy.types.Operator):
    bl_idname = "isometric.scene"
    bl_label = "Isometric scene"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
#        bpy.context.scene.compression = 90
        bpy.context.scene.render.resolution_x = 3000
        bpy.context.scene.render.resolution_y = 3000
        bpy.context.scene.render.resolution_percentage = 100
        bpy.context.scene.game_settings.material_mode = 'GLSL'
        bpy.context.scene.game_settings.use_glsl_lights = False
        bpy.context.scene.world.light_settings.use_ambient_occlusion = True
        bpy.context.scene.render.alpha_mode = 'TRANSPARENT'
        return {'FINISHED'}


class OBJECT_OT_Canon6Dscene(bpy.types.Operator):
    bl_idname = "canon6d.scene"
    bl_label = "Canon 6D scene"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.context.scene.render.resolution_x = 5472
        bpy.context.scene.render.resolution_y = 3648
        bpy.context.scene.render.resolution_percentage = 100
        bpy.context.scene.tool_settings.image_paint.screen_grab_size[0] = 5472
        bpy.context.scene.tool_settings.image_paint.screen_grab_size[1] = 3648
        bpy.context.scene.game_settings.material_mode = 'GLSL'
        bpy.context.scene.game_settings.use_glsl_lights = False
        return {'FINISHED'}

class OBJECT_OT_Canon6D35(bpy.types.Operator):
    bl_idname = "canon6d35mm.camera"
    bl_label = "Set as Canon 6D 35mm"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        selection = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')
        for obj in selection:
            obj.select = True
            obj.data.lens = 35
            obj.data.sensor_fit = 'HORIZONTAL'
            obj.data.sensor_width = 35.8
            obj.data.sensor_height = 23.9
        return {'FINISHED'}

class OBJECT_OT_Canon6D24(bpy.types.Operator):
    bl_idname = "canon6d24mm.camera"
    bl_label = "Set as Canon 6D 14mm"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        selection = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')
        for obj in selection:
            obj.select = True
            obj.data.lens = 24
            obj.data.sensor_fit = 'HORIZONTAL'
            obj.data.sensor_width = 35.8
            obj.data.sensor_height = 23.9
        return {'FINISHED'}

class OBJECT_OT_Canon6D14(bpy.types.Operator):
    bl_idname = "canon6d14mm.camera"
    bl_label = "Set as Canon 6D 14mm"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        selection = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')
        for obj in selection:
            obj.select = True
            obj.data.lens = 14.46
            obj.data.sensor_fit = 'HORIZONTAL'
            obj.data.sensor_width = 35.8
            obj.data.sensor_height = 23.9
        return {'FINISHED'}

class OBJECT_OT_BetterCameras(bpy.types.Operator):
    bl_idname = "better.cameras"
    bl_label = "Better Cameras"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        selection = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')
        for cam in selection:
            cam.select = True
            cam.data.show_limits = True
            cam.data.clip_start = 0.5
            cam.data.clip_end = 4
            cam.scale[0] = 0.1
            cam.scale[1] = 0.1
            cam.scale[2] = 0.1
        return {'FINISHED'}

class OBJECT_OT_NoBetterCameras(bpy.types.Operator):
    bl_idname = "nobetter.cameras"
    bl_label = "Disable Better Cameras"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        selection = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')
        for cam in selection:
            cam.select = True
            cam.data.show_limits = False
        return {'FINISHED'}

#_______________________________________________________________________________________________________________

class CreateCameraImagePlane(bpy.types.Operator):
    """Create image plane for camera"""
    bl_idname= "object.createcameraimageplane"
    bl_label="Camera Image Plane"
    bl_options={'REGISTER', 'UNDO'}
    def SetupDriverVariables(self, driver, imageplane):
        camAngle = driver.variables.new()
        camAngle.name = 'camAngle'
        camAngle.type = 'SINGLE_PROP'
        camAngle.targets[0].id = imageplane.parent
        camAngle.targets[0].data_path="data.angle"

        depth = driver.variables.new()
        depth.name = 'depth'
        depth.type = 'TRANSFORMS'
        depth.targets[0].id = imageplane
        depth.targets[0].data_path = 'location'
        depth.targets[0].transform_type = 'LOC_Z'
        depth.targets[0].transform_space = 'LOCAL_SPACE'

    def SetupDriversForImagePlane(self, imageplane):
        driver = imageplane.driver_add('scale',1).driver
        driver.type = 'SCRIPTED'
        self.SetupDriverVariables( driver, imageplane)
        #driver.expression ="-depth*math.tan(camAngle/2)*resolution_y*pixel_y/(resolution_x*pixel_x)"
        driver.expression ="-depth*tan(camAngle/2)*bpy.context.scene.render.resolution_y * bpy.context.scene.render.pixel_aspect_y/(bpy.context.scene.render.resolution_x * bpy.context.scene.render.pixel_aspect_x)"
        driver = imageplane.driver_add('scale',0).driver
        driver.type= 'SCRIPTED'
        self.SetupDriverVariables( driver, imageplane)
        driver.expression ="-depth*tan(camAngle/2)"

    # get selected camera (might traverse children of selected object until a camera is found?)
    # for now just pick the active object

    def createImagePlaneForCamera(self, camera):
        imageplane = None
        try:
            depth = 10

            #create imageplane
            bpy.ops.mesh.primitive_plane_add()#radius = 0.5)
            imageplane = bpy.context.active_object
            imageplane.name = ("objplane_"+camera.name)
            bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='TOGGLE')
            bpy.ops.transform.resize( value=(0.5,0.5,0.5))
            bpy.ops.uv.smart_project(angle_limit=66,island_margin=0, user_area_weight=0)
            bpy.ops.uv.select_all(action='TOGGLE')
            bpy.ops.transform.rotate(value=1.5708, axis=(0,0,1) )
            bpy.ops.object.editmode_toggle()

            imageplane.location = (0,0,-depth)
            imageplane.parent = camera

            #calculate scale
            #REPLACED WITH CREATING EXPRESSIONS
            self.SetupDriversForImagePlane(imageplane)

            #setup material
            if( len( imageplane.material_slots) == 0 ):
                bpy.ops.object.material_slot_add()
                #imageplane.material_slots.
            bpy.ops.material.new()
            mat_index = len(bpy.data.materials)-1
            imageplane.material_slots[0].material = bpy.data.materials[mat_index]
            material =  imageplane.material_slots[0].material
            # if not returned by new use imgeplane.material_slots[0].material
            material.name = 'mat_imageplane_'+camera.name

            material.use_nodes = False


            activename = bpy.path.clean_name(bpy.context.scene.objects.active.name)

            undistortedpath = bpy.context.scene.BL_undistorted_path

            if not undistortedpath:
                raise Exception("Hey Buddy, you have to set the undistorted images path !")

            bpy.context.object.data.uv_textures.active.data[0].image = bpy.data.images.load(undistortedpath+camera.name)

            bpy.ops.view3d.tex_to_material()

        except Exception as e:
            imageplane.select=False
            camera.select = True
            raise e
        return {'FINISHED'}

    def execute(self, context):
#        camera = bpy.context.active_object #bpy.data.objects['Camera']
        scene = context.scene
        undistortedpath = bpy.context.scene.BL_undistorted_path
        cam_ob = bpy.context.scene.camera

        if not undistortedpath:
            raise Exception("Set the Undistort path before to activate this command")
        else:
            obj_exists = False
            for obj in cam_ob.children:
                if obj.name.startswith("objplane_"):
                    obj.hide = False
                    obj_exists = True
                    bpy.ops.object.select_all(action='DESELECT')
                    scene.objects.active = obj
                    obj.select = True
                    return {'FINISHED'}
            if obj_exists is False:
                camera = bpy.context.scene.camera
                return self.createImagePlaneForCamera(camera)

#_____________________________________________________________________________

class OBJECT_OT_LOD0(bpy.types.Operator):
    bl_idname = "lod0.b2osg"
    bl_label = "LOD0"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        for obj in bpy.context.selected_objects:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select = True
            bpy.context.scene.objects.active = obj
            bpy.ops.object.shade_smooth()
            baseobj = obj.name
            if not baseobj.endswith('LOD0'):
                obj.name = baseobj + '_LOD0'
            if obj.data.uv_textures[0].name =='MultiTex' and obj.data.uv_textures[1].name =='Atlas':
                pass
            else:
                mesh = obj.data
                mesh.uv_textures.active_index = 0
                multitex_uvmap = mesh.uv_textures.active
                multitex_uvmap_name = multitex_uvmap.name
                multitex_uvmap.name = 'MultiTex'
                atlas_uvmap = mesh.uv_textures.new()
                atlas_uvmap.name = 'Atlas'
                mesh.uv_textures.active_index = 1
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.remove_doubles()
                bpy.ops.uv.select_all(action='SELECT')
                bpy.ops.uv.pack_islands(margin=0.001)
                bpy.ops.object.editmode_toggle()
                mesh.uv_textures.active_index = 0

        return {'FINISHED'}

#_____________________________________________________________________________


class OBJECT_OT_LOD1(bpy.types.Operator):
    bl_idname = "lod1.b2osg"
    bl_label = "LOD1"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        start_time = time.time()
        basedir = os.path.dirname(bpy.data.filepath)
        subfolder = 'LOD1'
        if not os.path.exists(os.path.join(basedir, subfolder)):
            os.mkdir(os.path.join(basedir, subfolder))
            print('There is no LOD1 folder. Creating one...')
        else:
            print('Found previously created LOD1 folder. I will use it')
        if not basedir:
            raise Exception("Il file Blender non è stato salvato, per favore, prima salvalo")

        ob_counter = 1
        ob_tot = len(bpy.context.selected_objects)
        print('<<<<<<<<<<<<<< CREATION OF LOD 1 >>>>>>>>>>>>>>')
        print('>>>>>> '+str(ob_tot)+' objects will be processed')

        for obj in bpy.context.selected_objects:
            start_time_ob = time.time()
            print('>>> LOD 1 >>>')
            print('>>>>>> processing the object ""'+ obj.name+'"" ('+str(ob_counter)+'/'+str(ob_tot)+')')
            bpy.ops.object.select_all(action='DESELECT')
            obj.select = True
            bpy.context.scene.objects.active = obj
            baseobjwithlod = obj.name
            if '_LOD0' in baseobjwithlod:
                baseobj = baseobjwithlod.replace("_LOD0", "")
            else:
                baseobj = baseobjwithlod
            print('Creating new LOD1 object..')
            bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})

            for obj in bpy.context.selected_objects:
                obj.name = baseobj + "_LOD1"
                newobj = obj
            for obj in bpy.context.selected_objects:
                lod1name = obj.name
            for i in range(0,len(bpy.data.objects[lod1name].material_slots)):
                bpy.ops.object.material_slot_remove()

            if obj.data.uv_textures[1] and obj.data.uv_textures[1].name =='Atlas':
                print('Found Atlas UV mapping layer. I will use it.')
                uv_textures = obj.data.uv_textures
                uv_textures = obj.data.uv_textures
                uv_textures.remove(uv_textures[0])
            else:
                print('Creating new UV mapping layer.')
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.remove_doubles()
                bpy.ops.uv.select_all(action='SELECT')
                bpy.ops.uv.pack_islands(margin=0.001)
                bpy.ops.object.editmode_toggle()


            # procedura di semplificazione mesh
            bpy.ops.object.editmode_toggle()
            print('Decimating the original mesh to obtain the LOD1 mesh...')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_non_manifold()
            bpy.ops.object.vertex_group_add()
            bpy.ops.object.vertex_group_assign()
            bpy.ops.object.editmode_toggle()
            bpy.data.objects[lod1name].modifiers.new("Decimate", type='DECIMATE')
            obj.modifiers["Decimate"].ratio = 0.5
            obj.modifiers["Decimate"].vertex_group = "Group"
            obj.modifiers["Decimate"].invert_vertex_group = True
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Decimate")
            # ora la mesh è semplificata
            #------------------------------------------------------------------


            bpy.ops.object.select_all(action='DESELECT')
            oggetto = bpy.data.objects[lod1name]
            oggetto.select = True
            print('Creating new texture atlas for LOD1....')

            tempimage = bpy.data.images.new(name=lod1name, width=2048, height=2048, alpha=False)
            tempimage.filepath_raw = "//"+subfolder+'/'+lod1name+".jpg"
            tempimage.file_format = 'JPEG'

            for uv_face in oggetto.data.uv_textures.active.data:
                uv_face.image = tempimage

            #--------------------------------------------------------------
            print('Passing color data from LOD0 to LOD1...')
            bpy.context.scene.render.engine = 'BLENDER_RENDER'
            bpy.context.scene.render.use_bake_selected_to_active = True
            bpy.context.scene.render.bake_type = 'TEXTURE'

            object = bpy.data.objects[baseobjwithlod]
            object.select = True

            bpy.context.scene.objects.active = bpy.data.objects[lod1name]
            #--------------------------------------------------------------

            bpy.ops.object.bake_image()
            tempimage.save()

            print('Creating custom material for LOD1...')
            bpy.ops.object.select_all(action='DESELECT')
            oggetto = bpy.data.objects[lod1name]
            oggetto.select = True
            bpy.context.scene.objects.active = oggetto
            bpy.ops.view3d.texface_to_material()
            oggetto.active_material.name = 'M_'+ oggetto.name
            oggetto.data.name = 'SM_' + oggetto.name
    #        basedir = os.path.dirname(bpy.data.filepath)

            print('Saving on obj/mtl file for LOD1...')
            activename = bpy.path.clean_name(bpy.context.scene.objects.active.name)
            fn = os.path.join(basedir, subfolder, activename)
            bpy.ops.export_scene.obj(filepath=fn + ".obj", use_selection=True, axis_forward='Y', axis_up='Z', path_mode='RELATIVE')

            bpy.ops.object.move_to_layer(layers=(False, False, False, False, False, False, False, False, False, False, False, True, False, False, False, False, False, False, False, False))
            print('>>> "'+obj.name+'" ('+str(ob_counter)+'/'+ str(ob_tot) +') object baked in '+str(time.time() - start_time_ob)+' seconds')
            ob_counter += 1

        bpy.context.scene.layers[11] = True
        bpy.context.scene.layers[0] = False
        end_time = time.time() - start_time
        print('<<<<<<< Process done >>>>>>')
        print('>>>'+str(ob_tot)+' objects processed in '+str(end_time)+' seconds')
        return {'FINISHED'}


#______________________________________


class OBJECT_OT_LOD2(bpy.types.Operator):
    bl_idname = "lod2.b2osg"
    bl_label = "LOD2"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        start_time = time.time()
        basedir = os.path.dirname(bpy.data.filepath)
        subfolder = 'LOD2'
        if not os.path.exists(os.path.join(basedir, subfolder)):
            os.mkdir(os.path.join(basedir, subfolder))
            print('There is no LOD2 folder. Creating one...')
        else:
            print('Found previously created LOD1 folder. I will use it')
        if not basedir:
            raise Exception("Il file Blender non è stato salvato, per favore, prima salvalo")
        ob_counter = 1
        ob_tot = len(bpy.context.selected_objects)
        print('<<<<<<<<<<<<<< CREATION OF LOD 2 >>>>>>>>>>>>>>')
        print('>>>>>> '+str(ob_tot)+' objects will be processed')

        for obj in bpy.context.selected_objects:
            print('>>> LOD 2 >>>')
            print('>>>>>> processing the object ""'+ obj.name+'"" ('+str(ob_counter)+'/'+str(ob_tot)+')')
            start_time_ob = time.time()

            bpy.ops.object.select_all(action='DESELECT')
            obj.select = True
            bpy.context.scene.objects.active = obj
            baseobjwithlod = obj.name
            if '_LOD0' in baseobjwithlod:
                baseobj = baseobjwithlod.replace("_LOD0", "")
            else:
                baseobj = baseobjwithlod
            print('Creating new LOD2 object..')
            bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})

            for obj in bpy.context.selected_objects:
                obj.name = baseobj + "_LOD2"
                newobj = obj
            for obj in bpy.context.selected_objects:
                lod2name = obj.name

            for i in range(0,len(bpy.data.objects[lod2name].material_slots)):
                bpy.ops.object.material_slot_remove()

# se abbiamo già un atlas è inutile rifarlo
            if obj.data.uv_textures[1] and obj.data.uv_textures[1].name =='Atlas':
                print('Found Atlas UV mapping layer. I will use it.')
                uv_textures = obj.data.uv_textures
                uv_textures.remove(uv_textures[0])

            else:
                print('Creating new UV mapping layer.')
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.remove_doubles()
                bpy.ops.uv.select_all(action='SELECT')
                bpy.ops.uv.pack_islands(margin=0.001)
                bpy.ops.object.editmode_toggle()

            # procedura di semplificazione mesh

            print('Decimating the original mesh to obtain the LOD2 mesh...')
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_non_manifold()
            bpy.ops.object.vertex_group_add()
            bpy.ops.object.vertex_group_assign()
            bpy.ops.object.editmode_toggle()
            bpy.data.objects[lod2name].modifiers.new("Decimate", type='DECIMATE')
            obj.modifiers["Decimate"].ratio = 0.1
            obj.modifiers["Decimate"].vertex_group = "Group"
            obj.modifiers["Decimate"].invert_vertex_group = True
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Decimate")
            # ora la mesh è semplificata
            #------------------------------------------------------------------
            bpy.ops.object.select_all(action='DESELECT')
            oggetto = bpy.data.objects[lod2name]
            oggetto.select = True
            print('Creating new texture atlas for LOD2....')

            tempimage = bpy.data.images.new(name=lod2name, width=512, height=512, alpha=False)
            tempimage.filepath_raw = "//"+subfolder+'/'+lod2name+".jpg"
            tempimage.file_format = 'JPEG'

            for uv_face in oggetto.data.uv_textures.active.data:
                uv_face.image = tempimage

            #--------------------------------------------------------------
            print('Passing color data from LOD0 to LOD2...')
            bpy.context.scene.render.engine = 'BLENDER_RENDER'
            bpy.context.scene.render.use_bake_selected_to_active = True
            bpy.context.scene.render.bake_type = 'TEXTURE'

            object = bpy.data.objects[baseobjwithlod]
            object.select = True

            bpy.context.scene.objects.active = bpy.data.objects[lod2name]
            #--------------------------------------------------------------

            bpy.ops.object.bake_image()
            tempimage.save()

            print('Creating custom material for LOD2...')

            bpy.ops.object.select_all(action='DESELECT')
            oggetto = bpy.data.objects[lod2name]
            oggetto.select = True

            bpy.context.scene.objects.active = oggetto
            bpy.ops.view3d.texface_to_material()

            oggetto.active_material.name = 'M_'+ oggetto.name
            oggetto.data.name = 'SM_' + oggetto.name

            print('Saving on obj/mtl file for LOD2...')
            activename = bpy.path.clean_name(bpy.context.scene.objects.active.name)
            fn = os.path.join(basedir, subfolder, activename)
            bpy.ops.export_scene.obj(filepath=fn + ".obj", use_selection=True, axis_forward='Y', axis_up='Z', path_mode='RELATIVE')

            bpy.ops.object.move_to_layer(layers=(False, False, False, False, False, False, False, False, False, False, True, False, False, False, False, False, False, False, False, False))
            print('>>> "'+obj.name+'" ('+str(ob_counter)+'/'+ str(ob_tot) +') object baked in '+str(time.time() - start_time_ob)+' seconds')
            ob_counter += 1

        bpy.context.scene.layers[10] = True
        bpy.context.scene.layers[0] = False
        end_time = time.time() - start_time
        print('<<<<<<< Process done >>>>>>')
        print('>>>'+str(ob_tot)+' objects processed in '+str(end_time)+' seconds')
        return {'FINISHED'}

#_______________________________________________________________

def selectLOD(listobjects, lodnum, basename):
    name2search = basename + '_LOD' + str(lodnum)
    for ob in listobjects:
        if ob.name == name2search:
            objatgivenlod = ob
            return objatgivenlod
        else:
            objatgivenlod = None
    return objatgivenlod

def getChildren(myObject):
    children = []
    for ob in bpy.data.objects:
        if ob.parent == myObject:
            children.append(ob)
    return children

#_______________________________________________________________

class OBJECT_OT_ExportGroupsLOD(bpy.types.Operator):
    bl_idname = "exportfbx.grouplod"
    bl_label = "Export Group LOD"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        start_time = time.time()
        basedir = os.path.dirname(bpy.data.filepath)
        if not basedir:
            raise Exception("Blend file is not saved")
        ob_counter = 1
        scene = context.scene
        listobjects = bpy.context.selected_objects
        for obj in listobjects:
            if obj.type == 'EMPTY':
                if obj.get('fbx_type') is not None:
                    print('Found LOD cluster to export: "'+obj.name+'", object')
                    bpy.ops.object.select_all(action='DESELECT')
                    obj.select = True
                    bpy.context.scene.objects.active = obj
                    for ob in getChildren(obj):
                        ob.select = True
                    name = bpy.path.clean_name(obj.name)
                    fn = os.path.join(basedir, name)
                    bpy.ops.export_scene.fbx(filepath= fn + ".fbx", check_existing=True, axis_forward='-Z', axis_up='Y', filter_glob="*.fbx", version='BIN7400', ui_tab='MAIN', use_selection=True, global_scale=1.0, apply_unit_scale=True, bake_space_transform=False, object_types={'ARMATURE', 'CAMERA', 'EMPTY', 'LAMP', 'MESH', 'OTHER'}, use_mesh_modifiers=True, mesh_smooth_type='EDGE', use_mesh_edges=False, use_tspace=False, use_custom_props=False, add_leaf_bones=True, primary_bone_axis='Y', secondary_bone_axis='X', use_armature_deform_only=False, bake_anim=True, bake_anim_use_all_bones=True, bake_anim_use_nla_strips=True, bake_anim_use_all_actions=True, bake_anim_force_startend_keying=True, bake_anim_step=1.0, bake_anim_simplify_factor=1.0, use_anim=True, use_anim_action_all=True, use_default_take=True, use_anim_optimize=True, anim_optimize_precision=6.0, path_mode='RELATIVE', embed_textures=False, batch_mode='OFF', use_batch_own_dir=True, use_metadata=True)
                else:
                    print('The "' + obj.name + '" empty object has not the correct settings to export an FBX - LOD enabled file. I will skip it.')
                    obj.select = False
                    print('>>> Object number '+str(ob_counter)+' processed in '+str(time.time() - start_time)+' seconds')
                    ob_counter += 1

        end_time = time.time() - start_time
        print('<<<<<<< Process done >>>>>>')
        print('>>>'+str(ob_counter)+' objects processed in '+str(end_time)+' seconds')

        return {'FINISHED'}

#_______________________________________________________________



class OBJECT_OT_RemoveGroupsLOD(bpy.types.Operator):
    bl_idname = "remove.grouplod"
    bl_label = "Remove Group LOD"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        listobjects = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')
        for obj in listobjects:
            if obj.get('fbx_type') is not None:
                obj.select = True
                bpy.context.scene.objects.active = obj
                for ob in getChildren(obj):
                    ob.select = True
                bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
                bpy.ops.object.select_all(action='DESELECT')
                obj.select = True
                bpy.context.scene.objects.active = obj
                bpy.ops.object.delete()
        return {'FINISHED'}

#_______________________________________________________________


class OBJECT_OT_CreateGroupsLOD(bpy.types.Operator):
    bl_idname = "create.grouplod"
    bl_label = "Create Group LOD"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        listobjects = bpy.context.selected_objects
        for obj in listobjects:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select = True
            bpy.context.scene.objects.active = obj
            baseobjwithlod = obj.name

            if '_LOD0' in baseobjwithlod:
                baseobj = baseobjwithlod.replace("_LOD0", "")
                print('Found LOD0 object:' + baseobjwithlod)
                local_bbox_center = 0.125 * sum((Vector(b) for b in obj.bound_box), Vector())
                global_bbox_center = obj.matrix_world * local_bbox_center
                emptyofname = 'GLOD_' + baseobj
                obempty = bpy.data.objects.new( emptyofname, None )
                bpy.context.scene.objects.link( obempty )
                obempty.empty_draw_size = 2
                obempty.empty_draw_type = 'PLAIN_AXES'
                obempty.location = global_bbox_center
                bpy.ops.object.select_all(action='DESELECT')
                obempty.select = True
                bpy.context.scene.objects.active = obempty
                obempty['fbx_type'] = 'LodGroup'
#                bpy.ops.wm.properties_edit(data_path="object", property="Fbx_Type", value="LodGroup", min=0, max=1, use_soft_limits=False, soft_min=0, soft_max=1, description="")

                num = 0
                child = selectLOD(listobjects, num, baseobj)
                while child is not None:
                    bpy.ops.object.select_all(action='DESELECT')
                    child.select = True
                    obempty.select = True
                    bpy.context.scene.objects.active = obempty
                    bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
#                    child.parent= obempty
#                    child.location.x = child.location.x - obempty.location.x
#                    child.location.y = child.location.y - obempty.location.y
                    num += 1
                    child = selectLOD(listobjects, num, baseobj)
        return {'FINISHED'}

class OBJECT_OT_ExportObjButton(bpy.types.Operator):
    bl_idname = "export.object"
    bl_label = "Export object"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        basedir = os.path.dirname(bpy.data.filepath)

        if not basedir:
            raise Exception("Il file Blender non è stato salvato, prima salvalo per la miseria !")

#        selection = bpy.context.selected_objects
#        bpy.ops.object.select_all(action='DESELECT')
        activename = bpy.path.clean_name(bpy.context.scene.objects.active.name)
        fn = os.path.join(basedir, activename)

        # write active object in obj format
        bpy.ops.export_scene.obj(filepath=fn + ".obj", use_selection=True, axis_forward='Y', axis_up='Z', path_mode='RELATIVE')
        return {'FINISHED'}


class OBJECT_OT_paintcam(bpy.types.Operator):
    bl_idname = "paint.cam"
    bl_label = "Paint selected from current cam"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        scene = context.scene
        undistortedpath = bpy.context.scene.BL_undistorted_path
        cam_ob = bpy.context.scene.camera

        if not undistortedpath:
            raise Exception("Set the Undistort path before to activate this command")
        else:
            for obj in cam_ob.children:
                if obj.name.startswith("objplane_"):
                    obj.hide = True
            bpy.ops.paint.texture_paint_toggle()
            bpy.context.space_data.show_only_render = True
            bpy.ops.image.project_edit()
            obj_camera = bpy.context.scene.camera

            undistortedphoto = undistortedpath+obj_camera.name
            cleanpath = bpy.path.abspath(undistortedphoto)
            bpy.ops.image.external_edit(filepath=cleanpath)

            bpy.context.space_data.show_only_render = False
            bpy.ops.paint.texture_paint_toggle()

        return {'FINISHED'}

class OBJECT_OT_applypaintcam(bpy.types.Operator):
    bl_idname = "applypaint.cam"
    bl_label = "Apply paint"
    bl_options = {"REGISTER"}

    def execute(self, context):
        bpy.ops.paint.texture_paint_toggle()
        bpy.ops.image.project_apply()
        bpy.ops.paint.texture_paint_toggle()
        return {'FINISHED'}

class OBJECT_OT_savepaintcam(bpy.types.Operator):
    bl_idname = "savepaint.cam"
    bl_label = "Save paint"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
#        bpy.ops.paint.texture_paint_toggle()
        bpy.ops.image.save_dirty()
        return {'FINISHED'}

#    print("written:", fn)

#_______________________________________________________________________________________________________________


class OBJECT_OT_objexportbatch(bpy.types.Operator):
    bl_idname = "obj.exportbatch"
    bl_label = "Obj export batch"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        basedir = os.path.dirname(bpy.data.filepath)
        if not basedir:
            raise Exception("Blend file is not saved")

        selection = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')

        for obj in selection:
            obj.select = True
            name = bpy.path.clean_name(obj.name)
            fn = os.path.join(basedir, name)
            bpy.ops.export_scene.obj(filepath=str(fn + '.obj'), use_selection=True, axis_forward='Y', axis_up='Z', path_mode='RELATIVE')
            obj.select = False
        return {'FINISHED'}

#_______________________________________________________________________________________________________________

class OBJECT_OT_fbxexp(bpy.types.Operator):
    bl_idname = "fbx.exp"
    bl_label = "Fbx export UE4"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        basedir = os.path.dirname(bpy.data.filepath)
        if not basedir:
            raise Exception("Blend file is not saved")
        obj = bpy.context.scene.objects.active
        name = bpy.path.clean_name(obj.name)
        fn = os.path.join(basedir, name)
        bpy.ops.export_scene.fbx(filepath= fn + ".fbx", check_existing=True, axis_forward='-Z', axis_up='Y', filter_glob="*.fbx", version='BIN7400', ui_tab='MAIN', use_selection=True, global_scale=100.0, apply_unit_scale=True, bake_space_transform=False, object_types={'ARMATURE', 'CAMERA', 'EMPTY', 'LAMP', 'MESH', 'OTHER'}, use_mesh_modifiers=True, mesh_smooth_type='EDGE', use_mesh_edges=False, use_tspace=False, use_custom_props=False, add_leaf_bones=True, primary_bone_axis='Y', secondary_bone_axis='X', use_armature_deform_only=False, bake_anim=True, bake_anim_use_all_bones=True, bake_anim_use_nla_strips=True, bake_anim_use_all_actions=True, bake_anim_force_startend_keying=True, bake_anim_step=1.0, bake_anim_simplify_factor=1.0, use_anim=True, use_anim_action_all=True, use_default_take=True, use_anim_optimize=True, anim_optimize_precision=6.0, path_mode='AUTO', embed_textures=False, batch_mode='OFF', use_batch_own_dir=True, use_metadata=True)
#filepath = fn + ".fbx", filter_glob="*.fbx", version='BIN7400', use_selection=True, global_scale=100.0, axis_forward='-Z', axis_up='Y', bake_space_transform=False, object_types={'MESH','EMPTY'}, use_mesh_modifiers=False, mesh_smooth_type='EDGE', use_mesh_edges=False, use_tspace=False, use_armature_deform_only=False, bake_anim=False, bake_anim_use_nla_strips=False, bake_anim_step=1.0, bake_anim_simplify_factor=1.0, use_anim=False, use_anim_action_all=False, use_default_take=False, use_anim_optimize=False, anim_optimize_precision=6.0, path_mode='AUTO', embed_textures=False, batch_mode='OFF', use_batch_own_dir=True, use_metadata=True)

#        obj.select = False
        return {'FINISHED'}

#_______________________________________________________________________________________________________________

class OBJECT_OT_fbxexportbatch(bpy.types.Operator):
    bl_idname = "fbx.exportbatch"
    bl_label = "Fbx export batch UE4"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        basedir = os.path.dirname(bpy.data.filepath)
        if not basedir:
            raise Exception("Blend file is not saved")

        selection = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')

        for obj in selection:
            obj.select = True
            name = bpy.path.clean_name(obj.name)
            fn = os.path.join(basedir, name)
            bpy.ops.export_scene.fbx(filepath = fn + ".fbx", filter_glob="*.fbx", version='BIN7400', use_selection=True, global_scale=100.0, axis_forward='-Z', axis_up='Y', bake_space_transform=False, object_types={'MESH'}, use_mesh_modifiers=False, mesh_smooth_type='FACE', use_mesh_edges=False, use_tspace=False, use_armature_deform_only=False, bake_anim=False, bake_anim_use_nla_strips=False, bake_anim_step=1.0, bake_anim_simplify_factor=1.0, use_anim=False, use_anim_action_all=False, use_default_take=False, use_anim_optimize=False, anim_optimize_precision=6.0, path_mode='AUTO', embed_textures=False, batch_mode='OFF', use_batch_own_dir=True, use_metadata=True)
            obj.select = False
        return {'FINISHED'}
#_______________________________________________________________________________________________________________
class OBJECT_OT_fbxexportbatch(bpy.types.Operator):
    bl_idname = "osgt.exportbatch"
    bl_label = "osgt export batch"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        basedir = os.path.dirname(bpy.data.filepath)
        if not basedir:
            raise Exception("Blend file is not saved")

        bpy.ops.osg.export(SELECTED=True)

#        selection = bpy.context.selected_objects
#        bpy.ops.object.select_all(action='DESELECT')
#
#        for obj in selection:
#            obj.select = True
#            name = bpy.path.clean_name(obj.name)
#            fn = os.path.join(basedir, name)
#            bpy.ops.osg.export(filepath = fn + ".osgt", SELECTED=True)
#            bpy.ops.osg.export(SELECTED=True)
#            obj.select = False
        return {'FINISHED'}


#_______________________________________________________________________________________________________________

def assignmatslots(ob, matlist):
    #given an object and a list of material names
    #removes all material slots form the object
    #adds new ones for each material in matlist
    #adds the materials to the slots as well.

    scn = bpy.context.scene
    ob_active = bpy.context.active_object
    scn.objects.active = ob

    for s in ob.material_slots:
        bpy.ops.object.material_slot_remove()

    # re-add them and assign material
    i = 0
    for m in matlist:
        mat = bpy.data.materials[m]
        ob.data.materials.append(mat)
        bpy.context.object.active_material.use_transparency = True
        bpy.context.object.active_material.alpha = 0.5
        i += 1

    # restore active object:
    scn.objects.active = ob_active


def check_texture(img, mat):
    #finds a texture from an image
    #makes a texture if needed
    #adds it to the material if it isn't there already

    tex = bpy.data.textures.get(img.name)

    if tex is None:
        tex = bpy.data.textures.new(name=img.name, type='IMAGE')

    tex.image = img

    #see if the material already uses this tex
    #add it if needed
    found = False
    for m in mat.texture_slots:
        if m and m.texture == tex:
            found = True
            break
    if not found and mat:
        mtex = mat.texture_slots.add()
        mtex.texture = tex
        mtex.texture_coords = 'UV'
        mtex.use_map_color_diffuse = True

def tex_to_mat():
    # editmode check here!
    editmode = False
    ob = bpy.context.object
    if ob.mode == 'EDIT':
        editmode = True
        bpy.ops.object.mode_set()

    for ob in bpy.context.selected_editable_objects:

        faceindex = []
        unique_images = []

        # get the texface images and store indices
        if (ob.data.uv_textures):
            for f in ob.data.uv_textures.active.data:
                if f.image:
                    img = f.image
                    #build list of unique images
                    if img not in unique_images:
                        unique_images.append(img)
                    faceindex.append(unique_images.index(img))

                else:
                    img = None
                    faceindex.append(None)

        # check materials for images exist; create if needed
        matlist = []
        for i in unique_images:
            if i:
                try:
                    m = bpy.data.materials[i.name]
                except:
                    m = bpy.data.materials.new(name=i.name)
                    continue

                finally:
                    matlist.append(m.name)
                    # add textures if needed
                    check_texture(i, m)

        # set up the object material slots
        assignmatslots(ob, matlist)

        #set texface indices to material slot indices..
        me = ob.data

        i = 0
        for f in faceindex:
            if f is not None:
                me.polygons[i].material_index = f
            i += 1
    if editmode:
        bpy.ops.object.mode_set(mode='EDIT')

class VIEW3D_OT_tex_to_material(bpy.types.Operator):
    """Create texture materials for images assigned in UV editor"""
    bl_idname = "view3d.tex_to_material"
    bl_label = "Texface Images to Material/Texture (Material Utils)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        if context.selected_editable_objects:
            tex_to_mat()
            return {'FINISHED'}
        else:
            self.report({'WARNING'},
                        "No editable selected objects, could not finish")
            return {'CANCELLED'}

#_______________________________________________________________________________________________________________


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


class ImportMultipleObjs(bpy.types.Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "import_scene.multiple_objs"
    bl_label = "Import multiple OBJ's"
    bl_options = {'PRESET', 'UNDO'}

    # ImportHelper mixin class uses this
    filename_ext = ".obj"

    filter_glob = StringProperty(
            default="*.obj",
            options={'HIDDEN'},
            )

    # Selected files
    files = CollectionProperty(type=bpy.types.PropertyGroup)

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    ngons_setting = BoolProperty(
            name="NGons",
            description="Import faces with more than 4 verts as ngons",
            default=True,
            )
    edges_setting = BoolProperty(
            name="Lines",
            description="Import lines and faces with 2 verts as edge",
            default=True,
            )
    smooth_groups_setting = BoolProperty(
            name="Smooth Groups",
            description="Surround smooth groups by sharp edges",
            default=True,
            )

    split_objects_setting = BoolProperty(
            name="Object",
            description="Import OBJ Objects into Blender Objects",
            default=True,
            )
    split_groups_setting = BoolProperty(
            name="Group",
            description="Import OBJ Groups into Blender Objects",
            default=True,
            )

    groups_as_vgroups_setting = BoolProperty(
            name="Poly Groups",
            description="Import OBJ groups as vertex groups",
            default=False,
            )

    image_search_setting = BoolProperty(
            name="Image Search",
            description="Search subdirs for any associated images "
                        "(Warning, may be slow)",
            default=True,
            )

    split_mode_setting = EnumProperty(
            name="Split",
            items=(('ON', "Split", "Split geometry, omits unused verts"),
                   ('OFF', "Keep Vert Order", "Keep vertex order from file"),
                   ),
            )

    clamp_size_setting = FloatProperty(
            name="Clamp Size",
            description="Clamp bounds under this value (zero to disable)",
            min=0.0, max=1000.0,
            soft_min=0.0, soft_max=1000.0,
            default=0.0,
            )
    axis_forward_setting = EnumProperty(
            name="Forward",
            items=(('X', "X Forward", ""),
                   ('Y', "Y Forward", ""),
                   ('Z', "Z Forward", ""),
                   ('-X', "-X Forward", ""),
                   ('-Y', "-Y Forward", ""),
                   ('-Z', "-Z Forward", ""),
                   ),
            default='Y',
            )

    axis_up_setting = EnumProperty(
            name="Up",
            items=(('X', "X Up", ""),
                   ('Y', "Y Up", ""),
                   ('Z', "Z Up", ""),
                   ('-X', "-X Up", ""),
                   ('-Y', "-Y Up", ""),
                   ('-Z', "-Z Up", ""),
                   ),
            default='Z',
            )

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.prop(self, "ngons_setting")
        row.prop(self, "edges_setting")

        layout.prop(self, "smooth_groups_setting")

        box = layout.box()
        row = box.row()
        row.prop(self, "split_mode_setting", expand=True)

        row = box.row()
        if self.split_mode_setting == 'ON':
            row.label(text="Split by:")
            row.prop(self, "split_objects_setting")
            row.prop(self, "split_groups_setting")
        else:
            row.prop(self, "groups_as_vgroups_setting")

        row = layout.split(percentage=0.67)
        row.prop(self, "clamp_size_setting")
        layout.prop(self, "axis_forward_setting")
        layout.prop(self, "axis_up_setting")

        layout.prop(self, "image_search_setting")

    def execute(self, context):

        # get the folder
        folder = (os.path.dirname(self.filepath))

        # iterate through the selected files
        for i in self.files:

            # generate full path to file
            path_to_file = (os.path.join(folder, i.name))

            # call obj operator and assign ui values
            bpy.ops.import_scene.obj(filepath = path_to_file,
                                axis_forward = self.axis_forward_setting,
                                axis_up = self.axis_up_setting,
                                use_edges = self.edges_setting,
                                use_smooth_groups = self.smooth_groups_setting,
                                use_split_objects = self.split_objects_setting,
                                use_split_groups = self.split_groups_setting,
                                use_groups_as_vgroups = self.groups_as_vgroups_setting,
                                use_image_search = self.image_search_setting,
                                split_mode = self.split_mode_setting,
                                global_clamp_size = self.clamp_size_setting)

        return {'FINISHED'}

#-------------------------------------------------------------

class OBJECT_OT_purge(bpy.types.Operator):
    """Purge resources BE CAREFULL !!"""
    bl_idname = "purge.resources"
    bl_label = "Purge resources BE CAREFULL !!"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        bpy.ops.outliner.orphans_purge()
        bpy.ops.outliner.orphans_purge()
        bpy.ops.outliner.orphans_purge()
        bpy.ops.outliner.orphans_purge()
        bpy.ops.outliner.orphans_purge()

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

#_______________________________________________________________________________________________________________

class OBJECT_OT_multimateriallayout(bpy.types.Operator):
    """Create multimaterial layout on selected mesh"""
    bl_idname = "multimaterial.layout"
    bl_label = "Create a multimaterial layout for selected meshe(s)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        totmodels=len(context.selected_objects)
        padding = 0.05
        #ob = bpy.context.object
        print("Found "+str(totmodels)+" models.")
        currentmod = 1
        for ob in context.selected_objects:
            print("I'm starting to process: "+ob.name+" model ("+str(currentmod)+"/"+str(totmodels)+")")
            bpy.ops.object.select_all(action='DESELECT')
            ob.select = True
            bpy.context.scene.objects.active = ob
            currentobjname = ob.name    
            objectname = ob.name
            me = ob.data
            tot_poly = len(me.polygons)
            materialnumber = desiredmatnumber(ob) #final number of whished materials
            materialsoriginal=len(ob.material_slots)
            cleaned_obname = clean_name(objectname)
            print("Removing the old "+str(materialsoriginal)+" materials..")

            for i in range(0,materialsoriginal):
                bpy.ops.object.material_slot_remove()
            current_material = 1
            for mat in range(materialnumber-1):
                bpy.ops.object.editmode_toggle()
                print("Selecting polygons for mat: "+str(mat+1)+"/"+str(materialnumber))
                bpy.ops.mesh.select_all(action='DESELECT')
                me.update()
                poly = len(me.polygons)
                bm = bmesh.from_edit_mesh(me)
                for i in range(5):
                    #print(i+1)
                    r = choice([(0,poly)])
                    random_index=(randint(*r))
                    if hasattr(bm.faces, "ensure_lookup_table"):
                        bm.faces.ensure_lookup_table()
                    bm.faces[random_index].select = True
                    bmesh.update_edit_mesh(me, True)
                poly_sel = 5 
                while poly_sel <= (tot_poly/materialnumber):
                    bpy.ops.mesh.select_more(use_face_step=True)
                    ob.update_from_editmode()
                    poly_sel = len([p for p in ob.data.polygons if p.select])
                bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=padding)
                bpy.ops.uv.pack_islands(margin=padding)
                print("Creating new textures (remember to save them later..)")
                bpy.ops.object.editmode_toggle()
                current_tex_name = (cleaned_obname+'_t'+str(current_material))
                newimage2selpoly(ob, current_tex_name)
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.separate(type='SELECTED')
                bpy.ops.object.editmode_toggle()
                current_material += 1

            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.uv.smart_project(island_margin=padding)
            bpy.ops.uv.pack_islands(margin=padding)
            bpy.ops.object.editmode_toggle()
            current_tex_name = (cleaned_obname+'_t'+str(current_material))
            newimage2selpoly(ob, current_tex_name)
            bpy.ops.object.select_all(action='DESELECT')
            ob.select = True
            bpy.context.scene.objects.active = ob
            currentobjname = ob.name

            for mat in range(materialnumber-1):
                
                bpy.data.objects[getnextobjname(currentobjname)].select = True
                nextname = getnextobjname(currentobjname)
                currentobjname = nextname

            bpy.ops.object.join()
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.remove_doubles()
            bpy.ops.object.editmode_toggle()
            #bpy.ops.view3d.texface_to_material()
            currentmod += 1

        return {'FINISHED'}



def menu_func_import(self, context):
    self.layout.operator(ImportMultipleObjs.bl_idname, text="Wavefont Batch (.obj)")

def register():
    bpy.utils.register_class(ToolsPanel4)
    bpy.utils.register_class(ToolsPanel)
    bpy.utils.register_class(ToolsPanel3)
    bpy.utils.register_class(ToolsPanel2)
    bpy.utils.register_class(ToolsPanel100)
    bpy.utils.register_class(OBJECT_OT_ExportButton)
    bpy.utils.register_class(OBJECT_OT_ExportButtonName)
    bpy.utils.register_class(OBJECT_OT_ExportCamButton)
    bpy.utils.register_class(OBJECT_OT_createpersonalgroups)
    bpy.utils.register_class(OBJECT_OT_removealluvexcept1)
    bpy.utils.register_class(OBJECT_OT_CenterMass)
    bpy.utils.register_class(OBJECT_OT_LocalTexture)
    bpy.utils.register_class(OBJECT_OT_LOD0)
    bpy.utils.register_class(OBJECT_OT_LOD1)
    bpy.utils.register_class(OBJECT_OT_LOD2)
    bpy.utils.register_class(OBJECT_OT_CreateGroupsLOD)
    bpy.utils.register_class(OBJECT_OT_ExportGroupsLOD)
    bpy.utils.register_class(OBJECT_OT_RemoveGroupsLOD)
    bpy.utils.register_class(OBJECT_OT_objexportbatch)
    bpy.utils.register_class(OBJECT_OT_fbxexportbatch)
    bpy.utils.register_class(OBJECT_OT_fbxexp)
    bpy.utils.register_class(OBJECT_OT_ExportObjButton)
    bpy.utils.register_class(OBJECT_OT_Canon6D35)
    bpy.utils.register_class(ImportMultipleObjs)
    bpy.utils.register_class(OBJECT_OT_material)
    bpy.utils.register_class(OBJECT_OT_removecc)
    bpy.utils.register_class(OBJECT_OT_bakecyclesdiffuse)
    bpy.utils.register_class(OBJECT_OT_removefromallgroups)
    bpy.utils.register_class(OBJECT_OT_multimateriallayout)
    bpy.types.INFO_MT_file_import.append(menu_func_import)

#
#bpy.utils.register_module(__name__)
#
#
#def register():
    bpy.utils.register_module(__name__)
#    bpy.types.Scene.colcor_bricon = bpy.props.FloatProperty(
#        name = "Brightness",
#        description = "Color correction brightness",
#        default = 0.0,
#        min = -3.0,
#        max = 3.0
#    )

# define path to undistorted image
    bpy.types.Scene.BL_undistorted_path = StringProperty(
      name = "Undistorted Path",
      default = "",
      description = "Define the root path of the undistorted images",
      subtype = 'DIR_PATH'
      )

    bpy.types.Scene.BL_oriented360_path = StringProperty(
      name = "Oriented 360 Path",
      default = "",
      description = "Define the root path of the oriented 360 collection",
      subtype = 'DIR_PATH'
      )
#
#
def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.utils.unregister_class(OBJECT_OT_LOD0)
    bpy.utils.unregister_class(OBJECT_OT_LOD1)
    bpy.utils.unregister_class(OBJECT_OT_LOD2)
    bpy.utils.unregister_class(OBJECT_OT_CreateGroupsLOD)
    bpy.utils.unregister_class(OBJECT_OT_ExportGroupsLOD)
    bpy.utils.unregister_class(OBJECT_OT_RemoveGroupsLOD)
    bpy.utils.unregister_class(ImportMultipleObjs)
    bpy.utils.unregister_class(OBJECT_OT_removecc)
    bpy.utils.unregister_class(OBJECT_OT_createpersonalgroups)
    bpy.utils.unregister_class(OBJECT_OT_removealluvexcept1)
    bpy.utils.unregister_class(OBJECT_OT_fbxexp)
    bpy.utils.unregister_class(OBJECT_OT_bakecyclesdiffuse)
    bpy.utils.unregister_class(OBJECT_OT_multimateriallayout)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    del bpy.types.Scene.colcor_bricon
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.BL_undistorted_path
#

if __name__ == "__main__":
    register()
