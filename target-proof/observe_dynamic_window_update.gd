extends SceneTree

const PRE_RECEIPT := "res://generated/nature-east-rear-dynamic-window-uc-target-receipt.json"
const ORACLE := "res://generated/nature-east-rear-dynamic-window-target-oracle.json"
const RECEIVER_GLB := "res://generated/nature-east-rear-dynamic-window.glb"
const OUTPUT := "res://nature-east-rear-dynamic-window-godot-target-receipt.json"
const POSITION_TOL_M := 0.000005
const EXPECTED_VERTICES := 390
const EXPECTED_WINDOW_START := 110
const EXPECTED_WINDOW_END := 370

var receipt := {
    "schema": "axm.nature-east-rear-dynamic-window-godot-target/v0.1",
    "state": "NOT_RUN",
    "renderer_boundary": "Godot 4.7.2 GL Compatibility; exact current-UC GLB import, then target-host ArrayMesh dynamic receiver rebuilt from imported arrays and exercised with full versus partial position-buffer updates."
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
    receipt["state"] = "FAIL_NATURE_EAST_REAR_DYNAMIC_WINDOW_GODOT_TARGET"
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
        fail("missing exact current-UC receiver GLB")
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
    mesh.add_surface_from_arrays(
        Mesh.PRIMITIVE_TRIANGLES,
        neutral_arrays,
        [],
        {},
        Mesh.ARRAY_FLAG_USE_DYNAMIC_UPDATE
    )
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
        fail("rendered image dimensions differ")
        return {}
    var left := a.get_data()
    var right := b.get_data()
    if left.size() != right.size() or left.size() % 3 != 0:
        fail("rendered RGB8 byte layout drift")
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

func max_position_delta(actual: PackedVector3Array, expected_rows) -> float:
    if not (expected_rows is Array) or actual.size() != expected_rows.size():
        fail("position-array count mismatch")
        return INF
    var maximum := 0.0
    for i in range(actual.size()):
        maximum = maxf(maximum, actual[i].distance_to(vec3(expected_rows[i])))
    return maximum

func configure_scene(neutral_vertices: PackedVector3Array) -> void:
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
    camera.look_at(center)
    camera.current = true
    root.add_child(camera)

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

func _run() -> void:
    var pre := read_json(PRE_RECEIPT)
    var oracle := read_json(ORACLE)
    if pre.get("result") != "PASS_NATURE_EAST_REAR_RUNTIME_WINDOW_CURRENT_UC_TARGET_RECEIVER_READY":
        fail("pre-target Technical Art receipt missing or not green")
        return
    if oracle.get("schema") != "axm.nature-east-rear-dynamic-window-godot-oracle/v0.1":
        fail("target oracle missing or wrong schema")
        return
    if FileAccess.get_sha256(RECEIVER_GLB) != String(oracle.get("receiver_glb_sha256", "")):
        fail("exact current-UC receiver GLB byte identity mismatch")
        return
    if int(oracle.get("vertex_count", -1)) != EXPECTED_VERTICES:
        fail("oracle vertex count drift")
        return
    if oracle.get("dynamic_window_vertices") != [EXPECTED_WINDOW_START, EXPECTED_WINDOW_END]:
        fail("oracle dynamic-window identity drift")
        return

    var imported := import_receiver()
    if imported == null or imported.mesh == null:
        return
    var imported_mesh := imported.mesh
    if imported_mesh.get_surface_count() != 1:
        fail("current-UC receiver must import as exactly one surface")
        return
    var arrays := imported_mesh.surface_get_arrays(0)
    var neutral_vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
    var indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX]
    if neutral_vertices.size() != EXPECTED_VERTICES:
        fail("Godot import did not preserve 390-vertex identity")
        return
    if indices.size() != int(oracle.get("triangle_count", -1)) * 3:
        fail("Godot imported index count drift")
        return

    var neutral_pose := {}
    for pose in oracle.get("poses", []):
        if absf(float(pose.get("shared_driver_deg", 999.0))) <= 0.000001:
            neutral_pose = pose
            break
    if neutral_pose.is_empty():
        fail("target oracle has no neutral pose")
        return
    var imported_neutral_delta := max_position_delta(neutral_vertices, neutral_pose.get("control_target_positions_m"))
    if imported_neutral_delta > POSITION_TOL_M:
        fail("Godot import reordered or drifted target vertices: " + str(imported_neutral_delta))
        return

    configure_scene(neutral_vertices)
    var neutral_mesh := make_dynamic_mesh(arrays)
    instance.mesh = neutral_mesh
    var neutral_image := await capture_image()
    if neutral_image.save_png("res://generated/neutral.png") != OK:
        fail("cannot retain neutral target frame")
        return

    var stride := int(oracle.get("position_stride_bytes", -1))
    var dynamic_offset := int(oracle.get("dynamic_byte_offset", -1))
    var dynamic_length := int(oracle.get("dynamic_byte_length", -1))
    var full_length := int(oracle.get("full_position_bytes", -1))
    if stride != 12 or dynamic_offset != EXPECTED_WINDOW_START * stride or dynamic_length != (EXPECTED_WINDOW_END - EXPECTED_WINDOW_START) * stride:
        fail("target byte-window contract drift")
        return
    if full_length != EXPECTED_VERTICES * stride:
        fail("target full position byte budget drift")
        return

    var rows := []
    var max_import_delta := imported_neutral_delta
    var discriminating_pose_count := 0
    for pose in oracle.get("poses", []):
        var driver := float(pose.get("shared_driver_deg", 999.0))
        var full_positions := packed_positions(pose.get("control_target_positions_m"))
        var dynamic_positions := packed_positions(pose.get("candidate_dynamic_target_positions_m"))
        if full_positions.size() != EXPECTED_VERTICES or dynamic_positions.size() != EXPECTED_WINDOW_END - EXPECTED_WINDOW_START:
            fail("target pose packet count drift")
            return

        var full_bytes := full_positions.to_byte_array()
        var dynamic_bytes := dynamic_positions.to_byte_array()
        if full_bytes.size() != full_length or dynamic_bytes.size() != dynamic_length:
            fail("Godot PackedVector3Array byte serialization drift")
            return

        var control_mesh := make_dynamic_mesh(arrays)
        control_mesh.surface_update_vertex_region(0, 0, full_bytes)
        instance.mesh = control_mesh
        var control_image := await capture_image()

        var candidate_mesh := make_dynamic_mesh(arrays)
        candidate_mesh.surface_update_vertex_region(0, dynamic_offset, dynamic_bytes)
        instance.mesh = candidate_mesh
        var candidate_image := await capture_image()

        var pair := image_delta(control_image, candidate_image)
        if not bool(pair.get("byte_identical", false)):
            fail("partial target update diverged from full control at driver " + str(driver) + ": " + str(pair))
            return

        var neutral_delta := image_delta(neutral_image, candidate_image)
        if absf(driver) >= 4.999 and int(neutral_delta.get("changed_pixels", 0)) <= 100:
            fail("peak partial update did not produce a discriminating rendered change")
            return
        if int(neutral_delta.get("changed_pixels", 0)) > 100:
            discriminating_pose_count += 1

        var tag := ("m" if driver < 0.0 else "p") + str(absf(driver)).replace(".", "_")
        if absf(driver) < 0.000001:
            tag = "zero"
        if control_image.save_png("res://generated/control-" + tag + ".png") != OK:
            fail("cannot retain control frame")
            return
        if candidate_image.save_png("res://generated/candidate-" + tag + ".png") != OK:
            fail("cannot retain candidate frame")
            return

        rows.append({
            "shared_driver_deg": driver,
            "full_update_bytes": full_bytes.size(),
            "partial_update_offset_bytes": dynamic_offset,
            "partial_update_bytes": dynamic_bytes.size(),
            "control_candidate_render_delta": pair,
            "candidate_vs_neutral_render_delta": neutral_delta
        })

    if rows.size() != 5:
        fail("target driver witness count drift")
        return
    if discriminating_pose_count < 4:
        fail("target receiver lacks discriminating non-neutral rendered witnesses")
        return

    receipt["state"] = "PASS_NATURE_EAST_REAR_CURRENT_UC_GODOT_PARTIAL_VERTEX_WINDOW_RECEIVER"
    receipt["godot_version"] = Engine.get_version_info()
    receipt["rendering_method"] = RenderingServer.get_current_rendering_method()
    receipt["display_server"] = DisplayServer.get_name()
    receipt["receiver_glb_sha256"] = FileAccess.get_sha256(RECEIVER_GLB)
    receipt["imported_vertices"] = neutral_vertices.size()
    receipt["imported_triangles"] = int(indices.size() / 3)
    receipt["maximum_imported_neutral_vertex_delta_m"] = max_import_delta
    receipt["position_tolerance_m"] = POSITION_TOL_M
    receipt["target_update_api"] = "ArrayMesh.surface_update_vertex_region"
    receipt["dynamic_update_flag"] = "Mesh.ARRAY_FLAG_USE_DYNAMIC_UPDATE"
    receipt["dynamic_window_vertices"] = [EXPECTED_WINDOW_START, EXPECTED_WINDOW_END]
    receipt["dynamic_window_byte_offset"] = dynamic_offset
    receipt["dynamic_window_byte_length"] = dynamic_length
    receipt["full_position_byte_length"] = full_length
    receipt["position_packet_reduction_bytes"] = full_length - dynamic_length
    receipt["position_packet_reduction_percent"] = float(full_length - dynamic_length) / float(full_length) * 100.0
    receipt["driver_rows"] = rows
    receipt["truth_boundary"] = {
        "exact_current_uc_glb_imported": true,
        "source_vertex_to_target_vertex_order_preserved": true,
        "real_target_host_partial_vertex_region_update_exercised": true,
        "full_vs_partial_shaded_render_byte_identity_proven_for_five_retained_static_poses": true,
        "proof_material_and_cull_override_are_target_receiver_only": true,
        "target_device_performance_proven": false,
        "physical_wind_or_animation_timing_proven": false,
        "continuous_motion_or_collision_proven": false,
        "final_nature_material_or_foliage_sidedness_proven": false,
        "art_direction_or_visual_qa_acceptance_proven": false,
        "uc_inferred_nature_or_runtime_semantics": false,
        "canon_or_production_readiness_proven": false
    }
    write_receipt()
    print("AXM NATURE DYNAMIC WINDOW TARGET ", JSON.stringify(receipt))
    quit(0)

func _initialize() -> void:
    _run.call_deferred()
