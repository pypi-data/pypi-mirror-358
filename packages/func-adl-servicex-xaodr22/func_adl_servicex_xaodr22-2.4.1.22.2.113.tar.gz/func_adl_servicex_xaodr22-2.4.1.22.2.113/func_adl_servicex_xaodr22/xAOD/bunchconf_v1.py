from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr22

_method_map = {
    'configID': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BunchConf_v1',
        'method_name': 'configID',
        'return_type': 'unsigned int',
    },
    'collidingBCIDs': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BunchConf_v1',
        'method_name': 'collidingBCIDs',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'intensitiesBeam1': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BunchConf_v1',
        'method_name': 'intensitiesBeam1',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'intensitiesBeam1Available': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BunchConf_v1',
        'method_name': 'intensitiesBeam1Available',
        'return_type': 'bool',
    },
    'intensitiesBeam2': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BunchConf_v1',
        'method_name': 'intensitiesBeam2',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'intensitiesBeam2Available': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BunchConf_v1',
        'method_name': 'intensitiesBeam2Available',
        'return_type': 'bool',
    },
    'unpairedBCIDsBeam1': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BunchConf_v1',
        'method_name': 'unpairedBCIDsBeam1',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'unpairedBCIDsBeam1Available': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BunchConf_v1',
        'method_name': 'unpairedBCIDsBeam1Available',
        'return_type': 'bool',
    },
    'unpairedBCIDsBeam2': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BunchConf_v1',
        'method_name': 'unpairedBCIDsBeam2',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'unpairedBCIDsBeam2Available': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BunchConf_v1',
        'method_name': 'unpairedBCIDsBeam2Available',
        'return_type': 'bool',
    },
    'unpairedIntensisitesBeam1': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BunchConf_v1',
        'method_name': 'unpairedIntensisitesBeam1',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'unpairedIntensitiesBeam1Available': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BunchConf_v1',
        'method_name': 'unpairedIntensitiesBeam1Available',
        'return_type': 'bool',
    },
    'unpairedIntensisitesBeam2': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BunchConf_v1',
        'method_name': 'unpairedIntensisitesBeam2',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'unpairedIntensitiesBeam2Available': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BunchConf_v1',
        'method_name': 'unpairedIntensitiesBeam2Available',
        'return_type': 'bool',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BunchConf_v1',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BunchConf_v1',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BunchConf_v1',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BunchConf_v1',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BunchConf_v1',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BunchConf_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BunchConf_v1',
        'method_name': 'trackIndices',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BunchConf_v1',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BunchConf_v1',
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
            'name': 'xAODTrigger/versions/BunchConf_v1.h',
            'body_includes': ["xAODTrigger/versions/BunchConf_v1.h"],
        })


        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODTrigger',
            'link_libraries': ["xAODTrigger"],
        })

        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class BunchConf_v1:
    "A class"


    def configID(self) -> int:
        "A method"
        ...

    def collidingBCIDs(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def intensitiesBeam1(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def intensitiesBeam1Available(self) -> bool:
        "A method"
        ...

    def intensitiesBeam2(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def intensitiesBeam2Available(self) -> bool:
        "A method"
        ...

    def unpairedBCIDsBeam1(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def unpairedBCIDsBeam1Available(self) -> bool:
        "A method"
        ...

    def unpairedBCIDsBeam2(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def unpairedBCIDsBeam2Available(self) -> bool:
        "A method"
        ...

    def unpairedIntensisitesBeam1(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def unpairedIntensitiesBeam1Available(self) -> bool:
        "A method"
        ...

    def unpairedIntensisitesBeam2(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def unpairedIntensitiesBeam2Available(self) -> bool:
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
