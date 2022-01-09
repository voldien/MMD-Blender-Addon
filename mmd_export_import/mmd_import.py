# <pep8 compliant>

if "bpy" in locals():
	import importlib

	if "parse_mmd" in locals():
		importlib.reload(mmd_export_import.parse_mmd)
	if "mmd_util" in locals():
		importlib.reload(mmd_export_import.mmd_util)

import bpy
from bpy_extras import node_shader_utils

from bpy_extras.mesh_utils import ngon_tessellate

import mmd_export_import.parse_mmd as parse_mmd
import mmd_export_import.mmd_util as mmd_util

from mathutils import Matrix, Euler, Vector
import array
import os
import time
import bpy
import bmesh
import mathutils
from bpy_extras.io_utils import unpack_list
from bpy_extras.image_utils import load_image

import mathutils

if bpy.app.version >= (2, 80, 0):
	from bpy_extras.wm_utils.progress_report import ProgressReport
else:
	from ProgressReport import progress_report


def insensitive_path(path):
	# find the io_stream on unix
	directory = os.path.dirname(path)
	name = os.path.basename(path)

	for io_stream_name in os.listdir(directory):
		if io_stream_name.lower() == name.lower():
			path = os.path.join(directory, io_stream_name)
	return path


def load_mmd_images(mmd_file_root_path, texture_paths):
	images = []
	filepath_dir = os.path.dirname(mmd_file_root_path)
	for texture_filename in texture_paths:
		texture_absolute_path = str.format("{}{}{}", filepath_dir, os.path.sep, texture_filename)
		print(texture_absolute_path)
		texture = load_image(texture_absolute_path)
		if texture is not None:
			texture.name = texture_filename
		#	texture.alpha_mode = 'STRAIGHT'
		images.append(texture)
	return images


def create_materials(filepath, relpath,
					 material_libs, unique_materials, mmd_texture_object,
					 use_image_search, use_cycles, mmd_materials):
	DIR = os.path.dirname(filepath)
	texture_paths = DIR
	context_material_vars = set()

	# Don't load the same image multiple times
	context_imagepath_map = {}

	cycles_material_wrap_map = {}

	unique_material_images = {}

	bpy.ops.object.mode_set(mode='OBJECT')

	# make sure face select mode is enabled
	#	bpy.context.tool_settings.mesh_select_mode = [False, False, True]

	# Create new materials
	for m in mmd_materials:
		name = m['local_name']

		local_material = bpy.data.materials.new(name=
												name)
		# local_material.material_type = 'SHADER_MATERIAL'
		local_material.use_nodes = True
		local_material.blend_method = 'BLEND'
		local_material.show_transparent_back = False
		local_material.diffuse_color = m["diffuse"]
		local_material.specular_color = m["specular_color"]
		local_material.specular_intensity = m["specular_intensity"]

		# local_material.ambient = m["ambient_color"]
		m["environment_blend_mode"]
		toon_ref = m["toon_reference"]
		m["toon_value"]

		material_flag = m["flag"]
		if material_flag & parse_mmd.const_material_flag_nocull:
			local_material.use_backface_culling = False
		#		if material_flag & parse_mmd.const_material_flag_ground_shadow:
		#			local_material.use_backface_culling = Fals
		if material_flag & parse_mmd.const_material_flag_draw_shadow:
			local_material.shadow_method = 'OPAQUE'

		principled = node_shader_utils.PrincipledBSDFWrapper(local_material, is_readonly=False)
		principled.base_color = m["diffuse"][0:3]
		principled.alpha = m["diffuse"][3]

		texture_index = m["texture_index"]
		environment_index = m["environment_index"]
		if texture_index >= 0:
			principled.base_color_texture.image = mmd_texture_object[texture_index]
		# principled.alpha_texture.image = mmd_texture_object[texture_index]

		# principled.alpha = mmd_texture_object[texture_index].to_a()
		unique_materials.append(local_material)

	return unique_materials


def split_mesh(verts_loc, faces, unique_materials, filepath, SPLIT_OB_OR_GROUP):
	pass


# def new_bone(obj, bone_name):
#     """ Adds a new bone to the given armature object.
#         Returns the resulting bone's name.
#     """
#     if obj == bpy.context.active_object and bpy.context.mode == 'EDIT_ARMATURE':
#         edit_bone = obj.data.edit_bones.new(bone_name)
#         name = edit_bone.name
#         edit_bone.head = (0, 0, 0)
#         edit_bone.tail = (0, 1, 0)
#         edit_bone.roll = 0
#         return name
#     else:
#         raise MetarigError("Can't add new bone '%s' outside of edit mode" % bone_name)

