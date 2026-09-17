extends SceneTree

const GENERATED_DIR := "res://generated-compact-east"
const OUTPUT_RECEIPT := "res://compact-east-tree-animation-playback-receipt.json"
const EXPECTED_VFX_PARENT := "cef2ad78d8e36a55ada5dad07329f1a7125d48de"
const EXPECTED_NEUTRAL_DIGEST := "420135f6effbadb1b344675948b9ddc471dcb83177702888f0b32327c5121c18"
const DURATION_S := 0.5
const INTERVAL_COUNT := 16
const SAMPLE_COUNT := 17
const STEP_S := DURATION_S / INTERVAL_COUNT
const TARGET_WRAPS := 3
const OBSERVER_FPS_CAP := 240

var receipt := {
    "schema": "axm.nature-animation-compact-east-discrete-phase-playback/v0.1",
    "state": "NOT_RUN",
    "motion_boundary": "Exact VFX-authored endpoint-inclusive 17-state half-sine response. AnimationPlayer uses DISCRETE mesh-resource keys only; this witness does not invent interpolation, physical wind, biomechanics, runtime-controller policy, target-device timing or final visual acceptance.",
}

func read_json(path: String) -> Dictionary:
    if not FileAccess.file_exists(path):
        return {}
    var parsed = JSON.parse_string(FileAccess.get_file_as_string(path))
    return parsed as Dictionary if parsed is Dictionary else {}

func write_receipt() -> void:
    var file := FileAccess.open(OUTPUT_RECEIPT, FileAccess.WRITE)
    if file != null:
        file.store_string(JSON.stringify(receipt, "  ") + "\n")
        file.close()

func fail(message: String) -> void:
    receipt["state"] = "FAIL_COMPACT_EAST_TREE_ANIMATION_PLAYBACK_OBSERVER"
    receipt["failure"] = message
    write_receipt()
    push_error(message)
    quit(1)

func source_to_godot(point: Array) -> Vector3:
    if point.size() != 3:
        fail("Nature vertex does not contain exactly three coordinates")
        return Vector3.ZERO
    return Vector3(float(point[0]), float(point[2]), float(point[1]))

func build_mesh(payload: Dictionary) -> ArrayMesh:
    var vertices = payload.get("vertices", [])
    var triangles = payload.get("triangles", [])
    if not (vertices is Array) or not (triangles is Array):
        fail("compact-tree phase payload lacks vertex/triangle arrays")
        return null
    if vertices.size() != 390 or triangles.size() != 570:
        fail("compact-tree phase payload count drifted")
        return null
    var surface := SurfaceTool.new()
    surface.begin(Mesh.PRIMITIVE_TRIANGLES)
    for triangle_value in triangles:
        if not (triangle_value is Array) or triangle_value.size() != 3:
            fail("compact-tree triangle is malformed")
            return null
        var triangle := triangle_value as Array
        for local_index in [0, 2, 1]:
            var vertex_index := int(triangle[local_index])
            if vertex_index < 0 or vertex_index >= vertices.size():
                fail("compact-tree triangle index is out of range")
                return null
            var point = vertices[vertex_index]
            if not (point is Array):
                fail("compact-tree vertex is malformed")
                return null
            surface.add_vertex(source_to_godot(point))
    surface.generate_normals()
    var mesh := surface.commit()
    if mesh == null:
        fail("SurfaceTool failed to build compact-tree phase mesh")
        return null
    return mesh

func mesh_max_vertex_delta(first: ArrayMesh, second: ArrayMesh) -> float:
    if first.get_surface_count() != 1 or second.get_surface_count() != 1:
        fail("phase mesh surface count drifted")
        return INF
    var first_arrays := first.surface_get_arrays(0)
    var second_arrays := second.surface_get_arrays(0)
    var a = first_arrays[Mesh.ARRAY_VERTEX]
    var b = second_arrays[Mesh.ARRAY_VERTEX]
    if not (a is PackedVector3Array) or not (b is PackedVector3Array) or a.size() != b.size():
        fail("phase mesh vertex arrays are not comparable")
        return INF
    var maximum := 0.0
    for index in range(a.size()):
        maximum = maxf(maximum, a[index].distance_to(b[index]))
    return maximum

