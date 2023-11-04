# <pep8 compliant>
from struct import unpack
from typing import Type

import ntpath
import os
from unittest.result import failfast

from mmd_export_import import mmd_util
from mmd_export_import.mmd_util import read_uint, read_float, read_ubyte, read_string_ubyte, read_vec3, read_index, \
	read_int, read_ushort, read_vec4, read_signed_index, read_signed_short

from mmd_export_import.pmx import pmx_const_float, pmx_const_vec3, pmx_magic_signature, pmx_const_vec4, pmx_const_vec2


class Vertices:
	vertices : list[tuple[float]] = []

	def __init__(self, stride):
		self.stride = stride

	def get_stride(self):
		self.stride

	def get_vertices(self):
		return self.vertices


class Surface:
	pass


class Morph:
	pass


class Material:
	pass


class Joint:
	pass


class Bone:
	pass


class MMDParser:
	class Header:
		class PMXSetting:
			def __init__(self):
				pass

		def __init__(self, file):
			self.comment_universal = None
			self.comment_local = None
			self.local_character_name = None
			self.globals_count = None
			self.version = None
			self.signature = None

			# TODO check for type.
			#if isinstance(file) == type(list):
			#	pass
			self.parse(self, file)

		#
		encoding = 0
		uv = 0
		vertex_index_size = 0
		texture_index_size = 0
		material_index_size = 0
		bone_index_size = 0
		morph_index_size = 0
		rigidbody_index_size = 0

		def parse(self, file):
			header_settings = self.get_settings()

			#
			self.signature = str(read_uint(file))
			self.version = float(read_float(file))

			# Validate the file type.
			if mmd_util.validate_version_signature(self.signature, self.version):
				raise failfast("")
			if self.version == 2.0:
				pass

			self.globals_count = read_ubyte(file)

			data_section_names = ['Vertex', 'Face', 'Texture', 'Material',
			                      'Bone', 'Morph', 'Frame', 'Rigidbody', 'Joint', 'Softbody']

			index_attribute_names = ['text_encoding', 'additional_vec4_count', 'vertex_index_size',
			                         'texture_index_size',
			                         'material_index_size',
			                         'bone_index_size', 'morph_index_size', 'rigid_index_size']
			nindex = 0
			for n in index_attribute_names:
				# Continue grabbing index data only if additional exits.
				if nindex < self.globals_count:
					header[n] = parse_mmd.read_ubyte(file)
					nindex = nindex + 1

			# Handle unused global index.
			if nindex < self.globals_count:
				file.seek(self.globals_count - nindex)

			# Load name and comments.
			encoding = self.text_encoding

			_, self.local_character_name = read_string_ubyte(
				file, encoding)
			_, self.universal_character_name_size = read_string_ubyte(
				file, encoding)
			_, self.comment_local = read_string_ubyte(file, encoding)
			_, self.comment_universal = read_string_ubyte(file, encoding)

			return file.pos

		@staticmethod
		def validate_version_signature(signature: tuple, version) -> bool:
			magic_signature = pmx_magic_signature
			if version > 2.0:
				pass
			for i, l in enumerate(signature):
				if magic_signature[i] != l:
					return False
			return True

		def compute_vertex_strip_size(self):
			return {'bdef1': header['bone_index_size'],
			        'bdef2': header['bone_index_size'] * 2 + pmx_const_float,
			        'bdef4': header['bone_index_size'] * 4 + pmx_const_float * 4,
			        'sdef': header['bone_index_size'] * 2 + pmx_const_float + pmx_const_vec3 * 3,
			        'qdef': header['bone_index_size'] * 4 + pmx_const_float * 4,
			        # TOOD add more.
			        }

		def get_name(self) -> str:
			return self.name

		def get_settings(self) -> PMXSetting:
			return self.setting

		def get_version(self) -> int:
			return self.version

	path = None
	vertices = Vertices
	materials = []
	joints = []
	bones = []
	header = None  # Header()

	def __init__(self):
		self.mmd_joints = None
		self.mmd_rigidbodies = None
		self.mmd_texture_paths = None
		self.mmd_displayFrames = None
		self.mmd_vertices = None
		self.mmd_morphs = None
		self.mmd_bones = None
		self.mmd_materials = None
		self.mdd_surfaces = None
		self.path = None

	def __init__(self, filepath):
		self.path = filepath

		with open(filepath, 'rb') as f:
			self.header = MMDParser.Header(f)
			self.parse(f)

	def get_version(self):
		return self.header.version

	def parse(self, file):

		# Get information about the model and its internal.
		struct_sizes = compute_vertex_strip_size(header)
		header.update(struct_sizes)

		mmd_version = self.header.get_version()

		additional_v4_count = header['additional_vec4_count']

		# Loading all required data.
		if mmd_version >= 2.0:
			# Extracting Vertices
			progress.enter_substeps(1, "Extracting Vertex Data...")

			self.mmd_vertices = parse_mmd.read_full_vertices_data(
				file, self.header, additional_vec4=additional_v4_count)
			# print("vertex count: " + str(len(vertices)))

			# Extract Surface data.
			progress.enter_substeps(1, "Extracting Surface Data...")
			self.mdd_surfaces = parse_mmd.read_full_surface_data(file, self.header)
			print("surface count: " + str(len(mdd_surfaces)))

			# Extract Texture Paths
			progress.enter_substeps(1, "Extracting Texture Path Data...")
			self.mmd_texture_paths = parse_mmd.read_all_texture_paths(file, header)
			# mmd_texture_paths = mmd_util.get_absolute_path(filepath, mmd_texture_paths)

			# Extract material Data
			progress.enter_substeps(1, "Extracting Material Data...")
			self.mmd_materials = self.read_all_material(file, self.header)

			# Extract Bone data
			self.mmd_bones = parse_mmd.read_all_bones(file, header)

			# Extract Morph
			self.mmd_morphs = parse_mmd.read_all_morph(file, header)

			# Displayframe count
			self.mmd_displayFrames = parse_mmd.read_all_display_frames(file, header)

			# Rigidbody count
			self.mmd_rigidbodies = parse_mmd.read_all_rigidbodies(file, header)

			# Joint count
			self.mmd_joints = parse_mmd.read_all_joints(file, header)

		if mmd_version >= 2.1:
			mmd_softbodies = parse_mmd.read_all_softbody(file, header)

	def getVertices(self) -> Type[Vertices]:
		return Vertices()

	def getSurface(self) -> Surface:
		return Surface()

	def getMaterials(self):
		return None

	def getBones(self):
		return None

	def getMorphs(self):
		return None

	def getDisplayFrames(self):
		return None

	def getRigidBodies(self):
		return None

	def getJoints(self):
		return None

	def read_full_vertices_data(reader, struct_sizes, additional_vec4):
		num_vertices = read_uint(reader)
		vertices = []

		for i in range(0, num_vertices):
			vertex = read_full_vertex_data(reader, struct_sizes, additional_vec4)
			vertices.append(vertex)
		return vertices

	def write_full_vertices_data(writer, struct_sizes, vertices, additional):
		num_vertices = len(vertices)

		for i in range(0, num_vertices):
			pass

	# {
	# 	'vertex': pos_normal_uv,
	# 	'additional_vec': additional_vec,
	# 	'weight_deform_type': weight_deform_type,
	# 	'weight_data': weight_data,
	# 	'edge_scale': edge_scale
	# }
	@staticmethod
	def read_bdef1(reader, struct_sizes):
		index_size = struct_sizes['bone_index_size']
		return [read_index(reader, index_size)]

	@staticmethod
	def read_bdef2(reader, struct_sizes):
		index_size = struct_sizes['bone_index_size']
		return [read_index(reader, index_size),
		        read_index(reader, index_size),
		        read_float(reader)]

	@staticmethod
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

	@staticmethod
	def read_sdef(reader, struct_sizes):
		index_size = struct_sizes['bone_index_size']
		return [read_index(reader, index_size),
		        read_index(reader, index_size),
		        read_float(reader),
		        read_vec3(reader),
		        read_vec3(reader),
		        read_vec3(reader)]

	@staticmethod
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

	@staticmethod
	def read_full_vertex_data(reader, struct_sizes, additional_vec4):
		pos_normal_uv = unpack(b'ffffffff', reader.read(pmx_const_vec3 * 2 + pmx_const_vec2))
		additional_vec = []
		for i in range(0, additional_vec4):
			add_vec = read_vec4(reader.read(pmx_const_vec4))
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
			'vertex': pos_normal_uv,
			'additional_vec': additional_vec,
			'weight_deform_type': weight_deform_type,
			'weight_data': weight_data,
			'edge_scale': edge_scale
		}

	# return list(pos_normal_uv) + additional_vec + [weight_deform_type] + [weight_data] + [edge_scale]
	@staticmethod
	def read_full_surface_data(reader, struct_size):
		num_surfaces = read_uint(reader)
		surfaces = []
		surface_index_size = struct_size['vertex_index_size']
		for _ in range(0, num_surfaces):
			surfaces.append(read_index(reader, surface_index_size))
		return surfaces

	@staticmethod
	def read_all_texture_paths(reader, struct_size):
		num_textures = read_int(reader)
		paths = []
		for j in range(0, num_textures):
			s, path = read_string_ubyte(reader)
			paths.append(path.replace(os.sep, ntpath.sep).replace("\\", os.sep))
		return paths

	@staticmethod
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
			texture_index = read_signed_index(reader, struct_size['texture_index_size'])
			environment_index = read_signed_index(reader, struct_size['texture_index_size'])
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

	@staticmethod
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
				tail_index = read_signed_index(reader, struct_size['bone_index_size'])
				bone['tail_index'] = tail_index
			else:
				tail_pos = read_vec3(reader)
				bone['tail_pos'] = tail_pos

			# Inherit bone
			if flag & (const_bone_flag_inherit_rotation | const_bone_flag_inherit_translation):
				parent_index = read_signed_index(reader, struct_size['bone_index_size'])
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

	@staticmethod
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

	@staticmethod
	def read_morph_group(reader, struct_size):
		morph_index = read_index(reader, struct_size['morph_index_size'])
		influence = read_float(reader)
		return [morph_index, influence]

	@staticmethod
	def read_morph_vertex(reader, struct_size):
		vertex_index = read_index(reader, struct_size['vertex_index_size'])
		translation = read_vec3(reader)
		return [vertex_index, translation]

	@staticmethod
	def read_morph_bone(reader, struct_size):
		bone_index = read_index(reader, struct_size['bone_index_size'])
		translation = read_vec3(reader)
		rotation = read_vec4(reader)
		return [bone_index, translation, rotation]

	@staticmethod
	def read_morph_uv(reader, struct_size):
		vertex_index = read_index(reader, struct_size['vertex_index_size'])
		uv = read_vec4(reader)
		return [vertex_index, uv]

	@staticmethod
	def read_morph_flip(reader, struct_size):
		morph_index = read_index(reader, struct_size['morph_index_size'])
		influence = read_float(reader)
		return [morph_index, influence]

	@staticmethod
	def read_morph_impulse(reader, struct_size):
		rigidbody_index = read_index(reader, struct_size['rigid_index_size'])
		local_flag = read_ubyte(reader)
		movement_speed = read_vec3(reader)
		rotation_torque = read_vec3(reader)
		return [rigidbody_index, local_flag, movement_speed, rotation_torque]

	@staticmethod
	def read_all_morph(f, struct_sizes):
		num_morphs = read_int(f)
		morph_targets = []
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
				'data': []
			}
			#
			parse_func = morph_type_parse_lookup[morph_type]
			for _ in range(0, offset_size):
				morph['data'].append(parse_func(f, struct_sizes))
			morph_targets.append(morph)
		return morph_targets

	@staticmethod
	def read_frame_bone(reader, struct_sizes):
		return [read_index(reader, struct_sizes['bone_index_size'])]

	@staticmethod
	def read_frame_morph(reader, struct_sizes):
		return [read_index(reader, struct_sizes['morph_index_size'])]

	@staticmethod
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

				frame['data'].append((frame_type, frame_lookup_table[frame_type](f, struct_sizes)))

			display_frames.append(frame)

		return display_frames

	@staticmethod
	def read_all_rigidbodies(f, struct_sizes):
		num_rigidbodies = read_int(f)
		rigidbodies = []
		for _ in range(0, num_rigidbodies):
			_, local_name = read_string_ubyte(f)
			_, universal_name = read_string_ubyte(f)

			related_bone_index = read_index(f, struct_sizes['bone_index_size'])
			group_id = read_ubyte(f)
			non_collision_group = read_signed_short(f)

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

	@staticmethod
	def read_all_joints(f, struct_sizes):
		num_joints = read_int(f)
		joints = []
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

	@staticmethod
	def read_all_softbody(f, struct_sizes):
		num_softbodies = read_int(f)
		softbodies = []
		for _ in range(0, num_softbodies):
			_, local_name = read_string_ubyte(f)
			_, universal_name = read_string_ubyte(f)
			shape = read_ubyte(f)
			material_index = read_index(f, struct_sizes['material_index_size'])
			group_id = read_ubyte(f)
			non_collision_group = read_signed_short(f)

			softbody = {
				'local_name': local_name,
				'universal_name': universal_name,
			}
			softbodies.append(softbody)
		return softbodies

