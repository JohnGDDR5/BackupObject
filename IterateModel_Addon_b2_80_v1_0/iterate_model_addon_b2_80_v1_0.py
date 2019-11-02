# ##### BEGIN GPL LICENSE BLOCK #####
#
# Iterate Model is an addon for creating duplicates of objects and having them sorted by most recent. A kind of version-control system.
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
    "location": "3D View > Side Bar > Iterate Model",
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

def objectIcon(object):
    scene = bpy.context.scene
    data = bpy.data
    props = scene.IM_Props
    
    #icons = ["OUTLINER_OB_EMPTY", "OUTLINER_OB_MESH", "OUTLINER_OB_CURVE", "OUTLINER_OB_LATTICE", "OUTLINER_OB_META", "OUTLINER_OB_LIGHT", "OUTLINER_OB_IMAGE", "OUTLINER_OB_CAMERA", "OUTLINER_OB_ARMATURE", "OUTLINER_OB_FONT", "OUTLINER_OB_SURFACE", "OUTLINER_OB_SPEAKER", "OUTLINER_OB_FORCE_FIELD", "OUTLINER_OB_GREASEPENCIL", "OUTLINER_OB_LIGHTPROBE"]
    #Object Type
    
    icon = "BLANK1"
    
    #If there is an object to see if it has a type
    if object is not None:
        type = object.type
        
        if type == "MESH":
            icon = "OUTLINER_OB_MESH"
        elif type == "EMPTY":
            if object.empty_display_type != "IMAGE":
                icon = "OUTLINER_OB_EMPTY"
            elif object.empty_display_type == "IMAGE":
                icon = "OUTLINER_OB_IMAGE"
            elif object.field.type != "NONE":
                icon = "OUTLINER_OB_FORCE_FIELD"
        elif type == "CAMERA":
            icon = "OUTLINER_OB_CAMERA"
        elif type == "CURVE":
            icon = "OUTLINER_OB_CURVE"
        elif type == "SURFACE":
            icon = "OUTLINER_OB_SURFACE"
        elif type == "META":
            icon = "OUTLINER_OB_META"
        elif type == "FONT":
            icon = "OUTLINER_OB_FONT"
        elif type == "GPENCIL":
            icon = "OUTLINER_OB_GREASEPENCIL"
        elif type == "ARMATURE":
            icon = "OUTLINER_OB_ARMATURE"
        elif type == "LATTICE":
            icon = "OUTLINER_OB_LATTICE"
        elif type == "LIGHT":
            icon = "OUTLINER_OB_LIGHT"
        elif type == "LIGHT_PROBE":
            icon = "OUTLINER_OB_LIGHTPROBE"
        elif type == "SPEAKER":
            icon = "OUTLINER_OB_SPEAKER"
        else:
            pass
    
    return icon

def findAxis(input):
    indexAxis = 0
    if input == "X":
        indexAxis = 0
    elif input == "Y":
        indexAxis = 1
    elif input == "Z":
        indexAxis = 2
        
    return indexAxis

class ITERATE_MODEL_OT_SelectCollection(bpy.types.Operator):
    bl_idname = "iteratemodel.select_collection"
    bl_label = "Select Collection"
    bl_description = "Set collection as Parent or Active collection"
    bl_options = {'UNDO',}
    type: bpy.props.StringProperty(default="DEFAULT")
    index: bpy.props.IntProperty(default=0, min=-1)
    
    def execute(self, context):
        scene = bpy.context.scene
        props = scene.IM_Props
            
        #Select a collection 
        if self.type == "SELECT_PARENT":
            if self.index >= 0:
                props.collection_parent = bpy.data.collections[self.index] 
            else:
                props.collection_parent = bpy.context.scene.collection
            
            if props.collection_active is None:
                colNew = bpy.data.collections.new(props.group_name)
                #Links colNew to collection_active
                props.collection_active = colNew
                props.collection_parent.children.link(colNew)
            else:
                pass
                
        if self.type == "SELECT_ACTIVE":
            props.collection_active = bpy.data.collections[self.index]
            
        self.type == "DEFAULT"
        
        return {'FINISHED'}

