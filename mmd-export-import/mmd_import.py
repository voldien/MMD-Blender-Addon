# if "bpy" in locals():
if "bpy" in locals():
	import importlib

	if "parse_mmd" in locals():
		importlib.reload(parse_mmd)
	if "mmd_util" in locals():
		importlib.reload(mmd_util)

from . import parse_mmd
from . import mmd_util
import bpy
from struct import unpack

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
from progress_report import ProgressReport


def image_load(context_imagepath_map, line, DIR, recursive, relpath):
	filepath_parts = line.split(b' ')
	image = None
	for i in range(-1, -len(filepath_parts), -1):
		imagepath = os.fsdecode(b" ".join(filepath_parts[i:]))
		image = context_imagepath_map.get(imagepath, ...)
		if image is ...:
			image = load_image(imagepath, DIR, recursive=recursive, relpath=relpath)
			if image is None and "_" in imagepath:
				image = load_image(imagepath.replace("_", " "), DIR, recursive=recursive, relpath=relpath)
			if image is not None:
				context_imagepath_map[imagepath] = image
				break

	if image is None:
		imagepath = os.fsdecode(filepath_parts[-1])
		image = load_image(imagepath, DIR, recursive=recursive, place_holder=True, relpath=relpath)
		context_imagepath_map[imagepath] = image

	return image


def load_mmd_images(dir, texture_paths):
	textures = []
	for path in texture_paths:
		texture = load_image(path, dir, recursive=False, place_holder=True)
		textures.append(texture)
	return textures

def create_materials(filepath, texture_paths, materials):
	DIR = os.path.dirname(filepath)
	context_material_vars = set()
	unique_materials = {}
	unique_material_images = {}

	textures = load_mmd_images(filepath, texture_paths)
	#bpy.data.materials.new(name="MaterialName")

	context_imagepath_map = {}

	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.object.mode_set(mode='OBJECT')

	# make sure face select mode is enabled
#	bpy.context.tool_settings.mesh_select_mode = [False, False, True]

	# Create new materials
	for m in materials:
		name = m['local_name']
		ma = unique_materials[name] = bpy.data.materials.new(name.decode('utf-8', "replace"))
		unique_material_images[name] = None
		if True: #use_cycles
			from modules import cycles_shader_compat
			ma_wrap = cycles_shader_compat.CyclesShaderWrapper(ma)


	for name in unique_materials:  # .keys()
		if name is not None:
			ma = unique_materials[name] = bpy.data.materials.new(name.decode('utf-8', "replace"))
			unique_material_images[name] = None  # assign None to all material images to start with, add to later.
			if use_cycles:
				from modules import cycles_shader_compat
				ma_wrap = cycles_shader_compat.CyclesShaderWrapper(ma)
				cycles_material_wrap_map[ma] = ma_wrap

	return unique_materials

def split_mesh(verts_loc, faces, unique_materials, filepath, SPLIT_OB_OR_GROUP):
	pass


def validate_version_signature(sig, version):
	magic_signature = [0x50, 0x4D, 0x58, 0x20]
	if version > 2.0:
		pass
	for i, l in enumerate(sig):
		if magic_signature[i] != l:
			return False
	return True

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
	#view_layer = bpy.context.view_layer

	bone_objects = []
	bone_internal = {}

	#root = bpy.data.objects.new("")
	arm_data = bpy.data.armatures.new(name="")# bpy.data.objects.new(bones[0].['local_name'], None)  # parent_type='BONE'
	root = bpy.data.objects.new(name="Root", object_data=arm_data)

	#view_layer.active_layer_collection.collection.objects.link(amature)
	#amature.select_set(True)

	# instance in scene
	obj_base = bpy.context.scene.objects.link(root)
	obj_base.select = True

	bpy.context.scene.objects.active = root
	is_hidden = root.hide
	root.hide = False  # Can't switch to Edit mode hidden objects...

	bpy.ops.object.mode_set(mode='EDIT')

	for bone in bones:
		arm_bone = root.data.edit_bones.new(name=bone['local_name'])
		mmd_flags = bone['flag']
		if mmd_flags & parse_mmd.const_bone_flag_inherit_rotation == 0:
			arm_bone.use_inherit_rotation = False
		else:
			arm_bone.use_inherit_rotation = True
		if mmd_flags & parse_mmd.const_bone_flag_inherit_translation == 0:
			arm_bone.use_inherit_rotation = False
		else:
			arm_bone.use_inherit_rotation = True
		if mmd_flags & parse_mmd.const_bone_flag_local_co_coordinate:
			arm_bone.use_local_location = True
		else:
			arm_bone.use_local_location = False
		arm_bone.head = bone['position']
		arm_bone.layers[bone['layer']] = True
		bone_internal[bone['parent_bone']] = arm_bone
		bone_objects.append(arm_bone)

		if "tail_pos" in bone.keys():
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
				arm_bone.tail = bones[tail_index]['position']
			else:
				arm_bone.tail = (0,0,0)
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
			pass


	bpy.ops.object.mode_set(mode='OBJECT')
	root.hide = is_hidden

	return root


