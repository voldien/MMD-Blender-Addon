from unittest import TestCase
import bpy
from unittest.mock import patch
from mmd_export_import.mmd_parser import MMDParser


class TestObjectImport(TestCase):
	def test_header(self):
		
		MMDParser.Header()
		pass