class ITERATE_MODEL_OT_GroupOperators(bpy.types.Operator):
    bl_idname = "iteratemodel.collection_ops"
    bl_label = "IterateModel Duplicating Operators"
    bl_description = "IterateModel Duplicating Operators"
    bl_options = {'UNDO',}
    type: bpy.props.StringProperty(default="DEFAULT")
    index: bpy.props.IntProperty(default=0, min=0)
    
    def execute(self, context):
        scene = bpy.context.scene
        props = scene.IM_Props
        
        #New Collection Group inside Parent Collection and set as Active Collection
        if self.type == "NEW_GROUP":
            
            if props.reset_offsets == True:
                for i in enumerate(bpy.context.scene.IM_Props.collections):
                    if len(i[1].collection.objects) > 0:
                        axis = findAxis(i[1].axis)
                        for y in enumerate(reversed(i[1].collection.objects[0:-1])):
                            print("Object: %s" % (y[1].name))
                            print("Location[%d]: [%f]" % (axis, y[1].location[axis]))
                            y[1].location[axis] -= ((y[0]+1) * i[1].offset)#(props.master_offset - i[1].offset))# + props.master_offset
                            
                            print("Location[%d]: [%f]" % (axis, y[1].location[axis]))
            
            colNew = bpy.data.collections.new(props.group_name)
            #Links colNew2 to collection_parent
            props.collection_active = colNew
            
            #If there is a Parent collection, link colNew to it
            if props.collection_parent is not None:
                props.collection_parent.children.link(colNew)
            #if collection_parent is None, link new Collection to Master Collection
            else:
                bpy.context.scene.collection.children.link(colNew)
            
            #Removes collections from all IM_Props.collections.collection
            for i in enumerate(props.collections):
                i[1].collection = None
                #i[1].duplicates = 0
        
        
        #Create a new Collection Parent, link it to scene, and an Active Collection linked to Parent    
        if self.type == "NEW_COLLECTION":
            # Create a new collection and link it to the scene.
            colNew = bpy.data.collections.new("Collection")
            props.collection_parent = colNew
            #Links new collection to Master Collection
            scene.collection.children.link(colNew)
            
            #If collection active isn't none, make a new one for it, or don't change Active Collection
            if props.collection_active is None:
                #Creates new Group Collection
                colNew2 = bpy.data.collections.new(props.group_name)
                #Links colNew2 to collection_parent
                props.collection_active = colNew2
                props.collection_parent.children.link(colNew2)
                
        self.type == "DEFAULT"
        
        return {'FINISHED'}
        
class ITERATE_MODEL_OT_Duplicate(bpy.types.Operator):
    bl_idname = "iteratemodel.duplicating_ops"
    bl_label = "Duplicates active objects"
    bl_description = "Duplicates active objects and sends them to the Active Collection"
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
                        colNew2 = bpy.data.collections.new(i[1].name)
                        #Links colNew2 to collection_parent
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
                    
                    #Checks if there is more than one object in collection
                    if len(existingCol.collection.objects) > 0:
                        #Master Axis's index
                        master_axis = findAxis(props.master_axis)
                        #IM_Props.collection.axis's 
                        axis_1 = findAxis(existingCol.axis)
                        
                        #If the IM_Props.collection.axis is the same as master_axis
                        if existingCol.axis == props.master_axis:
                            for y in enumerate(reversed(existingCol.collection.objects[0:-1])):
                                y[1].location[master_axis] += (y[0] * (props.master_offset - existingCol.offset)) + props.master_offset
                        else:
                            for y in enumerate(reversed(existingCol.collection.objects[0:-1])):
                                print("Object: %s" % (y[1].name))
                                
                                #Moves all objects in collection Backwards to 0 in collection's axis
                                y[1].location[axis_1] -= (y[0] * existingCol.offset)
                                print("Location[%d]: [%f]" % (axis_1, y[1].location[axis_1]))
                                
                                #Moves all objects forward with Master_offset & on the Master_Axis
                                y[1].location[master_axis] += ((y[0]+1) * (props.master_offset))
                                print("Location[%d]: [%f] %f" % (master_axis, y[1].location[master_axis],(y[0] * existingCol.offset)))
                            
                        print("Axis: %s , [%d]" % (existingCol.axis, findAxis(existingCol.axis)))
                    
                        #Sets props.collection's .offset & .axis as IM_Props's masters
                        print("Master Axis: %s" % (props.master_axis))
                        print("Master Offset: %s" % (props.master_offset))
                        existingCol.offset = props.master_offset
                        existingCol.axis = props.master_axis
                        print("-"*5)
                    
                    #Doesn't Temporarily hides in the viewport
                    ob.hide_set(not props.hide_types[0])
                    #Doesn't Hide object from rendering
                    ob.hide_render = not props.hide_types[1]
                    #Doesn't Hide object from rendering
                    ob.hide_viewport = not props.hide_types[2]
                    
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
                        
        self.type == "DEFAULT"
        
        return {'FINISHED'}

