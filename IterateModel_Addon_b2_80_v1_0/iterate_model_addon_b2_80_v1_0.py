# ##### BEGIN GPL LICENSE BLOCK #####
#
# Render Rig for rendering a rig using custom bone curve objects as curves.
# Copyright (C) 2019 Juan Cardenas
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Iterate Model",
    "description": "Panel tools for easy duplication and organization of objects into collections",
    "author": "Juan Cardenas (JohnGDDR5)",
    "version": (1, 0), 
    "blender": (2, 80, 0),
    "location": "Preferences: 3D View > view3d.toggle_orbit_method",
    "warning": "In Development",
    "support": "COMMUNITY",
    "category": "Scene"
}

import bpy
        
from bpy.props import *
from math import pi, radians
from mathutils import Matrix, Vector, Euler
import decimal
import copy

#bpy.context.object.local_view_get()
#bpy.context.screen.areas[5].type
#bpy.context.screen.areas[5].spaces.active.lens
#bpy.context.screen.areas[5].spaces[0].lens

#bpy.context.screen.areas[5].spaces[0].local_view is not None


class ITERATE_MODEL_OT_SelectCollection(bpy.types.Operator):
    bl_idname = "iteratemodel.collection_ops"
    bl_label = "IterateModel Duplicating Operators"
    bl_description = "IterateModel Duplicating Operators"
    bl_options = {'UNDO',}
    type: bpy.props.StringProperty(default="DEFAULT")
    index: bpy.props.IntProperty(default=0, min=0)
    
    """
    @classmethod
    def poll(cls, context):
        return props.collection_parent is not None """
    
    def execute(self, context):
        scene = bpy.context.scene
        props = scene.IM_Props
        #props.group_name
        #inputs = context.preferences.inputs
        #bpy.context.preferences.inputs.view_rotate_method
        
        #collection_parent:
        #collection_active: 
        #collections:
            #collection:
            #object:
            #duplicates:
            #recent:
            
        #Select a collection 
        if self.type == "SELECT_COLLECTION":
            props.collection_parent = bpy.data.collections[self.index]
            
            colNew = bpy.data.collections.new(props.group_name)
            #Links colNew to collection_active
            props.collection_active = colNew
            props.collection_parent.children.link(colNew)
        
        #NOTE THIS HING BRUHHHHHHH
        
        #Create a new Collection Parent, link it to scene, and an Active Collection linked to Parent    
        if self.type == "NEW_COLLECTION":
            # Create a new collection and link it to the scene.
            colNew = bpy.data.collections.new("Collection")
            props.collection_parent = colNew
            scene.collection.children.link(colNew)
            
            #Creates new Group Collection
            colNew2 = bpy.data.collections.new(props.group_name)
            #Links colNew2 to collection_parent
            props.collection_active = colNew2
            props.collection_parent.children.link(colNew2)
            
        self.type == "DEFAULT"
        
        return {'FINISHED'}

class ITERATE_MODEL_OT_UIOperators(bpy.types.Operator):
    bl_idname = "iteratemodel.group_ops"
    bl_label = "IterateModel Duplicating Operators"
    bl_description = "IterateModel Duplicating Operators"
    bl_options = {'UNDO',}
    type: bpy.props.StringProperty(default="DEFAULT")
    index: bpy.props.IntProperty(default=0, min=0)
    
    @classmethod
    def poll(cls, context):
        scene = bpy.context.scene
        props = scene.IM_Props
        
        return props.collection_parent is not None
    
    def execute(self, context):
        scene = bpy.context.scene
        props = scene.IM_Props
        #props.group_name
        #inputs = context.preferences.inputs
        #bpy.context.preferences.inputs.view_rotate_method
        
        #collection_parent:
        #collection_active: 
        #collections:
            #collection:
            #object:
            #duplicates:
            #recent:
        
        #New Collection Group inside Parent Collection and set as Active Collection
        if self.type == "NEW_GROUP":
            if props.collection_parent is not None:
                colNew = bpy.data.collections.new(props.group_name)
                #Links colNew2 to collection_parent
                props.collection_active = colNew
                props.collection_parent.children.link(colNew)
        
        self.type == "DEFAULT"
        
        return {'FINISHED'}
        
