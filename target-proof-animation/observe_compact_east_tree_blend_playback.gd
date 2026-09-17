extends SceneTree

const GENERATED_DIR := "res://generated-compact-east"
const OUTPUT_RECEIPT := "res://compact-east-tree-blend-playback-receipt.json"
const EXPECTED_VFX_PARENT := "cef2ad78d8e36a55ada5dad07329f1a7125d48de"
const EXPECTED_RUNTIME_REFERENCE := "6ea4148da61d3806123712e2eaf19613df9ae1eb"
const EXPECTED_NEUTRAL_DIGEST := "420135f6effbadb1b344675948b9ddc471dcb83177702888f0b32327c5121c18"
const DURATION_S := 0.5
const INTERVAL_COUNT := 16
const SAMPLE_COUNT := 17
const STEP_S := DURATION_S / INTERVAL_COUNT
const PEAK_PHASE := 8
const SOURCE_VERTICES := 390
const SOURCE_TRIANGLES := 570
const DENSE_SUBSTEPS := 8
const TARGET_WRAPS := 3
const OBSERVER_FPS_CAP := 240
const MAX_SOURCE_FAMILY_RESIDUAL_M := 1e-12
const MAX_KEY_GEOMETRY_RESIDUAL_M := 2e-6
const MAX_LINEAR_WEIGHT_RESIDUAL := 1e-5
const MAX_DIAGNOSTIC_ANALYTIC_GEOMETRY_DEVIATION_M := 0.00066

var receipt := {
    "schema": "axm.nature-animation-compact-east-single-shape-linear-playback/v0.1",
    "state": "NOT_RUN",
    "motion_boundary": "Exact VFX-authored 0.50 s / 17-state response remains source truth. This witness rebinds the newly evidenced one-normalized-blend-shape receiver to AnimationPlayer, proves exact authored-state hits, characterizes LINEAR between-key motion against the observed half-sine source family, and exercises repeated playback. It does not adopt Runtime policy or grant Art/QA smoothness acceptance.",
}

func read_json(path: String) -> Dictionary:
    if not FileAccess.file_exists(path):
        return {}
    var parsed = JSON.parse_string(FileAccess.get_file_as_string(path))
    return parsed as Dictionary if parsed is Dictionary else {}

func read_text(path: String) -> String:
    if not FileAccess.file_exists(path):
        return ""
    return FileAccess.get_file_as_string(path).strip_edges()

func write_receipt() -> void:
    var file := FileAccess.open(OUTPUT_RECEIPT, FileAccess.WRITE)
    if file != null:
        file.store_string(JSON.stringify(receipt, "  ") + "\n")
        file.close()

func fail(message: String) -> void:
    receipt["state"] = "FAIL_COMPACT_EAST_SINGLE_SHAPE_ANIMATION_PLAYBACK_OBSERVER"
    receipt["failure"] = message
    write_receipt()
    push_error(message)
    quit(1)

func source_to_godot(point: Array) -> Vector3:
    if point.size() != 3:
        fail("Nature vertex does not contain exactly three coordinates")
        return Vector3.ZERO
    return Vector3(float(point[0]), float(point[2]), float(point[1]))

func surface_arrays(payload: Dictionary) -> Array:
    var vertices = payload.get("vertices", [])
    var triangles = payload.get("triangles", [])
    if not (vertices is Array) or not (triangles is Array):
        return []
    if vertices.size() != SOURCE_VERTICES or triangles.size() != SOURCE_TRIANGLES:
        return []
    var surface := SurfaceTool.new()
    surface.begin(Mesh.PRIMITIVE_TRIANGLES)
    for triangle_value in triangles:
        if not (triangle_value is Array) or triangle_value.size() != 3:
            return []
        var triangle := triangle_value as Array
        for local_index in [0, 2, 1]:
            var vertex_index := int(triangle[local_index])
            if vertex_index < 0 or vertex_index >= vertices.size():
                return []
            surface.add_vertex(source_to_godot(vertices[vertex_index] as Array))
    surface.generate_normals()
    return surface.commit_to_arrays()

func phase_weight(phase_index: int) -> float:
    return sin(PI * float(phase_index) / float(INTERVAL_COUNT))

func analytic_weight(time_s: float) -> float:
    return sin(PI * clampf(time_s / DURATION_S, 0.0, 1.0))

