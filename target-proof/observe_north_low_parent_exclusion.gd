extends SceneTree

const PRE_RECEIPT := "res://generated/nature-north-low-parent-exclusion-uc-target-receipt.json"
const ORACLE := "res://generated/nature-north-low-parent-exclusion-target-oracle.json"
const RECEIVER_GLB := "res://generated/nature-north-low-parent-exclusion-receiver-rigid.glb"
const OUTPUT := "res://nature-north-low-parent-exclusion-godot-target-receipt.json"
const BRANCH_IDS := ["south-low", "north-low", "east-mid", "west-high", "north-top"]
const POSITION_TOL_M := 0.000005
const LOCAL_WITNESS_TOL_M := 0.000005

var receipt := {
    "schema": "axm.nature-north-low-parent-exclusion-godot-target/v0.1",
    "state": "NOT_RUN",
    "renderer_boundary": "Godot 4.7.2 GL Compatibility GLTFDocument import of exact current-UC rigid receiver; direct imported-array and transform observation, no visual-quality claim."
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
    receipt["state"] = "FAIL_NATURE_NORTH_LOW_PARENT_EXCLUSION_GODOT_TARGET"
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

func array_triangle_count(instance: MeshInstance3D) -> int:
    var mesh := instance.mesh
    if mesh == null:
        fail("MeshInstance3D has no mesh: " + String(instance.name))
        return 0
    var total := 0
    for surface_index in range(mesh.get_surface_count()):
        if mesh.surface_get_primitive_type(surface_index) != Mesh.PRIMITIVE_TRIANGLES:
            fail("non-triangle imported surface: " + String(instance.name))
            return 0
        var arrays := mesh.surface_get_arrays(surface_index)
        var indices = arrays[Mesh.ARRAY_INDEX]
        var vertices = arrays[Mesh.ARRAY_VERTEX]
        if indices != null and indices.size() > 0:
            if indices.size() % 3 != 0:
                fail("imported index count is not divisible by three")
                return 0
            total += int(indices.size() / 3)
        else:
            if vertices == null or vertices.size() % 3 != 0:
                fail("unindexed triangle surface has invalid vertex count")
                return 0
            total += int(vertices.size() / 3)
    return total

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
        fail("imported receiver did not enter SceneTree before observation")
        return

    var expected_names := ["static-woody", "static-foliage"]
    for branch_id in BRANCH_IDS:
        expected_names.append(branch_id + "-woody")
        expected_names.append(branch_id + "-foliage")

    var nodes := {}
    var total_triangles := 0
    for node_name in expected_names:
        var node := find_named(scene, node_name)
        if node == null or not (node is MeshInstance3D):
            fail("missing imported receiver mesh node: " + node_name)
            return
        nodes[node_name] = node
        total_triangles += array_triangle_count(node as MeshInstance3D)
    if total_triangles != int(receiver.get("emitted_triangles", -1)):
        fail("target-host receiver triangle count drift")
        return

    var north_woody := nodes["north-low-woody"] as MeshInstance3D
    var north_foliage := nodes["north-low-foliage"] as MeshInstance3D
    if north_foliage.get_parent() != north_woody:
        fail("north-low foliage is not parented under north-low woody receiver")
        return

    var original_transforms := {}
    for branch_id in BRANCH_IDS:
        var branch_root := nodes[branch_id + "-woody"] as MeshInstance3D
        original_transforms[branch_id] = branch_root.transform

    var primitive_id := String(oracle.get("primitive_id", ""))
    if not nodes.has(primitive_id):
        fail("target witness primitive is absent: " + primitive_id)
        return
    var witness_node := nodes[primitive_id] as MeshInstance3D
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

    var maximum_residual := 0.0
    var maximum_motion := 0.0
    var maximum_parent_stress_abs := 0.0
    var neutral_world := Vector3.ZERO
    var nonzero_parent_stress_samples := 0

    for sample_index in range(samples.size()):
        for reset_id in BRANCH_IDS:
            var reset_node := nodes[reset_id + "-woody"] as MeshInstance3D
            reset_node.transform = original_transforms[reset_id]

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

        var base_transform = original_transforms["north-low"] as Transform3D
        north_woody.transform = Transform3D(Basis(Quaternion(axis, deg_to_rad(target_angle_deg))), base_transform.origin)

        for other_id in BRANCH_IDS:
            if other_id == "north-low":
                continue
            var other_node := nodes[other_id + "-woody"] as MeshInstance3D
            if not other_node.transform.is_equal_approx(original_transforms[other_id]):
                fail("north-low target playback moved unrelated branch: " + other_id)
                return

        var actual_world := witness_node.global_transform * witness_local
        var expected_world := vec3(sample.get("expected_witness_world_uc_m"))
        var residual := actual_world.distance_to(expected_world)
        maximum_residual = maxf(maximum_residual, residual)
        if residual > POSITION_TOL_M:
            fail("target sample transport residual exceeded tolerance at sample " + str(sample_index) + ": " + str(residual))
            return
        if sample_index == 0:
            neutral_world = actual_world
        else:
            maximum_motion = maxf(maximum_motion, actual_world.distance_to(neutral_world))

    north_woody.transform = original_transforms["north-low"]
    var endpoint_actual := witness_node.global_transform * witness_local
    if endpoint_actual.distance_to(neutral_world) > POSITION_TOL_M:
        fail("target endpoint did not return to neutral")
        return
    if maximum_motion <= 0.001:
        fail("north-low target witness did not move materially")
        return
    if maximum_parent_stress_abs < 2.49 or nonzero_parent_stress_samples <= 0:
        fail("parent stress command was not actually present in the exercised Animation samples")
        return
    if float(oracle.get("maximum_forbidden_parent_command_as_child_rotation_residual_m", 0.0)) <= 0.001:
        fail("parent-command leak negative is not discriminating")
        return

    receipt["state"] = "PASS_NATURE_NORTH_LOW_PARENT_EXCLUSION_CURRENT_UC_GODOT_TARGET"
    receipt["godot_version"] = Engine.get_version_info()
    receipt["heads"] = pre.get("heads")
    receipt["receiver_glb_sha256"] = sha256_file(RECEIVER_GLB)
    receipt["receiver_triangles"] = total_triangles
    receipt["receiver_nodes_verified"] = expected_names.size()
    receipt["north_low_parent_edge_verified"] = true
    receipt["samples_verified"] = samples.size()
    receipt["visible_repeat_samples"] = 40
    receipt["maximum_imported_local_witness_delta_m"] = local_delta
    receipt["maximum_target_sample_position_residual_m"] = maximum_residual
    receipt["maximum_witness_motion_from_neutral_m"] = maximum_motion
    receipt["maximum_parent_stress_command_abs_deg"] = maximum_parent_stress_abs
    receipt["nonzero_parent_stress_samples"] = nonzero_parent_stress_samples
    receipt["forbidden_parent_command_as_child_rotation_max_residual_m"] = oracle.get("maximum_forbidden_parent_command_as_child_rotation_residual_m")
    receipt["position_tolerance_m"] = POSITION_TOL_M
    receipt["truth_boundary"] = {
        "exact_current_uc_receiver_imported": true,
        "exact_current_animation_samples_exercised": true,
        "detached_child_target_transport_proven": true,
        "parent_stress_command_applied_as_receiver_motion": false,
        "upper_trunk_deformation_receiver_proven": false,
        "connected_attachment_or_production_skinning_proven": false,
        "wind_or_vfx_behavior_proven": false,
        "runtime_controller_or_target_device_proven": false,
        "collision_gameplay_or_physics_proven": false,
        "art_or_visual_qa_acceptance_proven": false,
        "uc_inferred_nature_semantics": false,
        "canon_or_production_readiness_proven": false
    }
    write_receipt()
    print("AXM NATURE NORTH LOW PARENT EXCLUSION TARGET ", JSON.stringify(receipt))
    quit(0)
