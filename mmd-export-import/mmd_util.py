import os

if "bpy" in locals():
	import importlib

	if "parse_mmd" in locals():
		importlib.reload(parse_mmd)

from . import parse_mmd


def validate_version_signature(sig, version):
	magic_signature = parse_mmd.magic_signature
	if version > 2.0:
		pass
	for i, l in enumerate(sig):
		if magic_signature[i] != l:
			return False
	return True


def getFullPaths(filepath, texture_paths):
	return [os.fsdecode(str.format("{}/{}", filepath, t_path)) for t_path in texture_paths]