class ITERATE_MODEL_OT_OffsetCollection(bpy.types.Operator):
    bl_idname = "iteratemodel.offset_collection"
    bl_label = "Toggles Hide Except Recent"
    bl_description = "Toggles Hide All Except Recent Iteration"
    bl_options = {'UNDO',}
    
    state: bpy.props.BoolProperty(default=True)
    type: bpy.props.StringProperty(default="DEFAULT")
    index: bpy.props.IntProperty(default=0, min=0)
    
    @classmethod
    def poll(cls, context):
        scene = bpy.context.scene
        props = scene.IM_Props
        
        #return props.collection_parent is not None and props.collection_active is not None
        return props.collection_active is not None
    
    def execute(self, context):
        scene = bpy.context.scene
        props = scene.IM_Props
        #inputs = context.preferences.inputs
        #bpy.context.preferences.inputs.view_rotate_method
        
        #props.master_axis
        #props.master_offset
        
        if self.type == "DEFAULT":
            
            #if props.collection_parent is not None:
            axis = findAxis(props.master_axis)
            #Collections that are Viewable
            viewportCollections = []
            
            #Appends all viewable collections from IM_Props.collections to viewportCollections
            for i in enumerate(bpy.context.scene.IM_Props.collections):
                if i[1].collection.hide_viewport == False:
                    viewportCollections.append(i[1])
                        
                    if len(i[1].collection.objects) > 0:
                        #Master Axis's index
                        master_axis = findAxis(props.master_axis)
                        #IM_Props.collection.axis's 
                        axis_1 = findAxis(i[1].axis)
                        
                        #If the IM_Props.collection.axis is the same as master_axis
                        if i[1].axis == props.master_axis:
                            print("If : " + "-"*6)
                            for y in enumerate(reversed(i[1].collection.objects[0:-1])):
                                print("Object: %s" % (y[1].name))
                                print("Location[%d]: [%f]" % (axis_1, y[1].location[axis_1]))
                                y[1].location[master_axis] += ((y[0]+1) * (props.master_offset - i[1].offset))# + props.master_offset
                                
                                print("Location[%d]: [%f]" % (axis_1, y[1].location[axis_1]))
                        else:
                            print("Else : " + "-"*6)
                            for y in enumerate(reversed(i[1].collection.objects[0:-1])):
                                print("Object: %s" % (y[1].name))
                                print("Location[%d]: [%f]" % (axis_1, y[1].location[axis_1]))
                                #Moves all objects in collection Backwards to 0 in collection's axis
                                y[1].location[axis_1] -= ((y[0]+1) * i[1].offset)
                                print("Location[%d]: [%f]" % (axis_1, y[1].location[axis_1]))
                                
                                #Moves all objects forward with Master_offset & on the Master_Axis
                                #y[1].location[master_axis] += ((y[0]+1) * (props.master_offset))
                                y[1].location[master_axis] += ((y[0]+1) * (props.master_offset))
                                print("Location[%d]: [%f] %f" % (master_axis, y[1].location[master_axis],(y[0] * i[1].offset)))
                        
                    #Sets IM_Props.collections's offset same as master_offset
                    i[1].offset = props.master_offset
                    i[1].axis = props.master_axis
            
        self.type == "DEFAULT"
        
        #Changes the state the operator hides and unhides properties, True or False
        if self.state == True:
            self.state = False
        else:
            self.state = True
        
        return {'FINISHED'}
        
class ITERATE_MODEL_OT_OffsetUse(bpy.types.Operator):
    bl_idname = "iteratemodel.offset_use_object"
    bl_label = "Toggles Hide Except Recent"
    bl_description = "Toggles Hide All Except Recent Iteration"
    bl_options = {'UNDO',}
    
    state: bpy.props.BoolProperty(default=True)
    type: bpy.props.StringProperty(default="DEFAULT")
    index: bpy.props.IntProperty(default=0, min=0)
    
    @classmethod
    def poll(cls, context):
        scene = bpy.context.scene
        props = scene.IM_Props
        
        #return props.collection_parent is not None and props.collection_active is not None
        return props.collection_active is not None
    
    def execute(self, context):
        scene = bpy.context.scene
        props = scene.IM_Props
        #inputs = context.preferences.inputs
        #bpy.context.preferences.inputs.view_rotate_method
        
        #props.master_axis
        #props.master_offset
        
        if self.type == "DEFAULT":
            #If there is at least 1 object selected
            if len(bpy.context.selected_objects) > 0:
                #if props.collection_parent is not None:
                axis = findAxis(props.master_axis)
                #Collections that are Viewable
                nonIterationObjects = []
                
                previous_active = bpy.context.active_object
                
                previous_selected = bpy.context.selected_objects
                
                new_active = None
                
                new_objects = []
                
                #Unselects the objects
                for i in enumerate(previous_selected):
                    i[1].select_set(False)
                    
                #Sets Active Object to None
                bpy.context.view_layer.objects.active = None
                
                for i in enumerate(previous_selected):
                    iterated = False
                    for j in enumerate(bpy.context.scene.IM_Props.collections):
                        for c in enumerate(i[1].users_collection):
                            #if i[1].users_collection[c[1]] == j[1].collection:
                            if c[1] == j[1].collection:
                                #IM_Props.collection.axis's 
                                axis_1 = findAxis(j[1].axis)
                                
                                index1 = None
                                
                                for k in enumerate(reversed(j[1].collection.objects)):
                                    if k[1] == i[1]:
                                        index1 = k[0]
                                        iterated = True
                                        break
                                        
                                if index1 != None:
                                    i[1].select_set(True)
                                    
                                    bpy.context.view_layer.objects.active = i[1]
                                    
                                    #Duplicates selected objects in previous_selected
                                    bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0.0, 0.0, 0.0), "orient_type":'GLOBAL'})
                                    
                                    ob = bpy.context.object
                                    print("Duplicated Object: "+str(ob.name))
                                    new_objects.append(ob)
                                    
                                    #If new object's duplicate origin object was the previously active
                                    if i[1] == previous_active:
                                        new_active = ob
                                        
                                    #Unlinks duplicated Object inside the collection
                                    j[1].collection.objects.unlink(ob)
                                    
                                    #Links duplicated object into collection_active
                                    props.collection_active.objects.link(ob)
                                    
                                    #Moves Object Backwards
                                    ob.location[axis_1] -= index1 * j[1].offset
                                    
                                    i[1].select_set(False)
                                break
                    #If object wasn't found inside Iteration Collections
                    if iterated == False:
                        nonIterationObjects.append(i[1].name)
                        
                #Reselects the previously selected objects
                for i in enumerate(new_objects):
                    i[1].select_set(True)
                    
                #Sets Active Object to None
                bpy.context.view_layer.objects.active = new_active
                    
                if len(nonIterationObjects) > 0:
                    print("Objects not inside Iteration Collections: "+str(nonIterationObjects))
                    reportString = "Moved %d/%d Iterations to Original Location. %d Objects not in Iteration Collections" % (len(previous_selected)-len(nonIterationObjects), len(previous_selected), len(nonIterationObjects))
                else:
                    reportString = "Moved %d/%d Iterations to Original Location." % (len(previous_selected), len(previous_selected))
            else:
                reportString = "No Objects Selected"
                
            
        self.type == "DEFAULT"
        
        self.report({'INFO'}, reportString)
        
        return {'FINISHED'}
        
