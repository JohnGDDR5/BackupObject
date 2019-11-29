# ##### BEGIN GPL LICENSE BLOCK #####
#
# Iterate Objects is a workflow addon for easily creating duplicates of objects you're working on and sending them to a unique collection. 
# A kind of version-control system where duplicates function as "snapshots" of the object to be able to have a backup when doing destructive modeling on a mesh object.
#
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
    "name": "Iterate Objects",
    "description": "Workflow Addon for easy duplication and organization of objects into collections, to work as \"backups\" for destructive modeling.",
    "author": "Juan Cardenas (JohnGDDR5)",
    "version": (1, 0), 
    "blender": (2, 80, 0),
    "location": "3D View > Side Bar > Iterate Objects",
    "warning": "In Development",
    "support": "COMMUNITY",
    "category": "Scene"
}

import bpy
        
from bpy.props import *
#from math import pi, radians
#from mathutils import Matrix, Vector, Euler
#import decimal
#import copy
    
#Takes in an object as parameter, and returns a string of variable "icon"
def objectIcon(object):
    scene = bpy.context.scene
    data = bpy.data
    props = scene.IM_Props
    
    #icons = ["OUTLINER_OB_EMPTY", "OUTLINER_OB_MESH", "OUTLINER_OB_CURVE", "OUTLINER_OB_LATTICE", "OUTLINER_OB_META", "OUTLINER_OB_LIGHT", "OUTLINER_OB_IMAGE", "OUTLINER_OB_CAMERA", "OUTLINER_OB_ARMATURE", "OUTLINER_OB_FONT", "OUTLINER_OB_SURFACE", "OUTLINER_OB_SPEAKER", "OUTLINER_OB_FORCE_FIELD", "OUTLINER_OB_GREASEPENCIL", "OUTLINER_OB_LIGHTPROBE"]
    #Object Type
    
    icon = "QUESTION"
    
    dictionary = {
        "MESH": "OUTLINER_OB_MESH",
        "EMPTY": "EMPTY",
        "CAMERA": "OUTLINER_OB_CAMERA",
        "CURVE": "OUTLINER_OB_CURVE",
        "SURFACE": "OUTLINER_OB_SURFACE",
        "META": "OUTLINER_OB_META",
        "FONT": "OUTLINER_OB_FONT",
        "GPENCIL": "OUTLINER_OB_GREASEPENCIL",
        "ARMATURE": "OUTLINER_OB_ARMATURE",
        "LATTICE": "OUTLINER_OB_LATTICE",
        "LIGHT": "OUTLINER_OB_LIGHT",
        "LIGHT_PROBE": "OUTLINER_OB_LIGHTPROBE",
        "SPEAKER": "OUTLINER_OB_SPEAKER",
    }
    
    #If there is an object to see if it has a type
    if object is not None:
        type = object.type
    
        icon = dictionary.get(str(type), "QUESTION")
        
        if icon == "EMPTY":
            if object.empty_display_type != "IMAGE":
                icon = "OUTLINER_OB_EMPTY"
            elif object.empty_display_type == "IMAGE":
                icon = "OUTLINER_OB_IMAGE"
            elif object.field.type != "NONE":
                icon = "OUTLINER_OB_FORCE_FIELD"
                
    return icon

class ITERATE_OBJECTS_OT_SelectCollection(bpy.types.Operator):
    bl_idname = "iterate_objects.select_collection"
    bl_label = "Select Collection"
    bl_description = "Set collection as Parent or Active collection"
    bl_options = {'UNDO',}
    type: bpy.props.StringProperty(default="DEFAULT")
    index: bpy.props.IntProperty(default=0, min=-1)
    
    def execute(self, context):
        scene = bpy.context.scene
        props = scene.IM_Props
                
        if self.type == "SELECT_ACTIVE":
            props.collection_active = bpy.data.collections[self.index]
            
        self.type == "DEFAULT"
        
        return {'FINISHED'}

class ITERATE_OBJECTS_OT_GroupOperators(bpy.types.Operator):
    bl_idname = "iterate_objects.collection_ops"
    bl_label = "New Iterate Objects Parent Collection"
    bl_description = "Creates a new Collection to use as the Parent Collection of new Iterate Objects\' collections"
    bl_options = {'UNDO',}
    type: bpy.props.StringProperty(default="DEFAULT")
    index: bpy.props.IntProperty(default=0, min=0)
    
    def execute(self, context):
        scene = bpy.context.scene
        props = scene.IM_Props
        
        #New Collection Group inside Parent Collection and set as Active Collection
        if self.type == "NEW_GROUP":
            
            colNew = bpy.data.collections.new(props.group_name)
            #Links colNew2 to collection_active
            props.collection_active = colNew
            
            #Links new collection to Master_Collection
            bpy.context.scene.collection.children.link(colNew)
            
            #Note for For Loop Bellow: For every props.collections[].collection, create a new collection and set that as the pointer to the collections[].collection so each object gets a new collection
            
            #Removes collections from all IM_Props.collections.collection
            for i in enumerate(props.collections):
                i[1].collection = None
                
        self.type == "DEFAULT"
        
        return {'FINISHED'}
        
