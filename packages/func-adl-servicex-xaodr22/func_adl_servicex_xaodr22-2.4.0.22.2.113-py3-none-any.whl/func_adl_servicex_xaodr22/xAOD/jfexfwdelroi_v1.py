from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr22

_method_map = {
    'tobWord': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexFwdElRoI_v1',
        'method_name': 'tobWord',
        'return_type': 'unsigned int',
    },
    'tobEt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexFwdElRoI_v1',
        'method_name': 'tobEt',
        'return_type': 'uint16_t',
    },
    'tobEMIso': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexFwdElRoI_v1',
        'method_name': 'tobEMIso',
        'return_type': 'uint8_t',
    },
    'tobEMf1': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexFwdElRoI_v1',
        'method_name': 'tobEMf1',
        'return_type': 'uint8_t',
    },
    'tobEMf2': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexFwdElRoI_v1',
        'method_name': 'tobEMf2',
        'return_type': 'uint8_t',
    },
    'tobLocalEta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexFwdElRoI_v1',
        'method_name': 'tobLocalEta',
        'return_type': 'uint8_t',
    },
    'tobLocalPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexFwdElRoI_v1',
        'method_name': 'tobLocalPhi',
        'return_type': 'uint8_t',
    },
    'tobSat': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexFwdElRoI_v1',
        'method_name': 'tobSat',
        'return_type': 'uint8_t',
    },
    'globalEta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexFwdElRoI_v1',
        'method_name': 'globalEta',
        'return_type': 'int',
    },
    'globalPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexFwdElRoI_v1',
        'method_name': 'globalPhi',
        'return_type': 'uint',
    },
    'jFexNumber': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexFwdElRoI_v1',
        'method_name': 'jFexNumber',
        'return_type': 'uint8_t',
    },
    'fpgaNumber': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexFwdElRoI_v1',
        'method_name': 'fpgaNumber',
        'return_type': 'uint8_t',
    },
    'eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexFwdElRoI_v1',
        'method_name': 'eta',
        'return_type': 'float',
    },
    'phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexFwdElRoI_v1',
        'method_name': 'phi',
        'return_type': 'float',
    },
    'tobEtScale': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexFwdElRoI_v1',
        'method_name': 'tobEtScale',
        'return_type': 'int',
    },
    'isTOB': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexFwdElRoI_v1',
        'method_name': 'isTOB',
        'return_type': 'char',
    },
    'EtEMiso': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexFwdElRoI_v1',
        'method_name': 'EtEMiso',
        'return_type': 'uint16_t',
    },
    'EtEM': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexFwdElRoI_v1',
        'method_name': 'EtEM',
        'return_type': 'uint16_t',
    },
    'EtHad1': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexFwdElRoI_v1',
        'method_name': 'EtHad1',
        'return_type': 'uint16_t',
    },
    'EtHad2': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexFwdElRoI_v1',
        'method_name': 'EtHad2',
        'return_type': 'uint16_t',
    },
    'unpackEtTOB': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexFwdElRoI_v1',
        'method_name': 'unpackEtTOB',
        'return_type': 'unsigned int',
    },
    'et': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexFwdElRoI_v1',
        'method_name': 'et',
        'return_type': 'unsigned int',
    },
    'unpackEMIsoTOB': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexFwdElRoI_v1',
        'method_name': 'unpackEMIsoTOB',
        'return_type': 'unsigned int',
    },
    'unpackEMf1TOB': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexFwdElRoI_v1',
        'method_name': 'unpackEMf1TOB',
        'return_type': 'unsigned int',
    },
    'unpackEMf2TOB': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexFwdElRoI_v1',
        'method_name': 'unpackEMf2TOB',
        'return_type': 'unsigned int',
    },
    'unpackEtaIndex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexFwdElRoI_v1',
        'method_name': 'unpackEtaIndex',
        'return_type': 'unsigned int',
    },
    'unpackPhiIndex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexFwdElRoI_v1',
        'method_name': 'unpackPhiIndex',
        'return_type': 'unsigned int',
    },
    'unpackSaturationIndex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexFwdElRoI_v1',
        'method_name': 'unpackSaturationIndex',
        'return_type': 'unsigned int',
    },
    'getGlobalEta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexFwdElRoI_v1',
        'method_name': 'getGlobalEta',
        'return_type': 'int',
    },
    'getGlobalPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexFwdElRoI_v1',
        'method_name': 'getGlobalPhi',
        'return_type': 'uint',
    },
    'getEtEMiso': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexFwdElRoI_v1',
        'method_name': 'getEtEMiso',
        'return_type': 'unsigned int',
    },
    'getEtEM': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexFwdElRoI_v1',
        'method_name': 'getEtEM',
        'return_type': 'unsigned int',
    },
    'getEtHad1': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexFwdElRoI_v1',
        'method_name': 'getEtHad1',
        'return_type': 'unsigned int',
    },
    'getEtHad2': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexFwdElRoI_v1',
        'method_name': 'getEtHad2',
        'return_type': 'unsigned int',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexFwdElRoI_v1',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexFwdElRoI_v1',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexFwdElRoI_v1',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexFwdElRoI_v1',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexFwdElRoI_v1',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexFwdElRoI_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexFwdElRoI_v1',
        'method_name': 'trackIndices',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexFwdElRoI_v1',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexFwdElRoI_v1',
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
            'name': 'xAODTrigger/versions/jFexFwdElRoI_v1.h',
            'body_includes': ["xAODTrigger/versions/jFexFwdElRoI_v1.h"],
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
class jFexFwdElRoI_v1:
    "A class"


    def tobWord(self) -> int:
        "A method"
        ...

    def tobEt(self) -> int:
        "A method"
        ...

    def tobEMIso(self) -> int:
        "A method"
        ...

    def tobEMf1(self) -> int:
        "A method"
        ...

    def tobEMf2(self) -> int:
        "A method"
        ...

    def tobLocalEta(self) -> int:
        "A method"
        ...

    def tobLocalPhi(self) -> int:
        "A method"
        ...

    def tobSat(self) -> int:
        "A method"
        ...

    def globalEta(self) -> int:
        "A method"
        ...

    def globalPhi(self) -> int:
        "A method"
        ...

    def jFexNumber(self) -> int:
        "A method"
        ...

    def fpgaNumber(self) -> int:
        "A method"
        ...

    def eta(self) -> float:
        "A method"
        ...

    def phi(self) -> float:
        "A method"
        ...

    def tobEtScale(self) -> int:
        "A method"
        ...

    def isTOB(self) -> str:
        "A method"
        ...

    def EtEMiso(self) -> int:
        "A method"
        ...

    def EtEM(self) -> int:
        "A method"
        ...

    def EtHad1(self) -> int:
        "A method"
        ...

    def EtHad2(self) -> int:
        "A method"
        ...

    def unpackEtTOB(self) -> int:
        "A method"
        ...

    def et(self) -> int:
        "A method"
        ...

    def unpackEMIsoTOB(self) -> int:
        "A method"
        ...

    def unpackEMf1TOB(self) -> int:
        "A method"
        ...

    def unpackEMf2TOB(self) -> int:
        "A method"
        ...

    def unpackEtaIndex(self) -> int:
        "A method"
        ...

    def unpackPhiIndex(self) -> int:
        "A method"
        ...

    def unpackSaturationIndex(self) -> int:
        "A method"
        ...

    def getGlobalEta(self) -> int:
        "A method"
        ...

    def getGlobalPhi(self) -> int:
        "A method"
        ...

    def getEtEMiso(self) -> int:
        "A method"
        ...

    def getEtEM(self) -> int:
        "A method"
        ...

    def getEtHad1(self) -> int:
        "A method"
        ...

    def getEtHad2(self) -> int:
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
