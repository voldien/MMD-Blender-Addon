# <pep8 compliant>
from struct import unpack
from typing import Type


class Vertices:
	vertices = []

	def __init__(self, stride):
		self.stride = stride

	def get_stride(self):
		self.stride

	def get_vertices(self):
		return self.vertices
