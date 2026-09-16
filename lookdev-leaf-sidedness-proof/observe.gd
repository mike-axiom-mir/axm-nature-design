extends SceneTree

const DATA_PATH := "res://generated/comparison.json"
const RECEIPT_PATH := "res://leaf-sidedness-runtime-receipt.json"
const CONTEXTS := ["whole_three_quarter", "crown_back", "crown_low_grazing"]

var receipt := {
    "schema": "axm.nature-leaf-sidedness-material-runtime/v0.1",
    "promotion_effect": "NONE",
    "truth_boundary": "Pinned Godot 4.7.2 GL Compatibility observation of one exact sapling source comparing material-level disabled foliage culling against explicit opposite-wound leaf backface geometry while scalar material values, lighting and cameras are held fixed. Pixel evidence does not prove final normals, final leaf shader, botanical correctness, runtime cost acceptance, Map/VFX acceptance, CANON, production readiness, or Materials mastery."
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

func camera_pose(context_name: String) -> Dictionary:
    if context_name == "whole_three_quarter":
        return {"position": Vector3(5.8, 3.6, 7.8), "target": Vector3(0.0, 2.45, 0.0), "fov": 47.0}
    if context_name == "crown_back":
        return {"position": Vector3(-3.2, 4.35, -4.7), "target": Vector3(0.0, 3.75, 0.0), "fov": 43.0}
    return {"position": Vector3(4.2, 2.75, 2.4), "target": Vector3(0.0, 3.65, 0.0), "fov": 42.0}

func capture(context_name: String, strategy: String, data: Dictionary) -> Dictionary:
    var viewport := SubViewport.new()
    viewport.size = Vector2i(720, 560)
    viewport.own_world_3d = true
    viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
    viewport.render_target_clear_mode = SubViewport.CLEAR_MODE_ALWAYS
    get_root().add_child(viewport)

    var root3d := Node3D.new()
    viewport.add_child(root3d)
    add_environment(root3d)

    var mesh := data["baseline_mesh"] as Dictionary if strategy == "material_twosided" else data["explicit_mesh"] as Dictionary
    var stats := add_tree(root3d, mesh, data["material_profile"] as Dictionary, strategy)
    if stats.get("state") != "PASS":
        viewport.queue_free()
        return {"state": "FAIL_TREE", "stats": stats}

    var pose := camera_pose(context_name)
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
    var path := "res://%s-%s.png" % [strategy, context_name]
    if image.save_png(path) != OK:
        viewport.queue_free()
        return {"state": "FAIL_CAPTURE"}
    var meta := {
        "state": "PASS",
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
            var dr := abs(pa.r - pb.r)
            var dg := abs(pa.g - pb.g)
            var db := abs(pa.b - pb.b)
            var local_max := max(dr, max(dg, db))
            if local_max > threshold:
                changed += 1
            max_channel_delta = max(max_channel_delta, local_max)
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
        fail("missing exact leaf sidedness comparison packet")
        return
    if String(data.get("schema", "")) != "axm.nature-leaf-sidedness-material-ab/v0.1":
        fail("unexpected comparison schema")
        return
    if String(data.get("state", "")) != "PASS_EXACT_LEAF_SIDEDNESS_MATERIAL_AB_PACKET":
        fail("comparison packet is not structurally passing")
        return

    var contexts := {}
    for context_name in CONTEXTS:
        var baseline := await capture(context_name, "material_twosided", data)
        if baseline.get("state") != "PASS":
            fail("material-two-sided capture failed for %s" % context_name)
            return
        var explicit := await capture(context_name, "explicit_backfaces", data)
        if explicit.get("state") != "PASS":
            fail("explicit-backface capture failed for %s" % context_name)
            return
        var delta := compare_images(baseline["image"] as Image, explicit["image"] as Image)
        if delta.get("state") != "PASS":
            fail("image comparison failed for %s" % context_name)
            return
        contexts[context_name] = {
            "material_twosided": baseline["meta"],
            "explicit_backfaces": explicit["meta"],
            "pixel_delta": delta
        }

    receipt["state"] = "PASS_TARGET_HOST_LEAF_SIDEDNESS_AB_CAPTURED"
    receipt["godot_version"] = Engine.get_version_info()
    receipt["materials_head"] = String(data.get("materials_head", ""))
    receipt["geometry_donor"] = data["geometry_donor"]
    receipt["comparison_contract"] = data["comparison_contract"]
    receipt["contexts"] = contexts
    write_receipt()
    print("AXM LEAF SIDEDNESS MATERIAL AB ", JSON.stringify(receipt))
    quit(0)