class ITERATE_OBJECTS_OT_Duplicate(bpy.types.Operator):
    bl_idname = "iterate_objects.duplicating_ops"
    bl_label = "Duplicates active objects"
    bl_description = "Duplicates active objects and sends them to the their own Iterate Object collection. Creates a new Iterate Object and collection for objects without an Iterate Object."
    bl_options = {'UNDO',}
    
    type: bpy.props.StringProperty(default="DEFAULT")
    index: bpy.props.IntProperty(default=0, min=0)
    
    @classmethod
    def poll(cls, context):
        scene = bpy.context.scene
        props = scene.IM_Props
        
        #return props.collection_parent is not None and props.collection_active is not None
        return True#props.collection_active is not None
    
    def execute(self, context):
        scene = bpy.context.scene
        props = scene.IM_Props
        #inputs = context.preferences.inputs
        #bpy.context.preferences.inputs.view_rotate_method
        
        if self.type == "DUPLICATE":
            
            #prev_mode saves the previous mode of the object
            prev_mode = str(bpy.context.object.mode)
            
            #.mode_set() operator changes the mode of the object to "OBJECT" mode for the .duplicate_move() operator to work
            if prev_mode != "OBJECT":
                bpy.ops.object.mode_set(mode="OBJECT")
            
            #if props.collection_parent is not None:
                #Was here before
                
            #If there is no collection in collection_active, create one
            if props.collection_active is None:
                colNew = bpy.data.collections.new(props.group_name)
                #Sets collection_active as colNew
                props.collection_active = colNew
                
                bpy.context.scene.collection.children.link(colNew)
            
            if len(bpy.context.selected_objects) > 0:
                
                previous_active = bpy.context.active_object
                
                previous_selected = bpy.context.selected_objects
                
                #Duplicates selected objects in previous_selected
                bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0.0, 0.0, 0.0), "orient_type":'GLOBAL'})
                
                #Iterates through all selected objects
                for i in enumerate(previous_selected):
                    existingCol = None
                    existingColName = ""
                    #lastOb = None
                    #All objects in previous_selected have been deselected, and all duplicated objects have been selected in "ob"
                    ob = bpy.context.selected_objects[i[0]]
                    
                    #Unlinks duplicate from all collections it is linked to
                    for k in enumerate(ob.users_collection):
                        k[1].objects.unlink(ob)
                    
                    #Iterates through all IM_Props.collections
                    for j in enumerate(props.collections):
                        #If object is already registered in props.collections:object
                        if i[1] == j[1].object:
                            existingCol = j[1]
                            
                            #If IM_Props.collections.collection is None (Ex. when a New Group collection is made)
                            if j[1].collection is None:
                                colNew = bpy.data.collections.new(i[1].name)
                                #Sets IM_Props.collections' collection
                                j[1].collection = colNew
                                #Hides new collection
                                colNew.hide_viewport = True
                                
                                props.collection_active.children.link(colNew)
                            
                            #Links duplicated object to existing collection
                            j[1].collection.objects.link(ob)
                            #j[1].duplicates += 1
                            j[1].name = j[1].collection.name
                            
                            print("For: 1")
                            break
                    
                    print("existingCol: %s" % (str(existingCol)))
                    
                    #If object wasn't found inside props.collections as .object
                    if existingCol == None:
                        #Checks how you want the new Collection name for new Iteration Object to be
                        if props.group_name_use == True:
                            new_group_name = i[1].name
                        else:
                            new_group_name = props.group_name
                        
                        colNew2 = bpy.data.collections.new(new_group_name)
                        #Links colNew2 to collection_active
                        props.collection_active.children.link(colNew2)
                        
                        #Links duplicate to colNew2 collection
                        colNew2.objects.link(ob)
                        
                        #Adds scene.IM_Props collection
                        propsCol = props.collections.add()
                        propsCol.collection = colNew2
                        propsCol.object = i[1]#i[1]#bpy.context.selected_objects[existinOb]
                        #propsCol.duplicates += 1
                        #Makes the name of 
                        propsCol.name = colNew2.name
                        #Adds the index of the order of created
                        propsCol.recent += len(props.collections)
                        #Custom Index will be in order if it is a new props.collection
                        propsCol.custom += len(props.collections)
                        
                        #Adds icon name to props.collection object to display in Viewport
                        propsCol.icon = objectIcon(propsCol.object)
                        
                        #Hides Collection
                        propsCol.collection.hide_viewport = True
                        
                        existingCol = propsCol
                    
                    """
                    #Doesn't Temporarily hides in the viewport
                    ob.hide_set(not props.hide_types[0])
                    #Doesn't Hide object from rendering
                    ob.hide_render = not props.hide_types[1]
                    #Doesn't Hide object from rendering
                    ob.hide_viewport = not props.hide_types[2] """
                    
                    #Unselects duplicated object
                    ob.select_set(False)
                    #Selects previously selected object
                    previous_selected[i[0]].select_set(True)
                    
                #selects previously active object
                previous_active.select_set(True)
                #Sets previously active object as active
                bpy.context.view_layer.objects.active = previous_active
                    
            else:
                reportString = "No Objects Selected. 0 Objects Duplicated"
                
                #print(reportString)
                self.report({'INFO'}, reportString)
            
            #Calls the update function ListOrderUpdate to change locations of props.collections
            ListOrderUpdate(self, context)
            
            #Sets IM_ULIndex as index of previously active context object
            if props.index_to_new == True:
            
                for i in enumerate(props.collections):
                    if i[1].object == previous_active:
                        props.IM_ULIndex = i[0]
                        break
            
            #Changes the Mode of the active object back to its previous mode.
            bpy.ops.object.mode_set(mode=prev_mode)
                        
        self.type == "DEFAULT"
        
        return {'FINISHED'}
    
