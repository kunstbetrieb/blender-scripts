import bpy
import pathlib

def new_collection(name):
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col
    
# PROPERTIES

subject = bpy.data.objects['Cylinder']
cutters = bpy.data.collections['cutters'].objects.values()
cutter_thickness = 1e-5
output_path = 'parts-obj'

# INIT

tmp_col = new_collection('TMP')
res_col = new_collection('RESULT')
bpy.ops.object.select_all(action='DESELECT')

# JOIN ALL CUTTERS

for c in cutters:
    clone = c.copy()
    clone.data = c.data.copy()
    tmp_col.objects.link(clone)
    clone.select_set(True)

main_cutter = tmp_col.objects[0]
main_cutter.name = 'main_cutter'
bpy.context.view_layer.objects.active = main_cutter
bpy.ops.object.join()

# APPLY SOLIDIFY MODIFIER TO CUTTERS 

m_soli = main_cutter.modifiers.new('SOLI','SOLIDIFY')
m_soli.thickness = cutter_thickness

# COPY SUBJECT TO RESULT COLLECTION 

res = subject.copy()
res.data = subject.data.copy()
res_col.objects.link(res)

# APPLY BOOLEAN MODIFIER TO SUBJECT 

m_bool = res.modifiers.new('BOOL','BOOLEAN')
m_bool.object = main_cutter

bpy.context.view_layer.objects.active = res
bpy.ops.object.modifier_apply(modifier="BOOL", report=False)

# SEPARATE PARTS

bpy.ops.object.select_all(action='DESELECT')
res.select_set(True)
bpy.ops.mesh.separate(type='LOOSE')
parts = bpy.data.collections['RESULT'].objects

# SAVE PARTS TO DISK

abs_path = bpy.path.abspath('//')
export_path = pathlib.Path(abs_path) / output_path

for p in parts:
    bpy.ops.object.select_all(action='DESELECT')
    p.select_set(True)
    bpy.ops.export_scene.obj(
        filepath=export_path.absolute() / f"{p.name}.obj",
        use_selection=True,
        use_materials=False
    )
