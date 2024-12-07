import bpy
from bpy_extras.io_utils import ImportHelper

import json

def read_json_data(context, filepath, data_fields, data_array_name=None,
                   encoding='utf-8-sig', joint_names=None):
    '''
    # https://docs.blender.org/api/current/bpy.types.Attribute.html#bpy.types.Attribute
    '''

    # return variables for displaying a report
    report_type = 'INFO'
    report_message = ""

    f = open(filepath, 'r', encoding=encoding)
    data = json.load(f)

    if data_array_name:
        data_array = data[data_array_name] 
    else:
        assert isinstance(data, list), 'JSON list expected'
        data_array = data

    # name of the object and mesh
    data_name = "imported_data"
    
    mesh = bpy.data.meshes.new(name="json_"+data_array_name)
    mesh.vertices.add(len(data_array))

    # In JSON an empty string is a valid key.
    # Blender mesh attributes with an empty name string dont work
    # That's why an empty key in JSON generates an attribute with the name "empty_key_string"

    # set data according to json
    for index, frame in enumerate(data_array):

        for joint in frame:

            if joint_names:
                if joint['name'] not in joint_names:
                    continue

            # make sure it's the right data type
            for data_field in data_fields:
                value = joint[data_field.name]
                if(data_field.dataType == 'FLOAT'):
                    value = float(value)
                elif(data_field.dataType == 'INT'):
                    value = int(value)
                elif(data_field.dataType == 'BOOLEAN'):
                    value = bool(value)

                key = joint['name'] + '_' + (
                    data_field.name if data_field.name else "empty_key_string"
                )
                if not mesh.attributes.get(key):
                    mesh.attributes.new(
                        name=key,
                        type=data_field.dataType,
                        domain='POINT'
                    )

                mesh.attributes[key].data[index].value = value

        # set vertex x position according to index
        mesh.vertices[index].co = (0.01 * index,0.0,0.0)

    f.close()

    mesh.update()
    mesh.validate()

    file_name = bpy.path.basename(filepath)
    object_name = bpy.path.display_name(file_name)
    create_object(mesh, object_name)
    
    report_message = "Imported {num_values} from \"{file_name}\"".format(
        num_values=len(data_array),
        file_name=file_name
    )

    return report_message, report_type


def create_object(mesh, name):
    for ob in bpy.context.selected_objects:
        ob.select_set(False)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

