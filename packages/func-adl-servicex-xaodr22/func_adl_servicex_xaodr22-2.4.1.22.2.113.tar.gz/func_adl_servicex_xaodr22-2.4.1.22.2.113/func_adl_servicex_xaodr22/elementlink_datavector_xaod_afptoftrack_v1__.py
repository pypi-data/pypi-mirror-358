from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr22

_method_map = {
    'isValid': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::AFPToFTrack_v1>>',
        'method_name': 'isValid',
        'return_type': 'bool',
    },
    'stationID': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::AFPToFTrack_v1>>',
        'method_name': 'stationID',
        'return_type': 'int',
        'deref_count': 2
    },
    'trainTime': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::AFPToFTrack_v1>>',
        'method_name': 'trainTime',
        'return_type': 'float',
        'deref_count': 2
    },
    'trainID': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::AFPToFTrack_v1>>',
        'method_name': 'trainID',
        'return_type': 'int',
        'deref_count': 2
    },
    'trainSize': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::AFPToFTrack_v1>>',
        'method_name': 'trainSize',
        'return_type': 'int',
        'deref_count': 2
    },
    'trainNSat': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::AFPToFTrack_v1>>',
        'method_name': 'trainNSat',
        'return_type': 'int',
        'deref_count': 2
    },
    'hits': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::AFPToFTrack_v1>>',
        'method_name': 'hits',
        'return_type_element': 'ElementLink<DataVector<xAOD::AFPToFHit_v1>>',
        'return_type_collection': 'const vector<ElementLink<DataVector<xAOD::AFPToFHit_v1>>>',
        'deref_count': 2
    },
    'algID': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::AFPToFTrack_v1>>',
        'method_name': 'algID',
        'return_type': 'int',
        'deref_count': 2
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::AFPToFTrack_v1>>',
        'method_name': 'index',
        'return_type': 'unsigned int',
        'deref_count': 2
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::AFPToFTrack_v1>>',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
        'deref_count': 2
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::AFPToFTrack_v1>>',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
        'deref_count': 2
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::AFPToFTrack_v1>>',
        'method_name': 'hasStore',
        'return_type': 'bool',
        'deref_count': 2
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::AFPToFTrack_v1>>',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
        'deref_count': 2
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::AFPToFTrack_v1>>',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
        'deref_count': 2
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::AFPToFTrack_v1>>',
        'method_name': 'trackIndices',
        'return_type': 'bool',
        'deref_count': 2
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::AFPToFTrack_v1>>',
        'method_name': 'auxdataConst',
        'return_type': 'U',
        'deref_count': 2
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::AFPToFTrack_v1>>',
        'method_name': 'isAvailable',
        'return_type': 'bool',
        'deref_count': 2
    },
}

_enum_function_map = {      
}

_defined_enums = {      
}

_object_cpp_as_py_namespace=""

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
            'name': 'xAODForward/versions/AFPToFTrack_v1.h',
            'body_includes': ["xAODForward/versions/AFPToFTrack_v1.h"],
        })


        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODForward',
            'link_libraries': ["xAODForward"],
        })

        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class ElementLink_DataVector_xAOD_AFPToFTrack_v1__:
    "A class"


    def isValid(self) -> bool:
        "A method"
        ...

    def stationID(self) -> int:
        "A method"
        ...

    def trainTime(self) -> float:
        "A method"
        ...

    def trainID(self) -> int:
        "A method"
        ...

    def trainSize(self) -> int:
        "A method"
        ...

    def trainNSat(self) -> int:
        "A method"
        ...

    def hits(self) -> func_adl_servicex_xaodr22.vector_elementlink_datavector_xaod_afptofhit_v1___.vector_ElementLink_DataVector_xAOD_AFPToFHit_v1___:
        "A method"
        ...

    def algID(self) -> int:
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
