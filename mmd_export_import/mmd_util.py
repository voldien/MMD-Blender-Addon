# <pep8 compliant>
import os

import bpy

if "bpy" in locals():
	import importlib

	if "parse_mmd" in locals():
		importlib.reload(mmd_export_import.mmd_constants)

import mmd_export_import.mmd_constants as mmd_constants


def validate_version_signature(sig, version):
	magic_signature = mmd_constants.magic_signature
	if version > 2.0:
		pass
	for i, l in enumerate(sig):
		if magic_signature[i] != l:
			return False
	return True


def get_absolute_path(filepath, texture_paths):
	return [os.fsdecode(str.format("{}/{}", filepath, t_path)) for t_path in texture_paths]


def link_object_to_active_scene(obj, coll):
	coll.objects.link(obj)
	bpy.context.view_layer.objects.active = obj
	obj.select_set(True)
