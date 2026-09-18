extends SceneTree

const ORACLE_PATH := "res://generated/runtime-shader-driver-oracle.json"
const GLB_PATH := "res://generated/nature-east-rear-runtime-normal-receiver.glb"
const CORRECTED_SHADER_PATH := "res://generated/technical-art-position-plus-normal-debug.gdshader"
const NEGATIVE_SHADER_PATH := "res://generated/runtime-position-only-normal-debug.gdshader"
const PACKET_PATH := "res://generated/technical-art-normal-transport-packet.json"
const MATERIAL_FAMILY_PATH := "res://generated/nature_woody_foliage_family_001.json"
const RECEIPT_PATH := "res://normal-shaded-receive-runtime-receipt.json"
const RENDER_DIR := "res://renders/normal-shaded-receive"
const EXPECTED_VERTICES := 390
const EXPECTED_TRIANGLES := 570
const EXPECTED_MATERIAL_SCHEMA := "axm.nature-woody-foliage-material-family/v0.1"
const EXPECTED_FAMILY_ID := "nature-woody-foliage-family-001"

func _initialize() -> void:
    call_deferred("_run")

func _fail(message: String) -> void:
    push_error(message)
    quit(1)

func _read_json(path: String) -> Dictionary:
    if not FileAccess.file_exists(path):
        _fail("missing JSON: %s" % path)
        return {}
    var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
    if typeof(parsed) != TYPE_DICTIONARY:
        _fail("invalid JSON object: %s" % path)
        return {}
    return parsed as Dictionary

func _find_mesh(node: Node) -> MeshInstance3D:
    if node is MeshInstance3D:
        return node as MeshInstance3D
    for child: Node in node.get_children():
        var found: MeshInstance3D = _find_mesh(child)
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
    var positions: PackedVector3Array = neutral_positions.duplicate()
    var normals: PackedVector3Array = neutral_normals.duplicate()
    for group_variant: Variant in groups:
        var group: Dictionary = group_variant as Dictionary
        var pivot: Vector3 = _vec3(group.get("pivot_source_m", []))
        var axis: Vector3 = _vec3(group.get("axis_source", [])).normalized()
        var angle: float = deg_to_rad(driver_deg * float(group.get("command_sign_multiplier", 0.0)))
        for run_variant: Variant in group.get("vertex_id_runs", []):
            var run: Array = run_variant as Array
            if run.size() != 2:
                _fail("invalid VERTEX_ID run")
                return {}
            for vertex_index: int in range(int(run[0]), int(run[1])):
                var source_point: Vector3 = _target_to_source(neutral_positions[vertex_index])
                var source_normal: Vector3 = _target_to_source(neutral_normals[vertex_index]).normalized()
                positions[vertex_index] = _source_to_target(
                    pivot + (source_point - pivot).rotated(axis, angle)
                )
                normals[vertex_index] = _source_to_target(source_normal.rotated(axis, angle)).normalized()
    return {"positions": positions, "normals": normals}

func _control_mesh(source: ArrayMesh, positions: PackedVector3Array, normals: PackedVector3Array) -> ArrayMesh:
    var arrays: Array = source.surface_get_arrays(0)
    arrays[Mesh.ARRAY_VERTEX] = positions
    arrays[Mesh.ARRAY_NORMAL] = normals
    var result := ArrayMesh.new()
    result.add_surface_from_arrays(source.surface_get_primitive_type(0), arrays)
    return result

