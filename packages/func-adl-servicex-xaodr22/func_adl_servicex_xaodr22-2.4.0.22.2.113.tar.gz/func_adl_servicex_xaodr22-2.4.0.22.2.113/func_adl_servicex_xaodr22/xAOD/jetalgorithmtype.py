from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr22

_method_map = {
    'algName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetAlgorithmType',
        'method_name': 'algName',
        'return_type': 'const string',
    },
    'algId': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetAlgorithmType',
        'method_name': 'algId',
        'return_type': 'xAOD::JetAlgorithmType::ID',
    },
}

_enum_function_map = {
    'algName': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.JetAlgorithmType',
            'name': 'ID',
            'values': [
                'kt_algorithm',
                'cambridge_algorithm',
                'antikt_algorithm',
                'genkt_algorithm',
                'cambridge_for_passive_algorithm',
                'genkt_for_passive_algorithm',
                'ee_kt_algorithm',
                'ee_genkt_algorithm',
                'plugin_algorithm',
                'undefined_jet_algorithm',
            ],
        },
    ],
    'algId': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.JetAlgorithmType',
            'name': 'ID',
            'values': [
                'kt_algorithm',
                'cambridge_algorithm',
                'antikt_algorithm',
                'genkt_algorithm',
                'cambridge_for_passive_algorithm',
                'genkt_for_passive_algorithm',
                'ee_kt_algorithm',
                'ee_genkt_algorithm',
                'plugin_algorithm',
                'undefined_jet_algorithm',
            ],
        },
    ],      
}

_defined_enums = {
    'ID':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.JetAlgorithmType',
            'name': 'ID',
            'values': [
                'kt_algorithm',
                'cambridge_algorithm',
                'antikt_algorithm',
                'genkt_algorithm',
                'cambridge_for_passive_algorithm',
                'genkt_for_passive_algorithm',
                'ee_kt_algorithm',
                'ee_genkt_algorithm',
                'plugin_algorithm',
                'undefined_jet_algorithm',
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


        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class JetAlgorithmType:
    "A class"

    class ID(Enum):
        kt_algorithm = 0
        cambridge_algorithm = 1
        antikt_algorithm = 2
        genkt_algorithm = 3
        cambridge_for_passive_algorithm = 11
        genkt_for_passive_algorithm = 13
        ee_kt_algorithm = 50
        ee_genkt_algorithm = 53
        plugin_algorithm = 99
        undefined_jet_algorithm = 999


    def algName(self, id: func_adl_servicex_xaodr22.xAOD.jetalgorithmtype.JetAlgorithmType.ID) -> str:
        "A method"
        ...

    def algId(self, n: str) -> func_adl_servicex_xaodr22.xAOD.jetalgorithmtype.JetAlgorithmType.ID:
        "A method"
        ...
