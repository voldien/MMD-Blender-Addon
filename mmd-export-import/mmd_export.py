if "bpy" in locals():
	import importlib

	if "parser_mmd" in locals():
		importlib.reload(parser_mmd)
#    if "fbx_utils" in locals():
#       importlib.reload(fbx_utils)
import bpy
from mathutils import Matrix, Euler, Vector

#from . import parse_mmd

import array
import os
import time
import bpy
import mathutils
from bpy_extras.io_utils import unpack_list
from bpy_extras.image_utils import load_image

import mathutils
from progress_report import ProgressReport


def save(context,
         filepath,
         *,
         use_triangles=False,
         use_edges=True,
         use_normals=False,
         use_smooth_groups=False,
         use_smooth_groups_bitflags=False,
         use_uvs=True,
         use_materials=True,
         use_mesh_modifiers=True,
         use_mesh_modifiers_render=False,
         use_blen_objects=True,
         group_by_object=False,
         group_by_material=False,
         keep_vertex_order=False,
         use_vertex_groups=False,
         use_nurbs=True,
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

		orig_frame = scene.frame_current

		# Export an animation?
		if EXPORT_ANIMATION:
			scene_frames = range(scene.frame_start, scene.frame_end + 1)  # Up to and including the end frame.
		else:
			scene_frames = [orig_frame]  # Dont export an animation.

		# Loop through all frames in the scene and export.
		progress.enter_substeps(len(scene_frames))
		for frame in scene_frames:
			if EXPORT_ANIMATION:  # Add frame to the filepath.
				context_name[2] = '_%.6d' % frame

			scene.frame_set(frame, 0.0)
			if EXPORT_SEL_ONLY:
				objects = context.selected_objects
			else:
				objects = scene.objects

			full_path = ''.join(context_name)

			# erm... bit of a problem here, this can overwrite files when exporting frames. not too bad.
			# EXPORT THE FILE.
			progress.enter_substeps(1)
			write_file(full_path, objects, scene,
			           EXPORT_TRI,
			           EXPORT_EDGES,
			           EXPORT_SMOOTH_GROUPS,
			           EXPORT_SMOOTH_GROUPS_BITFLAGS,
			           EXPORT_NORMALS,
			           EXPORT_UV,
			           EXPORT_MTL,
			           EXPORT_APPLY_MODIFIERS,
			           EXPORT_APPLY_MODIFIERS_RENDER,
			           EXPORT_BLEN_OBS,
			           EXPORT_GROUP_BY_OB,
			           EXPORT_GROUP_BY_MAT,
			           EXPORT_KEEP_VERT_ORDER,
			           EXPORT_POLYGROUPS,
			           EXPORT_CURVE_AS_NURBS,
			           EXPORT_GLOBAL_MATRIX,
			           EXPORT_PATH_MODE,
			           progress,
			           )
			progress.leave_substeps()

		scene.frame_set(orig_frame, 0.0)
		progress.leave_substeps()

	return {'FINISHED'}