def create_influence(bones, mesh):
	pass

def process_header(f):
	header = {}

	#
	header['signature'] = str(parse_mmd.read_uint(f))
	header['version'] = float(parse_mmd.read_float(f))

	if validate_version_signature(header['signature'], header['version']):
		print("Invalid")
	if header['version'] == 2.0:
		pass

	header['globals_count'] = parse_mmd.read_ubyte(f)
	# Data[0] = Vertex
	# Data[1] = Face
	# Data[2] = Texture
	# Data[3] = Material
	# Data[4] = Bone
	# Data[5] = Morph
	# Data[6] = Frame
	# Data[7] = Rigidbody
	# Data[8] = Joint
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

	encoding = header['text_encoding']

	#local_character_name_size = parse_mmd.read_uint(f.read(4))
	#print(local_character_name_size)
	_, header['local_character_name'] = parse_mmd.read_string_ubyte(f,encoding)
	# if header['text_encoding'] == 0:
	# 	header['local_character_name'] = header['local_character_name'].decode("utf-16", "strict")
	# elif header['text_encoding'] == 1:
	# 	header['local_character_name'] = header['local_character_name'].decode("utf-8", "strict")

	#universal_character_name_size = parse_mmd.read_uint(f.read(4))
	_, header['universal_character_name_size'] = parse_mmd.read_string_ubyte(f,encoding)
	# if header['text_encoding'] == 0:
	# 	header['universal_character_name_size'] = header['universal_character_name_size'].decode("utf-16", "strict")
	# elif header['text_encoding'] == 1:
	# 	header['universal_character_name_size'] = header['universal_character_name_size'].decode("utf-8", "strict")

	#local_comment_size = parse_mmd.read_uint(f.read(4))
	_, header['comment_local'] = parse_mmd.read_string_ubyte(f,encoding)
	# if header['text_encoding'] == 0:
	# 	header['comment_local'] = header['comment_local'].decode("utf-16", "strict")
	# elif header['text_encoding'] == 1:
	# 	header['comment_local'] = header['comment_local'].decode("utf-8", "strict")

	#universal_comment_size = parse_mmd.read_uint(f.read(4))
	_, header['comment_universal'] = parse_mmd.read_string_ubyte(f,encoding)
	# if header['text_encoding'] == 0:
	# 	header['comment_universal'] = header['comment_universal'].decode("utf-16", "strict")
	# elif header['text_encoding'] == 1:
	# 	header['comment_universal'] = header['comment_universal'].decode("utf-8", "strict")

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


