# <pep8 compliant>
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
