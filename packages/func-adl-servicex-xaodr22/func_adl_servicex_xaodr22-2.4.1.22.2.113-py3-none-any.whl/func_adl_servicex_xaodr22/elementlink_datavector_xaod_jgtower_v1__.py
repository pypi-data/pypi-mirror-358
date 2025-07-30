from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr22

_method_map = {
    'isValid': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::JGTower_v1>>',
        'method_name': 'isValid',
        'return_type': 'bool',
    },
    'pt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::JGTower_v1>>',
        'method_name': 'pt',
        'return_type': 'double',
        'deref_count': 2
    },
    'eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::JGTower_v1>>',
        'method_name': 'eta',
        'return_type': 'double',
        'deref_count': 2
    },
    'phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::JGTower_v1>>',
        'method_name': 'phi',
        'return_type': 'double',
        'deref_count': 2
    },
    'deta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::JGTower_v1>>',
        'method_name': 'deta',
        'return_type': 'double',
        'deref_count': 2
    },
    'dphi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::JGTower_v1>>',
        'method_name': 'dphi',
        'return_type': 'double',
        'deref_count': 2
    },
    'et': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::JGTower_v1>>',
        'method_name': 'et',
        'return_type': 'double',
        'deref_count': 2
    },
    'Id': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::JGTower_v1>>',
        'method_name': 'Id',
        'return_type': 'int',
        'deref_count': 2
    },
    'sampling': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::JGTower_v1>>',
        'method_name': 'sampling',
        'return_type': 'int',
        'deref_count': 2
    },
    'SCIndex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::JGTower_v1>>',
        'method_name': 'SCIndex',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
        'deref_count': 2
    },
    'TileIndex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::JGTower_v1>>',
        'method_name': 'TileIndex',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
        'deref_count': 2
    },
    'm': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::JGTower_v1>>',
        'method_name': 'm',
        'return_type': 'double',
        'deref_count': 2
    },
    'e': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::JGTower_v1>>',
        'method_name': 'e',
        'return_type': 'double',
        'deref_count': 2
    },
    'rapidity': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::JGTower_v1>>',
        'method_name': 'rapidity',
        'return_type': 'double',
        'deref_count': 2
    },
    'p4': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::JGTower_v1>>',
        'method_name': 'p4',
        'return_type': 'TLorentzVector',
        'deref_count': 2
    },
    'type': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::JGTower_v1>>',
        'method_name': 'type',
        'return_type': 'xAODType::ObjectType',
        'deref_count': 2
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::JGTower_v1>>',
        'method_name': 'index',
        'return_type': 'unsigned int',
        'deref_count': 2
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::JGTower_v1>>',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
        'deref_count': 2
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::JGTower_v1>>',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
        'deref_count': 2
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::JGTower_v1>>',
        'method_name': 'hasStore',
        'return_type': 'bool',
        'deref_count': 2
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::JGTower_v1>>',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
        'deref_count': 2
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::JGTower_v1>>',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
        'deref_count': 2
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::JGTower_v1>>',
        'method_name': 'trackIndices',
        'return_type': 'bool',
        'deref_count': 2
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::JGTower_v1>>',
        'method_name': 'auxdataConst',
        'return_type': 'U',
        'deref_count': 2
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::JGTower_v1>>',
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
            'name': 'xAODTrigL1Calo/versions/JGTower_v1.h',
            'body_includes': ["xAODTrigL1Calo/versions/JGTower_v1.h"],
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
class ElementLink_DataVector_xAOD_JGTower_v1__:
    "A class"


    def isValid(self) -> bool:
        "A method"
        ...

    def pt(self) -> float:
        "A method"
        ...

    def eta(self) -> float:
        "A method"
        ...

    def phi(self) -> float:
        "A method"
        ...

    def deta(self) -> float:
        "A method"
        ...

    def dphi(self) -> float:
        "A method"
        ...

    def et(self) -> float:
        "A method"
        ...

    def Id(self) -> int:
        "A method"
        ...

    def sampling(self) -> int:
        "A method"
        ...

    def SCIndex(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def TileIndex(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def m(self) -> float:
        "A method"
        ...

    def e(self) -> float:
        "A method"
        ...

    def rapidity(self) -> float:
        "A method"
        ...

    def p4(self) -> func_adl_servicex_xaodr22.tlorentzvector.TLorentzVector:
        "A method"
        ...

    def type(self) -> func_adl_servicex_xaodr22.xaodtype.xAODType.ObjectType:
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