class ITERATE_MODEL_OT_ToggleHideObjects(bpy.types.Operator):
    bl_idname = "iteratemodel.toggle_hide_objects"
    bl_label = "Toggles Hide Except Recent"
    bl_description = "Toggles Hide All Except Recent Iteration"
    bl_options = {'UNDO',}
    
    state: bpy.props.BoolProperty(default=True)
    type: bpy.props.StringProperty(default="DEFAULT")
    index: bpy.props.IntProperty(default=0, min=0)
    
    @classmethod
    def poll(cls, context):
        scene = bpy.context.scene
        props = scene.IM_Props
        
        return props.collection_active is not None
    
    def execute(self, context):
        scene = bpy.context.scene
        props = scene.IM_Props
        
        if self.type == "DEFAULT":
            
            #Iterates through every collection inside collection_active
            for i in enumerate(bpy.context.scene.IM_Props.collection_active.children):
                lastObject = len(i[1].objects)-1
                
                #If there is at least one object in a collection
                if len(i[1].objects) > 0:
                    enumObjects = enumerate(i[1].objects)
                    if props.hide_last == False:
                        
                        if props.hide_types[0] == True:
                            for j in enumerate(i[1].objects):
                                j[1].hide_set(self.state)
                                
                        if props.hide_types[1] == True:
                            for j in enumerate(i[1].objects):
                                j[1].hide_render = self.state
                                
                        if props.hide_types[2] == True:
                            for j in enumerate(i[1].objects):
                                j[1].hide_viewport = self.state
                    else:
                        if props.hide_types[0] == True:
                            for j in enumerate(i[1].objects[0:-1]):
                                j[1].hide_set(self.state)
                                
                        if props.hide_types[1] == True:
                            for j in enumerate(i[1].objects[0:-1]):
                                j[1].hide_render = self.state
                                
                        if props.hide_types[2] == True:
                            for j in enumerate(i[1].objects[0:-1]):
                                j[1].hide_viewport = self.state 
                """        
                #Last Object
                #If hide_types' Booleans are True, the Last Object's hidden stays Off. Else, they can be toggle on or off by the opeartor
                if props.hide_last == False:
                    i[1].objects[lastObject].hide_set(self.state)
                    i[1].objects[lastObject].hide_render = self.state
                    i[1].objects[lastObject].hide_viewport = self.state """
                    
        self.type == "DEFAULT"
        
        #Changes the state the operator hides and unhides properties, True or False
        if self.state == True:
            self.state = False
        else:
            self.state = True
        
        return {'FINISHED'}
        
class ITERATE_MODEL_OT_ToggleHideCollections(bpy.types.Operator):
    bl_idname = "iteratemodel.toggle_hide_collections"
    bl_label = "Toggles Hide Except Recent"
    bl_description = "Toggles Hide All Except Recent Iteration"
    bl_options = {'UNDO',}
    
    state: bpy.props.BoolProperty(default=True)
    type: bpy.props.StringProperty(default="DEFAULT")
    index: bpy.props.IntProperty(default=0, min=0)
    
    @classmethod
    def poll(cls, context):
        scene = bpy.context.scene
        props = scene.IM_Props
        
        return props.collection_active is not None
    
    def execute(self, context):
        scene = bpy.context.scene
        props = scene.IM_Props
        
        if self.type == "DEFAULT":
            
            #Iterates through every collection inside collection_active
            for i in enumerate(bpy.context.scene.IM_Props.collections):
                #bpy.context.screen.areas[1].spaces[0].display_mode
                
                #bpy.context.scene.view_layers[0].active_layer_collection.name
                #Returns "Group"
                if i[1].collection is not None:
                    if props.hide_types_collections[1] == True:
                        i[1].collection.hide_render = self.state
                    
                    #Hides object from viewport
                    if props.hide_types_collections[2] == True:
                        i[1].collection.hide_viewport = self.state
                        
                    #Note: As of right now, I need a more complicated solution to be able to toggle the temporary Viewport Visibility [0] "Eye Icon" using python
                    
        self.type == "DEFAULT"
        
        #Changes the state the operator hides and unhides properties, True or False
        if self.state == True:
            self.state = False
        else:
            self.state = True
        
        return {'FINISHED'}
        
