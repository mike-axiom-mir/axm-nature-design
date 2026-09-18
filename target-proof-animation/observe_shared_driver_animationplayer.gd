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
const MIN_DISTINCT_NATURAL_SAMPLES := 8
const MIN_NATURAL_WRAPS := 2
const REPRESENTATIVE_INDICES := [0, 10, 20, 30, 39]
const MIN_PEAK_CHANGED_PIXELS := 100

var receipt := {
    "schema": "axm.nature-animation-five-socket-godot-animationplayer-replay/v0.2",
    "state": "NOT_RUN",
    "renderer_boundary": "Godot 4.7.2 GL Compatibility; exact Technical-Art current-UC dynamic-window GLB imported, rebuilt as one mutable ArrayMesh, then driven by a proof-local AnimationPlayer discrete authored-sample track. Current-pair target correspondence is observed by full-control versus AnimationPlayer partial-update render identity at bounded representative samples, not by unsupported post-update CPU array readback."
}
var camera := Camera3D.new()
var environment := Environment.new()
var instance := MeshInstance3D.new()
var proof_material := StandardMaterial3D.new()

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

func _settle() -> void:
    await process_frame
    await RenderingServer.frame_post_draw

func _capture_image() -> Image:
    await _settle()
    var image := root.get_texture().get_image()
    if image == null or image.is_empty():
        _fail("target renderer returned no image")
        return Image.new()
    image.convert(Image.FORMAT_RGB8)
    return image

func _image_delta(left_image: Image, right_image: Image) -> Dictionary:
    if left_image.get_width() != right_image.get_width() or left_image.get_height() != right_image.get_height():
        _fail("rendered image dimensions differ")
        return {}
    var left := left_image.get_data()
    var right := right_image.get_data()
    if left.size() != right.size() or left.size() % 3 != 0:
        _fail("rendered RGB8 byte layout drift")
        return {}
    var changed_pixels := 0
    var max_channel_delta := 0
    for byte_index in range(0, left.size(), 3):
        var changed := false
        for channel in range(3):
            var delta := absi(int(left[byte_index + channel]) - int(right[byte_index + channel]))
            max_channel_delta = maxi(max_channel_delta, delta)
            if delta != 0:
                changed = true
        if changed:
            changed_pixels += 1
    return {
        "changed_pixels": changed_pixels,
        "total_pixels": int(left.size() / 3),
        "max_channel_delta": max_channel_delta,
        "byte_identical": changed_pixels == 0
    }

func _configure_scene(neutral_vertices: PackedVector3Array) -> void:
    root.size = Vector2i(900, 700)
    DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
    var minimum := Vector3(INF, INF, INF)
    var maximum := Vector3(-INF, -INF, -INF)
    for vertex in neutral_vertices:
        minimum = minimum.min(vertex)
        maximum = maximum.max(vertex)
    var center := (minimum + maximum) * 0.5
    var radius := maxf((maximum - minimum).length() * 0.5, 0.1)
    camera.projection = Camera3D.PROJECTION_ORTHOGONAL
    camera.size = radius * 2.65
    camera.near = radius * 0.001
    camera.far = radius * 20.0
    camera.position = center + Vector3(1.45, 1.15, 1.8).normalized() * radius * 4.2
    root.add_child(camera)
    camera.look_at(center)
    camera.current = true
    environment.background_mode = Environment.BG_COLOR
    environment.background_color = Color(0.035, 0.045, 0.06)
    environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
    environment.ambient_light_color = Color(0.62, 0.7, 0.82)
    environment.ambient_light_energy = 0.65
    var world := WorldEnvironment.new()
    world.environment = environment
    root.add_child(world)
    for rotation in [Vector3(-48, -28, 0), Vector3(-24, 138, 0)]:
        var light := DirectionalLight3D.new()
        light.rotation_degrees = rotation
        light.light_energy = 1.15
        root.add_child(light)
    proof_material.albedo_color = Color(0.42, 0.53, 0.34)
    proof_material.metallic = 0.0
    proof_material.roughness = 0.82
    proof_material.cull_mode = BaseMaterial3D.CULL_DISABLED
    instance.material_override = proof_material
    root.add_child(instance)

func _full_control_positions(neutral_vertices: PackedVector3Array, packet_rows) -> PackedVector3Array:
    var packet := _packet_vectors(packet_rows)
    if packet.size() != WINDOW_END - WINDOW_START:
        return PackedVector3Array()
    var out := neutral_vertices.duplicate()
    for local_index in range(packet.size()):
        out[WINDOW_START + local_index] = packet[local_index]
    return out

