from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr22

_method_map = {
    'pt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::GBlock_v1',
        'method_name': 'pt',
        'return_type': 'double',
    },
    'eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::GBlock_v1',
        'method_name': 'eta',
        'return_type': 'double',
    },
    'phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::GBlock_v1',
        'method_name': 'phi',
        'return_type': 'double',
    },
    'deta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::GBlock_v1',
        'method_name': 'deta',
        'return_type': 'float',
    },
    'dphi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::GBlock_v1',
        'method_name': 'dphi',
        'return_type': 'float',
    },
    'et': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::GBlock_v1',
        'method_name': 'et',
        'return_type': 'float',
    },
    'm': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::GBlock_v1',
        'method_name': 'm',
        'return_type': 'double',
    },
    'e': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::GBlock_v1',
        'method_name': 'e',
        'return_type': 'double',
    },
    'rapidity': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::GBlock_v1',
        'method_name': 'rapidity',
        'return_type': 'double',
    },
    'p4': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::GBlock_v1',
        'method_name': 'p4',
        'return_type': 'TLorentzVector',
    },
    'type': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::GBlock_v1',
        'method_name': 'type',
        'return_type': 'xAODType::ObjectType',
    },
    'seedTowerLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::GBlock_v1',
        'method_name': 'seedTowerLink',
        'return_type': 'const ElementLink<DataVector<xAOD::JGTower_v1>>',
    },
    'seedTower': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::GBlock_v1',
        'method_name': 'seedTower',
        'return_type': 'const xAOD::JGTower_v1 *',
    },
    'nTowers': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::GBlock_v1',
        'method_name': 'nTowers',
        'return_type': 'unsigned int',
    },
    'towerLinks': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::GBlock_v1',
        'method_name': 'towerLinks',
        'return_type_element': 'ElementLink<DataVector<xAOD::JGTower_v1>>',
        'return_type_collection': 'const vector<ElementLink<DataVector<xAOD::JGTower_v1>>>',
    },
    'getTower': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::GBlock_v1',
        'method_name': 'getTower',
        'return_type': 'const xAOD::JGTower_v1 *',
    },
    'area': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::GBlock_v1',
        'method_name': 'area',
        'return_type': 'float',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::GBlock_v1',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::GBlock_v1',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::GBlock_v1',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::GBlock_v1',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::GBlock_v1',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::GBlock_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::GBlock_v1',
        'method_name': 'trackIndices',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::GBlock_v1',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::GBlock_v1',
        'method_name': 'isAvailable',
        'return_type': 'bool',
    },
}

_enum_function_map = {
    'type': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAODType',
            'name': 'ObjectType',
            'values': [
                'Other',
                'CaloCluster',
                'Jet',
                'ParticleFlow',
                'TrackParticle',
                'NeutralParticle',
                'Electron',
                'Photon',
                'Muon',
                'Tau',
                'TrackCaloCluster',
                'FlowElement',
                'Vertex',
                'BTag',
                'TruthParticle',
                'TruthVertex',
                'TruthEvent',
                'TruthPileupEvent',
                'L2StandAloneMuon',
                'L2IsoMuon',
                'L2CombinedMuon',
                'TrigElectron',
                'TrigPhoton',
                'TrigCaloCluster',
                'TrigEMCluster',
                'EventInfo',
                'EventFormat',
                'Particle',
                'CompositeParticle',
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
            'name': 'xAODTrigL1Calo/versions/GBlock_v1.h',
            'body_includes': ["xAODTrigL1Calo/versions/GBlock_v1.h"],
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
class GBlock_v1:
    "A class"


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

    def seedTowerLink(self) -> func_adl_servicex_xaodr22.elementlink_datavector_xaod_jgtower_v1__.ElementLink_DataVector_xAOD_JGTower_v1__:
        "A method"
        ...

    def seedTower(self) -> func_adl_servicex_xaodr22.xAOD.jgtower_v1.JGTower_v1:
        "A method"
        ...

    def nTowers(self) -> int:
        "A method"
        ...

    def towerLinks(self) -> func_adl_servicex_xaodr22.vector_elementlink_datavector_xaod_jgtower_v1___.vector_ElementLink_DataVector_xAOD_JGTower_v1___:
        "A method"
        ...

    def getTower(self, idx: int) -> func_adl_servicex_xaodr22.xAOD.jgtower_v1.JGTower_v1:
        "A method"
        ...

    def area(self) -> float:
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
