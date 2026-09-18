extends SceneTree

const GENERATED_DIR := "res://generated-compact-east"
const OUTPUT_RECEIPT := "res://compact-east-tree-wind-target-receipt.json"
const BG := Color(0.025, 0.030, 0.036, 1.0)
const EXPECTED_NEUTRAL_DIGEST := "420135f6effbadb1b344675948b9ddc471dcb83177702888f0b32327c5121c18"
const CONTEXTS := ["ground_oblique", "crown_oblique"]

var receipt := {
    "schema": "axm.nature-compact-east-tree-wind-target-observer/v0.1",
    "state": "NOT_RUN",
    "renderer_boundary": "Godot 4.7.2 GL Compatibility. Exact source-phase meshes are transformed from Nature +Z-up to Godot +Y-up. Culling is disabled deliberately so this response test does not absorb the separate leaf-sidedness decision. Neutral unshaded proof material isolates bounded shape motion from final lookdev.",
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
    receipt["state"] = "FAIL_COMPACT_EAST_TREE_WIND_TARGET_OBSERVER"
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
    var mesh = surface.commit()
    if mesh == null:
        fail("SurfaceTool failed to build compact-tree phase mesh")
        return null
    return mesh

func proof_material() -> StandardMaterial3D:
    var material := StandardMaterial3D.new()
    material.albedo_color = Color(0.54, 0.76, 0.43, 1.0)
    material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
    material.cull_mode = BaseMaterial3D.CULL_DISABLED
    return material

func camera_spec(context: String) -> Dictionary:
    if context == "crown_oblique":
        return {"position": Vector3(2.9, 3.3, 2.7), "target": Vector3(0.0, 2.35, 0.0), "fov": 38.0}
    return {"position": Vector3(3.4, 1.9, 4.0), "target": Vector3(0.0, 1.8, 0.0), "fov": 40.0}

func changed_from_background(image: Image) -> int:
    var changed := 0
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
    var changed := 0
    var max_delta := 0.0
    for y in range(first.get_height()):
        for x in range(first.get_width()):
            var a := first.get_pixel(x, y)
            var b := second.get_pixel(x, y)
            var delta: float = maxf(absf(a.r - b.r), maxf(absf(a.g - b.g), absf(a.b - b.b)))
            max_delta = maxf(max_delta, delta)
            if delta > 0.0:
                changed += 1
    return {"comparable": true, "changed_pixels": changed, "max_channel_delta": max_delta}

func capture_phase(payload: Dictionary, phase_index: int, context: String) -> Dictionary:
    var phase_mesh := build_mesh(payload)
    if phase_mesh == null:
        return {}
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
    instance.mesh = phase_mesh
    instance.material_override = proof_material()
    root3d.add_child(instance)

    var camera := Camera3D.new()
    camera.near = 0.03
    camera.far = 25.0
    var spec := camera_spec(context)
    camera.fov = float(spec["fov"])
    root3d.add_child(camera)
    camera.look_at_from_position(spec["position"] as Vector3, spec["target"] as Vector3, Vector3.UP)
    camera.make_current()

    for _i in range(5):
        await process_frame
    var image := viewport.get_texture().get_image()
    if image == null or image.is_empty():
        fail("empty compact-tree target-host capture")
        return {}
    var image_path := "res://compact-wind-%s-phase-%02d.png" % [context, phase_index]
    if image.save_png(image_path) != OK:
        fail("could not save compact-tree target-host capture")
        return {}
    var visible_pixels := changed_from_background(image)
    if visible_pixels < 300:
        fail("insufficient compact-tree geometry in target-host capture: " + str(visible_pixels))
        return {}
    var record := {
        "phase_index": phase_index,
        "context": context,
        "capture_path": image_path,
        "capture_sha256": sha256_file(image_path),
        "capture_width": image.get_width(),
        "capture_height": image.get_height(),
        "visible_pixels": visible_pixels,
        "source_vertices": 390,
        "source_triangles": 570,
        "culling": "disabled_for_response_isolation",
    }
    viewport.queue_free()
    for _i in range(2):
        await process_frame
    return {"record": record, "image": image}

func _initialize() -> void:
    var summary := read_json(GENERATED_DIR + "/summary.json")
    if summary.get("state") != "PASS_COMPACT_EAST_TREE_BOUNDED_VISUAL_RESPONSE_CANDIDATE":
        fail("compact-tree source response evidence is missing or not green")
        return
    if String(summary.get("migrated_neutral_mesh_digest", "")) != EXPECTED_NEUTRAL_DIGEST:
        fail("compact-tree migrated neutral digest drifted")
        return
    if int(summary.get("sample_count", 0)) != 17:
        fail("compact-tree response no longer contains 17 bounded source phases")
        return
    var exact_head_path := GENERATED_DIR + "/exact-head.txt"
    if not FileAccess.file_exists(exact_head_path):
        fail("exact VFX head binding is missing")
        return
    var exact_head := FileAccess.get_file_as_string(exact_head_path).strip_edges()

    var payloads := {}
    for phase_index in range(17):
        var path := GENERATED_DIR + "/phase_%02d_mesh.json" % phase_index
        var payload := read_json(path)
        if payload.is_empty():
            fail("missing compact-tree phase payload: " + path)
            return
        payloads[phase_index] = payload

    var captures := {}
    var images := {}
    for context_value in CONTEXTS:
        var context := String(context_value)
        for phase_index in range(17):
            var result := await capture_phase(payloads[phase_index] as Dictionary, phase_index, context)
            var key := "%s/%02d" % [context, phase_index]
            captures[key] = result["record"]
            images[key] = result["image"]

    var neutral_return := {}
    var neutral_to_peak := {}
    var symmetry := {}
    for context_value in CONTEXTS:
        var context := String(context_value)
        var returned := pixel_difference(images["%s/00" % context], images["%s/16" % context])
        if int(returned["changed_pixels"]) != 0:
            fail("compact-tree exact neutral return drifted in " + context)
            return
        neutral_return[context] = returned
        var moved := pixel_difference(images["%s/00" % context], images["%s/08" % context])
        if int(moved["changed_pixels"]) <= 0:
            fail("compact-tree peak response is not visibly distinct in " + context)
            return
        neutral_to_peak[context] = moved
        for phase_index in range(9):
            var paired := 16 - phase_index
            var compared := pixel_difference(images["%s/%02d" % [context, phase_index]], images["%s/%02d" % [context, paired]])
            if int(compared["changed_pixels"]) != 0:
                fail("compact-tree half-sine phase symmetry drifted in %s for %02d/%02d" % [context, phase_index, paired])
                return
            symmetry["%s/%02d-%02d" % [context, phase_index, paired]] = compared

    receipt["state"] = "PASS_COMPACT_EAST_TREE_17_PHASE_TARGET_VISUAL_RESPONSE"
    receipt["godot_version"] = Engine.get_version_info()
    receipt["vfx_head"] = exact_head
    receipt["migrated_neutral_mesh_digest"] = EXPECTED_NEUTRAL_DIGEST
    receipt["contexts"] = CONTEXTS
    receipt["phase_count"] = 17
    receipt["captures"] = captures
    receipt["neutral_return"] = neutral_return
    receipt["neutral_to_peak_visual_delta"] = neutral_to_peak
    receipt["phase_symmetry"] = symmetry
    receipt["truth_boundary"] = {
        "exact_compact_source_phase_meshes_consumed": true,
        "target_host_shape_motion_observed": true,
        "culling_disabled_for_response_isolation": true,
        "leaf_sidedness_or_final_materials_tested": false,
        "continuous_playback_or_wall_clock_timing_tested": false,
        "map_receiving_scene_tested": false,
        "declared_flex_zones_validated": false,
        "physical_wind_or_biomechanics": false,
        "gameplay_or_collision": false,
        "target_device_performance": false,
        "art_direction_acceptance": false,
        "canon_or_production_readiness": false,
    }
    write_receipt()
    quit(0)
