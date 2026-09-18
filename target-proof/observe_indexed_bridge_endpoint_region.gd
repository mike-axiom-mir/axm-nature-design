extends SceneTree

const PRE_RECEIPT := "res://generated/nature-north-low-indexed-bridge-uc-target-receipt.json"
const ORACLE := "res://generated/nature-north-low-indexed-bridge-target-oracle.json"
const RECEIVER_GLB := "res://generated/nature-north-low-indexed-bridge.glb"
const OUTPUT := "res://nature-north-low-indexed-bridge-godot-target-receipt.json"
const IMPORT_OBSERVATION_TOL_M := 0.0001
const EXPECTED_VERTICES := 16
const EXPECTED_TRIANGLES := 16
const EXPECTED_MOVING_END := 8

var receipt := {
    "schema": "axm.nature-north-low-indexed-bridge-godot-target/v0.1",
    "state": "NOT_RUN",
    "renderer_boundary": "Godot 4.7.2 GL Compatibility; exact current-UC GLB import, one dynamic ArrayMesh receiver, host-normalized full control versus first-eight-vertex partial update."
}
var camera := Camera3D.new()
var environment := Environment.new()
var instance := MeshInstance3D.new()
var proof_material := StandardMaterial3D.new()

func read_json(path: String) -> Dictionary:
    if not FileAccess.file_exists(path):
        return {}
    var parsed = JSON.parse_string(FileAccess.get_file_as_string(path))
    return parsed as Dictionary if parsed is Dictionary else {}

func write_receipt() -> void:
    var file := FileAccess.open(OUTPUT, FileAccess.WRITE)
    if file != null:
        file.store_string(JSON.stringify(receipt, "  ") + "\n")
        file.close()

func fail(message: String) -> void:
    receipt["state"] = "FAIL_NATURE_NORTH_LOW_INDEXED_BRIDGE_GODOT_TARGET"
    receipt["failure"] = message
    write_receipt()
    push_error(message)
    quit(1)

func vec3(row) -> Vector3:
    if not (row is Array) or row.size() != 3:
        fail("invalid target vector")
        return Vector3.ZERO
    return Vector3(float(row[0]), float(row[1]), float(row[2]))

func packed_positions(rows) -> PackedVector3Array:
    if not (rows is Array):
        fail("target position packet is not an array")
        return PackedVector3Array()
    var out := PackedVector3Array()
    out.resize(rows.size())
    for i in range(rows.size()):
        out[i] = vec3(rows[i])
    return out

func find_mesh(node: Node) -> MeshInstance3D:
    if node is MeshInstance3D:
        return node as MeshInstance3D
    for child in node.get_children():
        var found := find_mesh(child)
        if found != null:
            return found
    return null

func import_receiver() -> MeshInstance3D:
    if not FileAccess.file_exists(RECEIVER_GLB):
        fail("missing exact current-UC indexed bridge GLB")
        return null
    var document := GLTFDocument.new()
    var state := GLTFState.new()
    var error := document.append_from_file(RECEIVER_GLB, state)
    if error != OK:
        fail("GLTFDocument append_from_file failed: " + str(error))
        return null
    var scene = document.generate_scene(state)
    if scene == null:
        fail("GLTFDocument generate_scene returned null")
        return null
    var mesh_instance := find_mesh(scene)
    if mesh_instance == null:
        fail("current-UC receiver import contains no MeshInstance3D")
        return null
    return mesh_instance

func make_dynamic_mesh(neutral_arrays: Array) -> ArrayMesh:
    var mesh := ArrayMesh.new()
    mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, neutral_arrays, [], {}, Mesh.ARRAY_FLAG_USE_DYNAMIC_UPDATE)
    return mesh

func settle() -> void:
    await process_frame
    await RenderingServer.frame_post_draw

func capture_image() -> Image:
    await settle()
    var image := root.get_texture().get_image()
    if image == null or image.is_empty():
        fail("target renderer returned no image")
        return Image.new()
    image.convert(Image.FORMAT_RGB8)
    return image

