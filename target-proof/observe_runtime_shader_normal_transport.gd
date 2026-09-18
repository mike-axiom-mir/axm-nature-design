extends SceneTree

const ORACLE_PATH := "res://generated/runtime-shader-driver-oracle.json"
const GLB_PATH := "res://generated/nature-east-rear-runtime-normal-receiver.glb"
const CORRECTED_SHADER_PATH := "res://generated/technical-art-position-plus-normal-debug.gdshader"
const NEGATIVE_SHADER_PATH := "res://generated/runtime-position-only-normal-debug.gdshader"
const PACKET_PATH := "res://generated/technical-art-normal-transport-packet.json"
const RECEIPT_PATH := "res://runtime-shader-normal-transport-receipt.json"
const RENDER_DIR := "res://renders/runtime-shader-normal-transport"
const EXPECTED_VERTICES := 390
const EXPECTED_TRIANGLES := 570

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

func _vec3(row: Variant) -> Vector3:
    if typeof(row) != TYPE_ARRAY or row.size() != 3:
        _fail("invalid vec3 row")
        return Vector3.ZERO
    return Vector3(float(row[0]), float(row[1]), float(row[2]))

func _target_to_source(value: Vector3) -> Vector3:
    return Vector3(value.x, value.z, value.y)

func _source_to_target(value: Vector3) -> Vector3:
    return Vector3(value.x, value.z, value.y)

func _cpu_pose(
    neutral_positions: PackedVector3Array,
    neutral_normals: PackedVector3Array,
    groups: Array,
    driver_deg: float
) -> Dictionary:
    var positions := neutral_positions.duplicate()
    var normals := neutral_normals.duplicate()
    for group in groups:
        var pivot := _vec3(group.get("pivot_source_m", []))
        var axis := _vec3(group.get("axis_source", [])).normalized()
        var angle := deg_to_rad(driver_deg * float(group.get("command_sign_multiplier", 0.0)))
        for run in group.get("vertex_id_runs", []):
            if typeof(run) != TYPE_ARRAY or run.size() != 2:
                _fail("invalid VERTEX_ID run")
                return {}
            for vertex_index in range(int(run[0]), int(run[1])):
                var source_point := _target_to_source(neutral_positions[vertex_index])
                var source_normal := _target_to_source(neutral_normals[vertex_index]).normalized()
                positions[vertex_index] = _source_to_target(
                    pivot + (source_point - pivot).rotated(axis, angle)
                )
                normals[vertex_index] = _source_to_target(source_normal.rotated(axis, angle)).normalized()
    return {"positions": positions, "normals": normals}

func _control_mesh(source: ArrayMesh, positions: PackedVector3Array, normals: PackedVector3Array) -> ArrayMesh:
    var arrays := source.surface_get_arrays(0)
    arrays[Mesh.ARRAY_VERTEX] = positions
    arrays[Mesh.ARRAY_NORMAL] = normals
    var result := ArrayMesh.new()
    result.add_surface_from_arrays(source.surface_get_primitive_type(0), arrays)
    return result

func _material(path: String, driver: float, apply_driver: float) -> ShaderMaterial:
    var shader := Shader.new()
    shader.code = FileAccess.get_file_as_string(path)
    var material := ShaderMaterial.new()
    material.shader = shader
    material.set_shader_parameter("driver_deg", driver)
    material.set_shader_parameter("apply_driver", apply_driver)
    return material

func _driver_token(value: float) -> String:
    return String.num(value, 1).replace("-", "m").replace(".", "p")

func _capture(mesh_node: MeshInstance3D, mesh: ArrayMesh, material: ShaderMaterial, path: String) -> Image:
    mesh_node.mesh = mesh
    mesh_node.material_override = material
    await process_frame
    await RenderingServer.frame_post_draw
    var image := get_root().get_texture().get_image()
    if image == null or image.is_empty():
        _fail("render capture returned empty image")
        return Image.new()
    if image.save_png(path) != OK:
        _fail("failed to save render: %s" % path)
        return Image.new()
    return image

