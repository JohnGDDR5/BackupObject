

#Developer Script Version Notes

#Version 1.0000, 8/4/2019

bpy.context.scene.collection.children['Collection 3']
Returns bpy.data.collections['Collection 3']

bpy.data.objects['Cube'].data.copy()
scene.collection.objects.link(ob)

#Copied from ResSwitch TOP
object = bpy.data.objects[obData.pose.bones[i.name].custom_shape.name]
#Checks if object was an Empty, since Empty types don't have a data.copy()
if object.type != "EMPTY":
    object_copy = object.data.copy()
else:
    object_copy = object.data
    emptyDrawType = object.empty_draw_type

ob = bpy.data.objects.new(str(object.name), object_copy)
#Links the duplicated object in the scene
scene.objects.link(ob)
#Copied from ResSwitch BOTTOM

bpy.context.object.users_collection
#Returns: (bpy.data.collections['Bruh'], bpy.data.collections['Cube.002'], bpy.data.collections['Cube.003'])

bpy.context.selected_objects[0].users_collection
#Returns: (bpy.data.collections['Bruh'], bpy.data.collections['Cube.002'], bpy.data.collections['Cube.003'])

bpy.context.selected_objects[0].users_collection[0].objects.unlink()

#bpy.context.object.local_view_get()
#bpy.context.screen.areas[5].type
#bpy.context.screen.areas[5].spaces.active.lens
#bpy.context.screen.areas[5].spaces[0].lens

#bpy.context.screen.areas[5].spaces[0].local_view is not None

#bpy.ops.object.mode_set(mode="OBJECT")

#IM_Props.
    #collection_parent:
    #collection_active: 
    #collections:
        #collection:
        #object:
        #duplicates:
        #recent:
        
"""
ob = bpy.context.object
if not ob.select_get():
    ob.select_set(True) """
    
bpy.context.preferences.addons[0]
#returns the activated Addons the User has