#There was an Attempt 1
#For next try, just .move() every Iteration Object without a Collection or Object to the end of the props.collections list and .remove() them from there.
"""
class ITERATE_OBJECTS_OT_Cleaning(bpy.types.Operator):
    bl_idname = "iterate_objects.cleaning_ops"
    bl_label = "Removes Iteration Objects that don't have an Object or Collection to point to"
    bl_description = "Duplicates active objects and sends them to the Active Collection"
    bl_options = {'UNDO',}
    
    type: bpy.props.StringProperty(default="DEFAULT")
    index: bpy.props.IntProperty(default=0, min=0)
    
    def execute(self, context):
        scene = bpy.context.scene
        props = scene.IM_Props
        
        if self.type == "DELETE":
            #Gets previous length of props.collections
            len_previous = len(props.collections)
            
            if props.collection_active is not None:
                no_objects = 0
                no_collections = 0
                
                print("Total Objects Before: %d" % (len(props.collections)))
                
                #listed = reversed(list(enumerate(props.collections)))
                list_2 = props.collections[::]
                
                for i in enumerate(list_2) :#enumerate(props.collections):
                    #Will remove any Iteration Object without a collection or object
                    #if i[1].collection == None or i[1].object == None:
                    #This gets new index of the Iteration Object when others have been deleted
                    len_new = len(props.collections)
                    index_new = i[0]-(len_previous-len_new)
                    
                    if i[1].object != None:
                        print_ob = str(i[1].object.name)
                    else:
                        print_ob = "[None]"
                        no_objects += 1
                        
                    if i[1].collection != None:
                        print_col = str(i[1].collection.name)
                    else:
                        print_col = "[None]"
                        no_collections += 1
                    
                    print("%d. New Index: %d; Object: %s; Collection: %s" % (i[0], index_new, print_ob, print_col))
                    
                    if i[1].collection == None or i[1].object == None:
                        bpy.context.scene.IM_Props.collections.remove(index_new)
                        
                print("Total Objects After: %d" % (len(props.collections)))
                #Displays how many Iteration Objects don't have Objects or Collections
                print("No Objects: %d; No Collections: %d" % (no_objects, no_collections))
                    
        self.type == "DEFAULT"
        
        return {'FINISHED'} """
        
class ITERATE_OBJECTS_OT_Cleaning(bpy.types.Operator):
    bl_idname = "iterate_objects.cleaning_ops"
    bl_label = "Cleaning/Deleting Operators "
    bl_description = "Cleaning & Deleting Iterate Objects & Objects inside their collections."
    bl_options = {'UNDO',}
    
    type: bpy.props.StringProperty(default="DEFAULT")
    index: bpy.props.IntProperty(default=0, min=0)
    
    def execute(self, context):
        scene = bpy.context.scene
        props = scene.IM_Props
        
        #Deletes Objects inside Iterate Object collections, except most recent ammounts given by user
        if self.type == "CLEAN_1":
        
            #Gets previous length of props.collections
            len_previous = len(props.collections)
            
            len_diff = 0
            
            before = list(props.collections)
            #col_name = "[No Collection]"
            
            affected_collections = 0
            
            removed_total = 0
            
            #Goes through every Iterate Object
            for i in enumerate(props.collections):
                #If there is a collection its pointing to
                if i[1].collection != None:
                    #name of collection
                    col_name = str(i[1].collection.name)
                    
                    #gets name of pointed object
                    if i[1].object != None:
                        ob_name = str(i[1].object.name)
                    else:
                        ob_name = "[No Object]"
                        
                    list_before = i[1].collection.objects[:-props.clean_leave]
                    #Everyithing but the last # of objects from props.clean_leave integer
                    list_rev = reversed(list(enumerate(list_before)))
                    
                    if len(list_before) > props.clean_leave:
                        len_prev = len(i[1].collection.objects)
                        
                        removed = 0
                        
                        for j in list_rev:
                            bpy.data.objects.remove(j[1])
                            removed += 1;
                            
                        removed_total += removed
                        
                        affected_collections += 1
                            
                        #print("Index [%d]: Prev_Len: %d, Removed %d, [Object: %s; Collection: %s ]" % (i[0], len_prev, removed, ob_name, col_name))
                    else:
                        pass
                else:
                    pass
            
            #Prints the last ammount of different Iterate Objects calculated
            #print("Removed: ( %d/%d ) Iterate Objects \n" % (len_diff, len_previous))
            
            reportString = "Removed: %d Objects from %d Iterate Objects Collections" % (removed_total, affected_collections)
        
        #Deletes Iterate Objects without an Object or Collection pointer
        elif self.type == "CLEAN_2":
        
            #Gets previous length of props.collections
            len_previous = len(props.collections)
            
            len_diff = 0
            
            for i in reversed(list(enumerate(props.collections))):
                #print(" i : " + str(i))
                #if len(i[1].collection.objects) == 0:
                if i[1].object == None or i[1].collection == None:
                    #ob_name = ""
                    if i[1].object != None:
                        ob_name = str(i[1].object.name)
                    else:
                        ob_name = "[No Collection]"
                    #else:
                    if i[1].collection != None:
                        col_name = str(i[1].collection.name)
                    else:
                        col_name = "[No Collection]"
                        
                    print("Removed [%d]: [Object: %s; Collection: %s ]" % (i[0], ob_name, col_name))
                    
                    bpy.context.scene.IM_Props.collections.remove(i[0])
            
            #Prints the last ammount of different Iterate Objects calculated
            #print("Removed: ( %d/%d ) Iterate Objects \n" % (len_diff, len_previous))
            
            reportString = "Removed: ( %d/%d ) Iterate Objects that were empty" % (len_diff, len_previous)
            
        print(reportString + "\n")
        
        self.report({'INFO'}, reportString)
            
        self.type == "DEFAULT"
        
        return {'FINISHED'}

