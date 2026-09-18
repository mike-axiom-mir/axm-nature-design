extends SceneTree

const GENERATED_DIR := "res://generated-flutter"
const OUTPUT_RECEIPT := "res://vfx-leaf-flutter-godot-receipt.json"
const BG := Color(0.025, 0.030, 0.036, 1.0)
const EXPECTED_GEOMETRY_HEAD := "da3adbef4de8cddb8f3ebe841d39bb31a8936f5f"
const EXPECTED_LEAF_CANDIDATE_DIGEST := "e0b423bd4ff20251a960655441f97e36277da2f5b88a832ecfc5ccfe404bbbea"
const EXPECTED_MIGRATED_MESH_DIGEST := "47dd4d82651138299d05071df3e8a410f21f673ab8d42b936d7222eb5351b862"
const PHASE_COUNT := 17
const CONTEXTS := ["ground_oblique", "crown_overhead"]

var receipt := {
    "schema": "axm.nature-leaf-flutter-godot-observer/v0.1",
    "state": "NOT_RUN",
    "promotion_effect": "NONE",
    "renderer_boundary": "Godot 4.7.2 GL Compatibility. Seventeen direct visual-source phases compare the inherited explicit two-sided leaf candidate with and without the bounded deterministic leaf-plane twist. Unshaded opaque material isolates renderer-visible motion from lookdev.",
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
    receipt["state"] = "FAIL_BOUNDED_LEAF_FLUTTER_GODOT_VISUAL_CANDIDATE"
    receipt["failure"] = message
    write_receipt()
    push_error(message)
    quit(1)

func source_to_godot(point: Array) -> Vector3:
    if point.size() != 3:
        fail("Nature vertex does not contain exactly three coordinates")
        return Vector3.ZERO
    return Vector3(float(point[0]), float(point[2]), float(point[1]))

func build_full_mesh(payload: Dictionary) -> Dictionary:
    var vertices = payload.get("vertices", [])
    var triangles = payload.get("triangles", [])
    if not (vertices is Array) or not (triangles is Array) or vertices.is_empty() or triangles.is_empty():
        fail("leaf flutter payload lacks vertex/triangle arrays")
        return {}
    var surface := SurfaceTool.new()
    surface.begin(Mesh.PRIMITIVE_TRIANGLES)
    for triangle_value in triangles:
        if not (triangle_value is Array):
            fail("Nature triangle is not an array")
            return {}
        var triangle := triangle_value as Array
        if triangle.size() != 3:
            fail("Nature triangle is malformed")
            return {}
        for local_index in [0, 2, 1]:
            var vertex_index := int(triangle[local_index])
            if vertex_index < 0 or vertex_index >= vertices.size():
                fail("Nature triangle index is out of range")
                return {}
            var point = vertices[vertex_index]
            if not (point is Array):
                fail("Nature vertex is malformed")
                return {}
            surface.add_vertex(source_to_godot(point as Array))
    surface.generate_normals()
    var mesh := surface.commit()
    if mesh == null:
        fail("SurfaceTool failed to build leaf flutter mesh")
        return {}
    return {"mesh": mesh, "vertex_count": vertices.size(), "triangle_count": triangles.size()}

func proof_material() -> StandardMaterial3D:
    var material := StandardMaterial3D.new()
    material.albedo_color = Color(0.57, 0.78, 0.47, 1.0)
    material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
    material.cull_mode = BaseMaterial3D.CULL_BACK
    return material

func camera_spec(context: String) -> Dictionary:
    if context == "crown_overhead":
        return {"position": Vector3(2.8, 6.2, 2.8), "target": Vector3(0.0, 3.55, 0.0), "fov": 43.0}
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
        return {"comparable": false, "changed_pixels": -1, "max_channel_delta": 1.0, "mean_abs_rgb": 1.0}
    var changed := 0
    var max_delta := 0.0
    var total_abs_rgb := 0.0
    var pixel_count := first.get_width() * first.get_height()
    for y in range(first.get_height()):
        for x in range(first.get_width()):
            var a := first.get_pixel(x, y)
            var b := second.get_pixel(x, y)
            var dr := absf(a.r - b.r)
            var dg := absf(a.g - b.g)
            var db := absf(a.b - b.b)
            var delta: float = maxf(dr, maxf(dg, db))
            max_delta = maxf(max_delta, delta)
            total_abs_rgb += (dr + dg + db) / 3.0
            if delta > 0.0:
                changed += 1
    return {
        "comparable": true,
        "changed_pixels": changed,
        "max_channel_delta": max_delta,
        "mean_abs_rgb": total_abs_rgb / float(maxi(pixel_count, 1)),
    }

func capture_sample(payload: Dictionary, phase_index: int, kind: String, context: String) -> Dictionary:
    var built := build_full_mesh(payload)
    if built.is_empty():
        return {}
    if int(built["vertex_count"]) != 490 or int(built["triangle_count"]) != 620:
        fail("explicit two-sided leaf candidate counts drifted on target host")
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

    for _i in range(10):
        await process_frame

    var image := viewport.get_texture().get_image()
    if image == null or image.is_empty():
        fail("empty Godot leaf flutter capture")
        return {}

    var phase_id := "%02d" % phase_index
    var image_path := "res://flutter-%s-%s-%s.png" % [phase_id, kind, context]
    if image.save_png(image_path) != OK:
        fail("could not save Godot leaf flutter capture")
        return {}

    var visible_pixels := changed_from_background(image)
    if visible_pixels < 250:
        fail("insufficient sapling geometry in leaf flutter capture: " + str(visible_pixels))
        return {}

    var record := {
        "phase_index": phase_index,
        "kind": kind,
        "context": context,
        "capture_path": image_path,
        "capture_sha256": sha256_file(image_path),
        "capture_width": image.get_width(),
        "capture_height": image.get_height(),
        "visible_pixels": visible_pixels,
        "vertex_count": int(built["vertex_count"]),
        "triangle_count": int(built["triangle_count"]),
    }

    viewport.queue_free()
    for _i in range(2):
        await process_frame
    return {"record": record, "image": image}

func _initialize() -> void:
    var summary := read_json(GENERATED_DIR + "/leaf-flutter-summary.json")
    if summary.get("state") != "PASS_BOUNDED_DETERMINISTIC_LEAF_FLUTTER_SOURCE_CANDIDATE":
        fail("leaf flutter source evidence is missing or not green")
        return
    if String(summary.get("geometry_leaf_head", "")) != EXPECTED_GEOMETRY_HEAD:
        fail("Geometry leaf donor head drifted before Godot proof")
        return
    if String(summary.get("geometry_leaf_candidate_digest", "")) != EXPECTED_LEAF_CANDIDATE_DIGEST:
        fail("Geometry leaf candidate identity drifted before Godot proof")
        return
    if String(summary.get("migrated_neutral_mesh_digest", "")) != EXPECTED_MIGRATED_MESH_DIGEST:
        fail("migrated neutral sapling identity drifted before Godot proof")
        return
    if int(summary.get("leaf_count", -1)) != 25:
        fail("leaf count drifted before Godot proof")
        return
    if float(summary.get("max_observed_non_leaf_vertex_delta_m", 1.0)) > 1e-12:
        fail("leaf flutter candidate moved non-leaf geometry")
        return
    if float(summary.get("max_observed_duplicate_position_gap_m", 1.0)) > 1e-12:
        fail("leaf flutter candidate detached explicit backfaces")
        return
    if not bool(summary.get("negative_control_duplicate_detachment_rejected", false)):
        fail("leaf flutter source negative control did not reject")
        return

    var effect = summary.get("effect", {})
    if not (effect is Dictionary):
        fail("leaf flutter effect metadata is missing")
        return
    var effect_dict := effect as Dictionary
    if int(effect_dict.get("dense_phase_count", -1)) != PHASE_COUNT:
        fail("leaf flutter phase count drifted")
        return
    if absf(float(effect_dict.get("max_twist_deg", -1.0)) - 5.0) > 1e-12:
        fail("leaf flutter twist cap drifted")
        return

    var exact_head_path := GENERATED_DIR + "/exact-head.txt"
    if not FileAccess.file_exists(exact_head_path):
        fail("exact VFX head binding is missing")
        return
    var exact_head := FileAccess.get_file_as_string(exact_head_path).strip_edges()

    var payloads := {}
    var samples = summary.get("samples", [])
    if not (samples is Array):
        fail("leaf flutter sample metadata is malformed")
        return
    var samples_array := samples as Array
    if samples_array.size() != PHASE_COUNT:
        fail("leaf flutter sample count is not 17")
        return
    for sample_value in samples_array:
        if not (sample_value is Dictionary):
            fail("leaf flutter sample entry is malformed")
            return
        var sample := sample_value as Dictionary
        var phase_index := int(sample.get("index", -1))
        if phase_index < 0 or phase_index >= PHASE_COUNT:
            fail("leaf flutter phase index is out of range")
            return
        var phase_id := "%02d" % phase_index
        var baseline := read_json(GENERATED_DIR + "/phase_" + phase_id + "_baseline_candidate_mesh.json")
        var flutter := read_json(GENERATED_DIR + "/phase_" + phase_id + "_flutter_candidate_mesh.json")
        if baseline.is_empty() or flutter.is_empty():
            fail("missing leaf flutter payload for phase " + phase_id)
            return
        payloads[phase_id + "/baseline"] = baseline
        payloads[phase_id + "/flutter"] = flutter

    var captures := {}
    var images := {}
    for context_value in CONTEXTS:
        var context := String(context_value)
        for phase_index in range(PHASE_COUNT):
            var phase_id := "%02d" % phase_index
            for kind_value in ["baseline", "flutter"]:
                var kind := String(kind_value)
                var result := await capture_sample(
                    payloads[phase_id + "/" + kind] as Dictionary,
                    phase_index,
                    kind,
                    context
                )
                if result.is_empty():
                    return
                var key := "%s/%s/%s" % [context, phase_id, kind]
                captures[key] = result["record"]
                images[key] = result["image"]

    var effect_delta := {}
    var interior_visible_counts := {}
    var max_changed_pixels := {}
    var max_mean_abs_rgb := {}
    for context_value in CONTEXTS:
        var context := String(context_value)
        var visible_interior := 0
        var max_changed := 0
        var max_mean := 0.0
        for phase_index in range(PHASE_COUNT):
            var phase_id := "%02d" % phase_index
            var delta := pixel_difference(
                images[context + "/" + phase_id + "/baseline"] as Image,
                images[context + "/" + phase_id + "/flutter"] as Image
            )
            effect_delta[context + "/" + phase_id] = delta
            max_changed = maxi(max_changed, int(delta["changed_pixels"]))
            max_mean = maxf(max_mean, float(delta["mean_abs_rgb"]))
            if phase_index == 0 or phase_index == PHASE_COUNT - 1:
                if int(delta["changed_pixels"]) != 0:
                    fail("leaf flutter is not exact-neutral at endpoint " + context + "/" + phase_id)
                    return
            elif int(delta["changed_pixels"]) > 0:
                visible_interior += 1
        interior_visible_counts[context] = visible_interior
        max_changed_pixels[context] = max_changed
        max_mean_abs_rgb[context] = max_mean
        if int((effect_delta[context + "/08"] as Dictionary)["changed_pixels"]) <= 0:
            fail("bounded leaf flutter is not renderer-visible at the midpoint in " + context)
            return

    var neutral_return := {}
    for context_value in CONTEXTS:
        var context := String(context_value)
        var returned := pixel_difference(
            images[context + "/00/flutter"] as Image,
            images[context + "/16/flutter"] as Image
        )
        if int(returned["changed_pixels"]) != 0:
            fail("leaf flutter candidate lost exact neutral return in " + context)
            return
        neutral_return[context] = returned

    var adjacent_flutter := {}
    for context_value in CONTEXTS:
        var context := String(context_value)
        var changed_steps := 0
        for phase_index in range(PHASE_COUNT - 1):
            var a_id := "%02d" % phase_index
            var b_id := "%02d" % (phase_index + 1)
            var delta := pixel_difference(
                images[context + "/" + a_id + "/flutter"] as Image,
                images[context + "/" + b_id + "/flutter"] as Image
            )
            adjacent_flutter[context + "/" + a_id + "->" + b_id] = delta
            if int(delta["changed_pixels"]) > 0:
                changed_steps += 1
        if changed_steps != PHASE_COUNT - 1:
            fail("leaf flutter receiver contains an unchanged adjacent phase in " + context)
            return

    receipt = {
        "schema": "axm.nature-leaf-flutter-godot-observer/v0.1",
        "state": "PASS_BOUNDED_DETERMINISTIC_LEAF_FLUTTER_GODOT_VISUAL_CANDIDATE",
        "promotion_effect": "NONE",
        "vfx_head": exact_head,
        "geometry_leaf_head": EXPECTED_GEOMETRY_HEAD,
        "geometry_leaf_candidate_digest": EXPECTED_LEAF_CANDIDATE_DIGEST,
        "migrated_neutral_mesh_digest": EXPECTED_MIGRATED_MESH_DIGEST,
        "phase_count": PHASE_COUNT,
        "phase_step_s": float(effect_dict.get("phase_step_s", -1.0)),
        "contexts": CONTEXTS,
        "captures": captures,
        "effect_delta_baseline_vs_flutter": effect_delta,
        "interior_renderer_visible_phase_counts": interior_visible_counts,
        "max_changed_pixels_baseline_vs_flutter": max_changed_pixels,
        "max_mean_abs_rgb_baseline_vs_flutter": max_mean_abs_rgb,
        "neutral_return": neutral_return,
        "adjacent_flutter_phase_delta": adjacent_flutter,
        "source_max_observed_flutter_vertex_delta_m": float(summary.get("max_observed_flutter_vertex_delta_m", -1.0)),
        "source_max_observed_abs_twist_deg": float(summary.get("max_observed_abs_twist_deg", -1.0)),
        "renderer_boundary": receipt["renderer_boundary"],
        "truth_boundary": {
            "existing_wind_response_reauthored": false,
            "geometry_leaf_candidate_reauthored": false,
            "real_godot_renderer_visibility_tested": true,
            "bounded_leaf_local_twist_renderer_visible": true,
            "unshaded_opaque_proof_material_only": true,
            "shaded_leaf_material_or_translucency_tested": false,
            "perceptual_naturalness_or_final_art_acceptance": false,
            "continuous_interpolation_or_wall_clock_timing_tested": false,
            "physical_wind_or_biomechanics": false,
            "gameplay_or_collision": false,
            "runtime_cost_or_target_device_performance": false,
            "map_receiving_scene_equivalence": false,
            "canon_or_production_readiness": false,
        },
    }
    write_receipt()
    print("PASS_BOUNDED_DETERMINISTIC_LEAF_FLUTTER_GODOT_VISUAL_CANDIDATE")
    quit(0)
