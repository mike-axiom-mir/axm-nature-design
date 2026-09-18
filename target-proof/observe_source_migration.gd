extends SceneTree

const RECEIPT_PATH := "res://generated/uc-source-migration-rebind-overall.json"
const HISTORICAL_GLB := "res://generated/east-rear-tree-neutral-001-historical.glb"
const MIGRATED_GLB := "res://generated/east-rear-tree-neutral-001-source-migrated.glb"
const OUTPUT_RECEIPT := "res://nature-rear-tree-source-migration-culling-receipt.json"
const BG := Color(0.025, 0.030, 0.036, 1.0)

var receipt := {
    "schema": "axm.nature-uc-source-migration-godot-culling-observer/v0.1",
    "state": "NOT_RUN",
    "promotion_effect": "NONE",
    "renderer_boundary": "Godot 4.7.2 GL Compatibility runtime GLTFDocument import of exact current-UC GLBs. Neutral unshaded material overrides isolate target-host culling from lookdev."
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
    receipt["state"] = "FAIL_SOURCE_MIGRATION_TARGET_CULLING_PROOF"
    receipt["failure"] = message
    write_receipt()
    push_error(message)
    quit(1)

func imported_scene(path: String) -> Node3D:
    if not FileAccess.file_exists(path):
        fail("missing exact UC GLB: " + path)
        return Node3D.new()
    var document := GLTFDocument.new()
    var state := GLTFState.new()
    var error := document.append_from_file(path, state)
    if error != OK:
        fail("GLTFDocument append_from_file failed for " + path + ": " + str(error))
        return Node3D.new()
    var generated = document.generate_scene(state)
    if generated == null or not (generated is Node3D):
        fail("GLTFDocument generate_scene returned no Node3D for " + path)
        return Node3D.new()
    return generated as Node3D

func proof_material(culling: String) -> StandardMaterial3D:
    var material := StandardMaterial3D.new()
    material.albedo_color = Color(0.56, 0.82, 0.49, 1.0)
    material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
    material.cull_mode = BaseMaterial3D.CULL_DISABLED if culling == "disabled" else BaseMaterial3D.CULL_BACK
    return material

func inspect_and_override(node: Node, culling: String, stats: Dictionary) -> void:
    if node is MeshInstance3D:
        var instance := node as MeshInstance3D
        var mesh := instance.mesh
        if mesh == null:
            fail("MeshInstance3D has no mesh: " + instance.name)
            return
        instance.material_override = proof_material(culling)
        stats["mesh_instances"] = int(stats["mesh_instances"]) + 1
        stats["mesh_names"].append(String(instance.name))
        for surface_index in range(mesh.get_surface_count()):
            if mesh.surface_get_primitive_type(surface_index) != Mesh.PRIMITIVE_TRIANGLES:
                fail("imported surface is not triangles")
                return
            var arrays := mesh.surface_get_arrays(surface_index)
            var indices = arrays[Mesh.ARRAY_INDEX]
            var vertices = arrays[Mesh.ARRAY_VERTEX]
            if indices != null and indices.size() > 0:
                if indices.size() % 3 != 0:
                    fail("imported index count is not divisible by three")
                    return
                stats["triangles"] = int(stats["triangles"]) + int(indices.size() / 3)
            else:
                if vertices == null or vertices.size() % 3 != 0:
                    fail("unindexed triangle surface has invalid vertex count")
                    return
                stats["triangles"] = int(stats["triangles"]) + int(vertices.size() / 3)
            stats["surfaces"] = int(stats["surfaces"]) + 1
    for child in node.get_children():
        inspect_and_override(child, culling, stats)

func camera_spec(context: String) -> Dictionary:
    if context == "high_oblique":
        return {"position": Vector3(4.4, 5.1, 4.0), "target": Vector3(0.0, 2.15, 0.0), "fov": 39.0}
    return {"position": Vector3(4.8, 2.55, 5.0), "target": Vector3(0.0, 2.05, 0.0), "fov": 38.0}

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

func capture_variant(variant: String, culling: String, context: String, path: String, expected_triangles: int) -> Dictionary:
    var scene := imported_scene(path)
    var stats := {"mesh_instances": 0, "surfaces": 0, "triangles": 0, "mesh_names": []}
    inspect_and_override(scene, culling, stats)
    stats["mesh_names"].sort()
    if int(stats["triangles"]) != expected_triangles:
        fail("target-host triangle count drift for " + variant + "/" + culling + "/" + context)
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
    root3d.add_child(scene)

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
        fail("empty target-host capture")
        return {}
    var image_path := "res://source-migration-%s-%s-%s.png" % [variant, culling, context]
    if image.save_png(image_path) != OK:
        fail("could not save target-host capture")
        return {}
    var visible_pixels := changed_from_background(image)
    if visible_pixels < 1500:
        fail("insufficient visible geometry in target-host capture")
        return {}

    var result := {
        "variant": variant,
        "culling": culling,
        "context": context,
        "glb_path": path,
        "glb_sha256": sha256_file(path),
        "imported": stats,
        "capture_path": image_path,
        "capture_sha256": sha256_file(image_path),
        "capture_width": image.get_width(),
        "capture_height": image.get_height(),
        "visible_pixels": visible_pixels,
    }
    viewport.queue_free()
    for _i in range(2):
        await process_frame
    return {"record": result, "image": image}

func _initialize() -> void:
    var source := read_json(RECEIPT_PATH)
    if source.get("state") != "PASS_SOURCE_GENERATED_MIGRATED_NATURE_THROUGH_CURRENT_UC_GLB":
        fail("source-migration UC rebind receipt missing or not green")
        return
    var studies = source.get("studies", {}) as Dictionary
    var study = studies.get("east-rear-tree-neutral-001", {}) as Dictionary
    var historical = source.get("historical_rear", {}) as Dictionary
    if study.is_empty() or historical.is_empty():
        fail("rear-tree source-migration evidence is incomplete")
        return

    var migrated_glb = study.get("uc_glb", {}) as Dictionary
    var historical_glb = historical.get("uc_glb", {}) as Dictionary
    var expected_triangles := int((migrated_glb.get("verification", {}) as Dictionary).get("triangles", -1))
    if expected_triangles <= 0 or expected_triangles != int((historical_glb.get("verification", {}) as Dictionary).get("triangles", -2)):
        fail("historical/migrated UC triangle counts differ")
        return
    if sha256_file(HISTORICAL_GLB) != String(historical_glb.get("glb_sha256", "")):
        fail("historical exact UC GLB byte identity mismatch")
        return
    if sha256_file(MIGRATED_GLB) != String(migrated_glb.get("glb_sha256", "")):
        fail("source-migrated exact UC GLB byte identity mismatch")
        return

    var captures := {}
    var images := {}
    for context in ["ground_oblique", "high_oblique"]:
        for culling in ["disabled", "back"]:
            for variant in ["historical", "source_migrated"]:
                var glb_path := HISTORICAL_GLB if variant == "historical" else MIGRATED_GLB
                var result := await capture_variant(variant, culling, context, glb_path, expected_triangles)
                var key := "%s/%s/%s" % [context, culling, variant]
                captures[key] = result["record"]
                images[key] = result["image"]

    var comparisons := {}
    for context in ["ground_oblique", "high_oblique"]:
        var historical_vs_migrated_disabled := pixel_difference(images["%s/disabled/historical" % context], images["%s/disabled/source_migrated" % context])
        var historical_vs_migrated_back := pixel_difference(images["%s/back/historical" % context], images["%s/back/source_migrated" % context])
        var migrated_back_vs_disabled := pixel_difference(images["%s/back/source_migrated" % context], images["%s/disabled/source_migrated" % context])
        var historical_back_vs_disabled := pixel_difference(images["%s/back/historical" % context], images["%s/disabled/historical" % context])
        if int(historical_vs_migrated_disabled["changed_pixels"]) != 0:
            fail("source migration changed culling-disabled target pixels in " + context)
            return
        if int(historical_vs_migrated_back["changed_pixels"]) <= 0:
            fail("backface culling did not distinguish historical/source-migrated output in " + context)
            return
        if int(migrated_back_vs_disabled["changed_pixels"]) != 0:
            fail("source-migrated output still loses pixels under backface culling in " + context)
            return
        if int(historical_back_vs_disabled["changed_pixels"]) <= 0:
            fail("historical baseline no longer reproduces culling loss in " + context)
            return
        comparisons[context] = {
            "culling_disabled_historical_vs_source_migrated": historical_vs_migrated_disabled,
            "culling_back_historical_vs_source_migrated": historical_vs_migrated_back,
            "source_migrated_back_vs_disabled": migrated_back_vs_disabled,
            "historical_back_vs_disabled": historical_back_vs_disabled,
        }

    receipt["state"] = "PASS_SOURCE_GENERATED_MIGRATION_TARGET_CULLING_REPRODUCED"
    receipt["godot_version"] = Engine.get_version_info()
    receipt["receiving_head"] = source.get("receiving_head")
    receipt["source_migration_commit"] = source.get("source_migration_commit")
    receipt["historical_rear_commit"] = source.get("historical_rear_commit")
    receipt["uc_commit"] = source.get("uc_commit")
    receipt["study_id"] = "east-rear-tree-neutral-001"
    receipt["historical_mesh_digest"] = historical.get("mesh_digest")
    receipt["source_generated_migrated_mesh_digest"] = study.get("source_generated_migrated_mesh_digest")
    receipt["expected_triangles"] = expected_triangles
    receipt["captures"] = captures
    receipt["comparisons"] = comparisons
    receipt["truth_boundary"] = {
        "exact_source_generated_migrated_bytes_consumed": true,
        "exact_current_uc_glb_bytes_imported": true,
        "exact_triangle_count_preserved": true,
        "historical_culling_defect_reproduced": true,
        "source_migrated_backface_capture_matches_culling_disabled_control": true,
        "map_receiving_scene_tested": false,
        "global_outward_normal_correctness_proved": false,
        "final_material_or_art_direction_acceptance": false,
        "wind_or_deformation": false,
        "target_device_performance": false,
        "collision_or_gameplay": false
    }
    receipt["non_claims"] = [
        "This observer closes the Technical Art source-generated transport/culling rebind for the exact rear migration only; it does not merge the source PR or alter Map adoption authority.",
        "Two retained isolated cameras do not prove global outward-normal correctness or future procedural variants.",
        "Neutral unshaded overrides intentionally exclude material/lookdev judgments.",
    ]
    write_receipt()
    print("AXM NATURE UC SOURCE MIGRATION TARGET CULLING ", JSON.stringify(receipt))
    quit(0)