func image_delta(a: Image, b: Image) -> Dictionary:
    if a.get_width() != b.get_width() or a.get_height() != b.get_height():
        fail("render dimensions differ")
        return {}
    var left := a.get_data()
    var right := b.get_data()
    if left.size() != right.size() or left.size() % 3 != 0:
        fail("RGB8 byte layout drift")
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
    return {"changed_pixels": changed_pixels, "total_pixels": int(left.size() / 3), "max_channel_delta": max_channel_delta, "byte_identical": changed_pixels == 0}

func position_delta_stats(actual: PackedVector3Array, expected_rows) -> Dictionary:
    if not (expected_rows is Array) or actual.size() != expected_rows.size():
        fail("position-array count mismatch")
        return {}
    var maximum_distance := 0.0
    var maximum_component := 0.0
    var changed_vertices := 0
    for i in range(actual.size()):
        var expected := vec3(expected_rows[i])
        var distance := actual[i].distance_to(expected)
        maximum_distance = maxf(maximum_distance, distance)
        maximum_component = maxf(maximum_component, absf(actual[i].x - expected.x))
        maximum_component = maxf(maximum_component, absf(actual[i].y - expected.y))
        maximum_component = maxf(maximum_component, absf(actual[i].z - expected.z))
        if distance > 0.0:
            changed_vertices += 1
    return {"maximum_distance_m": maximum_distance, "maximum_component_delta_m": maximum_component, "changed_vertices": changed_vertices, "vertex_count": actual.size()}

func minimum_pair_span(rows: PackedVector3Array) -> float:
    if rows.size() != EXPECTED_VERTICES:
        fail("pair-span receiver cardinality drift")
        return 0.0
    var minimum := INF
    for i in range(EXPECTED_MOVING_END):
        minimum = minf(minimum, rows[i].distance_to(rows[EXPECTED_MOVING_END + i]))
    return minimum

func configure_scene(neutral_vertices: PackedVector3Array) -> void:
    root.size = Vector2i(900, 700)
    DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
    var minimum := Vector3(INF, INF, INF)
    var maximum := Vector3(-INF, -INF, -INF)
    for vertex in neutral_vertices:
        minimum = minimum.min(vertex)
        maximum = maximum.max(vertex)
    var center := (minimum + maximum) * 0.5
    var radius := maxf((maximum - minimum).length() * 0.5, 0.01)
    camera.projection = Camera3D.PROJECTION_ORTHOGONAL
    camera.size = radius * 2.7
    camera.near = maxf(radius * 0.001, 0.00001)
    camera.far = radius * 30.0
    camera.position = center + Vector3(1.3, 1.1, 1.7).normalized() * radius * 4.0
    root.add_child(camera)
    camera.look_at(center)
    camera.current = true
    environment.background_mode = Environment.BG_COLOR
    environment.background_color = Color(0.035, 0.045, 0.06)
    environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
    environment.ambient_light_color = Color(0.72, 0.76, 0.82)
    environment.ambient_light_energy = 0.8
    var world := WorldEnvironment.new()
    world.environment = environment
    root.add_child(world)
    var light := DirectionalLight3D.new()
    light.rotation_degrees = Vector3(-42, -32, 0)
    light.light_energy = 1.2
    root.add_child(light)
    proof_material.albedo_color = Color(0.45, 0.58, 0.36)
    proof_material.metallic = 0.0
    proof_material.roughness = 0.82
    proof_material.cull_mode = BaseMaterial3D.CULL_DISABLED
    instance.material_override = proof_material
    root.add_child(instance)

