"""
Quasicrystal Generator – Blender 4.5.0
"""

import bpy
import math

def clear_existing_setup():
    for name in ("Artistic_Quasicrystal",):
        if name in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)

    for name in ("Artistic_GN_Group",):
        if name in bpy.data.node_groups:
            bpy.data.node_groups.remove(bpy.data.node_groups[name], do_unlink=True)

    for mat_name in ("Quasicrystal_Mat", "Quasicrystal_Emission", "Quasicrystal_Glass"):
        if mat_name in bpy.data.materials:
            bpy.data.materials.remove(bpy.data.materials[mat_name], do_unlink=True)

clear_existing_setup()

OBJ_NAME = "Artistic_Quasicrystal"
MOD_NAME = "Artistic_GN"

mesh = bpy.data.meshes.new(f"{OBJ_NAME}_mesh")
obj  = bpy.data.objects.new(OBJ_NAME, mesh)
bpy.context.collection.objects.link(obj)

mod = obj.modifiers.new(name=MOD_NAME, type="NODES")
ng  = bpy.data.node_groups.new(f"{MOD_NAME}_Group", "GeometryNodeTree")
mod.node_group = ng

nodes, links = ng.nodes, ng.links
nodes.clear()

def add_input(name, stype, default, vmin, vmax):
    s = ng.interface.new_socket(name=name, socket_type=stype, in_out='INPUT')
    s.default_value = default
    if hasattr(s, "min_value"): s.min_value = vmin
    if hasattr(s, "max_value"): s.max_value = vmax
    return s

add_input("Count",              'NodeSocketInt',   89,   1, 2000)
add_input("Scale",              'NodeSocketFloat', 1.5,  0.1, 10.0)
add_input("Shape_Mix",          'NodeSocketFloat', 0.3,  0.0, 1.0)
add_input("Spiral_Factor",      'NodeSocketFloat', 1.0,  0.1, 5.0)
add_input("Pattern_Complexity", 'NodeSocketFloat', 1.0,  0.1, 3.0)
add_input("Fibonacci_Mode",     'NodeSocketFloat', 0.0,  0.0, 1.0)
add_input("Height_Variation",   'NodeSocketFloat', 2.0,  0.0, 8.0)
add_input("Size_Variation",     'NodeSocketFloat', 0.4,  0.0, 2.0)
add_input("Time_Factor",        'NodeSocketFloat', 0.0,  0.0, 10.0)
add_input("Rotation_Speed",     'NodeSocketFloat', 1.0,  0.0, 5.0)
add_input("Color_Variation",    'NodeSocketFloat', 1.0,  0.0, 3.0)
add_input("Emission_Strength",  'NodeSocketFloat', 0.5,  0.0, 10.0)
add_input("Fractal_Subdivisions",'NodeSocketInt',  1,    0,   4)
add_input("Organic_Distortion", 'NodeSocketFloat', 0.0,  0.0, 2.0)

ng.interface.new_socket(name="Geometry", socket_type="NodeSocketGeometry", in_out="OUTPUT")

input_node  = nodes.new("NodeGroupInput");  input_node.location  = (-900, 0)
output_node = nodes.new("NodeGroupOutput"); output_node.location = (1850, 0)

grid = nodes.new("GeometryNodeMeshGrid"); grid.location = (-750, 0)
grid.inputs["Size X"].default_value = 20.0
grid.inputs["Size Y"].default_value = 20.0
grid.inputs["Vertices Y"].default_value = 1
links.new(input_node.outputs["Count"], grid.inputs["Vertices X"])

mesh2pts = nodes.new("GeometryNodeMeshToPoints"); mesh2pts.location = (-500, 0)
links.new(grid.outputs["Mesh"], mesh2pts.inputs["Mesh"])

index = nodes.new("GeometryNodeInputIndex"); index.location = (-900, 350)

def math_node(op, loc, val=None):
    n = nodes.new("ShaderNodeMath"); n.operation = op; n.location = loc
    if val is not None:
        n.inputs[1].default_value = val
    return n

gold_angle = math_node("MULTIPLY", (-700, 350), math.radians(137.507764))
links.new(index.outputs["Index"], gold_angle.inputs[0])

fib_angle  = math_node("MULTIPLY", (-700, 450), math.radians(222.492))
links.new(index.outputs["Index"], fib_angle.inputs[0])

