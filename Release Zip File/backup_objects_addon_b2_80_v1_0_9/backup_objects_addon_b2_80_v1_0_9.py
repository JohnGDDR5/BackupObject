
import bpy
        
from bpy.props import *
    
# Takes in an object as parameter, and returns a string of variable "icon"
def objectIcon(object):
    scene = bpy.context.scene
    data = bpy.data
    props = scene.BO_Props
    
    # icons = ["OUTLINER_OB_EMPTY", "OUTLINER_OB_MESH", "OUTLINER_OB_CURVE", "OUTLINER_OB_LATTICE", "OUTLINER_OB_META", "OUTLINER_OB_LIGHT", "OUTLINER_OB_IMAGE", "OUTLINER_OB_CAMERA", "OUTLINER_OB_ARMATURE", "OUTLINER_OB_FONT", "OUTLINER_OB_SURFACE", "OUTLINER_OB_SPEAKER", "OUTLINER_OB_FORCE_FIELD", "OUTLINER_OB_GREASEPENCIL", "OUTLINER_OB_LIGHTPROBE"]
    # Object Type
    
    icon = "QUESTION"
    
    # schema: "Object Type": "Icon Name"
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
        "VOLUME": "OUTLINER_OB_VOLUME",
    }
    
    # If there is an object to see if it has a type
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

class BACKUP_OBJECTS_OT_select_collection(bpy.types.Operator):
    bl_idname = "backup_objects.select_collection"
    bl_label = "Select Collection"
    bl_description = "Sets Parent collection for Backups"
    bl_options = {'UNDO',}
    type: bpy.props.StringProperty(default="DEFAULT")
    index: bpy.props.IntProperty(default=0, min=-1)
    
    def execute(self, context):
        scene = bpy.context.scene
        props = scene.BO_Props
                
        if self.type == "SELECT_ACTIVE":
            props.master_collection = bpy.data.collections[self.index]
            
        self.type == "DEFAULT"
        
        return {'FINISHED'}

class BACKUP_OBJECTS_OT_group_operators(bpy.types.Operator):
    bl_idname = "backup_objects.collection_ops"
    bl_label = "Create a new Collection"
    bl_description = "Creates a new Parent/Master Collection where new Backup collections for Objects are created."
    bl_options = {'UNDO',}
    type: bpy.props.StringProperty(default="DEFAULT")
    index: bpy.props.IntProperty(default=0, min=0)
    
    def execute(self, context):
        scene = bpy.context.scene
        props = scene.BO_Props
        
        # New Collection Group inside Parent Collection and set as Active Collection
        if self.type == "NEW_GROUP":
            
            new_master_collection = bpy.data.collections.new(props.new_collection_name)
            # Links new_master_collection2 to master_collection
            props.master_collection = new_master_collection
            
            # Links new collection to Master_Collection
            bpy.context.scene.collection.children.link(new_master_collection)
            
            # Note for For Loop Bellow: For every props.collections[].collection, create a new collection and set that as the pointer to the collections[].collection so each object gets a new collection
            
            # Removes collections from all BO_Props.collections.collection
            for i in enumerate(props.collections):
                i[1].collection = None
                
        self.type == "DEFAULT"
        
        return {'FINISHED'}

# UI functions for handling correct grammar
class STRING_REPORT_FUNCTIONS:
    def report_objects(self, some_list):
        return "Objects" if some_list > 1 else "Object"

class BACKUP_OBJECTS_OT_duplicate(bpy.types.Operator, STRING_REPORT_FUNCTIONS):
    bl_idname = "backup_objects.duplicating_ops"
    bl_label = "Backups active objects."
    bl_description = "Duplicates active objects and sends their collection in the Parent Collection"
    bl_options = {'UNDO',}
    
    type: bpy.props.StringProperty(default="DEFAULT")
    index: bpy.props.IntProperty(default=0, min=0)
    
    @classmethod
    def poll(cls, context):
        scene = bpy.context.scene
        props = scene.BO_Props
        
        return context.active_object is not None
    
    def execute(self, context):
        scene = bpy.context.scene
        props = scene.BO_Props
        # inputs = context.preferences.inputs
        # bpy.context.preferences.inputs.view_rotate_method
        
        if self.type == "DUPLICATE":
            
            # previous_mode saves the previous mode of the object
            previous_mode = str(bpy.context.object.mode)
            
            # .mode_set() operator changes the mode of the object to "OBJECT" mode for the .duplicate_move() operator to work
            if previous_mode != "OBJECT":
                bpy.ops.object.mode_set(mode="OBJECT")
                
            # Creates a new master_collection if there isn't one already
            if props.master_collection is None:
                new_master_col = bpy.data.collections.new(props.new_collection_name)
                # Sets master_collection as new_master_col
                props.master_collection = new_master_col
                
                bpy.context.scene.collection.children.link(new_master_col)
            
            # Requires some selected objects to do anything
            if len(bpy.context.selected_objects) > 0:
                
                previous_active = bpy.context.active_object
                
                # This is to not Backup Armatures when in Weight Paint Mode - TOP
                previous_selected = bpy.context.selected_objects
                previous_selected_unselected = [] # Objects that were selected but aren't for Backups
                previous_unselected_selected = [] # Objects that weren't selected but were for Backups
                
                new_backup_count = 0 # For Report String
                boolean_count = 0

                # Checks if you don't want to Backup Armatures when Weight Painting an Object
                if props.exclude_armature == True and previous_mode == "WEIGHT_PAINT" :
                    
                    for i in previous_selected:
                        if i.type == "ARMATURE":
                            i.select_set(False)
                            previous_selected_unselected.append(i)
                            
                    # Since there are less selected objects, it needs to be reassigned
                    previous_selected = bpy.context.selected_objects
                            
                
                # BOTTOM
                
                # For only active object
                # Checks if you only want to Backup the Active Object
                if props.only_active == True :
                    for i in previous_selected:
                        if i is not previous_active:
                            i.select_set(False)
                            previous_selected_unselected.append(i)
                            
                    # Must be a list with a comma, or else it isn't Iterable for enumerate()
                    previous_selected = [previous_active, ]

                # New Code 2/25/2021 Added support for including Boolean Objects, for BoxCutter addon workflows.
                # TOP

                previous_selected = select_bool_objects(props, previous_selected)
                if previous_selected[1] is not None: previous_unselected_selected.extend(previous_selected[1])
                boolean_count = previous_selected[2] # Number of Booleans to Back Up
                previous_selected = previous_selected[0] # Previous one was 2 lists, so just the 1st one
                # BOTTOM
                
                # Duplicates selected objects in previous_selected
                bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0.0, 0.0, 0.0), "orient_type":'GLOBAL'})
                
                total_objects_backed = len(bpy.context.selected_objects)

                # Iterates through all selected objects
                for i in enumerate(previous_selected):
                    existingCol = None
                    
                    # All objects in previous_selected have been deselected, and all duplicated objects have been selected in "ob"
                    ob = bpy.context.selected_objects[i[0]]
                    
                    # Unlinks duplicate from all collections it is linked to
                    for k in enumerate(ob.users_collection):
                        k[1].objects.unlink(ob)
                    
                    # Iterates through all BO_Props.collections
                    for j in enumerate(props.collections):
                        # If object is already registered in props.collections:object
                        if i[1] == j[1].object:
                            existingCol = j[1]
                            
                            # Ceate Backup collection if BO_Props.collections[].collection is None (Ex. when a New Group collection is made)
                            if j[1].collection is None:
                                new_backup_col = bpy.data.collections.new(i[1].name )
                                # Sets BO_Props.collections' collection
                                j[1].collection = new_backup_col
                                # Hides new collection
                                new_backup_col.hide_viewport = True
                                
                                props.master_collection.children.link(new_backup_col)
                            
                            # Links duplicated object to existing collection
                            j[1].collection.objects.link(ob)
                            j[1].name = j[1].collection.name
                            
                            break
                    
                    
                    # If object wasn't found inside props.collections as .object
                    if existingCol == None:
                        new_backup_count += 1
                        # new_group_name = props.new_collection_name
                        new_group_name = i[1].name
                        
                        new_backup_col_2 = bpy.data.collections.new(new_group_name )
                        # Links new_backup_col_2 to master_collection
                        props.master_collection.children.link(new_backup_col_2 )
                        
                        # Links duplicate to new_backup_col_2 collection
                        new_backup_col_2.objects.link(ob)
                        
                        # Adds Backup collection
                        propsCol = props.collections.add()
                        propsCol.collection = new_backup_col_2
                        propsCol.object = i[1]

                        propsCol.name = new_backup_col_2.name # Makes the name of Backup Object
                        propsCol.recent += len(props.collections) # Adds the index of the order of created
                        propsCol.custom += len(props.collections) # Custom Index will be in order if it is a new props.collection
                        propsCol.icon = objectIcon(propsCol.object) # Adds icon name to props.collection object to display in Viewport
                        
                        # Auto Hides Collection
                        propsCol.collection.hide_viewport = True
                        propsCol.collection.hide_render  = True
                    
                    # Unselects duplicated object (Since they aren't the originally selected)
                    ob.select_set(False)
                    # Selects previously selected object
                    previous_selected[i[0]].select_set(True)
                
                # Reselects Previously Unselected Objects that weren't Backed up
                for i in previous_selected_unselected:
                    i.select_set(True)
                # Unselects Boolean Objects that weren't selected to be Backed up
                for i in previous_unselected_selected:
                    i.select_set(False)
                    
                # selects previously active object
                previous_active.select_set(True)
                # Sets previously active object as active
                bpy.context.view_layer.objects.active = previous_active
                
                # String Report
                """
                def report_objects(some_list):
                    return "Objects" if some_list > 1 else "Object" """
                report_new_objects = ". %s New %s" % (new_backup_count, self.report_objects(new_backup_count) ) if new_backup_count > 0 else ""
                report_boolean_count = ". %s Boolean" % (boolean_count) if boolean_count > 0 else ""
                self.report({'INFO'}, "Backed %d %s%s%s" % (total_objects_backed, self.report_objects(total_objects_backed), report_new_objects, report_boolean_count ) )
            else:
                reportString = "No Objects Selected. 0 Objects Duplicated"
                
                self.report({'INFO'}, reportString)
            
            # Calls the update function ListOrderUpdate to change locations of props.collections
            ListOrderUpdate(self, context)
            
            # Sets BO_ULIndex as index of previously active context object
            if props.index_to_new == True:
            
                for i in enumerate(props.collections):
                    if i[1].object == previous_active:
                        props.BO_ULIndex = i[0]
                        break
            
            # Changes the Mode of the active object back to its previous mode.
            bpy.ops.object.mode_set(mode=previous_mode)
                        
        self.type == "DEFAULT"
        
        return {'FINISHED'}

