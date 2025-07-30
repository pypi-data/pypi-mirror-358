from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr22

_method_map = {
    'hashValue': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SystematicEvent',
        'method_name': 'hashValue',
        'return_type': 'unsigned int',
    },
    'ttreeIndex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SystematicEvent',
        'method_name': 'ttreeIndex',
        'return_type': 'unsigned int',
    },
    'isLooseEvent': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SystematicEvent',
        'method_name': 'isLooseEvent',
        'return_type': 'char',
    },
    'goodPhotons': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SystematicEvent',
        'method_name': 'goodPhotons',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned int>',
    },
    'goodElectrons': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SystematicEvent',
        'method_name': 'goodElectrons',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned int>',
    },
    'goodFwdElectrons': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SystematicEvent',
        'method_name': 'goodFwdElectrons',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned int>',
    },
    'goodMuons': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SystematicEvent',
        'method_name': 'goodMuons',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned int>',
    },
    'goodSoftMuons': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SystematicEvent',
        'method_name': 'goodSoftMuons',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned int>',
    },
    'goodTaus': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SystematicEvent',
        'method_name': 'goodTaus',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned int>',
    },
    'goodJets': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SystematicEvent',
        'method_name': 'goodJets',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned int>',
    },
    'goodLargeRJets': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SystematicEvent',
        'method_name': 'goodLargeRJets',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned int>',
    },
    'goodTrackJets': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SystematicEvent',
        'method_name': 'goodTrackJets',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned int>',
    },
    'goodTracks': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SystematicEvent',
        'method_name': 'goodTracks',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned int>',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SystematicEvent',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SystematicEvent',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SystematicEvent',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SystematicEvent',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SystematicEvent',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SystematicEvent',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SystematicEvent',
        'method_name': 'trackIndices',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SystematicEvent',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::SystematicEvent',
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
            'name': 'TopEvent/SystematicEvent.h',
            'body_includes': ["TopEvent/SystematicEvent.h"],
        })


        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'TopEvent',
            'link_libraries': ["TopEvent"],
        })

        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class SystematicEvent:
    "A class"


    def hashValue(self) -> int:
        "A method"
        ...

    def ttreeIndex(self) -> int:
        "A method"
        ...

    def isLooseEvent(self) -> str:
        "A method"
        ...

    def goodPhotons(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def goodElectrons(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def goodFwdElectrons(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def goodMuons(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def goodSoftMuons(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def goodTaus(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def goodJets(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def goodLargeRJets(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def goodTrackJets(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def goodTracks(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
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
