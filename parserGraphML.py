bl_info = {
    "name": "EM tools",
    "author": "E. Demetrescu",
    "version": (1,0,0),
    "blender": (2, 7, 9),
    "location": "Tool Shelf panel",
    "description": "Blender tools for Extended Matrix",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Tools"}

#### iniziamo a importare un po' di moduli

import xml.etree.ElementTree as etree 
import bpy
import os
from bpy.props import (BoolProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
                       CollectionProperty
                       )

class EM_NODES_LIST(bpy.types.UIList):

    def draw_item(self, context, layout, test, active_data, active_propname, index, flt_flag):
        pass
    def draw_filter(self, context, layout):
        # Nothing much to say here, it's usual UI code...
        pass
        flt_flags = []
        flt_neworder = []

        # Do filtering/reordering here...

        return flt_flags, flt_neworder

##### da qui inizia la definizione delle classi pannello

class EMToolsPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "BL"
    bl_label = "Extended Matrix"
     
    def draw(self, context):
        layout = self.layout
        obj = context.object
        row = layout.row()
        row.label(text="EM file")
        row = layout.row()
        row.prop(context.scene, 'EM_file', toggle = True)
#        row = layout.row()
#        row.label(text="Painting Toolbox", icon='TPAINT_HLT')    
        row = layout.row()
        self.layout.operator("import.em_graphml", icon="STICKY_UVS_DISABLE", text='Read EM file')
        row = layout.row()
        layout.template_list("EM_NODE_LIST", "", obj, "material_slots", obj, "active_material_index")

#### da qui si definiscono gli operatori

class EM_import_GraphML(bpy.types.Operator):
    bl_idname = "import.em_graphml"
    bl_label = "Import the EM GraphML"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        graphml_file = bpy.data.scenes['Scene'].EM_file
        tree = etree.parse(graphml_file)
        test = tree.findall('.//{http://www.yworks.com/xml/graphml}NodeLabel')
        for n in test:
            print(n.text)
            print(n.tag)
            
#        basedir = os.path.dirname(bpy.data.filepath)
#        
#        if not basedir:
#            raise Exception("Il file Blender non è stato salvato, prima salvalo per la miseria !")

#        activename = bpy.path.clean_name(bpy.context.scene.objects.active.name)
#        fn = os.path.join(basedir, activename)
#        file = open(fn + ".txt", 'w')
        
        return {'FINISHED'}

    
# qui registro e cancello tutte le classi

def register():
    bpy.utils.register_class(EMToolsPanel)
#    bpy.utils.register_class(EM_import_GraphML)
    bpy.utils.register_module(__name__)
#    bpy.utils.register_class(EM_NODES_LIST)
    bpy.types.Scene.EM_file = StringProperty(
      name = "EM GraphML file",
      default = "",
      description = "Define the path to the EM GraphML file",
      subtype = 'FILE_PATH'
      )

def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.EM_file

if __name__ == "__main__":
    register()