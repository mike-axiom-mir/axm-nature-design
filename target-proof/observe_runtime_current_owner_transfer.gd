extends SceneTree

const PRE_RECEIPT := "res://generated-current-owner/nature-north-low-parent-exclusion-uc-target-receipt.json"
const ORACLE_PATH := "res://generated-current-owner/nature-north-low-parent-exclusion-target-oracle.json"
const RECEIVER_GLB := "res://generated-current-owner/nature-north-low-parent-exclusion-receiver-rigid.glb"
const SHADER_PATH := "res://generated-current-owner/runtime_current_owner_node_vs_shader.gdshader"
const OUTPUT := "res://runtime-current-owner-transfer-receipt.json"
const RENDER_DIR := "res://renders/runtime-current-owner-transfer"
const BRANCH_IDS := ["south-low", "north-low", "east-mid", "west-high", "north-top"]
const CAPTURE_INDICES := [0, 5, 10, 15, 20, 25, 30, 35, 39]
const EXPECTED_ANIMATION_HEAD := "5cacd61e22433b0c33f29111827283b81cc0ba0d"
const EXPECTED_RIGGING_HEAD := "69640e558f0c1ac59d4d0e3155676e0967a03d04"
const EXPECTED_UC_HEAD := "7ddefca57b153fab02c1f54f38de22148cb52c1b"
const EXPECTED_NODES := 12
const EXPECTED_TRIANGLES := 620
const POSITION_TOL_M := 0.000005

var receipt := {
    "schema": "axm.nature-runtime-current-owner-rigid-node-vs-shader/v0.1",
    "state": "NOT_RUN"
}

func _fail(message: String) -> void:
    receipt["state"] = "FAIL_RUNTIME_CURRENT_OWNER_TRANSFER_GATE"
    receipt["failure"] = message
    _write_json(OUTPUT, receipt)
    push_error(message)
    quit(1)

func _read_json(path: String) -> Dictionary:
    if not FileAccess.file_exists(path):
        _fail("missing JSON: %s" % path)
        return {}
    var parsed = JSON.parse_string(FileAccess.get_file_as_string(path))
    if not (parsed is Dictionary):
        _fail("invalid JSON object: %s" % path)
        return {}
    return parsed as Dictionary

func _write_json(path: String, payload: Dictionary) -> void:
    var handle := FileAccess.open(path, FileAccess.WRITE)
    if handle == null:
        push_error("failed to open receipt: %s" % path)
        return
    handle.store_string(JSON.stringify(payload, "  ", false) + "\n")
    handle.close()

func _sha256_file(path: String) -> String:
    var bytes := FileAccess.get_file_as_bytes(path)
    var ctx := HashingContext.new()
    ctx.start(HashingContext.HASH_SHA256)
    ctx.update(bytes)
    return ctx.finish().hex_encode()

func _find_named(node: Node, wanted: String) -> Node:
    if String(node.name) == wanted:
        return node
    for child in node.get_children():
        var found := _find_named(child, wanted)
        if found != null:
            return found
    return null

func _import_scene(path: String) -> Node3D:
    var document := GLTFDocument.new()
    var state := GLTFState.new()
    var error := document.append_from_file(path, state)
    if error != OK:
        _fail("GLTFDocument append failed: %s" % str(error))
        return Node3D.new()
    var generated = document.generate_scene(state)
    if generated == null or not (generated is Node3D):
        _fail("GLTFDocument generate_scene returned no Node3D")
        return Node3D.new()
    return generated as Node3D

func _vec3(value: Variant) -> Vector3:
    if not (value is Array) or value.size() != 3:
        _fail("invalid vec3 payload")
        return Vector3.ZERO
    return Vector3(float(value[0]), float(value[1]), float(value[2]))