func _image_delta(left: Image, right: Image) -> Dictionary:
    if left.get_size() != right.get_size():
        return {"size_mismatch": true}
    var changed := 0
    var gt1 := 0
    var maximum := 0
    var absolute_sum := 0
    var width := left.get_width()
    var height := left.get_height()
    for y in range(height):
        for x in range(width):
            var a := left.get_pixel(x, y)
            var b := right.get_pixel(x, y)
            var channels_a := [a.r8, a.g8, a.b8, a.a8]
            var channels_b := [b.r8, b.g8, b.b8, b.a8]
            var pixel_max := 0
            for channel in range(4):
                var delta: int = abs(int(channels_a[channel]) - int(channels_b[channel]))
                pixel_max = max(pixel_max, delta)
                absolute_sum += delta
            if pixel_max > 0:
                changed += 1
            if pixel_max > 1:
                gt1 += 1
            maximum = max(maximum, pixel_max)
    return {
        "pixels": width * height,
        "changed_pixels": changed,
        "pixels_gt_1_lsb": gt1,
        "maximum_channel_delta_lsb": maximum,
        "absolute_channel_delta_sum": absolute_sum,
    }

func _write_json(path: String, payload: Dictionary) -> void:
    var handle := FileAccess.open(path, FileAccess.WRITE)
    if handle == null:
        _fail("failed to open receipt")
        return
    handle.store_string(JSON.stringify(payload, "  ", false) + "\n")
    handle.close()