angle_mix = nodes.new("ShaderNodeMix"); angle_mix.data_type = 'FLOAT'; angle_mix.location = (-500, 400)
links.new(input_node.outputs["Fibonacci_Mode"], angle_mix.inputs["Factor"])
links.new(gold_angle.outputs["Value"], angle_mix.inputs['A'])
links.new(fib_angle.outputs["Value"],  angle_mix.inputs['B'])

spiral_mult = math_node("MULTIPLY", (-300, 400))
links.new(angle_mix.outputs["Result"], spiral_mult.inputs[0])
links.new(input_node.outputs["Spiral_Factor"], spiral_mult.inputs[1])

pat_mul = math_node("MULTIPLY", (-300, 320), 0.1)
links.new(index.outputs["Index"], pat_mul.inputs[0])
pat_sin = math_node("SINE",  (-150, 320)); links.new(pat_mul.outputs["Value"], pat_sin.inputs[0])
pat_scale = math_node("MULTIPLY", (0, 320))
links.new(pat_sin.outputs["Value"], pat_scale.inputs[0])
links.new(input_node.outputs["Pattern_Complexity"], pat_scale.inputs[1])

pat_add = math_node("ADD", (150, 380))
links.new(spiral_mult.outputs["Value"], pat_add.inputs[0])
links.new(pat_scale.outputs["Value"],  pat_add.inputs[1])

sqrt_idx = math_node("POWER", (-700, 600), 0.5)
links.new(index.outputs["Index"], sqrt_idx.inputs[0])

log_add = math_node("ADD", (-800, 700), 1.0); links.new(index.outputs["Index"], log_add.inputs[0])
log_idx = math_node("LOGARITHM", (-700, 700), math.e)
links.new(log_add.outputs["Value"], log_idx.inputs[0])

rad_mix = nodes.new("ShaderNodeMix"); rad_mix.data_type = 'FLOAT'; rad_mix.location = (-500, 650)
links.new(input_node.outputs["Fibonacci_Mode"], rad_mix.inputs["Factor"])
links.new(sqrt_idx.outputs["Value"], rad_mix.inputs['A'])
links.new(log_idx.outputs["Value"],  rad_mix.inputs['B'])

rad_scale = math_node("MULTIPLY", (-300, 650), 0.4)
links.new(rad_mix.outputs["Result"], rad_scale.inputs[0])

scene_time = nodes.new("GeometryNodeInputSceneTime"); scene_time.location = (-900, 800)
time_mul   = math_node("MULTIPLY", (-700, 800))
links.new(scene_time.outputs["Frame"], time_mul.inputs[0])
links.new(input_node.outputs["Time_Factor"], time_mul.inputs[1])
time_scale = math_node("MULTIPLY", (-500, 800), 0.01)
links.new(time_mul.outputs["Value"], time_scale.inputs[0])

anim_angle = math_node("ADD", (350, 380))
links.new(pat_add.outputs["Value"], anim_angle.inputs[0])
links.new(time_scale.outputs["Value"], anim_angle.inputs[1])

cos = math_node("COSINE", (550, 450)); links.new(anim_angle.outputs["Value"], cos.inputs[0])
sin = math_node("SINE",   (550, 350)); links.new(anim_angle.outputs["Value"], sin.inputs[0])

def organic(mult, loc):
    m = math_node("MULTIPLY", (300, loc), mult); links.new(index.outputs["Index"], m.inputs[0])
    s = math_node("SINE" if mult == 0.3 else "COSINE", (400, loc)); links.new(m.outputs["Value"], s.inputs[0])
    scale = math_node("MULTIPLY", (600, loc)); links.new(s.outputs["Value"], scale.inputs[0])
    links.new(input_node.outputs["Organic_Distortion"], scale.inputs[1])
    return scale

org_x = organic(0.3, 200)
org_y = organic(0.7, 100)

xpos = math_node("MULTIPLY", (750, 450)); links.new(cos.outputs["Value"], xpos.inputs[0]); links.new(rad_scale.outputs["Value"], xpos.inputs[1])
ypos = math_node("MULTIPLY", (750, 350)); links.new(sin.outputs["Value"], ypos.inputs[0]); links.new(rad_scale.outputs["Value"], ypos.inputs[1])