class ITERATE_MODEL_OT_Debugging(bpy.types.Operator):
    bl_idname = "iteratemodel.debug"
    bl_label = "IterateModel Debugging Operators"
    bl_description = "To assist with debugging and development"
    bl_options = {'UNDO',}
    type: bpy.props.StringProperty(default="DEFAULT")
    #index: bpy.props.IntProperty(default=0, min=0)
    
    def execute(self, context):
        scene = bpy.context.scene
        props = scene.IM_Props
        
        if self.type == "DELETE":
            
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
                colNameParent = "(No Parent Found)"
                
                if props.collection_parent is not None:
                    colNameParent = props.collection_parent.name
                    
                reportString = "Removed: [%s, %s] & %d Objects & %d Collection Groups" % (colNameParent, colNameActive, removedObjects, removedCol)
                
                bpy.data.collections.remove(props.collection_active, do_unlink=True)
                #bpy.data.collections.remove(props.collection_parent, do_unlink=True)
                
                print(reportString)
                self.report({'INFO'}, reportString)
            else:
                #Removes scene.IM_Props.collections
                for i in enumerate(reversed(props.collections)):
                    props.collections.remove(len(props.collections)-1)
                
            #If there was a Parent Collection selected
            if props.collection_parent is not None:
                reportString = "Removed: [%s] Collection" % (props.collection_parent.name)
                
                #Removes collection, but not other links of it incase the user linked it
                bpy.data.collections.remove(props.collection_parent, do_unlink=True)
            else:
                reportString = "collection_parent is None"
                
            print(reportString)
            self.report({'INFO'}, reportString)
                
        self.type == "DEFAULT"
        
        return {'FINISHED'}
        
class ITERATE_MODEL_OT_UIOperators(bpy.types.Operator):
    bl_idname = "iteratemodel.ui_list_ops"
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
        
        #collection_parent:
        #collection_active: 
        #collections:
            #collection:
            #object:
            #duplicates:
            #recent:
        if props.list_order != "CUSTOM" and self.type == "UP" or self.type == "DOWN":
            if props.list_reverse == "DESCENDING":
                for i in enumerate(props.collections):
                    i[1].custom = i[0]
            else:
                for i in enumerate(reversed(props.collections)):
                    i[1].custom = i[0]
                
            props.list_order = "CUSTOM"
            print("Mc Bruh")
        
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
                
        elif self.type == "DOWN":
            
            if self.sub == "DEFAULT":
                if active != len(props.collections)-1:
                    props.collections.move(active, active+1)
                    props.IM_ULIndex+=1
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
        
        #Sets self. into "DEFAULT"
        self.type == "DEFAULT"
        self.sub == "DEFAULT"
        
        return {'FINISHED'}

def updateValues(context):
    props = bpy.context.scene.IM_Props
    
    IMCollect = props.collections
    
    #if len_original != 0:
    if props.collections != None:
        #New Length to subtract from i to get the new index of i
        #len_sub = len(props.collections)
        len_original = len(props.collections)
        
        for i in enumerate(props.collections):
            
            if i[1].object != None:
                #bpy.context.scene.IM_Props.collections[0].collection.objects
                
            
                if i[1].collection != None:
                    #i[1].duplicates = len(i[1].collection.objects)
                    pass
            else:
                new_index = i[0] - (len(props.collections)-i[0])
                props.collections.remove(new_index+1)
                pass
    else:
        print("Bruh 1")
        
    return None
            
        

class ITERATE_MODEL_UL_items(bpy.types.UIList):
    #updateValues(bpy.context.scene)
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        scene = bpy.context.scene
        data = bpy.data
        props = scene.IM_Props
        
        #active = props.RIA_ULIndex
        IMCollect = props.collections
        
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            
            #len(bpy.context.scene.IM_Props.collections[0].collection.objects)
            
            #item.duplicates = len(item.collection.objects)
            #updateValues(bpy.context.scene)
            
            
            if len(IMCollect) > 0:
                #info = '%d. %s: %d' % (index, item.object.name, item.duplicates)
                info = '%d. %s: %d' % (index, item.object.name)#, item.duplicates)
                
                #Displays icon of objects in list
                if props.display_icons == True:
                    
                    if item.object != "EMPTY" or item.icon != "NONE":
                        row.label(text="", icon=item.icon)
                    else:
                        obIcon = objectIcon(item.object)
                        #row.label(text="", icon=obIcon) 
                    
                row.label(text=info)#, icon="OUTLINER_OB_MESH")
                #"OUTLINER_OB_MESH" for mesh, "OUTLINER_OB_IMAGE" for empty
                #row.icon(item.object)
            else:
                row.label(text="No Iterations Here")

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            #row.prop(item, "resolution", text="", emboss=False, icon="NONE")

    def invoke(self, context, event):
        pass

class ITERATE_MODEL_MT_CollectionsMenuParent(bpy.types.Menu):
    bl_idname = "ITERATE_MODEL_MT_CollectionsMenuParent"
    bl_label = "Select a Collection"
    bl_description = "Dropdown to select a Parent Collection where Active Collections will be created. (Optional)"
    
    # here you specify how they are drawn
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        data = bpy.data
        props = scene.IM_Props
        masterCol = bpy.context.scene.collection
        #collection_parent:
        #collection_active: 
        #collections:
        
        col = layout.column()
        
        #if self.type == "COLLECTION":
        
        row = col.row(align=True)
        
        button = row.operator("iteratemodel.select_collection", text=masterCol.name)
        button.type = "SELECT_PARENT"
        button.index = -1
        
        row = col.row(align=True)
        
        if len(bpy.data.collections) > 0:
            for i in enumerate(bpy.data.collections):
                button = row.operator("iteratemodel.select_collection", text=i[1].name)
                button.type = "SELECT_PARENT"
                button.index = i[0]
                
                row = col.row(align=True)
        else:
            #NEW_COLLECTION
            button = row.operator("iteratemodel.collection_ops", text="Add Collection", icon="ADD")
            button.type = "NEW_COLLECTION"
            #bpy.data.collections.new("Boi") 
        #row.prop(self, "ui_tab", expand=True)#, text="X")
        
