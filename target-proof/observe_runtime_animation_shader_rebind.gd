extends SceneTree

const ANIMATION_ORACLE_PATH := "res://generated/animation-shared-driver-target-oracle.json"
const SHADER_ORACLE_PATH := "res://generated/runtime-shader-driver-oracle.json"
const GLB_PATH := "res://generated/nature-east-rear-dynamic-window.glb"
const SHADER_PATH := "res://generated/runtime-shader-driver.gdshader"
const RECEIPT_PATH := "res://runtime-animation-shader-rebind-receipt.json"
const RENDER_DIR := "res://renders/runtime-animation-shader-rebind"
const EXPECTED_VERTICES := 390
const EXPECTED_WINDOW_START := 110
const EXPECTED_WINDOW_END := 370
const EXPECTED_WINDOW_COUNT := 260
const EXPECTED_IMPORTED_STRIDE := 8
const EXPECTED_MUTABLE_STRIDE := 12
const EXPECTED_PACKET_BYTES := 3120
const EXPECTED_VISIBLE_SAMPLES := 40
const CAPTURE_INDICES := [0, 5, 10, 15, 20, 25, 30, 35, 39]

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

func _vec3(row: Variant) -> Vector3:
    if typeof(row) != TYPE_ARRAY or row.size() != 3:
        _fail("invalid vec3 row")
        return Vector3.ZERO
    return Vector3(float(row[0]), float(row[1]), float(row[2]))

func _packed_vectors(rows: Array) -> PackedVector3Array:
    var result := PackedVector3Array()
    result.resize(rows.size())
    for index in range(rows.size()):
        result[index] = _vec3(rows[index])
    return result