func _run() -> void:
    var oracle := _read_json(ORACLE_PATH)
    var packet := _read_json(PACKET_PATH)
    if oracle.is_empty() or packet.is_empty():
        return
    if String(oracle.get("result", "")) != "PASS_FRAGMENTED_VERTEX_ID_RUNS_TILE_EXACT_DYNAMIC_WINDOW":
        _fail("Runtime fragmented-run oracle is not green")
        return
    if String(packet.get("result", "")) != "PASS_NATURE_RUNTIME_SHADER_NORMAL_TRANSPORT_PACKET_READY":
        _fail("Technical Art normal-transport packet is not green")
        return
    var groups: Array = oracle.get("groups", [])
    if groups.size() != 5 or int(oracle.get("vertex_id_run_count", -1)) != 10:
        _fail("exact Runtime carrier identity drift")
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
    var arrays := neutral_mesh.surface_get_arrays(0)
    var neutral_positions: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
    var neutral_normals: PackedVector3Array = arrays[Mesh.ARRAY_NORMAL]
    var indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX]
    if neutral_positions.size() != EXPECTED_VERTICES or neutral_normals.size() != EXPECTED_VERTICES:
        _fail("imported position/normal count drift")
        return
    if indices.size() != EXPECTED_TRIANGLES * 3:
        _fail("imported triangle count drift")
        return

    var camera := Camera3D.new()
    imported_root.add_child(camera)
    camera.position = Vector3(5.4, 3.4, 5.4)
    camera.look_at(Vector3(0.0, 2.0, 0.0), Vector3.UP)
    camera.fov = 42.0
    camera.current = true
    var world_environment := WorldEnvironment.new()
    var environment := Environment.new()
    environment.background_mode = Environment.BG_COLOR
    environment.background_color = Color(0.02, 0.025, 0.03, 1.0)
    world_environment.environment = environment
    imported_root.add_child(world_environment)
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(RENDER_DIR))

    var driver_values: Array = oracle.get("representative_driver_deg", [])
    if driver_values.size() != 5:
        _fail("Runtime witness set drift")
        return
    var rows: Array = []
    var corrected_gt1_total := 0
    var negative_gt1_total := 0
    var corrected_abs_total := 0
    var negative_abs_total := 0
    var nonzero_discriminating := 0

    for value in driver_values:
        var driver := float(value)
        var posed := _cpu_pose(neutral_positions, neutral_normals, groups, driver)
        if posed.is_empty():
            return
        var control_mesh := _control_mesh(neutral_mesh, posed["positions"], posed["normals"])
        var corrected_material := _material(CORRECTED_SHADER_PATH, driver, 1.0)
        var control_material := _material(CORRECTED_SHADER_PATH, driver, 0.0)
        var negative_material := _material(NEGATIVE_SHADER_PATH, driver, 1.0)
        var token := _driver_token(driver)
        var control_image := await _capture(mesh_node, control_mesh, control_material, "%s/control_%s.png" % [RENDER_DIR, token])
        var corrected_image := await _capture(mesh_node, neutral_mesh, corrected_material, "%s/corrected_%s.png" % [RENDER_DIR, token])
        var negative_image := await _capture(mesh_node, neutral_mesh, negative_material, "%s/position_only_%s.png" % [RENDER_DIR, token])
        var corrected_delta := _image_delta(control_image, corrected_image)
        var negative_delta := _image_delta(control_image, negative_image)
        corrected_gt1_total += int(corrected_delta.get("pixels_gt_1_lsb", 0))
        negative_gt1_total += int(negative_delta.get("pixels_gt_1_lsb", 0))
        corrected_abs_total += int(corrected_delta.get("absolute_channel_delta_sum", 0))
        negative_abs_total += int(negative_delta.get("absolute_channel_delta_sum", 0))
        if abs(driver) > 0.001 and int(negative_delta.get("pixels_gt_1_lsb", 0)) > int(corrected_delta.get("pixels_gt_1_lsb", 0)):
            nonzero_discriminating += 1
        rows.append({
            "shared_driver_deg": driver,
            "corrected_vs_cpu_control": corrected_delta,
            "position_only_negative_vs_cpu_control": negative_delta,
        })

    var neutral_row: Dictionary = rows[2]
    if int(neutral_row["corrected_vs_cpu_control"].get("pixels_gt_1_lsb", -1)) != 0:
        _fail("neutral corrected path is not observationally identical")
        return
    if int(neutral_row["position_only_negative_vs_cpu_control"].get("pixels_gt_1_lsb", -1)) != 0:
        _fail("neutral negative path unexpectedly differs")
        return
    if negative_gt1_total <= 100:
        _fail("position-only normal negative is not discriminating")
        return
    if nonzero_discriminating < 4:
        _fail("corrected normal path does not improve all four nonzero witnesses")
        return
    if corrected_abs_total >= negative_abs_total:
        _fail("corrected normal path is not closer to CPU normal control")
        return
    if corrected_gt1_total > max(64, int(float(negative_gt1_total) * 0.02)):
        _fail("corrected normal transport exceeds bounded diagnostic error envelope")
        return

    var receipt := {
        "schema": "axm.nature-runtime-shader-normal-godot-target/v0.1",
        "state": "PASS_NATURE_RUNTIME_SHADER_NORMAL_TRANSPORT_CURRENT_UC_GODOT",
        "godot": Engine.get_version_info(),
        "receiver": {
            "vertices": neutral_positions.size(),
            "normals": neutral_normals.size(),
            "triangles": indices.size() / 3,
            "runtime_vertex_id_runs": int(oracle.get("vertex_id_run_count", -1)),
        },
        "measurements": {
            "pose_count": rows.size(),
            "rows": rows,
            "corrected_pixels_gt_1_lsb_total": corrected_gt1_total,
            "position_only_negative_pixels_gt_1_lsb_total": negative_gt1_total,
            "corrected_absolute_channel_delta_sum": corrected_abs_total,
            "position_only_negative_absolute_channel_delta_sum": negative_abs_total,
            "nonzero_witnesses_where_corrected_beats_position_only": nonzero_discriminating,
        },
        "truth_boundary": {
            "proof_normal_direction_transport_only": true,
            "tangent_transport_proven": false,
            "final_nature_lookdev_or_art_acceptance_proven": false,
            "target_device_performance_proven": false,
            "physical_wind_or_animation_timing_proven": false,
            "generic_uc_normal_deformation_policy_created": false,
            "canon_or_production_readiness_proven": false,
        },
    }
    _write_json(RECEIPT_PATH, receipt)
    print(JSON.stringify(receipt, "  ", false))
    quit(0)
