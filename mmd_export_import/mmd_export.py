# <pep8 compliant>
if "bpy" in locals():
	import importlib

	if "parser_mmd" in locals():
		importlib.reload(parser_mmd)
	if "parser_mmd" in locals():
		importlib.reload(mmd_util)

import array
import os
import time

import bpy
import mathutils
import mathutils
import mmd_export_import.mmd_util as mmd_util
import mmd_export_import.mmd_parser as parse_mmd
from bpy_extras.image_utils import load_image
from bpy_extras.io_utils import unpack_list
from bpy_extras.wm_utils.progress_report import ProgressReport
from mathutils import Matrix, Euler, Vector


# from progress_report import ProgressReport


class MMDExport:
	def export(self, path : str, selected_objects : list):
		pass


def create_header(f, author, comment, character_name, version, section_data):
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

	_, header['local_character_name'] = parse_mmd.read_string_ubyte(
		f, encoding)
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
         use_animation=False,
         global_matrix=None,
         use_image_search=False,
         path_mode='AUTO'):

	with ProgressReport(context.window_manager) as progress:
		base_name, ext = os.path.splitext(filepath)
		# Base name, scene name, frame number, extension
		context_name = [base_name, '', '', ext]

		has_uv = False
		has_skinned = False

		scene = context.scene

		# Exit edit mode before exporting, so current object states are exported properly.
		if bpy.ops.object.mode_set.poll():
			bpy.ops.object.mode_set(mode='OBJECT')

		#
		selected_boject = bpy.context.selected_objects[0]
		armature = selected_boject.data
		mesh = selected_boject.data
		bones = armature.bones

		# Extract the vertices of object.
		mesh.has_custom_normals
		mesh.animation_data
		uv_active = mesh.uv_layers.active
		uv_layer = None
		skinned_vertices = mesh.skin_vertices
		if skinned_vertices:
			has_skinned = True
			print("Number of skinned vertices.	%d\n", len(skinned_vertices))
		if uv_active:
			uv_layer = uv_active.data

		for poly in mesh.polygons:
			print("Polygon index: %d, length: %d" %
			      (poly.index, poly.loop_total))

			# range is used here to show how the polygons reference loops,
			# for convenience 'poly.loop_indices' can be used instead.
			for loop_index in range(poly.loop_start, poly.loop_start + poly.loop_total):
				print("    Vertex: %d" % mesh.loops[loop_index].vertex_index)
		# print("    UV: %r" % uv_layer[loop_index].uv)

		# Extract the triangles indices.
		# Extract and convert materials.
		# Extract bones

		# header = create_header(author, comment,"", 2.0, {})

		# Final step. Write everything to file.
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
