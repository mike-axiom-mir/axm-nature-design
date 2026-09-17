extends SceneTree

const GENERATED_DIR := "res://generated-compact-east-runtime"
const EXPECTED_PARENT_HEAD := "cef2ad78d8e36a55ada5dad07329f1a7125d48de"
const EXPECTED_NEUTRAL_DIGEST := "420135f6effbadb1b344675948b9ddc471dcb83177702888f0b32327c5121c18"
const VALID_MODES := ["rebuild_resources_control", "reuse_arraymesh_candidate"]
const CONTEXTS := ["ground_oblique", "crown_oblique"]
const BG := Color(0.025, 0.030, 0.036, 1.0)
const SETTLE_FRAMES := 3
const STRESS_CYCLES := 24

var tree_node: MeshInstance3D = null
var tree_mesh: ArrayMesh = null
var tree_material: StandardMaterial3D = null
var created_nodes := 0
var created_meshes := 0
var created_materials := 0

func output_path(mode: String) -> String:
    return "res://compact-east-runtime-%s.json" % mode

func read_json(path: String) -> Dictionary:
    if not FileAccess.file_exists(path):
        return {}
    var parsed = JSON.parse_string(FileAccess.get_file_as_string(path))
    return parsed as Dictionary if parsed is Dictionary else {}

func sha256_file(path: String) -> String:
    var bytes := FileAccess.get_file_as_bytes(path)
    var ctx := HashingContext.new()
    ctx.start(HashingContext.HASH_SHA256)
    ctx.update(bytes)
    return ctx.finish().hex_encode()

func write_receipt(mode: String, receipt: Dictionary) -> void:
    var file := FileAccess.open(output_path(mode), FileAccess.WRITE)
    if file != null:
        file.store_string(JSON.stringify(receipt, "  ") + "\n")
        file.close()

func fail(mode: String, message: String, receipt: Dictionary = {}) -> void:
    receipt["state"] = "FAIL_COMPACT_EAST_RUNTIME_RESOURCE_OBSERVER"
    receipt["failure"] = message
    receipt["godot_version"] = Engine.get_version_info()
    write_receipt(mode, receipt)
    push_error(message)
    quit(1)

func source_to_godot(point: Array) -> Vector3:
    return Vector3(float(point[0]), float(point[2]), float(point[1]))

func make_material() -> StandardMaterial3D:
    var material := StandardMaterial3D.new()
    material.albedo_color = Color(0.54, 0.76, 0.43, 1.0)
    material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
    material.cull_mode = BaseMaterial3D.CULL_DISABLED
    created_materials += 1
    return material

func fill_mesh(mesh: ArrayMesh, payload: Dictionary) -> void:
    var vertices = payload.get("vertices", [])
    var triangles = payload.get("triangles", [])
    if not (vertices is Array) or not (triangles is Array):
        push_error("compact-tree phase payload lacks vertex/triangle arrays")
        return
    mesh.clear_surfaces()
    var surface := SurfaceTool.new()
    surface.begin(Mesh.PRIMITIVE_TRIANGLES)
    for triangle_value in triangles:
        var triangle := triangle_value as Array
        for local_index in [0, 2, 1]:
            surface.add_vertex(source_to_godot(vertices[int(triangle[local_index])] as Array))
    surface.generate_normals()
    surface.commit(mesh)

func apply_phase(root3d: Node3D, mode: String, payload: Dictionary) -> Dictionary:
    var start_usec := Time.get_ticks_usec()
    if mode == "rebuild_resources_control":
        if tree_node != null:
            tree_node.free()
        tree_material = make_material()
        tree_mesh = ArrayMesh.new()
        created_meshes += 1
        fill_mesh(tree_mesh, payload)
        tree_node = MeshInstance3D.new()
        created_nodes += 1
        tree_node.name = "compact-east-tree-runtime-control"
        tree_node.mesh = tree_mesh
        tree_node.material_override = tree_material
        root3d.add_child(tree_node)
    else:
        if tree_node == null:
            tree_material = make_material()
            tree_mesh = ArrayMesh.new()
            created_meshes += 1
            tree_node = MeshInstance3D.new()
            created_nodes += 1
            tree_node.name = "compact-east-tree-runtime-reuse"
            tree_node.mesh = tree_mesh
            tree_node.material_override = tree_material
            root3d.add_child(tree_node)
        fill_mesh(tree_mesh, payload)
    var elapsed := Time.get_ticks_usec() - start_usec
    return {
        "submission_usec": elapsed,
        "node_instance_id": tree_node.get_instance_id(),
        "mesh_instance_id": tree_mesh.get_instance_id(),
        "material_instance_id": tree_material.get_instance_id(),
        "surface_count": tree_mesh.get_surface_count(),
        "source_vertex_count": (payload["vertices"] as Array).size(),
        "source_triangle_count": (payload["triangles"] as Array).size(),
    }

