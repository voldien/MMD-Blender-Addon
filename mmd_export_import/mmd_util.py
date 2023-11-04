# <pep8 compliant>
import array
import os
import zlib
from struct import unpack, pack
import bpy
import mmd_export_import.pmx as pmx

if "bpy" in locals():
	import importlib

	if "parse_mmd" in locals():
		importlib.reload(mmd_export_import.parse_mmd)

import mmd_export_import.pmx as mmd_constants


def get_absolute_path(filepath: str, texture_paths: list) -> list[str]:
	return [os.fsdecode(str.format("{}/{}", filepath, t_path)) for t_path in texture_paths]


def link_object_to_active_scene(obj, coll):
	coll.objects.link(obj)
	bpy.context.view_layer.objects.active = obj
	obj.select_set(True)


#
def read_signed_index(reader, size_type):
	size_hash_lookup = {1: read_signed_byte, 2: read_signed_short, 4: read_signed_short}
	lookup_func = size_hash_lookup[size_type]

	return lookup_func(reader)


def read_index(reader, size_type) -> int:
	size_hash_lookup = {1: read_ubyte, 2: read_ushort, 4: read_uint}
	lookup_func = size_hash_lookup[size_type]
	return lookup_func(reader)

def read_uint(read) -> int:
	return unpack(b'I', read.read(pmx.pmx_const_int))[0]


def read_int(read)-> int:
	return unpack(b'<i', read.read(pmx.pmx_const_int))[0]


def read_signed_short(read) -> int:
	return unpack(b'h', read.read(pmx.pmx_const_short))[0]


def read_ushort(read)-> int:
	return unpack(b'H', read.read(pmx.pmx_const_short))[0]


def read_uint64(read):
	return unpack(b'<Q', read.read(pmx.pmx_const_uint64))[0]


def read_signed_byte(read):
	return unpack(b'b', read.read(pmx.pmx_const_byte))[0]


def read_ubyte(read):
	return unpack(b'B', read.read(pmx.pmx_const_byte))[0]


def read_vec3(read) -> tuple[float,...]:
	return unpack(b'fff', read.read(pmx.pmx_const_vec3))


def read_vec4(read) -> tuple[float,...]:
	return unpack(b'ffff', read.read(pmx.pmx_const_vec4))


def read_float(read)-> float:
	return unpack(b'f', read.read(pmx.pmx_const_float))[0]


def read_string_ubyte(reader, encoding=0) -> (int, str):
	size = read_uint(reader)
	data = reader.read(size)
	if encoding == 0:
		data = data.decode("utf-16", "strict")
	elif encoding == 1:
		data = data.decode("utf-8", "strict")
	return size, data


def write_index(writer, size_type, index):
	size_hash_lookup = {1: write_ubyte, 2: write_ushort, 4: write_uint}
	lookup_func = size_hash_lookup[size_type]
	return lookup_func(writer, index)


def write_uint(write, v):
	return write.write(pack(b'<I', v))


def write_int(write, v):
	return write.write(pack(b'<i', v))


def write_sint(writer, v):
	return writer.write(pack(b'H', v))


def write_ushort(writer, v):
	return writer.write(pack(b'h', v))


def write_uint64(writer, v):
	return writer.write(pack(b'<Q', v))


def write_ubyte(writer, v):
	return writer.write(pack(b'B', v))


def write_float(writer, v):
	return writer.write(pack(b'f', v))


def write_vec3(writer, v):
	return writer.write(pack(b'fff', v))


def write_vec4(writer, v):
	return writer.write(pack(b'ffff', v))


def write_string_ubyte(writer, v : str, encoding : int =0):
	size = len(v)
	data = v
	if encoding == 0:
		data = data.decode("utf-16", "strict")
	elif encoding == 1:
		data = data.decode("utf-8", "strict")
	return writer.write(data)


def unpack_array(read, array_type, array_stride, array_byteswap):
	length = read_uint(read)
	encoding = read_uint(read)
	comp_len = read_uint(read)

	data = read(comp_len)

	if encoding == 0:
		pass
	elif encoding == 1:
		data = zlib.decompress(data)

	assert (length * array_stride == len(data))

	data_array = array.array(array_type, data)
	#    if array_byteswap and _IS_BIG_ENDIAN:
	#        data_array.byteswap()
	return data_array