func _max_dynamic_delta(full: PackedVector3Array, expected_dynamic: PackedVector3Array) -> float:
    if full.size() != EXPECTED_VERTICES or expected_dynamic.size() != EXPECTED_WINDOW_COUNT:
        return INF
    var maximum := 0.0
    for local_index in range(EXPECTED_WINDOW_COUNT):
        var actual := full[EXPECTED_WINDOW_START + local_index]
        var expected := expected_dynamic[local_index]
        maximum = max(maximum, abs(actual.x - expected.x))
        maximum = max(maximum, abs(actual.y - expected.y))
        maximum = max(maximum, abs(actual.z - expected.z))
    return maximum

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
    var animation_oracle := _read_json(ANIMATION_ORACLE_PATH)
    var shader_oracle := _read_json(SHADER_ORACLE_PATH)
    if animation_oracle.is_empty() or shader_oracle.is_empty():
        return
    if String(animation_oracle.get("result", "")) != "PASS_CURRENT_ANIMATION_SHARED_DRIVER_PACKETS_MATCH_TA_DYNAMIC_WINDOW":
        _fail("current Animation target oracle is not green")
        return
    if String(shader_oracle.get("result", "")) != "PASS_FRAGMENTED_VERTEX_ID_RUNS_TILE_EXACT_DYNAMIC_WINDOW":
        _fail("Runtime shader oracle is not green")
        return
    var receiver: Dictionary = animation_oracle.get("receiver", {})
    var dynamic_window: Array = receiver.get("dynamic_window_vertices", [])
    if dynamic_window.size() != 2 or int(dynamic_window[0]) != EXPECTED_WINDOW_START or int(dynamic_window[1]) != EXPECTED_WINDOW_END:
        _fail("Animation dynamic window drift")
        return
    if int(receiver.get("dynamic_vertex_count", -1)) != EXPECTED_WINDOW_COUNT:
        _fail("Animation dynamic vertex count drift")
        return
    var samples: Array = animation_oracle.get("samples", [])
    if samples.size() != 41:
        _fail("Animation endpoint-inclusive sample count drift")
        return
    var first_packet: Array = samples[0].get("dynamic_target_positions_m", [])
    var endpoint_packet: Array = samples[40].get("dynamic_target_positions_m", [])
    if first_packet != endpoint_packet:
        _fail("Animation endpoint packet no longer closes to sample zero")
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
        _fail("receiver vertex count drift")
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

    var maximum_control_dynamic_readback_delta := 0.0
    var capture_rows: Array = []
    for sample_index in range(EXPECTED_VISIBLE_SAMPLES):
        var sample: Dictionary = samples[sample_index]
        if int(sample.get("index", -1)) != sample_index:
            _fail("Animation sample index drift")
            return
        var driver := float(sample.get("shared_driver_deg", 999.0))
        var dynamic_positions := _packed_vectors(sample.get("dynamic_target_positions_m", []))
        if dynamic_positions.size() != EXPECTED_WINDOW_COUNT:
            _fail("Animation dynamic packet length drift")
            return
        var packet := dynamic_positions.to_byte_array()
        if packet.size() != EXPECTED_PACKET_BYTES:
            _fail("Animation dynamic packet byte size drift")
            return

        var control_mesh := _clone_mutable_mesh(neutral_mesh)
        control_mesh.surface_update_vertex_region(0, EXPECTED_WINDOW_START * EXPECTED_MUTABLE_STRIDE, packet)
        await process_frame
        var control_after: PackedVector3Array = control_mesh.surface_get_arrays(0)[Mesh.ARRAY_VERTEX]
        var readback_delta := _max_dynamic_delta(control_after, dynamic_positions)
        maximum_control_dynamic_readback_delta = max(maximum_control_dynamic_readback_delta, readback_delta)
        if readback_delta > 0.000005:
            _fail("control dynamic readback exceeds target envelope")
            return

        if CAPTURE_INDICES.has(sample_index):
            candidate_material.set_shader_parameter("driver_deg", driver)
            control_material.set_shader_parameter("driver_deg", driver)
            var token := "%02d" % sample_index
            await _capture(mesh_node, control_mesh, control_material, "%s/control_%s.png" % [RENDER_DIR, token])
            await _capture(mesh_node, neutral_mesh, candidate_material, "%s/candidate_%s.png" % [RENDER_DIR, token])
            capture_rows.append({"sample_index": sample_index, "time_s": float(sample.get("time_s", -1.0)), "shared_driver_deg": driver})

    var control_loop_semantic_bytes := EXPECTED_VISIBLE_SAMPLES * EXPECTED_PACKET_BYTES
    var shader_loop_semantic_bytes := EXPECTED_VISIBLE_SAMPLES * 4
    var receipt := {
        "schema": "axm.nature-runtime-current-animation-shader-rebind/v0.1",
        "state": "PASS_RUNTIME_CURRENT_ANIMATION_LOOP_OVER_COMPRESSED_SHADER_DRIVER",
        "godot": Engine.get_version_info(),
        "receiver": {
            "vertex_count": EXPECTED_VERTICES,
            "surface_count": neutral_mesh.get_surface_count(),
            "candidate_imported_vertex_stride_bytes": imported_stride,
            "candidate_imported_position_stride_bytes": imported_stride,
            "candidate_imported_positions_compressed": imported_compressed,
            "candidate_position_storage_bytes": EXPECTED_VERTICES * imported_stride,
            "control_mutable_position_storage_bytes": EXPECTED_VERTICES * mutable_stride,
            "position_storage_bytes_avoided": EXPECTED_VERTICES * mutable_stride - EXPECTED_VERTICES * imported_stride,
            "dynamic_window_vertices": [EXPECTED_WINDOW_START, EXPECTED_WINDOW_END],
            "dynamic_packet_bytes_per_visible_sample": EXPECTED_PACKET_BYTES,
            "shader_semantic_driver_bytes_per_visible_sample": 4,
            "visible_authored_samples": EXPECTED_VISIBLE_SAMPLES,
            "control_loop_semantic_payload_bytes": control_loop_semantic_bytes,
            "shader_loop_semantic_payload_bytes": shader_loop_semantic_bytes,
            "loop_semantic_payload_bytes_avoided": control_loop_semantic_bytes - shader_loop_semantic_bytes,
            "loop_semantic_payload_reduction_percent": float(control_loop_semantic_bytes - shader_loop_semantic_bytes) / float(control_loop_semantic_bytes) * 100.0,
            "candidate_cpu_position_buffer_mutated_per_sample": false
        },
        "measurements": {
            "all_visible_authored_samples_checked": EXPECTED_VISIBLE_SAMPLES,
            "maximum_control_dynamic_readback_component_delta_m": maximum_control_dynamic_readback_delta,
            "capture_rows": capture_rows
        },
        "visual_tradeoff": {
            "fresh_capture_pair_count": capture_rows.size(),
            "additional_vertex_shader_control_flow": true,
            "normal_or_tangent_deformation_correctness_proven": false,
            "art_direction_review_state": "HOLD_FRESH_RASTER_COMPARISON_AND_FINAL_LOOKDEV"
        },
        "truth_boundary": {
            "shader_semantic_payload_is_not_measured_gpu_command_transport": true,
            "runtime_controller_state_machine_input_claimed": false,
            "animationplayer_natural_playback_claimed": false,
            "target_device_cpu_gpu_fps_vram_thermal_battery_proven": false,
            "candidate_gpu_vertex_positions_read_back_directly": false,
            "newer_rigging_hierarchy_6cf64925_adopted": false,
            "physical_wind_or_biological_motion_claimed": false,
            "art_direction_or_visual_qa_acceptance_proven": false,
            "canon_or_production_readiness_proven": false
        }
    }
    _write_json(RECEIPT_PATH, receipt)
    print(JSON.stringify(receipt, "  ", false))
    quit(0)
