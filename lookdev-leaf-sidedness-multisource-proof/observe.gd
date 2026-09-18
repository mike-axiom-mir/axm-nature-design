extends SceneTree

const DATA_PATH := "res://generated/comparison.json"
const RECEIPT_PATH := "res://leaf-sidedness-multisource-runtime-receipt.json"
const CONTEXTS := ["whole_three_quarter", "crown_back", "crown_low_grazing"]

var receipt := {
    "schema": "axm.nature-leaf-sidedness-material-multisource-runtime/v0.2",
    "promotion_effect": "NONE",
    "truth_boundary": "Pinned Godot 4.7.2 GL Compatibility observation of three exact Nature source forms comparing material-level disabled foliage culling against explicit opposite-wound leaf backface geometry while scalar review materials, lighting, and camera derivation are held fixed within each source/context. This does not widen the sapling material profile to other sources and does not prove final normals, final leaf shader, botanical correctness, runtime cost acceptance, Map/VFX acceptance, CANON, production readiness, or Materials mastery."
}

func write_receipt() -> void:
    var file := FileAccess.open(RECEIPT_PATH, FileAccess.WRITE)
    if file != null:
        file.store_string(JSON.stringify(receipt, "  ") + "\n")
        file.close()

func fail(message: String) -> void:
    receipt["state"] = "FAIL_INFRASTRUCTURE"
    receipt["failure"] = message
    write_receipt()
    push_error(message)
    quit(1)

func load_data() -> Dictionary:
    if not FileAccess.file_exists(DATA_PATH):
        return {}
    var parsed = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
    return parsed as Dictionary if parsed is Dictionary else {}

func source_to_godot(values: Array) -> Vector3:
    return Vector3(float(values[0]), float(values[2]), -float(values[1]))

func parse_hex_color(value: String) -> Color:
    var text := value.trim_prefix("#")
    if text.length() != 8:
        return Color(1, 0, 1, 1)
    return Color(
        float(text.substr(0, 2).hex_to_int()) / 255.0,
        float(text.substr(2, 2).hex_to_int()) / 255.0,
        float(text.substr(4, 2).hex_to_int()) / 255.0,
        float(text.substr(6, 2).hex_to_int()) / 255.0
    )

func material_from_payload(payload: Dictionary, cull_mode: int) -> StandardMaterial3D:
    var material := StandardMaterial3D.new()
    material.albedo_color = parse_hex_color(String(payload["color"]))
    material.metallic = float(payload["metallic"])
    material.roughness = float(payload["roughness"])
    material.cull_mode = cull_mode
    return material

func triangle_kinds(mesh: Dictionary) -> Array:
    var triangles := mesh["triangles"] as Array
    var kinds := []
    kinds.resize(triangles.size())
    for region_value in mesh["regions"] as Array:
        var region := region_value as Dictionary
        var start := int(region["triangle_start"])
        var count := int(region["triangle_count"])
        var kind := String(region["kind"])
        for index in range(start, start + count):
            if index < 0 or index >= kinds.size() or kinds[index] != null:
                return []
            kinds[index] = kind
    for value in kinds:
        if value == null:
            return []
    return kinds

func add_triangle(st: SurfaceTool, vertices: Array, triangle: Array) -> void:
    var a := source_to_godot(vertices[int(triangle[0])] as Array)
    var b := source_to_godot(vertices[int(triangle[1])] as Array)
    var c := source_to_godot(vertices[int(triangle[2])] as Array)
    var normal := (b - a).cross(c - a).normalized()
    for point in [a, b, c]:
        st.set_normal(normal)
        st.add_vertex(point)

func add_tree(root3d: Node3D, mesh: Dictionary, profile: Dictionary, strategy: String) -> Dictionary:
    var kinds := triangle_kinds(mesh)
    if kinds.is_empty():
        return {"state": "FAIL_REGION_OWNERSHIP"}
    var triangles := mesh["triangles"] as Array
    var vertices := mesh["vertices"] as Array
    var woody_st := SurfaceTool.new()
    var foliage_st := SurfaceTool.new()
    woody_st.begin(Mesh.PRIMITIVE_TRIANGLES)
    foliage_st.begin(Mesh.PRIMITIVE_TRIANGLES)
    var woody_triangles := 0
    var foliage_triangles := 0
    for triangle_index in range(triangles.size()):
        var kind := String(kinds[triangle_index])
        var is_foliage := kind.begins_with("leaf-blade")
        if is_foliage:
            add_triangle(foliage_st, vertices, triangles[triangle_index] as Array)
            foliage_triangles += 1
        else:
            add_triangle(woody_st, vertices, triangles[triangle_index] as Array)
            woody_triangles += 1

    var materials := profile["materials"] as Dictionary
    var woody_node := MeshInstance3D.new()
    woody_node.name = "%s-woody" % strategy
    woody_node.mesh = woody_st.commit()
    woody_node.material_override = material_from_payload(materials["woody"] as Dictionary, BaseMaterial3D.CULL_BACK)
    root3d.add_child(woody_node)

    var foliage_node := MeshInstance3D.new()
    foliage_node.name = "%s-foliage" % strategy
    foliage_node.mesh = foliage_st.commit()
    var foliage_cull := BaseMaterial3D.CULL_DISABLED if strategy == "material_twosided" else BaseMaterial3D.CULL_BACK
    foliage_node.material_override = material_from_payload(materials["foliage"] as Dictionary, foliage_cull)
    root3d.add_child(foliage_node)

    return {
        "state": "PASS",
        "strategy": strategy,
        "vertices": vertices.size(),
        "triangles": triangles.size(),
        "woody_triangles": woody_triangles,
        "foliage_triangles": foliage_triangles,
        "foliage_cull_mode": "CULL_DISABLED" if strategy == "material_twosided" else "CULL_BACK"
    }

