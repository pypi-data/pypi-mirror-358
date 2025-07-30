from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr22

_method_map = {
    'auxMode': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TEvent',
        'method_name': 'auxMode',
        'return_type': 'xAOD::TEvent::EAuxMode',
    },
    'dump': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TEvent',
        'method_name': 'dump',
        'return_type': 'string',
    },
    'addNameRemap': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TEvent',
        'method_name': 'addNameRemap',
        'return_type': 'StatusCode',
    },
    'inputEventFormat': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TEvent',
        'method_name': 'inputEventFormat',
        'return_type_element': '_Rb_tree_const_iterator<pair<const string, xAOD::EventFormatElement>>',
        'return_type_collection': 'const xAOD::EventFormat_v1 *',
    },
    'outputEventFormat': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TEvent',
        'method_name': 'outputEventFormat',
        'return_type_element': '_Rb_tree_const_iterator<pair<const string, xAOD::EventFormatElement>>',
        'return_type_collection': 'const xAOD::EventFormat_v1 *',
    },
    'addRef': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TEvent',
        'method_name': 'addRef',
        'return_type': 'unsigned long',
    },
    'release': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TEvent',
        'method_name': 'release',
        'return_type': 'unsigned long',
    },
    'name': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TEvent',
        'method_name': 'name',
        'return_type': 'const string',
    },
}

_enum_function_map = {
    'auxMode': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.TEvent',
            'name': 'EAuxMode',
            'values': [
                'kBranchAccess',
                'kClassAccess',
                'kAthenaAccess',
                'kUndefinedAccess',
            ],
        },
    ],      
}

_defined_enums = {
    'EAuxMode':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.TEvent',
            'name': 'EAuxMode',
            'values': [
                'kBranchAccess',
                'kClassAccess',
                'kAthenaAccess',
                'kUndefinedAccess',
            ],
        },      
}

_object_cpp_as_py_namespace="xAOD"

T = TypeVar('T')

def add_enum_info(s: ObjectStream[T], enum_name: str) -> ObjectStream[T]:
    '''Use this to add enum definition information to the backend.

    This can be used when you are writing a C++ function that needs to
    make sure a particular enum is defined.

    Args:
        s (ObjectStream[T]): The ObjectStream that is being updated
        enum_name (str): Name of the enum

    Raises:
        ValueError: If it is not known, a list of possibles is printed out

    Returns:
        ObjectStream[T]: Updated object stream with new metadata.
    '''
    if enum_name not in _defined_enums:
        raise ValueError(f"Enum {enum_name} is not known - "
                            f"choose from one of {','.join(_defined_enums.keys())}")
    return s.MetaData(_defined_enums[enum_name])

def _add_method_metadata(s: ObjectStream[T], a: ast.Call) -> Tuple[ObjectStream[T], ast.Call]:
    '''Add metadata for a collection to the func_adl stream if we know about it
    '''
    assert isinstance(a.func, ast.Attribute)
    if a.func.attr in _method_map:
        s_update = s.MetaData(_method_map[a.func.attr])

        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODRootAccess/TEvent.h',
            'body_includes': ["xAODRootAccess/TEvent.h"],
        })


        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODRootAccess',
            'link_libraries': ["xAODRootAccess"],
        })

        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class TEvent:
    "A class"

    class EAuxMode(Enum):
        kBranchAccess = 0
        kClassAccess = 1
        kAthenaAccess = 2
        kUndefinedAccess = 3


    def auxMode(self) -> func_adl_servicex_xaodr22.xAOD.tevent.TEvent.EAuxMode:
        "A method"
        ...

    def dump(self) -> str:
        "A method"
        ...

    def addNameRemap(self, onfile: str, newName: str) -> func_adl_servicex_xaodr22.statuscode.StatusCode:
        "A method"
        ...

    def inputEventFormat(self) -> func_adl_servicex_xaodr22.xAOD.eventformat_v1.EventFormat_v1:
        "A method"
        ...

    def outputEventFormat(self) -> func_adl_servicex_xaodr22.xAOD.eventformat_v1.EventFormat_v1:
        "A method"
        ...

    def addRef(self) -> int:
        "A method"
        ...

    def release(self) -> int:
        "A method"
        ...

    def name(self) -> str:
        "A method"
        ...
