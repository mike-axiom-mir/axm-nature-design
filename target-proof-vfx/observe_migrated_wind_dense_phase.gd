extends SceneTree

const GENERATED_DIR := "res://generated-dense"
const OUTPUT_RECEIPT := "res://vfx-migrated-wind-dense-phase-receipt.json"
const BG := Color(0.025, 0.030, 0.036, 1.0)
const EXPECTED_MIGRATED_MESH_DIGEST := "47dd4d82651138299d05071df3e8a410f21f673ab8d42b936d7222eb5351b862"
const EXPECTED_PHASE_COUNT := 17
const CONTEXTS := ["ground_oblique", "high_oblique"]

var receipt := {
    "schema": "axm.nature-migrated-wind-dense-phase-godot-observer/v0.1",
    "state": "NOT_RUN",
    "promotion_effect": "NONE",
    "renderer_boundary": "Godot 4.7.2 GL Compatibility. One persistent MeshInstance3D per camera receives 17 direct source-evaluated migrated woody meshes. Leaf blades remain excluded to preserve the Geometry-owned sidedness lane. No wall-clock cadence is asserted.",
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
    var file := FileAccess.open(OUTPUT_RECEIPT, FileAccess.WRITE)
    if file != null:
        file.store_string(JSON.stringify(receipt, "  ") + "\n")
        file.close()

func fail(message: String) -> void:
    receipt["state"] = "FAIL_MIGRATED_WIND_DENSE_PHASE_GODOT_RECEIVER"
    receipt["failure"] = message
    write_receipt()
    push_error(message)
    quit(1)

func source_to_godot(point: Array) -> Vector3:
    if point.size() != 3:
        fail("Nature vertex does not contain exactly three coordinates")
        return Vector3.ZERO
    return Vector3(float(point[0]), float(point[2]), float(point[1]))

func woody_triangle_indices(payload: Dictionary) -> Array:
    var triangles = payload.get("triangles", [])
    var regions = payload.get("regions", [])
    if not (triangles is Array) or not (regions is Array) or triangles.is_empty() or regions.is_empty():
        fail("dense migrated mesh lacks triangles or regions")
        return []
    var included: Array = []
    included.resize(triangles.size())
    included.fill(false)
    for region_value in regions:
        if not (region_value is Dictionary):
            fail("Nature mesh region is not an object")
            return []
        var region := region_value as Dictionary
        var start: int = int(region.get("triangle_start", -1))
        var count: int = int(region.get("triangle_count", -1))
        if start < 0 or count <= 0 or start + count > triangles.size():
            fail("Nature mesh region triangle range is invalid")
            return []
        if String(region.get("kind", "")) == "leaf-blade":
            continue
        for triangle_index in range(start, start + count):
            if bool(included[triangle_index]):
                fail("woody triangle region overlap detected")
                return []
            included[triangle_index] = true
    var result: Array = []
    for triangle_index in range(included.size()):
        if bool(included[triangle_index]):
            result.append(triangle_index)
    if result.is_empty():
        fail("woody-only dense proof selected zero triangles")
    return result

func build_woody_mesh(payload: Dictionary) -> Dictionary:
    var vertices = payload.get("vertices", [])
    var triangles = payload.get("triangles", [])
    if not (vertices is Array) or not (triangles is Array):
        fail("dense migrated mesh lacks vertex/triangle arrays")
        return {}
    var selected: Array = woody_triangle_indices(payload)
    var surface := SurfaceTool.new()
    surface.begin(Mesh.PRIMITIVE_TRIANGLES)
    for triangle_index_value in selected:
        var triangle_index: int = int(triangle_index_value)
        var triangle = triangles[triangle_index]
        if not (triangle is Array) or triangle.size() != 3:
            fail("Nature triangle is malformed")
            return {}
        for local_index in [0, 2, 1]:
            var vertex_index: int = int(triangle[local_index])
            if vertex_index < 0 or vertex_index >= vertices.size():
                fail("Nature triangle index is out of range")
                return {}
            var point = vertices[vertex_index]
            if not (point is Array):
                fail("Nature vertex is malformed")
                return {}
            surface.add_vertex(source_to_godot(point))
    surface.generate_normals()
    var mesh := surface.commit()
    if mesh == null:
        fail("SurfaceTool failed to build woody dense migrated mesh")
        return {}
    return {
        "mesh": mesh,
        "woody_triangle_count": selected.size(),
        "source_triangle_count": triangles.size(),
        "excluded_leaf_triangle_count": triangles.size() - selected.size(),
    }

func proof_material() -> StandardMaterial3D:
    var material := StandardMaterial3D.new()
    material.albedo_color = Color(0.57, 0.78, 0.47, 1.0)
    material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
    material.cull_mode = BaseMaterial3D.CULL_BACK
    return material

func camera_spec(context: String) -> Dictionary:
    if context == "high_oblique":
        return {"position": Vector3(3.4, 4.3, 3.5), "target": Vector3(0.0, 1.95, 0.0), "fov": 40.0}
    return {"position": Vector3(3.9, 2.35, 4.4), "target": Vector3(0.0, 1.8, 0.0), "fov": 39.0}

func changed_from_background(image: Image) -> int:
    var changed: int = 0
    for y in range(image.get_height()):
        for x in range(image.get_width()):
            var pixel := image.get_pixel(x, y)
            var delta: float = maxf(absf(pixel.r - BG.r), maxf(absf(pixel.g - BG.g), absf(pixel.b - BG.b)))
            if delta > 0.035:
                changed += 1
    return changed

func pixel_difference(first: Image, second: Image) -> Dictionary:
    if first.get_width() != second.get_width() or first.get_height() != second.get_height():
        return {"comparable": false, "changed_pixels": -1, "max_channel_delta": 1.0}
    var changed: int = 0
    var max_delta: float = 0.0
    for y in range(first.get_height()):
        for x in range(first.get_width()):
            var a := first.get_pixel(x, y)
            var b := second.get_pixel(x, y)
            var delta: float = maxf(absf(a.r - b.r), maxf(absf(a.g - b.g), absf(a.b - b.b)))
            max_delta = maxf(max_delta, delta)
            if delta > 0.0:
                changed += 1
    return {"comparable": true, "changed_pixels": changed, "max_channel_delta": max_delta}

func normalized_anchor_indices(raw: Variant) -> Array:
    if not (raw is Array):
        return []
    var result: Array = []
    for value in raw:
        result.append(int(value))
    return result

func capture_context(context: String, samples: Array) -> Dictionary:
    var viewport := SubViewport.new()
    viewport.size = Vector2i(720, 720)
    viewport.own_world_3d = true
    viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
    viewport.render_target_clear_mode = SubViewport.CLEAR_MODE_ALWAYS
    get_root().add_child(viewport)

    var root3d := Node3D.new()
    viewport.add_child(root3d)
    var env := Environment.new()
    env.background_mode = Environment.BG_COLOR
    env.background_color = BG
    var world := WorldEnvironment.new()
    world.environment = env
    root3d.add_child(world)

    var instance := MeshInstance3D.new()
    instance.material_override = proof_material()
    root3d.add_child(instance)
    var receiver_instance_id: int = int(instance.get_instance_id())

    var camera := Camera3D.new()
    camera.near = 0.03
    camera.far = 25.0
    var spec := camera_spec(context)
    camera.fov = float(spec["fov"])
    root3d.add_child(camera)
    camera.look_at_from_position(spec["position"] as Vector3, spec["target"] as Vector3, Vector3.UP)
    camera.make_current()

    for _warmup in range(12):
        await process_frame

    var images: Array = []
    var records: Array = []
    var expected_woody_triangles: int = -1
    var expected_leaf_triangles: int = -1
    for sample_value in samples:
        if not (sample_value is Dictionary):
            fail("dense source sample metadata is malformed")
            return {}
        var sample := sample_value as Dictionary
        var index: int = int(sample.get("index", -1))
        var payload_name: String = String(sample.get("payload", ""))
        var payload := read_json(GENERATED_DIR + "/" + payload_name)
        if payload.is_empty():
            fail("missing dense migrated source mesh: " + payload_name)
            return {}
        var built := build_woody_mesh(payload)
        if built.is_empty():
            return {}
        if expected_woody_triangles < 0:
            expected_woody_triangles = int(built["woody_triangle_count"])
            expected_leaf_triangles = int(built["excluded_leaf_triangle_count"])
        elif int(built["woody_triangle_count"]) != expected_woody_triangles or int(built["excluded_leaf_triangle_count"]) != expected_leaf_triangles:
            fail("woody/leaf triangle partition drifted across dense phase sequence")
            return {}

        instance.mesh = built["mesh"]
        for _settle in range(3):
            await process_frame
        if int(instance.get_instance_id()) != receiver_instance_id:
            fail("dense phase receiver MeshInstance3D identity changed")
            return {}
        var image := viewport.get_texture().get_image()
        if image == null or image.is_empty():
            fail("empty Godot dense-phase capture")
            return {}
        var image_path: String = "res://dense-%s-%02d.png" % [context, index]
        if image.save_png(image_path) != OK:
            fail("could not save Godot dense-phase capture")
            return {}
        var visible_pixels: int = changed_from_background(image)
        if visible_pixels < 250:
            fail("insufficient woody geometry in dense-phase capture: " + str(visible_pixels))
            return {}
        images.append(image)
        records.append({
            "index": index,
            "time_s": float(sample.get("time_s", -1.0)),
            "mesh_digest": String(sample.get("mesh_digest", "")),
            "capture_path": image_path,
            "capture_sha256": sha256_file(image_path),
            "visible_pixels": visible_pixels,
            "woody_triangle_count": int(built["woody_triangle_count"]),
            "excluded_leaf_triangle_count": int(built["excluded_leaf_triangle_count"]),
            "receiver_instance_id": receiver_instance_id,
        })

    var adjacent: Array = []
    for index in range(images.size() - 1):
        var comparison := pixel_difference(images[index], images[index + 1])
        comparison["from_index"] = index
        comparison["to_index"] = index + 1
        if int(comparison["changed_pixels"]) <= 0:
            fail("dense phase receiver produced an unchanged adjacent frame in %s: %d -> %d" % [context, index, index + 1])
            return {}
        adjacent.append(comparison)

    var symmetry: Array = []
    var symmetry_count: int = int((images.size() + 1) / 2.0)
    for index in range(symmetry_count):
        var mirror_index: int = images.size() - 1 - index
        var comparison := pixel_difference(images[index], images[mirror_index])
        comparison["index"] = index
        comparison["mirror_index"] = mirror_index
        if int(comparison["changed_pixels"]) != 0:
            fail("dense half-sine source symmetry changed target-host pixels in %s: %d <-> %d" % [context, index, mirror_index])
            return {}
        symmetry.append(comparison)

    var neutral_return := pixel_difference(images[0], images[images.size() - 1])
    if int(neutral_return["changed_pixels"]) != 0:
        fail("dense target-host sequence no longer returns exactly to neutral in " + context)
        return {}

    var peak_index: int = int(images.size() / 2.0)
    var neutral_to_peak := pixel_difference(images[0], images[peak_index])
    if int(neutral_to_peak["changed_pixels"]) <= 0:
        fail("dense target-host peak is not visibly distinct in " + context)
        return {}

    viewport.queue_free()
    for _cleanup in range(2):
        await process_frame

    return {
        "context": context,
        "receiver_instance_id": receiver_instance_id,
        "records": records,
        "adjacent_deltas": adjacent,
        "half_sine_symmetry": symmetry,
        "neutral_return": neutral_return,
        "neutral_to_peak": neutral_to_peak,
        "woody_triangle_count": expected_woody_triangles,
        "excluded_leaf_triangle_count": expected_leaf_triangles,
    }

func _initialize() -> void:
    var summary := read_json(GENERATED_DIR + "/dense-summary.json")
    if summary.get("state") != "PASS_MIGRATED_WOODY_WIND_RESPONSE_DENSE_SOURCE_PHASES":
        fail("dense migrated source evidence is missing or not green")
        return
    if String(summary.get("migrated_neutral_mesh_digest", "")) != EXPECTED_MIGRATED_MESH_DIGEST:
        fail("migrated neutral mesh digest drifted before dense receiver proof")
        return
    if int(summary.get("dense_phase_count", -1)) != EXPECTED_PHASE_COUNT:
        fail("dense phase count drifted")
        return
    if normalized_anchor_indices(summary.get("retained_anchor_indices", [])) != [0, 4, 8, 12, 16]:
        fail("retained five-sample anchor indices drifted")
        return
    var samples = summary.get("samples", [])
    if not (samples is Array) or samples.size() != EXPECTED_PHASE_COUNT:
        fail("dense source sample list is malformed")
        return

    var exact_head_path := GENERATED_DIR + "/exact-head.txt"
    if not FileAccess.file_exists(exact_head_path):
        fail("exact VFX head binding is missing")
        return
    var exact_head: String = FileAccess.get_file_as_string(exact_head_path).strip_edges()

    var contexts := {}
    for context_value in CONTEXTS:
        var context: String = String(context_value)
        var result := await capture_context(context, samples)
        if result.is_empty():
            return
        contexts[context] = result

    receipt["state"] = "PASS_MIGRATED_WOODY_WIND_RESPONSE_DENSE_PHASE_GODOT_RECEIVER"
    receipt["godot_version"] = Engine.get_version_info()
    receipt["vfx_head"] = exact_head
    receipt["migrated_neutral_mesh_digest"] = EXPECTED_MIGRATED_MESH_DIGEST
    receipt["dense_phase_count"] = EXPECTED_PHASE_COUNT
    receipt["retained_anchor_indices"] = [0, 4, 8, 12, 16]
    receipt["phase_step_s"] = float(summary.get("phase_step_s", -1.0))
    receipt["contexts"] = contexts
    receipt["truth_boundary"] = {
        "one_persistent_receiver_instance_per_context": true,
        "direct_source_evaluated_dense_meshes_consumed": true,
        "woody_trunk_branch_geometry_tested": true,
        "leaf_geometry_included": false,
        "neutral_unshaded_material_only": true,
        "dense_discrete_phase_application_tested": true,
        "wall_clock_pacing_tested": false,
        "continuous_mathematical_interpolation_claimed": false,
        "perceptual_smoothness_claimed": false,
        "shaded_lookdev_tested": false,
        "map_receiving_scene_tested": false,
        "physical_wind_or_biomechanics": false,
        "gameplay_or_collision": false,
        "target_device_performance": false,
    }
    write_receipt()
    print(JSON.stringify(receipt))
    quit(0)
