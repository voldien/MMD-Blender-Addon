from struct import unpack
import array
import bpy
import zlib

data_section_names = ['Vertex', 'Face', 'Texture', 'Material',
                      'Bone', 'Morph', 'Frame', 'Rigidbody', 'Joint', 'Softbody']
index_attribute_names = ['text_encoding', 'additional_vec4_count', 'vertex_index_size', 'texture_index_size',
                         'material_index_size',
                         'bone_index_size', 'morph_index_size', 'rigid_index_size']

magic_signature = [0x50, 0x4D, 0x58, 0x20]

# Morph flag types.
const_morph_type_group = 0
const_morph_type_vertex = 1
const_morph_type_bone = 2
const_morph_type_uv = 3
const_morph_type_uv_ext1 = 4
const_morph_type_uv_ext2 = 5
const_morph_type_uv_ext3 = 6
const_morph_type_material = 8
const_morph_type_flip = 9
const_morph_type_impulse = 10

# Material flags.
const_material_flag_nocull = 0x1
const_material_flag_ground_shadow = 0x2
const_material_flag_draw_shadow = 0x4
const_material_flag_recieve_shadow = 0x8
const_material_flag_has_edge = 0x10
const_material_flag_vertex_color = 0x20
const_material_flag_point_drawing = 0x40
const_material_flag_line_drawing = 0x80

# Bone flags.
const_bone_flag_index_tail_position = 0x1
const_bone_flag_rotatable = 0x2
const_bone_flag_translatable = 0x4
const_bone_flag_is_visable = 0x8
const_bone_flag_enabled = 0x10
const_bone_flag_ik = 0x20
const_bone_flag_inherit_rotation = 0x100
const_bone_flag_inherit_translation = 0x200
const_bone_flag_fixed_axis = 0x400
const_bone_flag_local_co_coordinate = 0x800
const_bone_flag_physic_deform = 0x1000
const_bone_flag_external_parent_deform = 0x2000

# Data types size in bytes.
const_byte = 1
const_sbyte = 1
const_short = 2
const_ushort = 2
const_int = 4
const_uint = 4
const_uint64 = 8
const_float = 4
const_flag = 1
# Vector size in bytes.
const_vec2 = 8
const_vec3 = 12
const_vec4 = 16

# Lookup tables.
deform_type_bdef1 = 0
deform_type_bdef2 = 1
deform_type_bdef4 = 2
deform_type_sdef = 3
deform_type_qdef = 4
deform_lookup_table = {0: 'bdef1',
                       1: 'bdef2',
                       2: 'bdef4',
                       3: 'sdef',
                       4: 'qdef'}


def read_full_vertices_data(reader, struct_sizes, additional):
	num_vertices = read_uint(reader)
	vertices = []

	for i in range(0, num_vertices):
		vertex = read_full_vertex_data(reader, struct_sizes, additional)
		vertices.append(vertex)
	return vertices


def read_bdef1(reader, struct_sizes):
	index_size = struct_sizes['bone_index_size']
	return [read_index(reader, index_size)]


def read_bdef2(reader, struct_sizes):
	index_size = struct_sizes['bone_index_size']
	return [read_index(reader, index_size),
	        read_index(reader, index_size),
	        read_float(reader)]


def read_bdef4(reader, struct_sizes):
	index_size = struct_sizes['bone_index_size']
	return [read_index(reader, index_size),
	        read_index(reader, index_size),
	        read_index(reader, index_size),
	        read_index(reader, index_size),
	        read_float(reader),
	        read_float(reader),
	        read_float(reader),
	        read_float(reader)]


def read_sdef(reader, struct_sizes):
	index_size = struct_sizes['bone_index_size']
	return [read_index(reader, index_size),
	        read_index(reader, index_size),
	        read_float(reader),
	        read_vec3(reader),
	        read_vec3(reader),
	        read_vec3(reader)]


def read_qdef(reader, struct_sizes):
	index_size = struct_sizes['bone_index_size']
	return [read_index(reader, index_size),
	        read_index(reader, index_size),
	        read_index(reader, index_size),
	        read_index(reader, index_size),
	        read_float(reader),
	        read_float(reader),
	        read_float(reader),
	        read_float(reader)]


deform_lookup_function = [read_bdef1,
                          read_bdef2,
                          read_bdef4,
                          read_sdef,
                          read_qdef]


