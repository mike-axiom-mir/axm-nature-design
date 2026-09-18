extends SceneTree

const PRE_RECEIPT := "res://generated/nature-north-low-parent-exclusion-uc-target-receipt.json"
const ORACLE := "res://generated/nature-north-low-parent-exclusion-target-oracle.json"
const RECEIVER_GLB := "res://generated/nature-north-low-parent-exclusion-receiver-rigid.glb"
const OUTPUT := "res://nature-north-low-animationplayer-loop-receipt.json"
const BRANCH_IDS := ["south-low", "north-low", "east-mid", "west-high", "north-top"]
const POSITION_TOL_M := 0.000005
const ENDPOINT_TOL_M := 0.000005
const EXPECTED_VISIBLE_KEYS := 40

var receipt := {
    "schema": "axm.nature-animation-north-low-parent-exclusion-animationplayer-target-loop/v0.1",
    "state": "NOT_RUN",
    "boundary": "Godot 4.7.2 AnimationPlayer proof over the exact Technical-Art/UC receiver. This proves exact-key and loop-wrap target motion only; it is not Runtime/controller, device, gameplay, wind, Art/QA, CANON or production acceptance."
}

func _initialize() -> void:
    call_deferred("_run")

func read_json(path: String) -> Dictionary:
    if not FileAccess.file_exists(path):
        fail("missing JSON: " + path)
        return {}
    var parsed = JSON.parse_string(FileAccess.get_file_as_string(path))
    if typeof(parsed) != TYPE_DICTIONARY:
        fail("invalid JSON object: " + path)
        return {}
    return parsed as Dictionary

func write_receipt() -> void:
    var file := FileAccess.open(OUTPUT, FileAccess.WRITE)
    if file != null:
        file.store_string(JSON.stringify(receipt, "  ") + "\n")
        file.close()

func fail(message: String) -> void:
    receipt["state"] = "FAIL_NATURE_NORTH_LOW_ANIMATIONPLAYER_TARGET_LOOP"
    receipt["failure"] = message
    write_receipt()
    push_error(message)
    quit(1)

func sha256_file(path: String) -> String:
    var bytes := FileAccess.get_file_as_bytes(path)
    var ctx := HashingContext.new()
    ctx.start(HashingContext.HASH_SHA256)
    ctx.update(bytes)
    return ctx.finish().hex_encode()

func find_named(node: Node, wanted: String) -> Node:
    if String(node.name) == wanted:
        return node
    for child in node.get_children():
        var found := find_named(child, wanted)
        if found != null:
            return found
    return null

func imported_scene(path: String) -> Node3D:
    if not FileAccess.file_exists(path):
        fail("missing exact receiver GLB")
        return Node3D.new()
    var document := GLTFDocument.new()
    var state := GLTFState.new()
    var error := document.append_from_file(path, state)
    if error != OK:
        fail("GLTFDocument append_from_file failed: " + str(error))
        return Node3D.new()
    var generated = document.generate_scene(state)
    if generated == null or not (generated is Node3D):
        fail("GLTFDocument generate_scene returned no Node3D")
        return Node3D.new()
    return generated as Node3D

func vec3(value) -> Vector3:
    if not (value is Array) or value.size() != 3:
        fail("invalid vector in target oracle")
        return Vector3.ZERO
    return Vector3(float(value[0]), float(value[1]), float(value[2]))

func nearest_local_vertex(instance: MeshInstance3D, expected: Vector3) -> Dictionary:
    var mesh := instance.mesh
    if mesh == null:
        fail("witness MeshInstance3D has no mesh")
        return {}
    var best_delta := INF
    var best := Vector3.ZERO
    var found := false
    for surface_index in range(mesh.get_surface_count()):
        var arrays := mesh.surface_get_arrays(surface_index)
        var vertices = arrays[Mesh.ARRAY_VERTEX]
        if vertices == null:
            continue
        for vertex in vertices:
            var point := vertex as Vector3
            var delta := point.distance_to(expected)
            if delta < best_delta:
                best_delta = delta
                best = point
                found = true
    if not found:
        fail("no imported vertices found for target witness")
    return {"position": best, "delta_m": best_delta}

