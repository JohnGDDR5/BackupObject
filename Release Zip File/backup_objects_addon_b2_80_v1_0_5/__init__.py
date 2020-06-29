bl_info = {
    "name": "Backup Object",
    "description": "Workflow Addon for easy duplication and organization of objects into collections, to work as \"backups\" for destructive modeling.",
    "author": "Juan Cardenas (JohnGDDR5)",
    "version": (1, 0, 5), 
    "blender": (2, 80, 0),
    "location": "3D View > Side Bar > Backup Object",
    "warning": "In Development",
    "support": "COMMUNITY",
    "category": "Scene"
}

import bpy
        
from bpy.props import *

#from . backup_objects_addon_b2_80_v1_0_1 import classes
from . backup_objects_addon_b2_80_v1_0_5 import (
    BACKUP_OBJECTS_OT_select_collection,
    BACKUP_OBJECTS_OT_group_operators,
    BACKUP_OBJECTS_OT_duplicate,
    BACKUP_OBJECTS_OT_duplicate_all,
    BACKUP_OBJECTS_OT_swap_backup_object,
    BACKUP_OBJECTS_OT_select_backup_ob_and_col,
    BACKUP_OBJECTS_OT_cleaning,
    BACKUP_OBJECTS_OT_removing,
    
    BACKUP_OBJECTS_OT_debugging,
    BACKUP_OBJECTS_OT_ui_operators_move,
    BACKUP_OBJECTS_OT_ui_operators_select,
    
    BACKUP_OBJECTS_UL_items,
    BACKUP_OBJECTS_MT_menu_select_collection,
    BACKUP_OBJECTS_MT_extra_backup_functions,
    BACKUP_OBJECTS_MT_extra_ui_list_functions,
    
    BACKUP_OBJECTS_PT_custom_panel1,
    BACKUP_OBJECTS_PT_display_settings,
    BACKUP_OBJECTS_PT_backup_settings,
    BACKUP_OBJECTS_PT_cleaning,
    BACKUP_OBJECTS_PT_debug_panel,
    
    BACKUP_OBJECTS_preferences,
    BACKUP_OBJECTS_collection_objects,
    BACKUP_OBJECTS_props,
)



#print("classes"+str(classes) )
#Yes, I had to do this or else it would not register correctly
classes = (
    BACKUP_OBJECTS_OT_select_collection,
    BACKUP_OBJECTS_OT_group_operators,
    BACKUP_OBJECTS_OT_duplicate,
    BACKUP_OBJECTS_OT_duplicate_all,
    BACKUP_OBJECTS_OT_swap_backup_object,
    BACKUP_OBJECTS_OT_select_backup_ob_and_col,
    BACKUP_OBJECTS_OT_cleaning,
    BACKUP_OBJECTS_OT_removing,
    
    BACKUP_OBJECTS_OT_debugging,
    BACKUP_OBJECTS_OT_ui_operators_move,
    BACKUP_OBJECTS_OT_ui_operators_select,
    
    BACKUP_OBJECTS_UL_items,
    BACKUP_OBJECTS_MT_menu_select_collection,
    BACKUP_OBJECTS_MT_extra_backup_functions,
    BACKUP_OBJECTS_MT_extra_ui_list_functions,
    
    BACKUP_OBJECTS_PT_custom_panel1,
    BACKUP_OBJECTS_PT_display_settings,
    BACKUP_OBJECTS_PT_backup_settings,
    BACKUP_OBJECTS_PT_cleaning,
    BACKUP_OBJECTS_PT_debug_panel,
    
    BACKUP_OBJECTS_preferences,
    BACKUP_OBJECTS_collection_objects,
    BACKUP_OBJECTS_props,
)

def register():
    #ut = bpy.utils
    #from bpy.utils import register_class
    #"""
    for cls in classes:
        bpy.utils.register_class(cls)
    #"""
    #bpy.utils.register_classes_factory(classes)
        
    bpy.types.Scene.BO_Props =  bpy.props.PointerProperty(type=BACKUP_OBJECTS_props)
    
def unregister():
    #ut = bpy.utils
    #from bpy.utils import unregister_class
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    #bpy.utils.register_classes_factory(classes)
    
    #Just incase to prevent an error
    if hasattr(bpy.types.Scene, "BO_Props") == True:
        del bpy.types.Scene.BO_Props
    
#register, unregister = bpy.utils.register_classes_factory(classes)
#"""
if __name__ == "__main__":
    register()
    
#"""