def read_full_vertex_data(reader, struct_sizes, additional):
	pos_normal_uv = unpack(b'ffffffff', reader.read(const_vec3 * 2 + const_vec2))
	additional_vec = []
	for i in range(0, additional):
		add_vec = read_vec4(reader.read(const_vec4))
		for f in add_vec:
			additional_vec.append(f)
	# Deforming data.
	weight_deform_type = read_ubyte(reader)

	#
	deform_func = deform_lookup_function[weight_deform_type]
	weight_data = deform_func(reader, struct_sizes)
	edge_scale = read_float(reader)

	#
	return {
		'vertex' : pos_normal_uv,
		'additional_vec' : additional_vec,
		'weight_deform_type' : weight_deform_type,
		'weight_data': weight_data,
		'edge_scale': edge_scale
	}
	#return list(pos_normal_uv) + additional_vec + [weight_deform_type] + [weight_data] + [edge_scale]


def read_full_surface_data(reader, struct_size):
	num_surfaces = read_uint(reader)
	surfaces = []
	surface_index_size = struct_size['vertex_index_size']
	for _ in range(0, num_surfaces):
		surfaces.append(read_index(reader, surface_index_size))
	return surfaces


def read_all_texture_paths(reader, struct_size):
	num_textures = read_int(reader)
	paths = []
	for j in range(0, num_textures):
		s, path = read_string_ubyte(reader)
		paths.append(path)
	return paths


def read_all_material(reader, struct_size):
	num_materials = read_int(reader)
	materials = []
	for _ in range(0, num_materials):
		_, local_name = read_string_ubyte(reader)
		_, universal_name = read_string_ubyte(reader)
		diffuse_color = read_vec4(reader)
		specular_color = read_vec3(reader)
		specular_intensity = read_float(reader)
		ambient_color = read_vec3(reader)
		flag = read_ubyte(reader)
		edge_color = read_vec4(reader)
		edge_scale = read_float(reader)
		texture_index = read_index(reader, struct_size['texture_index_size'])
		environment_index = read_index(reader, struct_size['texture_index_size'])
		Environmentblendmode = read_ubyte(reader)
		ToonReference = read_ubyte(reader)
		Toonvalue = read_ubyte(reader)
		meta = read_string_ubyte(reader)
		surface_count = read_int(reader)

		material = {
			'local_name': local_name,
			'universal_name': universal_name,
			'diffuse': diffuse_color,
			'specular_color': specular_color,
			'specular_intensity': specular_intensity,
			'ambient_color': ambient_color,
			'flag': flag,
			'edge_color': edge_color,
			'edge_scale': edge_scale,
			'texture_index': texture_index,
			'environment_index': environment_index,

			'environment_blend_mode': Environmentblendmode,
			'toon_reference': ToonReference,
			'toon_value': Toonvalue,

			'meta': meta,
			'surface_count': surface_count,
		}
		materials.append(material)
	# name,
	# name,
	# diffuse,
	# specular,
	# specular strength

	return materials


def read_all_bones(reader, struct_size):
	num_bones = read_uint(reader)
	bones = []
	for _ in range(0, num_bones):
		_, local_name = read_string_ubyte(reader, struct_size['text_encoding'])
		_, universal_name = read_string_ubyte(reader, struct_size['text_encoding'])

		pos = read_vec3(reader)
		index = read_index(reader, struct_size['bone_index_size'])
		layer = read_int(reader)
		flag = read_ushort(reader)

		bone = {
			'local_name': local_name,
			'universal_name': universal_name,
			'position': pos,
			'parent_bone': index,
			'layer': layer,
			'flag': flag,
		}

		#
		if flag & const_bone_flag_index_tail_position:
			tail_index = read_index(reader, struct_size['bone_index_size'])
			bone['tail_index'] = tail_index
		else:
			tail_pos = read_vec3(reader)
			bone['tail_pos'] = tail_pos

		# Inherit bone
		if flag & (const_bone_flag_inherit_rotation | const_bone_flag_inherit_translation):
			parent_index = read_index(reader, struct_size['bone_index_size'])
			parent_influence = read_float(reader)
			bone['parent_index'] = parent_index
			bone['parent_influence'] = parent_influence

		# Fixed axis
		if flag & const_bone_flag_fixed_axis:
			direction = read_vec3(reader)
			bone['direction'] = direction

		# Local co-coordinate
		if flag & const_bone_flag_local_co_coordinate:
			X_dir = read_vec3(reader)
			Z_dir = read_vec3(reader)
			bone['X_dir'] = X_dir
			bone['Z_dir'] = Z_dir

		# external parent
		if flag & const_bone_flag_external_parent_deform:
			external_parent_index = read_index(reader, struct_size['bone_index_size'])
			bone['external_parent_index'] = external_parent_index

		# IK.
		if flag & const_bone_flag_ik:
			target_index = read_index(reader, struct_size['bone_index_size'])
			loop_count = read_int(reader)
			loop_radian = read_float(reader)
			link_count = read_int(reader)

			bone['target_index'] = target_index
			bone['loop_count'] = loop_count
			bone['loop_radian'] = loop_radian
			bone['link_count'] = link_count
			limit_targets = []
			for n in range(0, link_count):
				bone_index = read_index(reader, struct_size['bone_index_size'])
				has_limit = read_ubyte(reader)
				link_target = {'bone_index': bone_index, 'has_limit': has_limit}
				if has_limit == 1:
					limit_min = read_vec3(reader)
					limit_max = read_vec3(reader)
					link_target['limit_min'] = limit_min
					link_target['limit_max'] = limit_max
				limit_targets.append(link_target)
			bone['links'] = limit_targets
		bones.append(bone)
	return bones