func target_transform(base_transform: Transform3D, axis: Vector3, angle_deg: float) -> Transform3D:
    return Transform3D(Basis(Quaternion(axis, deg_to_rad(angle_deg))), base_transform.origin)

func build_player(host: Node, north_woody: MeshInstance3D, base_transform: Transform3D, axis: Vector3, samples: Array, apply_parent_stress: bool, disable_loop: bool) -> Dictionary:
    var player := AnimationPlayer.new()
    player.name = "AnimationPlayer"
    host.add_child(player)
    player.root_node = NodePath("..")

    var clip := Animation.new()
    clip.length = 1.0
    clip.loop_mode = Animation.LOOP_NONE if disable_loop else Animation.LOOP_LINEAR
    var track := clip.add_track(Animation.TYPE_VALUE)
    var node_path := host.get_path_to(north_woody)
    clip.track_set_path(track, NodePath(String(node_path) + ":transform"))
    clip.track_set_interpolation_type(track, Animation.INTERPOLATION_NEAREST)
    clip.value_track_set_update_mode(track, Animation.UPDATE_DISCRETE)

    for index in range(EXPECTED_VISIBLE_KEYS):
        var sample := samples[index] as Dictionary
        var target_angle := float(sample.get("target_receiver_angle_deg", 9999.0))
        if apply_parent_stress:
            target_angle -= float(sample.get("upper_trunk_parent_stress_command_deg", 0.0))
        clip.track_insert_key(track, float(index) / 40.0, target_transform(base_transform, axis, target_angle))

    var library := AnimationLibrary.new()
    library.add_animation("north_low_parent_exclusion_loop", clip)
    player.add_animation_library("", library)
    return {"player": player, "clip": clip, "track": track}