def create_bone_system(bones):
	# view_layer = bpy.context.view_layer

	bone_objects = []
	bone_internal = {}

	def create_root_bone():
		# root = bpy.data.objects.new("")
		# bpy.data.objects.new(bones[0].['local_name'], None)  # parent_type='BONE'
		arm_data = bpy.data.armatures.new(name="")
		root = bpy.data.objects.new(name="Root", object_data=arm_data)

		# view_layer.active_layer_collection.collection.objects.link(amature)
		# amature.select_set(True)

		# instance in scene
		# old 2.8 obj_base = bpy.context.scene.objects.link(root)
		# 3.0
		obj_base = bpy.context.collection.objects.link(root)
		root.select_set(True)
		# obj_base.select = True

		# 3.0
		bpy.context.view_layer.objects.active = root
		# 2.8
		# bpy.context.collection.objects.active = root
		# is_hidden = root.hide
		# root.hide = False  # Can't switch to Edit mode hidden objects...
		return root

	root = create_root_bone()

	bpy.ops.object.mode_set(mode='EDIT')

	for i, bone in enumerate(bones):
		utf8_bone_name = bone['local_name']
		mmd_flags = bone['flag']
		arm_bone = root.data.edit_bones.new(name=utf8_bone_name)

		#		arm_bone.visable = mmd_flags & parse_mmd.const_bone_flag_is_visable

		if mmd_flags & parse_mmd.const_bone_flag_inherit_rotation == 0:
			arm_bone.use_inherit_rotation = False
		else:
			arm_bone.use_inherit_rotation = True
		# if mmd_flags & parse_mmd.const_bone_flag_inherit_translation == 0:
		#	arm_bone.use_inherit_rotation = False
		# else:
		#	arm_bone.use_inherit_rotation = True
		if mmd_flags & parse_mmd.const_bone_flag_local_co_coordinate:
			arm_bone.use_local_location = True
		else:
			arm_bone.use_local_location = False

		arm_bone.head = bone['position']
		arm_bone.layers[bone['layer']] = True
		bone_internal[bone['parent_bone']] = arm_bone
		bone_objects.append(arm_bone)

		if "tail_pos" in bone.keys():
			arm_bone.use_connect = False
			arm_bone.tail = bone['tail_pos']

	# Parent object.
	for i, bone in enumerate(bones):
		bone_index = bone['parent_bone']
		arm_bone = bone_objects[i]
		if bone_index >= 0:
			arm_parent_bone = bone_internal[bone_index]
			# Set parent and position.
			arm_bone.parent = arm_parent_bone

		if "tail_index" in bone.keys():
			tail_index = bone['tail_index']
			if tail_index >= 0:
				arm_bone.use_connect = False
				arm_bone.tail = bones[tail_index]['position']
			else:
				arm_bone.use_connect = True
				arm_bone.tail = (0, 0, 0)
	# if "X_dir" in bone.keys():
	# 	arm_bone.translate(bone['X_dir'])
	# 	arm_bone.translate(bone['Z_dir'])
	# Reset the state.
	bpy.ops.object.mode_set(mode='POSE')

	for i, bone in enumerate(bones):
		arm_bone = bone_objects[i]
		mmd_flags = bone['flag']
		if "parent_index" in bone.keys():
			parent_index = bone['parent_index']
			parent_influence = bone['parent_influence']

			pose_bone = root.pose.bones[i]
			child_of = pose_bone.constraints.new('CHILD_OF')
			# child_of = pose_bone.constraints.new('CHILD_OF')
			child_of.target = root
			child_of.subtarget = root.pose.bones[parent_index].name
			child_of.influence = parent_influence

		if mmd_flags & parse_mmd.const_bone_flag_ik:
			target_index = bone['target_index']
			chain_count = bone['link_count']

			pose_bone = root.pose.bones[i]
			ik = pose_bone.constraints.new('IK')
			ik.target = root
			ik.subtarget = root.pose.bones[target_index].name
			ik.chain_count = chain_count

	bpy.ops.object.mode_set(mode='OBJECT')
	root.hide_set(False)

	return root, bone_objects


