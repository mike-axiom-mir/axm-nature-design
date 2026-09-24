extends SceneTree

const CONTEXT_PATH := "res://generated/context.json"
const RECEIPT := "res://material-environment-context-runtime-receipt.json"

var receipt := {
    "schema":"axm.nature-material-environment-context-runtime/v0.1",
    "promotion_effect":"NONE",
    "truth_boundary":"Pinned Godot 4.7.2 GL Compatibility captures of the exact static Map receiving context with one material-only A/B difference on the already-proven portable sapling surface. Capture success and pixel non-identity do not prove aesthetic acceptance, botanical correctness, moving-sapling shading, final world-art hierarchy, renderer equivalence, gameplay/runtime acceptance, CANON, or mastery."
}

func write_receipt()->void:
    var file:=FileAccess.open(RECEIPT,FileAccess.WRITE)
    if file!=null:
        file.store_string(JSON.stringify(receipt,"  ")+"\n")
        file.close()

func fail(message:String)->void:
    receipt["state"]="FAIL_INFRASTRUCTURE"
    receipt["failure"]=message
    write_receipt()
    push_error(message)
    quit(1)

func load_context()->Dictionary:
    if not FileAccess.file_exists(CONTEXT_PATH):
        return {}
    var parsed=JSON.parse_string(FileAccess.get_file_as_string(CONTEXT_PATH))
    return parsed as Dictionary if parsed is Dictionary else {}

func gvec_source(values:Array)->Vector3:
    return Vector3(float(values[0]),float(values[2]),-float(values[1]))

func gvec_uc(values:Array)->Vector3:
    return Vector3(float(values[0]),float(values[1]),-float(values[2]))

func parse_hex_color(value:String)->Color:
    var text:=value.trim_prefix("#")
    if text.length()!=8:
        return Color(1,0,1,1)
    return Color(
        float(text.substr(0,2).hex_to_int())/255.0,
        float(text.substr(2,2).hex_to_int())/255.0,
        float(text.substr(4,2).hex_to_int())/255.0,
        float(text.substr(6,2).hex_to_int())/255.0
    )

func proxy_material(kind:String)->StandardMaterial3D:
    var material:=StandardMaterial3D.new()
    material.roughness=0.88
    if kind=="map-surface":
        material.albedo_color=Color(0.43,0.40,0.34,1.0)
    elif kind=="building-proxy":
        material.albedo_color=Color(0.34,0.38,0.44,1.0)
    elif kind=="nature-proxy":
        material.albedo_color=Color(0.27,0.42,0.25,1.0)
    elif kind=="object-proxy":
        material.albedo_color=Color(0.48,0.31,0.18,1.0)
    else:
        material.albedo_color=Color(0.45,0.45,0.45,1.0)
    return material

func add_proxy(root3d:Node3D,item:Dictionary)->void:
    var node:=MeshInstance3D.new()
    node.name=String(item.get("asset_id","proxy"))
    var mesh:=BoxMesh.new()
    var size=item["size_m"] as Array
    mesh.size=Vector3(float(size[0]),float(size[2]),float(size[1]))
    node.mesh=mesh
    node.position=gvec_source(item["position_m"] as Array)
    node.rotation.y=deg_to_rad(float(item.get("rotation_deg",0.0)))
    node.material_override=proxy_material(String(item.get("kind","unknown")))
    root3d.add_child(node)

func add_path(root3d:Node3D,scene:Dictionary)->void:
    var path=scene["readable_path"] as Dictionary
    var node:=MeshInstance3D.new()
    node.name="readable-path-observation-overlay"
    var mesh:=BoxMesh.new()
    var width=float(path["x_max"])-float(path["x_min"])
    var depth=float(path["y_max"])-float(path["y_min"])
    mesh.size=Vector3(width,0.035,depth)
    node.mesh=mesh
    var sx=(float(path["x_min"])+float(path["x_max"]))*0.5
    var sy=(float(path["y_min"])+float(path["y_max"]))*0.5
    node.position=gvec_source([sx,sy,0.035])
    var material:=StandardMaterial3D.new()
    material.albedo_color=Color(0.20,0.38,0.52,0.42)
    material.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA
    material.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED
    node.material_override=material
    root3d.add_child(node)