func _nearest_local_vertex(instance: MeshInstance3D, expected: Vector3) -> Dictionary:
    var best_delta := INF
    var best := Vector3.ZERO
    var found := false
    if instance.mesh == null:
        _fail("witness instance has no mesh")
        return {}
    for surface_index in range(instance.mesh.get_surface_count()):
        var arrays := instance.mesh.surface_get_arrays(surface_index)
        var vertices = arrays[Mesh.ARRAY_VERTEX]
        if vertices == null:
            continue
        for vertex in vertices:
            var point := vertex as Vector3
            var delta := point.distance_to(expected)
            if delta < best_delta:
                best_delta = delta
                best = point
                found = true
    if not found:
        _fail("no witness vertex found")
    return {"position": best, "delta_m": best_delta}

func _triangle_count(instance: MeshInstance3D) -> int:
    var total := 0
    if instance.mesh == null:
        return 0
    for surface_index in range(instance.mesh.get_surface_count()):
        var arrays := instance.mesh.surface_get_arrays(surface_index)
        var indices = arrays[Mesh.ARRAY_INDEX]
        var vertices = arrays[Mesh.ARRAY_VERTEX]
        if indices != null and indices.size() > 0:
            total += int(indices.size() / 3)
        elif vertices != null:
            total += int(vertices.size() / 3)
    return total

func _mesh_layout(instance: MeshInstance3D) -> Dictionary:
    var rows: Array = []
    var position_storage_bytes := 0
    var all_compressed := true
    if instance.mesh == null:
        return {"surfaces": rows, "position_storage_bytes": 0, "all_compressed": false}
    for surface_index in range(instance.mesh.get_surface_count()):
        var arrays := instance.mesh.surface_get_arrays(surface_index)
        var vertices = arrays[Mesh.ARRAY_VERTEX]
        var count := int(vertices.size()) if vertices != null else 0
        var format: int = int(instance.mesh.surface_get_format(surface_index))
        var stride: int = RenderingServer.mesh_surface_get_format_vertex_stride(format, count)
        var compressed: bool = (format & int(Mesh.ARRAY_FLAG_COMPRESS_ATTRIBUTES)) != 0
        all_compressed = all_compressed and compressed
        position_storage_bytes += count * stride
        rows.append({"surface": surface_index, "vertices": count, "position_stride_bytes": stride, "compressed_attributes": compressed})
    return {"surfaces": rows, "position_storage_bytes": position_storage_bytes, "all_compressed": all_compressed}

func _shader_material(shader: Shader, source: Material) -> ShaderMaterial:
    var result := ShaderMaterial.new()
    result.shader = shader
    if source is BaseMaterial3D:
        var base := source as BaseMaterial3D
        result.set_shader_parameter("albedo_color", base.albedo_color)
        result.set_shader_parameter("metallic_value", base.metallic)
        result.set_shader_parameter("roughness_value", base.roughness)
        result.set_shader_parameter("specular_value", base.metallic_specular)
    return result

func _counter_snapshot() -> Dictionary:
    return {
        "draw_calls": int(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)),
        "objects": int(Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME)),
        "primitives": int(Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME)),
        "buffer_memory_bytes": int(Performance.get_monitor(Performance.RENDER_BUFFER_MEM_USED)),
        "texture_memory_bytes": int(Performance.get_monitor(Performance.RENDER_TEXTURE_MEM_USED)),
        "video_memory_bytes": int(Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED))
    }

func _capture(path: String) -> Dictionary:
    await process_frame
    await RenderingServer.frame_post_draw
    var counters := _counter_snapshot()
    var image := get_root().get_texture().get_image()
    if image == null or image.is_empty():
        _fail("empty render capture")
        return {}
    if image.save_png(path) != OK:
        _fail("failed to save render: %s" % path)
        return {}
    counters["png_bytes"] = FileAccess.get_file_as_bytes(path).size()
    return counters

