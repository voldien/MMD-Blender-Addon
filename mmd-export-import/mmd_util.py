import os


def getFullPaths(filepath, texture_paths):
	return [os.fsdecode(str.format("{}/{}", filepath, t_path)) for t_path in texture_paths]