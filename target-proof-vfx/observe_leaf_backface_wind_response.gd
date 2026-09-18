extends SceneTree

const GENERATED_DIR := "res://generated-leaf"
const OUTPUT_RECEIPT := "res://vfx-leaf-backface-wind-godot-receipt.json"
const BG := Color(0.025, 0.030, 0.036, 1.0)
const EXPECTED_GEOMETRY_HEAD := "da3adbef4de8cddb8f3ebe841d39bb31a8936f5f"
const EXPECTED_LEAF_CANDIDATE_DIGEST := "e0b423bd4ff20251a960655441f97e36277da2f5b88a832ecfc5ccfe404bbbea"
const EXPECTED_MIGRATED_MESH_DIGEST := "47dd4d82651138299d05071df3e8a410f21f673ab8d42b936d7222eb5351b862"
const SAMPLE_IDS := ["0000", "0125", "0250", "0375", "0500"]
const SAMPLE_TIMES := {"0000": 0.0, "0125": 0.125, "0250": 0.25, "0375": 0.375, "0500": 0.5}
const CONTEXTS := ["ground_oblique", "crown_overhead"]

var receipt := {
    "schema": "axm.nature-dynamic-leaf-backface-godot-observer/v0.1",
    "state": "NOT_RUN",
    "promotion_effect": "NONE",
    "renderer_boundary": "Godot 4.7.2 GL Compatibility. Five exact VFX source states are compared with and without Geometry PR #10's disjoint opposite-wound leaf faces. Nature +Z-up is converted to Godot +Y-up with one winding reversal. Neutral unshaded opaque material isolates target-host backface coverage from lookdev.",
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
    receipt["state"] = "FAIL_DYNAMIC_EXPLICIT_LEAF_BACKFACE_GODOT_PROOF"
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
        fail("dynamic Nature sample lacks vertex/triangle arrays")
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
        fail("SurfaceTool failed to build dynamic Nature sample mesh")
        return {}
    return {"mesh": mesh, "vertex_count": vertices.size(), "triangle_count": triangles.size()}

func proof_material(culling: String) -> StandardMaterial3D:
    var material := StandardMaterial3D.new()
    material.albedo_color = Color(0.57, 0.78, 0.47, 1.0)
    material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
    material.cull_mode = BaseMaterial3D.CULL_DISABLED if culling == "disabled" else BaseMaterial3D.CULL_BACK
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

func capture_sample(payload: Dictionary, sample_id: String, mesh_kind: String, culling: String, context: String) -> Dictionary:
    var built := build_full_mesh(payload)
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
        fail("empty Godot dynamic leaf-backface capture")
        return {}
    var image_path := "res://leaf-%s-%s-%s-%s.png" % [sample_id, mesh_kind, culling, context]
    if image.save_png(image_path) != OK:
        fail("could not save Godot dynamic leaf-backface capture")
        return {}
    var visible_pixels := changed_from_background(image)
    if visible_pixels < 250:
        fail("insufficient Nature geometry in dynamic leaf-backface capture: " + str(visible_pixels))
        return {}
    var record := {
        "sample_id": sample_id,
        "sample_time_s": SAMPLE_TIMES[sample_id],
        "mesh_kind": mesh_kind,
        "culling": culling,
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
    var summary := read_json(GENERATED_DIR + "/leaf-dynamic-summary.json")
    if summary.get("state") != "PASS_EXPLICIT_LEAF_BACKFACE_WIND_RESPONSE_REBIND":
        fail("dynamic leaf-backface source evidence is missing or not green")
        return
    if String(summary.get("geometry_leaf_head", "")) != EXPECTED_GEOMETRY_HEAD:
        fail("Geometry leaf donor head drifted before Godot proof")
        return
    if String(summary.get("geometry_leaf_candidate_digest", "")) != EXPECTED_LEAF_CANDIDATE_DIGEST:
        fail("Geometry leaf candidate digest drifted before Godot proof")
        return
    if String(summary.get("migrated_neutral_mesh_digest", "")) != EXPECTED_MIGRATED_MESH_DIGEST:
        fail("migrated neutral sapling identity drifted before Godot proof")
        return
    if int(summary.get("front_vertices", -1)) != 390 or int(summary.get("front_triangles", -1)) != 570:
        fail("front mesh counts drifted before Godot proof")
        return
    if int(summary.get("candidate_vertices", -1)) != 490 or int(summary.get("candidate_triangles", -1)) != 620:
        fail("leaf-backface candidate counts drifted before Godot proof")
        return
    if float(summary.get("max_duplicate_position_gap_m", 1.0)) > 1e-12:
        fail("dynamic leaf duplicate positions detached before Godot proof")
        return
    if not bool(summary.get("negative_control_duplicate_drift_rejected", false)):
        fail("dynamic leaf duplicate negative control did not reject")
        return
    var exact_head_path := GENERATED_DIR + "/exact-head.txt"
    if not FileAccess.file_exists(exact_head_path):
        fail("exact VFX head binding is missing")
        return
    var exact_head := FileAccess.get_file_as_string(exact_head_path).strip_edges()
    var payloads := {}
    for sample_id_value in SAMPLE_IDS:
        var sample_id := String(sample_id_value)
        var front := read_json(GENERATED_DIR + "/frame_" + sample_id + "ms_front_mesh.json")
        var candidate := read_json(GENERATED_DIR + "/frame_" + sample_id + "ms_leaf_backface_mesh.json")
        if front.is_empty() or candidate.is_empty():
            fail("missing dynamic leaf-backface payload for sample " + sample_id)
            return
        payloads[sample_id + "/front"] = front
        payloads[sample_id + "/candidate"] = candidate

    var captures := {}
    var images := {}
    for context_value in CONTEXTS:
        var context := String(context_value)
        for sample_id_value in SAMPLE_IDS:
            var sample_id := String(sample_id_value)
            for mesh_kind_value in ["front", "candidate"]:
                var mesh_kind := String(mesh_kind_value)
                for culling_value in ["disabled", "back"]:
                    var culling := String(culling_value)
                    var result := await capture_sample(payloads[sample_id + "/" + mesh_kind] as Dictionary, sample_id, mesh_kind, culling, context)
                    if result.is_empty():
                        return
                    var key := "%s/%s/%s/%s" % [context, sample_id, mesh_kind, culling]
                    captures[key] = result["record"]
                    images[key] = result["image"]
                    var record := result["record"] as Dictionary
                    if mesh_kind == "front" and (int(record["vertex_count"]) != 390 or int(record["triangle_count"]) != 570):
                        fail("front target-host mesh counts drifted")
                        return
                    if mesh_kind == "candidate" and (int(record["vertex_count"]) != 490 or int(record["triangle_count"]) != 620):
                        fail("candidate target-host mesh counts drifted")
                        return

    var no_cull_equivalence := {}
    var candidate_culling_stability := {}
    var baseline_culling_loss := {}
    var candidate_recovery := {}
    var exact_recovery_to_no_cull_front := {}
    var total_baseline_loss := 0
    for context_value in CONTEXTS:
        var context := String(context_value)
        for sample_id_value in SAMPLE_IDS:
            var sample_id := String(sample_id_value)
            var prefix := "%s/%s" % [context, sample_id]
            var front_disabled := images[prefix + "/front/disabled"] as Image
            var front_back := images[prefix + "/front/back"] as Image
            var candidate_disabled := images[prefix + "/candidate/disabled"] as Image
            var candidate_back := images[prefix + "/candidate/back"] as Image
            var no_cull := pixel_difference(front_disabled, candidate_disabled)
            if int(no_cull["changed_pixels"]) != 0:
                fail("explicit leaf backfaces changed culling-disabled pixels in " + prefix)
                return
            no_cull_equivalence[prefix] = no_cull
            var stable := pixel_difference(candidate_disabled, candidate_back)
            if int(stable["changed_pixels"]) != 0:
                fail("explicit leaf-backface candidate still changes under backface culling in " + prefix)
                return
            candidate_culling_stability[prefix] = stable
            var loss := pixel_difference(front_disabled, front_back)
            baseline_culling_loss[prefix] = loss
            total_baseline_loss += int(loss["changed_pixels"])
            candidate_recovery[prefix] = pixel_difference(front_back, candidate_back)
            var exact_recovery := pixel_difference(front_disabled, candidate_back)
            if int(exact_recovery["changed_pixels"]) != 0:
                fail("explicit leaf-backface candidate did not restore the exact culling-disabled front result in " + prefix)
                return
            exact_recovery_to_no_cull_front[prefix] = exact_recovery

    var overhead_neutral_key := "crown_overhead/0000"
    if int((baseline_culling_loss[overhead_neutral_key] as Dictionary)["changed_pixels"]) <= 0:
        fail("crown overhead control did not expose the single-sided leaf culling gap")
        return
    if total_baseline_loss <= 0:
        fail("single-sided leaf baseline produced no renderer-visible culling loss")
        return

    var neutral_return := {}
    var neutral_to_peak := {}
    var mirrored_phase := {}
    for context_value in CONTEXTS:
        var context := String(context_value)
        var returned := pixel_difference(images[context + "/0000/candidate/back"] as Image, images[context + "/0500/candidate/back"] as Image)
        if int(returned["changed_pixels"]) != 0:
            fail("dynamic leaf-backface candidate lost exact neutral return in " + context)
            return
        neutral_return[context] = returned
        var moved := pixel_difference(images[context + "/0000/candidate/back"] as Image, images[context + "/0250/candidate/back"] as Image)
        if int(moved["changed_pixels"]) <= 0:
            fail("dynamic leaf-backface candidate peak is not visibly distinct in " + context)
            return
        neutral_to_peak[context] = moved
        var mirrored := pixel_difference(images[context + "/0125/candidate/back"] as Image, images[context + "/0375/candidate/back"] as Image)
        if int(mirrored["changed_pixels"]) != 0:
            fail("dynamic leaf-backface candidate broke exact half-sine mirrored phase identity in " + context)
            return
        mirrored_phase[context] = mirrored

    receipt["state"] = "PASS_DYNAMIC_EXPLICIT_LEAF_BACKFACE_GODOT_CULLING_RECOVERY"
    receipt["godot_version"] = Engine.get_version_info()
    receipt["vfx_head"] = exact_head
    receipt["geometry_leaf_head"] = EXPECTED_GEOMETRY_HEAD
    receipt["geometry_leaf_candidate_digest"] = EXPECTED_LEAF_CANDIDATE_DIGEST
    receipt["migrated_neutral_mesh_digest"] = EXPECTED_MIGRATED_MESH_DIGEST
    receipt["sample_ids"] = SAMPLE_IDS
    receipt["sample_times_s"] = [0.0, 0.125, 0.25, 0.375, 0.5]
    receipt["contexts"] = CONTEXTS
    receipt["captures"] = captures
    receipt["no_cull_front_vs_candidate"] = no_cull_equivalence
    receipt["candidate_culling_stability"] = candidate_culling_stability
    receipt["single_sided_baseline_culling_loss"] = baseline_culling_loss
    receipt["candidate_backface_recovery_delta"] = candidate_recovery
    receipt["candidate_back_equals_front_no_cull"] = exact_recovery_to_no_cull_front
    receipt["total_baseline_culling_loss_changed_pixels"] = total_baseline_loss
    receipt["neutral_return"] = neutral_return
    receipt["neutral_to_peak_visual_delta"] = neutral_to_peak
    receipt["mirrored_phase_visual_identity"] = mirrored_phase
    receipt["truth_boundary"] = {
        "exact_geometry_leaf_candidate_consumed": true,
        "exact_existing_vfx_response_consumed": true,
        "five_discrete_dynamic_states_tested": true,
        "real_godot_backface_culling_tested": true,
        "renderer_visible_leaf_backface_recovery_observed": true,
        "neutral_unshaded_opaque_material_only": true,
        "shaded_leaf_material_or_translucency_tested": false,
        "continuous_playback_or_wall_clock_timing_tested": false,
        "perceptual_natural_wind_or_final_visual_acceptance": false,
        "map_receiving_scene_tested": false,
        "physical_wind_or_biomechanics": false,
        "gameplay_or_collision": false,
        "runtime_cost_or_target_device_performance": false,
        "canon_or_production_readiness": false,
    }
    write_receipt()
    print(JSON.stringify(receipt))
    quit(0)