func runtime_stats() -> Dictionary:
    return {
        "objects_in_frame": RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_OBJECTS_IN_FRAME),
        "primitives_in_frame": RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_PRIMITIVES_IN_FRAME),
        "draw_calls_in_frame": RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_DRAW_CALLS_IN_FRAME),
        "texture_mem_bytes": RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TEXTURE_MEM_USED),
        "buffer_mem_bytes": RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_BUFFER_MEM_USED),
    }

func settle(frames: int = SETTLE_FRAMES) -> void:
    for _i in range(frames):
        await process_frame

func camera_spec(context: String) -> Dictionary:
    if context == "crown_oblique":
        return {"position": Vector3(2.9, 3.3, 2.7), "target": Vector3(0.0, 2.35, 0.0), "fov": 38.0}
    return {"position": Vector3(3.4, 1.9, 4.0), "target": Vector3(0.0, 1.8, 0.0), "fov": 40.0}

func configure_camera(camera: Camera3D, context: String) -> void:
    var spec := camera_spec(context)
    camera.fov = float(spec["fov"])
    camera.look_at_from_position(spec["position"] as Vector3, spec["target"] as Vector3, Vector3.UP)

func capture(viewport: SubViewport, mode: String, context: String, phase_index: int) -> Dictionary:
    var image := viewport.get_texture().get_image()
    if image == null or image.is_empty():
        return {"state": "FAIL_CAPTURE"}
    var path := "res://compact-east-runtime-%s-%s-%02d.png" % [mode, context, phase_index]
    if image.save_png(path) != OK:
        return {"state": "FAIL_CAPTURE"}
    return {
        "state": "PASS",
        "path": path,
        "sha256": sha256_file(path),
        "width": image.get_width(),
        "height": image.get_height(),
    }

func summarize(values: Array) -> Dictionary:
    if values.is_empty():
        return {"count": 0, "min_usec": 0, "median_usec": 0, "p95_usec": 0, "max_usec": 0, "total_usec": 0}
    var ordered := values.duplicate()
    ordered.sort()
    var count := ordered.size()
    var median_index := int(floor(float(count - 1) * 0.5))
    var p95_index := int(ceil(float(count) * 0.95)) - 1
    p95_index = clamp(p95_index, 0, count - 1)
    var total := 0
    for value in ordered:
        total += int(value)
    return {
        "count": count,
        "min_usec": int(ordered[0]),
        "median_usec": int(ordered[median_index]),
        "p95_usec": int(ordered[p95_index]),
        "max_usec": int(ordered[count - 1]),
        "total_usec": total,
    }