class ITERATE_OBJECTS_OT_Removing(bpy.types.Operator):
    bl_idname = "iterate_objects.removing_ops"
    bl_label = "Remove all but the ammount the user inputs for all Iterate Objects"
    bl_description = "Duplicates active objects and sends them to the Active Collection"
    bl_options = {'UNDO',}
    
    type: bpy.props.StringProperty(default="DEFAULT")
    index: bpy.props.IntProperty(default=0, min=0)
    
    def execute(self, context):
        scene = bpy.context.scene
        props = scene.IM_Props
        
        if self.type == "PRINT":
            #Gets previous length of props.collections
            len_previous = len(props.collections)
            
            before = list(props.collections)
            
            for i in reversed(list(enumerate(before))):
                if len(i[1].collection.objects) == 1:
                    print("before[i[0]]: [%d]; Object.name: %s" % (i[0], before[i[0]].object.name))
                    del before[i[0]]
                    
        #Prints the Iterate Objects with 1 or less objects
        elif self.type == "PRINT_DIFFERENT_1":
            #Gets previous length of props.collections
            len_previous = len(props.collections)
            
            len_diff = 0
            
            #before = list(props.collections)
            print("Iterate Objects with 1 Object or Less in .Collection: ")
            
            for i in enumerate(props.collections):
                #Checks if i[1] has an object for a name
                if i[1].object != None:
                    ob_name = i[1].object.name
                else:
                    ob_name = "[No Object]"
                    
                col_name = "[No Collection]"
                objects = 0
                    
                #If there is a collection pointer
                if i[1].collection != None:
                    objects = len(i[1].collection.objects)
                    #Checks if there is 1 or less objects in the collection
                    if objects <= 1:
                        #Sets the col_name variable to collection name
                        col_name = i[1].collection.name
                        len_diff += 1
                #else:
                #    col_name = "[No Collection]"
                    
                if objects <= 1:
                    print("Index[%d] (Objects: %d) [Object: %s; Collection: %s ]" % (i[0], objects, ob_name, col_name))
                
            #Prints the last ammount of different Iterate Objects calculated
            print("Different: ( %d/%d ) Iterate Objects \n" % (len_diff, len_previous))
            
        #Fake "Deletes" Iterate Objects without an Object or Collection pointer
        elif self.type == "CLEAN_TEST":
        
            #Gets previous length of props.collections
            len_previous = len(props.collections)
            
            len_diff = 0
            
            before = list(props.collections)
            
            for i in reversed(list(enumerate(before))):
                if i[1].object == None or i[1].collection == None:
                    #ob_name = ""
                    if i[1].object != None:
                        ob_name = str(i[1].object.name)
                    else:
                        ob_name = "[No Collection]"
                    #else:
                    if i[1].collection != None:
                        col_name = str(i[1].collection.name)
                    else:
                        col_name = "[No Collection]"
                        
                    print("Removed [%d]: [Object: %s; Collection: %s ]" % (i[0], ob_name, col_name))
                    
                    del before[i[0]]
                    
            print("Before: "+str(before[::]))
            
            #Prints the last ammount of different Iterate Objects calculated
            print("Removed: ( %d/%d ) Iterate Objects \n" % (len_diff, len_previous))
            
        self.type == "DEFAULT"
        
        return {'FINISHED'}
        
class ITERATE_OBJECTS_OT_Debugging(bpy.types.Operator):
    bl_idname = "iterate_objects.debug"
    bl_label = "Iterate Objects Debugging Operators"
    bl_description = "To assist with debugging and development"
    bl_options = {'UNDO',}
    type: bpy.props.StringProperty(default="DEFAULT")
    #index: bpy.props.IntProperty(default=0, min=0)
    
    def execute(self, context):
        scene = bpy.context.scene
        props = scene.IM_Props
        
        #Mass deletion of every Iteration Object & their collections and objects inside them
        if self.type == "DELETE_NUKE":
            
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
                    
                colNameActive = props.collection_active.name
                    
                reportString = "Removed: [%s] & %d Objects & %d Collection Groups" % (colNameActive, removedObjects, removedCol)
                
                bpy.data.collections.remove(props.collection_active, do_unlink=True)
                
                print(reportString)
                self.report({'INFO'}, reportString)
            else:
                #Removes scene.IM_Props.collections
                for i in enumerate(reversed(props.collections)):
                    props.collections.remove(len(props.collections)-1)
                
            print(reportString)
            self.report({'INFO'}, reportString)
                
        elif self.type == "PRINT_1":
            no_objects = 0
            no_collections = 0
            
            for i in enumerate(props.collections):
                if i[1].object != None:
                    print_ob = str(i[1].object.name)
                else:
                    print_ob = "[None]"
                    no_objects += 1
                    
                if i[1].collection != None:
                    print_col = str(i[1].collection.name)
                else:
                    print_col = "[None]"
                    no_collections += 1
                
                print("%d. Object: %s, Collection: %s" % (i[0], print_ob, print_col))
                
            print("Total Objects: %d" % (len(props.collections)))
            #Displays how many Iteration Objects don't have Objects or Collections
            print("No Objects: %d; No Collections: %d" % (no_objects, no_collections))
        
        #Adds 3 Iterate Objects with missing Objects & Collections for testing.
        elif self.type == "TESTING":
            
            ob_1 = props.collections.add()
            ob_1.collection = bpy.data.collections[0]
            
            ob_2 = props.collections.add()
            ob_2.object = bpy.data.objects[0]
            
            ob_3 = props.collections.add()
            print("Added 3 Iterate Objects.")
            
        #Copied from .remove_ops operator before.
        elif self.type == "PRINT":
            #Gets previous length of props.collections
            len_previous = len(props.collections)
            
            before = list(props.collections)
            
            for i in reversed(list(enumerate(before))):
                if len(i[1].collection.objects) == 1:
                    print("before[i[0]]: [%d]; Object.name: %s" % (i[0], before[i[0]].object.name))
                    del before[i[0]]
                    
        #Prints the Iterate Objects with 1 or less objects
        elif self.type == "PRINT_DIFFERENT_1":
            #Gets previous length of props.collections
            len_previous = len(props.collections)
            
            len_diff = 0
            
            #before = list(props.collections)
            print("Iterate Objects with 1 Object or Less in .Collection: ")
            
            for i in enumerate(props.collections):
                #Checks if i[1] has an object for a name
                if i[1].object != None:
                    ob_name = i[1].object.name
                else:
                    ob_name = "[No Object]"
                    
                col_name = "[No Collection]"
                objects = 0
                    
                #If there is a collection pointer
                if i[1].collection != None:
                    objects = len(i[1].collection.objects)
                    #Checks if there is 1 or less objects in the collection
                    if objects <= 1:
                        #Sets the col_name variable to collection name
                        col_name = i[1].collection.name
                        len_diff += 1
                #else:
                #    col_name = "[No Collection]"
                    
                if objects <= 1:
                    print("Index[%d] (Objects: %d) [Object: %s; Collection: %s ]" % (i[0], objects, ob_name, col_name))
                
            #Prints the last ammount of different Iterate Objects calculated
            print("Different: ( %d/%d ) Iterate Objects \n" % (len_diff, len_previous))
            
        #Fake "Deletes" Iterate Objects without an Object or Collection pointer
        elif self.type == "CLEAN_TEST":
        
            #Gets previous length of props.collections
            len_previous = len(props.collections)
            
            len_diff = 0
            
            before = list(props.collections)
            
            for i in reversed(list(enumerate(before))):
                if i[1].object == None or i[1].collection == None:
                    #ob_name = ""
                    if i[1].object != None:
                        ob_name = str(i[1].object.name)
                    else:
                        ob_name = "[No Collection]"
                    #else:
                    if i[1].collection != None:
                        col_name = str(i[1].collection.name)
                    else:
                        col_name = "[No Collection]"
                        
                    print("Removed [%d]: [Object: %s; Collection: %s ]" % (i[0], ob_name, col_name))
                    
                    del before[i[0]]
                    
            print("Before: "+str(before[::]))
            
            #Prints the last ammount of different Iterate Objects calculated
            print("Removed: ( %d/%d ) Iterate Objects \n" % (len_diff, len_previous))
            
        #Resets default settings
        self.type == "DEFAULT"
        
        return {'FINISHED'}
        
