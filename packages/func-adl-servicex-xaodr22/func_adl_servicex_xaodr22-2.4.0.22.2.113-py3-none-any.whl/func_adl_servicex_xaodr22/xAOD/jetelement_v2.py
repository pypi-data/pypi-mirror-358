from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr22

_method_map = {
    'eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetElement_v2',
        'method_name': 'eta',
        'return_type': 'float',
    },
    'phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetElement_v2',
        'method_name': 'phi',
        'return_type': 'float',
    },
    'key': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetElement_v2',
        'method_name': 'key',
        'return_type': 'unsigned int',
    },
    'peak': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetElement_v2',
        'method_name': 'peak',
        'return_type': 'uint8_t',
    },
    'emJetElementETVec': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetElement_v2',
        'method_name': 'emJetElementETVec',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned short>',
    },
    'hadJetElementETVec': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetElement_v2',
        'method_name': 'hadJetElementETVec',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned short>',
    },
    'emJetElementErrorVec': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetElement_v2',
        'method_name': 'emJetElementErrorVec',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned int>',
    },
    'hadJetElementErrorVec': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetElement_v2',
        'method_name': 'hadJetElementErrorVec',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned int>',
    },
    'linkErrorVec': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetElement_v2',
        'method_name': 'linkErrorVec',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned int>',
    },
    'emJetElementET': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetElement_v2',
        'method_name': 'emJetElementET',
        'return_type': 'unsigned int',
    },
    'hadJetElementET': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetElement_v2',
        'method_name': 'hadJetElementET',
        'return_type': 'unsigned int',
    },
    'et': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetElement_v2',
        'method_name': 'et',
        'return_type': 'unsigned int',
    },
    'emJetElementETSlice': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetElement_v2',
        'method_name': 'emJetElementETSlice',
        'return_type': 'unsigned int',
    },
    'hadJetElementETSlice': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetElement_v2',
        'method_name': 'hadJetElementETSlice',
        'return_type': 'unsigned int',
    },
    'sliceET': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetElement_v2',
        'method_name': 'sliceET',
        'return_type': 'unsigned int',
    },
    'isSaturated': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetElement_v2',
        'method_name': 'isSaturated',
        'return_type': 'bool',
    },
    'isEmSaturated': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetElement_v2',
        'method_name': 'isEmSaturated',
        'return_type': 'bool',
    },
    'isHadSaturated': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetElement_v2',
        'method_name': 'isHadSaturated',
        'return_type': 'bool',
    },
    'emJetElementError': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetElement_v2',
        'method_name': 'emJetElementError',
        'return_type': 'unsigned int',
    },
    'hadJetElementError': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetElement_v2',
        'method_name': 'hadJetElementError',
        'return_type': 'unsigned int',
    },
    'linkError': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetElement_v2',
        'method_name': 'linkError',
        'return_type': 'unsigned int',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetElement_v2',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetElement_v2',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetElement_v2',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetElement_v2',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetElement_v2',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetElement_v2',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetElement_v2',
        'method_name': 'trackIndices',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetElement_v2',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetElement_v2',
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
            'name': 'xAODTrigL1Calo/versions/JetElement_v2.h',
            'body_includes': ["xAODTrigL1Calo/versions/JetElement_v2.h"],
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
class JetElement_v2:
    "A class"


    def eta(self) -> float:
        "A method"
        ...

    def phi(self) -> float:
        "A method"
        ...

    def key(self) -> int:
        "A method"
        ...

    def peak(self) -> int:
        "A method"
        ...

    def emJetElementETVec(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def hadJetElementETVec(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def emJetElementErrorVec(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def hadJetElementErrorVec(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def linkErrorVec(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def emJetElementET(self) -> int:
        "A method"
        ...

    def hadJetElementET(self) -> int:
        "A method"
        ...

    def et(self) -> int:
        "A method"
        ...

    def emJetElementETSlice(self, slice: int) -> int:
        "A method"
        ...

    def hadJetElementETSlice(self, slice: int) -> int:
        "A method"
        ...

    def sliceET(self, slice: int) -> int:
        "A method"
        ...

    def isSaturated(self) -> bool:
        "A method"
        ...

    def isEmSaturated(self) -> bool:
        "A method"
        ...

    def isHadSaturated(self) -> bool:
        "A method"
        ...

    def emJetElementError(self) -> int:
        "A method"
        ...

    def hadJetElementError(self) -> int:
        "A method"
        ...

    def linkError(self) -> int:
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