def create_rigidbodies(bones, rigidbodies, joints):
	for rigidbody in rigidbodies:
		bone_link_obj = bones[rigidbody['related_bone_index']]

		# bpy.context.scene.rigidbody_world.group.objects.link(bone_link_obj)
		pass


def create_influence(bones, mesh):
	pass


def process_header(f):
	header = {}

	#
	header['signature'] = str(parse_mmd.read_uint(f))
	header['version'] = float(parse_mmd.read_float(f))

	# Validate the file type.
	if mmd_util.validate_version_signature(header['signature'], header['version']):
		print("Invalid")
	if header['version'] == 2.0:
		pass

	header['globals_count'] = parse_mmd.read_ubyte(f)

	data_section_names = ['Vertex', 'Face', 'Texture', 'Material',
						  'Bone', 'Morph', 'Frame', 'Rigidbody', 'Joint', 'Softbody']
	index_attribute_names = ['text_encoding', 'additional_vec4_count', 'vertex_index_size', 'texture_index_size',
							 'material_index_size',
							 'bone_index_size', 'morph_index_size', 'rigid_index_size']
	nindex = 0
	for n in index_attribute_names:
		# Continue grabbing index data only if additional exits.
		if nindex < header['globals_count']:
			header[n] = parse_mmd.read_ubyte(f)
			nindex = nindex + 1
	# Handle unused global index.
	if nindex < header['globals_count']:
		f.seek(header['globals_count'] - nindex)

	# Load name and comments.
	encoding = header['text_encoding']

	_, header['local_character_name'] = parse_mmd.read_string_ubyte(
		f, encoding)
	_, header['universal_character_name_size'] = parse_mmd.read_string_ubyte(
		f, encoding)
	_, header['comment_local'] = parse_mmd.read_string_ubyte(f, encoding)
	_, header['comment_universal'] = parse_mmd.read_string_ubyte(f, encoding)

	return header


def create_mesh(new_objects,
				use_edges,
				verts_loc,
				verts_nor,
				verts_tex,
				faces,
				unique_materials,
				unique_material_images,
				unique_smooth_groups,
				vertex_groups,
				use_material_import,
				dataname,
				):
	me = bpy.data.meshes.new(dataname)


