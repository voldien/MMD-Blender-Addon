if "bpy" in locals():
	import importlib
	if "parser_mmd" in locals():
		importlib.reload(parser_mmd)
	if "parser_mmd" in locals():
		importlib.reload(mmd_util)

import bpy
from mathutils import Matrix, Euler, Vector

from . import parse_mmd, mmd_util

import array
import os
import time
import bpy
import mathutils
from bpy_extras.io_utils import unpack_list
from bpy_extras.image_utils import load_image

import mathutils
from progress_report import ProgressReport


def create_header(author, comment, character_name, version, section_data):
	header = {}

	#
	header['signature'] = parse_mmd.magic_signature
	header['version'] = 2.0

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

	_, header['local_character_name'] = parse_mmd.read_string_ubyte(f, encoding)
	_, header['universal_character_name_size'] = parse_mmd.read_string_ubyte(
		f, encoding)
	_, header['comment_local'] = parse_mmd.read_string_ubyte(f, encoding)
	_, header['comment_universal'] = parse_mmd.read_string_ubyte(f, encoding)

	return header

def save(context,
         filepath,
         *,
		 author,
		 comment,
         character_name,
         use_triangles=False,
         use_edges=True,
         use_normals=False,
         use_smooth_groups=False,
         use_smooth_groups_bitflags=False,
         use_uvs=True,
         use_materials=True,
         use_mesh_modifiers=True,
         use_mesh_modifiers_render=False,
         keep_vertex_order=False,
         use_vertex_groups=False,
         use_selection=True,
         use_animation=False,
         global_matrix=None,
         path_mode='AUTO'):
	with ProgressReport(context.window_manager) as progress:
		base_name, ext = os.path.splitext(filepath)
		context_name = [base_name, '', '', ext]  # Base name, scene name, frame number, extension

		scene = context.scene

		# Exit edit mode before exporting, so current object states are exported properly.
		if bpy.ops.object.mode_set.poll():
			bpy.ops.object.mode_set(mode='OBJECT')

		# Extract the vertices of object.

		# Extract the triangles indices.
		# Extract and convert materials.
		# Extract bones


		header = create_header(author, comment,"", 2.0)

		#Final step. Write everything to file.
		# TODO write header

		# TODO Write vertices
		# TODO Write face indices (surface)
		# TODO Write texture paths
		# TODO Write Materials
		# TODO Write bones
		# TODO Write morphs
		# TODO Write animations
		# TODO Write rigidbodies
		# TODO Write Joints
		# TODO Write softbodies


		progress.leave_substeps()

	return {'FINISHED'}
