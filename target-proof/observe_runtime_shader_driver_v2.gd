extends SceneTree

const ORACLE_PATH := "res://generated/runtime-shader-driver-oracle.json"
const OWNER_ORACLE_PATH := "res://generated/nature-east-rear-dynamic-window-target-oracle.json"
const GLB_PATH := "res://generated/nature-east-rear-dynamic-window.glb"
const SHADER_PATH := "res://generated/runtime-shader-driver.gdshader"
const RECEIPT_PATH := "res://runtime-east-rear-shader-driver-receipt.json"
const RENDER_DIR := "res://renders/runtime-east-rear-shader-driver"
const EXPECTED_VERTICES := 390
const EXPECTED_IMPORTED_STRIDE := 8
const EXPECTED_MUTABLE_STRIDE := 12
const EXPECTED_WINDOW_START := 110
const EXPECTED_WINDOW_END := 370

func _initialize() -> void:
    call_deferred("_run")

func _fail(message: String) -> void:
    push_error(message)
    quit(1)

func _read_json(path: String) -> Dictionary:
    if not FileAccess.file_exists(path):
        _fail("missing JSON: %s" % path)
        return {}
    var parsed = JSON.parse_string(FileAccess.get_file_as_string(path))
    if typeof(parsed) != TYPE_DICTIONARY:
        _fail("invalid JSON object: %s" % path)
        return {}
    return parsed

func _find_mesh(node: Node) -> MeshInstance3D:
    if node is MeshInstance3D:
        return node as MeshInstance3D
    for child in node.get_children():
        var found := _find_mesh(child)
        if found != null:
            return found
    return null

func _clone_mutable_mesh(source: ArrayMesh) -> ArrayMesh:
    var result := ArrayMesh.new()
    for surface in range(source.get_surface_count()):
        result.add_surface_from_arrays(
            source.surface_get_primitive_type(surface),
            source.surface_get_arrays(surface),
            [], {}, Mesh.ARRAY_FLAG_USE_DYNAMIC_UPDATE
        )
    return result

func _target_to_source(value: Vector3) -> Vector3:
    return Vector3(value.x, value.z, value.y)

func _source_to_target(value: Vector3) -> Vector3:
    return Vector3(value.x, value.z, value.y)

func _vec3(row: Variant) -> Vector3:
    if typeof(row) != TYPE_ARRAY or row.size() != 3:
        _fail("invalid vec3 row")
        return Vector3.ZERO
    return Vector3(float(row[0]), float(row[1]), float(row[2]))

func _cpu_pose(neutral_target: PackedVector3Array, groups: Array, driver_deg: float) -> PackedVector3Array:
    var result := neutral_target.duplicate()
    for group in groups:
        var pivot := _vec3(group.get("pivot_source_m", []))
        var axis := _vec3(group.get("axis_source", [])).normalized()
        var angle := deg_to_rad(driver_deg * float(group.get("command_sign_multiplier", 0.0)))
        var runs: Array = group.get("vertex_id_runs", [])
        for run in runs:
            if typeof(run) != TYPE_ARRAY or run.size() != 2:
                _fail("invalid VERTEX_ID run")
                return PackedVector3Array()
            for vertex_index in range(int(run[0]), int(run[1])):
                var source_point := _target_to_source(neutral_target[vertex_index])
                result[vertex_index] = _source_to_target(pivot + (source_point - pivot).rotated(axis, angle))
    return result

func _packed_vectors(rows: Array) -> PackedVector3Array:
    var result := PackedVector3Array()
    result.resize(rows.size())
    for index in range(rows.size()):
        result[index] = _vec3(rows[index])
    return result

func _max_component_delta(left: PackedVector3Array, right: PackedVector3Array) -> float:
    if left.size() != right.size():
        return INF
    var maximum := 0.0
    for index in range(left.size()):
        maximum = max(maximum, abs(left[index].x - right[index].x))
        maximum = max(maximum, abs(left[index].y - right[index].y))
        maximum = max(maximum, abs(left[index].z - right[index].z))
    return maximum