def read_morph_material(reader, struct_size):
	material_index = read_index(reader, struct_size['material_index_size'])
	_ = read_ubyte(reader)
	diffuse = read_vec4(reader)
	specular = read_vec3(reader)
	specularity = read_float(reader)
	ambient = read_vec3(reader)
	edge_color = read_vec4(reader)
	edge_size = read_float(reader)
	texture_int = read_vec4(reader)
	environment_tint = read_vec4(reader)
	toon_tint = read_vec4(reader)
	return {'material_index', material_index}


def read_morph_group(reader, struct_size):
	morph_index = read_index(reader, struct_size['morph_index_size'])
	influence = read_float(reader)
	return [morph_index, influence]


def read_morph_vertex(reader, struct_size):
	vertex_index = read_index(reader, struct_size['vertex_index_size'])
	translation = read_vec3(reader)
	return [vertex_index, translation]


def read_morph_bone(reader, struct_size):
	bone_index = read_index(reader, struct_size['bone_index_size'])
	translation = read_vec3(reader)
	rotation = read_vec4(reader)
	return [bone_index, translation, rotation]


def read_morph_uv(reader, struct_size):
	vertex_index = read_index(reader, struct_size['vertex_index_size'])
	uv = read_vec4(reader)
	return [vertex_index, uv]


def read_morph_flip(reader, struct_size):
	morph_index = read_index(reader, struct_size['morph_index_size'])
	influence = read_float(reader)
	return [morph_index, influence]


def read_morph_impulse(reader, struct_size):
	rigidbody_index = read_index(reader, struct_size['rigid_index_size'])
	local_flag = read_ubyte(reader)
	movement_speed = read_vec3(reader)
	rotation_torque = read_vec3(reader)
	return [rigidbody_index, local_flag, movement_speed, rotation_torque]


def read_all_morph(f, struct_sizes):
	num_morphs = read_int(f)
	morphs = []
	morph_type_parse_lookup = [read_morph_group, read_morph_vertex, read_morph_bone, read_morph_uv, read_morph_uv,
	                           read_morph_uv, read_morph_uv, read_morph_uv, read_morph_material, read_morph_flip,
	                           read_morph_impulse]
	for i in range(0, num_morphs):
		_, local_name = read_string_ubyte(f, struct_sizes['text_encoding'])
		_, universal_name = read_string_ubyte(f, struct_sizes['text_encoding'])
		panel_type = read_ubyte(f)
		morph_type = read_ubyte(f)
		offset_size = read_int(f)

		morph = {
			'local_name': local_name,
			'universal_name': universal_name,
			'morph_type': morph_type,
			'data' : []
		}
		#
		parse_func = morph_type_parse_lookup[morph_type]
		for _ in range(0, offset_size):
			morph['data'].append(parse_func(f, struct_sizes))
		morphs.append(morph)
	return morphs


def read_frame_bone(reader, struct_sizes):
	return [read_index(reader, struct_sizes['bone_index_size'])]


def read_frame_morph(reader, struct_sizes):
	return [read_index(reader, struct_sizes['morph_index_size'])]


def read_all_display_frames(f, struct_sizes):
	num_display_frames = read_int(f)

	display_frames = []
	frame_lookup_table = [read_frame_bone, read_frame_morph]
	for i in range(0, num_display_frames):
		#
		_, local_name = read_string_ubyte(f, struct_sizes['text_encoding'])
		_, universal_name = read_string_ubyte(f, struct_sizes['text_encoding'])

		special_flag = read_ubyte(f)
		frame_count = read_int(f)
		frame = {
			'local_name': local_name,
			'universal_name': universal_name,
			'frame_type': special_flag,
			'data': []
		}

		for _ in range(0, frame_count):
			frame_type = read_ubyte(f)

			frame['data'].append(frame_lookup_table[frame_type](f, struct_sizes))
			
		display_frames.append(frame)

	return display_frames