func _run() -> void:
    var pre := read_json(PRE_RECEIPT)
    var oracle := read_json(ORACLE)
    if pre.get("result") != "PASS_NATURE_NORTH_LOW_INDEXED_BRIDGE_CURRENT_UC_TARGET_RECEIVER_READY":
        fail("pre-target Technical Art receipt missing or not green")
        return
    if oracle.get("schema") != "axm.nature-north-low-indexed-bridge-godot-oracle/v0.1":
        fail("target oracle missing or wrong schema")
        return
    if FileAccess.get_sha256(RECEIVER_GLB) != String(oracle.get("receiver_glb_sha256", "")):
        fail("exact current-UC GLB byte identity mismatch")
        return
    if int(oracle.get("vertex_count", -1)) != EXPECTED_VERTICES or int(oracle.get("triangle_count", -1)) != EXPECTED_TRIANGLES:
        fail("target oracle cardinality drift")
        return
    var moving = oracle.get("moving_vertex_region", [])
    var fixed = oracle.get("fixed_vertex_region", [])
    if moving != [0, EXPECTED_MOVING_END] or fixed != [EXPECTED_MOVING_END, EXPECTED_VERTICES]:
        fail("target endpoint region identity drift")
        return

    var imported := import_receiver()
    if imported == null or imported.mesh == null:
        return
    if imported.mesh.get_surface_count() != 1:
        fail("current-UC indexed bridge must import as one surface")
        return
    var arrays := imported.mesh.surface_get_arrays(0)
    var neutral_vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
    var indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX]
    if neutral_vertices.size() != EXPECTED_VERTICES or indices.size() != EXPECTED_TRIANGLES * 3:
        fail("Godot import did not preserve indexed bridge cardinality")
        return

    var neutral_pose := {}
    for pose in oracle.get("poses", []):
        if absf(float(pose.get("child_angle_deg", 999.0))) <= 0.000001:
            neutral_pose = pose
            break
    if neutral_pose.is_empty():
        fail("target oracle has no neutral pose")
        return
    var imported_neutral_stats := position_delta_stats(neutral_vertices, neutral_pose.get("control_target_positions_m"))
    if float(imported_neutral_stats.get("maximum_distance_m", INF)) > IMPORT_OBSERVATION_TOL_M:
        receipt["imported_neutral_position_observation"] = imported_neutral_stats
        fail("Godot imported neutral positions exceed bounded observation envelope")
        return

    configure_scene(neutral_vertices)
    var receiver_mesh := make_dynamic_mesh(arrays)
    instance.mesh = receiver_mesh
    var neutral_image := await capture_image()
    neutral_image.save_png("res://generated/neutral.png")

    var stride := int(oracle.get("position_stride_bytes", -1))
    var moving_offset := int(oracle.get("moving_byte_offset", -1))
    var moving_length := int(oracle.get("moving_byte_length", -1))
    var full_length := int(oracle.get("full_position_bytes", -1))
    if stride != 12 or moving_offset != 0 or moving_length != EXPECTED_MOVING_END * stride or full_length != EXPECTED_VERTICES * stride:
        fail("target byte-region contract drift")
        return
    var neutral_bytes := neutral_vertices.to_byte_array()
    if neutral_bytes.size() != full_length:
        fail("Godot imported neutral position byte serialization drift")
        return

    var rows := []
    var discriminating_pose_count := 0
    var minimum_observed_span := INF
    for pose in oracle.get("poses", []):
        var angle := float(pose.get("child_angle_deg", 999.0))
        var oracle_full := packed_positions(pose.get("control_target_positions_m"))
        var moving_positions := packed_positions(pose.get("moving_target_positions_m"))
        if oracle_full.size() != EXPECTED_VERTICES or moving_positions.size() != EXPECTED_MOVING_END:
            fail("target pose packet count drift")
            return

        var target_control_positions := neutral_vertices.duplicate()
        for i in range(EXPECTED_MOVING_END):
            target_control_positions[i] = moving_positions[i]
        var observation := position_delta_stats(target_control_positions, pose.get("control_target_positions_m"))
        if float(observation.get("maximum_distance_m", INF)) > IMPORT_OBSERVATION_TOL_M:
            fail("host-normalized control exceeds bounded owner observation at angle " + str(angle))
            return
        var span := minimum_pair_span(target_control_positions)
        minimum_observed_span = minf(minimum_observed_span, span)
        if span <= 0.009:
            fail("target-host indexed bridge paired span lost owner safety separation")
            return

        var full_bytes := target_control_positions.to_byte_array()
        var moving_bytes := moving_positions.to_byte_array()
        if full_bytes.size() != full_length or moving_bytes.size() != moving_length:
            fail("Godot endpoint packet byte serialization drift")
            return

        receiver_mesh.surface_update_vertex_region(0, 0, full_bytes)
        var control_image := await capture_image()
        receiver_mesh.surface_update_vertex_region(0, 0, neutral_bytes)
        receiver_mesh.surface_update_vertex_region(0, moving_offset, moving_bytes)
        var candidate_image := await capture_image()
        var pair := image_delta(control_image, candidate_image)
        if not bool(pair.get("byte_identical", false)):
            fail("partial endpoint update diverged from host-normalized full control at angle " + str(angle) + ": " + str(pair))
            return
        var neutral_delta := image_delta(neutral_image, candidate_image)
        if absf(angle) > 0.001 and int(neutral_delta.get("changed_pixels", 0)) > 10:
            discriminating_pose_count += 1

        var tag := ("m" if angle < 0.0 else "p") + str(absf(angle)).replace(".", "_")
        if absf(angle) < 0.000001:
            tag = "zero"
        control_image.save_png("res://generated/control-" + tag + ".png")
        candidate_image.save_png("res://generated/candidate-" + tag + ".png")
        rows.append({
            "child_angle_deg": angle,
            "full_update_bytes": full_bytes.size(),
            "partial_update_offset_bytes": moving_offset,
            "partial_update_bytes": moving_bytes.size(),
            "target_control_vs_owner_observation": observation,
            "target_minimum_paired_span_m": span,
            "owner_minimum_paired_span_m": float(pose.get("owner_minimum_paired_span_m", 0.0)),
            "control_candidate_render_delta": pair,
            "candidate_vs_neutral_render_delta": neutral_delta
        })

    if rows.size() != 5 or discriminating_pose_count < 4:
        fail("target receiver lacks the complete discriminating five-pose Rigging witness family")
        return

    receipt["state"] = "PASS_NATURE_NORTH_LOW_INDEXED_BRIDGE_CURRENT_UC_GODOT_ENDPOINT_REGION_TRANSPORT"
    receipt["godot_version"] = Engine.get_version_info()
    receipt["rendering_method"] = RenderingServer.get_current_rendering_method()
    receipt["display_server"] = DisplayServer.get_name()
    receipt["receiver_glb_sha256"] = FileAccess.get_sha256(RECEIVER_GLB)
    receipt["imported_vertices"] = neutral_vertices.size()
    receipt["imported_triangles"] = int(indices.size() / 3)
    receipt["imported_neutral_position_observation"] = imported_neutral_stats
    receipt["import_observation_tolerance_m"] = IMPORT_OBSERVATION_TOL_M
    receipt["target_update_api"] = "ArrayMesh.surface_update_vertex_region"
    receipt["dynamic_update_flag"] = "Mesh.ARRAY_FLAG_USE_DYNAMIC_UPDATE"
    receipt["moving_vertex_region"] = [0, EXPECTED_MOVING_END]
    receipt["fixed_vertex_region"] = [EXPECTED_MOVING_END, EXPECTED_VERTICES]
    receipt["moving_byte_offset"] = moving_offset
    receipt["moving_byte_length"] = moving_length
    receipt["full_position_byte_length"] = full_length
    receipt["minimum_target_host_paired_span_m"] = minimum_observed_span
    receipt["driver_rows"] = rows
    receipt["truth_boundary"] = {
        "exact_current_uc_glb_imported": true,
        "godot_import_exact_source_numeric_identity_proven": false,
        "godot_import_numeric_observation_bounded_only": true,
        "full_control_uses_imported_target_baseline_for_fixed_endpoints": true,
        "target_endpoint_region_correspondence_proven_operationally_by_full_vs_partial_render_identity": true,
        "real_target_host_partial_endpoint_region_update_exercised": true,
        "five_representative_rigging_poses_exercised": true,
        "animation_timing_or_playback_proven": false,
        "indexed_cut_or_connected_topology_proven": false,
        "continuous_triangle_foldover_collision_proven": false,
        "production_skinning_proven": false,
        "runtime_controller_device_or_performance_proven": false,
        "final_nature_normals_materials_or_visual_acceptance_proven": false,
        "uc_inferred_nature_geometry_or_rigging_semantics": false,
        "canon_or_production_readiness_proven": false
    }
    write_receipt()
    print("AXM NATURE INDEXED BRIDGE TARGET ", JSON.stringify(receipt))
    quit(0)

func _initialize() -> void:
    _run.call_deferred()
