# <pep8 compliant>
import bpy
from bpy.types import Panel
from bpy_extras.io_utils import ImportHelper, ExportHelper
import mmd_export_import.mmd_import as mmd_import
import mmd_export_import.mmd_export as mmd_export
from bpy.types import Operator
import typing
from bpy.props import BoolProperty, FloatProperty, StringProperty

from bpy_extras.io_utils import (
	ImportHelper,
	ExportHelper,
	orientation_helper,
	path_reference_mode,
	axis_conversion,
)

VERSION = (0, 1, 0)
bl_info = {
	'name': 'MMD Import - Export',
	'author': 'Valdemar Lindberg',
	'version': (0, 1, 0),
	'blender': (2, 80, 3),
	'location': 'File > Import-Export > Miku Mikue Dance',
	'description': 'Loading Miku Mikue Dance files (.pmx/.pmd/.vmd).',
	'warning': 'Still in progress',
	'wiki_url': '',
	'doc_url': 'https://github.com/voldien/MMD-Blender-Addon',
	'tracker_url': 'https://github.com/voldien/MMD-Blender-Addon/issues',
	'category': 'Import-Export'}


def print_version(info):
	pass


# IOOBJOrientationHelper = orientation_helper(
#	"IOOBJOrientationHelper", axis_forward='-Z', axis_up='Y')


@orientation_helper(axis_forward='-Z', axis_up='Y')
class ExportMMD(Operator, ExportHelper):
	"""Export a Miku Miku Dance File."""
	bl_idname = "export_scene.mmd"
	bl_label = "Export MMD"
	bl_options = {'PRESET'}

	filename_ext = ".pmx"
	filter_glob = StringProperty(
		default="*.pmx;*.pmd;*.vmd",
		options={'HIDDEN'},
	)

	use_animation = BoolProperty(
		name="Animation",
		description="Save animation associated for each exported object.",
		default=False,
	)

	# object group
	use_mesh_modifiers = BoolProperty(
		name="Apply Modifiers",
		description="Apply modifiers",
		default=True,
	)
	use_mesh_modifiers_render = BoolProperty(
		name="Use Modifiers Render Settings",
		description="Use render settings when applying modifiers to mesh objects",
		default=False,
	)

	# extra data group
	use_edges = BoolProperty(
		name="Include Edges",
		description="",
		default=True,
	)
	use_smooth_groups = BoolProperty(
		name="Smooth Groups",
		description="Write sharp edges as smooth groups",
		default=False,
	)
	use_normals = BoolProperty(
		name="Write Normals",
		description="Export one normal per vertex and per face, to represent flat faces and sharp edges",
		default=True,
	)
	use_uvs = BoolProperty(
		name="Include UVs",
		description="Write out the active UV coordinates",
		default=True,
	)
	keep_vertex_order = BoolProperty(
		name="Keep Vertex Order",
		description="",
		default=False,
	)

	global_scale = FloatProperty(
		name="Scale",
		min=0.01, max=1000.0,
		default=1.0,
	)
	author = StringProperty(
		name="Author",
		description="Assign author of the creation",
		default=""
	)
	comment = StringProperty(
		name="Comment",
		description="Assign a comment about the file/character",
		default=""
	)
	character_name = StringProperty(
		name="Character Name",
		description="Assign the character name.",
		default=""
	)

	path_mode = path_reference_mode

	check_extension = True

	use_image_search = BoolProperty(
		name="Image Search",
		description="Search subdirs for any associated images "
					"(Warning, may be slow)",
		default=True,
	)

	def execute(self, context) -> typing.Set[typing.Union[str, int]]:
		from . import mmd_export

		from mathutils import Matrix
		keywords = self.as_keywords(ignore=("axis_forward",
											"axis_up",
											"global_scale",
											"check_existing",
											"filter_glob",
											))

		global_matrix = (Matrix.Scale(self.global_scale, 4) *
						 axis_conversion(to_forward=self.axis_forward,
										 to_up=self.axis_up,
										 ).to_4x4())

		keywords["global_matrix"] = global_matrix
		return mmd_export.save(context, **keywords)

	def draw(self, context):
		layout = self.layout

		row = layout.row(align=True)
		row.prop(self, "use_smooth_groups")
		row.prop(self, "use_edges")

		box = layout.box()
		row = box.row()
		row.prop(self, "split_mode", expand=True)

		row = layout.split(percentage=0.67)
		row.prop(self, "global_clamp_size")
		layout.prop(self, "axis_forward")
		layout.prop(self, "axis_up")

		layout.prop(self, "use_image_search")
		layout.prop(self, "use_material_import")
		layout.prop(self, "use_joint_import")
		layout.prop(self, "author")
		layout.prop(self, "comment")
		layout.prop(self, "character_name")