class ITERATE_MODEL_OT_Duplicate(bpy.types.Operator):
    bl_idname = "iteratemodel.duplicating_ops"
    bl_label = "IterateModel Duplicating Operators"
    bl_description = "IterateModel Duplicating Operators"
    bl_options = {'UNDO',}
    type: bpy.props.StringProperty(default="DEFAULT")
    index: bpy.props.IntProperty(default=0, min=0)
    
    @classmethod
    def poll(cls, context):
        scene = bpy.context.scene
        props = scene.IM_Props
        
        return props.collection_parent is not None and props.collection_active is not None
    
    def execute(self, context):
        scene = bpy.context.scene
        props = scene.IM_Props
        #inputs = context.preferences.inputs
        #bpy.context.preferences.inputs.view_rotate_method
        
        #collection_parent:
        #collection_active: 
        #collections:
            #collection:
            #object:
            #duplicates:
            #recent:
                        
        if self.type == "DUPLICATE":
            
            if props.collection_parent is not None:
                #If there is no collection in collection_active
                if props.collection_active is None:
                    colNew = bpy.data.collections.new(props.group_name)
                    #Sets collection_active as colNew
                    props.collection_active = colNew
                    #Links colNew to collection_parent
                    props.collection_parent.children.link(colNew)
                
                previous_active = bpy.context.active_object
                
                previous_selected = bpy.context.selected_objects
                
                bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0.0, 0.0, 0.0), "orient_type":'GLOBAL'})

                
                #bpy.ops.object.mode_set(mode="OBJECT")
                
                """
                ob = bpy.context.object
                if not ob.select_get():
                    ob.select_set(True) """
                
                #Iterates through all selected objects
                for i in enumerate(previous_selected):
                    existingCol = None
                    existingColName = ""
                    
                    ob = bpy.context.selected_objects[i[0]]
                    #Unselects object
                    ob.select_set(False)
                    
                    for j in enumerate(props.collections):
                        #If object is already registered in props.collections:object
                        if i[1] == j[1].object:
                            existingCol = j[0]
                            
                            """
                            #Duplicates object
                            ob_copy = i[1].data.copy()
                            ob = bpy.data.objects.new(i[1].name, ob_copy)
                            #Links the duplicated object in the scene
                            j[1].collection.objects.link(ob) """
                            #scene.collection.objects.link(ob)
                            
                            #Unlinks duplicate from all collections it is linked to
                            for k in enumerate(ob.users_collection):
                                k[1].objects.unlink(ob)
                            
                            #Links duplicated object to existing collection
                            j[1].collection.objects.link(ob)
                            print("For: 1")
                            break
                    
                    print("existingCol: %s" % (str(existingCol)))
                    
                    if existingCol == None:
                        colNew2 = bpy.data.collections.new(i[1].name)
                        #Links colNew2 to collection_parent
                        props.collection_active.children.link(colNew2)
                        #Sets collection_active as colNew2
                        
                        """
                        #Duplicates object
                        ob_copy = i[1].data.copy()
                        ob = bpy.data.objects.new(i[1].name, ob_copy) 
                        #Links the duplicated object in the scene
                        colNew2.objects.link(ob) """
                        
                        #Unlinks duplicate from all collections it is linked to
                        for k in enumerate(ob.users_collection):
                            k[1].objects.unlink(ob)
                        
                        #Links duplicate to colNew2 collection
                        colNew2.objects.link(ob)
                        
                        #Adds scene.IM_Props collection
                        propsCol = props.collections.add()
                        propsCol.collection = colNew2
                        propsCol.object = i[1]#i[1]#bpy.context.selected_objects[existinOb]
                        
                        #Hides Collection
                        propsCol.collection.hide_viewport = True
                        
                        print("If: None")
                        
                    #Unselects duplicated object
                    ob.select_set(False)
                    
                    #bpy.context.active_object = previous_active
                    previous_active.select_set(True)
                    
                    bpy.context.view_layer.objects.active = previous_active
                        
        self.type == "DEFAULT"
        
        return {'FINISHED'}
        