class ITERATE_OBJECTS_OT_UIOperators(bpy.types.Operator):
    bl_idname = "iterate_objects.ui_list_ops"
    bl_label = "List Operators"
    bl_description = "Operators for moving and deleting list rows"
    bl_options = {'UNDO',}
    type: bpy.props.StringProperty(default="DEFAULT")
    sub: bpy.props.StringProperty(default="DEFAULT")
    #index: bpy.props.IntProperty(default=0, min=0)
    
    def execute(self, context):
        scene = bpy.context.scene
        props = scene.IM_Props
        active = props.IM_ULIndex
        
        #collection_active: 
        #collections:
            #collection:
            #object:
            #duplicates:
            #recent:
            
        #Sets list_order to "CUSTOM" when moving list rows UP or DOWN
        if props.list_order != "CUSTOM" and (self.type == "UP" or self.type == "DOWN"):
            if props.list_reverse == "DESCENDING":
                for i in enumerate(props.collections):
                    i[1].custom = i[0]
            else:
                for i in enumerate(reversed(props.collections)):
                    i[1].custom = i[0]
                
            props.list_order = "CUSTOM"
            print("Mc Bruh")
        
        #Moves list row UP
        if self.type == "UP":
            
            if self.sub == "DEFAULT":
                if active != 0:
                    props.collections.move(active, active-1)
                    props.IM_ULIndex-=1
                    
                else:
                    props.collections.move(0, len(props.collections)-1)
                    props.IM_ULIndex  = len(props.collections)-1
                    
            elif self.sub == "TOP":
                props.collections.move(active, 0)
                props.IM_ULIndex = 0
        
        #Moves list row DOWN
        elif self.type == "DOWN":
            
            if self.sub == "DEFAULT":
                if active != len(props.collections)-1:
                    props.collections.move(active, active+1)
                    props.IM_ULIndex += 1
                    
                else:
                    props.collections.move(len(props.collections)-1, 0)
                    props.IM_ULIndex = 0
                    
            elif self.sub == "BOTTOM":
                props.collections.move(active, len(props.collections)-1)
                props.IM_ULIndex = len(props.collections)-1
                
        elif self.type == "REMOVE" and len(props.collections) > 0:
            if self.sub == "DEFAULT":
                #If active is the last one
                if active == len(props.collections)-1:
                    props.collections.remove(props.IM_ULIndex)
                    
                    if len(props.collections) != 0:
                        props.IM_ULIndex -= 1
                        
                else:
                    props.collections.remove(props.IM_ULIndex)
            #Note: This only removes the props.collections, not the actual collections or objects
            elif self.sub == "ALL":
                props.collections.clear()
        
        #Resets self props into "DEFAULT"
        self.type == "DEFAULT"
        self.sub == "DEFAULT"
        
        return {'FINISHED'}
            