class SPREADSHEET_UL_data_fields(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(data=item, property="name", text="")
            layout.prop(data=item, property="dataType", text="")
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.prop(data=item, property="name", text="")
            layout.prop(data=item, property="dataType", text="")

# https://blender.stackexchange.com/questions/16511/how-can-i-store-and-retrieve-a-custom-list-in-a-blend-file
# https://docs.blender.org/api/master/bpy_types_enum_items/attribute_domain_items.html?highlight=mesh+attributes

class DataFieldPropertiesGroup(bpy.types.PropertyGroup):
    name : bpy.props.StringProperty(
        name="Field Name",
        description="The name of the field to import",
        default="",
    ) # type: ignore

    #  https://docs.blender.org/api/current/bpy.types.Attribute.html#bpy.types.Attribute
    dataType: bpy.props.EnumProperty(
        name="Field Data Type",
        description="Choose Data Type",
        items=(
            ('FLOAT', "Float", "Floating-point value"),
            ('INT', "Integer", "32-bit integer"),
            ('BOOLEAN', "Boolean", "True or false"),
            # ('STRING', "String", "Text string"), # string wont work
        ),
        default='FLOAT',
    ) # type: ignore


class SPREADSHEET_UL_joint_names(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(data=item, property="name", text="")
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.prop(data=item, property="name", text="")


class JointNamesGroup(bpy.types.PropertyGroup):
    name : bpy.props.StringProperty(
        name="Joint Name",
        description="Name of joint to import",
        default="",
    ) # type: ignore

#todo: add presets
# https://sinestesia.co/blog/tutorials/using-blenders-presets-in-python/

# ImportHelper is a helper class, defines filename and invoke() function which calls the file selector.
class ImportSpreadsheetData(bpy.types.Operator, ImportHelper):
    """Import data to Spreadsheet"""
    bl_idname = "import.spreadsheet"  # important since its how bpy.ops.import.spreadsheet is constructed
    bl_label = "Interfaces Import"

    # ImportHelper mixin class uses this
    # filename_ext = ".json;.csv"

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    filter_glob: bpy.props.StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    ) # type: ignore

    data_fields: bpy.props.CollectionProperty(
        type=DataFieldPropertiesGroup,
        name="Field names",
        description="All the fields that should be imported",
        options={'HIDDEN'},
    ) # type: ignore

    # The index of the selected data_field
    active_data_field_index: bpy.props.IntProperty(
        name="Index of data_fields",
        default=0,
        options={'HIDDEN'},
    ) # type: ignore

    array_name: bpy.props.StringProperty(
        name="Array name",
        description="The name of the array to import",
        default="",
        options={'HIDDEN'},
    ) # type: ignore

    json_encoding: bpy.props.StringProperty(
        name="Encoding",
        description="Encoding of the JSON File",
        default="utf-8-sig",
        options={'HIDDEN'},
    ) # type: ignore

    joint_names: bpy.props.CollectionProperty(
        type=JointNamesGroup,
        name="Joint names",
        description="Name of joints that should be imported",
        options={'HIDDEN'},
    ) # type: ignore

    # The index of the selected joint name
    active_joint_field_index: bpy.props.IntProperty(
        name="Index of joint_names",
        default=0,
        options={'HIDDEN'},
    ) # type: ignore

    def draw(self, context):
        layout = self.layout
        layout.label(text="Interfaces Import Options")

    def execute(self, context):
        if(self.filepath.lower().endswith('.json')):
            report_message, report_type = read_json_data(
                context,
                filepath=self.filepath,
                data_fields=self.data_fields,
                data_array_name=self.array_name,
                encoding=self.json_encoding,
                joint_names=self.joint_names,
            )

        self.report({report_type}, report_message)
        return {'FINISHED'}

class AddDataFieldOperator(bpy.types.Operator):
    bl_idname = "import.spreadsheet_field_add"
    bl_label = "Add field"

    def execute(self, context):
        sfile = context.space_data
        operator = sfile.active_operator
        item = operator.data_fields.add()
        operator.active_data_field_index = len(operator.data_fields) - 1
        return {'FINISHED'}

class RemoveDataFieldOperator(bpy.types.Operator):
    bl_idname = "import.spreadsheet_field_remove"
    bl_label = "Remove field"

    def execute(self, context):
        sfile = context.space_data
        operator = sfile.active_operator
        index = operator.active_data_field_index
        operator.data_fields.remove(index)
        operator.active_data_field_index = min(max(0,index - 1), len(operator.data_fields)-1)
        return {'FINISHED'}

class AddJointOperator(bpy.types.Operator):
    bl_idname = "import.spreadsheet_joint_add"
    bl_label = "Add joint"

    def execute(self, context):
        sfile = context.space_data
        operator = sfile.active_operator
        item = operator.joint_names.add()
        operator.active_joint_field_index = len(operator.joint_names) - 1
        return {'FINISHED'}

class RemoveJointOperator(bpy.types.Operator):
    bl_idname = "import.spreadsheet_joint_remove"
    bl_label = "Remove joint"

    def execute(self, context):
        sfile = context.space_data
        operator = sfile.active_operator
        index = operator.active_joint_field_index
        operator.joint_names.remove(index)
        operator.active_joint_field_index = min(max(0,index - 1), len(operator.joint_names)-1)
        return {'FINISHED'}


class SPREADSHEET_PT_json_options(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "JSON Import Options"
    bl_parent_id = "FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        return operator.bl_idname == "IMPORT_OT_spreadsheet" and operator.filepath.lower().endswith('.json')

    def draw(self, context):
        sfile = context.space_data
        operator = sfile.active_operator
        layout = self.layout
        layout.prop(data=operator, property="array_name")
        layout.prop(data=operator, property="json_encoding")


class SPREADSHEET_PT_field_names(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Field Names"
    bl_parent_id = "FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        return operator.bl_idname == "IMPORT_OT_spreadsheet"

    def draw(self, context):
        sfile = context.space_data
        operator = sfile.active_operator
        layout = self.layout

        # layout.template_list("UI_UL_list", "", operator, "data_fields", operator, )
        # success with this tutorial!
        # https://sinestesia.co/blog/tutorials/using-uilists-in-blender/

        rows = 2
        filed_names_exist = bool(len(operator.data_fields) >= 1)
        if filed_names_exist:
            rows = 4

        row = layout.row()
        row.template_list(
            "SPREADSHEET_UL_data_fields",
            "",
            operator,
            "data_fields",
            operator,
            "active_data_field_index",
            rows=rows
        )
        col = row.column(align=True)
        col.operator(AddDataFieldOperator.bl_idname, icon='ADD', text="")
        col.operator(RemoveDataFieldOperator.bl_idname, icon='REMOVE', text="")

class SPREADSHEET_PT_joint_names(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Joint Names"
    bl_parent_id = "FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        return operator.bl_idname == "IMPORT_OT_spreadsheet"

    def draw(self, context):
        sfile = context.space_data
        operator = sfile.active_operator
        layout = self.layout

        rows = 2
        filed_names_exist = bool(len(operator.joint_names) >= 1)
        if filed_names_exist:
            rows = 4

        row = layout.row()
        row.template_list(
            "SPREADSHEET_UL_joint_names",
            "",
            operator,
            "joint_names",
            operator,
            "active_joint_field_index",
            rows=rows
        )
        col = row.column(align=True)
        col.operator(AddJointOperator.bl_idname, icon='ADD', text="")
        col.operator(RemoveJointOperator.bl_idname, icon='REMOVE', text="")


blender_classes = [
    SPREADSHEET_UL_data_fields,
    SPREADSHEET_UL_joint_names,
    DataFieldPropertiesGroup,
    JointNamesGroup,
    ImportSpreadsheetData,
    SPREADSHEET_PT_field_names,
    SPREADSHEET_PT_json_options,
    SPREADSHEET_PT_joint_names,
    AddDataFieldOperator,
    RemoveDataFieldOperator,
    AddJointOperator,
    RemoveJointOperator,
]

def menu_func_import(self, context):
    '''
    Only needed if you want to add into a dynamic menu
    '''
    self.layout.operator(
        ImportSpreadsheetData.bl_idname,
        text="Interfaces Import (.json)"
    )

def register():
    '''
    Register and add to the "file selector" menu
    (required to use F3 search "Text Import Operator" for quick access)
    '''
    for blender_class in blender_classes:
        bpy.utils.register_class(blender_class)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    for blender_class in blender_classes:
        bpy.utils.unregister_class(blender_class)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

