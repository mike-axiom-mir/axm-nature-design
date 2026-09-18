extends SceneTree

const ORACLE_PATH := "res://generated/nature-east-rear-dynamic-window-target-oracle.json"
const GLB_PATH := "res://generated/nature-east-rear-dynamic-window.glb"
const RECEIPT_PATH := "res://runtime-east-rear-target-host-receipt.json"
const RENDER_DIR := "res://renders/runtime-east-rear-target-host"
const EXPECTED_VERTICES := 390
const WINDOW_START := 110
const WINDOW_END := 370
const EXPECTED_IMPORTED_STRIDE := 8
const EXPECTED_MUTABLE_STRIDE := 12
const EXPECTED_OFFSET := 1320
const EXPECTED_LENGTH := 3120
const POSITION_GATE_M := 0.000005

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

func _packed_vectors(rows: Array) -> PackedVector3Array:
    var out := PackedVector3Array()
    out.resize(rows.size())
    for index in range(rows.size()):
        var row = rows[index]
        if typeof(row) != TYPE_ARRAY or row.size() != 3:
            _fail("invalid position row")
            return PackedVector3Array()
        out[index] = Vector3(float(row[0]), float(row[1]), float(row[2]))
    return out

func _clone_mutable_mesh(source: ArrayMesh) -> ArrayMesh:
    var result := ArrayMesh.new()
    for surface in range(source.get_surface_count()):
        var arrays := source.surface_get_arrays(surface)
        result.add_surface_from_arrays(
            source.surface_get_primitive_type(surface),
            arrays,
            [],
            {},
            Mesh.ARRAY_FLAG_USE_DYNAMIC_UPDATE
        )
        var material := source.surface_get_material(surface)
        if material != null:
            result.surface_set_material(surface, material)
    return result

func _max_component_delta(left: PackedVector3Array, right: PackedVector3Array) -> float:
    if left.size() != right.size():
        return INF
    var result := 0.0
    for index in range(left.size()):
        result = max(result, abs(left[index].x - right[index].x))
        result = max(result, abs(left[index].y - right[index].y))
        result = max(result, abs(left[index].z - right[index].z))
    return result

func _max_component_delta_static(left: PackedVector3Array, right: PackedVector3Array) -> float:
    if left.size() != right.size():
        return INF
    var result := 0.0
    for index in range(left.size()):
        if index >= WINDOW_START and index < WINDOW_END:
            continue
        result = max(result, abs(left[index].x - right[index].x))
        result = max(result, abs(left[index].y - right[index].y))
        result = max(result, abs(left[index].z - right[index].z))
    return result

func _max_window_packet_delta(full_positions: PackedVector3Array, packet: PackedVector3Array) -> float:
    if full_positions.size() != EXPECTED_VERTICES or packet.size() != WINDOW_END - WINDOW_START:
        return INF
    var result := 0.0
    for local_index in range(packet.size()):
        var full_index := WINDOW_START + local_index
        result = max(result, abs(full_positions[full_index].x - packet[local_index].x))
        result = max(result, abs(full_positions[full_index].y - packet[local_index].y))
        result = max(result, abs(full_positions[full_index].z - packet[local_index].z))
    return result

func _max_distance(left: PackedVector3Array, right: PackedVector3Array) -> float:
    if left.size() != right.size():
        return INF
    var result := 0.0
    for index in range(left.size()):
        result = max(result, left[index].distance_to(right[index]))
    return result

func _driver_token(value: float) -> String:
    var token := String.num(value, 1)
    token = token.replace("-", "m")
    token = token.replace(".", "p")
    return token

func _capture(mesh_node: MeshInstance3D, mesh: ArrayMesh, path: String) -> void:
    mesh_node.mesh = mesh
    await process_frame
    await RenderingServer.frame_post_draw
    var image := get_root().get_texture().get_image()
    if image == null or image.is_empty():
        _fail("render capture returned empty image")
        return
    var error := image.save_png(path)
    if error != OK:
        _fail("failed to save render %s error=%s" % [path, error])

func _write_json(path: String, payload: Dictionary) -> void:
    var handle := FileAccess.open(path, FileAccess.WRITE)
    if handle == null:
        _fail("failed to open receipt for write: %s" % path)
        return
    handle.store_string(JSON.stringify(payload, "  ", false) + "\n")
    handle.close()

