extends SceneTree

const BASELINE := "res://generated/sapling_baseline_proof_materials.glb"
const CANDIDATE := "res://generated/sapling_candidate_lookdev.glb"
const RECEIPT := "res://material-lookdev-runtime-receipt.json"

var receipt := {
    "schema":"axm.nature-sapling-material-lookdev-runtime/v0.1",
    "promotion_effect":"NONE",
    "truth_boundary":"Godot 4.7.2 GL Compatibility captures of byte-retained baseline/candidate GLBs under three fixed contexts. Successful import/capture does not itself prove aesthetic acceptance, renderer equivalence, botanical correctness, or runtime readiness."
}

func write_receipt()->void:
    var file:=FileAccess.open(RECEIPT,FileAccess.WRITE)
    if file!=null:
        file.store_string(JSON.stringify(receipt,"  ")+"\n")
        file.close()

func fail(message:String)->void:
    receipt["state"]="FAIL_INFRASTRUCTURE"
    receipt["failure"]=message
    write_receipt()
    push_error(message)
    quit(1)

func import_glb(path:String)->Node3D:
    var doc:=GLTFDocument.new()
    var state:=GLTFState.new()
    if doc.append_from_file(path,state)!=OK:
        return null
    var scene:=doc.generate_scene(state)
    return scene as Node3D if scene is Node3D else null

func collect_meshes(node:Node,out:Array)->void:
    if node is MeshInstance3D:
        out.append(node)
    for child in node.get_children():
        collect_meshes(child,out)

func import_stats(root:Node3D)->Dictionary:
    var meshes:Array=[]
    collect_meshes(root,meshes)
    var vertices:=0
    var indices:=0
    var surfaces:=0
    for item in meshes:
        var node:=item as MeshInstance3D
        if node.mesh==null:
            continue
        for surface_index in range(node.mesh.get_surface_count()):
            var arrays:=node.mesh.surface_get_arrays(surface_index)
            vertices+=(arrays[Mesh.ARRAY_VERTEX] as PackedVector3Array).size()
            indices+=(arrays[Mesh.ARRAY_INDEX] as PackedInt32Array).size()
            surfaces+=1
    return {"state":"PASS","mesh_instances":meshes.size(),"vertices":vertices,"indices":indices,"surfaces":surfaces}

func make_floor()->MeshInstance3D:
    var floor:=MeshInstance3D.new()
    var mesh:=PlaneMesh.new()
    mesh.size=Vector2(14.0,14.0)
    floor.mesh=mesh
    var material:=StandardMaterial3D.new()
    material.albedo_color=Color(0.16,0.17,0.18,1.0)
    material.roughness=1.0
    floor.material_override=material
    return floor

func make_viewport(context:String)->Dictionary:
    var viewport:=SubViewport.new()
    viewport.size=Vector2i(900,700)
    viewport.own_world_3d=true
    viewport.render_target_update_mode=SubViewport.UPDATE_ALWAYS
    viewport.render_target_clear_mode=SubViewport.CLEAR_MODE_ALWAYS
    get_root().add_child(viewport)

    var root3d:=Node3D.new()
    viewport.add_child(root3d)

    var env:=Environment.new()
    env.background_mode=Environment.BG_COLOR
    env.background_color=Color(0.035,0.045,0.055,1.0)
    env.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR
    if context=="neutral_three_quarter":
        env.ambient_light_color=Color(0.62,0.66,0.72,1.0)
        env.ambient_light_energy=0.75
    elif context=="crown_close":
        env.ambient_light_color=Color(0.50,0.54,0.60,1.0)
        env.ambient_light_energy=0.58
    else:
        env.ambient_light_color=Color(0.34,0.37,0.42,1.0)
        env.ambient_light_energy=0.42
    var world:=WorldEnvironment.new()
    world.environment=env
    root3d.add_child(world)

    root3d.add_child(make_floor())

    var sun:=DirectionalLight3D.new()
    sun.shadow_enabled=true
    if context=="neutral_three_quarter":
        sun.light_energy=1.55
        sun.rotation_degrees=Vector3(-48,-32,0)
    elif context=="crown_close":
        sun.light_energy=1.95
        sun.rotation_degrees=Vector3(-42,-46,0)
    else:
        sun.light_energy=2.15
        sun.rotation_degrees=Vector3(-24,128,0)
    root3d.add_child(sun)

    var camera:=Camera3D.new()
    camera.near=0.05
    camera.far=80
    root3d.add_child(camera)
    camera.make_current()
    if context=="crown_close":
        camera.fov=40
        camera.look_at_from_position(Vector3(3.25,3.65,3.85),Vector3(0.0,3.35,0.0),Vector3.UP)
    else:
        camera.fov=48
        camera.look_at_from_position(Vector3(6.2,3.7,7.4),Vector3(0.0,2.35,0.0),Vector3.UP)

    return {"viewport":viewport,"root":root3d,"camera":camera}

func capture_asset(path:String,context:String,capture_path:String)->Dictionary:
    var asset:=import_glb(path)
    if asset==null:
        return {"state":"FAIL_IMPORT"}
    var stats:=import_stats(asset)
    var setup:=make_viewport(context)
    var viewport:=setup["viewport"] as SubViewport
    var root3d:=setup["root"] as Node3D
    root3d.add_child(asset)
    for _i in range(10):
        await process_frame
    var image:=viewport.get_texture().get_image()
    if image==null or image.is_empty():
        return {"state":"FAIL_CAPTURE"}
    if image.save_png(capture_path)!=OK:
        return {"state":"FAIL_CAPTURE"}
    var result={
        "state":"PASS",
        "import":stats,
        "capture":{
            "width":image.get_width(),
            "height":image.get_height(),
            "bytes":FileAccess.get_file_as_bytes(capture_path).size()
        }
    }
    viewport.queue_free()
    for _i in range(2):
        await process_frame
    return result

func _initialize()->void:
    var rows={}
    for context in ["neutral_three_quarter","grazing_side_key","crown_close"]:
        var baseline_name="res://baseline-%s.png" % context
        var candidate_name="res://candidate-%s.png" % context
        var baseline:=await capture_asset(BASELINE,context,baseline_name)
        var candidate:=await capture_asset(CANDIDATE,context,candidate_name)
        if baseline.get("state")!="PASS" or candidate.get("state")!="PASS":
            fail("material comparison import/capture failed for %s" % context)
            return
        rows[context]={"baseline":baseline,"candidate":candidate}
    receipt["contexts"]=rows
    receipt["state"]="PASS_TARGET_HOST_COMPARISON_READY_FOR_VISUAL_REVIEW"
    receipt["godot_version"]=Engine.get_version_info()
    write_receipt()
    print("AXM NATURE MATERIAL LOOKDEV ",JSON.stringify(receipt))
    quit(0)
