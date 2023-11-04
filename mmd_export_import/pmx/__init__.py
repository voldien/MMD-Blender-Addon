# <pep8 compliant>
import mmd_export_import.pmx.mmd_joints
import mmd_export_import.pmx.mmd_bones
import mmd_export_import.pmx.mmd_material
import mmd_export_import.pmx.mmd_morphs
import mmd_export_import.pmx.mmd_vertices

#
pmx_data_section_names = ['Vertex', 'Face', 'Texture', 'Material',
                      'Bone', 'Morph', 'Frame', 'Rigidbody', 'Joint', 'Softbody']
#
pmx_index_attribute_names = ['text_encoding', 'additional_vec4_count', 'vertex_index_size', 'texture_index_size',
                         'material_index_size',
                         'bone_index_size', 'morph_index_size', 'rigid_index_size']

pmx_magic_signature = [0x50, 0x4D, 0x58, 0x20]

# Morph flag types.
pmx_const_morph_type_group = 0
pmx_const_morph_type_vertex = 1
pmx_const_morph_type_bone = 2
pmx_const_morph_type_uv = 3
pmx_const_morph_type_uv_ext1 = 4
pmx_const_morph_type_uv_ext2 = 5
pmx_const_morph_type_uv_ext3 = 6
pmx_const_morph_type_material = 8
pmx_const_morph_type_flip = 9
pmx_const_morph_type_impulse = 10

# Frame flag type
pmx_const_frame_type_bone = 0
pmx_const_frame_type_morph = 1

# Material flags.
pmx_const_material_flag_no_culling = 0x1
pmx_const_material_flag_ground_shadow = 0x2
pmx_const_material_flag_draw_shadow = 0x4
pmx_const_material_flag_receive_shadow = 0x8
pmx_const_material_flag_has_edge = 0x10
pmx_const_material_flag_vertex_color = 0x20
pmx_const_material_flag_point_drawing = 0x40
pmx_const_material_flag_line_drawing = 0x80

# Bone flags.
pmx_const_bone_flag_index_tail_position = 0x1
pmx_const_bone_flag_rotatable = 0x2
pmx_const_bone_flag_translatable = 0x4
pmx_const_bone_flag_is_visible = 0x8
pmx_const_bone_flag_enabled = 0x10
pmx_const_bone_flag_ik = 0x20
pmx_const_bone_flag_inherit_rotation = 0x100
pmx_const_bone_flag_inherit_translation = 0x200
pmx_const_bone_flag_fixed_axis = 0x400
pmx_const_bone_flag_local_co_coordinate = 0x800
pmx_const_bone_flag_physic_deform = 0x1000
pmx_const_bone_flag_external_parent_deform = 0x2000

# Data types size in bytes.
pmx_const_byte = 1
pmx_const_sbyte = 1
pmx_const_short = 2
pmx_const_ushort = 2
pmx_const_int = 4
pmx_const_uint = 4
pmx_const_uint64 = 8
pmx_const_float = 4
pmx_const_flag = 1
# Vector size in bytes.
pmx_const_vec2 = 8
pmx_const_vec3 = 12
pmx_const_vec4 = 16

# Lookup tables.
pmx_deform_type_bdef1 = 0
pmx_deform_type_bdef2 = 1
pmx_deform_type_bdef4 = 2
pmx_deform_type_sdef = 3
pmx_deform_type_qdef = 4
pmx_deform_lookup_table = {0: 'bdef1',
                           1: 'bdef2',
                           2: 'bdef4',
                           3: 'sdef',
                           4: 'qdef'}