class BACKUP_OBJECTS_OT_duplicate_all(bpy.types.Operator, STRING_REPORT_FUNCTIONS):
    bl_idname = "backup_objects.duplicating_all_ops"
    bl_label = "Backups all Backup Objects."
    bl_description = "Backs up All Backup objects"
    bl_options = {'UNDO',}
    
    @classmethod
    def poll(cls, context):
        scene = bpy.context.scene
        props = scene.BO_Props
        
        return context.active_object is not None
    
    def execute(self, context):
        scene = bpy.context.scene
        props = scene.BO_Props
        
        # previous_mode saves the previous mode of the object
        previous_mode = str(bpy.context.object.mode)
        
        # .mode_set() operator changes the mode of the object to "OBJECT" mode for the .duplicate_move() operator to work
        if previous_mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
            
        # Creates a new master_collection if there isn't one already
        if props.master_collection is None:
            new_master_col = bpy.data.collections.new(props.new_collection_name)
            # Sets master_collection as new_master_col
            props.master_collection = new_master_col
            
            bpy.context.scene.collection.children.link(new_master_col)
        
        # Requires some selected objects to do anything
        if len(props.collections) > 0:
            
            previous_active = bpy.context.active_object
            
            # This is to not Backup Armatures when in Weight Paint Mode - TOP
            previous_selected = list(bpy.context.selected_objects)

            # Unselects All Selected Objects   
            for i in bpy.context.selected_objects:
                i.select_set(False)
            
            # Selects objects that have Backups
            for j in enumerate(props.collections):
                if j[1].object is not None:
                    # Since some deleted objects can still be tracked by the Pointer, they won't be selectable in the 3D ViewLayer
                    if j[1].object.visible_get() == True:
                        j[1].object.select_set(True)
            
            selected_backups = list(bpy.context.selected_objects)
            # Duplicates selected objects in previous_selected
            bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0.0, 0.0, 0.0), "orient_type":'GLOBAL'})
            
            selected_backup_duplicates = list(bpy.context.selected_objects)
            total_objects_backed = len(selected_backups)
            
            for i in enumerate(selected_backups ):
                
                # All objects in previous_selected have been deselected, and all duplicated objects have been selected in "ob"
                ob = selected_backup_duplicates[i[0]]
                
                # Unlinks duplicate from all collections it is linked to
                for k in enumerate(ob.users_collection):
                    k[1].objects.unlink(ob)
                
                # Iterates through all BO_Props.collections
                for j in enumerate(props.collections):
                    # If object is already registered in props.collections:object
                    if i[1] == j[1].object:
                        
                        # Ceate Backup collection if BO_Props.collections[].collection is None (Ex. when a New Group collection is made)
                        if j[1].collection is None:
                            new_backup_col = bpy.data.collections.new(i[1].name )
                            # Sets BO_Props.collections' collection
                            j[1].collection = new_backup_col
                            # Hides new collection
                            new_backup_col.hide_viewport = True
                            
                            props.master_collection.children.link(new_backup_col)
                        
                        # Links duplicated object to existing collection
                        j[1].collection.objects.link(ob)
                        j[1].name = j[1].collection.name
                        
                        break
                
                # Unselects duplicated object (Since they aren't the originally selected)
                ob.select_set(False)
                
            # Reselects Previously Unselected Objects that weren't Backed up
            #for i in previous_selected_unselected:
            for i in previous_selected:
                i.select_set(True)
                
            # selects previously active object
            previous_active.select_set(True)
            # Sets previously active object as active
            bpy.context.view_layer.objects.active = previous_active
            
            # String Report
            #report_objects = "Objects" if total_objects_backed > 1 else "Object"
            reportString = "Backed %d %s" % (total_objects_backed, self.report_objects(total_objects_backed) )
        else:
            reportString = "No Backup Collections to Backup"
            
        self.report({'INFO'}, reportString)
        
        # Calls the update function ListOrderUpdate to change locations of props.collections
        ListOrderUpdate(self, context)
        
        # Sets BO_ULIndex as index of previously active context object
        if props.index_to_new == True:
        
            for i in enumerate(props.collections):
                if i[1].object == previous_active:
                    props.BO_ULIndex = i[0]
                    break
        
        # Changes the Mode of the active object back to its previous mode.
        bpy.ops.object.mode_set(mode=previous_mode)
                        
        #self.type == "DEFAULT"
        
        return {'FINISHED'}

def select_bool_objects(props, previous_selected):
    ## Returns modified previous_selected, and list of objects to unselect after duplication
    #props = scene.BO_Props
    boolean_count = 0
    previous_unselected_selected = []
    # New Code 2/25/2021 Added support for including Boolean Objects, for BoxCutter addon workflows.
    # TOP
    if props.include_bool_objects == True :
        for i in previous_selected:
            if len(i.modifiers) > 0:
                for j in i.modifiers:
                    if j.name == 'Boolean': ## Only looks for Boolean modifiers
                        j_ob = j.object
                        if j_ob is not None:
                            
                            if j_ob.select_get() is False: ## If it wasn't selected when BackingUp
                                previous_unselected_selected.append(j_ob)

                            j_ob.select_set(True) # selects it for duplicating
                            boolean_count += 1

    # If Bool Objects are selected, must reasign previous_selected
    previous_selected = bpy.context.selected_objects
    # BOTTOM
    
    return [previous_selected, previous_unselected_selected, boolean_count]