class ITERATE_MODEL_MT_CollectionsMenuActive(bpy.types.Menu):
    bl_idname = "ITERATE_MODEL_MT_CollectionsMenuActive"
    bl_label = "Select a Collection for Active"
    bl_description = "Dropdown to select an Active Collection to iterate objects to"
    
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
                button = row.operator("iteratemodel.select_collection", text=i[1].name)
                button.type = "SELECT_ACTIVE"
                button.index = i[0]
                
                row = col.row(align=True)
        else:
            #NEW_COLLECTION
            button = row.operator("iteratemodel.collection_ops", text="Add Collection", icon = "ADD")
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
        
        #Parent Collection
        row = col.row(align=True)
        row.label(text="Parent Collection:")
        
        row = col.row(align=True)
        
        MenuName1 = "Select Collection"
        
        if props.collection_parent is not None:
            MenuName1 = props.collection_parent.name
        
        #Lock Icon
        if props.lock_parent == False:
            row.prop(props, "lock_parent", icon="UNLOCKED", text="")
        else:
            row.prop(props, "lock_parent", icon="LOCKED", text="")
        
        #if props.collection_parent is None:
        if props.lock_parent == False or props.collection_parent is None:
            row.menu("ITERATE_MODEL_MT_CollectionsMenuParent", icon="GROUP", text=MenuName1)
        else:
            row.prop(props.collection_parent, "name", icon="GROUP", text="")
            
        row.operator("iteratemodel.collection_ops", icon="ADD", text="").type = "NEW_COLLECTION"
        
        #Active Collection
        row = col.row(align=True)
        row.label(text="Active Collection:")
        
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
            row.menu("ITERATE_MODEL_MT_CollectionsMenuActive", icon="GROUP", text=MenuName2)
        else:
            row.prop(props.collection_active, "name", icon="GROUP", text="")
            
        row.operator("iteratemodel.collection_ops", icon="ADD", text="").type = "NEW_GROUP"
        
        #Duplicate Button
        row = col.row(align=True)
        row.operator("iteratemodel.duplicating_ops", icon="DUPLICATE", text="Iterate").type = "DUPLICATE"
        
        row = col.row(align=True)
        row.label(text="Iterations:")
        #TOP
        
        split = layout.row(align=False)
        col = split.column(align=True)
        
        row = col.row(align=True)
        row.template_list("ITERATE_MODEL_UL_items", "custom_def_list", props, "collections", props, "IM_ULIndex", rows=3)
        
        if props.edit_mode == True:
            
            col = split.column(align=True)
            
            row = col.row(align=True)
            button = row.operator("iteratemodel.ui_list_ops", text="", icon="TRIA_UP")
            button.type = "UP"
            
            row = col.row(align=True)
            button = row.operator("iteratemodel.ui_list_ops", text="", icon="TRIA_DOWN")
            button.type = "DOWN"
            
            row = col.row(align=True)
            button = row.operator("iteratemodel.ui_list_ops", text="", icon="PANEL_CLOSE")
            button.type = "REMOVE"
            
            row = col.row(align=True)
            row.prop(props, "display_icons", text="", icon="OUTLINER_OB_MESH")
            
            row = col.row(align=True)
            row.prop(props, "edit_mode", text="", icon="TEXT")
        
        #End of CustomPanel

class ITERATE_MODEL_PT_IterationCollectionSettings(bpy.types.Panel):
    bl_label = "Iteration Collection Settings"
    bl_parent_id = "ITERATE_MODEL_PT_CustomPanel1"
    bl_space_type = "VIEW_3D"
    bl_region_type = 'UI'
    #bl_context = "output"
    bl_category = "Iterate Model"
    
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
        row.label(text="Toggle:")
        
        #row = col.row(align=True)
        
        split = col.row(align=False)
        #col = split.row(align=False)
        
        #row = col.row(align=False)
        split.operator("iteratemodel.toggle_hide_objects", text="All Objects")
        
        row = split.row(align=True)
        #row = col.row(align=True)
        row.prop(props, "hide_types", index=0, text="", icon="HIDE_OFF")
        row.prop(props, "hide_types", index=1, text="", icon="RESTRICT_RENDER_OFF")
        row.prop(props, "hide_types", index=2, text="", icon="RESTRICT_VIEW_OFF")
        
        split = col.row(align=False)
        split.operator("iteratemodel.toggle_hide_collections", text="All Collections")
        
        row = split.row(align=True)
        
        row.prop(props, "hide_types_collections", index=0, text="", icon="HIDE_OFF")
        row.prop(props, "hide_types_collections", index=1, text="", icon="RESTRICT_RENDER_OFF")
        row.prop(props, "hide_types_collections", index=2, text="", icon="RESTRICT_VIEW_OFF")
        
        row = col.row(align=True)
        row.prop(props, "hide_last")#, index=2, text="")
        
        col = layout.column()
        
        row = col.row(align=True)
        row.label(text="Align Array:")
        
        row = col.row(align=False)
        #row.label(text="Offset Axis")
        row.operator("iteratemodel.offset_collection", text="Offset Objects")#+str(round(props.master_offset, 2)))
        
        row = col.row(align=True)
        #row.alignment = "RIGHT"
        row.label(text="Offset")#.alignment = "RIGHT"
        row.prop(props, "master_offset", text="", icon="NONE", expand=True)
        
        #row = col.row(align=True)
        #row.label(text="Hide Objects when Iterating")
        row = col.row(align=True)
        row.label(text="Offset Axis")
        row.prop(props, "master_axis", text="", icon="EMPTY_AXIS")#, expand=True)
        
        row = col.row(align=True)
        row.operator("iteratemodel.offset_use_object", text="Select Move Iteration")
        
        col.separator()
        
        row = col.row(align=True)
        row.label(text="New Collection:")
        
        row = col.row(align=True)
        #row.prop(props, "group_name", text="Name", icon="NONE")
        row.label(text="Name")
        row.prop(props, "group_name", text="", icon="NONE")
        
        row = col.row(align=True)
        #row.label(text="Offset")
        row.prop(props, "reset_offsets")#, text=None, icon="ARROW_LEFTRIGHT")
        
        

