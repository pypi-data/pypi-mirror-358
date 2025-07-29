from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr22

_method_map = {
    'identifier': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SCTRawHitValidation_v1',
        'method_name': 'identifier',
        'return_type': 'uint64_t',
    },
    'getWord': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SCTRawHitValidation_v1',
        'method_name': 'getWord',
        'return_type': 'unsigned int',
    },
    'getGroupSize': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SCTRawHitValidation_v1',
        'method_name': 'getGroupSize',
        'return_type': 'int',
    },
    'getStrip': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SCTRawHitValidation_v1',
        'method_name': 'getStrip',
        'return_type': 'int',
    },
    'getTimeBin': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SCTRawHitValidation_v1',
        'method_name': 'getTimeBin',
        'return_type': 'int',
    },
    'getErrors': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SCTRawHitValidation_v1',
        'method_name': 'getErrors',
        'return_type': 'int',
    },
    'OnTime': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SCTRawHitValidation_v1',
        'method_name': 'OnTime',
        'return_type': 'bool',
    },
    'FirstHitError': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SCTRawHitValidation_v1',
        'method_name': 'FirstHitError',
        'return_type': 'bool',
    },
    'SecondHitError': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SCTRawHitValidation_v1',
        'method_name': 'SecondHitError',
        'return_type': 'bool',
    },
    'bec': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SCTRawHitValidation_v1',
        'method_name': 'bec',
        'return_type': 'int',
    },
    'layer': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SCTRawHitValidation_v1',
        'method_name': 'layer',
        'return_type': 'int',
    },
    'eta_module': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SCTRawHitValidation_v1',
        'method_name': 'eta_module',
        'return_type': 'int',
    },
    'phi_module': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SCTRawHitValidation_v1',
        'method_name': 'phi_module',
        'return_type': 'int',
    },
    'side': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SCTRawHitValidation_v1',
        'method_name': 'side',
        'return_type': 'int',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SCTRawHitValidation_v1',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SCTRawHitValidation_v1',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SCTRawHitValidation_v1',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SCTRawHitValidation_v1',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SCTRawHitValidation_v1',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SCTRawHitValidation_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SCTRawHitValidation_v1',
        'method_name': 'trackIndices',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SCTRawHitValidation_v1',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SCTRawHitValidation_v1',
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
            'name': 'xAODTracking/versions/SCTRawHitValidation_v1.h',
            'body_includes': ["xAODTracking/versions/SCTRawHitValidation_v1.h"],
        })


        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODTracking',
            'link_libraries': ["xAODTracking"],
        })

        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class SCTRawHitValidation_v1:
    "A class"


    def identifier(self) -> int:
        "A method"
        ...

    def getWord(self) -> int:
        "A method"
        ...

    def getGroupSize(self) -> int:
        "A method"
        ...

    def getStrip(self) -> int:
        "A method"
        ...

    def getTimeBin(self) -> int:
        "A method"
        ...

    def getErrors(self) -> int:
        "A method"
        ...

    def OnTime(self) -> bool:
        "A method"
        ...

    def FirstHitError(self) -> bool:
        "A method"
        ...

    def SecondHitError(self) -> bool:
        "A method"
        ...

    def bec(self) -> int:
        "A method"
        ...

    def layer(self) -> int:
        "A method"
        ...

    def eta_module(self) -> int:
        "A method"
        ...

    def phi_module(self) -> int:
        "A method"
        ...

    def side(self) -> int:
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