def compute_type_sizes(header):
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
         use_smooth_groups=True,
         use_edges=True,
         use_split_objects=True,
         use_split_groups=True,
         use_image_search=True,
         use_groups_as_vgroups=False,
         use_cycles=True,
         relpath=None,
         use_material_import,
         use_joint_import,
         global_matrix=None
         ):
	#view_layer = context.view_layer

	with ProgressReport(context.window_manager) as progress:
		progress.enter_substeps(1, str.format("Importing MMD file: {}...", filepath))

		if global_matrix is None:
			global_matrix = mathutils.Matrix()

		if use_split_objects or use_split_groups:
			use_groups_as_vgroups = False
		time_main = time.time()

		verts_loc = []
		verts_nor = []
		verts_tex = []
		faces = []
		material_libs = set()
		vertex_groups = {}

		subprogress = progress.enter_substeps(3, "Parsing MMD file...")
		header = []
		with open(filepath, 'rb') as f:
			# Get information
			header = process_header(f)
			struct_sizes = compute_type_sizes(header)
			header.update(struct_sizes)
			version = header['version']
			# Loading all nedded data.
			if version >= 2.0:
				# Vertex count
				# Vertex
				#progress.enter_substeps(1,"Extracting Vertex Data...")
				vertices = parse_mmd.read_full_vertices_data(f, struct_sizes, header['additional_vec4_count'])
				print("vertex count: " + str(len(vertices)))

				# Surface
				#subprogress.enter_substeps(1,"Extracting Surface Data...")
				surfaces = parse_mmd.read_full_surface_data(f, header)
				print("surface count: " + str(len(surfaces)))
				# for s in surfaces:
				#	bm.faces.
				# make the bmesh the object's mesh

				# Texture
				texture_paths = parse_mmd.read_all_texture_paths(f, header)
				texture_paths = mmd_util.getFullPaths(filepath, texture_paths)
				print(texture_paths)
				# material
				materials = parse_mmd.read_all_material(f, header)
				print(materials)
				# Bone
				bones = parse_mmd.read_all_bones(f, header)
				print(bones)
				# Morph
				morphs = parse_mmd.read_all_morph(f, header)
				print(morphs)
				# Displayframe count
				# displayFrames = parse_mmd.read_all_display_frames(f, header)
				# print(displayFrames)
				# # Rigidbody count
				# rigidbodies = parse_mmd.read_all_rigidbodies(f, header)
				# print(rigidbodies)
				# # Joint count
				# joints = parse_mmd.read_all_joints(f, header)
				# print(joints)
			if version >= 2.1:
				softbodies = parse_mmd.read_all_softbody(f, header)
				print(softbodies)

		# Name the character.
		root = create_bone_system(bones)
		root.name = header['local_character_name']

		progress.step("Done, loading materials and images...")

		load_mmd_images(filepath, texture_paths)
		object_materials = create_materials(filepath, texture_paths, materials)
		root.data.materils = object_materials

		# create_materials(filepath, texture_paths, material_libs, unique_materials,
		#                   unique_material_images, use_image_search, use_cycles, float_func)
		#
		# progress.step("Done, building geometries (verts:%i faces:%i materials: %i smoothgroups:%i) ..." %
		#               (len(verts_loc), len(faces), len(unique_materials), len(unique_smooth_groups)))

		# TODO relocate
		mesh = bpy.data.meshes.new("mesh")  # add a new mesh
		obj = bpy.data.objects.new("MyObject", mesh)  # add a new object using the mesh


		scene = bpy.context.scene
		scene.objects.link(obj)  # put the object into the scene (link)
		scene.objects.active = obj  # set as the active object in the scene
		obj.select = True  # select object

		# me.loops.foreach_set("normal", loops_nor)
		#				bm = bmesh.new()

		# mesh.uv_layers.new().data
		vertices_data = []
		normal_data = []
		for v in vertices:
			vertices_data.append([v[0], v[1], v[2]])
			normal_data.append([v[5], v[6], v[7]])

		#			bm.verts.new([v[0],v[1],v[2]])  # add a new vert

		facesData = []
		for i0, i1, i2 in zip(*[iter(surfaces)] * 3):
			facesData.append([i0, i1, i2])
		# me.vertices.add(len(verts_loc))
		# me.loops.add(tot_loops)
		# mesh.face.new(surfaces)
		mesh.from_pydata(vertices_data, [], facesData)
		mesh.validate(clean_customdata=False)  # important to not remove loop normals here!
		mesh.update()

		mesh.polygons.foreach_set("use_smooth", [True] * len(mesh.polygons))
		mesh.normals_split_custom_set(normal_data)
		# mesh.polygons.add(len(surfaces))
		# mesh.polygons.foreach_set("vertices", surfaces)

		#	bmesh.ops.triangulate(bm, faces=bm.faces)
		#	bm.to_mesh(mesh)
		#	bm.free()  # always do this when finished

		# deselect all
		if bpy.ops.object.select_all.poll():
			bpy.ops.object.select_all(action='DESELECT')

		scene = context.scene
		new_objects = []  # put new objects here

		#	create_mesh

		scene.update()

		axis_min = [1000000000] * 3
		axis_max = [-1000000000] * 3

		progress.leave_substeps("Done.")
		progress.leave_substeps(str.format("Finished importing: {}", filepath))

	return {'FINISHED'}