class ITERATE_MODEL_OT_Debugging(bpy.types.Operator):
    bl_idname = "iteratemodel.clear_collections"
    bl_label = "IterateModel Duplicating Operators"
    bl_description = "IterateModel Duplicating Operators"
    bl_options = {'UNDO',}
    type: bpy.props.StringProperty(default="DEFAULT")
    #index: bpy.props.IntProperty(default=0, min=0)
    
    def execute(self, context):
        scene = bpy.context.scene
        props = scene.IM_Props
        #inputs = context.preferences.inputs
        #bpy.context.preferences.inputs.view_rotate_method
        
        #collection_parent:
        #collection_active: 
        #collections:
            #collection:
            #object:
            #duplicates:
            #recent:
                        
        if self.type == "DELETE":
            
            if props.collection_parent is not None:
                if props.collection_active is not None:
                    removedObjects = 0
                    removedCol = 0
                    for i in enumerate(reversed(props.collections)):
                        if i[1].collection is not None:
                            for j in i[1].collection.objects:
                                removedObjects += 1
                                i[1].collection.objects.unlink(j)
                            removedCol += 1
                            #Removes collection, but not other links of it incase the user linked it
                            bpy.data.collections.remove(i[1].collection, do_unlink=True)
                            
                        props.collections.remove(len(props.collections)-1)
                    colNames = [props.collection_parent.name, props.collection_active.name]
                    
                    reportString = "Removed: [%s, %s] & %d Objects & %d Collection Groups" % (colNames[0], colNames[1], removedObjects, removedCol)
                    
                    bpy.data.collections.remove(props.collection_active, do_unlink=True)
                    bpy.data.collections.remove(props.collection_parent, do_unlink=True)
                    
                    print(reportString)
                    self.report({'INFO'}, reportString)
                else:
                    #Removes scene.IM_Props.collections
                    for i in enumerate(reversed(props.collections)):
                        props.collections.remove(len(props.collections)-1)
                    
                    reportString = "Removed: [%s] Collection" % (props.collection_parent.name)
                    
                    #Removes collection, but not other links of it incase the user linked it
                    bpy.data.collections.remove(props.collection_parent, do_unlink=True)
                    
                    print(reportString)
                    self.report({'INFO'}, reportString)
            else:
                #Removes scene.IM_Props.collections
                for i in enumerate(reversed(props.collections)):
                    props.collections.remove(len(props.collections)-1)
                    
                reportString = "collection_parent is None"
                
                print(reportString)
                self.report({'INFO'}, reportString)
                
        self.type == "DEFAULT"
        
        return {'FINISHED'}

