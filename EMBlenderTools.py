bl_info = {
    "name": "EM tools",
    "author": "E. Demetrescu",
    "version": (1,0,1),
    "blender": (2, 7, 9),
    "location": "Tool Shelf panel",
    "description": "Blender tools for Extended Matrix",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Tools"}

#### iniziamo a importare un po' di moduli

import xml.etree.ElementTree as ET
import bpy
import os
import bpy.props as prop
from bpy.props import (BoolProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
                       CollectionProperty,
                       IntProperty
                       )

class EMListItem(bpy.types.PropertyGroup):
    """ Group of properties representing an item in the list """

    name = prop.StringProperty(
           name="Name",
           description="A name for this item",
           default="Untitled")
    
    description = prop.StringProperty(
           name="Description",
           description="A description for this item",
           default="Empty")

    icon = prop.StringProperty(
           name="code for icon",
           description="",
           default="")

class EM_UL_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        # We could write some code to decide which icon to use here...
        
        scene = context.scene
#        custom_icon = 'CANCEL'

        # Make sure your code supports all 3 layout types
#        if self.layout_type in {'DEFAULT', 'COMPACT'}:
        layout.label(item.name, icon = item.icon)
        layout.label(item.description, icon='NONE', icon_value=0)
#        layout.prop(item, "description", text="", emboss=False)
#        icon = item.icon

#        elif self.layout_type in {'GRID'}:
#            layout.alignment = 'CENTER'
#            layout.label("", icon = custom_icon)

##### da qui inizia la definizione delle classi pannello

class EMToolsPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "BL"
    bl_label = "Extended Matrix"
     
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        obj = context.object
        row = layout.row()
        row.label(text="EM file")
        row = layout.row()
        row.prop(context.scene, 'EM_file', toggle = True) 
        row = layout.row()
        self.layout.operator("import.em_graphml", icon="STICKY_UVS_DISABLE", text='Read/Refresh EM file')
        row = layout.row()
        row.template_list("EM_UL_List", "EM nodes", scene, "em_list", scene, "em_list_index" )
        if scene.em_list_index >= 0 and len(scene.em_list) > 0:
            item = scene.em_list[scene.em_list_index]
            row = layout.row()
            row.prop(item, "name")
#            row.prop(item, "random_property")
            
                    
#### da qui si definiscono le funzioni e gli operatori

def EM_extract_node_name(node_element):
    for subnode in node_element.findall('.//{http://graphml.graphdrawing.org/xmlns}data'):
        attrib = subnode.attrib
        if attrib == {'key': 'd4'}:
            nodeurl = subnode.text
        else:
            nodeurl = 'Non assegnato'
        print(nodeurl)
        if attrib == {'key': 'd5'}:
            nodedescription = subnode.text
        else:
            nodedescription = 'Non assegnato'
        print(nodedescription)
        for USname in subnode.findall('.//{http://www.yworks.com/xml/graphml}NodeLabel'):
            nodename = USname.text
            print(nodename)
        for USshape in subnode.findall('.//{http://www.yworks.com/xml/graphml}Shape'):
            nodeshape = USshape.attrib
            print(nodeshape)   
    return nodename, nodedescription, nodeurl, nodeshape 

def EM_check_node_type(node_element):
    id_node = str(node_element.attrib)
    if id_node.startswith("{'yfiles.foldertype': 'group', 'id':"):
        tablenode = node_element.find('.//{http://www.yworks.com/xml/graphml}TableNode')
#        print(tablenode.attrib)
        if tablenode is not None:
            print('è un nodo swimlane: ' + id_node)
            node_type = 'node_swimlane'
        else:
            print('è un nodo group: ' + id_node)
            node_type = 'node_group'
    else:
        print('è un semplice nodo: ' + id_node)
        node_type = 'node_simple'
    return node_type

def EM_check_node_us(node_element):
    us_name = node_element.find('.//{http://www.yworks.com/xml/graphml}NodeLabel')
    if us_name.text.startswith("SU") or us_name.text.startswith("USV") or us_name.text.startswith("USM") or us_name.text.startswith("USR"):
        id_node_us = True
    else:
        id_node_us = False
    return id_node_us


#Check the presence-absence of US against the GraphML
def EM_check_GraphML_Blender(node_name):
    data = bpy.data
    for ob in data.objects:
        if ob.name == node_name:
            icon_check = 'FILE_TICK'
        else:
            icon_check = 'CANCEL'
    return icon_check
    

class EM_import_GraphML(bpy.types.Operator):
    bl_idname = "import.em_graphml"
    bl_label = "Import the EM GraphML"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        scene = context.scene
        graphml_file = scene.EM_file
        tree = ET.parse(graphml_file)
#        tree = ET.parse('/Users/emanueldemetrescu/Desktop/EM_test.graphml')
        allnodes = tree.findall('.//{http://graphml.graphdrawing.org/xmlns}node')
        for node_element in allnodes:
            if EM_check_node_type(node_element) == 'node_simple':
                if EM_check_node_us(node_element):
                    my_nodename, my_node_description, my_node_url, my_node_shape = EM_extract_node_name(node_element)
                else:
                    pass
            else:
                pass        

        
#        test = tree.findall('.//{http://www.yworks.com/xml/graphml}NodeLabel')
#        
#        scene.em_list.update()
#        list_lenght = len(scene.em_list)
#        for x in range(list_lenght):
#            scene.em_list.remove(0)

#        em_list_index_ema = 0
#        for n in test:
#            if n.text.startswith("SU") or n.text.startswith("USV") or n.text.startswith("USM") or n.text.startswith("USR"):
#                scene.em_list.add()
#                scene.em_list[em_list_index_ema].name = n.text
#                scene.em_list[em_list_index_ema].icon = EM_check_GraphML_Blender(n.text)
#                scene.em_list[em_list_index_ema].description = 'to be implemented'
#                em_list_index_ema += 1
##        
        return {'FINISHED'}

    
# qui registro e cancello tutte le classi

def register():
    bpy.utils.register_class(EMToolsPanel)
    bpy.utils.register_class(EM_import_GraphML)
    bpy.utils.register_class(EMListItem)
    bpy.utils.register_class(EM_UL_List)

# here I register the EM node list with the stratigraphic units
    bpy.types.Scene.em_list = prop.CollectionProperty(type = EMListItem)
    bpy.types.Scene.em_list_index = prop.IntProperty(name = "Index for my_list", default = 0)
    bpy.types.Scene.EM_file = StringProperty(
      name = "EM GraphML file",
      default = "",
      description = "Define the path to the EM GraphML file",
      subtype = 'FILE_PATH'
      )

def unregister():
#    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.em_list
    del bpy.types.Scene.em_list_index
    
    bpy.utils.unregister_class(EMListItem)
    bpy.utils.unregister_class(EM_UL_List)
    bpy.utils.unregister_class(EMToolsPanel)
    bpy.utils.unregister_class(EM_import_GraphML)    
    del bpy.types.Scene.EM_file

if __name__ == "__main__":
    register()