func _driver_token(value: float) -> String:
    return String.num(value, 1).replace("-", "m").replace(".", "p")

func _capture(mesh_node: MeshInstance3D, mesh: ArrayMesh, material: ShaderMaterial, path: String) -> void:
    mesh_node.mesh = mesh
    mesh_node.material_override = material
    await process_frame
    await RenderingServer.frame_post_draw
    var image := get_root().get_texture().get_image()
    if image == null or image.is_empty():
        _fail("render capture returned empty image")
        return
    if image.save_png(path) != OK:
        _fail("failed to save render: %s" % path)

func _write_json(path: String, payload: Dictionary) -> void:
    var handle := FileAccess.open(path, FileAccess.WRITE)
    if handle == null:
        _fail("failed to open receipt")
        return
    handle.store_string(JSON.stringify(payload, "  ", false) + "\n")
    handle.close()

func _run() -> void:
    var oracle := _read_json(ORACLE_PATH)
    var owner_oracle := _read_json(OWNER_ORACLE_PATH)
    if oracle.is_empty() or owner_oracle.is_empty():
        return
    if String(oracle.get("result", "")) != "PASS_FRAGMENTED_VERTEX_ID_RUNS_TILE_EXACT_DYNAMIC_WINDOW":
        _fail("fragmented-run shader-driver preflight is not green")
        return
    if int(oracle.get("vertex_count", -1)) != EXPECTED_VERTICES:
        _fail("vertex count drift")
        return
    var groups: Array = oracle.get("groups", [])
    var flat_runs: Array = oracle.get("flat_vertex_id_runs", [])
    if groups.size() != 5 or flat_runs.is_empty():
        _fail("group/run identity drift")
        return
    if int(oracle.get("vertex_id_run_count", -1)) != flat_runs.size():
        _fail("run-count receipt drift")
        return
    var cursor := EXPECTED_WINDOW_START
    for run in flat_runs:
        if int(run.get("start", -1)) != cursor or int(run.get("end", -1)) <= cursor:
            _fail("VERTEX_ID runs no longer tile exact moving window")
            return
        cursor = int(run.get("end", -1))
    if cursor != EXPECTED_WINDOW_END:
        _fail("moving-window end drift")
        return

    var document := GLTFDocument.new()
    var state := GLTFState.new()
    if document.append_from_file(GLB_PATH, state) != OK:
        _fail("GLB import failed")
        return
    var imported_root := document.generate_scene(state)
    if imported_root == null:
        _fail("GLB generate_scene returned null")
        return
    get_root().add_child(imported_root)
    await process_frame
    var mesh_node := _find_mesh(imported_root)
    if mesh_node == null:
        _fail("no MeshInstance3D found")
        return
    var neutral_mesh := mesh_node.mesh as ArrayMesh
    if neutral_mesh == null or neutral_mesh.get_surface_count() != 1:
        _fail("receiver is not one-surface ArrayMesh")
        return
    var neutral_vertices: PackedVector3Array = neutral_mesh.surface_get_arrays(0)[Mesh.ARRAY_VERTEX]
    if neutral_vertices.size() != EXPECTED_VERTICES:
        _fail("imported vertex count drift")
        return

    var imported_format := neutral_mesh.surface_get_format(0)
    var imported_stride := RenderingServer.mesh_surface_get_format_vertex_stride(imported_format, EXPECTED_VERTICES)
    var imported_compressed := (imported_format & Mesh.ARRAY_FLAG_COMPRESS_ATTRIBUTES) != 0
    if imported_stride != EXPECTED_IMPORTED_STRIDE or not imported_compressed:
        _fail("candidate did not retain compressed imported positions")
        return
    var mutable_probe := _clone_mutable_mesh(neutral_mesh)
    var mutable_stride := RenderingServer.mesh_surface_get_format_vertex_stride(mutable_probe.surface_get_format(0), EXPECTED_VERTICES)
    if mutable_stride != EXPECTED_MUTABLE_STRIDE:
        _fail("control mutable position stride drift")
        return

    var shader := Shader.new()
    shader.code = FileAccess.get_file_as_string(SHADER_PATH)
    var control_material := ShaderMaterial.new()
    control_material.shader = shader
    control_material.set_shader_parameter("apply_driver", 0.0)
    var candidate_material := ShaderMaterial.new()
    candidate_material.shader = shader
    candidate_material.set_shader_parameter("apply_driver", 1.0)

    var camera := Camera3D.new()
    imported_root.add_child(camera)
    camera.position = Vector3(5.4, 3.4, 5.4)
    camera.look_at(Vector3(0.0, 2.0, 0.0), Vector3.UP)
    camera.fov = 42.0
    camera.current = true
    var light := DirectionalLight3D.new()
    imported_root.add_child(light)
    light.rotation_degrees = Vector3(-52.0, -28.0, 0.0)
    light.light_energy = 1.35
    light.shadow_enabled = false
    var world_environment := WorldEnvironment.new()
    var environment := Environment.new()
    environment.background_mode = Environment.BG_COLOR
    environment.background_color = Color(0.045, 0.05, 0.06, 1.0)
    environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
    environment.ambient_light_color = Color(0.52, 0.55, 0.60, 1.0)
    environment.ambient_light_energy = 0.82
    world_environment.environment = environment
    imported_root.add_child(world_environment)
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(RENDER_DIR))

    var owner_pose_by_driver := {}
    for pose in owner_oracle.get("poses", []):
        owner_pose_by_driver[String.num(float(pose.get("shared_driver_deg", 999.0)), 1)] = pose
    var rows: Array = []
    var maximum_cpu_vs_owner_delta := 0.0
    var maximum_control_readback_delta := 0.0
    var driver_rows: Array = oracle.get("representative_driver_deg", [])
    if driver_rows.size() != 5:
        _fail("representative driver field drift")
        return

    for driver_value in driver_rows:
        var driver := float(driver_value)
        var runtime_positions := _cpu_pose(neutral_vertices, groups, driver)
        if runtime_positions.size() != EXPECTED_VERTICES:
            return
        var owner_pose = owner_pose_by_driver.get(String.num(driver, 1), {})
        if typeof(owner_pose) != TYPE_DICTIONARY or owner_pose.is_empty():
            _fail("owner pose witness missing")
            return
        var owner_positions := _packed_vectors(owner_pose.get("control_target_positions_m", []))
        var cpu_vs_owner := _max_component_delta(runtime_positions, owner_positions)
        maximum_cpu_vs_owner_delta = max(maximum_cpu_vs_owner_delta, cpu_vs_owner)

        var control_mesh := _clone_mutable_mesh(neutral_mesh)
        control_mesh.surface_update_vertex_region(0, 0, runtime_positions.to_byte_array())
        await process_frame
        var control_after: PackedVector3Array = control_mesh.surface_get_arrays(0)[Mesh.ARRAY_VERTEX]
        var control_readback_delta := _max_component_delta(control_after, runtime_positions)
        maximum_control_readback_delta = max(maximum_control_readback_delta, control_readback_delta)

        control_material.set_shader_parameter("driver_deg", driver)
        candidate_material.set_shader_parameter("driver_deg", driver)
        var token := _driver_token(driver)
        await _capture(mesh_node, control_mesh, control_material, "%s/control_%s.png" % [RENDER_DIR, token])
        await _capture(mesh_node, neutral_mesh, candidate_material, "%s/candidate_%s.png" % [RENDER_DIR, token])
        rows.append({
            "shared_driver_deg": driver,
            "cpu_analytic_vs_exact_owner_max_component_delta_m": cpu_vs_owner,
            "control_mutable_readback_vs_cpu_analytic_max_component_delta_m": control_readback_delta,
        })

    var budget: Dictionary = oracle.get("representation_budget", {})
    var semantic_driver_bytes := int(budget.get("shader_semantic_driver_payload_bytes", -1))
    var pass53_partial_bytes := int(budget.get("pass53_partial_float32_position_packet_bytes", -1))
    if semantic_driver_bytes != 4 or pass53_partial_bytes != 3120:
        _fail("representation budget drift")
        return
    var imported_position_bytes := EXPECTED_VERTICES * imported_stride
    var mutable_position_bytes := EXPECTED_VERTICES * mutable_stride
    var receipt := {
        "schema": "axm.nature-runtime-east-rear-godot-shader-driver-receipt/v0.2",
        "state": "PASS_NATURE_EAST_REAR_RUNTIME_FRAGMENTED_VERTEX_ID_SHADER_DRIVER",
        "godot": Engine.get_version_info(),
        "receiver": {
            "vertex_count": EXPECTED_VERTICES,
            "surface_count": neutral_mesh.get_surface_count(),
            "vertex_id_run_count": flat_runs.size(),
            "candidate_imported_vertex_stride_bytes": imported_stride,
            "candidate_imported_positions_compressed": imported_compressed,
            "candidate_position_storage_bytes": imported_position_bytes,
            "pass53_mutable_position_storage_bytes": mutable_position_bytes,
            "position_storage_bytes_saved_vs_pass53_mutable": mutable_position_bytes - imported_position_bytes,
            "position_storage_reduction_percent_vs_pass53_mutable": float(mutable_position_bytes - imported_position_bytes) / float(mutable_position_bytes) * 100.0,
            "pass53_partial_float32_position_packet_bytes": pass53_partial_bytes,
            "shader_semantic_driver_payload_bytes": semantic_driver_bytes,
            "semantic_payload_bytes_saved_vs_pass53_partial": pass53_partial_bytes - semantic_driver_bytes,
            "semantic_payload_reduction_percent_vs_pass53_partial": float(pass53_partial_bytes - semantic_driver_bytes) / float(pass53_partial_bytes) * 100.0,
            "candidate_geometry_reindexed": false,
            "candidate_surface_count_changed": false,
            "candidate_cpu_position_buffer_mutated_per_pose": false,
        },
        "measurements": {
            "pose_count": rows.size(),
            "maximum_cpu_analytic_vs_exact_owner_component_delta_m": maximum_cpu_vs_owner_delta,
            "maximum_control_mutable_readback_vs_cpu_analytic_component_delta_m": maximum_control_readback_delta,
            "rows": rows,
        },
        "visual_tradeoff": {
            "additional_vertex_shader_control_flow": true,
            "vertex_id_range_tests_per_vertex_upper_bound": flat_runs.size(),
            "normal_or_tangent_deformation_correctness_proven": false,
            "art_direction_review_state": "HOLD_FIXED_VIEW_A_B_AND_FINAL_LOOKDEV",
        },
        "truth_boundary": {
            "single_range_per_branch_hypothesis_was_falsified": true,
            "shader_semantic_driver_payload_is_not_measured_gpu_command_transport": true,
            "candidate_gpu_vertex_positions_read_back_directly": false,
            "vertex_shader_range_tests_are_not_free_gpu_work": true,
            "target_device_cpu_gpu_fps_vram_thermal_battery_proven": false,
            "animation_timing_or_physical_wind_semantics_proven": false,
            "art_direction_or_visual_qa_acceptance_proven": false,
            "generic_vegetation_policy_proven": false,
            "canon_or_production_readiness_proven": false,
        },
    }
    _write_json(RECEIPT_PATH, receipt)
    print(JSON.stringify(receipt, "  ", false))
    quit(0)