func _pbr_shader_code(path: String) -> String:
    var code: String = FileAccess.get_file_as_string(path)
    if code.is_empty():
        _fail("missing shader: %s" % path)
        return ""
    if code.count("render_mode unshaded, cull_disabled;") != 1:
        _fail("Technical Art diagnostic render mode drift: %s" % path)
        return ""
    code = code.replace("render_mode unshaded, cull_disabled;", "render_mode cull_disabled;")
    var fragment_index: int = code.find("void fragment()")
    if fragment_index < 0:
        _fail("Technical Art diagnostic fragment drift: %s" % path)
        return ""
    code = code.substr(0, fragment_index)
    var marker := "render_mode cull_disabled;\n"
    var uniforms := (
        "uniform vec4 material_albedo = vec4(1.0);\n"
        + "uniform float material_roughness = 0.5;\n"
        + "uniform float material_metallic = 0.0;\n"
    )
    if code.count(marker) != 1:
        _fail("Materials shaded receiver marker drift: %s" % path)
        return ""
    code = code.replace(marker, marker + uniforms)
    code += (
        "void fragment() {\n"
        + "    ALBEDO = material_albedo.rgb;\n"
        + "    ROUGHNESS = material_roughness;\n"
        + "    METALLIC = material_metallic;\n"
        + "}\n"
    )
    return code

func _material(
    path: String,
    driver: float,
    apply_driver: float,
    albedo: Color,
    roughness: float,
    metallic: float
) -> ShaderMaterial:
    var shader := Shader.new()
    shader.code = _pbr_shader_code(path)
    var material := ShaderMaterial.new()
    material.shader = shader
    material.set_shader_parameter("driver_deg", driver)
    material.set_shader_parameter("apply_driver", apply_driver)
    material.set_shader_parameter("material_albedo", albedo)
    material.set_shader_parameter("material_roughness", roughness)
    material.set_shader_parameter("material_metallic", metallic)
    return material

func _driver_token(value: float) -> String:
    return String.num(value, 1).replace("-", "m").replace(".", "p")

func _capture(mesh_node: MeshInstance3D, mesh: ArrayMesh, material: ShaderMaterial, path: String) -> Image:
    mesh_node.mesh = mesh
    mesh_node.material_override = material
    await process_frame
    await RenderingServer.frame_post_draw
    var image: Image = get_root().get_texture().get_image()
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
    var changed: int = 0
    var gt1: int = 0
    var maximum: int = 0
    var absolute_sum: int = 0
    var width: int = left.get_width()
    var height: int = left.get_height()
    for y: int in range(height):
        for x: int in range(width):
            var a: Color = left.get_pixel(x, y)
            var b: Color = right.get_pixel(x, y)
            var channels_a: Array[int] = [a.r8, a.g8, a.b8, a.a8]
            var channels_b: Array[int] = [b.r8, b.g8, b.b8, b.a8]
            var pixel_max: int = 0
            for channel: int in range(4):
                var delta: int = abs(channels_a[channel] - channels_b[channel])
                pixel_max = maxi(pixel_max, delta)
                absolute_sum += delta
            if pixel_max > 0:
                changed += 1
            if pixel_max > 1:
                gt1 += 1
            maximum = maxi(maximum, pixel_max)
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

func _set_context(camera: Camera3D, light: DirectionalLight3D, context_name: String) -> void:
    if context_name == "three_quarter":
        camera.position = Vector3(5.4, 3.4, 5.4)
        camera.look_at(Vector3(0.0, 2.0, 0.0), Vector3.UP)
        camera.fov = 42.0
        light.rotation_degrees = Vector3(-48.0, -35.0, 0.0)
    elif context_name == "low_grazing":
        camera.position = Vector3(6.2, 1.85, 3.2)
        camera.look_at(Vector3(0.0, 1.85, 0.0), Vector3.UP)
        camera.fov = 38.0
        light.rotation_degrees = Vector3(-22.0, 58.0, 0.0)
    else:
        _fail("unknown context: %s" % context_name)