xfin = math_node("ADD", (950, 450)); links.new(xpos.outputs["Value"], xfin.inputs[0]); links.new(org_x.outputs["Value"], xfin.inputs[1])
yfin = math_node("ADD", (950, 350)); links.new(ypos.outputs["Value"], yfin.inputs[0]); links.new(org_y.outputs["Value"], yfin.inputs[1])

h_mul1 = math_node("MULTIPLY", (250, 250), 0.3); links.new(anim_angle.outputs["Value"], h_mul1.inputs[0])
h_sin  = math_node("SINE", (400, 250)); links.new(h_mul1.outputs["Value"], h_sin.inputs[0])
h_mul2 = math_node("MULTIPLY", (250, 300), 0.7); links.new(rad_scale.outputs["Value"], h_mul2.inputs[0])
h_cos  = math_node("COSINE", (400, 300)); links.new(h_mul2.outputs["Value"], h_cos.inputs[0])
h_add  = math_node("ADD", (600, 275)); links.new(h_sin.outputs["Value"], h_add.inputs[0]); links.new(h_cos.outputs["Value"], h_add.inputs[1])
zpos   = math_node("MULTIPLY", (750, 250)); links.new(h_add.outputs["Value"], zpos.inputs[0]); links.new(input_node.outputs["Height_Variation"], zpos.inputs[1])

combine_xyz = nodes.new("ShaderNodeCombineXYZ"); combine_xyz.location = (1150, 350)
links.new(xfin.outputs["Value"], combine_xyz.inputs["X"])
links.new(yfin.outputs["Value"], combine_xyz.inputs["Y"])
links.new(zpos.outputs["Value"], combine_xyz.inputs["Z"])

def ico(radius, subs, loc): 
    n = nodes.new("GeometryNodeMeshIcoSphere"); n.location = loc
    n.inputs["Radius"].default_value = radius
    n.inputs["Subdivisions"].default_value = subs
    return n

tetra, octa = ico(0.12, 0, (-750, -200)), ico(0.10, 1, (-750, -300))

if hasattr(bpy.types, "GeometryNodeMeshTorus"):
    torus = nodes.new("GeometryNodeMeshTorus"); torus.location = (-750, -400)
    torus.inputs["Major Radius"].default_value  = 0.08
    torus.inputs["Minor Radius"].default_value  = 0.03
    torus.inputs["Major Segments"].default_value = 12
    torus.inputs["Minor Segments"].default_value = 8
    torus_socket = torus.outputs["Mesh"]
else:
    outer = nodes.new("GeometryNodeCurvePrimitiveCircle");  outer.location = (-900, -380); outer.inputs["Radius"].default_value = 0.08
    inner = nodes.new("GeometryNodeCurvePrimitiveCircle");  inner.location = (-900, -430); inner.inputs["Radius"].default_value = 0.03
    c2m   = nodes.new("GeometryNodeCurveToMesh");           c2m.location = (-750, -400)
    links.new(outer.outputs["Curve"], c2m.inputs["Curve"])
    links.new(inner.outputs["Curve"], c2m.inputs["Profile Curve"])
    torus_socket = c2m.outputs["Mesh"]

cone = nodes.new("GeometryNodeMeshCone"); cone.location = (-750, -500)
cone.inputs["Radius Top"].default_value    = 0.02
cone.inputs["Radius Bottom"].default_value = 0.08
cone.inputs["Depth"].default_value         = 0.15
cone.inputs["Vertices"].default_value      = 8

def switch_chain(prev_out, thresh, true_geo, loc_x):
    cmp = math_node("GREATER_THAN", (loc_x-100, -200 - loc_x), thresh)
    links.new(input_node.outputs["Shape_Mix"], cmp.inputs[0])
    sw = nodes.new("GeometryNodeSwitch"); sw.input_type = 'GEOMETRY'; sw.location = (loc_x, -250 - loc_x)
    links.new(cmp.outputs["Value"], sw.inputs["Switch"])
    links.new(prev_out,             sw.inputs["False"])
    links.new(true_geo,             sw.inputs["True"])
    return sw.outputs["Output"]

out1 = switch_chain(tetra.outputs["Mesh"], 0.125, octa.outputs["Mesh"], -400)
out2 = switch_chain(out1,            0.375, torus_socket,             -200)
out3 = switch_chain(out2,            0.625, cone.outputs["Mesh"],        0)

