extends SceneTree

const GENERATED_DIR := "res://generated"
const OUTPUT_RECEIPT := "res://vfx-migrated-wind-godot-culling-receipt.json"
const BG := Color(0.025, 0.030, 0.036, 1.0)
const EXPECTED_MIGRATED_MESH_DIGEST := "47dd4d82651138299d05071df3e8a410f21f673ab8d42b936d7222eb5351b862"
const SAMPLE_IDS := ["0000", "0125", "0250", "0375", "0500"]
const SAMPLE_TIMES := {"0000": 0.0, "0125": 0.125, "0250": 0.25, "0375": 0.375, "0500": 0.5}
const CONTEXTS := ["ground_oblique", "high_oblique"]

var receipt := {
    "schema": "axm.nature-migrated-wind-godot-culling-observer/v0.1",
    "state": "NOT_RUN",
    "promotion_effect": "NONE",
    "renderer_boundary": "Godot 4.7.2 GL Compatibility. Exact migrated VFX sample meshes are transformed from Nature +Z-up to Godot +Y-up; the handedness-changing axis swap is paired with one triangle-winding reversal. Neutral unshaded material isolates target-host culling from lookdev.",
}

func sha256_file(path: String) -> String:
    var bytes := FileAccess.get_file_as_bytes(path)
    var ctx := HashingContext.new()
    ctx.start(HashingContext.HASH_SHA256)
    ctx.update(bytes)
    return ctx.finish().hex_encode()

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
    receipt["state"] = "FAIL_MIGRATED_WIND_GODOT_CULLING_PROOF"
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
        fail("migrated sample mesh lacks triangles or regions")
        return []
    var included := []
    included.resize(triangles.size())
    included.fill(false)
    for region_value in regions:
        if not (region_value is Dictionary):
            fail("Nature mesh region is not an object")
            return []
        var region := region_value as Dictionary
        var start := int(region.get("triangle_start", -1))
        var count := int(region.get("triangle_count", -1))
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
    var result := []
    for triangle_index in range(included.size()):
        if bool(included[triangle_index]):
            result.append(triangle_index)
    if result.is_empty():
        fail("woody-only proof selected zero triangles")
    return result

func build_woody_mesh(payload: Dictionary) -> Dictionary:
    var vertices = payload.get("vertices", [])
    var triangles = payload.get("triangles", [])
    if not (vertices is Array) or not (triangles is Array):
        fail("migrated sample mesh lacks vertex/triangle arrays")
        return {}
    var selected := woody_triangle_indices(payload)
    var surface := SurfaceTool.new()
    surface.begin(Mesh.PRIMITIVE_TRIANGLES)
    for triangle_index_value in selected:
        var triangle_index := int(triangle_index_value)
        var triangle = triangles[triangle_index]
        if not (triangle is Array) or triangle.size() != 3:
            fail("Nature triangle is malformed")
            return {}
        # Nature +Z-up -> Godot +Y-up swaps Y/Z and changes handedness.
        # Reversing one triangle edge restores the source front-face sense.
        for local_index in [0, 2, 1]:
            var vertex_index := int(triangle[local_index])
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
        fail("SurfaceTool failed to build woody migrated sample mesh")
        return {}
    return {
        "mesh": mesh,
        "woody_triangle_count": selected.size(),
        "source_triangle_count": triangles.size(),
        "excluded_leaf_triangle_count": triangles.size() - selected.size(),
    }

func proof_material(culling: String) -> StandardMaterial3D:
    var material := StandardMaterial3D.new()
    material.albedo_color = Color(0.57, 0.78, 0.47, 1.0)
    material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
    material.cull_mode = BaseMaterial3D.CULL_DISABLED if culling == "disabled" else BaseMaterial3D.CULL_BACK
    return material

func camera_spec(context: String) -> Dictionary:
    if context == "high_oblique":
        return {"position": Vector3(3.4, 4.3, 3.5), "target": Vector3(0.0, 1.95, 0.0), "fov": 40.0}
    return {"position": Vector3(3.9, 2.35, 4.4), "target": Vector3(0.0, 1.8, 0.0), "fov": 39.0}

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

func capture_sample(payload: Dictionary, sample_id: String, culling: String, context: String) -> Dictionary:
    var built := build_woody_mesh(payload)
    if built.is_empty():
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
    instance.mesh = built["mesh"]
    instance.material_override = proof_material(culling)
    root3d.add_child(instance)

    var camera := Camera3D.new()
    camera.near = 0.03
    camera.far = 25.0
    var spec := camera_spec(context)
    camera.fov = float(spec["fov"])
    root3d.add_child(camera)
    camera.look_at_from_position(spec["position"] as Vector3, spec["target"] as Vector3, Vector3.UP)
    camera.make_current()

    for _i in range(12):
        await process_frame
    var image := viewport.get_texture().get_image()
    if image == null or image.is_empty():
        fail("empty Godot migrated-wind capture")
        return {}
    var image_path := "res://wind-%s-%s-%s.png" % [sample_id, culling, context]
    if image.save_png(image_path) != OK:
        fail("could not save Godot migrated-wind capture")
        return {}
    var visible_pixels := changed_from_background(image)
    if visible_pixels < 250:
        fail("insufficient woody geometry in Godot migrated-wind capture: " + str(visible_pixels))
        return {}

    var record := {
        "sample_id": sample_id,
        "sample_time_s": SAMPLE_TIMES[sample_id],
        "culling": culling,
        "context": context,
        "capture_path": image_path,
        "capture_sha256": sha256_file(image_path),
        "capture_width": image.get_width(),
        "capture_height": image.get_height(),
        "visible_pixels": visible_pixels,
        "woody_triangle_count": int(built["woody_triangle_count"]),
        "source_triangle_count": int(built["source_triangle_count"]),
        "excluded_leaf_triangle_count": int(built["excluded_leaf_triangle_count"]),
    }
    viewport.queue_free()
    for _i in range(2):
        await process_frame
    return {"record": record, "image": image}

