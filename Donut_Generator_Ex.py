import bpy
import random

# THIS IS FREE ADDON FOR BLENDER USERS DONT CHANGE STUFF HERE (Klo ga gw ngamuk)
bl_info = {
    "name": "DonutGen",
    "description": "Simple Donut Generator",
    "author": "Atthariq Insanulhaq Supiana",
    "version": (1, 0),
    "blender": (4, 1, 0),
    "category": "Object"
}

def create_donut(DonutColor, CreamColor):
    # MAIN OBJS
    bpy.ops.object.empty_add(location=(0, 0, 0))
    empty_obj = bpy.context.object
    empty_obj.name = "Donut Object"

    donut = bpy.ops.mesh.primitive_torus_add(minor_radius = 0.5,
    minor_segments = 32, location=(0, 0, 0.5))
    donut = bpy.context.object
    donut.name = "Donut"
    bpy.ops.object.shade_smooth()

    chocolate = bpy.ops.mesh.primitive_torus_add(minor_radius = 0.5,
    minor_segments = 32, location = (0, 0, 0.05))
    chocolate = bpy.context.object
    chocolate.name = "Donut Top"
    bpy.ops.object.shade_smooth()

    def get_or_create_collection(collection_name):
        if collection_name in bpy.data.collections:
            return bpy.data.collections[collection_name]
        else:
            new_collection = bpy.data.collections.new(collection_name)
            bpy.context.scene.collection.children.link(new_collection)
            return new_collection

    sprinkles_collection = get_or_create_collection("Sprinks Particle")
    sprinkles = bpy.data.objects.get("Sprink")

    if not sprinkles:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.3, location=(0, 0, -10))
        sprinkles = bpy.context.object
        sprinkles.name = "Sprink"

    if sprinkles_collection:
        if sprinkles.name not in sprinkles_collection.objects:
            bpy.context.collection.objects.unlink(sprinkles)
            sprinkles_collection.objects.link(sprinkles)


    # MODELLING
    bpy.context.view_layer.objects.active = chocolate
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(type="FACE")
    bpy.ops.mesh.select_all(action='DESELECT')

    bpy.ops.object.mode_set(mode='OBJECT')

    for face in chocolate.data.polygons:
        vertices = [chocolate.data.vertices[vertex_index].co for vertex_index in face.vertices]
        z_coords = [vertex.z for vertex in vertices]
        if any(z < 0 for z in z_coords):
            face.select = True

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.delete(type='FACE')

    bpy.ops.mesh.select_mode(type="VERT")
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')

    i = 0

    for vertex in chocolate.data.vertices:
        if i%2 == 0 :
            if vertex.co.z == 0:
                chocolate.data.vertices[vertex.index].select = True
        i+=1

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.transform.translate(value=(0, 0, -0.1))

    # MODIFIERS
    subdiv = chocolate.modifiers.new(name="Subdivision", type='SUBSURF')
    subdiv.levels = 2 
    subdiv.render_levels = 2

    solid = chocolate.modifiers.new(name="Solidify", type='SOLIDIFY')
    solid.thickness = -0.03

    bpy.ops.object.mode_set(mode='OBJECT')

    # MATERIAL (DONUT & CHOCO)
    donutmat = bpy.data.materials.new(name="Donut")
    donutmat.use_nodes = True
    nodes = donutmat.node_tree.nodes
    donutcolor = nodes.get("Principled BSDF")

    donutcolor.inputs["Base Color"].default_value = (DonutColor)
    donutcolor.inputs[12].default_value = 0.2
    donutcolor.inputs["Roughness"].default_value = 0.55

    donut.data.materials.append(donutmat)

    chocomat = bpy.data.materials.new(name="Top")
    chocomat.use_nodes = True
    nodes = chocomat.node_tree.nodes

    chocolor = nodes.get("Principled BSDF")
    chocolor.inputs["Base Color"].default_value = (CreamColor)
    chocolor.inputs[12].default_value = 0.4
    chocolor.inputs["Roughness"].default_value = 0.35

    chocolate.data.materials.append(chocomat)

    # MATERIAL (SPRINKS)
    smat = bpy.data.materials.new(name="Smat")
    smat.use_nodes = True
    nodes = smat.node_tree.nodes
    sprincipled = nodes.get("Principled BSDF")
    sobjinf = nodes.new(type='ShaderNodeObjectInfo')
    sramp = nodes.new(type='ShaderNodeValToRGB')

    sramp.color_ramp.interpolation = "CONSTANT"

    sramp.color_ramp.elements.new(0.2)
    sramp.color_ramp.elements.new(0.4)
    sramp.color_ramp.elements.new(0.6)
    sramp.color_ramp.elements.new(0.8)

    sramp.color_ramp.elements[0].color = (0.1, 0.7, 1, 1 )
    sramp.color_ramp.elements[1].color = (0.7, 0.1, 0.1, 1 )
    sramp.color_ramp.elements[2].color = (1, 1, 1, 1 )
    sramp.color_ramp.elements[3].color = (0.045253, 0.02783, 0.003596, 1 )
    sramp.color_ramp.elements[4].color = (1, 0.5, 0.5, 1 )

    smat.node_tree.links.new(sobjinf.outputs["Random"], sramp.inputs["Fac"])
    smat.node_tree.links.new(sramp.outputs["Color"], sprincipled.inputs["Base Color"])

    sprinkles.data.materials.append(smat)

    # Apply Mods
    bpy.context.view_layer.objects.active = chocolate
    bpy.ops.object.modifier_apply(modifier= "Subdivision")
    bpy.ops.object.modifier_apply(modifier= "Solidify")

    # Particles
    spark = chocolate.modifiers.new(name="Sparks", type="PARTICLE_SYSTEM")
    sparkset = spark.particle_system.settings
    sparkset.type = "HAIR"
    sparkset.use_advanced_hair = True
    sparkset.count = random.randint(400, 700)
    sparkset.render_type = "OBJECT"
    sparkset.instance_object = bpy.data.objects["Sprink"]
    sparkset.particle_size = 0.06
    sparkset.size_random = random.uniform(0.3, 0.6)
    sparkset.use_rotations = True
    sparkset.phase_factor = random.uniform(0, 2)
    sparkset.phase_factor_random = random.uniform(0.5, 2)
    sprinkles.hide_set(True)
    bpy.context.object.particle_systems["Sparks"].seed = random.randint(1, 1000)


    # PARENTING
    chocolate.parent = donut
    donut.parent = empty_obj
    
    # SELECT EMPTY
    bpy.context.view_layer.objects.active = empty_obj