func _set_control(nodes: Dictionary, originals: Dictionary, axis: Vector3, target_angle_deg: float) -> void:
    for branch_id in BRANCH_IDS:
        var root := nodes[branch_id + "-woody"] as MeshInstance3D
        root.transform = originals[branch_id] as Transform3D
        root.material_override = null
        var foliage := nodes[branch_id + "-foliage"] as MeshInstance3D
        foliage.material_override = null
    var north := nodes["north-low-woody"] as MeshInstance3D
    var base := originals["north-low"] as Transform3D
    north.transform = Transform3D(Basis(Quaternion(axis, deg_to_rad(target_angle_deg))), base.origin)

func _set_candidate(nodes: Dictionary, originals: Dictionary, woody_material: ShaderMaterial, foliage_material: ShaderMaterial, target_angle_deg: float) -> void:
    for branch_id in BRANCH_IDS:
        var root := nodes[branch_id + "-woody"] as MeshInstance3D
        root.transform = originals[branch_id] as Transform3D
        root.material_override = null
        var foliage := nodes[branch_id + "-foliage"] as MeshInstance3D
        foliage.material_override = null
    woody_material.set_shader_parameter("driver_deg", target_angle_deg)
    foliage_material.set_shader_parameter("driver_deg", target_angle_deg)
    var north := nodes["north-low-woody"] as MeshInstance3D
    var north_foliage := nodes["north-low-foliage"] as MeshInstance3D
    north.material_override = woody_material
    north_foliage.material_override = foliage_material

