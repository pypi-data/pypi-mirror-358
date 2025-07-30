from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr22

_method_map = {
    'nRings': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RingSetConf_v1',
        'method_name': 'nRings',
        'return_type': 'unsigned int',
    },
    'nLayers': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RingSetConf_v1',
        'method_name': 'nLayers',
        'return_type': 'unsigned int',
    },
    'layerAt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RingSetConf_v1',
        'method_name': 'layerAt',
        'return_type': 'CaloSampling::CaloSample',
    },
    'etaWidth': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RingSetConf_v1',
        'method_name': 'etaWidth',
        'return_type': 'float',
    },
    'phiWidth': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RingSetConf_v1',
        'method_name': 'phiWidth',
        'return_type': 'float',
    },
    'cellMaxDEtaDist': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RingSetConf_v1',
        'method_name': 'cellMaxDEtaDist',
        'return_type': 'float',
    },
    'cellMaxDPhiDist': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RingSetConf_v1',
        'method_name': 'cellMaxDPhiDist',
        'return_type': 'float',
    },
    'doEtaAxesDivision': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RingSetConf_v1',
        'method_name': 'doEtaAxesDivision',
        'return_type': 'bool',
    },
    'doPhiAxesDivision': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RingSetConf_v1',
        'method_name': 'doPhiAxesDivision',
        'return_type': 'bool',
    },
    'calJointLayer': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RingSetConf_v1',
        'method_name': 'calJointLayer',
        'return_type': 'Ringer::CalJointLayer',
    },
    'calJointSection': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RingSetConf_v1',
        'method_name': 'calJointSection',
        'return_type': 'Ringer::CalJointSection',
    },
    'layerStartIdx': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RingSetConf_v1',
        'method_name': 'layerStartIdx',
        'return_type': 'unsigned int',
    },
    'sectionStartIdx': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RingSetConf_v1',
        'method_name': 'sectionStartIdx',
        'return_type': 'unsigned int',
    },
    'layerEndIdx': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RingSetConf_v1',
        'method_name': 'layerEndIdx',
        'return_type': 'unsigned int',
    },
    'sectionEndIdx': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RingSetConf_v1',
        'method_name': 'sectionEndIdx',
        'return_type': 'unsigned int',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RingSetConf_v1',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RingSetConf_v1',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RingSetConf_v1',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RingSetConf_v1',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RingSetConf_v1',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RingSetConf_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RingSetConf_v1',
        'method_name': 'trackIndices',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RingSetConf_v1',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RingSetConf_v1',
        'method_name': 'isAvailable',
        'return_type': 'bool',
    },
}

_enum_function_map = {
    'layerAt': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'CaloSampling',
            'name': 'CaloSample',
            'values': [
                'PreSamplerB',
                'EMB1',
                'EMB2',
                'EMB3',
                'PreSamplerE',
                'EME1',
                'EME2',
                'EME3',
                'HEC0',
                'HEC1',
                'HEC2',
                'HEC3',
                'TileBar0',
                'TileBar1',
                'TileBar2',
                'TileGap1',
                'TileGap2',
                'TileGap3',
                'TileExt0',
                'TileExt1',
                'TileExt2',
                'FCAL0',
                'FCAL1',
                'FCAL2',
                'MINIFCAL0',
                'MINIFCAL1',
                'MINIFCAL2',
                'MINIFCAL3',
                'Unknown',
            ],
        },
    ],
    'calJointLayer': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'Ringer',
            'name': 'CalJointLayer',
            'values': [
                'PS',
                'EM1',
                'EM2',
                'EM3',
                'HAD1',
                'HAD2',
                'HAD3',
                'NJointLayers',
                'UnknownJointLayer',
            ],
        },
    ],
    'calJointSection': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'Ringer',
            'name': 'CalJointSection',
            'values': [
                'EM',
                'HAD',
                'NJointSections',
                'UnknownJointSection',
            ],
        },
    ],      
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
            'name': 'xAODCaloRings/versions/RingSetConf_v1.h',
            'body_includes': ["xAODCaloRings/versions/RingSetConf_v1.h"],
        })


        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODCaloRings',
            'link_libraries': ["xAODCaloRings"],
        })

        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class RingSetConf_v1:
    "A class"


    def nRings(self) -> int:
        "A method"
        ...

    def nLayers(self) -> int:
        "A method"
        ...

    def layerAt(self, idx: int) -> func_adl_servicex_xaodr22.calosampling.CaloSampling.CaloSample:
        "A method"
        ...

    def etaWidth(self) -> float:
        "A method"
        ...

    def phiWidth(self) -> float:
        "A method"
        ...

    def cellMaxDEtaDist(self) -> float:
        "A method"
        ...

    def cellMaxDPhiDist(self) -> float:
        "A method"
        ...

    def doEtaAxesDivision(self) -> bool:
        "A method"
        ...

    def doPhiAxesDivision(self) -> bool:
        "A method"
        ...

    def calJointLayer(self) -> func_adl_servicex_xaodr22.ringer.Ringer.CalJointLayer:
        "A method"
        ...

    def calJointSection(self) -> func_adl_servicex_xaodr22.ringer.Ringer.CalJointSection:
        "A method"
        ...

    def layerStartIdx(self) -> int:
        "A method"
        ...

    def sectionStartIdx(self) -> int:
        "A method"
        ...

    def layerEndIdx(self) -> int:
        "A method"
        ...

    def sectionEndIdx(self) -> int:
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
