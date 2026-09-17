extends SceneTree

const GENERATED_DIR := "res://generated-compact-east-runtime"
const EXPECTED_PARENT_HEAD := "cef2ad78d8e36a55ada5dad07329f1a7125d48de"
const EXPECTED_NEUTRAL_DIGEST := "420135f6effbadb1b344675948b9ddc471dcb83177702888f0b32327c5121c18"
const VALID_MODES := ["surface_resubmit_control", "single_blend_shape_candidate"]
const CAMERA_CONTEXTS := ["ground_oblique", "crown_oblique"]
const SHADE_CONTEXTS := ["unshaded", "normal_lit"]
const BG := Color(0.025, 0.030, 0.036, 1.0)
const SETTLE_FRAMES := 3
const STRESS_CYCLES := 24
const PHASE_COUNT := 17
const SOURCE_VERTICES := 390
const SOURCE_TRIANGLES := 570
const PEAK_PHASE := 8

var tree_node: MeshInstance3D = null
var tree_mesh: ArrayMesh = null
var tree_material: StandardMaterial3D = null
var created_nodes := 0
var created_meshes := 0
var created_materials := 0
var payloads: Array = []

func output_path(mode: String) -> String:
    return "res://compact-east-blend-runtime-%s.json" % mode

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
    receipt["state"] = "FAIL_COMPACT_EAST_BLEND_RUNTIME_OBSERVER"
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
    material.roughness = 0.8
    material.cull_mode = BaseMaterial3D.CULL_DISABLED
    material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
    created_materials += 1
    return material

func surface_arrays(payload: Dictionary) -> Array:
    var vertices = payload.get("vertices", [])
    var triangles = payload.get("triangles", [])
    if not (vertices is Array) or not (triangles is Array):
        return []
    var surface := SurfaceTool.new()
    surface.begin(Mesh.PRIMITIVE_TRIANGLES)
    for triangle_value in triangles:
        var triangle := triangle_value as Array
        for local_index in [0, 2, 1]:
            surface.add_vertex(source_to_godot(vertices[int(triangle[local_index])] as Array))
    surface.generate_normals()
    return surface.commit_to_arrays()

func storage_receipt(mesh: ArrayMesh) -> Dictionary:
    if mesh == null or mesh.get_surface_count() != 1:
        return {}
    var arrays := mesh.surface_get_arrays(0)
    var stored_vertex_count := 0
    var stored_index_count := 0
    if arrays.size() > Mesh.ARRAY_VERTEX and arrays[Mesh.ARRAY_VERTEX] != null:
        stored_vertex_count = (arrays[Mesh.ARRAY_VERTEX] as PackedVector3Array).size()
    if arrays.size() > Mesh.ARRAY_INDEX and arrays[Mesh.ARRAY_INDEX] != null:
        stored_index_count = (arrays[Mesh.ARRAY_INDEX] as PackedInt32Array).size()
    var result := {
        "stored_vertex_count": stored_vertex_count,
        "stored_index_count": stored_index_count,
        "surface_format": int(mesh.surface_get_format(0)),
        "blend_shape_count": mesh.get_blend_shape_count(),
        "blend_shape_mode": int(mesh.blend_shape_mode),
    }
    if mesh.get_blend_shape_count() == 1:
        result["peak_phase"] = PEAK_PHASE
        result["representation"] = "ONE_NORMALIZED_BLEND_SHAPE_NEUTRAL_TO_PEAK"
    return result

func fill_surface_control(mesh: ArrayMesh, payload: Dictionary) -> Dictionary:
    mesh.clear_surfaces()
    var arrays := surface_arrays(payload)
    if arrays.is_empty():
        return {}
    mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
    return storage_receipt(mesh)