class ITERATE_MODEL_UL_items(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        scene = bpy.context.scene
        data = bpy.data
        props = scene.IM_Props
        
        #active = props.RIA_ULIndex
        IMCollect = props.collections
        
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            info = '%d: %s' % (index, item.object.name)
            if len(IMCollect) > 0:
                row.label(text=info)
            else:
                row.label(text="No Iterations Here")
            """
            if len(IMCollect) > 0:
                if active == index:
                    row.operator("resswitch.res_button_active", icon="RADIOBUT_ON", text="", emboss=False).index = index
                else:
                    row.operator("resswitch.res_button_active", icon="RADIOBUT_OFF", text="", emboss=False).index = index
                    
                #RS_ToggleEdit Boolean Button to edit ResButtons
                if props.RS_ToggleEdit == False:
                    #info = 'Item "%s" removed from scene' % (item.armature.name)
                    option = ""
                    if props.RS_MenuUIOptions[0] == True:
                        option = '%d: ' % (index)
                        
                    option += '%dx%d' % (item.resolution[0], item.resolution[1])
                    
                    if props.RS_MenuUIOptions[1] == True:
                        option += ' (%s)' % (item.aspectRatio)#aspRatio
                        
                    row.operator("resswitch.res_button", text=option).index = index
                    
                else:
                    row.prop(item, "resolution", index=0, text="X")
                    row.prop(item, "resolution", index=1, text="Y") """

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            #row.prop(item, "resolution", text="", emboss=False, icon="NONE")

    def invoke(self, context, event):
        pass

class ITERATE_MODEL_MT_CollectionsMenu(bpy.types.Menu):
    bl_idname = "ITERATE_MODEL_MT_CollectionsMenu"
    bl_label = "Select a Collection"
    bl_description = "Menu That Displays all Collections in Scene"
    
    # here you specify how they are drawn
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        data = bpy.data
        props = scene.IM_Props
        
        #collection_parent:
        #collection_active: 
        #collections:
        
        col = layout.column()
        
        row = col.row(align=True)
        
        if len(bpy.data.collections) > 0:
            for i in enumerate(bpy.data.collections):
                button = row.operator("iteratemodel.collection_ops", text=i[1].name)
                button.type = "SELECT_COLLECTION"
                button.index = i[0]
                
                row = col.row(align=True)
        else:
            #NEW_COLLECTION
            button = row.operator("iteratemodel.collection_ops", text=i[1].name)
            button.type = "NEW_COLLECTION"
            #bpy.data.collections.new("Boi") 
        #row.prop(self, "ui_tab", expand=True)#, text="X")

class ITERATE_MODEL_PT_CustomPanel1(bpy.types.Panel):
    #A Custom Panel in Viewport
    bl_idname = "ITERATE_MODEL_PT_CustomPanel1"
    bl_label = "Iterate Model"
    bl_space_type = "VIEW_3D"
    bl_region_type = 'UI'
    #bl_context = "output"
    bl_category = "Iterate Model"
    
    # draw function
    def draw(self, context):
                 
        layout = self.layout
        scene = context.scene
        props = scene.IM_Props
        
        #active = props.RIA_ULIndex
        #riaCollect = scene.RIA_Collections
        
        #global aspect_ratios#, active
        #active = props.RIA_ULIndex
        #riaCollect = scene.RIA_Collections
        #
        #Layout Starts
        col = layout.column()
        
        row = col.row(align=True)
        row.label(text="Parent Collection:")
        
        row = col.row(align=True)
        if props.collection_parent is None:
            #If a collection exists
            if len(bpy.data.collections) > 0:
                #row = col.row(align=True)
                row.menu("ITERATE_MODEL_MT_CollectionsMenu", icon="GROUP", text="Select Collection")
                row.operator("iteratemodel.collection_ops", icon="ADD", text="").type = "NEW_COLLECTION"
            else:
                row.operator("iteratemodel.collection_ops", icon="ADD", text="Add Collection").type = "NEW_COLLECTION"
        else:
            
            #row = col.row(align=True)
            row.prop(scene.IM_Props.collection_parent, "name", icon="GROUP", text="")
            row.operator("iteratemodel.collection_ops", icon="ADD", text="").type = "NEW_COLLECTION"
            
            row = col.row(align=True)
            row.label(text="Active Collection:")
            
            row = col.row(align=True)
            row.prop(scene.IM_Props.collection_active, "name", icon="GROUP", text="")
            row.operator("iteratemodel.group_ops", icon="ADD", text="").type = "NEW_GROUP"
            
        #Duplicate Button
        row = col.row(align=True)
        row.operator("iteratemodel.duplicating_ops", text="Iterate").type = "DUPLICATE"
        
        row = col.row(align=True)
        row.label(text="Iterations:")
        
        row = col.row(align=True)
        row.template_list("ITERATE_MODEL_UL_items", "custom_def_list", scene.IM_Props, "collections", scene.IM_Props, "IM_ULIndex", rows=3)
        
        row = col.row(align=True)
        row.label(text="Debug Ops:")
        
        row = col.row(align=True)
        row.operator("iteratemodel.clear_collections", text="Delete All").type = "DELETE"
        
        #End of CustomPanel

"""
class ITERATE_MODEL_Collections(bpy.types.PropertyGroup):
    #resolution: bpy.props.IntVectorProperty(name="ResolutionVector", default=(1080,1080), size=2, min=4)#, update=AspectRatioUpdate)
    collection: bpy.props.PointerProperty(name="Added Collections to List", type=bpy.types.Collection)
    #aspectRatio: bpy.props.StringProperty(name="Aspect Ratio", default="1:1")
    #bool: bpy.props.BoolProperty(name="Active Bool", default=False)
    empty_display_size: bpy.props.FloatProperty(name="Float", description="", default= 5.0, min=0.01, update=RIA_Update_empty_display_size)
    use_empty_image_alpha: bpy.props.BoolProperty(name="Boolean", description="", default=False, update=RIA_Update_use_empty_image_alpha)
    alpha: bpy.props.FloatProperty(name="Float", description="", default= 1.0, min=0, max=1)
    empty_image_offset: bpy.props.FloatVectorProperty(name="FloatVector", description = "", size=2, default=(-0.5,-0.5))
    
    disMode1 =  ["List: Allows User most control of how many ResButtons display in the Tab", "Extended: Displays all of the ResButtons in the Tab", "Dropdown: Displays only one ResButton at a time, and adds a dropdown menu to select other ResButtons. The most condensed Display Mode"]
    empty_image_depth: bpy.props.EnumProperty(name="Display Mode", items= [("DEFAULT", "Default", disMode1[0]), ("FRONT", "Front", disMode1[1]), ("BACK", "Back", disMode1[2])], description="Display Mode of ResButtons", default="DEFAULT")
    empty_image_side: bpy.props.EnumProperty(name="Display Mode", items= [("BOTH", "Both", disMode1[0]), ("FRONT", "Front", disMode1[1]), ("BACK", "Back", disMode1[2])], description="Display Mode of ResButtons", default="BOTH")
    show_empty_image_orthographic: bpy.props.BoolProperty(name="Boolean", description="", default=True)
    show_empty_image_perspective: bpy.props.BoolProperty(name="Boolean", description="", default=True) """
    
class ITERATE_MODEL_CollectionObjects(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="", default="")
    collection: bpy.props.PointerProperty(name="Added Collections to List", type=bpy.types.Collection)
    object: bpy.props.PointerProperty(name="Object", type=bpy.types.Object)
    duplicates: bpy.props.IntProperty(name="Int", description="", default= 0, min=0)
    recent: bpy.props.IntProperty(name="Int", description="", default= 0, min=0)
    #custom: bpy.props.IntProperty(name="Int", description="", default= 0, min=0)
    
class ITERATE_MODEL_Props(bpy.types.PropertyGroup):
    collection_parent: bpy.props.PointerProperty(name="Collection to add Groups to", type=bpy.types.Collection)
    collection_active: bpy.props.PointerProperty(name="Collection to add Collections for Object duplicates", type=bpy.types.Collection)
    collections: bpy.props.CollectionProperty(type=ITERATE_MODEL_CollectionObjects)
    IM_ULIndex: bpy.props.IntProperty(name="Int", description="UI List Index", default= 0, min=0)
    group_name: bpy.props.StringProperty(default="Group")

#Classes that are registered
classes = (
    ITERATE_MODEL_OT_SelectCollection,
    ITERATE_MODEL_OT_UIOperators,
    ITERATE_MODEL_OT_Duplicate,
    ITERATE_MODEL_OT_Debugging,
    
    ITERATE_MODEL_UL_items,
    ITERATE_MODEL_MT_CollectionsMenu,
    
    ITERATE_MODEL_PT_CustomPanel1,
    
    ITERATE_MODEL_CollectionObjects,
    ITERATE_MODEL_Props,
)

def register():
    #ut = bpy.utils
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    
    #bpy.types.Scene.IM_Collections = bpy.props.CollectionProperty(type=REF_IMAGEAID_Collections)
    bpy.types.Scene.IM_Props = bpy.props.PointerProperty(type=ITERATE_MODEL_Props)
    
def unregister():
    #ut = bpy.utils
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    
    del bpy.types.Scene.IM_Props
    
if __name__ == "__main__":
    register()