# # Get information about the model and its internal.
# 	header = process_header(f)
# 	struct_sizes = compute_vertex_strip_size(header)
# 	header.update(struct_sizes)
#
# 	mmd_version = header['version']
# 	assert isinstance(mmd_version, float)
#
# 	additional_v4_count = header['additional_vec4_count']
#
# 	# Loading all required data.
# 	if mmd_version >= 2.0:
# 		# Extracting Vertices
# 		progress.enter_substeps(1, "Extracting Vertex Data...")
#
# 		mmd_vertices = parse_mmd.read_full_vertices_data(
# 			f, header, additional_vec4=additional_v4_count)
# 		# print("vertex count: " + str(len(vertices)))
#
# 		# Extract Surface data.
# 		progress.enter_substeps(1, "Extracting Surface Data...")
# 		mdd_surfaces = parse_mmd.read_full_surface_data(f, header)
# 		print("surface count: " + str(len(mdd_surfaces)))
#
# 		# Extract Texture Paths
# 		progress.enter_substeps(1, "Extracting Texture Path Data...")
# 		mmd_texture_paths = parse_mmd.read_all_texture_paths(f, header)
# 		# mmd_texture_paths = mmd_util.get_absolute_path(filepath, mmd_texture_paths)
# 		print(mmd_texture_paths)
#
# 		# Extract material Data
# 		progress.enter_substeps(1, "Extracting Material Data...")
# 		mmd_materials = parse_mmd.read_all_material(f, header)
# 		# print(materials)
#
# 		# Extract Bone data
# 		mmd_bones = parse_mmd.read_all_bones(f, header)
# 		# print(bones)
#
# 		# Extract Morph
# 		mmd_morphs = parse_mmd.read_all_morph(f, header)
# 		# print(mmd_morphs)
#
# 		# Displayframe count
# 		mmd_displayFrames = parse_mmd.read_all_display_frames(f, header)
# 		# print(mmd_displayFrames)
# 		# Rigidbody count
# 		mmd_rigidbodies = parse_mmd.read_all_rigidbodies(f, header)
# 		# print(mmd_rigidbodies)
# 		# # Joint count
# 		mmd_joints = parse_mmd.read_all_joints(f, header)
# 	# print(mmd_joints)
# 	if mmd_version >= 2.1:
# 		mmd_softbodies = parse_mmd.read_all_softbody(f, header)
# # print(mmd_softbodies)
#
# header['signature'] = str(parse_mmd.read_uint(f))
# header['version'] = float(parse_mmd.read_float(f))
#
# # Validate the file type.
# if mmd_util.validate_version_signature(header['signature'], header['version']):
# 	print("Invalid")
# if header['version'] == 2.0:
# 	pass
#
# header['globals_count'] = parse_mmd.read_ubyte(f)
#
# data_section_names = ['Vertex', 'Face', 'Texture', 'Material',
# 					  'Bone', 'Morph', 'Frame', 'Rigidbody', 'Joint', 'Softbody']
# index_attribute_names = ['text_encoding', 'additional_vec4_count', 'vertex_index_size', 'texture_index_size',
# 						 'material_index_size',
# 						 'bone_index_size', 'morph_index_size', 'rigid_index_size']
# nindex = 0
# for n in index_attribute_names:
# 	# Continue grabbing index data only if additional exits.
# 	if nindex < header['globals_count']:
# 		header[n] = parse_mmd.read_ubyte(f)
# 		nindex = nindex + 1
# # Handle unused global index.
# if nindex < header['globals_count']:
# 	f.seek(header['globals_count'] - nindex)
#
# # Load name and comments.
# encoding = header['text_encoding']
#
# _, header['local_character_name'] = parse_mmd.read_string_ubyte(
# 	f, encoding)
# _, header['universal_character_name_size'] = parse_mmd.read_string_ubyte(
# 	f, encoding)
# _, header['comment_local'] = parse_mmd.read_string_ubyte(f, encoding)
# _, header['comment_universal'] = parse_mmd.read_string_ubyte(f, encoding)
#
# return header


# TODO flip UV
