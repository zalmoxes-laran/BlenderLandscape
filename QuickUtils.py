import bpy
import time
import bmesh
from random import randint, choice
from .functions import *

class ToolsPanel3(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "BL"
    bl_label = "Quick Utils"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        obj = context.object
        scene = context.scene
        row = layout.row()
        self.layout.operator("center.mass", icon="DOT", text='Center of Mass')
        row = layout.row()
        self.layout.operator("local.texture", icon="TEXTURE", text='Local texture mode ON')
        row = layout.row()
        self.layout.operator("light.off", icon="LAMP_DATA", text='Deactivate lights')
        row = layout.row()
        self.layout.operator("create.personalgroups", icon="GROUP", text='Create per-object groups')
        row = layout.row()
        self.layout.operator("remove.alluvexcept1", icon="GROUP", text='Only UV0 will survive')
        row = layout.row()
        self.layout.operator("remove.fromallgroups", icon="LIBRARY_DATA_BROKEN", text='Remove from all groups')
        row = layout.row()
        self.layout.operator("multimaterial.layout", icon="IMGDISPLAY", text='Multimaterial layout')
        row = layout.row()
        self.layout.operator("lod0poly.reducer", icon="IMGDISPLAY", text='LOD0 mesh decimator')
        row = layout.row()
        row.label(text="Switch engine")
        self.layout.operator("activatenode.material", icon="PMARKER_SEL", text='Activate cycles nodes')
        self.layout.operator("deactivatenode.material", icon="PMARKER", text='De-activate cycles nodes')
        self.layout.operator("bi2cycles.material", icon="SMOOTH", text='Create cycles nodes')
        self.layout.operator("cycles2bi.material", icon="PMARKER", text='Cycles to BI')


class OBJECT_OT_lightoff(bpy.types.Operator):
    """Turn off light sensibility"""
    bl_idname = "light.off"
    bl_label = "Turn off light sensibility"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.context.scene.game_settings.material_mode = 'GLSL'
        bpy.context.scene.game_settings.use_glsl_lights = False
        return {'FINISHED'}

class OBJECT_OT_LOD0polyreducer(bpy.types.Operator):
    """Reduce the polygon number to a correct LOD0 set up"""
    bl_idname = "lod0poly.reducer"
    bl_label = "Reduce the polygon number to a correct LOD0 set up"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context = bpy.context

        selected_objs = context.selected_objects

        for obj in selected_objs:
            me = obj.data
            tot_poly = len(me.polygons)
            tot_area = areamesh(obj)
            final_poly = tot_area*1000
            if final_poly < tot_poly:
                ratio = final_poly/tot_poly
                print("ratio is "+ str(ratio))
                decimate_mesh(context,obj,ratio,'LOD0')

        return {'FINISHED'}

class OBJECT_OT_cycles2bi(bpy.types.Operator):
    """Convert cycles to bi"""
    bl_idname = "cycles2bi.material"
    bl_label = "Convert cycles to bi"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        bpy.context.scene.render.engine = 'BLENDER_RENDER'
        cycles2bi()

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
    
    
    
class OBJECT_OT_multimateriallayout(bpy.types.Operator):
    """Create multimaterial layout on selected mesh"""
    bl_idname = "multimaterial.layout"
    bl_label = "Create a multimaterial layout for selected meshe(s)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        start_time = time.time()
        totmodels=len(context.selected_objects)
        padding = 0.05
        #ob = bpy.context.object
        print("Found "+str(totmodels)+" models.")
        currentmod = 1
        for ob in context.selected_objects:
            start_time_ob = time.time()
            print("")
            print("***********************")
            print("I'm starting to process: "+ob.name+" model ("+str(currentmod)+"/"+str(totmodels)+")")
            print("***********************")
            print("")
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
                bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.01, user_area_weight=0.0, use_aspect=True)
#                bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=padding)
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
            print('>>> "'+ob.name+'" ('+str(currentmod)+'/'+ str(totmodels) +') object baked in '+str(time.time() - start_time_ob)+' seconds')
            currentmod += 1
        end_time = time.time() - start_time
        print(' ')
        print('<<<<<<< Process done >>>>>>')
        print('>>>'+str(totmodels)+' objects processed in '+str(end_time)+' seconds')
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>')       
        return {'FINISHED'}