class BACKUP_OBJECTS_OT_full_backup(bpy.types.Operator, STRING_REPORT_FUNCTIONS):
    bl_idname = "backup_objects.full_backup_ops"
    bl_label = "Backs up all selected Backup Objects and sends them to a \"Full Backup\" Collection."
    bl_description = "Backs up All Backup objects"
    bl_options = {'UNDO', 'REGISTER'}
    
    only_backups: bpy.props.BoolProperty(name="Only Backups", description=" Only Full Backups of already Backed up Objects. Won't create new Backup Objects from selection.", default=False)

    @classmethod
    def poll(cls, context):
        scene = bpy.context.scene
        props = scene.BO_Props
        
        return context.active_object is not None
    
    def execute(self, context):
        scene = bpy.context.scene
        props = scene.BO_Props
        
        # previous_mode saves the previous mode of the object
        previous_mode = str(bpy.context.object.mode)
        
        # .mode_set() operator changes the mode of the object to "OBJECT" mode for the .duplicate_move() operator to work
        if previous_mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
            
        # Creates a new master_collection if there isn't one already
        # bpy.data.collections.get("Full Backups") is not None
        if props.full_backups_collection is None:
            new_master_col = bpy.data.collections.new("Full Backups")
            # Sets master_collection as new_master_col
            props.full_backups_collection = new_master_col
            
            bpy.context.scene.collection.children.link(new_master_col)
        
        # New Full Backup Collection
        new_full_backup_col = bpy.data.collections.new("Full Backup %s" % (len(props.full_backups_collection.children) + 1 ) )
        # Hides new collection
        new_full_backup_col.hide_viewport = True
        new_full_backup_col.hide_render = True
        # Links collection to scene
        props.full_backups_collection.children.link(new_full_backup_col)
        
        previous_active = bpy.context.active_object
        
        # This is to not Backup Armatures when in Weight Paint Mode - TOP
        previous_selected = list(bpy.context.selected_objects)

        previous_unselected_selected = [] # Objects that weren't selected but were for Backups

        # New Code 2/25/2021 Added support for including Boolean Objects, for BoxCutter addon workflows.
        # TOP

        previous_selected = select_bool_objects(props, previous_selected)
        if previous_selected[1] is not None: previous_unselected_selected.extend(previous_selected[1])
        boolean_count = previous_selected[2] # Number of Booleans to Back Up
        previous_selected = previous_selected[0] # Previous one was 2 lists, so just the 1st one
        # BOTTOM

        # If you only want existing Backup Objects to be Fully BackedUp
        if self.only_backups == True:
            if len(props.collections) > 0:
                # Unselects All Selected Objects   
                for i in bpy.context.selected_objects:
                    i.select_set(False)
                
                # Selects objects that have Backups
                for j in enumerate(props.collections):
                    if j[1].object is not None:
                        # Since some deleted objects can still be tracked by the Pointer, they won't be selectable in the 3D ViewLayer
                        if j[1].object.visible_get() == True:
                            j[1].object.select_set(True)
        
        selected_backups = list(bpy.context.selected_objects)

        if len(selected_backups) > 0:
            # Duplicates selected objects in previous_selected
            bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0.0, 0.0, 0.0), "orient_type":'GLOBAL'})
            
            selected_backup_duplicates = list(bpy.context.selected_objects)
            total_objects_backed = len(selected_backups)
            
            for ob in selected_backup_duplicates:

                # Unlinks duplicate from all collections it is linked to
                for k in enumerate(ob.users_collection):
                    k[1].objects.unlink(ob)
                
                # Links object to new Full Backup Collection
                new_full_backup_col.objects.link(ob)
                # Unselects duplicated object (Since they aren't the originally selected)
                ob.select_set(False)
                    
            # Reselects Previously Unselected Objects that weren't Backed up
            for i in previous_selected:
                i.select_set(True)
            # Unselects Boolean Objects that weren't selected to be Backed up
            for i in previous_unselected_selected:
                i.select_set(False)

            # selects previously active object
            previous_active.select_set(True)
            # Sets previously active object as active
            bpy.context.view_layer.objects.active = previous_active
                
            # String Report
            #report_objects = "Objects" if total_objects_backed > 1 else "Object"
            report_boolean_count = ". %s Boolean" % (boolean_count) if boolean_count > 0 else ""
            reportString = "Backed %d/%d %s%s" % (total_objects_backed, len(previous_selected), self.report_objects(total_objects_backed), report_boolean_count )
        else:
            reportString = "No Backup Objects to Backup"
            
        self.report({'INFO'}, reportString)
        
        # Changes the Mode of the active object back to its previous mode.
        bpy.ops.object.mode_set(mode=previous_mode)
                        
        #self.type == "DEFAULT"
        
        return {'FINISHED'}

class BACKUP_OBJECTS_OT_swap_backup_object(bpy.types.Operator, STRING_REPORT_FUNCTIONS):
    bl_idname = "backup_objects.swap_backup_object"
    bl_label = "Swaps Selected Object from Backups"
    bl_description = "Swaps Selected Object if it is inside the Backups of Active Object"
    bl_options = {'UNDO',}
    
    @classmethod
    def poll(cls, context):
        scene = bpy.context.scene
        props = scene.BO_Props
        
        return context.active_object is not None
    
    def execute(self, context):
        scene = bpy.context.scene
        props = scene.BO_Props
        
        # previous_mode saves the previous mode of the object
        previous_mode = str(bpy.context.object.mode)
        previous_object_type = str(bpy.context.object.type)
        
        # .mode_set() operator changes the mode of the object to "OBJECT" mode for the .duplicate_move() operator to work
        if previous_mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
            
        # Creates a new master_collection if there isn't one already
        if props.master_collection is None:
            new_master_col = bpy.data.collections.new(props.new_collection_name)
            # Sets master_collection as new_master_col
            props.master_collection = new_master_col
            
            bpy.context.scene.collection.children.link(new_master_col)
        
        # Requires some selected objects to do anything
        if len(props.collections) > 0:
            
            previous_active = bpy.context.active_object
            # .users_collection returns a tuple of collections an object is in
            previous_active_collection = previous_active.users_collection[0]
            
            def props_backup(ob):
                for i in props.collections:
                    if ob == i.object:
                        return i
                return None

            props_backup = props_backup(previous_active)

            if len(bpy.context.selected_objects) == 2:
                # Checks if Active object has been Backed Up, else there is no reason to swap
                if props_backup is not None:
                        
                    # This is to not Backup Armatures when in Weight Paint Mode - TOP
                    previous_selected = list(bpy.context.selected_objects)

                    # Gets the 2nd object that was selected
                    object_from_backups = previous_selected[1] if previous_selected[0] is previous_active else previous_selected[0]
                    
                    object_from_backups_collection = object_from_backups.users_collection[0] # Gets the 1st collection the object is in, may change later

                    # Sorts the previous_selected so that previous_active is always first
                    if previous_selected[1] is previous_active:
                        previous_selected.remove(object_from_backups)
                        previous_selected.append(object_from_backups)

                    # Unlinks objects from their previous collections
                    for i in previous_selected:
                        for j in i.users_collection:
                            j.objects.unlink(i)
                    
                    # Links the Objects to their opposite collections
                    previous_active_collection.objects.link(object_from_backups) # Backup to Previous
                    object_from_backups_collection.objects.link(previous_active) # Previous to Backup

                    # Sets the Active Object to selected object
                    bpy.context.view_layer.objects.active = object_from_backups

                    # Swaps the hide options
                    def swap_hide_options(ob1, ob2):
                        ob1_hide_set = ob1.hide_get()
                        ob1_hide_viewport = ob1.hide_viewport
                        ob1_hide_render = ob1.hide_render

                        ob1.hide_set(ob2.hide_get() )
                        ob1.hide_viewport = ob2.hide_viewport
                        ob1.hide_render = ob2.hide_render

                        ob2.hide_set(ob1_hide_set )
                        ob2.hide_viewport = ob1_hide_viewport
                        ob2.hide_render = ob1_hide_render

                    swap_hide_options(previous_active, object_from_backups)
                    
                    # Sets the New Tracking/Pointer object to the Swapped Object
                    props_backup.object = object_from_backups

                    # String Report
                    #report_objects = "Objects" if total_objects_backed > 1 else "Object"
                    #reportString = "Backed %d %s" % (total_objects_backed, self.report_objects(total_objects_backed) )
                    reportString = "Swapped \'%s\' with \'%s\'. Now Tracking swapped object in %s" % (previous_active.name, object_from_backups.name, object_from_backups_collection.name  )
                else:
                    reportString = "Active Object doesn't have a Backup"
            else:
                if len(bpy.context.selected_objects) > 2:
                    reportString = "Only 2 Objects need to be selected with 1 active"
                else:
                    reportString = "2 Objects need to be selected"
        else:
            reportString = "No Backup Collections to Backup"
            
        self.report({'INFO'}, reportString)
        
        # Calls the update function ListOrderUpdate to change locations of props.collections
        ListOrderUpdate(self, context)
        
        # Changes the Mode of the active object back to its previous mode.
        if str(bpy.context.active_object.type) == previous_object_type:
            bpy.ops.object.mode_set(mode=previous_mode)
        else:
            bpy.ops.object.mode_set(mode="OBJECT")
                        
        #self.type == "DEFAULT"
        
        return {'FINISHED'}

