extends SceneTree

const DATA_PATH := "res://generated/comparison.json"
const RECEIPT_PATH := "res://foliage-backface-shading-runtime-receipt.json"
const CONTEXTS := ["whole_three_quarter", "crown_back", "crown_low_grazing"]
const STRATEGIES := ["standard_twosided", "shader_authored_normal_twosided", "shader_faceforward_normal_twosided", "explicit_backfaces"]

var receipt := {
    "schema": "axm.nature-foliage-backface-shading-runtime/v0.1",
    "promotion_effect": "NONE",
    "truth_boundary": "Pinned Godot 4.7.2 GL Compatibility diagnostic of the existing bounded three-source woody/foliage family under four foliage receiving strategies. Source form, scalar PBR values, woody treatment, cameras and lights are held within each study/context. This isolates whether back-facing foliage normal handling changes shaded response; it does not establish final botanical shading, translucency/transmission, textures, arbitrary-view equivalence, Environment adoption, target-device runtime cost, CANON, production readiness, or Materials mastery."
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

func standard_material(payload: Dictionary, cull_mode: int) -> StandardMaterial3D:
    var material := StandardMaterial3D.new()
    material.albedo_color = parse_hex_color(String(payload["color"]))
    material.metallic = float(payload["metallic"])
    material.roughness = float(payload["roughness"])
    material.cull_mode = cull_mode
    return material

func shader_material(payload: Dictionary, faceforward_backfaces: bool, cull_disabled: bool) -> ShaderMaterial:
    var shader := Shader.new()
    var render_mode := "cull_disabled" if cull_disabled else "cull_back"
    var normal_logic := "if (!FRONT_FACING) { NORMAL = -NORMAL; }" if faceforward_backfaces else ""
    shader.code = """shader_type spatial;
render_mode %s;
uniform vec4 albedo_color : source_color = vec4(1.0);
uniform float metallic_value = 0.0;
uniform float roughness_value = 0.5;
void fragment() {
    ALBEDO = albedo_color.rgb;
    METALLIC = metallic_value;
    ROUGHNESS = roughness_value;
    %s
}
""" % [render_mode, normal_logic]
    var material := ShaderMaterial.new()
    material.shader = shader
    material.set_shader_parameter("albedo_color", parse_hex_color(String(payload["color"])))
    material.set_shader_parameter("metallic_value", float(payload["metallic"]))
    material.set_shader_parameter("roughness_value", float(payload["roughness"]))
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

func add_tree(root3d: Node3D, study_data: Dictionary, profile: Dictionary, strategy: String) -> Dictionary:
    var use_explicit := strategy == "explicit_backfaces"
    var mesh := study_data["explicit_mesh"] as Dictionary if use_explicit else study_data["baseline_mesh"] as Dictionary
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
    woody_node.material_override = standard_material(materials["woody"] as Dictionary, BaseMaterial3D.CULL_BACK)
    root3d.add_child(woody_node)

    var foliage_node := MeshInstance3D.new()
    foliage_node.name = "%s-foliage" % strategy
    foliage_node.mesh = foliage_st.commit()
    var foliage_payload := materials["foliage"] as Dictionary
    if strategy == "standard_twosided":
        foliage_node.material_override = standard_material(foliage_payload, BaseMaterial3D.CULL_DISABLED)
    elif strategy == "shader_authored_normal_twosided":
        foliage_node.material_override = shader_material(foliage_payload, false, true)
    elif strategy == "shader_faceforward_normal_twosided":
        foliage_node.material_override = shader_material(foliage_payload, true, true)
    elif strategy == "explicit_backfaces":
        foliage_node.material_override = shader_material(foliage_payload, false, false)
    else:
        return {"state": "FAIL_UNKNOWN_STRATEGY", "strategy": strategy}
    root3d.add_child(foliage_node)

    return {
        "state": "PASS",
        "strategy": strategy,
        "vertices": vertices.size(),
        "triangles": triangles.size(),
        "woody_triangles": woody_triangles,
        "foliage_triangles": foliage_triangles,
        "foliage_cull_mode": "CULL_BACK" if use_explicit else "CULL_DISABLED",
        "normal_policy": (
            "STANDARD_MATERIAL3D_CURRENT_RECEIVER" if strategy == "standard_twosided"
            else "AUTHORED_NORMAL_UNCHANGED" if strategy == "shader_authored_normal_twosided"
            else "FRONT_FACING_BACKFACE_NORMAL_NEGATED" if strategy == "shader_faceforward_normal_twosided"
            else "EXPLICIT_OPPOSITE_WINDING_NORMAL_REFERENCE"
        )
    }

func add_environment(root3d: Node3D) -> void:
    var env := Environment.new()
    env.background_mode = Environment.BG_COLOR
    env.background_color = Color(0.055, 0.065, 0.08, 1.0)
    env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
    env.ambient_light_color = Color(0.52, 0.56, 0.62, 1.0)
    env.ambient_light_energy = 0.24
    var world := WorldEnvironment.new()
    world.environment = env
    root3d.add_child(world)

    var key := DirectionalLight3D.new()
    key.light_energy = 2.15
    key.rotation_degrees = Vector3(-50, -36, 0)
    key.shadow_enabled = true
    root3d.add_child(key)

    var fill := DirectionalLight3D.new()
    fill.light_energy = 0.16
    fill.light_color = Color(0.58, 0.68, 0.90, 1.0)
    fill.rotation_degrees = Vector3(-18, 145, 0)
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
    var stats := add_tree(root3d, study_data, profile, strategy)
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
        fail("missing exact multi-source comparison packet")
        return
    if String(data.get("schema", "")) != "axm.nature-leaf-sidedness-material-multisource/v0.2":
        fail("unexpected comparison schema")
        return
    if String(data.get("profile_mode", "")) != "BOUNDED_THREE_SOURCE_FAMILY_CANDIDATE":
        fail("backface shading proof requires bounded family candidate")
        return

    var studies_payload := data["studies"] as Dictionary
    var study_results := {}
    for study_id_value in studies_payload.keys():
        var study_id := String(study_id_value)
        var study_data := studies_payload[study_id] as Dictionary
        var contexts := {}
        for context_name in CONTEXTS:
            var captures := {}
            for strategy in STRATEGIES:
                var result := await capture(study_id, context_name, strategy, study_data, data["review_material_profile"] as Dictionary)
                if result.get("state") != "PASS":
                    fail("capture failed for %s / %s / %s" % [study_id, context_name, strategy])
                    return
                captures[strategy] = result
            contexts[context_name] = {
                "captures": {
                    "standard_twosided": captures["standard_twosided"]["meta"],
                    "shader_authored_normal_twosided": captures["shader_authored_normal_twosided"]["meta"],
                    "shader_faceforward_normal_twosided": captures["shader_faceforward_normal_twosided"]["meta"],
                    "explicit_backfaces": captures["explicit_backfaces"]["meta"]
                },
                "deltas": {
                    "standard_vs_shader_authored": compare_images(captures["standard_twosided"]["image"] as Image, captures["shader_authored_normal_twosided"]["image"] as Image),
                    "shader_authored_vs_faceforward": compare_images(captures["shader_authored_normal_twosided"]["image"] as Image, captures["shader_faceforward_normal_twosided"]["image"] as Image),
                    "standard_vs_faceforward": compare_images(captures["standard_twosided"]["image"] as Image, captures["shader_faceforward_normal_twosided"]["image"] as Image),
                    "faceforward_vs_explicit_backfaces": compare_images(captures["shader_faceforward_normal_twosided"]["image"] as Image, captures["explicit_backfaces"]["image"] as Image),
                    "standard_vs_explicit_backfaces": compare_images(captures["standard_twosided"]["image"] as Image, captures["explicit_backfaces"]["image"] as Image)
                }
            }
        study_results[study_id] = {
            "source_digest": study_data["source_digest"],
            "baseline_mesh_digest": study_data["baseline_mesh_digest"],
            "explicit_mesh_digest": study_data["explicit_mesh_digest"],
            "contexts": contexts
        }

    receipt["state"] = "PASS_TARGET_HOST_FOLIAGE_BACKFACE_SHADING_DIAGNOSTIC_CAPTURED"
    receipt["godot_version"] = Engine.get_version_info()
    receipt["materials_head"] = String(data.get("materials_head", ""))
    receipt["geometry_donor"] = data["geometry_donor"]
    receipt["material_profile"] = data["review_material_profile"]
    receipt["lighting_policy"] = "ASYMMETRIC_LOW_AMBIENT_KEY_PLUS_WEAK_FILL__FIXED_ACROSS_ALL_STRATEGIES"
    receipt["studies"] = study_results
    write_receipt()
    print("AXM FOLIAGE BACKFACE SHADING DIAGNOSTIC ", JSON.stringify(receipt))
    quit(0)
