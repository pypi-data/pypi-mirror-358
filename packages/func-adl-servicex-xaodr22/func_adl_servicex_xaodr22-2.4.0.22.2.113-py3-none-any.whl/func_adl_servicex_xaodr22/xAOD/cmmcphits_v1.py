from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr22

_method_map = {
    'crate': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMCPHits_v1',
        'method_name': 'crate',
        'return_type': 'int',
    },
    'dataID': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMCPHits_v1',
        'method_name': 'dataID',
        'return_type': 'int',
    },
    'peak': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMCPHits_v1',
        'method_name': 'peak',
        'return_type': 'int',
    },
    'hitsVec0': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMCPHits_v1',
        'method_name': 'hitsVec0',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned int>',
    },
    'hitsVec1': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMCPHits_v1',
        'method_name': 'hitsVec1',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned int>',
    },
    'errorVec0': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMCPHits_v1',
        'method_name': 'errorVec0',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'errorVec1': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMCPHits_v1',
        'method_name': 'errorVec1',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'hitWord0': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMCPHits_v1',
        'method_name': 'hitWord0',
        'return_type': 'unsigned int',
    },
    'hitWord1': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMCPHits_v1',
        'method_name': 'hitWord1',
        'return_type': 'unsigned int',
    },
    'error0': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMCPHits_v1',
        'method_name': 'error0',
        'return_type': 'int',
    },
    'error1': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMCPHits_v1',
        'method_name': 'error1',
        'return_type': 'int',
    },
    'HitWord0': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMCPHits_v1',
        'method_name': 'HitWord0',
        'return_type': 'unsigned int',
    },
    'HitWord1': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMCPHits_v1',
        'method_name': 'HitWord1',
        'return_type': 'unsigned int',
    },
    'Error0': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMCPHits_v1',
        'method_name': 'Error0',
        'return_type': 'int',
    },
    'Error1': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMCPHits_v1',
        'method_name': 'Error1',
        'return_type': 'int',
    },
    'HitsVec0': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMCPHits_v1',
        'method_name': 'HitsVec0',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned int>',
    },
    'HitsVec1': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMCPHits_v1',
        'method_name': 'HitsVec1',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned int>',
    },
    'ErrorVec0': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMCPHits_v1',
        'method_name': 'ErrorVec0',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'ErrorVec1': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMCPHits_v1',
        'method_name': 'ErrorVec1',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMCPHits_v1',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMCPHits_v1',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMCPHits_v1',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMCPHits_v1',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMCPHits_v1',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMCPHits_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMCPHits_v1',
        'method_name': 'trackIndices',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMCPHits_v1',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMCPHits_v1',
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
            'name': 'xAODTrigL1Calo/versions/CMMCPHits_v1.h',
            'body_includes': ["xAODTrigL1Calo/versions/CMMCPHits_v1.h"],
        })


        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODTrigL1Calo',
            'link_libraries': ["xAODTrigL1Calo"],
        })

        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class CMMCPHits_v1:
    "A class"


    def crate(self) -> int:
        "A method"
        ...

    def dataID(self) -> int:
        "A method"
        ...

    def peak(self) -> int:
        "A method"
        ...

    def hitsVec0(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def hitsVec1(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def errorVec0(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def errorVec1(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def hitWord0(self) -> int:
        "A method"
        ...

    def hitWord1(self) -> int:
        "A method"
        ...

    def error0(self) -> int:
        "A method"
        ...

    def error1(self) -> int:
        "A method"
        ...

    def HitWord0(self) -> int:
        "A method"
        ...

    def HitWord1(self) -> int:
        "A method"
        ...

    def Error0(self) -> int:
        "A method"
        ...

    def Error1(self) -> int:
        "A method"
        ...

    def HitsVec0(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def HitsVec1(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def ErrorVec0(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def ErrorVec1(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
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