def create_geometry(vertices, surfaces, bones, header, use_edges, unique_materials, use_material_import, mmd_materials):
	# if unique_smooth_groups:
	#     sharp_edges = set()
	#     smooth_group_users = {context_smooth_group: {}
	#                           for context_smooth_group in unique_smooth_groups.keys()}
	#     context_smooth_group_old = -1

	# Used for storing fgon keys when we need to tesselate/untesselate them (ngons with hole).
	fgon_edges = set()
	edges = []
	tot_loops = 0

	#additonal_uv = header["additional_vec"]

	vertices_data = []
	normal_data = []

	for i, v_ in enumerate(vertices):
		pos_normal_uv = v_['vertex']
		vertices_data.append((pos_normal_uv[0], pos_normal_uv[1], pos_normal_uv[2]))
		normal_data.append((pos_normal_uv[3], pos_normal_uv[4], pos_normal_uv[5]))

	triangles = []
	for i0, i1, i2 in zip(*[iter(surfaces)] * 3):
		assert i0 < len(vertices) and i1 < len(vertices) and i2 < len(vertices)
		assert i0 >= 0 and i1 >= 0 and i2 >= 0
		triangles.append((i0, i1, i2))

	mesh = bpy.data.meshes.new(name=
							   header['local_character_name'])  # add a new mesh
	print("assign data " + str(len(vertices_data)) + " " + str(len(triangles)))
	mesh.from_pydata(vertices_data, [], triangles)
	mesh.validate(verbose=True)

	mesh.normals_split_custom_set_from_vertices(normal_data)
	mesh.use_auto_smooth = True

	# mesh.object_type = 'MESH'
	# mesh.userText = mesh_struct.user_text
	# mesh.sort_level = mesh_struct.header.sort_level
	# mesh.casts_shadow = mesh_struct.casts_shadow()
	# mesh.two_sided = mesh_struct.two_sided()

	mesh_obj = bpy.data.objects.new(header['local_character_name'], mesh)
	mesh_obj.use_empty_image_alpha = True
	# # make sure the list isnt too big
	# for material in materials:
	#     me.materials.append(material)
	#
	# mesh.vertices.add(len(vertices))
	# mesh.loops.add(tot_loops)
	# mesh.polygons.add(len(surfaces) / 3)

	# Add object the scene.
	scene = bpy.context.scene

	bpy.context.collection.objects.link(mesh_obj)  # put the object into the scene (link)
	# 3.0
	bpy.context.view_layer.objects.active = mesh_obj
	# 2.8
	# scene.objects.active = obj  # set as the active object in the scene
	bpy.context.object.select_set(True)

	loops_vert_idx = []
	faces_loop_start = []
	faces_loop_total = []
	lidx = 0

	# me.loops.foreach_set("normal", loops_nor)
	b_mesh = bmesh.new()
	b_mesh.from_mesh(mesh)

	# uv.data[i].uv = v[6:7]
	# mesh.vertices.foreach_set("co", unpack_list(vertices_data))
	# mesh.loops.foreach_get("normal", unpack_list(normal_data))
	# #			bm.verts.new([v[0],v[1],v[2]])  # add a new vert

	#
	# for f in triangles:
	# 	print(f)
	# 	vidx = f
	# 	nbr_vidx = len(vidx)
	# 	loops_vert_idx.extend(vidx)
	# 	faces_loop_start.append(lidx)
	# 	faces_loop_total.append(nbr_vidx)
	# 	lidx += nbr_vidx

	# mesh.loops.foreach_set("vertex_index", loops_vert_idx)
	# mesh.polygons.foreach_set("loop_start", faces_loop_start)
	# mesh.polygons.foreach_set("loop_total", faces_loop_total)

	# Compute all groups used.
	#		vg = obj.vertex_groups

	# Load all UV data.
	# if verts_tex and me.polygons:
	# 	me.uv_textures.new()
	#	for
	# bpy.ops.object.vertex_group_add()
	# bpy.ops.object.shape_key_add(from_mix=False)
	# bpy.ops.mesh.uv_texture_add()
	#		vg.add([vertice index], weight, "ADD")
	# me.vertices.add(len(verts_loc))
	# me.loops.add(tot_loops)
	# mesh.face.new(surfaces)

	bpy.ops.object.mode_set(mode='OBJECT')
	# mesh.from_pydata(vertices_data, [], facesData)
	# important to not remove loop normals here!

	uv_layer = mesh.uv_layers.new(do_init=False)
	uv_layer.name = "UV"
	for i, face in enumerate(b_mesh.faces):
		for loop in face.loops:
			idx = triangles[i][loop.index % 3]
			pos_normal_uv = vertices[idx]['vertex']
			uv_layer.data[loop.index].uv = (pos_normal_uv[6], pos_normal_uv[7])
	for i in range(0, additonal_uv):
		uv_layer = mesh.uv_layers.new(do_init=False)
		uv_layer.name = "expand UV" + str(i)

	# Create all the weight groups from the bones.
	for bone in bones:
		mesh_obj.vertex_groups.new(name="")

	# Assign all bone vertex influence.
	for i, vertex in enumerate(vertices):
		vertex_indices = i
		deform_type = vertex['weight_deform_type']
		weight_data = vertex['weight_data']

		if deform_type == parse_mmd.deform_type_bdef1:
			bone_index1 = weight_data[0]
			mesh_obj.vertex_groups[bone_index1].add(
				[vertex_indices], 1, 'REPLACE')
		elif deform_type == parse_mmd.deform_type_bdef2:
			bone_index1 = weight_data[0]
			bone_index2 = weight_data[1]
			weight = weight_data[2]
			mesh_obj.vertex_groups[bone_index1].add(
				[vertex_indices], weight, 'REPLACE')
			mesh_obj.vertex_groups[bone_index2].add(
				[vertex_indices], 1.0 - weight, 'REPLACE')
		elif deform_type == parse_mmd.deform_type_bdef4:
			bone_index1 = weight_data[0]
			bone_index2 = weight_data[1]
			bone_index3 = weight_data[2]
			bone_index4 = weight_data[3]
			weight1 = weight_data[4]
			weight2 = weight_data[5]
			weight3 = weight_data[6]
			weight4 = weight_data[7]
			mesh_obj.vertex_groups[bone_index1].add(
				[vertex_indices], weight1, 'REPLACE')
			mesh_obj.vertex_groups[bone_index2].add(
				[vertex_indices], weight2, 'REPLACE')
			mesh_obj.vertex_groups[bone_index3].add(
				[vertex_indices], weight3, 'REPLACE')
			mesh_obj.vertex_groups[bone_index4].add(
				[vertex_indices], weight4, 'REPLACE')
		elif deform_type == parse_mmd.deform_type_sdef:
			pass
		elif deform_type == parse_mmd.deform_type_qdef:
			bone_index1 = weight_data[0]
			bone_index2 = weight_data[1]
			bone_index3 = weight_data[2]
			bone_index4 = weight_data[3]
			weight1 = weight_data[4]
			weight2 = weight_data[5]
			weight3 = weight_data[6]
			weight4 = weight_data[7]
			mesh_obj.vertex_groups[bone_index1].add(
				[vertex_indices], weight1, 'REPLACE')
			mesh_obj.vertex_groups[bone_index2].add(
				[vertex_indices], weight2, 'REPLACE')
			mesh_obj.vertex_groups[bone_index3].add(
				[vertex_indices], weight3, 'REPLACE')
			mesh_obj.vertex_groups[bone_index4].add(
				[vertex_indices], weight4, 'REPLACE')
		else:
			assert 0

	mesh.update()
	mesh.validate(clean_customdata=False)

	# mesh.polygons.foreach_set("use_smooth", [True] * len(mesh.polygons))
	# mesh.normals_split_custom_set(normal_data)
	# bpy.ops.object.mode_set(mode='OBJECT')

	return mesh_obj, mesh