func linear_key_weight(time_s: float) -> float:
    var clamped := clampf(time_s, 0.0, DURATION_S)
    if clamped >= DURATION_S:
        return phase_weight(INTERVAL_COUNT)
    var phase_f := clamped / STEP_S
    var lower := mini(int(floor(phase_f)), INTERVAL_COUNT - 1)
    var alpha := phase_f - float(lower)
    return lerpf(phase_weight(lower), phase_weight(lower + 1), alpha)

func source_family_residual(payloads: Array) -> float:
    var neutral := payloads[0] as Dictionary
    var peak := payloads[PEAK_PHASE] as Dictionary
    var neutral_vertices := neutral.get("vertices", []) as Array
    var peak_vertices := peak.get("vertices", []) as Array
    if neutral_vertices.size() != SOURCE_VERTICES or peak_vertices.size() != SOURCE_VERTICES:
        return INF
    var maximum := 0.0
    for phase_index in range(SAMPLE_COUNT):
        var payload := payloads[phase_index] as Dictionary
        var vertices := payload.get("vertices", []) as Array
        if vertices.size() != SOURCE_VERTICES or payload.get("triangles") != neutral.get("triangles"):
            return INF
        var weight := phase_weight(phase_index)
        for vertex_index in range(SOURCE_VERTICES):
            var actual := vertices[vertex_index] as Array
            var n := neutral_vertices[vertex_index] as Array
            var p := peak_vertices[vertex_index] as Array
            var predicted := Vector3(
                float(n[0]) + weight * (float(p[0]) - float(n[0])),
                float(n[1]) + weight * (float(p[1]) - float(n[1])),
                float(n[2]) + weight * (float(p[2]) - float(n[2]))
            )
            var observed := Vector3(float(actual[0]), float(actual[1]), float(actual[2]))
            maximum = maxf(maximum, predicted.distance_to(observed))
    return maximum

func build_single_shape_mesh(payloads: Array) -> ArrayMesh:
    var neutral_arrays := surface_arrays(payloads[0] as Dictionary)
    var peak_arrays := surface_arrays(payloads[PEAK_PHASE] as Dictionary)
    if neutral_arrays.is_empty() or peak_arrays.is_empty():
        return null
    var neutral_vertices := neutral_arrays[Mesh.ARRAY_VERTEX] as PackedVector3Array
    var peak_vertices := peak_arrays[Mesh.ARRAY_VERTEX] as PackedVector3Array
    var neutral_normals := neutral_arrays[Mesh.ARRAY_NORMAL] as PackedVector3Array
    var peak_normals := peak_arrays[Mesh.ARRAY_NORMAL] as PackedVector3Array
    if neutral_vertices.size() != SOURCE_TRIANGLES * 3 or peak_vertices.size() != neutral_vertices.size():
        return null
    if neutral_normals.size() != neutral_vertices.size() or peak_normals.size() != neutral_vertices.size():
        return null
    var blend_arrays := []
    blend_arrays.resize(Mesh.ARRAY_MAX)
    blend_arrays[Mesh.ARRAY_VERTEX] = peak_vertices
    blend_arrays[Mesh.ARRAY_NORMAL] = peak_normals
    var mesh := ArrayMesh.new()
    mesh.blend_shape_mode = Mesh.BLEND_SHAPE_MODE_NORMALIZED
    mesh.add_blend_shape("compact_east_peak")
    mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, neutral_arrays, [blend_arrays])
    return mesh

func max_vertex_delta_from_arrays(a: PackedVector3Array, b: PackedVector3Array) -> float:
    if a.size() != b.size():
        return INF
    var maximum := 0.0
    for index in range(a.size()):
        maximum = maxf(maximum, a[index].distance_to(b[index]))
    return maximum

func baked_source_residual(receiver: MeshInstance3D, payload: Dictionary) -> float:
    var baked := receiver.bake_mesh_from_current_blend_shape_mix()
    var expected := surface_arrays(payload)
    if baked == null or baked.get_surface_count() != 1 or expected.is_empty():
        return INF
    var actual_arrays := baked.surface_get_arrays(0)
    return max_vertex_delta_from_arrays(
        actual_arrays[Mesh.ARRAY_VERTEX] as PackedVector3Array,
        expected[Mesh.ARRAY_VERTEX] as PackedVector3Array
    )

