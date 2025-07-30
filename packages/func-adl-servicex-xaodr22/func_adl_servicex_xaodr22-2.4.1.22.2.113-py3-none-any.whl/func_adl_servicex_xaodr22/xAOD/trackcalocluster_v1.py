from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr22

_method_map = {
    'pt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackCaloCluster_v1',
        'method_name': 'pt',
        'return_type': 'double',
    },
    'eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackCaloCluster_v1',
        'method_name': 'eta',
        'return_type': 'double',
    },
    'phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackCaloCluster_v1',
        'method_name': 'phi',
        'return_type': 'double',
    },
    'm': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackCaloCluster_v1',
        'method_name': 'm',
        'return_type': 'double',
    },
    'e': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackCaloCluster_v1',
        'method_name': 'e',
        'return_type': 'double',
    },
    'rapidity': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackCaloCluster_v1',
        'method_name': 'rapidity',
        'return_type': 'double',
    },
    'taste': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackCaloCluster_v1',
        'method_name': 'taste',
        'return_type': 'int',
    },
    'p4': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackCaloCluster_v1',
        'method_name': 'p4',
        'return_type': 'TLorentzVector',
    },
    'type': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackCaloCluster_v1',
        'method_name': 'type',
        'return_type': 'xAODType::ObjectType',
    },
    'trackParticleLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackCaloCluster_v1',
        'method_name': 'trackParticleLink',
        'return_type': 'const ElementLink<DataVector<xAOD::TrackParticle_v1>>',
    },
    'trackParticle': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackCaloCluster_v1',
        'method_name': 'trackParticle',
        'return_type': 'const xAOD::TrackParticle_v1 *',
    },
    'caloClusterLinks': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackCaloCluster_v1',
        'method_name': 'caloClusterLinks',
        'return_type_element': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'return_type_collection': 'const vector<ElementLink<DataVector<xAOD::CaloCluster_v1>>>',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackCaloCluster_v1',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackCaloCluster_v1',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackCaloCluster_v1',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackCaloCluster_v1',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackCaloCluster_v1',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackCaloCluster_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackCaloCluster_v1',
        'method_name': 'trackIndices',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackCaloCluster_v1',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackCaloCluster_v1',
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
    'Taste':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.TrackCaloCluster_v1',
            'name': 'Taste',
            'values': [
                'Charged',
                'Neutral',
                'Combined',
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
            'name': 'xAODPFlow/versions/TrackCaloCluster_v1.h',
            'body_includes': ["xAODPFlow/versions/TrackCaloCluster_v1.h"],
        })


        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODPFlow',
            'link_libraries': ["xAODPFlow"],
        })

        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class TrackCaloCluster_v1:
    "A class"

    class Taste(Enum):
        Charged = 0
        Neutral = 1
        Combined = 2


    def pt(self) -> float:
        "A method"
        ...

    def eta(self) -> float:
        "A method"
        ...

    def phi(self) -> float:
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

    def taste(self) -> int:
        "A method"
        ...

    def p4(self) -> func_adl_servicex_xaodr22.tlorentzvector.TLorentzVector:
        "A method"
        ...

    def type(self) -> func_adl_servicex_xaodr22.xaodtype.xAODType.ObjectType:
        "A method"
        ...

    def trackParticleLink(self) -> func_adl_servicex_xaodr22.elementlink_datavector_xaod_trackparticle_v1__.ElementLink_DataVector_xAOD_TrackParticle_v1__:
        "A method"
        ...

    def trackParticle(self) -> func_adl_servicex_xaodr22.xAOD.trackparticle_v1.TrackParticle_v1:
        "A method"
        ...

    def caloClusterLinks(self) -> func_adl_servicex_xaodr22.vector_elementlink_datavector_xaod_calocluster_v1___.vector_ElementLink_DataVector_xAOD_CaloCluster_v1___:
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