class BACKUP_OBJECTS_OT_select_backup_ob_and_col(bpy.types.Operator, STRING_REPORT_FUNCTIONS):
    bl_idname = "backup_objects.select_backup_ob_and_col"
    bl_label = "Select Backup Object or Collection"
    bl_description = "Select Backup Object or Collection of active Backup"
    bl_options = {'UNDO',}
    
    type: bpy.props.StringProperty(default="DEFAULT")

    @classmethod
    def poll(cls, context):
        scene = bpy.context.scene
        props = scene.BO_Props
        
        return context.active_object is not None
    
    def execute(self, context):
        scene = bpy.context.scene
        props = scene.BO_Props
        
        # Selects Object of Active Backup of UI List
        if self.type == "LIST_BACKUP_OBJECT":
            if len(props.collections) > 0:
                props_backup = props.collections[props.BO_ULIndex ] # Active Backup in UI List

                if props_backup.object is not None:
                    # If Object is in the 3D viewport
                    if props_backup.object.visible_get() == True:
                        # Sets active object
                        props_backup.object.select_set(True)
                        # Sets the object as Active Object if there isn't an Active Object
                        if bpy.context.view_layer.objects.active is None:
                            bpy.context.view_layer.objects.active = props_backup.object
                        reportString = "Selected \'%s\' Object" % (props_backup.object.name)
                    else:
                        reportString = "\'%s\' Object not in 3D Viewport" % (props_backup.object.name)
                else:
                    reportString = "Backup has no Object Pointed at"
            else:
                reportString = "No Backups to Select From"
        # Selects Collection of Active Backup of UI List
        elif self.type == "LIST_BACKUP_COLLECTION":
            if len(props.collections) > 0:
                props_backup = props.collections[props.BO_ULIndex ] # Active Backup in UI List

                if props_backup.collection is not None:
                    props_backup_layer_collection = None

                    def getLayerCollection(layer_collection, collection):#, props_backup_layer_collection):
                        nonlocal props_backup_layer_collection
                        #props_backup_layer_collection = None
                        
                        if layer_collection.name == collection.name:
                            props_backup_layer_collection = layer_collection
                            return
                        else:
                            for i in layer_collection.children:
                                if props_backup_layer_collection is None:
                                    #print("i: %s, child: %s" % (i.name, collection.name) )
                                    if len(i.children) > 0:
                                        #print("children: %d" % (len(i.children)) )
                                        for j in i.children:
                                            getLayerCollection(j, collection)#, props_backup_layer_collection)
                                    if i.name == collection.name:
                                        #print("OOF 2")
                                        props_backup_layer_collection = i
                                        break
                                else:
                                    #print("OOF")
                                    break
                        return  #object type is LayerCollection, not Collection
                    getLayerCollection(context.view_layer.layer_collection, props_backup.collection)
                    
                    #print("props_backup_layer_collection: %s" % (str(props_backup_layer_collection)) )
                    bpy.context.view_layer.active_layer_collection = props_backup_layer_collection

                    reportString = "Selected Collection \'%s\' of \'%s\' Object" % (props_backup.collection.name, props_backup.object.name)
                else:
                    reportString = "Object doesn't have a Backup Collection"
            else:
                reportString = "No Backups to Select From"
        
        else:
            reportString = "No Type Set"
            
        self.report({'INFO'}, reportString)
        
        # Calls the update function ListOrderUpdate to change locations of props.collections
        #ListOrderUpdate(self, context)
                        
        self.type == "DEFAULT"
        
        return {'FINISHED'}

class BACKUP_OBJECTS_OT_cleaning(bpy.types.Operator):
    bl_idname = "backup_objects.cleaning_ops"
    bl_label = "Cleaning/Deleting Operators "
    bl_description = "Deletes oldest objects in Iteration Collections up to the most recent user set to leave. Also opearators to clean the UI list with previous Objects set to be backed up that have been or their collection deleted."
    bl_options = {'UNDO',}
    
    type: bpy.props.StringProperty(default="DEFAULT")
    # index: bpy.props.IntProperty(default=0, min=0)
    
    # Brings a pop-up to confirm operator
    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        scene = bpy.context.scene
        props = scene.BO_Props
        
        # Deletes Objects inside Backup Object collections, except most recent ammounts given by user
        if self.type == "CLEAN_COLLECTION_OBJECTS":
        
            # Gets previous length of props.collections
            len_previous = len(props.collections)
            
            removed_objects = 0
            affected_collections = 0
            
            before = list(props.collections)
            # col_name = "[No Collection]"
            
            # Goes through every Backup Object
            for i in enumerate(props.collections):
                
                if i[1].collection != None:
                    col_name = str(i[1].collection.name)
                    
                    if i[1].object != None:
                        ob_name = str(i[1].object.name)
                    else:
                        ob_name = "[No Object]"
                        
                    # # 
                    last_slice_index = -int(props.clean_leave)
                    
                    # If last slice index is 0 and not negative, then it won't work
                    if last_slice_index == 0:
                        last_slice_index = len(i[1].collection.objects)
                        
                    # Everything but the last # of objects from props.clean_leave integer
                    list_rev = reversed(list(enumerate(i[1].collection.objects[:last_slice_index]) ))
                    # # 
                    
                    len_prev = len(i[1].collection.objects)
                    
                    removed = 0
                    
                    for j in list_rev:
                        bpy.data.objects.remove(j[1])
                        removed += 1;
                        
                    removed_objects += removed
                    
                    if removed > 0:
                        affected_collections += 1
                        
                    print("Index [%d]: Prev_Len: %d, Removed %d, [Object: %s; Collection: %s ]" % (i[0], len_prev, removed, ob_name, col_name))
                else:
                    pass
            
            # Prints the last ammount of different Backup Objects calculated
            reportString = "Removed: %d Backup Objects in %d Collections" % (removed_objects, affected_collections)
        
        # Deletes Backup Objects without an Object or Collection pointer
        elif self.type == "CLEAN_NOT_FOUND":
        
            # Gets previous length of props.collections
            len_previous = len(props.collections)
            
            len_diff = 0
            
            for i in reversed(list(enumerate(props.collections))):
                
                # if the object or collection is None
                if i[1].object == None or i[1].collection == None:
                    # object Name
                    if i[1].object != None:
                        ob_name = str(i[1].object.name)
                    else:
                        ob_name = "[No Collection]"
                        
                    # collection Name
                    if i[1].collection != None:
                        col_name = str(i[1].collection.name)
                    else:
                        col_name = "[No Collection]"
                        
                    print("Removed [%d]: [Object: %s; Collection: %s ]" % (i[0], ob_name, col_name))
                    
                    bpy.context.scene.BO_Props.collections.remove(i[0])
                    
                    len_diff += 1
            
            # Prints the last ammount of different Backup Objects calculated
            reportString = "Removed: ( %d/%d ) Backup Objects" % (len_diff, len_previous)
            
        self.type == "DEFAULT"
        #print(reportString)
        self.report({'INFO'}, reportString)
        
        return {'FINISHED'}

class BACKUP_OBJECTS_OT_removing(bpy.types.Operator):
    bl_idname = "backup_objects.removing_ops"
    bl_label = "Remove all but the ammount the user inputs for all Backup Objects"
    bl_description = "Duplicates active objects and sends them to the Active Collection"
    bl_options = {'UNDO',}
    
    type: bpy.props.StringProperty(default="DEFAULT")
    index: bpy.props.IntProperty(default=0, min=0)
    
    def execute(self, context):
        scene = bpy.context.scene
        props = scene.BO_Props
        
        if self.type == "PRINT":
            # Gets previous length of props.collections
            len_previous = len(props.collections)
            
            before = list(props.collections)
            
            for i in reversed(list(enumerate(before))):
                if len(i[1].collection.objects) == 1:
                    print("before[i[0]]: [%d]; Object.name: %s" % (i[0], before[i[0]].object.name))
                    del before[i[0]]
                    
        # Prints the Backup Objects with 1 or less objects
        elif self.type == "PRINT_DIFFERENT_1":
            # Gets previous length of props.collections
            len_previous = len(props.collections)
            
            len_diff = 0
            
            # before = list(props.collections)
            print("Backup Objects with 1 Object or Less in .Collection: ")
            
            for i in enumerate(props.collections):
                # Checks if i[1] has an object for a name
                if i[1].object != None:
                    ob_name = i[1].object.name
                else:
                    ob_name = "[No Object]"
                    
                col_name = "[No Collection]"
                objects = 0
                    
                # If there is a collection pointer
                if i[1].collection != None:
                    objects = len(i[1].collection.objects)
                    # Checks if there is 1 or less objects in the collection
                    if objects <= 1:
                        # Sets the col_name variable to collection name
                        col_name = i[1].collection.name
                        len_diff += 1
                # else:
                #    col_name = "[No Collection]"
                    
                if objects <= 1:
                    print("Index[%d] (Objects: %d) [Object: %s; Collection: %s ]" % (i[0], objects, ob_name, col_name))
                
            # Prints the last ammount of different Backup Objects calculated
            print("Different: ( %d/%d ) Backup Objects \n" % (len_diff, len_previous))
            
        # Fake "Deletes" Backup Objects without an Object or Collection pointer
        elif self.type == "CLEAN_TEST":
        
            # Gets previous length of props.collections
            len_previous = len(props.collections)
            
            len_diff = 0
            
            before = list(props.collections)
            
            for i in reversed(list(enumerate(before))):
                if i[1].object == None or i[1].collection == None:
                    # ob_name = ""
                    if i[1].object != None:
                        ob_name = str(i[1].object.name)
                    else:
                        ob_name = "[No Collection]"
                    # else:
                    if i[1].collection != None:
                        col_name = str(i[1].collection.name)
                    else:
                        col_name = "[No Collection]"
                        
                    print("Removed [%d]: [Object: %s; Collection: %s ]" % (i[0], ob_name, col_name))
                    
                    del before[i[0]]
                    
            print("Before: "+str(before[::]))
            
            # Prints the last ammount of different Backup Objects calculated
            print("Removed: ( %d/%d ) Backup Objects \n" % (len_diff, len_previous))
            
        self.type == "DEFAULT"
        
        return {'FINISHED'}
        
