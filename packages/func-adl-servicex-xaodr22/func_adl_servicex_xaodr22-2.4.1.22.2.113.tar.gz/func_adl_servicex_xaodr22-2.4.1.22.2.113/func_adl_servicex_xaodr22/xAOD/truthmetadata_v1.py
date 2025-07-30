from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr22

_method_map = {
    'mcChannelNumber': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthMetaData_v1',
        'method_name': 'mcChannelNumber',
        'return_type': 'unsigned int',
    },
    'weightNames': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthMetaData_v1',
        'method_name': 'weightNames',
        'return_type_element': 'string',
        'return_type_collection': 'const vector<string>',
    },
    'lhefGenerator': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthMetaData_v1',
        'method_name': 'lhefGenerator',
        'return_type': 'const string',
    },
    'generators': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthMetaData_v1',
        'method_name': 'generators',
        'return_type': 'const string',
    },
    'evgenProcess': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthMetaData_v1',
        'method_name': 'evgenProcess',
        'return_type': 'const string',
    },
    'evgenTune': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthMetaData_v1',
        'method_name': 'evgenTune',
        'return_type': 'const string',
    },
    'hardPDF': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthMetaData_v1',
        'method_name': 'hardPDF',
        'return_type': 'const string',
    },
    'softPDF': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthMetaData_v1',
        'method_name': 'softPDF',
        'return_type': 'const string',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthMetaData_v1',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthMetaData_v1',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthMetaData_v1',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthMetaData_v1',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthMetaData_v1',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthMetaData_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthMetaData_v1',
        'method_name': 'trackIndices',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthMetaData_v1',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthMetaData_v1',
        'method_name': 'isAvailable',
        'return_type': 'bool',
    },
}

_enum_function_map = {      
}

_defined_enums = {      
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
            'name': 'xAODTruth/versions/TruthMetaData_v1.h',
            'body_includes': ["xAODTruth/versions/TruthMetaData_v1.h"],
        })


        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODTruth',
            'link_libraries': ["xAODTruth"],
        })

        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class TruthMetaData_v1:
    "A class"


    def mcChannelNumber(self) -> int:
        "A method"
        ...

    def weightNames(self) -> func_adl_servicex_xaodr22.vector_str_.vector_str_:
        "A method"
        ...

    def lhefGenerator(self) -> str:
        "A method"
        ...

    def generators(self) -> str:
        "A method"
        ...

    def evgenProcess(self) -> str:
        "A method"
        ...

    def evgenTune(self) -> str:
        "A method"
        ...

    def hardPDF(self) -> str:
        "A method"
        ...

    def softPDF(self) -> str:
        "A method"
        ...

    def index(self) -> int:
        "A method"
        ...

    def usingPrivateStore(self) -> bool:
        "A method"
        ...

    def usingStandaloneStore(self) -> bool:
        "A method"
        ...

    def hasStore(self) -> bool:
        "A method"
        ...

    def hasNonConstStore(self) -> bool:
        "A method"
        ...

    def clearDecorations(self) -> bool:
        "A method"
        ...

    def trackIndices(self) -> bool:
        "A method"
        ...

    @func_adl_parameterized_call(lambda s, a, param_1: func_adl_servicex_xaodr22.type_support.cpp_generic_1arg_callback('auxdataConst', s, a, param_1))
    @property
    def auxdataConst(self) -> func_adl_servicex_xaodr22.type_support.index_type_forwarder[str]:
        "A method"
        ...

    @func_adl_parameterized_call(lambda s, a, param_1: func_adl_servicex_xaodr22.type_support.cpp_generic_1arg_callback('isAvailable', s, a, param_1))
    @property
    def isAvailable(self) -> func_adl_servicex_xaodr22.type_support.index_type_forwarder[str]:
        "A method"
        ...