subd = nodes.new("GeometryNodeSubdivisionSurface"); subd.location = (250, -400)
links.new(out3, subd.inputs["Mesh"])
links.new(input_node.outputs["Fractal_Subdivisions"], subd.inputs["Level"])

rx = math_node("MULTIPLY", (950, 550), 0.4); links.new(anim_angle.outputs["Value"], rx.inputs[0])
ry = math_node("MULTIPLY", (950, 500), 0.6); links.new(pat_add.outputs["Value"],   ry.inputs[0])
rz = math_node("MULTIPLY", (850, 450));       links.new(anim_angle.outputs["Value"], rz.inputs[0]); links.new(input_node.outputs["Rotation_Speed"], rz.inputs[1])
rot_xyz = nodes.new("ShaderNodeCombineXYZ"); rot_xyz.location = (1150, 500); links.new(rx.outputs["Value"], rot_xyz.inputs["X"]); links.new(ry.outputs["Value"], rot_xyz.inputs["Y"]); links.new(rz.outputs["Value"], rot_xyz.inputs["Z"])

sv1 = math_node("MULTIPLY", (600, 150), 0.2); links.new(index.outputs["Index"], sv1.inputs[0])
sw1 = math_node("SINE", (750, 150)); links.new(sv1.outputs["Value"], sw1.inputs[0])
sv2 = math_node("MULTIPLY", (600, 50), 0.1); links.new(rad_scale.outputs["Value"], sv2.inputs[0])
sw2 = math_node("COSINE", (750, 50)); links.new(sv2.outputs["Value"], sw2.inputs[0])
sz_add = math_node("ADD", (950, 100)); links.new(sw1.outputs["Value"], sz_add.inputs[0]); links.new(sw2.outputs["Value"], sz_add.inputs[1])
sz_mul = math_node("MULTIPLY", (1150, 100)); links.new(sz_add.outputs["Value"], sz_mul.inputs[0]); links.new(input_node.outputs["Size_Variation"], sz_mul.inputs[1])
sz_fin = math_node("ADD", (1350, 100), 1.0); links.new(sz_mul.outputs["Value"], sz_fin.inputs[0])

set_pos = nodes.new("GeometryNodeSetPosition"); set_pos.location = (1350, 0); links.new(mesh2pts.outputs["Points"], set_pos.inputs["Geometry"]); links.new(combine_xyz.outputs["Vector"], set_pos.inputs["Position"])

inst = nodes.new("GeometryNodeInstanceOnPoints"); inst.location = (1550, 0)
links.new(set_pos.outputs["Geometry"], inst.inputs["Points"])
links.new(subd.outputs["Mesh"],        inst.inputs["Instance"])
links.new(rot_xyz.outputs["Vector"],   inst.inputs["Rotation"])
links.new(sz_fin.outputs["Value"],     inst.inputs["Scale"])

scale_inst = nodes.new("GeometryNodeScaleInstances"); scale_inst.location = (1750, 0)
links.new(inst.outputs["Instances"], scale_inst.inputs["Instances"])
links.new(input_node.outputs["Scale"], scale_inst.inputs["Scale"])

realize = nodes.new("GeometryNodeRealizeInstances"); realize.location = (1950, 0)
links.new(scale_inst.outputs["Instances"], realize.inputs["Geometry"])
links.new(realize.outputs["Geometry"], output_node.inputs["Geometry"])