class BACKUP_OBJECTS_OT_debugging(bpy.types.Operator):
    bl_idname = "backup_objects.debug"
    bl_label = "Backup Objects Debugging Operators"
    bl_description = "To assist with debugging and development"
    bl_options = {'UNDO','REGISTER'}
    type: bpy.props.StringProperty(default="DEFAULT")
    # index: bpy.props.IntProperty(default=0, min=0)
    
    def invoke(self, context, event):
        # self.x = event.mouse_x
        # self.y = event.mouse_y
        if self.type != "DELETE_NUKE":
            return self.execute(context)
        else:
            print("MLG")
            wm = context.window_manager
            print(str(event))
            # invoke_props_popup(operator, event)
            # return wm.invoke_props_dialog(self)
            return wm.invoke_confirm(self, event)
    
    def execute(self, context):
        scene = bpy.context.scene
        props = scene.BO_Props
        
        # Mass deletion of every Iteration Object & their collections and objects inside them
        if self.type == "DELETE_NUKE":
            
            if props.master_collection is not None:
                removedObjects = 0
                removedCol = 0
                
                for i in enumerate(reversed(props.collections)):
                    if i[1].collection is not None:
                        for j in i[1].collection.objects:
                            removedObjects += 1
                            i[1].collection.objects.unlink(j)
                            
                        removedCol += 1
                        # Removes collection, but not other links of it incase the user linked it
                        bpy.data.collections.remove(i[1].collection, do_unlink=True)
                        
                    props.collections.remove(len(props.collections)-1)
                    
                colNameActive = props.master_collection.name
                    
                reportString = "Removed: [%s] & %d Objects & %d Collection Groups" % (colNameActive, removedObjects, removedCol)
                
                bpy.data.collections.remove(props.master_collection, do_unlink=True)
                
                print(reportString)
                self.report({'INFO'}, reportString)
            else:
                removedCol = 0
                
                # Removes scene.BO_Props.collections
                for i in enumerate(reversed(props.collections)):
                    props.collections.remove(len(props.collections)-1)
                    
                    removedCol += 1
                    
                reportString = "Removed: %d Collection Groups" % (removedCol)
                
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
            # Displays how many Iteration Objects don't have Objects or Collections
            print("No Objects: %d; No Collections: %d" % (no_objects, no_collections))
        
        # Adds 3 Backup Objects with missing Objects & Collections for testing.
        elif self.type == "TESTING":
            
            ob_1 = props.collections.add()
            ob_1.collection = bpy.data.collections[0]
            
            ob_2 = props.collections.add()
            ob_2.object = bpy.data.objects[0]
            
            ob_3 = props.collections.add()
            print("Added 3 Backup Objects.")
            
        # Copied from .remove_ops operator before.
        elif self.type == "PRINT":
            # Gets previous length of props.collections
            len_previous = len(props.collections)
            
            before = list(props.collections)
            
            for i in reversed(list(enumerate(before))):
                if len(i[1].collection.objects) == 1:
                    print("before[i[0]]: [%d]; Object.name: %s" % (i[0], before[i[0]].object.name))
                    del before[i[0]]
                    
        # Prints the Backup Objects with 1 or less objects
        elif self.type == "PRINT_DIFFERENT_1":
            # Gets previous length of props.collections
            len_previous = len(props.collections)
            
            len_diff = 0
            
            # before = list(props.collections)
            print("Backup Objects with 1 Object or Less in .Collection: ")
            
            for i in enumerate(props.collections):
                # Checks if i[1] has an object for a name
                if i[1].object != None:
                    ob_name = i[1].object.name
                else:
                    ob_name = "[No Object]"
                    
                col_name = "[No Collection]"
                objects = 0
                    
                # If there is a collection pointer
                if i[1].collection != None:
                    objects = len(i[1].collection.objects)
                    # Checks if there is 1 or less objects in the collection
                    if objects <= 1:
                        # Sets the col_name variable to collection name
                        col_name = i[1].collection.name
                        len_diff += 1
                # else:
                #    col_name = "[No Collection]"
                    
                if objects <= 1:
                    print("Index[%d] (Objects: %d) [Object: %s; Collection: %s ]" % (i[0], objects, ob_name, col_name))
                
            # Prints the last ammount of different Backup Objects calculated
            print("Different: ( %d/%d ) Backup Objects \n" % (len_diff, len_previous))
            
        # Fake "Deletes" Backup Objects without an Object or Collection pointer
        elif self.type == "CLEAN_TEST":
        
            # Gets previous length of props.collections
            len_previous = len(props.collections)
            
            len_diff = 0
            
            before = list(props.collections)
            
            for i in reversed(list(enumerate(before))):
                if i[1].object == None or i[1].collection == None:
                    # ob_name = ""
                    if i[1].object != None:
                        ob_name = str(i[1].object.name)
                    else:
                        ob_name = "[No Collection]"
                    # else:
                    if i[1].collection != None:
                        col_name = str(i[1].collection.name)
                    else:
                        col_name = "[No Collection]"
                        
                    print("Removed [%d]: [Object: %s; Collection: %s ]" % (i[0], ob_name, col_name))
                    
                    del before[i[0]]
                    
            print("Before: "+str(before[::]))
            
            # Prints the last ammount of different Backup Objects calculated
            print("Removed: ( %d/%d ) Backup Objects \n" % (len_diff, len_previous))
            
        elif self.type == "Bruh":
            print(("O"*10)+"F")
            
        # Resets default settings
        self.type == "DEFAULT"
        
        return {'FINISHED'}
        
class BACKUP_OBJECTS_OT_ui_operators_move(bpy.types.Operator):
    bl_idname = "backup_objects.ui_ops_move"
    bl_label = "List Operators"
    bl_description = "Operators for moving rows Up, Down and Deleting"
    bl_options = {'UNDO',}
    type: bpy.props.StringProperty(default="DEFAULT")
    sub: bpy.props.StringProperty(default="DEFAULT")
    # index: bpy.props.IntProperty(default=0, min=0)
    
    def execute(self, context):
        scene = bpy.context.scene
        props = scene.BO_Props
        active = props.BO_ULIndex
            
        # Sets list_order to "CUSTOM" when moving list rows UP or DOWN
        if props.list_order != "CUSTOM" and (self.type == "UP" or self.type == "DOWN"):
            if props.list_reverse == "DESCENDING":
                for i in enumerate(props.collections):
                    i[1].custom = i[0]
            else:
                for i in enumerate(reversed(props.collections)):
                    i[1].custom = i[0]
                
            props.list_order = "CUSTOM"
            print("Mc Bruh")
        
        # Moves list row UP
        if self.type == "UP":
            
            if self.sub == "DEFAULT":
                if active != 0:
                    props.collections.move(active, active-1)
                    props.BO_ULIndex-=1
                    
                else:
                    props.collections.move(0, len(props.collections)-1)
                    props.BO_ULIndex  = len(props.collections)-1
                    
            elif self.sub == "TOP":
                props.collections.move(active, 0)
                props.BO_ULIndex = 0
        
        # Moves list row DOWN
        elif self.type == "DOWN":
            
            if self.sub == "DEFAULT":
                if active != len(props.collections)-1:
                    props.collections.move(active, active+1)
                    props.BO_ULIndex += 1
                    
                else:
                    props.collections.move(len(props.collections)-1, 0)
                    props.BO_ULIndex = 0
                    
            elif self.sub == "BOTTOM":
                props.collections.move(active, len(props.collections)-1)
                props.BO_ULIndex = len(props.collections)-1
                
        elif self.type == "REMOVE" and len(props.collections) > 0:
            if self.sub == "DEFAULT":
                # If active is the last one
                if active == len(props.collections)-1:
                    props.collections.remove(props.BO_ULIndex)
                    
                    if len(props.collections) != 0:
                        props.BO_ULIndex -= 1
                        
                else:
                    props.collections.remove(props.BO_ULIndex)
            # Note: This only removes the props.collections, not the actual collections or 
            """
            elif self.sub == "ALL":
                props.collections.clear()
            """
                
                
        # Note: This only removes the props.collections, not the actual collections or objects
        elif self.type == "REMOVE_UI_ALL":
            props.collections.clear()
            
            reportString = "Removed all UI List elements. (Objects in Scene unaffected)" # % (active_object.name)
            
            self.report({'INFO'}, reportString)
                
        elif self.type == "SELECT_ACTIVE_UI":
            active_object = bpy.context.active_object
            if active_object != None:
                found = False
                
                for i in enumerate(props.collections):
                    if active_object == i[1].object:
                        props.BO_ULIndex = i[0]
                        found = True
                        break
                        
                if found == False:
                    reportString = "\"%s\" not in Iteration List" % (active_object.name)
                    
                    self.report({'INFO'}, reportString)
            else:
                reportString = "No Active Object"
                    
                self.report({'INFO'}, reportString)
            
        
        # Resets self props into "DEFAULT"
        self.type == "DEFAULT"
        self.sub == "DEFAULT"
        
        return {'FINISHED'}
        
