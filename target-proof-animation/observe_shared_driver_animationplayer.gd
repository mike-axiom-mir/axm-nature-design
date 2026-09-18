extends SceneTree

const ORACLE_PATH := "res://generated/animation-shared-driver-target-oracle.json"
const GLB_PATH := "res://generated/nature-east-rear-dynamic-window.glb"
const RECEIPT_PATH := "res://animation-shared-driver-godot-target-receipt.json"
const EXPECTED_SCHEMA := "axm.nature-animation-five-socket-ta-window-replay/v0.1"
const EXPECTED_RESULT := "PASS_CURRENT_ANIMATION_SHARED_DRIVER_PACKETS_MATCH_TA_DYNAMIC_WINDOW"
const EXPECTED_VERTICES := 390
const WINDOW_START := 110
const WINDOW_END := 370
const EXPECTED_MUTABLE_STRIDE := 12
const EXPECTED_OFFSET := 1320
const EXPECTED_LENGTH := 3120
const POSITION_GATE_M := 0.000005
const MIN_DISTINCT_NATURAL_SAMPLES := 8
const MIN_NATURAL_WRAPS := 2

var receipt := {
    "schema": "axm.nature-animation-five-socket-godot-animationplayer-replay/v0.1",
    "state": "NOT_RUN",
    "renderer_boundary": "Godot 4.7.2 GL Compatibility; exact Technical-Art current-UC dynamic-window GLB imported, rebuilt as one mutable ArrayMesh, then driven by a proof-local AnimationPlayer discrete authored-sample track."
}

func _initialize() -> void:
    call_deferred("_run")

func _read_json(path: String) -> Dictionary:
    if not FileAccess.file_exists(path):
        _fail("missing JSON: %s" % path)
        return {}
    var parsed = JSON.parse_string(FileAccess.get_file_as_string(path))
    if typeof(parsed) != TYPE_DICTIONARY:
        _fail("invalid JSON object: %s" % path)
        return {}
    return parsed

func _write_receipt() -> void:
    var file := FileAccess.open(RECEIPT_PATH, FileAccess.WRITE)
    if file != null:
        file.store_string(JSON.stringify(receipt, "  ", false) + "\n")
        file.close()

func _fail(message: String) -> void:
    receipt["state"] = "FAIL_NATURE_SHARED_DRIVER_ANIMATIONPLAYER_TARGET_REPLAY"
    receipt["failure"] = message
    _write_receipt()
    push_error(message)
    quit(1)

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

func _packet_vectors(rows) -> PackedVector3Array:
    if not (rows is Array):
        _fail("dynamic packet is not an array")
        return PackedVector3Array()
    var out := PackedVector3Array()
    out.resize(rows.size())
    for index in range(rows.size()):
        var row = rows[index]
        if not (row is Array) or row.size() != 3:
            _fail("dynamic packet vector shape drift")
            return PackedVector3Array()
        out[index] = Vector3(float(row[0]), float(row[1]), float(row[2]))
    return out

func _window_component_delta(full_positions: PackedVector3Array, expected_rows) -> float:
    if full_positions.size() != EXPECTED_VERTICES or not (expected_rows is Array) or expected_rows.size() != WINDOW_END - WINDOW_START:
        return INF
    var result := 0.0
    for local_index in range(expected_rows.size()):
        var row = expected_rows[local_index]
        var expected := Vector3(float(row[0]), float(row[1]), float(row[2]))
        var actual := full_positions[WINDOW_START + local_index]
        result = maxf(result, absf(actual.x - expected.x))
        result = maxf(result, absf(actual.y - expected.y))
        result = maxf(result, absf(actual.z - expected.z))
    return result

func _static_component_delta(left: PackedVector3Array, right: PackedVector3Array) -> float:
    if left.size() != EXPECTED_VERTICES or right.size() != EXPECTED_VERTICES:
        return INF
    var result := 0.0
    for index in range(EXPECTED_VERTICES):
        if index >= WINDOW_START and index < WINDOW_END:
            continue
        result = maxf(result, absf(left[index].x - right[index].x))
        result = maxf(result, absf(left[index].y - right[index].y))
        result = maxf(result, absf(left[index].z - right[index].z))
    return result