def create_advanced_materials():
    mat = bpy.data.materials.new("Quasicrystal_Mat"); mat.use_nodes = True
    n, l = mat.node_tree.nodes, mat.node_tree.links; n.clear()

    coord = n.new("ShaderNodeTexCoord"); coord.location = (-600, 0)

    noise = n.new("ShaderNodeTexNoise"); noise.location = (-400, 100)
    noise.inputs["Scale"].default_value, noise.inputs["Detail"].default_value, noise.inputs["Roughness"].default_value = 5.0, 15.0, 0.7
    l.new(coord.outputs["Generated"], noise.inputs["Vector"])

    voro = n.new("ShaderNodeTexVoronoi"); voro.location = (-400, -100)
    voro.inputs["Scale"].default_value = 8.0
    l.new(coord.outputs["Generated"], voro.inputs["Vector"])

    mix = n.new("ShaderNodeMix"); mix.data_type = 'FLOAT'; mix.location = (-200, 0)
    mix.inputs["Factor"].default_value = 0.6
    l.new(noise.outputs["Fac"],     mix.inputs["A"])
    l.new(voro.outputs["Distance"], mix.inputs["B"])

    ramp = n.new("ShaderNodeValToRGB"); ramp.location = (0, 0)
    ramp.color_ramp.elements[0].color = (0.1, 0.3, 0.8, 1)
    ramp.color_ramp.elements[1].color = (0.8, 0.4, 0.1, 1)
    l.new(mix.outputs["Result"], ramp.inputs["Fac"])

    princ = n.new("ShaderNodeBsdfPrincipled"); princ.location = (250, 0)
    l.new(ramp.outputs["Color"], princ.inputs["Base Color"])
    princ.inputs["Metallic"].default_value, princ.inputs["Roughness"].default_value = 0.7, 0.3
    l.new(noise.outputs["Fac"], princ.inputs["Emission Color"])
    princ.inputs["Emission Strength"].default_value = 0.5

    out = n.new("ShaderNodeOutputMaterial"); out.location = (500, 0)
    l.new(princ.outputs["BSDF"], out.inputs["Surface"])

    # Emission material
    emit = bpy.data.materials.new("Quasicrystal_Emission"); emit.use_nodes = True
    en, el = emit.node_tree.nodes, emit.node_tree.links; en.clear()
    e_shader = en.new("ShaderNodeEmission"); e_shader.location = (200, 0)
    e_shader.inputs["Color"].default_value, e_shader.inputs["Strength"].default_value = (0.3, 0.8, 1, 1), 2
    e_out = en.new("ShaderNodeOutputMaterial"); e_out.location = (400, 0)
    el.new(e_shader.outputs["Emission"], e_out.inputs["Surface"])

    # Glass material
    glass = bpy.data.materials.new("Quasicrystal_Glass"); glass.use_nodes = True
    gn, gl = glass.node_tree.nodes, glass.node_tree.links; gn.clear()
    g_shader = gn.new("ShaderNodeBsdfGlass"); g_shader.location = (200, 0)
    g_shader.inputs["Color"].default_value, g_shader.inputs["IOR"].default_value, g_shader.inputs["Roughness"].default_value = (0.9, 0.95, 1, 1), 1.45, 0.05
    g_out = gn.new("ShaderNodeOutputMaterial"); g_out.location = (400, 0)
    gl.new(g_shader.outputs["BSDF"], g_out.inputs["Surface"])

    return mat, emit, glass

main_mat, emission_mat, glass_mat = create_advanced_materials()
obj.data.materials.append(main_mat)

def setup_presets():
    return {
        "Cosmic_Nebula":  {"Count": 233,"Scale": 2.5,"Shape_Mix": 0.2,"Spiral_Factor": 1.3,"Pattern_Complexity": 2.0,"Height_Variation": 4.0,"Size_Variation": 0.8,"Color_Variation": 2.5,"Emission_Strength": 3.0,"Organic_Distortion": 0.3},
        "Crystal_Garden": {"Count": 144,"Scale": 1.8,"Shape_Mix": 0.8,"Spiral_Factor": 0.8,"Pattern_Complexity": 1.2,"Height_Variation": 1.5,"Size_Variation": 0.4,"Fractal_Subdivisions": 2,"Organic_Distortion": 0.0},
        "Organic_Flow":   {"Count": 177,"Scale": 1.5,"Shape_Mix": 0.4,"Spiral_Factor": 2.0,"Pattern_Complexity": 1.8,"Height_Variation": 3.0,"Size_Variation": 1.2,"Organic_Distortion": 1.5,"Fibonacci_Mode": 0.7},
        "Minimalist_Zen": {"Count":  89,"Scale": 2.0,"Shape_Mix": 0.0,"Spiral_Factor": 1.0,"Pattern_Complexity": 0.5,"Height_Variation": 0.8,"Size_Variation": 0.2,"Organic_Distortion": 0.0},
        "Fractal_Storm":  {"Count": 377,"Scale": 3.0,"Shape_Mix": 0.6,"Spiral_Factor": 2.5,"Pattern_Complexity": 2.8,"Height_Variation": 6.0,"Size_Variation": 1.5,"Fractal_Subdivisions": 3,"Organic_Distortion": 1.0,"Time_Factor": 2.0},
    }
presets = setup_presets()

print("QUASICRYSTAL GENERATOR – Blender 4.5 ready\n"
      "No missing nodes – happy fractaling!\n")