class BACKUP_OBJECTS_OT_ui_operators_select(bpy.types.Operator):
    bl_idname = "backup_objects.ui_ops_select"
    bl_label = "Select List from Active Object"
    bl_description = "Selects list UI element of Active Object"
    bl_options = {'UNDO',}
    type: bpy.props.StringProperty(default="DEFAULT")
    sub: bpy.props.StringProperty(default="DEFAULT")
    # index: bpy.props.IntProperty(default=0, min=0)
    
    def execute(self, context):
        scene = bpy.context.scene
        props = scene.BO_Props
        active = props.BO_ULIndex
        
        if self.type == "SELECT_ACTIVE_UI":
            active_object = bpy.context.active_object
            if active_object != None:
                found = False
                
                for i in enumerate(props.collections):
                    if active_object == i[1].object:
                        props.BO_ULIndex = i[0]
                        found = True
                        break
                        
                if found == False:
                    reportString = "\"%s\" not in Iteration List" % (active_object.name)
                    
                    self.report({'INFO'}, reportString)
            else:
                reportString = "No Active Object"
                    
                self.report({'INFO'}, reportString)
            
        
        # Resets self props into "DEFAULT"
        self.type == "DEFAULT"
        self.sub == "DEFAULT"
        
        return {'FINISHED'}
        

