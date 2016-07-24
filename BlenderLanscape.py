bl_info = {
    "name": "BlenderLandscape",
    "author": "E. Demetrescu",
    "version": (1,2.1),
    "blender": (2, 7, 7),
    "api": 48000,
    "location": "Tool Shelf panel",
    "description": "Blender tools for Landscape reconstruction",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Tools"}


import bpy
import os

from bpy_extras.io_utils import ImportHelper

from bpy.props import (BoolProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
                       CollectionProperty
                       )

# Panel creation in the toolshelf, category B2osg

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
        row.label(text="Active object is: " + obj.name)
        row = layout.row()
        row.label(text="Override")
        row = layout.row()
        row.prop(obj, "name")
        row = layout.row()
        self.layout.operator("export.coord", icon="WORLD_DATA", text='Export coordinates of selected')
        row = layout.row()
        self.layout.operator("export.coordname", icon="WORLD_DATA", text='Export position-name of selected')
        row = layout.row()
        row.label(text="Resulting file: " + obj.name + "-inst.txt")
        row = layout.row()
        self.layout.operator("export.object", icon="OBJECT_DATA", text='Export selected in one file')
        row = layout.row()
        row.label(text="Resulting file: " + obj.name + ".obj")
        row = layout.row()
        self.layout.operator("obj.exportbatch", icon="OBJECT_DATA", text='Export selected in several obj files')
        row = layout.row()
        self.layout.operator("fbx.exportbatch", icon="OBJECT_DATA", text='Export selected in several fbx files')
        row = layout.row()
        self.layout.operator("export.camdata", icon="OBJECT_DATA", text='Export cameras')

class ToolsPanel3(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "BL"
    bl_label = "Converters"
     
    def draw(self, context):
        layout = self.layout
        obj = context.object
        row = layout.row()
        self.layout.operator("center.mass", icon="DOT", text='Center of Mass')
        row = layout.row()
        self.layout.operator("local.texture", icon="TEXTURE", text='Local texture mode ON')

class ToolsPanel5(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
#    bl_context = "objectmode"
    bl_category = "BL"
    bl_label = "Photogrammetry"
#    bpy.types.Scene.scn_property = bpy.props.StringProperty(name = "UndistortedPath")
     
    def draw(self, context):
        layout = self.layout
        obj = context.object
        row = layout.row()
        row.label(text="Set up cams and scene", icon='RADIO')
        row = layout.row()
        self.layout.operator("correct.material", icon="NODE", text='Correct Photoscan mats')
        row = layout.row()
        self.layout.operator("isometric.scene", icon="RENDER_REGION", text='Isometric scene')
        self.layout.operator("canon6d.scene", icon="RENDER_REGION", text='CANON 6D scene')
        self.layout.operator("canon6d35mm.camera", icon="RENDER_REGION", text='Set as Canon6D 35mm')
        self.layout.operator("canon6d14mm.camera", icon="RENDER_REGION", text='Set as Canon6D 14mm')
        row = layout.row()
        self.layout.operator("better.cameras", icon="RENDER_REGION", text='Better Cams')
        self.layout.operator("nobetter.cameras", icon="RENDER_REGION", text='Disable Better Cams')
        row = layout.row()
        row.label(text="Folder with undistorted images:")
        row = layout.row()
        row.prop(context.scene, 'BL_undistorted_path', toggle = True)
        row = layout.row()
        row = layout.row()
        row.label(text="Painting Toolbox", icon='TPAINT_HLT')
        self.layout.operator("object.createcameraimageplane", icon="IMAGE_COL", text='Photo to camera')      
        row = layout.row()

        self.layout.operator("paint.cam", icon="IMAGE_COL", text='Paint selected from cam')
        self.layout.operator("applypaint.cam", icon="IMAGE_COL", text='Apply paint')
        self.layout.operator("savepaint.cam", icon="IMAGE_COL", text='Save modified texs')
 
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
        row.prop(obj, "name")
        row = layout.row()
        row.label(text="Active object is: " + obj.name)
        row = layout.row()
        self.layout.operator("lod2.b2osg", icon="COLOR", text='LOD 2')
        row = layout.row()
        row.label(text="Resulting files: ")
        row = layout.row()
        row.label(text= "LOD2_"+ obj.name + ".obj" )
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


class OBJECT_OT_ExportButton(bpy.types.Operator):
    bl_idname = "export.coord"
    bl_label = "Export coord"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):

        basedir = os.path.dirname(bpy.data.filepath)
        
        if not basedir:
            raise Exception("Il file Blender non è stato salvato, prima salvalo per la miseria !")

        selection = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')
        activename = bpy.path.clean_name(bpy.context.scene.objects.active.name)
        fn = os.path.join(basedir, activename)
        file = open(fn + "-inst.txt", 'w')
        
        # write selected objects coordinate
        for obj in selection:    
            obj.select = True  
            file.write("%s %s %s %s %s %s %s %s %s\n" % (obj.location[0], obj.location[1], obj.location[2], obj.rotation_euler[0], obj.rotation_euler[1], obj.rotation_euler[2], obj.scale[0], obj.scale[1], obj.scale[2]))
        file.close()
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
        for ma in bpy.data.materials:
            ma.alpha = 1.0
            ma.use_transparency = False
            ma.transparency_method = 'Z_TRANSPARENCY'
            ma.use_transparent_shadows = True
            ma.specular_intensity = 0.0
            ma.ambient = 0.0
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

            undistortedpath = bpy.context.scene.path
            
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
        camera = bpy.context.active_object #bpy.data.objects['Camera']
        return self.createImagePlaneForCamera(camera)

#_______________________________________________________________________________________________________________


class OBJECT_OT_LOD2(bpy.types.Operator):
    bl_idname = "lod2.b2osg"
    bl_label = "LOD2"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):

        basedir = os.path.dirname(bpy.data.filepath)
        
        if not basedir:
            raise Exception("Il file Blender non è stato salvato, prima salvalo per la miseria !")
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
        bpy.ops.paint.texture_paint_toggle()
        bpy.context.space_data.show_only_render = True
        bpy.ops.image.project_edit()
        obj_camera = bpy.context.scene.camera

        undistortedpath = bpy.context.scene.path
        if not undistortedpath:
            raise Exception("Hey Buddy, you have to set the undistorted images path !")
        
        undistortedphoto = undistortedpath+obj_camera.name
        cleanpath = bpy.path.abspath(undistortedphoto)
        bpy.ops.image.external_edit(filepath=cleanpath)

        return {'FINISHED'}

class OBJECT_OT_applypaintcam(bpy.types.Operator):
    bl_idname = "applypaint.cam"
    bl_label = "Apply paint"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        bpy.ops.paint.texture_paint_toggle()
        bpy.ops.image.project_apply()  
        bpy.context.space_data.show_only_render = False
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


class OBJECT_OT_fbxexportbatch(bpy.types.Operator):
    bl_idname = "fbx.exportbatch"
    bl_label = "Fbx export batch"
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
            bpy.ops.export_scene.fbx(filepath = fn + ".fbx", filter_glob="*.fbx", version='BIN7400', use_selection=True, global_scale=1.0, axis_forward='-Z', axis_up='Y', bake_space_transform=False, object_types={'MESH'}, use_mesh_modifiers=False, mesh_smooth_type='FACE', use_mesh_edges=False, use_tspace=False, use_armature_deform_only=False, bake_anim=False, bake_anim_use_nla_strips=False, bake_anim_step=1.0, bake_anim_simplify_factor=1.0, use_anim=False, use_anim_action_all=False, use_default_take=False, use_anim_optimize=False, anim_optimize_precision=6.0, path_mode='COPY', embed_textures=True, batch_mode='OFF', use_batch_own_dir=True, use_metadata=True)
            obj.select = False
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

#_______________________________________________________________________________________________________________


def menu_func_import(self, context):
    self.layout.operator(ImportMultipleObjs.bl_idname, text="Wavefont Batch (.obj)")

def register():
    bpy.utils.register_class(ToolsPanel4)
    bpy.utils.register_class(ToolsPanel)
    bpy.utils.register_class(ToolsPanel3)
    bpy.utils.register_class(ToolsPanel2)
    bpy.utils.register_class(OBJECT_OT_ExportButton)
    bpy.utils.register_class(OBJECT_OT_ExportButtonName)
    bpy.utils.register_class(OBJECT_OT_ExportCamButton)
    bpy.utils.register_class(OBJECT_OT_TranslatetoSCSButton)
    bpy.utils.register_class(OBJECT_OT_TranslatetoDPButton)
    bpy.utils.register_class(OBJECT_OT_CenterMass)
    bpy.utils.register_class(OBJECT_OT_LocalTexture)
    bpy.utils.register_class(OBJECT_OT_LOD2)
    bpy.utils.register_class(OBJECT_OT_AutomatorDP2)
    bpy.utils.register_class(OBJECT_OT_objexportbatch)
    bpy.utils.register_class(OBJECT_OT_fbxexportbatch)
    bpy.utils.register_class(OBJECT_OT_ExportObjButton)
    bpy.utils.register_class(OBJECT_OT_Canon6D35)
    bpy.utils.register_class(ImportMultipleObjs)
    bpy.types.INFO_MT_file_import.append(menu_func_import)

#    
#bpy.utils.register_module(__name__)
#
#
def register():
    bpy.utils.register_module(__name__)

# define path to undistorted image 
    bpy.types.Scene.BL_undistorted_path = StringProperty(
      name = "Undistorted Path",
      default = "",
      description = "Define the root path of the undistorted images",
      subtype = 'DIR_PATH'
      )
#
#
def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.utils.unregister_class(ImportMultipleObjs)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.BL_undistorted_path
#

if __name__ == "__main__":
    register()