func _initialize() -> void:
    var summary := read_json(GENERATED_DIR + "/summary.json")
    var evidence := read_json(GENERATED_DIR + "/evidence.json")
    if summary.get("state") != "PASS_MIGRATED_TOPOLOGY_VISUAL_WIND_RESPONSE_REBIND":
        fail("migrated VFX source evidence is missing or not green")
        return
    if String(summary.get("migrated_neutral_mesh_digest", "")) != EXPECTED_MIGRATED_MESH_DIGEST:
        fail("migrated neutral mesh digest drifted before Godot proof")
        return
    if evidence.get("state") != "PASS_BOUNDED_VISUAL_WIND_RESPONSE":
        fail("underlying visual wind response evidence is missing or not green")
        return
    var exact_head_path := GENERATED_DIR + "/exact-head.txt"
    if not FileAccess.file_exists(exact_head_path):
        fail("exact VFX head binding is missing")
        return
    var exact_head := FileAccess.get_file_as_string(exact_head_path).strip_edges()

    var payloads := {}
    for sample_id in SAMPLE_IDS:
        var path := GENERATED_DIR + "/frame_" + sample_id + "ms_mesh.json"
        var payload := read_json(path)
        if payload.is_empty():
            fail("missing migrated sample payload: " + path)
            return
        payloads[sample_id] = payload

    var captures := {}
    var images := {}
    var expected_woody_triangles := -1
    var expected_leaf_triangles := -1
    for context in CONTEXTS:
        for sample_id in SAMPLE_IDS:
            for culling in ["disabled", "back"]:
                var result := await capture_sample(payloads[sample_id] as Dictionary, sample_id, culling, context)
                var key := "%s/%s/%s" % [context, sample_id, culling]
                captures[key] = result["record"]
                images[key] = result["image"]
                var record := result["record"] as Dictionary
                if expected_woody_triangles < 0:
                    expected_woody_triangles = int(record["woody_triangle_count"])
                    expected_leaf_triangles = int(record["excluded_leaf_triangle_count"])
                elif int(record["woody_triangle_count"]) != expected_woody_triangles or int(record["excluded_leaf_triangle_count"]) != expected_leaf_triangles:
                    fail("woody/leaf triangle partition drifted across wind samples")
                    return

    var culling_comparisons := {}
    for context in CONTEXTS:
        for sample_id in SAMPLE_IDS:
            var comparison := pixel_difference(images["%s/%s/disabled" % [context, sample_id]], images["%s/%s/back" % [context, sample_id]])
            if int(comparison["changed_pixels"]) != 0:
                fail("backface culling changed exact woody migrated-wind output in %s at %sms" % [context, sample_id])
                return
            culling_comparisons["%s/%s" % [context, sample_id]] = comparison

    var neutral_return := {}
    var neutral_to_peak := {}
    for context in CONTEXTS:
        var returned := pixel_difference(images["%s/0000/back" % context], images["%s/0500/back" % context])
        if int(returned["changed_pixels"]) != 0:
            fail("target-host exact neutral return drifted in " + context)
            return
        neutral_return[context] = returned
        var moved := pixel_difference(images["%s/0000/back" % context], images["%s/0250/back" % context])
        if int(moved["changed_pixels"]) <= 0:
            fail("target-host peak deformation is not visibly distinct in " + context)
            return
        neutral_to_peak[context] = moved

    receipt["state"] = "PASS_MIGRATED_WOODY_WIND_RESPONSE_GODOT_CULLING_STABILITY"
    receipt["godot_version"] = Engine.get_version_info()
    receipt["vfx_head"] = exact_head
    receipt["migrated_neutral_mesh_digest"] = EXPECTED_MIGRATED_MESH_DIGEST
    receipt["sample_ids"] = SAMPLE_IDS
    receipt["sample_times_s"] = [0.0, 0.125, 0.25, 0.375, 0.5]
    receipt["contexts"] = CONTEXTS
    receipt["woody_triangle_count"] = expected_woody_triangles
    receipt["excluded_leaf_triangle_count"] = expected_leaf_triangles
    receipt["captures"] = captures
    receipt["culling_comparisons"] = culling_comparisons
    receipt["neutral_return"] = neutral_return
    receipt["neutral_to_peak_visual_delta"] = neutral_to_peak
    receipt["truth_boundary"] = {
        "exact_migrated_vfx_sample_meshes_consumed": true,
        "woody_trunk_branch_geometry_tested": true,
        "leaf_geometry_included": false,
        "target_host_backface_culling_tested": true,
        "neutral_unshaded_material_only": true,
        "five_discrete_samples_only": true,
        "continuous_playback_or_timing_tested": false,
        "shaded_lookdev_tested": false,
        "map_receiving_scene_tested": false,
        "physical_wind_or_biomechanics": false,
        "gameplay_or_collision": false,
        "target_device_performance": false,
        "final_art_direction_or_visual_qa_acceptance": false,
    }
    receipt["non_claims"] = [
        "Pixel-identical cull-back versus culling-disabled frames prove only that no woody target-host culling loss was observed in these exact samples and cameras.",
        "Leaf blades are deliberately excluded because explicit leaf-sidedness is owned by the separate Geometry lane; this proof cannot grant leaf acceptance.",
        "The unshaded observer proves renderable dynamic shape reachability, not final shading, material, motion smoothness, physical wind, runtime performance, gameplay, CANON or production readiness.",
    ]
    write_receipt()
    print("AXM NATURE MIGRATED WIND GODOT CULLING ", JSON.stringify(receipt))
    quit(0)