func _run() -> void:
    var oracle := _read_json(ORACLE_PATH)
    if oracle.is_empty():
        return
    if int(oracle.get("vertex_count", -1)) != EXPECTED_VERTICES:
        _fail("oracle vertex count drift")
        return
    var oracle_window = oracle.get("dynamic_window_vertices", [])
    if typeof(oracle_window) != TYPE_ARRAY or oracle_window.size() != 2:
        _fail("oracle dynamic window shape drift")
        return
    var start_kind := typeof(oracle_window[0])
    var end_kind := typeof(oracle_window[1])
    if (start_kind != TYPE_INT and start_kind != TYPE_FLOAT) or (end_kind != TYPE_INT and end_kind != TYPE_FLOAT):
        _fail("oracle dynamic window type drift")
        return
    if float(oracle_window[0]) != float(WINDOW_START) or float(oracle_window[1]) != float(WINDOW_END):
        _fail("oracle dynamic window value drift")
        return
    if int(oracle.get("dynamic_byte_offset", -1)) != EXPECTED_OFFSET:
        _fail("oracle byte offset drift")
        return
    if int(oracle.get("dynamic_byte_length", -1)) != EXPECTED_LENGTH:
        _fail("oracle byte length drift")
        return

    var document := GLTFDocument.new()
    var state := GLTFState.new()
    var load_error := document.append_from_file(GLB_PATH, state)
    if load_error != OK:
        _fail("GLB import failed error=%s" % load_error)
        return
    var imported_root := document.generate_scene(state)
    if imported_root == null:
        _fail("GLB generate_scene returned null")
        return
    get_root().add_child(imported_root)
    await process_frame

    var mesh_node := _find_mesh(imported_root)
    if mesh_node == null:
        _fail("no MeshInstance3D found in receiver")
        return
    var neutral_mesh := mesh_node.mesh as ArrayMesh
    if neutral_mesh == null:
        _fail("receiver mesh is not ArrayMesh")
        return
    if neutral_mesh.get_surface_count() != 1:
        _fail("expected one receiver surface")
        return

    var neutral_arrays := neutral_mesh.surface_get_arrays(0)
    var neutral_vertices: PackedVector3Array = neutral_arrays[Mesh.ARRAY_VERTEX]
    if neutral_vertices.size() != EXPECTED_VERTICES:
        _fail("imported vertex count drift")
        return

    var imported_format := neutral_mesh.surface_get_format(0)
    var imported_stride := RenderingServer.mesh_surface_get_format_vertex_stride(imported_format, EXPECTED_VERTICES)
    var imported_offset := RenderingServer.mesh_surface_get_format_offset(imported_format, EXPECTED_VERTICES, Mesh.ARRAY_VERTEX)
    var imported_compressed := (imported_format & Mesh.ARRAY_FLAG_COMPRESS_ATTRIBUTES) != 0
    if imported_stride != EXPECTED_IMPORTED_STRIDE:
        _fail("Godot imported vertex stride drift: %s" % imported_stride)
        return
    if imported_offset != 0:
        _fail("Godot imported vertex position offset drift: %s" % imported_offset)
        return
    if not imported_compressed:
        _fail("Godot exact GLB receiver unexpectedly lost automatic attribute compression")
        return

    var mutable_probe := _clone_mutable_mesh(neutral_mesh)
    var mutable_format := mutable_probe.surface_get_format(0)
    var mutable_stride := RenderingServer.mesh_surface_get_format_vertex_stride(mutable_format, EXPECTED_VERTICES)
    var mutable_offset := RenderingServer.mesh_surface_get_format_offset(mutable_format, EXPECTED_VERTICES, Mesh.ARRAY_VERTEX)
    var mutable_compressed := (mutable_format & Mesh.ARRAY_FLAG_COMPRESS_ATTRIBUTES) != 0
    var mutable_dynamic := (mutable_format & Mesh.ARRAY_FLAG_USE_DYNAMIC_UPDATE) != 0
    if mutable_stride != EXPECTED_MUTABLE_STRIDE:
        _fail("Godot mutable vertex stride drift: %s" % mutable_stride)
        return
    if mutable_offset != 0:
        _fail("Godot mutable vertex position offset drift: %s" % mutable_offset)
        return
    if mutable_compressed:
        _fail("Runtime mutable receiver unexpectedly retained compressed position storage")
        return
    if not mutable_dynamic:
        _fail("Runtime mutable receiver lost ARRAY_FLAG_USE_DYNAMIC_UPDATE")
        return

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
    var offset_delta := 0
    if OS.has_environment("AXM_RUNTIME_OFFSET_DELTA_BYTES"):
        offset_delta = int(OS.get_environment("AXM_RUNTIME_OFFSET_DELTA_BYTES"))
    var candidate_offset := EXPECTED_OFFSET + offset_delta

    var pose_rows: Array = oracle.get("poses", [])
    if pose_rows.size() != 5:
        _fail("expected five retained Runtime witnesses")
        return

    var result_rows: Array = []
    var max_control_candidate_delta := 0.0
    var max_control_expected_delta := 0.0
    var max_candidate_expected_delta := 0.0
    var max_static_delta := 0.0
    var max_owner_window_packet_delta := 0.0
    var max_imported_static_vs_owner_delta := 0.0
    var max_readback_motion := 0.0

    for pose in pose_rows:
        var driver := float(pose.get("shared_driver_deg", 999.0))
        var owner_control_positions := _packed_vectors(pose.get("control_target_positions_m", []))
        var dynamic_positions := _packed_vectors(pose.get("candidate_dynamic_target_positions_m", []))
        if owner_control_positions.size() != EXPECTED_VERTICES:
            _fail("owner control position count drift at driver %s" % driver)
            return
        if dynamic_positions.size() != WINDOW_END - WINDOW_START:
            _fail("dynamic position count drift at driver %s" % driver)
            return

        var owner_window_packet_delta := _max_window_packet_delta(owner_control_positions, dynamic_positions)
        var imported_static_vs_owner_delta := _max_component_delta_static(neutral_vertices, owner_control_positions)
        max_owner_window_packet_delta = max(max_owner_window_packet_delta, owner_window_packet_delta)
        max_imported_static_vs_owner_delta = max(max_imported_static_vs_owner_delta, imported_static_vs_owner_delta)

        var runtime_control_positions := neutral_vertices.duplicate()
        for local_index in range(dynamic_positions.size()):
            runtime_control_positions[WINDOW_START + local_index] = dynamic_positions[local_index]

        var control_mesh := _clone_mutable_mesh(neutral_mesh)
        var candidate_mesh := _clone_mutable_mesh(neutral_mesh)
        control_mesh.surface_update_vertex_region(0, 0, runtime_control_positions.to_byte_array())
        candidate_mesh.surface_update_vertex_region(0, candidate_offset, dynamic_positions.to_byte_array())
        await process_frame

        var control_after_arrays := control_mesh.surface_get_arrays(0)
        var candidate_after_arrays := candidate_mesh.surface_get_arrays(0)
        var control_after: PackedVector3Array = control_after_arrays[Mesh.ARRAY_VERTEX]
        var candidate_after: PackedVector3Array = candidate_after_arrays[Mesh.ARRAY_VERTEX]

        var control_expected_delta := _max_component_delta(control_after, runtime_control_positions)
        var candidate_expected_delta := _max_component_delta(candidate_after, runtime_control_positions)
        var pair_delta := _max_component_delta(control_after, candidate_after)
        var static_delta := _max_component_delta_static(control_after, candidate_after)
        var readback_motion := _max_distance(candidate_after, neutral_vertices)

        max_control_expected_delta = max(max_control_expected_delta, control_expected_delta)
        max_candidate_expected_delta = max(max_candidate_expected_delta, candidate_expected_delta)
        max_control_candidate_delta = max(max_control_candidate_delta, pair_delta)
        max_static_delta = max(max_static_delta, static_delta)
        max_readback_motion = max(max_readback_motion, readback_motion)

        var token := _driver_token(driver)
        var control_render := "%s/control_%s.png" % [RENDER_DIR, token]
        var candidate_render := "%s/candidate_%s.png" % [RENDER_DIR, token]
        await _capture(mesh_node, control_mesh, control_render)
        await _capture(mesh_node, candidate_mesh, candidate_render)

        result_rows.append({
            "shared_driver_deg": driver,
            "owner_window_packet_max_component_delta_m": owner_window_packet_delta,
            "imported_static_vs_owner_max_component_delta_m": imported_static_vs_owner_delta,
            "control_readback_vs_runtime_expected_max_component_delta_m": control_expected_delta,
            "candidate_readback_vs_runtime_expected_max_component_delta_m": candidate_expected_delta,
            "control_candidate_readback_max_component_delta_m": pair_delta,
            "static_control_candidate_max_component_delta_m": static_delta,
            "candidate_readback_max_distance_from_neutral_m": readback_motion,
            "control_render": control_render,
            "candidate_render": candidate_render,
        })

    var state_name := "PASS_NATURE_EAST_REAR_RUNTIME_WINDOW_GODOT_PARTIAL_VERTEX_UPDATE"
    var passed := (
        candidate_offset == EXPECTED_OFFSET
        and max_owner_window_packet_delta <= POSITION_GATE_M
        and max_control_expected_delta <= POSITION_GATE_M
        and max_candidate_expected_delta <= POSITION_GATE_M
        and max_control_candidate_delta <= POSITION_GATE_M
        and max_static_delta <= POSITION_GATE_M
        and max_readback_motion > 0.05
    )
    if not passed:
        state_name = "FAIL_NATURE_EAST_REAR_RUNTIME_WINDOW_GODOT_PARTIAL_VERTEX_UPDATE"

    var imported_position_bytes := EXPECTED_VERTICES * imported_stride
    var mutable_position_bytes := EXPECTED_VERTICES * mutable_stride
    var storage_delta_bytes := mutable_position_bytes - imported_position_bytes
    var receipt := {
        "schema": "axm.nature-runtime-east-rear-godot-partial-window-receipt/v0.2",
        "state": state_name,
        "godot": Engine.get_version_info(),
        "receiver": {
            "vertex_count": EXPECTED_VERTICES,
            "surface_count": neutral_mesh.get_surface_count(),
            "imported_vertex_stride_bytes": imported_stride,
            "imported_vertex_position_offset_bytes": imported_offset,
            "imported_positions_compressed": imported_compressed,
            "imported_position_buffer_bytes": imported_position_bytes,
            "mutable_vertex_stride_bytes": mutable_stride,
            "mutable_vertex_position_offset_bytes": mutable_offset,
            "mutable_positions_compressed": mutable_compressed,
            "mutable_dynamic_update_flag": mutable_dynamic,
            "mutable_position_buffer_bytes": mutable_position_bytes,
            "mutable_vs_imported_position_storage_delta_bytes": storage_delta_bytes,
            "mutable_vs_imported_position_storage_delta_percent": float(storage_delta_bytes) / float(imported_position_bytes) * 100.0,
            "dynamic_window_vertices": [WINDOW_START, WINDOW_END],
            "control_full_update_bytes": EXPECTED_VERTICES * mutable_stride,
            "candidate_update_offset_bytes": candidate_offset,
            "candidate_update_bytes": EXPECTED_LENGTH,
            "candidate_update_bytes_saved": EXPECTED_VERTICES * mutable_stride - EXPECTED_LENGTH,
            "candidate_update_percent_saved": float(EXPECTED_VERTICES * mutable_stride - EXPECTED_LENGTH) / float(EXPECTED_VERTICES * mutable_stride) * 100.0,
            "api": "ArrayMesh.surface_update_vertex_region",
        },
        "measurements": {
            "pose_count": pose_rows.size(),
            "maximum_owner_window_packet_component_delta_m": max_owner_window_packet_delta,
            "maximum_imported_static_vs_owner_component_delta_m": max_imported_static_vs_owner_delta,
            "maximum_control_readback_vs_runtime_expected_component_delta_m": max_control_expected_delta,
            "maximum_candidate_readback_vs_runtime_expected_component_delta_m": max_candidate_expected_delta,
            "maximum_control_candidate_readback_component_delta_m": max_control_candidate_delta,
            "maximum_static_control_candidate_component_delta_m": max_static_delta,
            "maximum_candidate_readback_distance_from_neutral_m": max_readback_motion,
            "pose_rows": result_rows,
        },
        "visual_tradeoff": {
            "fixed_view_control_candidate_pairs_captured": pose_rows.size(),
            "pixel_comparison_performed_by_followup_workflow_step": true,
            "normal_or_tangent_buffer_updated": false,
            "material_scope": oracle.get("target_material_scope", "UNKNOWN"),
            "imported_receiver_uses_8_byte_compressed_positions": true,
            "runtime_mutable_receiver_uses_12_byte_float_positions": true,
            "runtime_mutable_position_storage_cost_bytes": storage_delta_bytes,
            "art_direction_review_state": "HOLD_ART_QA_FINAL_LOOK_NORMAL_DEFORMATION_AND_TARGET_DEVICE",
        },
        "truth_boundary": {
            "real_target_host_partial_vertex_update_api_exercised": true,
            "full_position_control_api_exercised": true,
            "source_or_geometry_reauthored": false,
            "index_buffer_reauthored": false,
            "godot_import_compression_observed_not_assumed": true,
            "runtime_mutable_surface_conversion_required_for_float32_update_path": true,
            "compressed_position_direct_update_proven": false,
            "normal_or_tangent_deformation_correctness_proven": false,
            "physical_wind_or_animation_timing_proven": false,
            "target_device_cpu_gpu_fps_vram_thermal_battery_proven": false,
            "art_direction_or_visual_qa_acceptance_proven": false,
            "generic_vegetation_policy_proven": false,
            "canon_or_production_readiness_proven": false,
        },
    }
    _write_json(RECEIPT_PATH, receipt)
    if not passed:
        _fail("target-host partial-window comparison failed: %s" % JSON.stringify(receipt))
        return
    print(JSON.stringify(receipt, "  ", false))
    quit(0)
