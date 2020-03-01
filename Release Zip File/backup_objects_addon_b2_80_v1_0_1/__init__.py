bl_info = {
    "name": "Backup Object",
    "description": "Workflow Addon for easy duplication and organization of objects into collections, to work as \"backups\" for destructive modeling.",
    "author": "Juan Cardenas (JohnGDDR5)",
    "version": (1, 0, 1), 
    "blender": (2, 80, 0),
    "location": "3D View > Side Bar > Backup Object",
    "warning": "In Development",
    "support": "COMMUNITY",
    "category": "Scene"
}

from . backup_objects_addon_b2_80_v1_0_1 import classes

import bpy
        
from bpy.props import *

#print("classes"+str(classes) )

def register():
    #ut = bpy.utils
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    
    #bpy.types.Scene.IM_Collections = bpy.props.CollectionProperty(type=REF_IMAGEAID_Collections)
    bpy.types.Scene.BO_Props = bpy.props.PointerProperty(type=BACKUP_OBJECTS_props)
    
def unregister():
    #ut = bpy.utils
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    
    del bpy.types.Scene.BO_Props
    
if __name__ == "__main__":
    register()