extends Node

const WINDOW_START := 110
const WINDOW_END := 370

var _mesh: ArrayMesh
var _packets: Array = []
var _byte_offset: int = 1320
var _sample_index: int = -1
var application_count: int = 0
var applied_indices: Array[int] = []

var sample_index: int:
    set(value):
        _sample_index = int(value)
        _apply_sample(_sample_index)
    get:
        return _sample_index

func configure(mesh: ArrayMesh, packets: Array, byte_offset: int) -> void:
    _mesh = mesh
    _packets = packets
    _byte_offset = byte_offset
    application_count = 0
    applied_indices.clear()

func _packet_vectors(index: int) -> PackedVector3Array:
    if index < 0 or index >= _packets.size():
        push_error("Animation proof bridge sample index outside packet family: %s" % index)
        return PackedVector3Array()
    var row = _packets[index]
    if not (row is Array) or row.size() != WINDOW_END - WINDOW_START:
        push_error("Animation proof bridge packet shape drift at sample %s" % index)
        return PackedVector3Array()
    var out := PackedVector3Array()
    out.resize(row.size())
    for local_index in range(row.size()):
        var point = row[local_index]
        if not (point is Array) or point.size() != 3:
            push_error("Animation proof bridge vector shape drift")
            return PackedVector3Array()
        out[local_index] = Vector3(float(point[0]), float(point[1]), float(point[2]))
    return out

func _apply_sample(index: int) -> void:
    if _mesh == null or index < 0:
        return
    var packet := _packet_vectors(index)
    if packet.size() != WINDOW_END - WINDOW_START:
        return
    _mesh.surface_update_vertex_region(0, _byte_offset, packet.to_byte_array())
    application_count += 1
    applied_indices.append(index)