func add_environment(root3d: Node3D) -> void:
    var env := Environment.new()
    env.background_mode = Environment.BG_COLOR
    env.background_color = Color(0.055, 0.065, 0.08, 1.0)
    env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
    env.ambient_light_color = Color(0.58, 0.62, 0.68, 1.0)
    env.ambient_light_energy = 0.58
    var world := WorldEnvironment.new()
    world.environment = env
    root3d.add_child(world)

    var key := DirectionalLight3D.new()
    key.light_energy = 1.5
    key.rotation_degrees = Vector3(-48, -32, 0)
    key.shadow_enabled = true
    root3d.add_child(key)

    var fill := DirectionalLight3D.new()
    fill.light_energy = 0.42
    fill.light_color = Color(0.62, 0.72, 0.92, 1.0)
    fill.rotation_degrees = Vector3(-22, 142, 0)
    root3d.add_child(fill)

func mesh_bounds(mesh: Dictionary) -> Dictionary:
    var vertices := mesh["vertices"] as Array
    if vertices.is_empty():
        return {}
    var first := source_to_godot(vertices[0] as Array)
    var min_v := first
    var max_v := first
    for raw in vertices:
        var point := source_to_godot(raw as Array)
        min_v.x = minf(min_v.x, point.x)
        min_v.y = minf(min_v.y, point.y)
        min_v.z = minf(min_v.z, point.z)
        max_v.x = maxf(max_v.x, point.x)
        max_v.y = maxf(max_v.y, point.y)
        max_v.z = maxf(max_v.z, point.z)
    return {"min": min_v, "max": max_v}

func camera_pose(context_name: String, mesh: Dictionary) -> Dictionary:
    var bounds := mesh_bounds(mesh)
    var min_v := bounds["min"] as Vector3
    var max_v := bounds["max"] as Vector3
    var center := (min_v + max_v) * 0.5
    var height: float = maxf(max_v.y - min_v.y, 0.5)
    if context_name == "whole_three_quarter":
        var target := Vector3(center.x, min_v.y + height * 0.52, center.z)
        return {"position": target + Vector3(height * 1.18, height * 0.23, height * 1.58), "target": target, "fov": 47.0}
    if context_name == "crown_back":
        var target := Vector3(center.x, min_v.y + height * 0.82, center.z)
        return {"position": target + Vector3(-height * 0.66, height * 0.12, -height * 0.98), "target": target, "fov": 43.0}
    var target := Vector3(center.x, min_v.y + height * 0.80, center.z)
    return {"position": target + Vector3(height * 0.86, -height * 0.18, height * 0.50), "target": target, "fov": 42.0}

func capture(study_id: String, context_name: String, strategy: String, study_data: Dictionary, profile: Dictionary) -> Dictionary:
    var viewport := SubViewport.new()
    viewport.size = Vector2i(720, 560)
    viewport.own_world_3d = true
    viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
    viewport.render_target_clear_mode = SubViewport.CLEAR_MODE_ALWAYS
    get_root().add_child(viewport)

    var root3d := Node3D.new()
    viewport.add_child(root3d)
    add_environment(root3d)

    var mesh := study_data["baseline_mesh"] as Dictionary if strategy == "material_twosided" else study_data["explicit_mesh"] as Dictionary
    var stats := add_tree(root3d, mesh, profile, strategy)
    if stats.get("state") != "PASS":
        viewport.queue_free()
        return {"state": "FAIL_TREE", "stats": stats}

    var pose := camera_pose(context_name, study_data["baseline_mesh"] as Dictionary)
    var camera := Camera3D.new()
    camera.near = 0.05
    camera.far = 80.0
    camera.fov = float(pose["fov"])
    root3d.add_child(camera)
    camera.make_current()
    camera.look_at_from_position(pose["position"] as Vector3, pose["target"] as Vector3, Vector3.UP)

    for _i in range(12):
        await process_frame
    var image := viewport.get_texture().get_image()
    if image == null or image.is_empty():
        viewport.queue_free()
        return {"state": "FAIL_CAPTURE"}
    var path := "res://%s-%s-%s.png" % [strategy, study_id, context_name]
    if image.save_png(path) != OK:
        viewport.queue_free()
        return {"state": "FAIL_CAPTURE"}
    var meta := {
        "state": "PASS",
        "study_id": study_id,
        "capture": {"width": image.get_width(), "height": image.get_height(), "bytes": FileAccess.get_file_as_bytes(path).size()},
        "camera": {"position": pose["position"], "target": pose["target"], "fov": pose["fov"]},
        "tree": stats
    }
    viewport.queue_free()
    for _i in range(2):
        await process_frame
    return {"state": "PASS", "image": image, "meta": meta}

