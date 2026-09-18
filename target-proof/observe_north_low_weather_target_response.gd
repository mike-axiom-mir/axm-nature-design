extends SceneTree

const PRE_RECEIPT := "res://generated/nature-north-low-parent-exclusion-uc-target-receipt.json"
const ORACLE := "res://generated/nature-north-low-parent-exclusion-target-oracle.json"
const RECEIVER_GLB := "res://generated/nature-north-low-parent-exclusion-receiver-rigid.glb"
const OUTPUT := "res://nature-north-low-weather-vfx-godot-target-receipt.json"
const POSITION_TOL_M := 0.000005
const LOCAL_WITNESS_TOL_M := 0.000005
const SIGN_EPS_M := 0.0000005
const WEATHER_SOURCE_XY := Vector2(1.0, 0.35)

var receipt := {
    "schema": "axm.nature-north-low-weather-vfx-godot-target/v0.1",
    "state": "NOT_RUN",
    "renderer_boundary": "Godot 4.7.2 GL Compatibility GLTFDocument import of exact Technical-Art current-UC receiver; VFX observes Weather-direction response only, not physical wind or visual-quality acceptance."
}

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

func write_receipt() -> void:
    var file := FileAccess.open(OUTPUT, FileAccess.WRITE)
    if file != null:
        file.store_string(JSON.stringify(receipt, "  ") + "\n")
        file.close()

func fail(message: String) -> void:
    receipt["state"] = "FAIL_NATURE_NORTH_LOW_WEATHER_VFX_GODOT_TARGET"
    receipt["failure"] = message
    write_receipt()
    push_error(message)
    quit(1)

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

func nearest_local_vertex(instance: MeshInstance3D, expected: Vector3) -> Dictionary:
    var mesh := instance.mesh
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
        fail("no imported vertices found for witness: " + String(instance.name))
    return {"position": best, "delta_m": best_delta}

func vec3(value) -> Vector3:
    if not (value is Array) or value.size() != 3:
        fail("invalid vector in target oracle")
        return Vector3.ZERO
    return Vector3(float(value[0]), float(value[1]), float(value[2]))

func vec3_array(value: Vector3) -> Array:
    return [value.x, value.y, value.z]