class ITERATE_MODEL_PT_DisplaySettings(bpy.types.Panel):
    bl_label = "Display Settings"
    bl_parent_id = "ITERATE_MODEL_PT_CustomPanel1"
    bl_space_type = "VIEW_3D"
    bl_region_type = 'UI'
    #bl_context = "output"
    bl_category = "Iterate Model"
    
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
        row.prop(props, "edit_mode", text="Edit Mode", icon="TEXT")
        row.prop(props, "display_icons", text="Icons", icon="OUTLINER_OB_MESH")
        
        row = col.row(align=True)
        row.label(text="New Collection Name")
        
        #row = col.row(align=True)
        #row.prop(props, "group_name", text="Name", icon="NONE")
        #row.prop(props, "group_name", text="", icon="NONE")
        
        row = col.row(align=True)
        #row.label(text="Hide Objects when Iterating")
        
        col = layout.column(align=True)
        
        row = col.row(align=True)
        row.separator()
        
        if props.debug_mode == True:
            #Debug Operators
            row = col.row(align=True)
            row.label(text="Debug Ops:")
            
            row = col.row(align=True)
            row.operator("iteratemodel.debug", text="Delete All").type = "DELETE"
        

def ListOrderUpdate(self, context):
    scene = bpy.context.scene
    data = bpy.data
    props = scene.IM_Props
    #list_order "DUPLICATES" "RECENT" "CUSTOM"
    #list_reverse: "DESCENDING" "ASCENDING"
    
    reverseBool = False
    if props.list_reverse == "ASCENDING":
        reverseBool = True
        
    def returnOrder(a):
        #value = None
        if props.list_order == "DUPLICATES":
            return len(a.collection.objects)#a.duplicates
        if props.list_order == "RECENT":
            return a.recent
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

def printBruh(self, context):
    
    print("printBruh Update:")
    print("Collection Parent Name: "+self.collection_parent.name)
    
    return
    
def pollBruh(self, object):
    
    print("printBruh Update:")
    print("Collection Parent Name: "+str(object))
    
    return
    
class ITERATE_MODEL_PreferencesMenu(bpy.types.AddonPreferences):
    bl_idname = "iterate_model_addon_b2_80_v1_0"
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

class ITERATE_MODEL_CollectionObjects(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="", default="")
    collection: bpy.props.PointerProperty(name="Added Collections to List", type=bpy.types.Collection)
    object: bpy.props.PointerProperty(name="Object", type=bpy.types.Object)
    duplicates: bpy.props.IntProperty(name="Int", description="", default= 0, min=0)
    recent: bpy.props.IntProperty(name="Int", description="", default= 0, min=0)
    custom: bpy.props.IntProperty(name="Int", description="", default= 0, min=0)
    icon: bpy.props.StringProperty(name="Icon name for object", description="Used to display in the list", default="NONE")#, get=)#, update=checkIcon)
    
    offset: bpy.props.FloatProperty(name="Offset", description="Offset for Iterated Objects", default= 0.0)
    axis: bpy.props.EnumProperty(name="Object Axis Offset", items= [("X", "X", "X Axis"), ("Y", "Y", "Y Axis"), ("Z", "Z", "Z Axis")], default="X")
    
    index_offset: bpy.props.IntProperty(name="Offset", description="Offset for Iterated Objects", default= 0)
    