func compare_images(a: Image, b: Image) -> Dictionary:
    if a.get_width() != b.get_width() or a.get_height() != b.get_height():
        return {"state": "FAIL_SIZE_MISMATCH"}
    var changed := 0
    var max_channel_delta := 0.0
    var summed_rgb_delta := 0.0
    var threshold := 1.0 / 255.0 + 0.000001
    for y in range(a.get_height()):
        for x in range(a.get_width()):
            var pa := a.get_pixel(x, y)
            var pb := b.get_pixel(x, y)
            var dr: float = absf(pa.r - pb.r)
            var dg: float = absf(pa.g - pb.g)
            var db: float = absf(pa.b - pb.b)
            var local_max: float = maxf(dr, maxf(dg, db))
            if local_max > threshold:
                changed += 1
            max_channel_delta = maxf(max_channel_delta, local_max)
            summed_rgb_delta += dr + dg + db
    var total := a.get_width() * a.get_height()
    return {
        "state": "PASS",
        "changed_pixels": changed,
        "total_pixels": total,
        "changed_percent": float(changed) * 100.0 / float(total),
        "max_channel_delta": max_channel_delta,
        "mean_absolute_rgb_channel_delta": summed_rgb_delta / float(total * 3)
    }

func _initialize() -> void:
    var data := load_data()
    if data.is_empty():
        fail("missing exact multi-source leaf sidedness comparison packet")
        return
    if String(data.get("schema", "")) != "axm.nature-leaf-sidedness-material-multisource/v0.2":
        fail("unexpected comparison schema")
        return
    if String(data.get("state", "")) != "PASS_EXACT_MULTI_SOURCE_LEAF_SIDEDNESS_MATERIAL_AB_PACKET":
        fail("comparison packet is not structurally passing")
        return

    var studies_payload := data["studies"] as Dictionary
    var study_results := {}
    for study_id_value in studies_payload.keys():
        var study_id := String(study_id_value)
        var study_data := studies_payload[study_id] as Dictionary
        var contexts := {}
        for context_name in CONTEXTS:
            var baseline := await capture(study_id, context_name, "material_twosided", study_data, data["review_material_profile"] as Dictionary)
            if baseline.get("state") != "PASS":
                fail("material-two-sided capture failed for %s / %s" % [study_id, context_name])
                return
            var explicit := await capture(study_id, context_name, "explicit_backfaces", study_data, data["review_material_profile"] as Dictionary)
            if explicit.get("state") != "PASS":
                fail("explicit-backface capture failed for %s / %s" % [study_id, context_name])
                return
            var delta := compare_images(baseline["image"] as Image, explicit["image"] as Image)
            if delta.get("state") != "PASS":
                fail("image comparison failed for %s / %s" % [study_id, context_name])
                return
            contexts[context_name] = {
                "material_twosided": baseline["meta"],
                "explicit_backfaces": explicit["meta"],
                "pixel_delta": delta
            }
        study_results[study_id] = {
            "source_digest": study_data["source_digest"],
            "baseline_mesh_digest": study_data["baseline_mesh_digest"],
            "explicit_mesh_digest": study_data["explicit_mesh_digest"],
            "comparison_contract": study_data["comparison_contract"],
            "contexts": contexts
        }

    receipt["state"] = "PASS_TARGET_HOST_MULTI_SOURCE_LEAF_SIDEDNESS_AB_CAPTURED"
    receipt["godot_version"] = Engine.get_version_info()
    receipt["materials_head"] = String(data.get("materials_head", ""))
    receipt["geometry_donor"] = data["geometry_donor"]
    receipt["review_material_policy"] = data["review_material_policy"]
    receipt["studies"] = study_results
    write_receipt()
    print("AXM MULTI-SOURCE LEAF SIDEDNESS MATERIAL AB ", JSON.stringify(receipt))
    quit(0)
