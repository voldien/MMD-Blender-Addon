bl_info = {
	"name": "MMD Import - Export",
	"author": "Valdemar Lindberg",
	"version": (0, 1, 0),
	"blender": (2, 79, 0),
	"location": "File > Import-Export",
	"description": "Loading MMD files.",
	"warning": "",
	"wiki_url": "",
	"category": "Import-Export"}

if "bpy" in locals():
	import importlib

	if "mmd_export" in locals():
		importlib.reload(mmd_export)
	if "mmd_import" in locals():
		importlib.reload(mmd_import)

from bpy.types import Operator
import bpy
import typing
from bpy.props import (
	BoolProperty,
	FloatProperty,
	StringProperty,
	EnumProperty,
)
from bpy_extras.io_utils import (
	ImportHelper,
	ExportHelper,
	orientation_helper_factory,
	path_reference_mode,
	axis_conversion,
)

IOOBJOrientationHelper = orientation_helper_factory("IOOBJOrientationHelper", axis_forward='-Z', axis_up='Y')

class ExportMMD(Operator, ExportHelper, IOOBJOrientationHelper):
	"""Export a Miku Miku Dance File"""
	bl_idname = "export_scene.mmd"
	bl_label = "Export MMD"
	bl_options = {'PRESET'}

	filename_ext = ".pmx"
	filter_glob = StringProperty(
		default="*.pmx;*.pmd",
		options={'HIDDEN'},
	)

	# context group
	use_selection = BoolProperty(
		name="Selection Only",
		description="Export selected objects only",
		default=False,
	)
	use_animation = BoolProperty(
		name="Animation",
		description="Write out an OBJ for each frame",
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
	use_smooth_groups_bitflags = BoolProperty(
		name="Bitflag Smooth Groups",
		description="Same as 'Smooth Groups', but generate smooth groups IDs as bitflags "
		            "(produces at most 32 different smooth groups, usually much less)",
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
	use_materials = BoolProperty(
		name="Write Materials",
		description="Write out the MTL file",
		default=True,
	)
	use_triangles = BoolProperty(
		name="Triangulate Faces",
		description="Convert all faces to triangles",
		default=False,
	)
	use_nurbs = BoolProperty(
		name="Write Nurbs",
		description="Write nurbs curves as OBJ nurbs rather than "
		            "converting to geometry",
		default=False,
	)
	use_vertex_groups = BoolProperty(
		name="Polygroups",
		description="",
		default=False,
	)

	# grouping group
	use_blen_objects = BoolProperty(
		name="Objects as OBJ Objects",
		description="",
		default=True,
	)
	group_by_object = BoolProperty(
		name="Objects as OBJ Groups ",
		description="",
		default=False,
	)
	group_by_material = BoolProperty(
		name="Material Groups",
		description="",
		default=False,
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

		row = box.row()
		if self.split_mode == 'ON':
			row.label(text="Split by:")
			row.prop(self, "use_split_objects")
			row.prop(self, "use_split_groups")
		else:
			row.prop(self, "use_groups_as_vgroups")

		row = layout.split(percentage=0.67)
		row.prop(self, "global_clamp_size")
		layout.prop(self, "axis_forward")
		layout.prop(self, "axis_up")

		layout.prop(self, "use_image_search")
		layout.prop(self, "use_material_import")
		layout.prop(self, "use_joint_import")


class ImportMMD(Operator, ImportHelper, IOOBJOrientationHelper):
	"""Load a Miku Miku Dance File"""
	bl_idname = "import_scene.mmd"
	bl_label = "Import MMD"
	bl_options = {'PRESET', 'UNDO'}

	filename_ext = "*.pmx;*.pmd"
	filter_glob = StringProperty(
		default="*.pmx;*.pmd",
		options={'HIDDEN'},
	)

	use_edges = BoolProperty(
		name="Lines",
		description="Import lines and faces with 2 verts as edge",
		default=True,
	)
	use_smooth_groups = BoolProperty(
		name="Smooth Groups",
		description="Surround smooth groups by sharp edges",
		default=True,
	)

	use_split_objects = BoolProperty(
		name="Object",
		description="Import OBJ Objects into Blender Objects",
		default=True,
	)
	use_split_groups = BoolProperty(
		name="Group",
		description="Import OBJ Groups into Blender Objects",
		default=True,
	)

	use_groups_as_vgroups = BoolProperty(
		name="Poly Groups",
		description="Import OBJ groups as vertex groups",
		default=False,
	)

	use_image_search = BoolProperty(
		name="Image Search",
		description="Search subdirs for any associated images "
		            "(Warning, may be slow)",
		default=True,
	)

	split_mode = EnumProperty(
		name="Split",
		items=(('ON', "Split", "Split geometry, omits unused verts"),
		       ('OFF', "Keep Vert Order", "Keep vertex order from file"),
		       ),
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

	def execute(self, context) -> typing.Set[typing.Union[str, int]]:
		from . import mmd_import

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

		return mmd_import.load(context, **keywords)

	def draw(self, context):
		layout = self.layout

		row = layout.row(align=True)
		row.prop(self, "use_smooth_groups")
		row.prop(self, "use_edges")

		box = layout.box()
		row = box.row()
		row.prop(self, "split_mode", expand=True)

		row = box.row()
		if self.split_mode == 'ON':
			row.label(text="Split by:")
			row.prop(self, "use_split_objects")
			row.prop(self, "use_split_groups")
		else:
			row.prop(self, "use_groups_as_vgroups")

		row = layout.split(percentage=0.67)
		row.prop(self, "global_clamp_size")
		layout.prop(self, "axis_forward")
		layout.prop(self, "axis_up")

		layout.prop(self, "use_image_search")
		layout.prop(self, "use_material_import")
		layout.prop(self, "use_joint_import")

classes = (
	ImportMMD,
	ExportMMD,
)


def menu_func_import(self, context):
	self.layout.operator(ImportMMD.bl_idname, text="Miku Miku Dance MMD (.pmx/.pmd)")

def menu_func_export(self, context):
	self.layout.operator(ExportMMD.bl_idname, text="Miku Miku Dance MMD (.pmx/.pmd)")

menu_func_list = [menu_func_import, menu_func_export]

def register():
	for cls in classes:
		bpy.utils.register_class(cls)

	if bpy.app.version >= (2, 80, 0):
		bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
		bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
	else:
		bpy.types.INFO_MT_file_import.append(menu_func_import)
		bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
	if bpy.app.version >= (2, 80, 0):
		bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
		bpy.types.VIEW3D_MT_image_add.remove(menu_func_import)
	else:
		bpy.types.INFO_MT_file_import.remove(menu_func_import)
		bpy.types.INFO_MT_mesh_add.remove(menu_func_import)

	for cls in classes:
		bpy.utils.unregister_module(cls)

if __name__ == "__main__":
	register()