func material_from_payload(payload:Dictionary)->StandardMaterial3D:
    var material:=StandardMaterial3D.new()
    material.albedo_color=parse_hex_color(String(payload["color"]))
    material.metallic=float(payload["metallic"])
    material.roughness=float(payload["roughness"])
    return material

func add_sapling(root3d:Node3D,surface:Dictionary,translation_source:Array)->Dictionary:
    var translation:=gvec_source(translation_source)
    var primitive_stats={}
    var total_triangles:=0
    for primitive_value in surface["primitives"] as Array:
        var primitive=primitive_value as Dictionary
        var positions=primitive["positions"] as Array
        var normals=primitive["normals"] as Array
        var indices=primitive["indices"] as Array
        var st:=SurfaceTool.new()
        st.begin(Mesh.PRIMITIVE_TRIANGLES)
        for i in range(0,indices.size(),3):
            var ordered=[int(indices[i]),int(indices[i+2]),int(indices[i+1])]
            for index in ordered:
                var normal=normals[index] as Array
                var position=positions[index] as Array
                st.set_normal(gvec_uc(normal))
                st.add_vertex(gvec_uc(position)+translation)
        var mesh:=st.commit()
        var node:=MeshInstance3D.new()
        node.name="sapling-%s" % String(primitive["id"])
        node.mesh=mesh
        node.material_override=material_from_payload(primitive["material"] as Dictionary)
        root3d.add_child(node)
        var triangle_count:=indices.size()/3
        total_triangles+=triangle_count
        primitive_stats[String(primitive["id"])]=triangle_count
    return {"primitives":primitive_stats,"triangles":total_triangles}

func add_weather(root3d:Node3D,scene:Dictionary)->Dictionary:
    var lines=scene["weather_lines"] as Array
    var mesh:=ImmediateMesh.new()
    var material:=StandardMaterial3D.new()
    material.albedo_color=Color(0.55,0.77,1.0,0.62)
    material.emission_enabled=true
    material.emission=Color(0.25,0.48,0.78,1.0)
    material.emission_energy_multiplier=0.85
    material.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA
    material.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED
    mesh.surface_begin(Mesh.PRIMITIVE_LINES,material)
    for line_value in lines:
        var row=line_value as Dictionary
        var a=row["tail_xy"] as Array
        var b=row["head_xy"] as Array
        var h=float(row["presentation_height_m"])
        mesh.surface_add_vertex(gvec_source([float(a[0]),float(a[1]),h]))
        mesh.surface_add_vertex(gvec_source([float(b[0]),float(b[1]),h]))
    mesh.surface_end()
    var node:=MeshInstance3D.new()
    node.name="source-weather-visual-field"
    node.mesh=mesh
    root3d.add_child(node)
    return {"streaks":lines.size(),"presentation":scene["weather_presentation"]}

func add_environment(root3d:Node3D)->void:
    var env:=Environment.new()
    env.background_mode=Environment.BG_COLOR
    env.background_color=Color(0.055,0.07,0.09,1.0)
    env.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR
    env.ambient_light_color=Color(0.56,0.60,0.67,1.0)
    env.ambient_light_energy=0.62
    var world:=WorldEnvironment.new()
    world.environment=env
    root3d.add_child(world)
    var sun:=DirectionalLight3D.new()
    sun.shadow_enabled=true
    sun.light_energy=1.55
    sun.rotation_degrees=Vector3(-52,-35,0)
    root3d.add_child(sun)