class ITERATE_MODEL_Props(bpy.types.PropertyGroup):
    collection_parent: bpy.props.PointerProperty(name="Collection to add Groups to", type=bpy.types.Collection, update=printBruh, poll=pollBruh)
    #Tries to set collection_parent's default to Master Collection
    
    collection_active: bpy.props.PointerProperty(name="Collection to add Collections for Object duplicates", type=bpy.types.Collection)
    
    #Booleans for locking collection of parent and active
    lock_parent: bpy.props.BoolProperty(name="Lock Collection of Parent", description="When locked, you can now edit the name of the selected collection", default=False)
    lock_active: bpy.props.BoolProperty(name="Lock Collection of Active", description="When locked, you can now edit the name of the selected collection", default=False)
    
    collections: bpy.props.CollectionProperty(type=ITERATE_MODEL_CollectionObjects)
    IM_ULIndex: bpy.props.IntProperty(name="List Index", description="UI List Index", default= 0, min=0)
    group_name: bpy.props.StringProperty(name="New Collection Name", description="Name used when creating a new collection for Active", default="Group")
    
    listDesc =  ["Displays List in order of how many duplicates each object has", "Displays List in the order they were created", "Displays List in order user specified"]
    listDesc2 =  ["List displays in Descending Order", "List displays in Ascending Order"]
    
    list_order: bpy.props.EnumProperty(name="Display Mode", items= [("DUPLICATES", "Duplicates", listDesc[0], "DUPLICATE", 0), ("RECENT", "Recent", listDesc[1], "SORTTIME", 1), ("CUSTOM", "Custom", listDesc[2], "ARROW_LEFTRIGHT", 2)], description="Display Mode of List", default="DUPLICATES", update=ListOrderUpdate)
    list_reverse: bpy.props.EnumProperty(name="Display Mode", items= [("DESCENDING", "Descending", listDesc2[0], "SORT_DESC", 0), ("ASCENDING", "Ascending", listDesc2[1], "SORT_ASC", 1)], description="Display Mode of List", default="DESCENDING", update=ListOrderUpdate)
    
    edit_mode: bpy.props.BoolProperty(name="Toggle Edit Mode", description="Toggles side bar buttons to edit the \"Iterate\" list", default=True)
    
    display_icons: bpy.props.BoolProperty(name="Display Icons", description="Display icons of objects in the list", default=True)
    
    debug_mode: bpy.props.BoolProperty(name="Display Debug Operators", description="To aid in Debugging Operators. Displayed in \"Display Settings\"", default=True)
    
    #For Iterate Collection Settings and Operators
    
    hide_types: bpy.props.BoolVectorProperty(name="Iterate Object Hide Types", description="Toggle Hidden Types of all except most Recent Duplicated Object", default= [True, True, True], size=3)
    
    hide_types_collections: bpy.props.BoolVectorProperty(name="Iterate Collection Hide Types", description="Toggle Hidden Types of all Iterate Collections", default= [False, True, True], size=3)
    
    #hide_types_last
    hide_last: bpy.props.BoolProperty(name="Exclude Recent Iteration", description="When using the operators for toggling \"all objects\"", default=False)
    
    listDesc4 =  ["Offset Axis: X", "Offset Axis: Y", "Offset Axis: Z"]
    
    master_axis: bpy.props.EnumProperty(name="Iterate Object Axis Offset", items= [("X", "X", listDesc4[0]), ("Y", "Y", listDesc4[1]), ("Z", "Z", listDesc4[2])], description="Set Axis for Offset", default="X")
    
    master_offset: bpy.props.FloatProperty(name="Offset", description="Offset for Iterated Objects", default= 1.0)#, min=0)
    
    reset_offsets: bpy.props.BoolProperty(name="Reset Object Offsets", description="Resets Iterated Object Offsets when an Active Collection Changes. (If user doesn't want the Iterated objects)", default=False)
    
    master_index_offset: bpy.props.IntProperty(name="Offset", description="Offset for Iterated Objects", default= 0)#, min=0)
    
    #listDesc3 =  ["Hide in Viewport: Temporarily hide in viewport", "Disable in Renders: Globally disable in Renders", "Disable in Viewports: Globally disable in Viewports"]
    
    #hide_types: bpy.props.EnumProperty(name="Iterate Object Hide Types", items= [("HIDE_SET", "hide_set", listDesc3[0], "HIDE_OFF", 0), ("HIDE_RENDER", "hide_render", listDesc3[1], "RESTRICT_RENDER_OFF", 1), ("HIDE_VIEWPORT", "hide_viewport", listDesc3[2], "RESTRICT_VIEW_OFF", 2)], description="Toggle Hidden Types of all except most Recent Duplicated Object", default="DESCENDING")
    
    #list_order: "DUPLICATES" "RECENT" "CUSTOM"
    #list_reverse: "DESCENDING" "ASCENDING"
    
#Classes that are registered
classes = (
    ITERATE_MODEL_OT_SelectCollection,
    ITERATE_MODEL_OT_GroupOperators,
    ITERATE_MODEL_OT_Duplicate,
    ITERATE_MODEL_OT_OffsetCollection,
    ITERATE_MODEL_OT_OffsetUse,
    
    ITERATE_MODEL_OT_ToggleHideObjects,
    ITERATE_MODEL_OT_ToggleHideCollections,
    ITERATE_MODEL_OT_Debugging,
    ITERATE_MODEL_OT_UIOperators,
    
    ITERATE_MODEL_UL_items,
    ITERATE_MODEL_MT_CollectionsMenuParent,
    ITERATE_MODEL_MT_CollectionsMenuActive,
    
    ITERATE_MODEL_PT_CustomPanel1,
    ITERATE_MODEL_PT_IterationCollectionSettings,
    ITERATE_MODEL_PT_DisplaySettings,
    
    ITERATE_MODEL_PreferencesMenu,
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