class BACKUP_OBJECTS_UL_items(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        scene = bpy.context.scene
        data = bpy.data
        props = scene.BO_Props
        
        # active = props.RIA_ULIndex
        IMCollect = props.collections
        
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            
            row = layout.row(align=True)
            
            if len(IMCollect) > 0:
                # obItems
                if item.collection != None:
                    obItems = len(item.collection.objects)
                else:
                    obItems = 0
                
                # info = "%d. (%d)" % (index+1, obItems)
                info = ""
                # info = "%d. (%d)" % (index+1, obItems)
                if props.display_index == True:
                    if props.display_object_count == True:
                        info += "%d. " % (index+1)
                    else:
                        info += "%d" % (index+1)
                    
                if props.display_object_count == True:
                    info += "(%d)" % (obItems)
                # bpy.context.scene.BO_Props.collections.add()
                
                # Displays icon of objects in list
                if props.display_icons == True:
                    
                    if item.object != "EMPTY" and item.icon != "NONE":
                        row.label(text="", icon=item.icon)
                        
                    else:
                        # obIcon = objectIcon(item.object)
                        row.label(text="", icon="QUESTION")
                        
                # Checks if the item has an object pointed
                if item.object != None:
                    row.prop(item.object, "name", text=info, emboss=False)
                # This is for an Error Basically, if object isn't there
                else:
                    col = row.column()
                    # Grays this out
                    col.enabled = False
                    
                    col.prop(props, "error_object", text=info, emboss=False)
                
                if props.display_collections == True:
                    if item.collection != None:
                        row.prop(item.collection, "name", text="", icon="GROUP", emboss=False)
                        
                    else:
                        col = row.column()
                        # Grays this out
                        col.enabled = False
                        
                        col.prop(props, "error_collection", text="", icon="GROUP", emboss=False)
                    
            else:
                row.label(text="No Iterations Here")
                
        # Theres nothing in this layout_type since it isn't intended to be used.
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'

    def invoke(self, context, event):
        pass
        
class BACKUP_OBJECTS_MT_menu_select_collection(bpy.types.Menu):
    bl_idname = "BACKUP_OBJECTS_MT_menu_select_collection"
    bl_label = "Select a Collection for Active"
    bl_description = "Select an Parent Collection to create collections to send object iteration duplicates"
    
    # here you specify how they are drawn
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        data = bpy.data
        props = scene.BO_Props
        
        col = layout.column()
        
        row = col.row(align=True)
        
        if len(bpy.data.collections) > 0:
            for i in enumerate(bpy.data.collections):
                button = row.operator("backup_objects.select_collection", text=i[1].name)
                button.type = "SELECT_ACTIVE"
                button.index = i[0]
                
                row = col.row(align=True)
        else:
            # NEW_COLLECTION
            button = row.operator("backup_objects.collection_ops", text="Add Collection", icon = "ADD")
            button.type = "NEW_COLLECTION"
            # bpy.data.collections.new("Boi") 
        # row.prop(self, "ui_tab", expand=True)# , text="X")

class BACKUP_OBJECTS_MT_extra_backup_functions(bpy.types.Menu):
    bl_idname = "BACKUP_OBJECTS_MT_extra_backup_functions"
    bl_label = "Extra Backup Functions"
    bl_description = "Extra functions for Backups"
    
    # here you specify how they are drawn
    def draw(self, context):
        layout = self.layout

        scene = context.scene
        data = bpy.data
        props = scene.BO_Props
        
        col = layout.column()

        Dup_String_All = "Backup All Backups: %d" % (len(props.collections) )
        # row = col.row(align=True)
        button = col.operator("backup_objects.duplicating_all_ops", icon="DUPLICATE", text=Dup_String_All)

        row = col.row(align=True)
        row.operator("backup_objects.swap_backup_object", icon="DUPLICATE", text="Swap Objects")

        row = col.row(align=True)
        row.operator("backup_objects.full_backup_ops", icon="DUPLICATE", text="Full Backup")
        

class BACKUP_OBJECTS_MT_extra_ui_list_functions(bpy.types.Menu):
    bl_idname = "BACKUP_OBJECTS_MT_extra_ui_list_functions"
    bl_label = "Extra UI List Backup Functions"
    bl_description = "Extra functions for Backups UI List"
    
    # here you specify how they are drawn
    def draw(self, context):
        layout = self.layout

        scene = context.scene
        data = bpy.data
        props = scene.BO_Props
        
        col = layout.column()

        #Dup_String_All = "Backup All Backups: %d" % (len(props.collections) )
        # row = col.row(align=True)
        button = col.operator("backup_objects.select_backup_ob_and_col", icon="RESTRICT_SELECT_OFF", text="Select Backup Object")
        button.type = "LIST_BACKUP_OBJECT"

        button = col.operator("backup_objects.select_backup_ob_and_col", icon="RESTRICT_SELECT_OFF", text="Select Backup Collection")
        button.type = "LIST_BACKUP_COLLECTION"

        button = col.operator("backup_objects.ui_ops_select", icon="RESTRICT_SELECT_OFF", text="Select List of Active Object")
        button.type = "SELECT_ACTIVE_UI"
    
# Default Settings for Panels
class PANEL_DEFAULTS:
    bl_space_type = "VIEW_3D"
    bl_region_type = 'UI'
    # bl_context = "output"
    bl_category = "Backup"
    bl_options = {"DEFAULT_CLOSED"}

class BACKUP_OBJECTS_PT_custom_panel1(bpy.types.Panel): #, PANEL_DEFAULTS):
    # A Custom Panel in Viewport
    bl_idname = "BACKUP_OBJECTS_PT_custom_panel1"
    bl_label = "Backup Object"
    bl_space_type = "VIEW_3D"
    bl_region_type = 'UI'
    # bl_context = "output"
    bl_category = "Backup"
    #bl_options = {"DEFAULT_CLOSED"}

    # draw function
    def draw(self, context):
                 
        layout = self.layout
        scene = context.scene
        props = scene.BO_Props
        
        # Layout Starts
        col = layout.column()
        
        # Active Collection
        row = col.row(align=True)
        row.label(text="Parent Collection:")
        
        row = col.row(align=True)
        
        MenuName2 = "Select Collection"
        
        if props.master_collection is not None:
            MenuName2 = props.master_collection.name
            
        # Lock Icon
        if props.lock_active == False:
            row.prop(props, "lock_active", icon="UNLOCKED", text="")
        else:
            row.prop(props, "lock_active", icon="LOCKED", text="")
            
        # if props.master_collection is None:
        if props.lock_active == False or props.master_collection is None:
            if props.master_collection is None:
                row.menu("BACKUP_OBJECTS_MT_menu_select_collection", icon="GROUP", text=MenuName2)
            else:
                row.prop(props, "master_collection", text="")# , icon="GROUP", text="")
        else:
            row.prop(props.master_collection, "name", icon="GROUP", text="")
            
        row.operator("backup_objects.collection_ops", icon="ADD", text="").type = "NEW_GROUP"
        
        # Separates for extra space between
        col.separator()
        
        # Duplicate Button TOP
        if bpy.context.object != None:
            ob_name_1 = bpy.context.object.name
        else:
            ob_name_1 = "No Object Selected"
            
        # For Loop Checks if the active Object hasn't been Backed Up before
        ob_name_col_1 = "New Collection"
        # iterateNew is False if the Object/Collection has been Backed Up
        iterateNew = False
        
        for i in enumerate(props.collections):
            if i[1].object == bpy.context.object:
                if i[1].collection != None:
                    ob_name_col_1 = i[1].collection.name
                    # changes iterateNew to 
                    iterateNew = True
                    break
                    
        # How many objects you have selected
        selected_objects = len(bpy.context.selected_objects)
        
        # Changes the text from "Object" to "Objects" if more than one object is selected
        object_text = "Object" if selected_objects <= 1 else "Objects"
        
        # Changes text from "Iterate" to "Iterate New" if object wasn't found in Backup Objects
        ob_name_iterate = "Backup %d New %s" % (selected_objects, object_text) if iterateNew == False else "Backup %d %s" % (selected_objects, object_text)
        
        Dup_String_All = "Backup %d Backup Objects" % (len(props.collections) )

        row = col.row(align=True)
        row.operator("backup_objects.duplicating_ops", icon="DUPLICATE", text=ob_name_iterate).type = "DUPLICATE"

        row.menu("BACKUP_OBJECTS_MT_extra_backup_functions", icon="DOWNARROW_HLT", text="")

        # if props.dropdown_1 == True:
        row = col.row(align=True)
        
        row.label(text="Active Object: ", icon="OUTLINER_OB_MESH")
        row.label(text=ob_name_1)

        row = col.row(align=True)
        
        # row.label(text="Collection: "+ob_name_col_1, icon="GROUP")
        row.label(text="Send To: ", icon="GROUP")
        row.label(text=ob_name_col_1)
        
        col.separator()
        # Duplicate Button BOTTOM
        
        row = col.row(align=True)
        
        # This is how many collections have both an Object or Collection assigned to them
        working_collections = 0
        for i in props.collections:
            if i.collection != None and i.object != None:
                working_collections += 1
                
        row.label(text="Backup Objects (%d/%d):" % (working_collections, len(props.collections)) )
        
        # TOP
        
        split = layout.row(align=False)
        col = split.column(align=True)
        
        row = col.row(align=True)
        row.template_list("BACKUP_OBJECTS_UL_items", "custom_def_list", props, "collections", props, "BO_ULIndex", rows=3)
        
        # Side_Bar Operators
        col = split.column(align=True)
        
        button = col.operator("backup_objects.ui_ops_move", text="", icon="TRIA_UP")
        button.type = "UP"
        
        button = col.operator("backup_objects.ui_ops_move", text="", icon="TRIA_DOWN")
        button.type = "DOWN"
        
        button = col.operator("backup_objects.ui_ops_move", text="", icon="PANEL_CLOSE")
        button.type = "REMOVE"
        
        col.menu("BACKUP_OBJECTS_MT_extra_ui_list_functions", icon="DOWNARROW_HLT", text="")

        #button = col.operator("backup_objects.ui_ops_select", text="", icon="RESTRICT_SELECT_OFF")
        #button.type = "SELECT_ACTIVE_UI"
        # SELECT_ACTIVE_UI
        
        col = layout.column()

        row = col.row(align=True)
        row.label(text="Backed Object")

        row = col.row(align=True)
        # row.prop(item.collection, "name", text="", icon="GROUP", emboss=False)
        if len(props.collections) > 0:
            # Active List Object
            if props.collections[props.BO_ULIndex].object is not None:
                row.prop(props.collections[props.BO_ULIndex].object, "name", text="", icon="OUTLINER_OB_MESH", emboss=True)
                row = col.row(align=True)
            else:
                row.label(text="Object")
            # Active List Collection
            if props.collections[props.BO_ULIndex].collection is not None:
                row.prop(props.collections[props.BO_ULIndex].collection, "name", text="", icon="GROUP", emboss=True)
            else:
                row.label(text="Collection")
        else:
            row.label(text="Object (None)", icon="OUTLINER_OB_MESH")

            row = col.row(align=True)

            row.label(text="Collection (None)", icon="GROUP")

        row = col.row(align=True)
        
        # End of CustomPanel
        

class BACKUP_OBJECTS_PT_display_settings(bpy.types.Panel, PANEL_DEFAULTS):
    bl_label = "Display Settings"
    bl_parent_id = "BACKUP_OBJECTS_PT_custom_panel1"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        data = bpy.data
        props = scene.BO_Props
        
        # master_collection: 
        # collections:
        
        col = layout.column()
        
        row = col.row(align=True)
        row.label(text="Display Order")
        
        row = col.row(align=True)
        row.prop(scene.BO_Props, "list_order", expand=True)
        
        row = col.row(align=True)
        row.label(text="Sort Order")
        
        row = col.row(align=True)
        row.prop(props, "list_reverse", expand=True)# , text="X")
        
        
        row = col.row(align=True)
        row.label(text="Display")
        
        row = col.row(align=True)
        row.prop(props, "display_collections", text="Collections", icon="GROUP")
        row.prop(props, "display_icons", text="Icons", icon="OUTLINER_OB_MESH")
        
        row = col.row(align=True)
        row.prop(props, "display_index", text="Index", icon="LINENUMBERS_ON")
        row.prop(props, "display_object_count", text="Backups", icon="OBJECT_DATAMODE")
        
        col.separator()
        
        row = col.row(align=True)
        
        row.label(text="New Parent Collection Name")
        
        row = col.row(align=True)
        row.prop(props, "new_collection_name", text="", icon="NONE")
        
        col.separator()
        
        row = col.row(align=True)
        
        row.label(text="List Row")
        
        row = col.row(align=True)
        row.prop(props, "index_to_new", text="Update Active List Row", icon="NONE")
        
class BACKUP_OBJECTS_PT_backup_settings(bpy.types.Panel, PANEL_DEFAULTS):
    bl_label = "Backup Settings"
    bl_parent_id = "BACKUP_OBJECTS_PT_custom_panel1"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        data = bpy.data
        props = scene.BO_Props
        
        col = layout.column()
        
        row = col.row(align=True)
        row.prop(scene.BO_Props, "only_active", expand=True)

        row = col.row(align=True)
        row.prop(scene.BO_Props, "include_bool_objects", expand=True)
        
        col.separator()
        
        row = col.row(align=True)
        row.label(text="In Weight Paint")
        
        row = col.row(align=True)
        row.prop(props, "exclude_armature", expand=True)# , text="")
        
        
        
class BACKUP_OBJECTS_PT_cleaning(bpy.types.Panel, PANEL_DEFAULTS):
    bl_label = "Cleaning Operators"
    bl_parent_id = "BACKUP_OBJECTS_PT_custom_panel1"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        data = bpy.data
        props = scene.BO_Props
        
        col = layout.column(align=False)
        
        row = col.row(align=True)
        row.label(text="Backup Collections")
        
        row = col.row(align=True)
        # "Clean Collections"
        row.operator("backup_objects.cleaning_ops", icon="TRASH", text="Clean Backups").type = "CLEAN_COLLECTION_OBJECTS"
        
        row = col.row(align=True)
        row.prop(props, "clean_leave", text="Leave Recent Backups")
        
        col.separator()
        
        row = col.row(align=True)
        row.label(text="Cleaning UI List")
        
        row = col.row(align=True)
        row.operator("backup_objects.cleaning_ops", text="Remove Empty in UI List").type = "CLEAN_NOT_FOUND"
        
        # col.separator()
        
class BACKUP_OBJECTS_PT_debug_panel(bpy.types.Panel, PANEL_DEFAULTS):
    bl_label = "Debugging Operators"
    bl_parent_id = "BACKUP_OBJECTS_PT_custom_panel1"
    
    @classmethod
    def poll(cls, context):
        scene = bpy.context.scene
        props = scene.BO_Props
        
        # return props.collection_parent is not None and props.master_collection is not None
        return props.debug_mode == True
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        data = bpy.data
        props = scene.BO_Props
        
        col = layout.column(align=False)
        
        row = col.row(align=True)
        row.label(text="Print")
        
        row = col.row(align=True)
        row.operator("backup_objects.debug", text="Print Different").type = "PRINT_DIFFERENT_1"
        
        row = col.row(align=True)
        row.operator("backup_objects.debug", text="Print Objects/Collections").type = "PRINT_1"
        
        row = col.row(align=True)
        row.label(text="Add")
        
        row = col.row(align=True)
        row.operator("backup_objects.debug", text="Add 3 Objects").type = "TESTING"
        
        # col.separator()
        
        row = col.row(align=True)
        
        row.label(text="Delete")
        
        row = col.row(align=True)
        row.operator("backup_objects.ui_ops_move", icon="TRASH", text="All UI Elements").type = "REMOVE_UI_ALL"
        
        row = col.row(align=True)
        row.operator("backup_objects.debug", icon="TRASH", text="All Objects & UI Elements").type = "DELETE_NUKE"
            

def ListOrderUpdate(self, context):
    scene = bpy.context.scene
    data = bpy.data
    props = scene.BO_Props
    # list_order "DUPLICATES" "RECENT" "CUSTOM"
    # list_reverse: "DESCENDING" "ASCENDING"
    
    reverseBool = False
    if props.list_reverse == "ASCENDING":
        reverseBool = True
        
    # Updates the UI List selected index when ListOrderUpdate is called
    props.BO_ULIndex = len(props.collections)-props.BO_ULIndex-1
        
    # "a" parameter would be an object with methods
    def returnOrder(a):
        # Returns len() of objects in collection, else return 0
        if props.list_order == "DUPLICATES":
            
            return len(a.collection.objects) if a.collection != None else 0
            
        # Returns the integer value of the order the objects were created
        if props.list_order == "RECENT":
            return a.recent
            
        # Returns custom value order made by user in the UI List
        if props.list_order == "CUSTOM":
            return a.custom
        
    # This is where sorting is done
    # sort = sorted(props.collections, key=lambda a: a.duplicates, reverse=reverseBool)
    sort = sorted(props.collections, key=returnOrder, reverse=reverseBool)
    
    nameList = []
    
    # For loop appends the names of objects in props.collections.objects into nameList
    for i in enumerate(sort):
        if i[1].object is not None:
            nameList.append(i[1].object.name)
        else:
            print("Collection: %s missing object" % (i[1].name))
            # This section calculates the index of props.collection even when they are being removed in order to remove them
            newIndex = None
            for j in enumerate(props.collections):
                if i[1] == j[1]:
                    newIndex = j[0]
            props.collections.remove(newIndex)
    
    # For loop uses object names in nameList to move props.collections
    for i in enumerate(nameList):
        colLocation = 0
        # Loops through props.collections to see if their names matches the names of object names in nameList
        for j in enumerate(props.collections):
            # if j[1].name == i[1]:
            if j[1].object.name == i[1]:
                colLocation = j[0]
                break
        props.collections.move(colLocation, i[0])
    
    return
    
class BACKUP_OBJECTS_preferences(bpy.types.AddonPreferences):
    # bl_idname = "iterate_objects_addon_b2_80_v1_0"
    bl_idname = "backup_objects_addon_b2_80_v1_0_7"#__name__
    # here you define the addons customizable props
    ui_tab: bpy.props.EnumProperty(name="Enum", items=
        [("GENERAL", "General", "General Options"),
        ("AUTHOR", "Author", "About Author & Where to Support"),
        ("SUPPORT", "Support Addon", "Help fund development of the addon!")
        ], description="Backup Object UI Tabs", default="GENERAL")
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.BO_Props
        
        col = layout.column()
        
        row = col.row(align=True)
        row.prop(self, "ui_tab", expand=True)
        row = col.row(align=True)
        
        box = layout.box()
        col = box.column()
        # row = col.row(align=True)
        
        if self.ui_tab == "GENERAL":
            row = col.row(align=True)
            # row.label(text="Add Button to 3D Viewport Header?")
            row.prop(props, "debug_mode", expand=True, text="Debug Mode")
            
            row = col.row(align=True)
            
        elif self.ui_tab == "AUTHOR":
            row = col.row(align=True)
            row.label(text="JohnGDDR5 on: ")
            row.operator("wm.url_open", text="Youtube").url = "https://www.youtube.com/channel/UCzPZvV24AXpOBEQWK4HWXIA"
            row.operator("wm.url_open", text="Twitter").url = "https://twitter.com/JohnGDDR5"
            row.operator("wm.url_open", text="Artstation").url = "https://www.artstation.com/johngddr5"

        elif self.ui_tab == "SUPPORT":
            row = col.row(align=True)
            row.label(text="Purchase Addon On: ")
            row.operator("wm.url_open", text="Blendermarket").url = "https://blendermarket.com/products/backup-object"
            row.operator("wm.url_open", text="Gumroad").url = "https://gum.co/dNqyc"

# Schema of Custom Property Classes
"""
props = scene.BO_Props
active = props.BO_ULIndex

# master_collection: 
# collections:
    # collection:
    # object:
    # duplicates:
    # recent:

"""

class BACKUP_OBJECTS_collection_objects(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="", default="")
    collection: bpy.props.PointerProperty(name="Added Collections to List", type=bpy.types.Collection)
    object: bpy.props.PointerProperty(name="Object", type=bpy.types.Object)
    
    # duplicates: bpy.props.IntProperty(name="Int", description="", default= 0, min=0)
    
    recent: bpy.props.IntProperty(name="Int", description="", default= 0, min=0)
    custom: bpy.props.IntProperty(name="Int", description="", default= 0, min=0)
    icon: bpy.props.StringProperty(name="Icon name for object", description="Used to display in the list", default="QUESTION")# , get=)# , update=checkIcon)
    
class BACKUP_OBJECTS_props(bpy.types.PropertyGroup):
    # Tries to set collection_parent's default to Master Collection
    
    master_collection: bpy.props.PointerProperty(name="Parent Collection where all Backup Collections and Objects are sent and organized", type=bpy.types.Collection)
    full_backups_collection: bpy.props.PointerProperty(name="Collection where Full Backups are sent", type=bpy.types.Collection)
    # Booleans for locking default collection of parent
    
    lock_active: bpy.props.BoolProperty(name="Lock Parent Collection", description="Edit the name of parent collection", default=False)
    
    collections: bpy.props.CollectionProperty(type=BACKUP_OBJECTS_collection_objects)
    
    BO_ULIndex: bpy.props.IntProperty(name="List Index", description="UI List Index", default= 0, min=0)
    
    clean_leave: bpy.props.IntProperty(name="List Index", description="Ammount of recent Objects to leave when cleaning.", default=2, min=0)
    
    # Dropdown for Iterate Display
    dropdown_1: bpy.props.BoolProperty(name="Dropdown", description="Show Object of Backup Object", default=False)
    
    # group_name_use: bpy.props.BoolProperty(name="Use Object Name for New Collection", description="Use the Object\'s name for the New Collection when creating a new Iteration Object", default=True)
    
    new_collection_name: bpy.props.StringProperty(name="New Collection Name", description="Name used when creating a new collection for Active Object", default="Backups")
    
    listDesc =  ["Displays List in order of how many duplicates each object has", "Displays List in the order they were created", "Displays List in order user specified"]
    listDesc2 =  ["List displays in Descending Order", "List displays in Ascending Order"]
    
    list_order: bpy.props.EnumProperty(name="Display Mode", items= [("DUPLICATES", "Duplicates", listDesc[0], "DUPLICATE", 0), ("RECENT", "Recent", listDesc[1], "SORTTIME", 1), ("CUSTOM", "Custom", listDesc[2], "ARROW_LEFTRIGHT", 2)], description="Display Mode of List", default="DUPLICATES", update=ListOrderUpdate)
    
    list_reverse: bpy.props.EnumProperty(name="Display Mode", items= [("DESCENDING", "Descending", listDesc2[0], "SORT_DESC", 0), ("ASCENDING", "Ascending", listDesc2[1], "SORT_ASC", 1)], description="Display Mode of List", default="DESCENDING", update=ListOrderUpdate)
    
    display_collections: bpy.props.BoolProperty(name="Display Collections in List", description="Backup Object Collections where duplicates are sent.", default=True)
    
    display_icons: bpy.props.BoolProperty(name="Display Icons", description="Display icons of objects in the list", default=True)
    
    display_index: bpy.props.BoolProperty(name="Display Index", description="Display index of list row", default=True)
    
    display_object_count: bpy.props.BoolProperty(name="Display Backup Object Count", description="Display amount of backed up objects in Backup Collection", default=True)
    
    index_to_new: bpy.props.BoolProperty(name="Updates Active List Row", description="Sets Active list row to newest backup object that was added.", default=True)
    
    debug_mode: bpy.props.BoolProperty(name="Enable Debug Operators", description="Enables a panel with Debugging operators for developers", default=True)
    
    debug_mode_arrow: bpy.props.BoolProperty(name="Debug Mode Dropdown Arrow", description="To display Debug Mode", default=True)
    
    # For Iterate Collection Settings and Operators
    
    error_object: bpy.props.StringProperty(name="Collection Not Found", description="Collection has been deleted or doesn\'t exist", default="[No Object]", options={'HIDDEN'})
    
    error_collection: bpy.props.StringProperty(name="Collection Not Found", description="Collection has been deleted or doesn\'t exist", default="[No Collection]", options={'HIDDEN'})
    
    # backup settings
    only_active: bpy.props.BoolProperty(name="Backup Only Active Object", description="Only the active object will be backed up", default=False)
    
    include_bool_objects: bpy.props.BoolProperty(name="Inlcude Boolean Objects", description="Checks Modifiers to include boolean objects to backup", default=True)
    

    exclude_armature: bpy.props.BoolProperty(name="Exclude Armature Backups", description="Selected Armatures won\'t be backed up when in Weight Paint mode. To prevent unnecessary backups of an Armature when weight painting an object.", default=True)
    
    # hide_types_last
    # hide_last: bpy.props.BoolProperty(name="Exclude Recent Iteration", description="When using the operators for toggling \"all objects\"", default=False)