func _run() -> void:
    var pre := _read_json(PRE_RECEIPT)
    var oracle := _read_json(ORACLE_PATH)
    if pre.is_empty() or oracle.is_empty():
        return
    if String(pre.get("result", "")) != "PASS_NATURE_NORTH_LOW_PARENT_EXCLUSION_CURRENT_UC_TARGET_RECEIVER_READY":
        _fail("current Technical Art pre-receipt is not green")
        return
    var heads := pre.get("heads", {}) as Dictionary
    if String(heads.get("animation", "")) != EXPECTED_ANIMATION_HEAD or String(heads.get("rigging", "")) != EXPECTED_RIGGING_HEAD or String(heads.get("uc", "")) != EXPECTED_UC_HEAD:
        _fail("current owner head drift")
        return
    if String(oracle.get("branch_id", "")) != "north-low":
        _fail("oracle branch drift")
        return
    var expected_glb_sha := String((pre.get("receiver", {}) as Dictionary).get("rigid_glb_sha256", ""))
    if _sha256_file(RECEIVER_GLB) != expected_glb_sha:
        _fail("exact rigid receiver GLB identity drift")
        return

    var scene := _import_scene(RECEIVER_GLB)
    get_root().add_child(scene)
    await process_frame

    var expected_names := ["static-woody", "static-foliage"]
    for branch_id in BRANCH_IDS:
        expected_names.append(branch_id + "-woody")
        expected_names.append(branch_id + "-foliage")
    var nodes := {}
    var total_triangles := 0
    for node_name in expected_names:
        var node := _find_named(scene, node_name)
        if node == null or not (node is MeshInstance3D):
            _fail("missing receiver mesh node: %s" % node_name)
            return
        nodes[node_name] = node
        total_triangles += _triangle_count(node as MeshInstance3D)
    if nodes.size() != EXPECTED_NODES or total_triangles != EXPECTED_TRIANGLES:
        _fail("receiver node/triangle budget drift")
        return
    var north_woody := nodes["north-low-woody"] as MeshInstance3D
    var north_foliage := nodes["north-low-foliage"] as MeshInstance3D
    if north_foliage.get_parent() != north_woody:
        _fail("north-low foliage parent edge drift")
        return

    var originals := {}
    for branch_id in BRANCH_IDS:
        originals[branch_id] = (nodes[branch_id + "-woody"] as MeshInstance3D).transform

    var axis := _vec3(oracle.get("target_axis_uc")).normalized()
    var witness_node := nodes[String(oracle.get("primitive_id", ""))] as MeshInstance3D
    if witness_node == null:
        _fail("missing oracle witness node")
        return
    var nearest := _nearest_local_vertex(witness_node, _vec3(oracle.get("witness_local_uc_m")))
    var witness_local := nearest.get("position", Vector3.ZERO) as Vector3
    if float(nearest.get("delta_m", INF)) > POSITION_TOL_M:
        _fail("imported witness drift")
        return

    var shader := Shader.new()
    shader.code = FileAccess.get_file_as_string(SHADER_PATH)
    var woody_source: Material = north_woody.mesh.surface_get_material(0)
    var foliage_source: Material = north_foliage.mesh.surface_get_material(0)
    var woody_candidate := _shader_material(shader, woody_source)
    var foliage_candidate := _shader_material(shader, foliage_source)
    woody_candidate.set_shader_parameter("driver_axis", axis)
    foliage_candidate.set_shader_parameter("driver_axis", axis)

    var camera := Camera3D.new()
    scene.add_child(camera)
    camera.position = Vector3(5.4, 3.4, 5.4)
    camera.look_at(Vector3(0.0, 2.0, 0.0), Vector3.UP)
    camera.fov = 42.0
    camera.current = true
    var light := DirectionalLight3D.new()
    scene.add_child(light)
    light.rotation_degrees = Vector3(-52.0, -28.0, 0.0)
    light.light_energy = 1.35
    light.shadow_enabled = false
    var world_environment := WorldEnvironment.new()
    var environment := Environment.new()
    environment.background_mode = Environment.BG_COLOR
    environment.background_color = Color(0.045, 0.05, 0.06, 1.0)
    environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
    environment.ambient_light_color = Color(0.52, 0.55, 0.60, 1.0)
    environment.ambient_light_energy = 0.82
    world_environment.environment = environment
    scene.add_child(world_environment)
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(RENDER_DIR))

    var samples = oracle.get("samples", []) as Array
    if samples.size() != 41:
        _fail("current target sample count drift")
        return
    var maximum_control_residual := 0.0
    var maximum_parent_stress_abs := 0.0
    var capture_rows: Array = []
    var control_peak_counters := {}
    var candidate_peak_counters := {}
    for sample_index in range(samples.size()):
        var sample := samples[sample_index] as Dictionary
        if int(sample.get("index", -1)) != sample_index:
            _fail("sample index drift")
            return
        var target_angle := float(sample.get("target_receiver_angle_deg", 999.0))
        var parent_stress := float(sample.get("upper_trunk_parent_stress_command_deg", 999.0))
        maximum_parent_stress_abs = max(maximum_parent_stress_abs, abs(parent_stress))
        _set_control(nodes, originals, axis, target_angle)
        await process_frame
        var actual_world := witness_node.global_transform * witness_local
        var expected_world := _vec3(sample.get("expected_witness_world_uc_m"))
        var residual := actual_world.distance_to(expected_world)
        maximum_control_residual = max(maximum_control_residual, residual)
        if residual > POSITION_TOL_M:
            _fail("current rigid-node control residual exceeds tolerance at sample %d" % sample_index)
            return
        if CAPTURE_INDICES.has(sample_index):
            var token := "%02d" % sample_index
            var control_counters := await _capture("%s/control_%s.png" % [RENDER_DIR, token])
            _set_candidate(nodes, originals, woody_candidate, foliage_candidate, target_angle)
            var candidate_counters := await _capture("%s/candidate_%s.png" % [RENDER_DIR, token])
            capture_rows.append({
                "sample_index": sample_index,
                "time_s": float(sample.get("time_s", -1.0)),
                "north_low_child_angle_deg": float(sample.get("north_low_child_angle_deg", 999.0)),
                "target_receiver_angle_deg": target_angle,
                "parent_stress_command_deg": parent_stress,
                "control_counters": control_counters,
                "candidate_counters": candidate_counters
            })
            if sample_index == 10:
                control_peak_counters = control_counters
                candidate_peak_counters = candidate_counters

    var layout_rows := {}
    var total_position_storage_bytes := 0
    var all_compressed := true
    for node_name in expected_names:
        var layout := _mesh_layout(nodes[node_name] as MeshInstance3D)
        layout_rows[node_name] = layout
        total_position_storage_bytes += int(layout.get("position_storage_bytes", 0))
        all_compressed = all_compressed and bool(layout.get("all_compressed", false))

    var control_semantic_bytes := 4
    var candidate_semantic_bytes := 4
    var semantic_saving := control_semantic_bytes - candidate_semantic_bytes
    receipt = {
        "schema": "axm.nature-runtime-current-owner-rigid-node-vs-shader/v0.1",
        "state": "PASS_CURRENT_OWNER_RUNTIME_REBIND_MEASURED__HOLD_PREDECESSOR_SHADER_TRANSFER_NO_INCREMENTAL_BUDGET_WIN",
        "godot": Engine.get_version_info(),
        "heads": heads,
        "receiver": {
            "nodes_verified": nodes.size(),
            "triangles": total_triangles,
            "north_low_foliage_parented_under_woody": true,
            "rigid_glb_sha256": _sha256_file(RECEIVER_GLB),
            "all_imported_surfaces_compressed": all_compressed,
            "summed_imported_position_storage_bytes": total_position_storage_bytes,
            "mesh_layout": layout_rows
        },
        "measurements": {
            "all_endpoint_inclusive_samples_checked": samples.size(),
            "visible_repeat_samples": 40,
            "maximum_current_rigid_node_control_position_residual_m": maximum_control_residual,
            "maximum_parent_stress_command_abs_deg": maximum_parent_stress_abs,
            "control_semantic_driver_bytes_per_visible_sample": control_semantic_bytes,
            "candidate_semantic_driver_bytes_per_visible_sample": candidate_semantic_bytes,
            "semantic_payload_saving_bytes_per_visible_sample": semantic_saving,
            "control_cpu_position_buffer_mutated_per_sample": false,
            "candidate_cpu_position_buffer_mutated_per_sample": false,
            "control_north_low_node_transforms_per_sample": 1,
            "candidate_custom_shader_instances": 2,
            "control_peak_counters": control_peak_counters,
            "candidate_peak_counters": candidate_peak_counters,
            "capture_rows": capture_rows
        },
        "runtime_decision": {
            "decision": "KEEP_CURRENT_TA_RIGID_NODE_CONTROL__HOLD_PREDECESSOR_SHADER_TRANSFER",
            "reason": "CURRENT_TA_RECEIVER_ALREADY_CONSUMES_ONE_4_BYTE_SCALAR_WITH_NO_CPU_VERTEX_PACKET__SHADER_CANDIDATE_SAVES_ZERO_SEMANTIC_BYTES_AND_ADDS_CUSTOM_VERTEX_WORK",
            "predecessor_3120_byte_dynamic_packet_may_be_used_as_current_baseline": false,
            "automatic_shader_adoption": false
        },
        "visual_tradeoff": {
            "fresh_capture_pair_count": capture_rows.size(),
            "exact_raster_comparison_owned_by_workflow": true,
            "custom_shader_rotates_positions_and_normals": true,
            "tangent_deformation_correctness_proven": false,
            "art_direction_review_state": "RETURN_CURRENT_OWNER_A_B_WITH_RUNTIME_HOLD"
        },
        "truth_boundary": {
            "semantic_driver_payload_is_measured_gpu_command_transport": false,
            "target_device_cpu_gpu_fps_vram_thermal_battery_proven": false,
            "natural_animationplayer_playback_claimed": false,
            "parent_stress_command_applied_as_receiver_motion": false,
            "connected_attachment_or_production_skinning_proven": false,
            "art_direction_or_visual_qa_acceptance_proven": false,
            "canon_or_production_readiness_proven": false
        }
    }
    _write_json(OUTPUT, receipt)
    print(JSON.stringify(receipt, "  ", false))
    quit(0)

func _initialize() -> void:
    call_deferred("_run")