# TODO relocate to common
def compute_vertex_strip_size(header):
	return {'bdef1': header['bone_index_size'],
			'bdef2': header['bone_index_size'] * 2 + parse_mmd.const_float,
			'bdef4': header['bone_index_size'] * 4 + parse_mmd.const_float * 4,
			'sdef': header['bone_index_size'] * 2 + parse_mmd.const_float + parse_mmd.const_vec3 * 3,
			'qdef': header['bone_index_size'] * 4 + parse_mmd.const_float * 4,
			# TOOD add more.
			}


def load(context,
		 filepath,
		 *,
		 global_clamp_size=0.0,
		 use_edges=True,
		 use_image_search=True,
		 use_cycles=True,
		 relpath=None,
		 use_material_import,
		 use_joint_import,
		 global_matrix=None
		 ):
	"""
		Process:
			- Read Header
			- Extract Data
				- Extracting Vertices
				- Extract Surface
				- Extract Texture Paths
				- Extract Material
				- Bones
				- Morph
				- Display Frame
				- Rigidbody
				- Joints
				- Softbodies
	"""
	view_layer = context.view_layer

	with ProgressReport() as progress:
		progress.enter_substeps(1, str.format(
			"Importing MMD file: {}...", filepath))

		if global_matrix is None:
			global_matrix = mathutils.Matrix()

		time_main = time.time()

		verts_loc = []
		verts_nor = []
		verts_tex = []
		faces = []
		material_libs = set()
		vertex_groups = {}
		unique_materials = []

		progress.enter_substeps(3, "Parsing MMD file... " + filepath)

		with open(filepath, 'rb') as f:
			# Get information about the model and its internal.
			header = process_header(f)
			struct_sizes = compute_vertex_strip_size(header)
			header.update(struct_sizes)

			mmd_version = header['version']
			# Loading all required data.
			if mmd_version >= 2.0:
				# Extracting Vertices
				progress.enter_substeps(1, "Extracting Vertex Data...")
				additional_v4_count = header['additional_vec4_count']
				mmd_vertices = parse_mmd.read_full_vertices_data(
					f, header, header['additional_vec4_count'])
				# print("vertex count: " + str(len(vertices)))

				# Extract Surface data.
				progress.enter_substeps(1, "Extracting Surface Data...")
				mdd_surfaces = parse_mmd.read_full_surface_data(f, header)
				print("surface count: " + str(len(mdd_surfaces)))

				# Extract Texture Paths
				progress.enter_substeps(1, "Extracting Texture Path Data...")
				mmd_texture_paths = parse_mmd.read_all_texture_paths(f, header)
				# mmd_texture_paths = mmd_util.get_absolute_path(filepath, mmd_texture_paths)
				print(mmd_texture_paths)

				# Extract material Data
				progress.enter_substeps(1, "Extracting Material Data...")
				mmd_materials = parse_mmd.read_all_material(f, header)
				# print(materials)

				# Extract Bone data
				mmd_bones = parse_mmd.read_all_bones(f, header)
				# print(bones)

				# Extract Morph
				mmd_morphs = parse_mmd.read_all_morph(f, header)
				print(mmd_morphs)

				# Displayframe count
				mmd_displayFrames = parse_mmd.read_all_display_frames(f, header)
				print(mmd_displayFrames)
				# Rigidbody count
				mmd_rigidbodies = parse_mmd.read_all_rigidbodies(f, header)
				print(mmd_rigidbodies)
				# # Joint count
				mmd_joints = parse_mmd.read_all_joints(f, header)
				print(mmd_joints)
			if mmd_version >= 2.1:
				mmd_softbodies = parse_mmd.read_all_softbody(f, header)
				print(mmd_softbodies)

			# Check position and the size of the file and report the state of parsing the file.
			size = os.path.getsize(filepath)
			left = size - f.tell()
			print(left)

		# context.info("")
		# Construct material

		# materials_set = create_materials(filepath, relpath, material_libs, unique_materials,
		#								 unique_material_images, use_image_search, use_cycles, float_func)

		#
		progress.step("Done, loading bone skeleton system...")
		root, bone_objects = create_bone_system(mmd_bones)

		# Construct mesh data object.
		mesh_object, mesh = create_geometry(
			mmd_vertices, mdd_surfaces, bone_objects, header, use_edges, None, use_material_import, mmd_materials)
		mesh_object.parent = root

		# Construct rigidbodies
		create_rigidbodies(bone_objects, mmd_rigidbodies, mmd_joints)

		# Load all the image files
		progress.step("Done, loading texture/images...")
		mmd_texture_object = load_mmd_images(filepath, mmd_texture_paths)

		progress.step("Done, material...")
		object_materials = create_materials(filepath, mmd_texture_paths, material_libs, unique_materials,
											mmd_texture_object, use_image_search, use_cycles,
											mmd_materials=mmd_materials)

		assert len(object_materials) == len(mmd_materials)

		mesh_object.select_set(True)
		context.view_layer.objects.active = mesh_object
		for material in object_materials:
			mesh_object.data.materials.append(material)

		bpy.ops.object.mode_set(mode='EDIT')
		b_mesh = bmesh.from_edit_mesh(mesh)
		face = b_mesh.faces
		for s in face:
			s.select = False

		# for i, face in enumerate(b_mesh.faces):
		# 	for loop in face.loops:
		# 		idx = triangles[i][loop.index % 3]
		# 		pos_normal_uv = vertices[idx]['vertex']
		# 		uv_layer.data[loop.index].uv = (pos_normal_uv[6], pos_normal_uv[7])
		#
		material_offset = 0
		for i, material in enumerate(mmd_materials):
			print(str(i))
			surface_count = int(material["surface_count"] / 3)
			select_surface = b_mesh.faces[material_offset:material_offset + surface_count]
			for s in select_surface:
				s.select = True
			bpy.context.object.active_material_index = i
			bpy.ops.object.material_slot_assign()

			bpy.ops.object.material_slot_deselect()
			material_offset += surface_count

		print(str(material_offset * 3) + " " + str(int(material["surface_count"])) + "\n")
		assert material_offset * 3 == material["surface_count"]

		bmesh.update_edit_mesh(mesh=mesh)
		bpy.ops.object.mode_set(mode='OBJECT')

		progress.step("Done, building geometries (verts:{0} faces:{1} materials: {2}) ...",
					  (len(verts_loc), len(faces), len(unique_materials)))

		progress.step("Done, loading geometry data..")

		progress.step("Done, loading materials and images...")

		# Morph

		# mesh.polygons.add(len(surfaces))
		# mesh.polygons.foreach_set("vertices", surfaces)

		#	bmesh.ops.triangulate(bm, faces=bm.faces)
		#	bm.to_mesh(mesh)
		#	bm.free()  # always do this when finished

		# deselect all
		if bpy.ops.object.select_all.poll():
			bpy.ops.object.select_all(action='DESELECT')

		# Name the character.
		root.name = header['local_character_name']
		scene = context.scene
		new_objects = []  # put new objects here

		#	create_mesh

		# scene.update()

		axis_min = [1000000000] * 3
		axis_max = [-1000000000] * 3

		progress.leave_substeps("Done.")
		progress.leave_substeps(str.format("Finished importing: {}", filepath))

	return {'FINISHED'}