class SimplePanel(bpy.types.Panel):
    bl_label = "Donut Generator"
    bl_idname = "DONUTGENERATORID"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Donut Generator"

    def draw(self, context):
        layout = self.layout
        
        layout.label(text="Donut Color :")
        row = layout.row()
        row.prop(context.scene, "donut_color", text="")

        layout.label(text="Cream Color :")
        row = layout.row()
        row.prop(context.scene, "cream_color", text="")
        
        layout.separator(factor=1)
        
        layout.operator("object.generate_donut", text="Generate")
        
class GenerateDonutButton(bpy.types.Operator):
    bl_idname = "object.generate_donut"
    bl_label = "Generate Donut"
    
    def execute(self, context):
        create_donut(bpy.context.scene.donut_color, bpy.context.scene.cream_color)
        self.report({'INFO'}, "Donut generated!")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(SimplePanel)
    bpy.utils.register_class(GenerateDonutButton)
    
    bpy.types.Scene.donut_color = bpy.props.FloatVectorProperty(name="Donut Color",
    subtype='COLOR',
    size=4,
    default=(1.0, 1.0, 1.0, 1.0), min = 0.0, max = 1.0, soft_min=0.0, soft_max=1.0)
    
    bpy.types.Scene.cream_color = bpy.props.FloatVectorProperty(name="Cream Color",
    subtype='COLOR',
    size=4,
    default=(1.0, 1.0, 1.0, 1.0), min = 0.0, max = 1.0, soft_min=0.0, soft_max=1.0)

def unregister():
    bpy.utils.unregister_class(SimplePanel)
    bpy.utils.unregister_class(GenerateDonutButton)
    del bpy.types.Scene.donut_color
    del bpy.types.Scene.cream_color

if __name__ == "__main__":
    register()