func _run() -> void:
    var oracle := _read_json(ORACLE_PATH)
    if oracle.get("schema") != EXPECTED_SCHEMA or oracle.get("result") != EXPECTED_RESULT:
        _fail("Animation target oracle missing or not green")
        return
    var receiver: Dictionary = oracle.get("receiver", {})
    if FileAccess.get_sha256(GLB_PATH) != String(receiver.get("receiver_glb_sha256", "")):
        _fail("exact Technical-Art receiver GLB identity mismatch")
        return
    var samples: Array = oracle.get("samples", [])
    if samples.size() != 41:
        _fail("Animation endpoint-inclusive sample count drift")
        return
    var dynamic_window = receiver.get("dynamic_window_vertices", [])
    if (
        int(receiver.get("vertex_count", -1)) != EXPECTED_VERTICES
        or not (dynamic_window is Array)
        or dynamic_window.size() != 2
        or int(dynamic_window[0]) != WINDOW_START
        or int(dynamic_window[1]) != WINDOW_END
    ):
        _fail("receiver vertex/window identity drift")
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
    imported_root.free()

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

    var packet_rows: Array = []
    for sample in samples:
        packet_rows.append(sample.get("dynamic_target_positions_m", []))
    if packet_rows[0] != packet_rows[40]:
        _fail("endpoint packet is not exact sample-zero closure")
        return

    var offset_delta := 0
    if OS.has_environment("AXM_ANIMATION_PACKET_OFFSET_DELTA_BYTES"):
        offset_delta = int(OS.get_environment("AXM_ANIMATION_PACKET_OFFSET_DELTA_BYTES"))
    _configure_scene(neutral_vertices)
    instance.mesh = mutable_mesh

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
    bridge.configure(mutable_mesh, packet_rows, EXPECTED_OFFSET + offset_delta)
    var player := _build_player(host, bridge, 40)

    var bridge_mismatches := 0
    player.play("shared_driver_loop")
    for index in range(40):
        player.seek(float(index) / 40.0, true)
        player.advance(0.0)
        if int(bridge.sample_index) != index:
            bridge_mismatches += 1
    if bridge_mismatches != 0:
        _fail("AnimationPlayer discrete exact-key bridge binding drift")
        return

    var neutral_bytes := neutral_vertices.to_byte_array()
    if neutral_bytes.size() != EXPECTED_VERTICES * EXPECTED_MUTABLE_STRIDE:
        _fail("neutral target byte serialization drift")
        return
    var representative_rows: Array = []
    var neutral_image: Image
    var positive_peak_image: Image
    var negative_peak_image: Image
    var max_control_candidate_changed_pixels := 0
    for representative_index in REPRESENTATIVE_INDICES:
        var expected_full := _full_control_positions(neutral_vertices, packet_rows[representative_index])
        if expected_full.size() != EXPECTED_VERTICES:
            _fail("representative full-control packet shape drift")
            return
        mutable_mesh.surface_update_vertex_region(0, 0, neutral_bytes)
        var applications_before_reseek := int(bridge.application_count)
        player.stop()
        player.play("shared_driver_loop")
        player.seek(float(representative_index) / 40.0, true)
        player.advance(0.0)
        if int(bridge.application_count) <= applications_before_reseek:
            _fail("representative AnimationPlayer seek did not reapply target packet after neutral reset")
            return
        if int(bridge.sample_index) != representative_index:
            _fail("representative AnimationPlayer bridge index drift")
            return
        var candidate_image := await _capture_image()
        mutable_mesh.surface_update_vertex_region(0, 0, expected_full.to_byte_array())
        var control_image := await _capture_image()
        var control_candidate := _image_delta(control_image, candidate_image)
        var changed_pixels := int(control_candidate.get("changed_pixels", -1))
        max_control_candidate_changed_pixels = maxi(max_control_candidate_changed_pixels, changed_pixels)
        if not bool(control_candidate.get("byte_identical", false)):
            receipt["representative_rows"] = representative_rows
            _fail("AnimationPlayer partial target update diverged from host-normalized full control at sample %s" % representative_index)
            return
        if representative_index == 0:
            neutral_image = candidate_image
        elif representative_index == 10:
            positive_peak_image = candidate_image
        elif representative_index == 30:
            negative_peak_image = candidate_image
        representative_rows.append({
            "sample_index": representative_index,
            "time_s": float(representative_index) / 40.0,
            "bridge_index": int(bridge.sample_index),
            "full_vs_partial_render_delta": control_candidate
        })

    if neutral_image == null or positive_peak_image == null or negative_peak_image == null:
        _fail("representative peak/neutral render set incomplete")
        return
    var positive_peak_motion := _image_delta(neutral_image, positive_peak_image)
    var negative_peak_motion := _image_delta(neutral_image, negative_peak_image)
    if int(positive_peak_motion.get("changed_pixels", 0)) <= MIN_PEAK_CHANGED_PIXELS or int(negative_peak_motion.get("changed_pixels", 0)) <= MIN_PEAK_CHANGED_PIXELS:
        _fail("current Animation target replay lacks discriminating rendered peak motion")
        return

    mutable_mesh.surface_update_vertex_region(0, 0, neutral_bytes)
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
        var current_index: int = int(bridge.sample_index)
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
        "animationplayer_bridge_index_mismatches": bridge_mismatches,
        "surface_update_application_count": int(bridge.application_count),
        "representative_render_checks": REPRESENTATIVE_INDICES.size(),
        "representative_full_vs_partial_render_changed_pixels_max": max_control_candidate_changed_pixels,
        "positive_peak_vs_neutral_render_delta": positive_peak_motion,
        "negative_peak_vs_neutral_render_delta": negative_peak_motion,
        "representative_rows": representative_rows
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
        "current_pair_target_correspondence_observed_by_render_identity": true,
        "unsupported_post_update_cpu_array_readback_used": false,
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