func find_active_phase(receiver: MeshInstance3D, meshes: Array) -> int:
    for index in range(meshes.size()):
        if receiver.mesh == meshes[index]:
            return index
    return -1

func missing_loop_phases(seen: Dictionary) -> Array:
    var missing: Array = []
    for index in range(INTERVAL_COUNT):
        if not seen.has(index):
            missing.append(index)
    return missing

func make_animation(meshes: Array) -> Animation:
    var animation := Animation.new()
    animation.length = DURATION_S
    animation.loop_mode = Animation.LOOP_NONE
    var track := animation.add_track(Animation.TYPE_VALUE)
    animation.track_set_path(track, NodePath("receiver:mesh"))
    animation.value_track_set_update_mode(track, Animation.UPDATE_DISCRETE)
    for index in range(SAMPLE_COUNT):
        animation.track_insert_key(track, STEP_S * index, meshes[index], 1.0)
    return animation

func _initialize() -> void:
    Engine.max_fps = OBSERVER_FPS_CAP

    var summary := read_json(GENERATED_DIR + "/summary.json")
    if summary.get("state") != "PASS_COMPACT_EAST_TREE_BOUNDED_VISUAL_RESPONSE_CANDIDATE":
        fail("compact-tree VFX source response evidence is missing or not green")
        return
    if String(summary.get("migrated_neutral_mesh_digest", "")) != EXPECTED_NEUTRAL_DIGEST:
        fail("compact-tree migrated neutral digest drifted")
        return
    if int(summary.get("sample_count", 0)) != SAMPLE_COUNT:
        fail("compact-tree response no longer contains 17 endpoint-inclusive states")
        return
    var response = summary.get("response", {})
    if not (response is Dictionary):
        fail("compact-tree response contract missing")
        return
    if absf(float(response.get("duration_s", -1.0)) - DURATION_S) > 1e-12 or int(response.get("phase_count", -1)) != INTERVAL_COUNT:
        fail("compact-tree response timing identity drifted")
        return

    var head_path := GENERATED_DIR + "/exact-head.txt"
    var parent_path := GENERATED_DIR + "/vfx-parent-head.txt"
    if not FileAccess.file_exists(head_path) or not FileAccess.file_exists(parent_path):
        fail("exact Animation/VFX head binding is missing")
        return
    var exact_head := FileAccess.get_file_as_string(head_path).strip_edges()
    var vfx_parent := FileAccess.get_file_as_string(parent_path).strip_edges()
    if vfx_parent != EXPECTED_VFX_PARENT:
        fail("VFX parent identity drifted")
        return

    var payloads: Array = []
    var meshes: Array = []
    for phase_index in range(SAMPLE_COUNT):
        var payload := read_json(GENERATED_DIR + "/phase_%02d_mesh.json" % phase_index)
        if payload.is_empty():
            fail("missing compact-tree phase payload %02d" % phase_index)
            return
        payloads.append(payload)
        var mesh := build_mesh(payload)
        if mesh == null:
            return
        meshes.append(mesh)

    var endpoint_delta := mesh_max_vertex_delta(meshes[0], meshes[16])
    var seam_authored_delta := mesh_max_vertex_delta(meshes[15], meshes[16])
    var seam_loop_delta := mesh_max_vertex_delta(meshes[15], meshes[0])
    var peak_delta := mesh_max_vertex_delta(meshes[0], meshes[8])

    var mutated_payload := (payloads[16] as Dictionary).duplicate(true)
    var mutated_vertices = mutated_payload.get("vertices", [])
    if not (mutated_vertices is Array) or mutated_vertices.is_empty():
        fail("could not construct endpoint negative control")
        return
    var first_point = (mutated_vertices[0] as Array).duplicate()
    first_point[0] = float(first_point[0]) + 0.001
    mutated_vertices[0] = first_point
    mutated_payload["vertices"] = mutated_vertices
    var mutated_mesh := build_mesh(mutated_payload)
    if mutated_mesh == null:
        return
    var mutated_endpoint_delta := mesh_max_vertex_delta(meshes[0], mutated_mesh)
    var negative_endpoint_rejected := mutated_endpoint_delta > 0.0009

    var root3d := Node3D.new()
    root3d.name = "PlaybackRoot"
    get_root().add_child(root3d)

    var receiver := MeshInstance3D.new()
    receiver.name = "receiver"
    receiver.mesh = meshes[0]
    root3d.add_child(receiver)
    var receiver_instance_id := int(receiver.get_instance_id())

    var player := AnimationPlayer.new()
    player.name = "AnimationPlayer"
    player.root_node = NodePath("..")
    root3d.add_child(player)
    var library := AnimationLibrary.new()
    var animation := make_animation(meshes)
    library.add_animation("response", animation)
    player.add_animation_library("", library)

    # Exact endpoint key check through AnimationPlayer before enabling loop observation.
    player.play("response")
    player.advance(DURATION_S)
    var endpoint_track_phase := find_active_phase(receiver, meshes)
    var endpoint_track_applied := endpoint_track_phase == 16
    player.stop()

    receiver.mesh = meshes[0]
    animation.loop_mode = Animation.LOOP_LINEAR
    player.play("response")
    player.advance(0.0)

    var initial_phase := find_active_phase(receiver, meshes)
    if initial_phase != 0:
        fail("AnimationPlayer did not start on exact phase 00")
        return

    var transitions: Array = [{"wrap": 0, "position_s": 0.0, "phase_index": 0, "wall_elapsed_s": 0.0}]
    var completed_cycles: Array = []
    var seen: Dictionary = {0: true}
    var wraps := 0
    var active_mismatches := 0
    var unexpected_reversals := 0
    var previous_position := float(player.current_animation_position)
    var previous_phase := initial_phase
    var start_us := Time.get_ticks_usec()
    var cycle_start_us := start_us
    var previous_frame_us := start_us
    var min_frame_ms := INF
    var max_frame_ms := 0.0
    var sum_frame_ms := 0.0
    var frame_count := 0

    while wraps < TARGET_WRAPS:
        await process_frame
        var now_us := Time.get_ticks_usec()
        var frame_ms := float(now_us - previous_frame_us) / 1000.0
        previous_frame_us = now_us
        min_frame_ms = minf(min_frame_ms, frame_ms)
        max_frame_ms = maxf(max_frame_ms, frame_ms)
        sum_frame_ms += frame_ms
        frame_count += 1

        if int(receiver.get_instance_id()) != receiver_instance_id:
            fail("Animation playback receiver identity changed")
            return

        var position := float(player.current_animation_position)
        var active_phase := find_active_phase(receiver, meshes)
        if active_phase < 0:
            fail("AnimationPlayer applied a mesh outside the pinned 17-state set")
            return

        var wrapped := position + 1e-9 < previous_position
        if wrapped:
            var missing := missing_loop_phases(seen)
            completed_cycles.append({
                "wrap_index": wraps + 1,
                "wall_duration_s": float(now_us - cycle_start_us) / 1000000.0,
                "observed_phase_count_0_to_15": INTERVAL_COUNT - missing.size(),
                "missing_phases_0_to_15": missing,
                "pre_wrap_phase": previous_phase,
                "post_wrap_phase": active_phase,
            })
            wraps += 1
            cycle_start_us = now_us
            seen = {}
        elif position + 1e-9 < previous_position:
            unexpected_reversals += 1

        seen[active_phase] = true
        var expected_phase := int(floor(position / STEP_S + 1e-9))
        expected_phase = mini(maxi(expected_phase, 0), 16)
        if active_phase != expected_phase:
            active_mismatches += 1

        if active_phase != previous_phase or wrapped:
            transitions.append({
                "wrap": wraps,
                "position_s": position,
                "phase_index": active_phase,
                "expected_phase_index": expected_phase,
                "wall_elapsed_s": float(now_us - start_us) / 1000000.0,
            })
        previous_position = position
        previous_phase = active_phase

    var all_loop_phases_observed := true
    for cycle_value in completed_cycles:
        var cycle := cycle_value as Dictionary
        if not (cycle.get("missing_phases_0_to_15", []) as Array).is_empty():
            all_loop_phases_observed = false

    var checks := {
        "exact_endpoint_key_applied_by_animationplayer": endpoint_track_applied,
        "endpoint_geometry_closes_exactly": endpoint_delta <= 1e-12,
        "loop_seam_step_equals_authored_final_step": absf(seam_loop_delta - seam_authored_delta) <= 1e-12,
        "peak_geometry_is_distinct_and_within_vfx_ceiling": peak_delta >= 0.11475 and peak_delta <= 0.135000000001,
        "negative_endpoint_mutation_rejected": negative_endpoint_rejected,
        "persistent_receiver_identity": int(receiver.get_instance_id()) == receiver_instance_id,
        "three_real_animationplayer_wraps_observed": wraps == TARGET_WRAPS,
        "active_mesh_matches_animation_position": active_mismatches == 0,
        "no_unexpected_position_reversals": unexpected_reversals == 0,
        "all_discrete_loop_phases_observed_each_cycle": all_loop_phases_observed,
    }

    var all_green := true
    for value in checks.values():
        if not bool(value):
            all_green = false
            break

    receipt["state"] = "PASS_COMPACT_EAST_TREE_TARGET_HOST_DISCRETE_PHASE_PLAYBACK_AND_LOOP_SEAM" if all_green else "HOLD_COMPACT_EAST_TREE_TARGET_HOST_DISCRETE_PHASE_PLAYBACK"
    receipt["godot_version"] = Engine.get_version_info()
    receipt["animation_head"] = exact_head
    receipt["vfx_parent_head"] = vfx_parent
    receipt["migrated_neutral_mesh_digest"] = EXPECTED_NEUTRAL_DIGEST
    receipt["duration_s"] = DURATION_S
    receipt["interval_count"] = INTERVAL_COUNT
    receipt["sample_count_endpoint_inclusive"] = SAMPLE_COUNT
    receipt["discrete_step_s"] = STEP_S
    receipt["observer_fps_cap"] = OBSERVER_FPS_CAP
    receipt["endpoint_track_phase"] = endpoint_track_phase
    receipt["endpoint_geometry_delta_m"] = endpoint_delta
    receipt["authored_phase15_to16_delta_m"] = seam_authored_delta
    receipt["loop_phase15_to0_delta_m"] = seam_loop_delta
    receipt["peak_phase0_to8_delta_m"] = peak_delta
    receipt["mutated_endpoint_delta_m"] = mutated_endpoint_delta
    receipt["wrap_count"] = wraps
    receipt["completed_cycles"] = completed_cycles
    receipt["transitions"] = transitions
    receipt["active_phase_mismatch_frames"] = active_mismatches
    receipt["process_frame_count"] = frame_count
    receipt["process_frame_interval_ms"] = {
        "min": min_frame_ms if frame_count > 0 else 0.0,
        "mean": sum_frame_ms / float(frame_count) if frame_count > 0 else 0.0,
        "max": max_frame_ms,
    }
    receipt["checks"] = checks
    receipt["truth_boundary"] = {
        "exact_vfx_source_states_reused_unchanged": true,
        "animationplayer_discrete_mesh_keys_tested": true,
        "real_repeated_playback_tested": true,
        "wall_clock_characterized_on_proof_host": true,
        "interpolated_between_state_motion_tested": false,
        "continuous_visual_smoothness_accepted": false,
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
