bl_info = {
    "name": "Blender2osg",
    "author": "E. Demetrescu",
    "version": (0,9),
    "blender": (2, 7, 7),
    "api": 48000,
    "location": "Tool Shelf panel",
    "description": "Blender exporter to osg4web",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Exporter"}


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
    bl_category = "B2OSG"
    bl_label = "Importer"
     
    def draw(self, context):
        layout = self.layout
        obj = context.object
        row = layout.row()
        self.layout.operator("import_scene.multiple_objs", icon="WORLD_DATA", text='Import multiple objs')

class ToolsPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "B2OSG"
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
    bl_category = "B2OSG"
    bl_label = "Converters"
     
    def draw(self, context):
        layout = self.layout
        obj = context.object
        row = layout.row()
        self.layout.operator("translate.scs", icon="AUTO", text='Grab Selected to SCS')
        row = layout.row()
        self.layout.operator("translate.dp", icon="AUTO", text='Grab Selected to D. Piscului')
        row = layout.row()
        self.layout.operator("center.mass", icon="DOT", text='Center of Mass')
        row = layout.row()
        self.layout.operator("local.texture", icon="TEXTURE", text='Local texture mode ON')

class ToolsPanel2(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "B2OSG"
    bl_label = "Automator"
     
    def draw(self, context):
        layout = self.layout
        
        obj = context.object
        row = layout.row()
        row.prop(obj, "name")
        row = layout.row()
        row.label(text="Active object is: " + obj.name)
        row = layout.row()
        self.layout.operator("automator.b2osg", icon="COLOR", text='Automator')
        row = layout.row()
        row.label(text="Resulting files: ")
        row = layout.row()
        row.label(text= obj.name + "-inst.txt and " + obj.name + ".obj" )
        row = layout.row()
        self.layout.operator("automator.export", icon="COLOR", text='D. Piscului to exported SCS')
        row = layout.row()
        row.label(text="Resulting files: ")
        row = layout.row()
        row.label(text= obj.name + ".obj" )
        

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

class OBJECT_OT_TranslatetoSCSButton(bpy.types.Operator):
    bl_idname = "translate.scs"
    bl_label = "Translate to SCS"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):

        selection = bpy.context.selected_objects
#        bpy.ops.object.select_all(action='DESELECT')
        
        # translate objects in SCS coordinate
        for obj in selection:    
            obj.select = True  
            bpy.ops.transform.translate(value=(-327300, -448370, -500), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
        return {'FINISHED'}

class OBJECT_OT_TranslatetoDPButton(bpy.types.Operator):
    bl_idname = "translate.dp"
    bl_label = "Translate to DP"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):

        selection = bpy.context.selected_objects
#        bpy.ops.object.select_all(action='DESELECT')
        
        # translate objects in SCS coordinate
        for obj in selection:    
            obj.select = True  
            bpy.ops.transform.translate(value=(327300, 448370, 500), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
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

class OBJECT_OT_Automator(bpy.types.Operator):
    bl_idname = "automator.b2osg"
    bl_label = "Automator"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):

        selection = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')
        
        for obj in selection:    
            obj.select = True  
            bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')
            basedir = os.path.dirname(bpy.data.filepath)
            if not basedir:
                raise Exception("Il file Blender non è stato salvato, prima salvalo per la miseria !")
            activename = bpy.path.clean_name(bpy.context.scene.objects.active.name)
            fn = os.path.join(basedir, activename)
            file = open(fn + "-inst.txt", 'w')
            file.write("%s %s %s %s %s %s %s %s %s\n" % (obj.location[0], obj.location[1], obj.location[2], obj.rotation_euler[0], obj.rotation_euler[1], obj.rotation_euler[2], obj.scale[0], obj.scale[1], obj.scale[2]))
            file.close()
            bpy.context.object.location[0] = 0
            bpy.context.object.location[1] = 0
            bpy.context.object.location[2] = 0
            bpy.ops.export_scene.obj(filepath=fn + ".obj", use_selection=True, axis_forward='Y', axis_up='Z', path_mode='RELATIVE')
        return {'FINISHED'}

class OBJECT_OT_AutomatorDP2(bpy.types.Operator):
    bl_idname = "automator.export"
    bl_label = "Automator DP2"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):

        selection = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')
        
        for obj in selection:    
            obj.select = True
            bpy.ops.transform.translate(value=(-233000, -394000, -150), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
            bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
            basedir = os.path.dirname(bpy.data.filepath)
            if not basedir:
                raise Exception("Il file Blender non è stato salvato, prima salvalo per la miseria !")
            activename = bpy.path.clean_name(bpy.context.scene.objects.active.name)
            fn = os.path.join(basedir, activename)
            bpy.ops.export_scene.obj(filepath=fn + ".obj", use_selection=True, axis_forward='Y', axis_up='Z', path_mode='RELATIVE')
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
    bpy.utils.register_class(OBJECT_OT_Automator)
    bpy.utils.register_class(OBJECT_OT_AutomatorDP2)
    bpy.utils.register_class(OBJECT_OT_objexportbatch)
    bpy.utils.register_class(OBJECT_OT_fbxexportbatch)
    bpy.utils.register_class(OBJECT_OT_ExportObjButton)
    bpy.utils.register_class(ImportMultipleObjs)
    bpy.types.INFO_MT_file_import.append(menu_func_import)

#    
#bpy.utils.register_module(__name__)
#
#
def register():
    bpy.utils.register_module(__name__)
#
#
def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.utils.unregister_class(ImportMultipleObjs)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
#

if __name__ == "__main__":
    register()