from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr22

_method_map = {
    'pt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigElectron_v1',
        'method_name': 'pt',
        'return_type': 'double',
    },
    'eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigElectron_v1',
        'method_name': 'eta',
        'return_type': 'double',
    },
    'phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigElectron_v1',
        'method_name': 'phi',
        'return_type': 'double',
    },
    'm': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigElectron_v1',
        'method_name': 'm',
        'return_type': 'double',
    },
    'e': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigElectron_v1',
        'method_name': 'e',
        'return_type': 'double',
    },
    'rapidity': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigElectron_v1',
        'method_name': 'rapidity',
        'return_type': 'double',
    },
    'p4': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigElectron_v1',
        'method_name': 'p4',
        'return_type': 'TLorentzVector',
    },
    'type': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigElectron_v1',
        'method_name': 'type',
        'return_type': 'xAODType::ObjectType',
    },
    'roiWord': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigElectron_v1',
        'method_name': 'roiWord',
        'return_type': 'unsigned int',
    },
    'zvtx': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigElectron_v1',
        'method_name': 'zvtx',
        'return_type': 'float',
    },
    'charge': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigElectron_v1',
        'method_name': 'charge',
        'return_type': 'float',
    },
    'nTRTHits': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigElectron_v1',
        'method_name': 'nTRTHits',
        'return_type': 'int',
    },
    'nTRTHiThresholdHits': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigElectron_v1',
        'method_name': 'nTRTHiThresholdHits',
        'return_type': 'int',
    },
    'rcore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigElectron_v1',
        'method_name': 'rcore',
        'return_type': 'float',
    },
    'eratio': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigElectron_v1',
        'method_name': 'eratio',
        'return_type': 'float',
    },
    'etHad': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigElectron_v1',
        'method_name': 'etHad',
        'return_type': 'float',
    },
    'etHad1': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigElectron_v1',
        'method_name': 'etHad1',
        'return_type': 'float',
    },
    'f0': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigElectron_v1',
        'method_name': 'f0',
        'return_type': 'float',
    },
    'f1': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigElectron_v1',
        'method_name': 'f1',
        'return_type': 'float',
    },
    'f2': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigElectron_v1',
        'method_name': 'f2',
        'return_type': 'float',
    },
    'f3': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigElectron_v1',
        'method_name': 'f3',
        'return_type': 'float',
    },
    'trkEtaAtCalo': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigElectron_v1',
        'method_name': 'trkEtaAtCalo',
        'return_type': 'float',
    },
    'trkPhiAtCalo': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigElectron_v1',
        'method_name': 'trkPhiAtCalo',
        'return_type': 'float',
    },
    'etOverPt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigElectron_v1',
        'method_name': 'etOverPt',
        'return_type': 'float',
    },
    'trkClusDeta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigElectron_v1',
        'method_name': 'trkClusDeta',
        'return_type': 'float',
    },
    'trkClusDphi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigElectron_v1',
        'method_name': 'trkClusDphi',
        'return_type': 'float',
    },
    'caloEta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigElectron_v1',
        'method_name': 'caloEta',
        'return_type': 'float',
    },
    'caloPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigElectron_v1',
        'method_name': 'caloPhi',
        'return_type': 'float',
    },
    'emCluster': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigElectron_v1',
        'method_name': 'emCluster',
        'return_type': 'const xAOD::TrigEMCluster_v1 *',
    },
    'emClusterLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigElectron_v1',
        'method_name': 'emClusterLink',
        'return_type': 'const ElementLink<DataVector<xAOD::TrigEMCluster_v1>>',
    },
    'trackParticle': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigElectron_v1',
        'method_name': 'trackParticle',
        'return_type': 'const xAOD::TrackParticle_v1 *',
    },
    'trackParticleLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigElectron_v1',
        'method_name': 'trackParticleLink',
        'return_type': 'const ElementLink<DataVector<xAOD::TrackParticle_v1>>',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigElectron_v1',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigElectron_v1',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigElectron_v1',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigElectron_v1',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigElectron_v1',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigElectron_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigElectron_v1',
        'method_name': 'trackIndices',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigElectron_v1',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigElectron_v1',
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
            'name': 'xAODTrigEgamma/versions/TrigElectron_v1.h',
            'body_includes': ["xAODTrigEgamma/versions/TrigElectron_v1.h"],
        })


        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODTrigEgamma',
            'link_libraries': ["xAODTrigEgamma"],
        })

        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class TrigElectron_v1:
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

    def roiWord(self) -> int:
        "A method"
        ...

    def zvtx(self) -> float:
        "A method"
        ...

    def charge(self) -> float:
        "A method"
        ...

    def nTRTHits(self) -> int:
        "A method"
        ...

    def nTRTHiThresholdHits(self) -> int:
        "A method"
        ...

    def rcore(self) -> float:
        "A method"
        ...

    def eratio(self) -> float:
        "A method"
        ...

    def etHad(self) -> float:
        "A method"
        ...

    def etHad1(self) -> float:
        "A method"
        ...

    def f0(self) -> float:
        "A method"
        ...

    def f1(self) -> float:
        "A method"
        ...

    def f2(self) -> float:
        "A method"
        ...

    def f3(self) -> float:
        "A method"
        ...

    def trkEtaAtCalo(self) -> float:
        "A method"
        ...

    def trkPhiAtCalo(self) -> float:
        "A method"
        ...

    def etOverPt(self) -> float:
        "A method"
        ...

    def trkClusDeta(self) -> float:
        "A method"
        ...

    def trkClusDphi(self) -> float:
        "A method"
        ...

    def caloEta(self) -> float:
        "A method"
        ...

    def caloPhi(self) -> float:
        "A method"
        ...

    def emCluster(self) -> func_adl_servicex_xaodr22.xAOD.trigemcluster_v1.TrigEMCluster_v1:
        "A method"
        ...

    def emClusterLink(self) -> func_adl_servicex_xaodr22.elementlink_datavector_xaod_trigemcluster_v1__.ElementLink_DataVector_xAOD_TrigEMCluster_v1__:
        "A method"
        ...

    def trackParticle(self) -> func_adl_servicex_xaodr22.xAOD.trackparticle_v1.TrackParticle_v1:
        "A method"
        ...

    def trackParticleLink(self) -> func_adl_servicex_xaodr22.elementlink_datavector_xaod_trackparticle_v1__.ElementLink_DataVector_xAOD_TrackParticle_v1__:
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