func _maximum_distance_from_neutral(current: PackedVector3Array, neutral: PackedVector3Array) -> float:
    if current.size() != EXPECTED_VERTICES or neutral.size() != EXPECTED_VERTICES:
        return INF
    var result := 0.0
    for index in range(WINDOW_START, WINDOW_END):
        result = maxf(result, current[index].distance_to(neutral[index]))
    return result

func _build_player(host: Node, bridge: Node, sample_count: int) -> AnimationPlayer:
    var player := AnimationPlayer.new()
    player.name = "AnimationPlayer"
    host.add_child(player)
    player.root_node = NodePath("..")

    var clip := Animation.new()
    clip.length = 1.0
    clip.loop_mode = Animation.LOOP_LINEAR
    var track := clip.add_track(Animation.TYPE_VALUE)
    clip.track_set_path(track, NodePath("Bridge:sample_index"))
    clip.track_set_interpolation_type(track, Animation.INTERPOLATION_NEAREST)
    clip.value_track_set_update_mode(track, Animation.UPDATE_DISCRETE)
    for index in range(sample_count):
        clip.track_insert_key(track, float(index) / 40.0, index)

    var library := AnimationLibrary.new()
    library.add_animation("shared_driver_loop", clip)
    player.add_animation_library("", library)
    return player