func peak_displacement(payloads: Array) -> float:
    var neutral := surface_arrays(payloads[0] as Dictionary)
    var peak := surface_arrays(payloads[PEAK_PHASE] as Dictionary)
    if neutral.is_empty() or peak.is_empty():
        return INF
    return max_vertex_delta_from_arrays(
        neutral[Mesh.ARRAY_VERTEX] as PackedVector3Array,
        peak[Mesh.ARRAY_VERTEX] as PackedVector3Array
    )

func make_animation() -> Dictionary:
    var animation := Animation.new()
    animation.length = DURATION_S
    animation.loop_mode = Animation.LOOP_NONE
    var track := animation.add_track(Animation.TYPE_VALUE)
    animation.track_set_path(track, NodePath("receiver:blend_shapes/compact_east_peak"))
    animation.track_set_interpolation_type(track, Animation.INTERPOLATION_LINEAR)
    animation.value_track_set_update_mode(track, Animation.UPDATE_CONTINUOUS)
    for phase_index in range(SAMPLE_COUNT):
        animation.track_insert_key(track, STEP_S * phase_index, phase_weight(phase_index), 1.0)
    return {"animation": animation, "track": track}

func _initialize() -> void:
    Engine.max_fps = OBSERVER_FPS_CAP

    var summary := read_json(GENERATED_DIR + "/summary.json")
    if summary.get("state") != "PASS_COMPACT_EAST_TREE_BOUNDED_VISUAL_RESPONSE_CANDIDATE":
        fail("compact-east VFX source response evidence is missing or not green")
        return
    if String(summary.get("migrated_neutral_mesh_digest", "")) != EXPECTED_NEUTRAL_DIGEST:
        fail("compact-east migrated neutral digest drifted")
        return
    if int(summary.get("sample_count", 0)) != SAMPLE_COUNT:
        fail("compact-east response no longer contains 17 endpoint-inclusive states")
        return
    var response = summary.get("response", {})
    if not (response is Dictionary):
        fail("compact-east response contract missing")
        return
    if absf(float(response.get("duration_s", -1.0)) - DURATION_S) > 1e-12 or int(response.get("phase_count", -1)) != INTERVAL_COUNT:
        fail("compact-east response timing identity drifted")
        return

    var exact_head := read_text(GENERATED_DIR + "/exact-head.txt")
    var vfx_parent := read_text(GENERATED_DIR + "/vfx-parent-head.txt")
    var runtime_reference := read_text(GENERATED_DIR + "/runtime-reference-head.txt")
    if exact_head == "" or vfx_parent != EXPECTED_VFX_PARENT or runtime_reference != EXPECTED_RUNTIME_REFERENCE:
        fail("Animation / VFX / Runtime reference lineage binding is missing or drifted")
        return

    var payloads: Array = []
    for phase_index in range(SAMPLE_COUNT):
        var payload := read_json(GENERATED_DIR + "/phase_%02d_mesh.json" % phase_index)
        if payload.is_empty():
            fail("missing compact-tree phase payload %02d" % phase_index)
            return
        payloads.append(payload)

    var family_residual := source_family_residual(payloads)
    var peak_delta := peak_displacement(payloads)
    if not is_finite(family_residual) or not is_finite(peak_delta):
        fail("could not evaluate exact compact-east source family")
        return

    var root3d := Node3D.new()
    root3d.name = "PlaybackRoot"
    get_root().add_child(root3d)

    var receiver := MeshInstance3D.new()
    receiver.name = "receiver"
    receiver.mesh = build_single_shape_mesh(payloads)
    if receiver.mesh == null:
        fail("failed to build one-normalized-blend-shape receiver")
        return
    root3d.add_child(receiver)
    var receiver_id := int(receiver.get_instance_id())
    var mesh_id := int(receiver.mesh.get_instance_id())

    var blend_property := "blend_shapes/compact_east_peak"
    receiver.set(blend_property, 0.25)
    if absf(float(receiver.get(blend_property)) - 0.25) > 1e-6:
        fail("Godot blend-shape property identity could not be resolved")
        return
    receiver.set(blend_property, 0.0)

    var player := AnimationPlayer.new()
    player.name = "AnimationPlayer"
    player.root_node = NodePath("..")
    root3d.add_child(player)
    var built := make_animation()
    var animation := built["animation"] as Animation
    var track := int(built["track"])
    var library := AnimationLibrary.new()
    library.add_animation("response", animation)
    player.add_animation_library("", library)

    var max_key_geometry_residual := 0.0
    var key_rows: Array = []
    player.play("response")
    for phase_index in range(SAMPLE_COUNT):
        var time_s := STEP_S * phase_index
        player.seek(time_s, true)
        player.advance(0.0)
        var observed_weight := float(receiver.get(blend_property))
        var geometry_residual := baked_source_residual(receiver, payloads[phase_index] as Dictionary)
        max_key_geometry_residual = maxf(max_key_geometry_residual, geometry_residual)
        key_rows.append({
            "phase": phase_index,
            "time_s": time_s,
            "expected_weight": phase_weight(phase_index),
            "observed_weight": observed_weight,
            "geometry_residual_m": geometry_residual,
        })
    player.stop()

    var original_peak_key := float(animation.track_get_key_value(track, PEAK_PHASE))
    animation.track_set_key_value(track, PEAK_PHASE, 0.99)
    player.play("response")
    player.seek(STEP_S * PEAK_PHASE, true)
    player.advance(0.0)
    var mutation_residual := baked_source_residual(receiver, payloads[PEAK_PHASE] as Dictionary)
    player.stop()
    animation.track_set_key_value(track, PEAK_PHASE, original_peak_key)
    receiver.set(blend_property, 0.0)

    var dense_count := INTERVAL_COUNT * DENSE_SUBSTEPS + 1
    var max_linear_weight_residual := 0.0
    var max_analytic_weight_delta := 0.0
    var min_dense_weight := INF
    var max_dense_weight := -INF
    player.play("response")
    for sample_index in range(dense_count):
        var time_s := DURATION_S * float(sample_index) / float(dense_count - 1)
        player.seek(time_s, true)
        player.advance(0.0)
        var observed := float(receiver.get(blend_property))
        var expected_linear := linear_key_weight(time_s)
        var expected_analytic := analytic_weight(time_s)
        max_linear_weight_residual = maxf(max_linear_weight_residual, absf(observed - expected_linear))
        max_analytic_weight_delta = maxf(max_analytic_weight_delta, absf(observed - expected_analytic))
        min_dense_weight = minf(min_dense_weight, observed)
        max_dense_weight = maxf(max_dense_weight, observed)
    player.stop()

    var analytic_geometry_deviation := max_analytic_weight_delta * peak_delta

    animation.loop_mode = Animation.LOOP_LINEAR
    receiver.set(blend_property, 0.0)
    player.play("response")
    player.advance(0.0)
    var wraps := 0
    var frame_count := 0
    var max_live_linear_weight_residual := 0.0
    var min_live_weight := INF
    var max_live_weight := -INF
    var previous_position := float(player.current_animation_position)
    var start_us := Time.get_ticks_usec()
    var wrap_rows: Array = []
    while wraps < TARGET_WRAPS:
        await process_frame
        frame_count += 1
        if int(receiver.get_instance_id()) != receiver_id or int(receiver.mesh.get_instance_id()) != mesh_id:
            fail("one-shape playback receiver or mesh identity changed")
            return
        var position := float(player.current_animation_position)
        var observed := float(receiver.get(blend_property))
        var expected := linear_key_weight(position)
        max_live_linear_weight_residual = maxf(max_live_linear_weight_residual, absf(observed - expected))
        min_live_weight = minf(min_live_weight, observed)
        max_live_weight = maxf(max_live_weight, observed)
        if position + 1e-9 < previous_position:
            wraps += 1
            wrap_rows.append({
                "wrap_index": wraps,
                "position_s": position,
                "weight": observed,
                "wall_elapsed_s": float(Time.get_ticks_usec() - start_us) / 1000000.0,
            })
        previous_position = position
        if frame_count > 2000:
            fail("real playback did not reach three wraps within observer guard")
            return

    var checks := {
        "source_17_states_fit_observed_half_sine_family_within_1pm": family_residual <= MAX_SOURCE_FAMILY_RESIDUAL_M,
        "single_normalized_blend_shape_receiver_preserved": receiver.mesh.get_blend_shape_count() == 1 and receiver.mesh.blend_shape_mode == Mesh.BLEND_SHAPE_MODE_NORMALIZED,
        "all_17_authored_keys_hit_source_geometry_within_2um": max_key_geometry_residual <= MAX_KEY_GEOMETRY_RESIDUAL_M,
        "negative_peak_weight_mutation_rejected": mutation_residual > 0.001,
        "dense_animationplayer_matches_linear_key_interpolation": max_linear_weight_residual <= MAX_LINEAR_WEIGHT_RESIDUAL,
        "dense_linear_candidate_has_no_weight_overshoot": min_dense_weight >= -1e-6 and max_dense_weight <= 1.000001,
        "analytic_family_deviation_is_measured_not_hidden": analytic_geometry_deviation > 0.0 and analytic_geometry_deviation <= MAX_DIAGNOSTIC_ANALYTIC_GEOMETRY_DEVIATION_M,
        "three_real_animationplayer_wraps_observed": wraps == TARGET_WRAPS,
        "real_playback_tracks_linear_candidate": max_live_linear_weight_residual <= MAX_LINEAR_WEIGHT_RESIDUAL,
        "real_playback_has_no_weight_overshoot": min_live_weight >= -1e-6 and max_live_weight <= 1.000001,
        "persistent_receiver_and_mesh_identity": int(receiver.get_instance_id()) == receiver_id and int(receiver.mesh.get_instance_id()) == mesh_id,
    }

    var all_green := true
    for value in checks.values():
        if not bool(value):
            all_green = false
            break

    receipt["state"] = "PASS_COMPACT_EAST_SINGLE_SHAPE_LINEAR_ANIMATIONPLAYER_PLAYBACK_CHARACTERIZED" if all_green else "HOLD_COMPACT_EAST_SINGLE_SHAPE_LINEAR_ANIMATIONPLAYER_PLAYBACK"
    receipt["godot_version"] = Engine.get_version_info()
    receipt["animation_head"] = exact_head
    receipt["vfx_parent_head"] = vfx_parent
    receipt["runtime_reference_head"] = runtime_reference
    receipt["migrated_neutral_mesh_digest"] = EXPECTED_NEUTRAL_DIGEST
    receipt["duration_s"] = DURATION_S
    receipt["interval_count"] = INTERVAL_COUNT
    receipt["sample_count_endpoint_inclusive"] = SAMPLE_COUNT
    receipt["dense_sample_count"] = dense_count
    receipt["dense_substeps_per_authored_interval"] = DENSE_SUBSTEPS
    receipt["source_half_sine_family_max_residual_m"] = family_residual
    receipt["peak_source_displacement_m"] = peak_delta
    receipt["max_authored_key_geometry_residual_m"] = max_key_geometry_residual
    receipt["negative_peak_weight_mutation_geometry_residual_m"] = mutation_residual
    receipt["max_dense_animationplayer_vs_manual_linear_weight_residual"] = max_linear_weight_residual
    receipt["max_dense_linear_vs_analytic_half_sine_weight_delta"] = max_analytic_weight_delta
    receipt["max_dense_linear_vs_analytic_half_sine_geometry_envelope_m"] = analytic_geometry_deviation
    receipt["dense_weight_range"] = [min_dense_weight, max_dense_weight]
    receipt["real_playback_wrap_count"] = wraps
    receipt["real_playback_process_frames"] = frame_count
    receipt["max_real_playback_vs_manual_linear_weight_residual"] = max_live_linear_weight_residual
    receipt["real_playback_weight_range"] = [min_live_weight, max_live_weight]
    receipt["wraps"] = wrap_rows
    receipt["authored_key_rows"] = key_rows
    receipt["checks"] = checks
    receipt["truth_boundary"] = {
        "exact_vfx_source_states_reused_unchanged": true,
        "runtime_single_shape_candidate_referenced_not_adopted": true,
        "animationplayer_single_shape_linear_candidate_tested": true,
        "authored_state_geometry_equivalence_tested": true,
        "between_key_linear_motion_tested": true,
        "between_key_motion_is_animation_candidate_not_vfx_source_truth": true,
        "analytic_half_sine_family_used_as_diagnostic_reference_not_new_source_semantics": true,
        "continuous_visual_smoothness_accepted": false,
        "normal_or_shaded_equivalence_accepted": false,
        "physical_wind_or_biomechanics": false,
        "runtime_controller_or_state_machine": false,
        "target_device_performance_or_delivery": false,
        "map_receiving_scene": false,
        "gameplay_or_collision": false,
        "art_direction_or_visual_qa_acceptance": false,
        "canon_or_production_readiness": false,
    }
    write_receipt()
    quit(0)