def read_all_rigidbodies(f, struct_sizes):
	num_rigidbodies = read_int(f)
	rigidbodies = []
	for _ in range(0, num_rigidbodies):
		_, local_name = read_string_ubyte(f)
		_, universal_name = read_string_ubyte(f)

		related_bone_index = read_index(f, struct_sizes['bone_index_size'])
		group_id = read_ubyte(f)
		non_collision_group = read_sint(f)

		shape = read_ubyte(f)
		shape_size = read_vec3(f)
		shape_position = read_vec3(f)
		shape_rotation = read_vec3(f)

		mass = read_float(f)
		move_attenuation = read_float(f)
		rotation_damping = read_float(f)
		repulsion = read_float(f)
		friction_force = read_float(f)

		physic_mode = read_ubyte(f)

		rigidbody = {
			'local_name': local_name,
			'universal_name': universal_name,

			'related_bone_index': related_bone_index,
			'group_id': group_id,
			'non_collision_group': non_collision_group,

			'shape': shape,
			'shape_size': shape_size,
			'shape_position': shape_position,
			'shape_rotation': shape_rotation,

			'mass': mass,
			'move_attenuation': move_attenuation,
			'rotation_damping': rotation_damping,
			'repulsion': repulsion,
			'friction_force': friction_force,
			'physic_mode': physic_mode 
		}

		rigidbodies.append(rigidbody)

	return rigidbodies


def read_all_joints(f, struct_sizes):
	num_joints = read_int(f)
	joints= []
	for a in range(0, num_joints):
		_, local_name = read_string_ubyte(f)
		_, universal_name = read_string_ubyte(f)
		joint_type = read_ubyte(f)
		rigidbody_indexA = read_index(f, struct_sizes['rigid_index_size'])
		rigidbody_indexB = read_index(f, struct_sizes['rigid_index_size'])

		position = read_vec3(f)
		rotation = read_vec3(f)
		position_min = read_vec3(f)
		position_max = read_vec3(f)
		rotation_min = read_vec3(f)
		rotation_max = read_vec3(f)
		spring_position = read_vec3(f)
		spring_rotation = read_vec3(f)

		joint = {
			'local_name': local_name,
			'universal_name': universal_name,

			'joint_type': joint_type,
			'rigidbody_indexA': rigidbody_indexA,
			'rigidbody_indexB': rigidbody_indexB,

			'position': position,
			'rotation': rotation,
			'position_min': position_min,
			'position_max': position_max,
			'rotation_min': rotation_min,
			'rotation_max': rotation_min,
			'spring_position': rotation_min,
			'spring_rotation': rotation_min
		}

		joints.append(joint)

	return joints


def read_all_softbody(f, struct_sizes):
	num_softbodies = read_int(f)
	softbodies = []
	for _ in range(0, num_softbodies):
		_, local_name = read_string_ubyte(f)
		_, universal_name = read_string_ubyte(f)
		shape = read_ubyte(f)
		material_index = read_index(f, struct_sizes['material_index_size'])
		group_id = read_ubyte(f)
		non_collision_group = read_sint(f)

		softbody = {
			'local_name': local_name,
			'universal_name': universal_name,
		}
		softbodies.append(softbody)
	return softbodies


def read_index(reader, size_type):
	size_hash_lookup = {1: read_ubyte, 2: read_ushort, 4: read_uint}
	lookup_func = size_hash_lookup[size_type]
	# data = reader.read(size_type)
	return lookup_func(reader)

def read_uint(read):
	return unpack(b'<I', read.read(const_int))[0]


def read_int(read):
	return unpack(b'<i', read.read(const_int))[0]


def read_sint(read):
	return unpack(b'H', read.read(const_short))[0]


def read_ushort(read):
	return unpack(b'h', read.read(const_short))[0]


def read_uint64(read):
	return unpack(b'<Q', read.read(const_uint64))[0]


def read_ubyte(read):
	return unpack(b'B', read.read(const_byte))[0]


def read_vec3(read):
	return unpack(b'fff', read.read(const_vec3))


def read_vec4(read):
	return unpack(b'ffff', read.read(const_vec4))


def read_float(read):
	return unpack(b'f', read.read(const_float))[0]


def read_string_ubyte(reader, encoding=0):
	size = read_uint(reader)
	data = reader.read(size)
	if encoding == 0:
		data = data.decode("utf-16", "strict")
	elif encoding == 1:
		data = data.decode("utf-8", "strict")
	return size, data


def unpack_array(read, array_type, array_stride, array_byteswap):
	length = read_uint(read)
	encoding = read_uint(read)
	comp_len = read_uint(read)

	data = read(comp_len)

	if encoding == 0:
		pass
	elif encoding == 1:
		data = zlib.decompress(data)

	assert (length * array_stride == len(data))

	data_array = array.array(array_type, data)
	#    if array_byteswap and _IS_BIG_ENDIAN:
	#        data_array.byteswap()
	return data_array