func _initialize() -> void:
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
        fail("exact current-UC rigid receiver byte identity mismatch")
        return

    var scene := imported_scene(RECEIVER_GLB)
    get_root().add_child(scene)
    await process_frame
    if not scene.is_inside_tree():
        fail("imported receiver did not enter SceneTree before VFX observation")
        return

    var north_woody_node := find_named(scene, "north-low-woody")
    var north_foliage_node := find_named(scene, "north-low-foliage")
    if north_woody_node == null or not (north_woody_node is MeshInstance3D):
        fail("missing north-low-woody target node")
        return
    if north_foliage_node == null or not (north_foliage_node is MeshInstance3D):
        fail("missing north-low-foliage target node")
        return
    var north_woody := north_woody_node as MeshInstance3D
    var north_foliage := north_foliage_node as MeshInstance3D
    if north_foliage.get_parent() != north_woody:
        fail("north-low foliage receiver parent edge drift")
        return

    var primitive_id := String(oracle.get("primitive_id", ""))
    var witness_node_raw := find_named(scene, primitive_id)
    if witness_node_raw == null or not (witness_node_raw is MeshInstance3D):
        fail("target witness primitive is absent: " + primitive_id)
        return
    var witness_node := witness_node_raw as MeshInstance3D
    var expected_local := vec3(oracle.get("witness_local_uc_m"))
    var nearest := nearest_local_vertex(witness_node, expected_local)
    var witness_local := nearest["position"] as Vector3
    var local_delta := float(nearest["delta_m"])
    if local_delta > LOCAL_WITNESS_TOL_M:
        fail("imported witness local-position drift: " + str(local_delta))
        return

    var axis := vec3(oracle.get("target_axis_uc")).normalized()
    var samples = oracle.get("samples", []) as Array
    if samples.size() != 41:
        fail("target oracle sample count drift")
        return

    var weather_parallel := Vector3(WEATHER_SOURCE_XY.x, 0.0, WEATHER_SOURCE_XY.y).normalized()
    var weather_cross := Vector3(-WEATHER_SOURCE_XY.y, 0.0, WEATHER_SOURCE_XY.x).normalized()
    var source_vertical_target := Vector3(0.0, 1.0, 0.0)

    var original_transform := north_woody.transform
    var neutral_world := Vector3.ZERO
    var neutral_expected := Vector3.ZERO
    var rows: Array = []
    var sign_violations := 0
    var maximum_position_residual := 0.0
    var maximum_parallel_residual := 0.0
    var maximum_parent_stress_abs := 0.0
    var nonzero_parent_stress_samples := 0
    var peak_downwind_parallel := -INF
    var peak_upwind_parallel := INF

    for sample_index in range(samples.size()):
        north_woody.transform = original_transform
        var sample = samples[sample_index] as Dictionary
        var child_angle_deg := float(sample.get("north_low_child_angle_deg", 9999.0))
        var target_angle_deg := float(sample.get("target_receiver_angle_deg", 9999.0))
        var parent_stress_deg := float(sample.get("upper_trunk_parent_stress_command_deg", 9999.0))
        if absf(target_angle_deg + child_angle_deg) > 0.0000001:
            fail("target angle no longer equals negated child angle")
            return

        maximum_parent_stress_abs = maxf(maximum_parent_stress_abs, absf(parent_stress_deg))
        if absf(parent_stress_deg) > 0.000001:
            nonzero_parent_stress_samples += 1

        north_woody.transform = Transform3D(Basis(Quaternion(axis, deg_to_rad(target_angle_deg))), original_transform.origin)
        var actual_world := witness_node.global_transform * witness_local
        var expected_world := vec3(sample.get("expected_witness_world_uc_m"))
        var position_residual := actual_world.distance_to(expected_world)
        maximum_position_residual = maxf(maximum_position_residual, position_residual)
        if position_residual > POSITION_TOL_M:
            fail("target witness residual exceeded tolerance at sample " + str(sample_index) + ": " + str(position_residual))
            return

        if sample_index == 0:
            neutral_world = actual_world
            neutral_expected = expected_world

        var actual_delta := actual_world - neutral_world
        var expected_delta := expected_world - neutral_expected
        var parallel_m := actual_delta.dot(weather_parallel)
        var expected_parallel_m := expected_delta.dot(weather_parallel)
        var cross_m := actual_delta.dot(weather_cross)
        var vertical_m := actual_delta.dot(source_vertical_target)
        var parallel_residual := absf(parallel_m - expected_parallel_m)
        maximum_parallel_residual = maxf(maximum_parallel_residual, parallel_residual)

        var sign_ok := true
        if child_angle_deg < -0.0000001:
            sign_ok = parallel_m > SIGN_EPS_M
            peak_downwind_parallel = maxf(peak_downwind_parallel, parallel_m)
        elif child_angle_deg > 0.0000001:
            sign_ok = parallel_m < -SIGN_EPS_M
            peak_upwind_parallel = minf(peak_upwind_parallel, parallel_m)
        else:
            sign_ok = absf(parallel_m) <= POSITION_TOL_M
        if not sign_ok:
            sign_violations += 1

        rows.append({
            "index": int(sample.get("index", sample_index)),
            "time_s": float(sample.get("time_s", sample_index / 40.0)),
            "north_low_child_angle_deg": child_angle_deg,
            "upper_trunk_parent_stress_command_deg": parent_stress_deg,
            "target_receiver_angle_deg": target_angle_deg,
            "actual_witness_world_target_m": vec3_array(actual_world),
            "expected_witness_world_target_m": vec3_array(expected_world),
            "target_position_residual_m": position_residual,
            "weather_parallel_m": parallel_m,
            "weather_parallel_expected_analytic_m": expected_parallel_m,
            "weather_parallel_residual_m": parallel_residual,
            "weather_cross_m": cross_m,
            "source_vertical_in_target_m": vertical_m,
            "weather_polarity_sign_ok": sign_ok
        })

    north_woody.transform = original_transform
    var endpoint_world := witness_node.global_transform * witness_local
    var endpoint_closure := endpoint_world.distance_to(neutral_world)
    if endpoint_closure > POSITION_TOL_M:
        fail("target endpoint did not return to neutral")
        return
    if sign_violations != 0:
        fail("one or more target-host samples violated established Weather polarity")
        return
    if maximum_parallel_residual > POSITION_TOL_M:
        fail("Weather-parallel target/analytic residual exceeded position tolerance")
        return
    if peak_downwind_parallel <= 0.001 or peak_upwind_parallel >= -0.001:
        fail("target-host Weather response did not produce material signed movement")
        return
    if maximum_parent_stress_abs < 2.49 or nonzero_parent_stress_samples <= 0:
        fail("parent stress command was not present in the exercised owner samples")
        return

    receipt["state"] = "PASS_NORTH_LOW_WEATHER_POLARITY_CURRENT_GODOT_TARGET_REVIEW"
    receipt["godot_version"] = Engine.get_version_info()
    receipt["heads"] = pre.get("heads")
    receipt["receiver_glb_sha256"] = sha256_file(RECEIVER_GLB)
    receipt["weather_source_xy"] = [WEATHER_SOURCE_XY.x, WEATHER_SOURCE_XY.y]
    receipt["weather_target_parallel_xyz"] = vec3_array(weather_parallel)
    receipt["weather_target_cross_xyz"] = vec3_array(weather_cross)
    receipt["source_vertical_target_xyz"] = vec3_array(source_vertical_target)
    receipt["samples_verified"] = samples.size()
    receipt["visible_repeat_samples"] = 40
    receipt["maximum_imported_local_witness_delta_m"] = local_delta
    receipt["maximum_target_sample_position_residual_m"] = maximum_position_residual
    receipt["maximum_weather_parallel_target_vs_analytic_residual_m"] = maximum_parallel_residual
    receipt["weather_polarity_sign_violations"] = sign_violations
    receipt["target_witness_peak_downwind_parallel_m"] = peak_downwind_parallel
    receipt["target_witness_peak_upwind_parallel_m"] = peak_upwind_parallel
    receipt["endpoint_closure_m"] = endpoint_closure
    receipt["maximum_parent_stress_command_abs_deg"] = maximum_parent_stress_abs
    receipt["nonzero_parent_stress_samples"] = nonzero_parent_stress_samples
    receipt["rows"] = rows
    receipt["truth_boundary"] = {
        "real_godot_target_host_observation": true,
        "weather_visual_direction_response_observed": true,
        "source_centroid_and_target_witness_numeric_identity_claimed": false,
        "physical_wind_speed_force_drag_or_turbulence_claimed": false,
        "botanical_or_natural_motion_quality_claimed": false,
        "runtime_controller_or_target_device_performance_claimed": false,
        "collision_gameplay_damage_or_physics_claimed": false,
        "art_direction_or_independent_visual_qa_acceptance_claimed": false,
        "canon_or_production_readiness_claimed": false
    }
    write_receipt()
    print("AXM NATURE NORTH LOW WEATHER VFX TARGET ", JSON.stringify(receipt))
    quit(0)