class ITERATE_OBJECTS_UL_items(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        scene = bpy.context.scene
        data = bpy.data
        props = scene.IM_Props
        
        #active = props.RIA_ULIndex
        IMCollect = props.collections
        
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            
            row = layout.row(align=True)
            
            if len(IMCollect) > 0:
                #obName
                #obName = item.object.name if item.object != None else "Row"+str(index)
                
                #obItems
                if item.collection != None:
                    obItems = len(item.collection.objects)
                else:
                    obItems = 0
                
                info = '%d. (%d)' % (index+1, obItems)#, obName, obItems)
                #bpy.context.scene.IM_Props.collections.add()
                
                #Displays icon of objects in list
                if props.display_icons == True:
                    
                    if item.object != "EMPTY" and item.icon != "NONE":
                        row.label(text="", icon=item.icon)
                        
                    else:
                        #obIcon = objectIcon(item.object)
                        row.label(text="", icon="QUESTION")
                        
                #Checks if the item has an object pointed
                if item.object != None:
                    row.prop(item.object, "name", text=info)
                    
                else:
                    row.label(text=info+": [No Object]")
                
                if props.display_collections == True:
                    if item.collection != None:
                        row.prop(item.collection, "name", text="", icon="GROUP")
                        
                    else:
                        row.label(text="[No Collection]")
                    
            else:
                row.label(text="No Iterations Here")
                
        #Theres nothing in this layout_type since it isn't intended to be used.
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'

    def invoke(self, context, event):
        pass
        
class ITERATE_OBJECTS_MT_CollectionsMenuActive(bpy.types.Menu):
    bl_idname = "ITERATE_OBJECTS_MT_CollectionsMenuActive"
    bl_label = "Select a Collection for Active"
    bl_description = "Dropdown to select an existing Collection as Parent Collection of new Iterate Objects\s collections"
    
    # here you specify how they are drawn
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        data = bpy.data
        props = scene.IM_Props
        
        col = layout.column()
        
        row = col.row(align=True)
        
        if len(bpy.data.collections) > 0:
            for i in enumerate(bpy.data.collections):
                button = row.operator("iterate_objects.select_collection", text=i[1].name)
                button.type = "SELECT_ACTIVE"
                button.index = i[0]
                
                row = col.row(align=True)
        else:
            #NEW_COLLECTION
            button = row.operator("iterate_objects.collection_ops", text="Add Collection", icon = "ADD")
            button.type = "NEW_COLLECTION"
            #bpy.data.collections.new("Boi") 
        #row.prop(self, "ui_tab", expand=True)#, text="X")
    
class ITERATE_OBJECTS_PT_CustomPanel1(bpy.types.Panel):
    #A Custom Panel in Viewport
    bl_idname = "ITERATE_OBJECTS_PT_CustomPanel1"
    bl_label = "Iterate Objects"
    bl_space_type = "VIEW_3D"
    bl_region_type = 'UI'
    #bl_context = "output"
    bl_category = "Iterate Objects"
    
    # draw function
    def draw(self, context):
                 
        layout = self.layout
        scene = context.scene
        props = scene.IM_Props
        
        #Layout Starts
        col = layout.column()
        
        #Active Collection
        row = col.row(align=True)
        row.label(text="Parent Collection:")
        
        row = col.row(align=True)
        
        MenuName2 = "Select Collection"
        
        if props.collection_active is not None:
            MenuName2 = props.collection_active.name
            
        #Lock Icon
        if props.lock_active == False:
            row.prop(props, "lock_active", icon="UNLOCKED", text="")
        else:
            row.prop(props, "lock_active", icon="LOCKED", text="")
            
        #if props.collection_active is None:
        if props.lock_active == False or props.collection_active is None:
            row.menu("ITERATE_OBJECTS_MT_CollectionsMenuActive", icon="GROUP", text=MenuName2)
        else:
            row.prop(props.collection_active, "name", icon="GROUP", text="")
            
        row.operator("iterate_objects.collection_ops", icon="ADD", text="").type = "NEW_GROUP"
        
        #Separates for extra space between
        col.separator()
        
        #Duplicate Button TOP
        if bpy.context.object != None:
            ob_name_1 = bpy.context.object.name
        else:
            ob_name_1 = "[None Selected]"
            
        #for loop
        ob_name_col_1 = "[New Collection]"
        #ob_name_iterate = "Iterate"
        iterateNew = False
        
        for i in enumerate(props.collections):
            if i[1].object == bpy.context.object:
                if i[1].collection != None:
                    ob_name_col_1 = i[1].collection.name
                    #changes iterateNew to 
                    iterateNew = True
                    break
        #Changes text from "Iterate" to "Iterate New" if object wasn't found in Iterate Objects
        ob_name_iterate = "Iterate New" if iterateNew == False else "Iterate"
        
        row = col.row(align=True)
        row.operator("iterate_objects.duplicating_ops", icon="DUPLICATE", text=ob_name_iterate).type = "DUPLICATE"
        
        row = col.row(align=True)
        
        #row.label(text="Collection: "+ob_name_col_1, icon="GROUP")
        row.label(text="Collection: ", icon="GROUP")
        row.label(text=ob_name_col_1)
        
        #if props.dropdown_1 == True:
        row = col.row(align=True)
        
        row.label(text="Object: ", icon="OUTLINER_OB_MESH")
        row.label(text=ob_name_1)
            
        #Duplicate Button BOTTOM
        
        row = col.row(align=True)
        row.label(text="Iteration Objects (%d):" % len(props.collections))
        #TOP
        
        split = layout.row(align=False)
        col = split.column(align=True)
        
        row = col.row(align=True)
        row.template_list("ITERATE_OBJECTS_UL_items", "custom_def_list", props, "collections", props, "IM_ULIndex", rows=3)
        
        #Side_Bar Operators
        col = split.column(align=True)
        
        row = col.row(align=True)
        button = row.operator("iterate_objects.ui_list_ops", text="", icon="TRIA_UP")
        button.type = "UP"
        
        row = col.row(align=True)
        button = row.operator("iterate_objects.ui_list_ops", text="", icon="TRIA_DOWN")
        button.type = "DOWN"
        
        row = col.row(align=True)
        button = row.operator("iterate_objects.ui_list_ops", text="", icon="PANEL_CLOSE")
        button.type = "REMOVE"
        
        row = col.row(align=True)
        row.prop(props, "display_icons", text="", icon="OUTLINER_OB_MESH")
        
        #Edit Mode option
        row = col.row(align=True)
        row.prop(props, "display_collections", text="", icon="GROUP")
        
        #End of CustomPanel
        

class ITERATE_OBJECTS_PT_DisplaySettings(bpy.types.Panel):
    bl_label = "Display Settings"
    bl_parent_id = "ITERATE_OBJECTS_PT_CustomPanel1"
    bl_space_type = "VIEW_3D"
    bl_region_type = 'UI'
    #bl_context = "output"
    bl_category = "Iterate Model"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        data = bpy.data
        props = scene.IM_Props
        
        #collection_active: 
        #collections:
        
        col = layout.column()
        
        row = col.row(align=True)
        row.label(text="Display Order")
        
        row = col.row(align=True)
        row.prop(scene.IM_Props, "list_order", expand=True)
        
        row = col.row(align=True)
        row.label(text="Sort Order")
        
        row = col.row(align=True)
        row.prop(props, "list_reverse", expand=True)#, text="X")
        
        #row = col.row(align=True)
        #row.separator()
        
        #col = layout.column(align=False)
        
        row = col.row(align=True)
        row.label(text="Display")
        
        row = col.row(align=True)
        row.prop(props, "display_collections", text="Collections", icon="GROUP")
        row.prop(props, "display_icons", text="Icons", icon="OUTLINER_OB_MESH")
        
        col.separator()
        
        row = col.row(align=True)
        
        row.label(text="New Collection")
        
        row = col.row(align=True)

        row.prop(props, "index_to_new", text="Update Active List Index", icon="NONE")
        
        row = col.row(align=True)

        row.prop(props, "group_name_use", text="Use Object Name", icon="NONE")
        
        row = col.row(align=True)
        
        #Grays row out with .active, but you can still change props inside it.
        row.active = not bool(props.group_name_use)
        
        row.prop(props, "group_name", text="New Name", icon="NONE")
        
            
class ITERATE_OBJECTS_PT_Cleaning(bpy.types.Panel):
    bl_label = "Cleaning Operators"
    bl_parent_id = "ITERATE_OBJECTS_PT_CustomPanel1"
    bl_space_type = "VIEW_3D"
    bl_region_type = 'UI'
    #bl_context = "output"
    bl_category = "Iterate Model"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        data = bpy.data
        props = scene.IM_Props
        
        col = layout.column(align=False)
        
        row = col.row(align=True)
        row.operator("iterate_objects.cleaning_ops", icon="TRASH", text="Clean Collections").type = "CLEAN_1"
        
        row = col.row(align=True)
        row.prop(props, "clean_leave", text="Leave")
        
        col.separator()
        
        #row = col.row(align=True)
        #row.label(text="Cleaning List:")
        
        row = col.row(align=True)
        row.operator("iterate_objects.cleaning_ops", icon="TRASH", text="Remove Empty in List").type = "CLEAN_2"
        
        col.separator()
        
        if props.debug_mode == True:
            #Debug Operators
            row = col.row(align=True)
            #Dropdown Arrow Boolean
            row.prop(props, "debug_mode_arrow", text="", icon="DOWNARROW_HLT")
            row.label(text="Debug Operators:")
            
            if props.debug_mode_arrow == True:
                
                row = col.row(align=True)
                row.operator("iterate_objects.debug", text="Print Different").type = "PRINT_DIFFERENT_1"
                
                #row = col.row(align=True)
                #row.operator("iterate_objects.debug", text="Delete Test").type = "CLEAN"
                
                col.separator()
                
                row = col.row(align=True)
                row.operator("iterate_objects.debug", text="Add 3 Objects").type = "TESTING"
                
                col.separator()
                
                row = col.row(align=True)
                row.operator("iterate_objects.debug", icon="ERROR", text="Delete All").type = "DELETE_NUKE"
                
                row = col.row(align=True)
                row.operator("iterate_objects.debug", text="Print Objects/Collections").type = "PRINT_1"
            

def ListOrderUpdate(self, context):
    scene = bpy.context.scene
    data = bpy.data
    props = scene.IM_Props
    #list_order "DUPLICATES" "RECENT" "CUSTOM"
    #list_reverse: "DESCENDING" "ASCENDING"
    
    reverseBool = False
    if props.list_reverse == "ASCENDING":
        reverseBool = True
        
    #Updates the UI List selected index when ListOrderUpdate is called
    props.IM_ULIndex = len(props.collections)-props.IM_ULIndex-1
        
    # "a" parameter would be an object with methods
    def returnOrder(a):
        #Returns len() of objects in collection, else return 0
        if props.list_order == "DUPLICATES":
            
            return len(a.collection.objects) if a.collection != None else 0
            
        #Returns the integer value of the order the objects were created
        if props.list_order == "RECENT":
            return a.recent
            
        #Returns custom value order made by user in the UI List
        if props.list_order == "CUSTOM":
            return a.custom
        
    #This is where sorting is done
    #sort = sorted(props.collections, key=lambda a: a.duplicates, reverse=reverseBool)
    sort = sorted(props.collections, key=returnOrder, reverse=reverseBool)
    
    nameList = []
    
    #For loop appends the names of objects in props.collections.objects into nameList
    for i in enumerate(sort):
        if i[1].object is not None:
            nameList.append(i[1].object.name)
        else:
            print("Collection: %s missing object" % (i[1].name))
            #This section calculates the index of props.collection even when they are being removed in order to remove them
            newIndex = None
            for j in enumerate(props.collections):
                if i[1] == j[1]:
                    newIndex = j[0]
            props.collections.remove(newIndex)
    
    #For loop uses object names in nameList to move props.collections
    for i in enumerate(nameList):
        colLocation = 0
        #Loops through props.collections to see if their names matches the names of object names in nameList
        for j in enumerate(props.collections):
            #if j[1].name == i[1]:
            if j[1].object.name == i[1]:
                colLocation = j[0]
                break
        props.collections.move(colLocation, i[0])
    
    return
    
class ITERATE_OBJECTS_PreferencesMenu(bpy.types.AddonPreferences):
    bl_idname = "iterate_objects_addon_b2_80_v1_0"
    # here you define the addons customizable props
    ui_tab: bpy.props.EnumProperty(name="Enum", items= [("GENERAL", "General", "General Options"), ("ABOUT", "About", "About Author & Where to Support")], description="Iterate Model UI Tabs", default="GENERAL")
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.IM_Props
        
        col = layout.column()
        
        row = col.row(align=True)
        row.prop(self, "ui_tab", expand=True)
        row = col.row(align=True)
        
        box = layout.box()
        col = box.column()
        #row = col.row(align=True)
        
        if self.ui_tab == "GENERAL":
            row = col.row(align=True)
            #row.label(text="Add Button to 3D Viewport Header?")
            row.prop(props, "debug_mode", expand=True, text="Debug Mode")
            
            row = col.row(align=True)
            
        elif self.ui_tab == "ABOUT":
            row = col.row(align=True)
            row.label(text="JohnGDDR5 on: ")
            row.operator("wm.url_open", text="Youtube").url = "https://www.youtube.com/channel/UCzPZvV24AXpOBEQWK4HWXIA"
            row.operator("wm.url_open", text="Twitter").url = "https://twitter.com/JohnGDDR5"
            row.operator("wm.url_open", text="Artstation").url = "https://www.artstation.com/johngddr5"

class ITERATE_OBJECTS_CollectionObjects(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="", default="")
    collection: bpy.props.PointerProperty(name="Added Collections to List", type=bpy.types.Collection)
    object: bpy.props.PointerProperty(name="Object", type=bpy.types.Object)
    
    #duplicates: bpy.props.IntProperty(name="Int", description="", default= 0, min=0)
    
    recent: bpy.props.IntProperty(name="Int", description="", default= 0, min=0)
    custom: bpy.props.IntProperty(name="Int", description="", default= 0, min=0)
    icon: bpy.props.StringProperty(name="Icon name for object", description="Used to display in the list", default="QUESTION")#, get=)#, update=checkIcon)
    
class ITERATE_OBJECTS_Props(bpy.types.PropertyGroup):
    #Tries to set collection_parent's default to Master Collection
    
    collection_active: bpy.props.PointerProperty(name="Collection to add Collections for Object duplicates", type=bpy.types.Collection)
    
    #Booleans for locking default collection of parent
    
    lock_active: bpy.props.BoolProperty(name="Lock Collection of Active", description="When locked, you can now edit the name of the selected collection", default=False)
    
    collections: bpy.props.CollectionProperty(type=ITERATE_OBJECTS_CollectionObjects)
    
    IM_ULIndex: bpy.props.IntProperty(name="List Index", description="UI List Index", default= 0, min=0)
    
    clean_leave: bpy.props.IntProperty(name="List Index", description="Ammount of recent Objects to leave when cleaning.", default=2, min=0)
    
    #Dropdown for Iterate Display
    dropdown_1: bpy.props.BoolProperty(name="Dropdown", description="Show Object of Iterate Object", default=False)
    
    group_name_use: bpy.props.BoolProperty(name="Use Object Name for New Collection", description="Use the Object\'s name for the New Collection when creating a new Iteration Object", default=True)
    
    group_name: bpy.props.StringProperty(name="New Collection Name", description="Name used when creating a new collection for Active", default="Group")
    
    listDesc =  ["Displays List in order of how many duplicates each object has", "Displays List in the order they were created", "Displays List in order user specified"]
    listDesc2 =  ["List displays in Descending Order", "List displays in Ascending Order"]
    
    list_order: bpy.props.EnumProperty(name="Display Mode", items= [("DUPLICATES", "Duplicates", listDesc[0], "DUPLICATE", 0), ("RECENT", "Recent", listDesc[1], "SORTTIME", 1), ("CUSTOM", "Custom", listDesc[2], "ARROW_LEFTRIGHT", 2)], description="Display Mode of List", default="DUPLICATES", update=ListOrderUpdate)
    
    list_reverse: bpy.props.EnumProperty(name="Display Mode", items= [("DESCENDING", "Descending", listDesc2[0], "SORT_DESC", 0), ("ASCENDING", "Ascending", listDesc2[1], "SORT_ASC", 1)], description="Display Mode of List", default="DESCENDING", update=ListOrderUpdate)
    
    display_collections: bpy.props.BoolProperty(name="Display Collections in List", description="Display Iterate Object collections where duplicates are sent.", default=True)
    
    display_icons: bpy.props.BoolProperty(name="Display Icons", description="Display icons of objects in the list", default=True)
    
    index_to_new: bpy.props.BoolProperty(name="Updates Active List Index to New Iteration Object", description="Sets Active list index to New Iteration Object that was added.", default=True)
    
    debug_mode: bpy.props.BoolProperty(name="Display Debug Operators", description="To aid in Debugging Operators. Displayed in \"Display Settings\"", default=False)
    
    debug_mode_arrow: bpy.props.BoolProperty(name="Debug Mode Dropdown Arrow", description="To display Debug Mode", default=True)
    
    #For Iterate Collection Settings and Operators
    
    #hide_types_last
    #hide_last: bpy.props.BoolProperty(name="Exclude Recent Iteration", description="When using the operators for toggling \"all objects\"", default=False)
    
#Classes that are registered
classes = (
    ITERATE_OBJECTS_OT_SelectCollection,
    ITERATE_OBJECTS_OT_GroupOperators,
    ITERATE_OBJECTS_OT_Duplicate,
    ITERATE_OBJECTS_OT_Cleaning,
    ITERATE_OBJECTS_OT_Removing,
    
    ITERATE_OBJECTS_OT_Debugging,
    ITERATE_OBJECTS_OT_UIOperators,
    
    ITERATE_OBJECTS_UL_items,
    ITERATE_OBJECTS_MT_CollectionsMenuActive,
    
    ITERATE_OBJECTS_PT_CustomPanel1,
    ITERATE_OBJECTS_PT_DisplaySettings,
    ITERATE_OBJECTS_PT_Cleaning,
    
    ITERATE_OBJECTS_PreferencesMenu,
    ITERATE_OBJECTS_CollectionObjects,
    ITERATE_OBJECTS_Props,
)

def register():
    #ut = bpy.utils
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    
    #bpy.types.Scene.IM_Collections = bpy.props.CollectionProperty(type=REF_IMAGEAID_Collections)
    bpy.types.Scene.IM_Props = bpy.props.PointerProperty(type=ITERATE_OBJECTS_Props)
    
def unregister():
    #ut = bpy.utils
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    
    del bpy.types.Scene.IM_Props
    
if __name__ == "__main__":
    register()