func _run() -> void:
    var pre := read_json(PRE_RECEIPT)
    var oracle := read_json(ORACLE)
    if pre.get("result") != "PASS_NATURE_NORTH_LOW_PARENT_EXCLUSION_CURRENT_UC_TARGET_RECEIVER_READY":
        fail("pre-target Technical Art receipt missing or not green")
        return
    if oracle.get("schema") != "axm.nature-north-low-parent-exclusion-target-oracle/v0.1":
        fail("target oracle missing or wrong schema")
        return
    if String(oracle.get("branch_id", "")) != "north-low":
        fail("target oracle branch identity drift")
        return

    var receiver = pre.get("receiver", {}) as Dictionary
    if sha256_file(RECEIVER_GLB) != String(receiver.get("rigid_glb_sha256", "")):
        fail("exact Technical-Art receiver GLB identity mismatch")
        return

    var samples = oracle.get("samples", []) as Array
    if samples.size() != 41:
        fail("endpoint-inclusive owner sample count drift")
        return
    if vec3((samples[0] as Dictionary).get("expected_witness_world_uc_m")).distance_to(vec3((samples[40] as Dictionary).get("expected_witness_world_uc_m"))) > 1e-9:
        fail("owner endpoint sample 40 no longer closes exactly to sample 0")
        return

    var host := Node3D.new()
    host.name = "AnimationLoopHost"
    get_root().add_child(host)
    var scene := imported_scene(RECEIVER_GLB)
    scene.name = "Receiver"
    host.add_child(scene)
    await process_frame

    var nodes := {}
    for branch_id in BRANCH_IDS:
        var woody_name := branch_id + "-woody"
        var foliage_name := branch_id + "-foliage"
        var woody := find_named(scene, woody_name)
        var foliage := find_named(scene, foliage_name)
        if woody == null or not (woody is MeshInstance3D):
            fail("missing imported receiver node: " + woody_name)
            return
        if foliage == null or not (foliage is MeshInstance3D):
            fail("missing imported receiver node: " + foliage_name)
            return
        nodes[woody_name] = woody
        nodes[foliage_name] = foliage
    if (nodes["north-low-foliage"] as MeshInstance3D).get_parent() != (nodes["north-low-woody"] as MeshInstance3D):
        fail("north-low foliage parent edge drift")
        return

    var north_woody := nodes["north-low-woody"] as MeshInstance3D
    var primitive_id := String(oracle.get("primitive_id", ""))
    if not nodes.has(primitive_id):
        fail("target witness primitive is absent: " + primitive_id)
        return
    var witness_node := nodes[primitive_id] as MeshInstance3D
    var nearest := nearest_local_vertex(witness_node, vec3(oracle.get("witness_local_uc_m")))
    var witness_local := nearest.get("position", Vector3.ZERO) as Vector3
    var local_delta := float(nearest.get("delta_m", INF))
    if local_delta > POSITION_TOL_M:
        fail("imported witness local-position drift: " + str(local_delta))
        return

    var original_transforms := {}
    for branch_id in BRANCH_IDS:
        original_transforms[branch_id] = (nodes[branch_id + "-woody"] as MeshInstance3D).transform
    var base_transform := original_transforms["north-low"] as Transform3D
    var axis := vec3(oracle.get("target_axis_uc")).normalized()

    var apply_parent_stress := OS.get_environment("AXM_APPLY_PARENT_STRESS_AS_CHILD") == "1"
    var disable_loop := OS.get_environment("AXM_DISABLE_ANIMATION_LOOP") == "1"
    receipt["negative_modes"] = {
        "apply_parent_stress_as_child": apply_parent_stress,
        "disable_animation_loop": disable_loop
    }

    var built := build_player(host, north_woody, base_transform, axis, samples, apply_parent_stress, disable_loop)
    var player := built["player"] as AnimationPlayer
    var clip := built["clip"] as Animation
    var track := int(built["track"])
    if clip.track_get_key_count(track) != EXPECTED_VISIBLE_KEYS:
        fail("AnimationPlayer visible-key count drift")
        return
    if clip.track_get_interpolation_type(track) != Animation.INTERPOLATION_NEAREST:
        fail("AnimationPlayer interpolation mode drift")
        return
    if clip.value_track_get_update_mode(track) != Animation.UPDATE_DISCRETE:
        fail("AnimationPlayer update mode drift")
        return

    player.play("north_low_parent_exclusion_loop")
    var maximum_residual := 0.0
    var maximum_motion := 0.0
    var neutral_world := Vector3.ZERO
    var maximum_parent_stress_abs := 0.0
    var nonzero_parent_stress_samples := 0
    var samples_verified := 0

    for index in range(EXPECTED_VISIBLE_KEYS):
        player.seek(float(index) / 40.0, true)
        player.advance(0.0)
        var sample := samples[index] as Dictionary
        var actual_world := witness_node.global_transform * witness_local
        var expected_world := vec3(sample.get("expected_witness_world_uc_m"))
        var residual := actual_world.distance_to(expected_world)
        maximum_residual = maxf(maximum_residual, residual)
        if residual > POSITION_TOL_M:
            receipt["failing_sample_index"] = index
            receipt["maximum_target_witness_residual_m"] = maximum_residual
            fail("AnimationPlayer target witness residual exceeded tolerance at sample " + str(index) + ": " + str(residual))
            return
        if index == 0:
            neutral_world = actual_world
        else:
            maximum_motion = maxf(maximum_motion, actual_world.distance_to(neutral_world))
        var parent_stress := absf(float(sample.get("upper_trunk_parent_stress_command_deg", 0.0)))
        maximum_parent_stress_abs = maxf(maximum_parent_stress_abs, parent_stress)
        if parent_stress > 0.000001:
            nonzero_parent_stress_samples += 1
        for other_id in BRANCH_IDS:
            if other_id == "north-low":
                continue
            var other := nodes[other_id + "-woody"] as MeshInstance3D
            if not other.transform.is_equal_approx(original_transforms[other_id] as Transform3D):
                fail("AnimationPlayer moved unrelated branch: " + other_id)
                return
        samples_verified += 1

    if maximum_motion <= 0.001:
        fail("AnimationPlayer witness did not move materially")
        return
    if maximum_parent_stress_abs < 2.49 or nonzero_parent_stress_samples <= 0:
        fail("owner parent-stress command was not present in sampled semantics")
        return

    player.seek(39.0 / 40.0, true)
    player.advance(0.0)
    var before_wrap := witness_node.global_transform * witness_local
    player.advance(1.0 / 40.0)
    var after_wrap := witness_node.global_transform * witness_local
    var expected_wrap_world := vec3((samples[40] as Dictionary).get("expected_witness_world_uc_m"))
    var wrap_target_residual := after_wrap.distance_to(expected_wrap_world)
    var actual_wrap_step := before_wrap.distance_to(after_wrap)
    var expected_wrap_step := vec3((samples[39] as Dictionary).get("expected_witness_world_uc_m")).distance_to(expected_wrap_world)
    var wrap_step_residual := absf(actual_wrap_step - expected_wrap_step)
    if wrap_target_residual > ENDPOINT_TOL_M:
        receipt["loop_wrap_target_residual_m"] = wrap_target_residual
        fail("AnimationPlayer visible-repeat wrap did not return to owner endpoint/sample-zero state")
        return
    if wrap_step_residual > ENDPOINT_TOL_M:
        receipt["loop_wrap_transition_step_residual_m"] = wrap_step_residual
        fail("AnimationPlayer wrap transition no longer matches the authored final adjacent step")
        return

    receipt["state"] = "PASS_NATURE_NORTH_LOW_PARENT_EXCLUSION_ANIMATIONPLAYER_TARGET_LOOP"
    receipt["godot_version"] = Engine.get_version_info()
    receipt["heads"] = pre.get("heads")
    receipt["receiver_glb_sha256"] = sha256_file(RECEIVER_GLB)
    receipt["animationplayer"] = {
        "clip": "north_low_parent_exclusion_loop",
        "length_s": clip.length,
        "loop_mode": clip.loop_mode,
        "track_count": clip.get_track_count(),
        "visible_key_count": clip.track_get_key_count(track),
        "interpolation": "NEAREST",
        "update_mode": "DISCRETE",
        "samples_verified": samples_verified
    }
    receipt["maximum_imported_local_witness_delta_m"] = local_delta
    receipt["maximum_target_witness_residual_m"] = maximum_residual
    receipt["maximum_witness_motion_from_neutral_m"] = maximum_motion
    receipt["maximum_parent_stress_command_abs_deg"] = maximum_parent_stress_abs
    receipt["nonzero_parent_stress_samples"] = nonzero_parent_stress_samples
    receipt["loop_wrap_target_residual_m"] = wrap_target_residual
    receipt["actual_last_visible_to_repeat_step_m"] = actual_wrap_step
    receipt["expected_owner_last_visible_to_endpoint_step_m"] = expected_wrap_step
    receipt["loop_wrap_transition_step_residual_m"] = wrap_step_residual
    receipt["truth_boundary"] = {
        "exact_current_ta_uc_receiver_imported": true,
        "exact_frozen_animation_owner_samples_consumed": true,
        "animationplayer_exact_key_playback_proven": true,
        "animationplayer_visible_repeat_wrap_transition_proven": true,
        "parent_stress_command_applied_as_receiver_motion": false,
        "wall_clock_40hz_delivery_proven": false,
        "runtime_controller_or_target_device_proven": false,
        "connected_attachment_or_production_skinning_proven": false,
        "wind_or_vfx_behavior_proven": false,
        "collision_gameplay_or_physics_proven": false,
        "art_or_visual_qa_acceptance_proven": false,
        "canon_or_production_readiness_proven": false
    }
    write_receipt()
    print("AXM NATURE NORTH LOW ANIMATIONPLAYER LOOP ", JSON.stringify(receipt))
    quit(0)