@orientation_helper(axis_forward='-Z', axis_up='Y')
class ImportMMD(Operator, ImportHelper):
	"""Import a Miku Miku Dance File."""
	bl_idname = "import_mesh.mmd"
	bl_label = "Import MMD"
	bl_options = {'PRESET', 'UNDO'}

	filename_ext = "*.pmx;*.pmd,*.vmd"
	filter_glob = StringProperty(
		default=filename_ext,
		options={'HIDDEN'},
	)

	use_image_search = BoolProperty(
		name="Image Search",
		description="Search subdirs for any associated images "
					"(Warning, may be slow)",
		default=True,
	)

	use_material_import = BoolProperty(name="Import Material",
									   description="",
									   default=True)
	use_joint_import = BoolProperty(name="Import Joints",
									description="",
									default=True)

	global_clamp_size = FloatProperty(
		name="Clamp Size",
		description="Clamp bounds under this value (zero to disable)",
		min=0.0, max=1000.0,
		soft_min=0.0, soft_max=1000.0,
		default=0.0,
	)
	split_mode = BoolProperty(name="split_mode", description="", default=False)

	use_split_objects = BoolProperty(name="Split Objects",
									 description="",
									 default=True)

	def execute(self, context) -> typing.Set[typing.Union[str, int]]:

		if self.split_mode == 'OFF':
			self.use_split_objects = False
			self.use_split_groups = False
		else:
			self.use_groups_as_vgroups = False

		keywords = self.as_keywords(ignore=("axis_forward",
											"axis_up",
											"filter_glob",
											"split_mode",
											))

		global_matrix = axis_conversion(from_forward=self.axis_forward,
										from_up=self.axis_up,
										).to_4x4()
		keywords["global_matrix"] = global_matrix
		keywords["use_cycles"] = (context.scene.render.engine == 'CYCLES')

		#
		if bpy.data.is_saved and context.user_preferences.filepaths.use_relative_paths:
			import os
			keywords["relpath"] = os.path.dirname(bpy.data.filepath)

		import_settings = {}

		return mmd_import.load(context, **keywords, use_joint_import=False, use_material_import=False)

	def draw(self, context):
		layout = self.layout

	# row = layout.row(align=True)
	# row.prop(self, "use_smooth_groups")
	# row.prop(self, "use_edges")
	#
	# box = layout.box()
	# row = box.row()
	# row.prop(self, "split_mode", expand=True)
	#
	# row = layout.split()
	# row.prop(self, "global_clamp_size")
	# layout.prop(self, "axis_forward")
	# layout.prop(self, "axis_up")
	#
	# layout.prop(self, "use_image_search")
	# layout.prop(self, "use_material_import")
	# layout.prop(self, "use_joint_import")


def menu_func_import(self, context):
	self.layout.operator(ImportMMD.bl_idname,
						 text="Miku Miku Dance MMD (.pmx/.pmd/.vmd)")


def menu_func_export(self, context):
	self.layout.operator(ExportMMD.bl_idname,
						 text="Miku Miku Dance MMD (.pmx/.pmd/.vmd)")


menu_func_list = [menu_func_import, menu_func_export]

classes = (
	ImportMMD,
	ExportMMD,
)


def register():
	for cls in classes:
		bpy.utils.register_class(cls)

	# Create menu for export and import
	if bpy.app.version >= (2, 80, 0):
		bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
		bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
	else:
		bpy.types.INFO_MT_file_import.append(menu_func_import)
		bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
	# Delete menu for export and import
	if bpy.app.version >= (2, 80, 0):
		bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
		bpy.types.VIEW3D_MT_image_add.remove(menu_func_import)
	else:
		bpy.types.INFO_MT_file_import.remove(menu_func_import)
		bpy.types.INFO_MT_mesh_add.remove(menu_func_import)

	for class_ in reversed(classes):
		bpy.utils.unregister_class(class_)


if __name__ == "__main__":
	register()