func build_blend_shape_mesh(mesh: ArrayMesh) -> Dictionary:
    if payloads.size() != PHASE_COUNT:
        return {}
    var neutral_arrays := surface_arrays(payloads[0] as Dictionary)
    var peak_arrays := surface_arrays(payloads[PEAK_PHASE] as Dictionary)
    if neutral_arrays.is_empty() or peak_arrays.is_empty():
        return {}
    var neutral_vertices := neutral_arrays[Mesh.ARRAY_VERTEX] as PackedVector3Array
    var peak_vertices := peak_arrays[Mesh.ARRAY_VERTEX] as PackedVector3Array
    var neutral_normals := neutral_arrays[Mesh.ARRAY_NORMAL] as PackedVector3Array
    var peak_normals := peak_arrays[Mesh.ARRAY_NORMAL] as PackedVector3Array
    if neutral_vertices.size() != SOURCE_TRIANGLES * 3 or peak_vertices.size() != neutral_vertices.size():
        return {}
    if neutral_normals.size() != neutral_vertices.size() or peak_normals.size() != neutral_vertices.size():
        return {}
    var blend_arrays := []
    blend_arrays.resize(Mesh.ARRAY_MAX)
    blend_arrays[Mesh.ARRAY_VERTEX] = peak_vertices
    blend_arrays[Mesh.ARRAY_NORMAL] = peak_normals
    mesh.blend_shape_mode = Mesh.BLEND_SHAPE_MODE_NORMALIZED
    mesh.add_blend_shape("compact_east_peak")
    mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, neutral_arrays, [blend_arrays])
    return storage_receipt(mesh)

func phase_weight(phase_index: int) -> float:
    return sin(PI * float(phase_index) / float(PHASE_COUNT - 1))

func ensure_resources(root3d: Node3D, mode: String) -> Dictionary:
    if tree_node != null:
        return storage_receipt(tree_mesh)
    tree_material = make_material()
    tree_mesh = ArrayMesh.new()
    created_meshes += 1
    var mesh_storage := {}
    if mode == "single_blend_shape_candidate":
        mesh_storage = build_blend_shape_mesh(tree_mesh)
    tree_node = MeshInstance3D.new()
    created_nodes += 1
    tree_node.name = "compact-east-runtime-%s" % mode
    tree_node.mesh = tree_mesh
    tree_node.material_override = tree_material
    root3d.add_child(tree_node)
    return mesh_storage

func apply_phase(root3d: Node3D, mode: String, payload: Dictionary, phase_index: int) -> Dictionary:
    var start_usec := Time.get_ticks_usec()
    var mesh_storage := ensure_resources(root3d, mode)
    var weight := 0.0
    if mode == "surface_resubmit_control":
        mesh_storage = fill_surface_control(tree_mesh, payload)
    else:
        if mesh_storage.is_empty():
            return {}
        weight = phase_weight(phase_index)
        tree_node.set_blend_shape_value(0, weight)
    if mesh_storage.is_empty():
        return {}
    var elapsed := Time.get_ticks_usec() - start_usec
    return {
        "submission_usec": elapsed,
        "phase_index": phase_index,
        "blend_shape_weight": weight,
        "node_instance_id": tree_node.get_instance_id(),
        "mesh_instance_id": tree_mesh.get_instance_id(),
        "material_instance_id": tree_material.get_instance_id(),
        "surface_count": tree_mesh.get_surface_count(),
        "source_vertex_count": (payload["vertices"] as Array).size(),
        "source_triangle_count": (payload["triangles"] as Array).size(),
        "mesh_storage": mesh_storage,
    }