func _run() -> void:
    var oracle := _read_json(ORACLE_PATH)
    if oracle.get("schema") != EXPECTED_SCHEMA or oracle.get("result") != EXPECTED_RESULT:
        _fail("Animation target oracle missing or not green")
        return
    if FileAccess.get_sha256(GLB_PATH) != String((oracle.get("receiver") or {}).get("receiver_glb_sha256", "")):
        _fail("exact Technical-Art receiver GLB identity mismatch")
        return
    var samples: Array = oracle.get("samples", [])
    if samples.size() != 41:
        _fail("Animation endpoint-inclusive sample count drift")
        return
    var receiver: Dictionary = oracle.get("receiver", {})
    if int(receiver.get("vertex_count", -1)) != EXPECTED_VERTICES:
        _fail("receiver vertex count drift")
        return
    if receiver.get("dynamic_window_vertices", []) != [WINDOW_START, WINDOW_END]:
        _fail("receiver dynamic window drift")
        return
    if int(receiver.get("dynamic_byte_offset", -1)) != EXPECTED_OFFSET or int(receiver.get("dynamic_byte_length", -1)) != EXPECTED_LENGTH:
        _fail("receiver dynamic byte window drift")
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
        _fail("receiver import contains no MeshInstance3D")
        return
    var imported_mesh := mesh_node.mesh as ArrayMesh
    if imported_mesh == null or imported_mesh.get_surface_count() != 1:
        _fail("receiver import is not one ArrayMesh surface")
        return
    var imported_arrays := imported_mesh.surface_get_arrays(0)
    var neutral_vertices: PackedVector3Array = imported_arrays[Mesh.ARRAY_VERTEX]
    if neutral_vertices.size() != EXPECTED_VERTICES:
        _fail("receiver imported vertex count drift")
        return

    var mutable_mesh := _clone_mutable_mesh(imported_mesh)
    var mutable_format := mutable_mesh.surface_get_format(0)
    var mutable_stride := RenderingServer.mesh_surface_get_format_vertex_stride(mutable_format, EXPECTED_VERTICES)
    var mutable_offset := RenderingServer.mesh_surface_get_format_offset(mutable_format, EXPECTED_VERTICES, Mesh.ARRAY_VERTEX)
    if mutable_stride != EXPECTED_MUTABLE_STRIDE or mutable_offset != 0:
        _fail("mutable receiver float32 position layout drift")
        return
    if (mutable_format & Mesh.ARRAY_FLAG_USE_DYNAMIC_UPDATE) == 0:
        _fail("mutable receiver lost ARRAY_FLAG_USE_DYNAMIC_UPDATE")
        return
    mesh_node.mesh = mutable_mesh

    var packet_rows: Array = []
    for sample in samples:
        packet_rows.append(sample.get("dynamic_target_positions_m", []))
    if packet_rows[0] != packet_rows[40]:
        _fail("endpoint packet is not exact sample-zero closure")
        return

    var host := Node.new()
    host.name = "AnimationReplayHost"
    get_root().add_child(host)
    var bridge_script = load("res://sample_bridge.gd")
    if bridge_script == null:
        _fail("cannot load proof-local sample bridge")
        return
    var bridge = bridge_script.new()
    bridge.name = "Bridge"
    host.add_child(bridge)

    var offset_delta := 0
    if OS.has_environment("AXM_ANIMATION_PACKET_OFFSET_DELTA_BYTES"):
        offset_delta = int(OS.get_environment("AXM_ANIMATION_PACKET_OFFSET_DELTA_BYTES"))
    bridge.configure(mutable_mesh, packet_rows, EXPECTED_OFFSET + offset_delta)
    var player := _build_player(host, bridge, 40)

    var max_seek_delta := 0.0
    var max_static_drift := 0.0
    var max_motion := 0.0
    var exact_seek_rows: Array = []
    player.play("shared_driver_loop")
    for index in range(40):
        var time_s := float(index) / 40.0
        player.seek(time_s, true)
        player.advance(0.0)
        await process_frame
        var after_arrays := mutable_mesh.surface_get_arrays(0)
        var after: PackedVector3Array = after_arrays[Mesh.ARRAY_VERTEX]
        var delta := _window_component_delta(after, samples[index].get("dynamic_target_positions_m", []))
        var static_drift := _static_component_delta(after, neutral_vertices)
        var motion := _maximum_distance_from_neutral(after, neutral_vertices)
        max_seek_delta = maxf(max_seek_delta, delta)
        max_static_drift = maxf(max_static_drift, static_drift)
        max_motion = maxf(max_motion, motion)
        exact_seek_rows.append({
            "index": index,
            "time_s": time_s,
            "bridge_index": bridge.sample_index,
            "dynamic_readback_max_component_delta_m": delta,
            "static_readback_max_component_delta_m": static_drift,
            "maximum_dynamic_distance_from_imported_neutral_m": motion
        })
        if bridge.sample_index != index:
            _fail("AnimationPlayer discrete exact-key binding drift at index %s observed %s" % [index, bridge.sample_index])
            return
        if delta > POSITION_GATE_M or static_drift > POSITION_GATE_M:
            receipt["exact_seek_rows"] = exact_seek_rows
            receipt["maximum_exact_seek_dynamic_readback_delta_m"] = max_seek_delta
            receipt["maximum_static_readback_drift_m"] = max_static_drift
            _fail("AnimationPlayer exact-key target readback mismatch at sample %s" % index)
            return

    # Endpoint sample 40 is an exact duplicate of sample 0 by the owner contract.
    player.seek(0.0, true)
    player.advance(0.0)
    await process_frame
    var endpoint_arrays := mutable_mesh.surface_get_arrays(0)
    var endpoint_positions: PackedVector3Array = endpoint_arrays[Mesh.ARRAY_VERTEX]
    var endpoint_delta := _window_component_delta(endpoint_positions, samples[40].get("dynamic_target_positions_m", []))
    if endpoint_delta > POSITION_GATE_M:
        _fail("endpoint-neutral target replay closure drift")
        return
    if max_motion <= 0.05:
        _fail("target replay did not produce discriminating dynamic motion")
        return

    # Characterize natural process-frame delivery without demanding that every
    # authored 40 Hz slot be observed by this proof host. Missing slots are
    # retained as evidence rather than converted into source-timing defects.
    player.stop()
    player.play("shared_driver_loop")
    player.seek(0.0, true)
    player.advance(0.0)
    var natural_observed: Array[int] = []
    var natural_unique := {}
    var natural_wraps := 0
    var previous_index: int = int(bridge.sample_index)
    var change_intervals_ms: Array[float] = []
    var last_change_usec := Time.get_ticks_usec()
    var natural_start_usec := last_change_usec
    while natural_wraps < MIN_NATURAL_WRAPS and Time.get_ticks_usec() - natural_start_usec < 4500000:
        await process_frame
        var current_index: int = bridge.sample_index
        if current_index != previous_index:
            var now_usec := Time.get_ticks_usec()
            change_intervals_ms.append(float(now_usec - last_change_usec) / 1000.0)
            last_change_usec = now_usec
            natural_observed.append(current_index)
            natural_unique[current_index] = true
            if current_index < previous_index:
                natural_wraps += 1
            previous_index = current_index

    var natural_elapsed_ms := float(Time.get_ticks_usec() - natural_start_usec) / 1000.0
    var natural_distinct := natural_unique.size()
    if natural_wraps < MIN_NATURAL_WRAPS:
        _fail("natural AnimationPlayer replay did not cross required loop seams")
        return
    if natural_distinct < MIN_DISTINCT_NATURAL_SAMPLES:
        _fail("natural AnimationPlayer replay did not expose enough discriminating authored states")
        return

    var minimum_change_interval_ms := INF
    var maximum_change_interval_ms := 0.0
    var mean_change_interval_ms := 0.0
    for value in change_intervals_ms:
        minimum_change_interval_ms = minf(minimum_change_interval_ms, value)
        maximum_change_interval_ms = maxf(maximum_change_interval_ms, value)
        mean_change_interval_ms += value
    if change_intervals_ms.size() > 0:
        mean_change_interval_ms /= float(change_intervals_ms.size())
    else:
        minimum_change_interval_ms = 0.0

    receipt["state"] = "PASS_NATURE_SHARED_DRIVER_ANIMATIONPLAYER_OVER_TA_DYNAMIC_WINDOW_RECEIVER"
    receipt["godot"] = Engine.get_version_info()
    receipt["receiver"] = {
        "vertex_count": EXPECTED_VERTICES,
        "dynamic_window_vertices": [WINDOW_START, WINDOW_END],
        "mutable_position_stride_bytes": mutable_stride,
        "dynamic_byte_offset": EXPECTED_OFFSET + offset_delta,
        "dynamic_byte_length": EXPECTED_LENGTH,
        "technical_art_current_animation_rigging_pair_adoption": false
    }
    receipt["exact_seek"] = {
        "visible_authored_samples_checked": 40,
        "endpoint_sample_40_checked_as_exact_sample_0": true,
        "maximum_dynamic_readback_component_delta_m": max_seek_delta,
        "maximum_static_readback_component_delta_m": max_static_drift,
        "endpoint_dynamic_readback_component_delta_m": endpoint_delta,
        "maximum_dynamic_distance_from_imported_neutral_m": max_motion,
        "rows": exact_seek_rows
    }
    receipt["natural_playback_observation"] = {
        "required_wraps": MIN_NATURAL_WRAPS,
        "observed_wraps": natural_wraps,
        "distinct_authored_sample_indices_observed": natural_distinct,
        "observed_sample_indices_in_change_order": natural_observed,
        "elapsed_ms": natural_elapsed_ms,
        "sample_change_observation_count": change_intervals_ms.size(),
        "minimum_process_observed_change_interval_ms": minimum_change_interval_ms,
        "mean_process_observed_change_interval_ms": mean_change_interval_ms,
        "maximum_process_observed_change_interval_ms": maximum_change_interval_ms,
        "full_40hz_source_slot_delivery_claimed": false,
        "target_device_or_display_cadence_claimed": false
    }
    receipt["truth_boundary"] = {
        "real_godot_animationplayer_replay_exercised": true,
        "technical_art_current_pair_adoption_claimed": false,
        "runtime_controller_state_machine_or_input_claimed": false,
        "full_40hz_wall_clock_slot_delivery_claimed": false,
        "physical_wind_or_biological_motion_claimed": false,
        "continuous_collision_or_physics_claimed": false,
        "gameplay_acceptance_claimed": false,
        "art_or_visual_qa_acceptance_claimed": false,
        "canon_or_production_readiness_claimed": false
    }
    _write_receipt()
    quit(0)
