from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr22

_method_map = {
    'eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonRoI_v1',
        'method_name': 'eta',
        'return_type': 'float',
    },
    'phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonRoI_v1',
        'method_name': 'phi',
        'return_type': 'float',
    },
    'roiWord': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonRoI_v1',
        'method_name': 'roiWord',
        'return_type': 'unsigned int',
    },
    'thrValue': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonRoI_v1',
        'method_name': 'thrValue',
        'return_type': 'float',
    },
    'thrName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonRoI_v1',
        'method_name': 'thrName',
        'return_type': 'const string',
    },
    'getThrNumber': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonRoI_v1',
        'method_name': 'getThrNumber',
        'return_type': 'int',
    },
    'getRoI': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonRoI_v1',
        'method_name': 'getRoI',
        'return_type': 'int',
    },
    'getSectorAddress': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonRoI_v1',
        'method_name': 'getSectorAddress',
        'return_type': 'int',
    },
    'getSectorID': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonRoI_v1',
        'method_name': 'getSectorID',
        'return_type': 'int',
    },
    'isFirstCandidate': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonRoI_v1',
        'method_name': 'isFirstCandidate',
        'return_type': 'bool',
    },
    'isMoreCandInRoI': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonRoI_v1',
        'method_name': 'isMoreCandInRoI',
        'return_type': 'bool',
    },
    'isMoreCandInSector': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonRoI_v1',
        'method_name': 'isMoreCandInSector',
        'return_type': 'bool',
    },
    'getSource': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonRoI_v1',
        'method_name': 'getSource',
        'return_type': 'xAOD::MuonRoI_v1::RoISource',
    },
    'getHemisphere': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonRoI_v1',
        'method_name': 'getHemisphere',
        'return_type': 'xAOD::MuonRoI_v1::Hemisphere',
    },
    'getPhiOverlap': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonRoI_v1',
        'method_name': 'getPhiOverlap',
        'return_type': 'bool',
    },
    'getEtaOverlap': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonRoI_v1',
        'method_name': 'getEtaOverlap',
        'return_type': 'bool',
    },
    'getCharge': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonRoI_v1',
        'method_name': 'getCharge',
        'return_type': 'xAOD::MuonRoI_v1::Charge',
    },
    'getBW3Coincidence': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonRoI_v1',
        'method_name': 'getBW3Coincidence',
        'return_type': 'bool',
    },
    'getInnerCoincidence': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonRoI_v1',
        'method_name': 'getInnerCoincidence',
        'return_type': 'bool',
    },
    'getGoodMF': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonRoI_v1',
        'method_name': 'getGoodMF',
        'return_type': 'bool',
    },
    'isVetoed': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonRoI_v1',
        'method_name': 'isVetoed',
        'return_type': 'bool',
    },
    'isRun3': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonRoI_v1',
        'method_name': 'isRun3',
        'return_type': 'bool',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonRoI_v1',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonRoI_v1',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonRoI_v1',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonRoI_v1',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonRoI_v1',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonRoI_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonRoI_v1',
        'method_name': 'trackIndices',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonRoI_v1',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonRoI_v1',
        'method_name': 'isAvailable',
        'return_type': 'bool',
    },
}

_enum_function_map = {
    'getSource': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.MuonRoI_v1',
            'name': 'RoISource',
            'values': [
                'Barrel',
                'Endcap',
                'Forward',
            ],
        },
    ],
    'getHemisphere': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.MuonRoI_v1',
            'name': 'Hemisphere',
            'values': [
                'Positive',
                'Negative',
            ],
        },
    ],
    'getCharge': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.MuonRoI_v1',
            'name': 'Charge',
            'values': [
                'Neg',
                'Pos',
                'Undef',
            ],
        },
    ],      
}

_defined_enums = {
    'RoISource':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.MuonRoI_v1',
            'name': 'RoISource',
            'values': [
                'Barrel',
                'Endcap',
                'Forward',
            ],
        },
    'Hemisphere':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.MuonRoI_v1',
            'name': 'Hemisphere',
            'values': [
                'Positive',
                'Negative',
            ],
        },
    'Charge':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.MuonRoI_v1',
            'name': 'Charge',
            'values': [
                'Neg',
                'Pos',
                'Undef',
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

        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODTrigger/versions/MuonRoI_v1.h',
            'body_includes': ["xAODTrigger/versions/MuonRoI_v1.h"],
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
class MuonRoI_v1:
    "A class"

    class RoISource(Enum):
        Barrel = 0
        Endcap = 1
        Forward = 2

    class Hemisphere(Enum):
        Positive = 0
        Negative = 1

    class Charge(Enum):
        Neg = 0
        Pos = 1
        Undef = 100


    def eta(self) -> float:
        "A method"
        ...

    def phi(self) -> float:
        "A method"
        ...

    def roiWord(self) -> int:
        "A method"
        ...

    def thrValue(self) -> float:
        "A method"
        ...

    def thrName(self) -> str:
        "A method"
        ...

    def getThrNumber(self) -> int:
        "A method"
        ...

    def getRoI(self) -> int:
        "A method"
        ...

    def getSectorAddress(self) -> int:
        "A method"
        ...

    def getSectorID(self) -> int:
        "A method"
        ...

    def isFirstCandidate(self) -> bool:
        "A method"
        ...

    def isMoreCandInRoI(self) -> bool:
        "A method"
        ...

    def isMoreCandInSector(self) -> bool:
        "A method"
        ...

    def getSource(self) -> func_adl_servicex_xaodr22.xAOD.muonroi_v1.MuonRoI_v1.RoISource:
        "A method"
        ...

    def getHemisphere(self) -> func_adl_servicex_xaodr22.xAOD.muonroi_v1.MuonRoI_v1.Hemisphere:
        "A method"
        ...

    def getPhiOverlap(self) -> bool:
        "A method"
        ...

    def getEtaOverlap(self) -> bool:
        "A method"
        ...

    def getCharge(self) -> func_adl_servicex_xaodr22.xAOD.muonroi_v1.MuonRoI_v1.Charge:
        "A method"
        ...

    def getBW3Coincidence(self) -> bool:
        "A method"
        ...

    def getInnerCoincidence(self) -> bool:
        "A method"
        ...

    def getGoodMF(self) -> bool:
        "A method"
        ...

    def isVetoed(self) -> bool:
        "A method"
        ...

    def isRun3(self) -> bool:
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