func compare_baked_to_source(payload: Dictionary) -> Dictionary:
    if tree_node == null or tree_mesh == null or tree_mesh.get_blend_shape_count() != 1:
        return {}
    var baked := tree_node.bake_mesh_from_current_blend_shape_mix()
    if baked == null or baked.get_surface_count() != 1:
        return {}
    var expected_arrays := surface_arrays(payload)
    if expected_arrays.is_empty():
        return {}
    var baked_arrays := baked.surface_get_arrays(0)
    var actual_vertices := baked_arrays[Mesh.ARRAY_VERTEX] as PackedVector3Array
    var expected_vertices := expected_arrays[Mesh.ARRAY_VERTEX] as PackedVector3Array
    var actual_normals := baked_arrays[Mesh.ARRAY_NORMAL] as PackedVector3Array
    var expected_normals := expected_arrays[Mesh.ARRAY_NORMAL] as PackedVector3Array
    if actual_vertices.size() != expected_vertices.size() or actual_normals.size() != expected_normals.size():
        return {}
    var max_vertex_component_delta := 0.0
    var max_vertex_distance := 0.0
    var max_normal_component_delta := 0.0
    var max_normal_angle_deg := 0.0
    var max_normal_length_delta := 0.0
    for index in range(actual_vertices.size()):
        var av: Vector3 = actual_vertices[index]
        var ev: Vector3 = expected_vertices[index]
        max_vertex_component_delta = max(max_vertex_component_delta, abs(av.x - ev.x), abs(av.y - ev.y), abs(av.z - ev.z))
        max_vertex_distance = max(max_vertex_distance, av.distance_to(ev))
        var an: Vector3 = actual_normals[index]
        var en: Vector3 = expected_normals[index]
        max_normal_component_delta = max(max_normal_component_delta, abs(an.x - en.x), abs(an.y - en.y), abs(an.z - en.z))
        max_normal_length_delta = max(max_normal_length_delta, abs(an.length() - 1.0))
        if an.length_squared() > 0.0 and en.length_squared() > 0.0:
            var cosine: float = clampf(an.normalized().dot(en.normalized()), -1.0, 1.0)
            max_normal_angle_deg = max(max_normal_angle_deg, rad_to_deg(acos(cosine)))
    return {
        "baked_vertex_count": actual_vertices.size(),
        "max_vertex_component_delta_m": max_vertex_component_delta,
        "max_vertex_distance_m": max_vertex_distance,
        "max_normal_component_delta": max_normal_component_delta,
        "max_normal_angle_deg_after_normalization": max_normal_angle_deg,
        "max_raw_normal_length_delta_from_unit": max_normal_length_delta,
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

func set_shading(shade_context: String) -> void:
    tree_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED if shade_context == "unshaded" else BaseMaterial3D.SHADING_MODE_PER_PIXEL

func capture(viewport: SubViewport, mode: String, camera_context: String, shade_context: String, phase_index: int) -> Dictionary:
    var image := viewport.get_texture().get_image()
    if image == null or image.is_empty():
        return {"state": "FAIL_CAPTURE"}
    var path := "res://compact-east-blend-runtime-%s-%s-%s-%02d.png" % [mode, camera_context, shade_context, phase_index]
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
        "schema": "axm.nature-compact-east-runtime-single-blend-shape/v0.2",
        "state": "NOT_RUN",
        "mode": mode,
        "parent_vfx_head": EXPECTED_PARENT_HEAD,
        "migrated_neutral_mesh_digest": EXPECTED_NEUTRAL_DIGEST,
        "proof_runtime": "Godot 4.7.2 GL Compatibility",
    }
    if not VALID_MODES.has(mode):
        fail(mode if mode != "" else "invalid", "missing or unsupported compact-east blend runtime mode", receipt)
        return

    var summary := read_json(GENERATED_DIR + "/summary.json")
    if summary.get("state") != "PASS_COMPACT_EAST_TREE_BOUNDED_VISUAL_RESPONSE_CANDIDATE":
        fail(mode, "compact-east VFX prerequisite is missing or not green", receipt)
        return
    if String(summary.get("migrated_neutral_mesh_digest", "")) != EXPECTED_NEUTRAL_DIGEST:
        fail(mode, "compact-east migrated neutral digest drifted", receipt)
        return
    if int(summary.get("sample_count", 0)) != PHASE_COUNT:
        fail(mode, "compact-east response no longer contains exactly 17 phases", receipt)
        return

    payloads = []
    for phase_index in range(PHASE_COUNT):
        var payload := read_json(GENERATED_DIR + "/phase_%02d_mesh.json" % phase_index)
        if payload.is_empty():
            fail(mode, "missing compact-east phase payload %02d" % phase_index, receipt)
            return
        if (payload.get("vertices", []) as Array).size() != SOURCE_VERTICES or (payload.get("triangles", []) as Array).size() != SOURCE_TRIANGLES:
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
    env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
    env.ambient_light_color = Color(0.22, 0.24, 0.28, 1.0)
    env.ambient_light_energy = 0.35
    var world := WorldEnvironment.new()
    world.environment = env
    root3d.add_child(world)
    var light := DirectionalLight3D.new()
    light.rotation_degrees = Vector3(-48.0, -32.0, 0.0)
    light.light_energy = 1.15
    root3d.add_child(light)
    var camera := Camera3D.new()
    camera.near = 0.03
    camera.far = 25.0
    root3d.add_child(camera)
    camera.make_current()

    var retained_submission := []
    var retained_samples := []
    for phase_index in range(PHASE_COUNT):
        var update := apply_phase(root3d, mode, payloads[phase_index] as Dictionary, phase_index)
        if update.is_empty():
            fail(mode, "mesh submission failed for retained phase %02d" % phase_index, receipt)
            return
        retained_submission.append(update["submission_usec"])
        await settle()
        var shape_evidence := {}
        if mode == "single_blend_shape_candidate":
            shape_evidence = compare_baked_to_source(payloads[phase_index] as Dictionary)
            if shape_evidence.is_empty():
                fail(mode, "blend-shape bake comparison failed at phase %02d" % phase_index, receipt)
                return
        var contexts := {}
        for shade_value in SHADE_CONTEXTS:
            var shade_context := String(shade_value)
            set_shading(shade_context)
            await settle(2)
            for camera_value in CAMERA_CONTEXTS:
                var camera_context := String(camera_value)
                configure_camera(camera, camera_context)
                await settle(2)
                var stats := runtime_stats()
                var shot := capture(viewport, mode, camera_context, shade_context, phase_index)
                if shot.get("state") != "PASS":
                    fail(mode, "capture failed for %s/%s phase %02d" % [camera_context, shade_context, phase_index], receipt)
                    return
                contexts["%s__%s" % [camera_context, shade_context]] = {"runtime": stats, "capture": shot}
        retained_samples.append({"phase_index": phase_index, "update": update, "shape_evidence": shape_evidence, "contexts": contexts})

    var pre_stress_stats := runtime_stats()
    var stress_submission := []
    for _cycle in range(STRESS_CYCLES):
        for phase_index in range(PHASE_COUNT):
            var update := apply_phase(root3d, mode, payloads[phase_index] as Dictionary, phase_index)
            if update.is_empty():
                fail(mode, "mesh submission failed during stress sequence", receipt)
                return
            stress_submission.append(update["submission_usec"])
        await process_frame
    await settle(4)
    var post_stress_stats := runtime_stats()

    receipt["state"] = "PASS_COMPACT_EAST_BLEND_RUNTIME_OBSERVATION"
    receipt["phase_count"] = PHASE_COUNT
    receipt["stress_cycles"] = STRESS_CYCLES
    receipt["retained_update_count"] = PHASE_COUNT
    receipt["stress_update_count"] = STRESS_CYCLES * PHASE_COUNT
    receipt["total_update_count"] = PHASE_COUNT + STRESS_CYCLES * PHASE_COUNT
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
        "control_rebuilds_same_unindexed_triangle_corner_surface": true,
        "candidate_uses_one_normalized_neutral_to_peak_blend_shape": mode == "single_blend_shape_candidate",
        "candidate_phase_updates_change_only_one_blend_weight_after_initial_build": mode == "single_blend_shape_candidate",
        "unshaded_silhouette_and_simple_normal_lit_frames_measured": true,
        "final_materials_or_leaf_sidedness_tested": false,
        "target_device_performance_tested": false,
        "continuous_wall_clock_playback_tested": false,
        "map_receiving_scene_tested": false,
        "art_direction_acceptance": false,
        "canon_or_production_readiness": false,
    }
    write_receipt(mode, receipt)
    quit(0)