func _run() -> void:
    var oracle: Dictionary = _read_json(ORACLE_PATH)
    var packet: Dictionary = _read_json(PACKET_PATH)
    var family: Dictionary = _read_json(MATERIAL_FAMILY_PATH)
    if oracle.is_empty() or packet.is_empty() or family.is_empty():
        return
    if String(oracle.get("result", "")) != "PASS_FRAGMENTED_VERTEX_ID_RUNS_TILE_EXACT_DYNAMIC_WINDOW":
        _fail("Runtime fragmented-run oracle is not green")
        return
    if String(packet.get("result", "")) != "PASS_NATURE_RUNTIME_SHADER_NORMAL_TRANSPORT_PACKET_READY":
        _fail("Technical Art normal-transport packet is not green")
        return
    if String(family.get("schema", "")) != EXPECTED_MATERIAL_SCHEMA or String(family.get("family_id", "")) != EXPECTED_FAMILY_ID:
        _fail("Materials family identity drift")
        return
    var groups: Array = oracle.get("groups", [])
    if groups.size() != 5 or int(oracle.get("vertex_id_run_count", -1)) != 10:
        _fail("exact Runtime carrier identity drift")
        return

    var material_rows: Dictionary = family.get("materials", {})
    if material_rows.size() != 2 or not material_rows.has("woody") or not material_rows.has("foliage"):
        _fail("Materials family probe set drift")
        return
    var woody: Dictionary = material_rows["woody"] as Dictionary
    var foliage: Dictionary = material_rows["foliage"] as Dictionary
    if String(woody.get("color", "")) != "#5C3B27FF" or float(woody.get("roughness", -1.0)) != 0.84 or float(woody.get("metallic", -1.0)) != 0.0:
        _fail("woody scalar probe drift")
        return
    if String(foliage.get("color", "")) != "#5A823EFF" or float(foliage.get("roughness", -1.0)) != 0.58 or float(foliage.get("metallic", -1.0)) != 0.0:
        _fail("foliage scalar probe drift")
        return

    var document := GLTFDocument.new()
    var state := GLTFState.new()
    if document.append_from_file(GLB_PATH, state) != OK:
        _fail("GLB import failed")
        return
    var imported_root: Node = document.generate_scene(state)
    if imported_root == null:
        _fail("GLB generate_scene returned null")
        return
    get_root().add_child(imported_root)
    await process_frame
    var mesh_node: MeshInstance3D = _find_mesh(imported_root)
    if mesh_node == null:
        _fail("no MeshInstance3D found")
        return
    var neutral_mesh: ArrayMesh = mesh_node.mesh as ArrayMesh
    if neutral_mesh == null or neutral_mesh.get_surface_count() != 1:
        _fail("receiver is not one-surface ArrayMesh")
        return
    var arrays: Array = neutral_mesh.surface_get_arrays(0)
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
    camera.current = true
    var light := DirectionalLight3D.new()
    imported_root.add_child(light)
    light.light_energy = 1.9
    var world_environment := WorldEnvironment.new()
    var environment := Environment.new()
    environment.background_mode = Environment.BG_COLOR
    environment.background_color = Color(0.025, 0.03, 0.035, 1.0)
    environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
    environment.ambient_light_color = Color(0.20, 0.22, 0.24, 1.0)
    environment.ambient_light_energy = 0.55
    world_environment.environment = environment
    imported_root.add_child(world_environment)
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(RENDER_DIR))

    var driver_values: Array = oracle.get("representative_driver_deg", [])
    if driver_values.size() != 5:
        _fail("Runtime witness set drift")
        return
    var probes: Dictionary = {
        "woody": {"albedo": Color8(92, 59, 39, 255), "roughness": 0.84, "metallic": 0.0},
        "foliage": {"albedo": Color8(90, 130, 62, 255), "roughness": 0.58, "metallic": 0.0},
    }
    var context_names: Array[String] = ["three_quarter", "low_grazing"]
    var receipt_contexts: Dictionary = {}
    var corrected_gt1_total: int = 0
    var negative_gt1_total: int = 0
    var corrected_abs_total: int = 0
    var negative_abs_total: int = 0
    var expected_nonzero_comparisons: int = 0
    var nonzero_corrected_better: int = 0
    var neutral_equivalence_checks: int = 0
    var active_driver_checks: int = 0
    var active_material_context_checks: int = 0

    for context_name: String in context_names:
        _set_context(camera, light, context_name)
        var context_receipt: Dictionary = {}
        var neutral_controls: Dictionary = {}
        for probe_name: String in probes.keys():
            var probe: Dictionary = probes[probe_name] as Dictionary
            var probe_rows: Array = []
            var control_images: Dictionary = {}
            for value: Variant in driver_values:
                var driver: float = float(value)
                var posed: Dictionary = _cpu_pose(neutral_positions, neutral_normals, groups, driver)
                if posed.is_empty():
                    return
                var control_mesh: ArrayMesh = _control_mesh(neutral_mesh, posed["positions"], posed["normals"])
                var albedo: Color = probe["albedo"] as Color
                var roughness: float = float(probe["roughness"])
                var metallic: float = float(probe["metallic"])
                var control_material: ShaderMaterial = _material(CORRECTED_SHADER_PATH, driver, 0.0, albedo, roughness, metallic)
                var corrected_material: ShaderMaterial = _material(CORRECTED_SHADER_PATH, driver, 1.0, albedo, roughness, metallic)
                var negative_material: ShaderMaterial = _material(NEGATIVE_SHADER_PATH, driver, 1.0, albedo, roughness, metallic)
                var token: String = _driver_token(driver)
                var prefix := "%s/%s-%s-%s" % [RENDER_DIR, context_name, probe_name, token]
                var control_image: Image = await _capture(mesh_node, control_mesh, control_material, prefix + "-control.png")
                var corrected_image: Image = await _capture(mesh_node, neutral_mesh, corrected_material, prefix + "-corrected.png")
                var negative_image: Image = await _capture(mesh_node, neutral_mesh, negative_material, prefix + "-position-only.png")
                control_images[token] = control_image
                if abs(driver) < 0.001:
                    neutral_controls[probe_name] = control_image
                var corrected_delta: Dictionary = _image_delta(control_image, corrected_image)
                var negative_delta: Dictionary = _image_delta(control_image, negative_image)
                corrected_gt1_total += int(corrected_delta.get("pixels_gt_1_lsb", 0))
                negative_gt1_total += int(negative_delta.get("pixels_gt_1_lsb", 0))
                corrected_abs_total += int(corrected_delta.get("absolute_channel_delta_sum", 0))
                negative_abs_total += int(negative_delta.get("absolute_channel_delta_sum", 0))
                if abs(driver) < 0.001:
                    if int(corrected_delta.get("pixels_gt_1_lsb", -1)) != 0 or int(negative_delta.get("pixels_gt_1_lsb", -1)) != 0:
                        _fail("neutral shaded receiver equivalence drift: %s/%s" % [context_name, probe_name])
                        return
                    neutral_equivalence_checks += 1
                else:
                    expected_nonzero_comparisons += 1
                    if int(corrected_delta.get("absolute_channel_delta_sum", 0)) < int(negative_delta.get("absolute_channel_delta_sum", 0)):
                        nonzero_corrected_better += 1
                probe_rows.append({
                    "shared_driver_deg": driver,
                    "corrected_vs_cpu_control": corrected_delta,
                    "position_only_negative_vs_cpu_control": negative_delta,
                })
            if not control_images.has("0p0") or not control_images.has("5p0"):
                _fail("control driver witness images missing")
                return
            var driver_delta: Dictionary = _image_delta(control_images["0p0"] as Image, control_images["5p0"] as Image)
            if int(driver_delta.get("pixels_gt_1_lsb", 0)) <= 100:
                _fail("shaded receiver does not visibly discriminate neutral from +5 degrees")
                return
            active_driver_checks += 1
            context_receipt[probe_name] = {
                "albedo": String(woody["color"] if probe_name == "woody" else foliage["color"]),
                "roughness": float(probe["roughness"]),
                "metallic": float(probe["metallic"]),
                "rows": probe_rows,
                "neutral_to_plus5_control": driver_delta,
            }
        if not neutral_controls.has("woody") or not neutral_controls.has("foliage"):
            _fail("neutral material probe captures missing")
            return
        var material_delta: Dictionary = _image_delta(neutral_controls["woody"] as Image, neutral_controls["foliage"] as Image)
        if int(material_delta.get("pixels_gt_1_lsb", 0)) <= 100:
            _fail("woody and foliage scalar probe contexts are not renderer-visible")
            return
        active_material_context_checks += 1
        context_receipt["neutral_woody_vs_foliage"] = material_delta
        receipt_contexts[context_name] = context_receipt

    if expected_nonzero_comparisons != 16 or nonzero_corrected_better != expected_nonzero_comparisons:
        _fail("corrected shaded normal transport does not beat position-only negative in every nonzero probe/context witness")
        return
    if corrected_abs_total >= negative_abs_total:
        _fail("corrected shaded normal transport is not closer to CPU control in aggregate")
        return
    if negative_gt1_total <= 500:
        _fail("position-only shaded normal negative is not sufficiently discriminating")
        return
    if neutral_equivalence_checks != 4 or active_driver_checks != 4 or active_material_context_checks != 2:
        _fail("expected shaded receiver activity/equivalence checks did not complete")
        return

    var receipt := {
        "schema": "axm.nature-material-shaded-normal-receive/v0.1",
        "state": "PASS_NATURE_TA_PROOF_NORMAL_DIRECTION_SURVIVES_SHADED_MATERIAL_RECEIVER__PASS54_EXACT_CARRIER_ONLY",
        "godot": Engine.get_version_info(),
        "receiver": {
            "vertices": neutral_positions.size(),
            "normals": neutral_normals.size(),
            "triangles": indices.size() / 3,
            "runtime_vertex_id_runs": int(oracle.get("vertex_id_run_count", -1)),
        },
        "material_probe_contract": {
            "family_id": EXPECTED_FAMILY_ID,
            "whole_receiver_probe_only_not_region_assignment": true,
            "cull_mode": "CULL_DISABLED_TO_REMOVE_SIDEDNESS_AS_VARIABLE",
            "normal_map_used": false,
            "tangent_space_used": false,
            "lighting_is_proof_host_only": true,
        },
        "measurements": {
            "contexts": receipt_contexts,
            "corrected_pixels_gt_1_lsb_total": corrected_gt1_total,
            "position_only_negative_pixels_gt_1_lsb_total": negative_gt1_total,
            "corrected_absolute_channel_delta_sum": corrected_abs_total,
            "position_only_negative_absolute_channel_delta_sum": negative_abs_total,
            "nonzero_corrected_better": nonzero_corrected_better,
            "nonzero_comparisons": expected_nonzero_comparisons,
            "neutral_equivalence_checks": neutral_equivalence_checks,
            "active_driver_checks": active_driver_checks,
            "active_material_context_checks": active_material_context_checks,
        },
        "truth_boundary": {
            "pass54_exact_carrier_only": true,
            "current_animation_runtime_owner_chain_rebound": false,
            "final_region_material_assignment_proven": false,
            "tangent_transport_proven": false,
            "normal_map_or_tangent_space_shading_proven": false,
            "final_nature_lookdev_or_art_acceptance_proven": false,
            "environment_or_map_adoption_proven": false,
            "target_device_performance_proven": false,
            "physical_wind_or_animation_timing_proven": false,
            "generic_uc_material_or_normal_policy_created": false,
            "canon_or_production_readiness_proven": false,
        },
    }
    _write_json(RECEIPT_PATH, receipt)
    print(JSON.stringify(receipt, "  ", false))
    quit(0)