func _initialize() -> void:
    var args := OS.get_cmdline_user_args()
    var mode := String(args[0]) if args.size() > 0 else ""
    var receipt := {
        "schema": "axm.nature-compact-east-runtime-resource-reuse/v0.1",
        "state": "NOT_RUN",
        "mode": mode,
        "parent_vfx_head": EXPECTED_PARENT_HEAD,
        "migrated_neutral_mesh_digest": EXPECTED_NEUTRAL_DIGEST,
        "proof_runtime": "Godot 4.7.2 GL Compatibility",
    }
    if not VALID_MODES.has(mode):
        fail(mode if mode != "" else "invalid", "missing or unsupported compact-east runtime mode", receipt)
        return

    var summary := read_json(GENERATED_DIR + "/summary.json")
    if summary.get("state") != "PASS_COMPACT_EAST_TREE_BOUNDED_VISUAL_RESPONSE_CANDIDATE":
        fail(mode, "compact-east VFX prerequisite is missing or not green", receipt)
        return
    if String(summary.get("migrated_neutral_mesh_digest", "")) != EXPECTED_NEUTRAL_DIGEST:
        fail(mode, "compact-east migrated neutral digest drifted", receipt)
        return
    if int(summary.get("sample_count", 0)) != 17:
        fail(mode, "compact-east response no longer contains exactly 17 phases", receipt)
        return

    var payloads := []
    for phase_index in range(17):
        var payload := read_json(GENERATED_DIR + "/phase_%02d_mesh.json" % phase_index)
        if payload.is_empty():
            fail(mode, "missing compact-east phase payload %02d" % phase_index, receipt)
            return
        if (payload.get("vertices", []) as Array).size() != 390 or (payload.get("triangles", []) as Array).size() != 570:
            fail(mode, "compact-east phase topology drifted", receipt)
            return
        payloads.append(payload)

    var viewport := SubViewport.new()
    viewport.size = Vector2i(720, 720)
    viewport.own_world_3d = true
    viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
    viewport.render_target_clear_mode = SubViewport.CLEAR_MODE_ALWAYS
    get_root().add_child(viewport)

    var root3d := Node3D.new()
    viewport.add_child(root3d)
    var env := Environment.new()
    env.background_mode = Environment.BG_COLOR
    env.background_color = BG
    var world := WorldEnvironment.new()
    world.environment = env
    root3d.add_child(world)
    var camera := Camera3D.new()
    camera.near = 0.03
    camera.far = 25.0
    root3d.add_child(camera)
    camera.make_current()

    var retained_submission := []
    var retained_samples := []
    for phase_index in range(17):
        var update := apply_phase(root3d, mode, payloads[phase_index] as Dictionary)
        retained_submission.append(update["submission_usec"])
        await settle()
        var contexts := {}
        for context_value in CONTEXTS:
            var context := String(context_value)
            configure_camera(camera, context)
            await settle(2)
            var stats := runtime_stats()
            var shot := capture(viewport, mode, context, phase_index)
            if shot.get("state") != "PASS":
                fail(mode, "capture failed for %s phase %02d" % [context, phase_index], receipt)
                return
            contexts[context] = {"runtime": stats, "capture": shot}
        retained_samples.append({"phase_index": phase_index, "update": update, "contexts": contexts})

    var pre_stress_stats := runtime_stats()
    var stress_submission := []
    for _cycle in range(STRESS_CYCLES):
        for phase_index in range(17):
            var update := apply_phase(root3d, mode, payloads[phase_index] as Dictionary)
            stress_submission.append(update["submission_usec"])
        await process_frame
    await settle(4)
    var post_stress_stats := runtime_stats()

    receipt["state"] = "PASS_COMPACT_EAST_RUNTIME_RESOURCE_OBSERVATION"
    receipt["phase_count"] = 17
    receipt["stress_cycles"] = STRESS_CYCLES
    receipt["retained_update_count"] = 17
    receipt["stress_update_count"] = STRESS_CYCLES * 17
    receipt["total_update_count"] = 17 + STRESS_CYCLES * 17
    receipt["resource_constructions"] = {
        "mesh_instances": created_nodes,
        "array_meshes": created_meshes,
        "materials": created_materials,
    }
    receipt["retained_submission_timing"] = summarize(retained_submission)
    receipt["stress_submission_timing"] = summarize(stress_submission)
    receipt["pre_stress_runtime"] = pre_stress_stats
    receipt["post_stress_runtime"] = post_stress_stats
    receipt["retained_samples"] = retained_samples
    receipt["truth_boundary"] = {
        "exact_vfx_source_phases_consumed": true,
        "only_resource_lifecycle_differs_between_modes": true,
        "neutral_unshaded_proof_material": true,
        "culling_disabled_for_response_isolation": true,
        "target_device_performance_tested": false,
        "continuous_wall_clock_playback_tested": false,
        "final_materials_or_leaf_sidedness_tested": false,
        "art_direction_acceptance": false,
        "map_receiving_scene_tested": false,
        "canon_or_production_readiness": false,
    }
    write_receipt(mode, receipt)
    quit(0)