func make_viewport(context_name:String,variant_name:String,data:Dictionary)->Dictionary:
    var scene=(data["environment"] as Dictionary)["scene"] as Dictionary
    var portable=data["portable_surface"] as Dictionary
    var viewport:=SubViewport.new()
    viewport.size=Vector2i(1100,720)
    viewport.own_world_3d=true
    viewport.render_target_update_mode=SubViewport.UPDATE_ALWAYS
    viewport.render_target_clear_mode=SubViewport.CLEAR_MODE_ALWAYS
    get_root().add_child(viewport)
    var root3d:=Node3D.new()
    viewport.add_child(root3d)
    add_environment(root3d)
    for item in scene["items"] as Array:
        add_proxy(root3d,item as Dictionary)
    add_path(root3d,scene)
    var sapling_stats:=add_sapling(root3d,portable[variant_name] as Dictionary,portable["placement_translation_source_xyz_m"] as Array)
    var weather_stats:=add_weather(root3d,scene)
    var camera:=Camera3D.new()
    camera.near=0.05
    camera.far=120.0
    root3d.add_child(camera)
    camera.make_current()
    var camera_data=(scene["cameras"] as Dictionary)[context_name] as Dictionary
    camera.fov=float(camera_data["fov_deg"])
    camera.look_at_from_position(gvec_source(camera_data["position_source_xyz_m"] as Array),gvec_source(camera_data["target_source_xyz_m"] as Array),Vector3.UP)
    return {"viewport":viewport,"sapling":sapling_stats,"weather":weather_stats,"camera":camera_data}

func capture(context_name:String,variant_name:String,data:Dictionary)->Dictionary:
    var setup:=make_viewport(context_name,variant_name,data)
    var viewport:=setup["viewport"] as SubViewport
    for _i in range(12):
        await process_frame
    var image:=viewport.get_texture().get_image()
    if image==null or image.is_empty():
        return {"state":"FAIL_CAPTURE"}
    var path="res://%s-%s.png" % [variant_name,context_name]
    if image.save_png(path)!=OK:
        return {"state":"FAIL_CAPTURE"}
    var result={
        "state":"PASS",
        "capture":{"width":image.get_width(),"height":image.get_height(),"bytes":FileAccess.get_file_as_bytes(path).size()},
        "camera":setup["camera"],
        "sapling":setup["sapling"],
        "weather":setup["weather"]
    }
    viewport.queue_free()
    for _i in range(2):
        await process_frame
    return result

func _initialize()->void:
    var data:=load_context()
    if data.is_empty():
        fail("missing or invalid exact material environment context")
        return
    if String(data.get("schema",""))!="axm.nature-material-environment-context/v0.1":
        fail("unexpected context schema")
        return
    var scene=(data["environment"] as Dictionary)["scene"] as Dictionary
    var contexts={}
    for context_name in ["path_eye","elevated_oblique"]:
        var row={}
        for variant_name in ["baseline","candidate"]:
            var capture_row:=await capture(context_name,variant_name,data)
            if capture_row.get("state")!="PASS":
                fail("capture failed for %s / %s" % [context_name,variant_name])
                return
            row[variant_name]=capture_row
        contexts[context_name]=row
    receipt["state"]="PASS_TARGET_HOST_STATIC_ENVIRONMENT_MATERIAL_AB_READY"
    receipt["godot_version"]=Engine.get_version_info()
    receipt["context_digest"]=String(data.get("context_digest",""))
    receipt["environment_scene_digest"]=String((data["environment"] as Dictionary).get("scene_digest",""))
    receipt["materials_head"]=String(data.get("materials_head",""))
    receipt["comparison_contract"]=data["comparison_contract"]
    receipt["representation_note"]=(data["portable_surface"] as Dictionary)["representation_note"]
    receipt["weather_presentation"]=scene["weather_presentation"]
    receipt["contexts"]=contexts
    write_receipt()
    print("AXM MATERIAL ENVIRONMENT CONTEXT ",JSON.stringify(receipt))
    quit(0)
