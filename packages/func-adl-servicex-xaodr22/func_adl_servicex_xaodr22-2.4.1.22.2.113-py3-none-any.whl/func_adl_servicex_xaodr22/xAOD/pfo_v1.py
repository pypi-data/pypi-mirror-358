from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr22

_method_map = {
    'pt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::PFO_v1',
        'method_name': 'pt',
        'return_type': 'double',
    },
    'eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::PFO_v1',
        'method_name': 'eta',
        'return_type': 'double',
    },
    'phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::PFO_v1',
        'method_name': 'phi',
        'return_type': 'double',
    },
    'm': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::PFO_v1',
        'method_name': 'm',
        'return_type': 'double',
    },
    'e': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::PFO_v1',
        'method_name': 'e',
        'return_type': 'double',
    },
    'rapidity': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::PFO_v1',
        'method_name': 'rapidity',
        'return_type': 'double',
    },
    'p4': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::PFO_v1',
        'method_name': 'p4',
        'return_type': 'TLorentzVector',
    },
    'type': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::PFO_v1',
        'method_name': 'type',
        'return_type': 'xAODType::ObjectType',
    },
    'p4EM': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::PFO_v1',
        'method_name': 'p4EM',
        'return_type': 'TLorentzVector',
    },
    'ptEM': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::PFO_v1',
        'method_name': 'ptEM',
        'return_type': 'double',
    },
    'etaEM': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::PFO_v1',
        'method_name': 'etaEM',
        'return_type': 'double',
    },
    'phiEM': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::PFO_v1',
        'method_name': 'phiEM',
        'return_type': 'double',
    },
    'mEM': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::PFO_v1',
        'method_name': 'mEM',
        'return_type': 'double',
    },
    'eEM': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::PFO_v1',
        'method_name': 'eEM',
        'return_type': 'double',
    },
    'bdtPi0Score': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::PFO_v1',
        'method_name': 'bdtPi0Score',
        'return_type': 'float',
    },
    'centerMag': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::PFO_v1',
        'method_name': 'centerMag',
        'return_type': 'float',
    },
    'isCharged': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::PFO_v1',
        'method_name': 'isCharged',
        'return_type': 'bool',
    },
    'charge': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::PFO_v1',
        'method_name': 'charge',
        'return_type': 'float',
    },
    'getClusterMoment': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::PFO_v1',
        'method_name': 'getClusterMoment',
        'return_type': 'bool',
    },
    'nCaloCluster': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::PFO_v1',
        'method_name': 'nCaloCluster',
        'return_type': 'unsigned int',
    },
    'cluster': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::PFO_v1',
        'method_name': 'cluster',
        'return_type': 'const xAOD::CaloCluster_v1 *',
    },
    'track': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::PFO_v1',
        'method_name': 'track',
        'return_type': 'const xAOD::TrackParticle_v1 *',
    },
    'vertex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::PFO_v1',
        'method_name': 'vertex',
        'return_type': 'const xAOD::Vertex_v1 *',
    },
    'setVertexLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::PFO_v1',
        'method_name': 'setVertexLink',
        'return_type': 'bool',
    },
    'setTrackLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::PFO_v1',
        'method_name': 'setTrackLink',
        'return_type': 'bool',
    },
    'setClusterLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::PFO_v1',
        'method_name': 'setClusterLink',
        'return_type': 'bool',
    },
    'addClusterLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::PFO_v1',
        'method_name': 'addClusterLink',
        'return_type': 'bool',
    },
    'setAssociatedParticleLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::PFO_v1',
        'method_name': 'setAssociatedParticleLink',
        'return_type': 'bool',
    },
    'addAssociatedParticleLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::PFO_v1',
        'method_name': 'addAssociatedParticleLink',
        'return_type': 'bool',
    },
    'setAssociatedParticleLinks': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::PFO_v1',
        'method_name': 'setAssociatedParticleLinks',
        'return_type': 'bool',
    },
    'GetVertexCorrectedFourVec': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::PFO_v1',
        'method_name': 'GetVertexCorrectedFourVec',
        'return_type': 'TLorentzVector',
    },
    'GetVertexCorrectedEMFourVec': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::PFO_v1',
        'method_name': 'GetVertexCorrectedEMFourVec',
        'return_type': 'TLorentzVector',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::PFO_v1',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::PFO_v1',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::PFO_v1',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::PFO_v1',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::PFO_v1',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::PFO_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::PFO_v1',
        'method_name': 'trackIndices',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::PFO_v1',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::PFO_v1',
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
    'getClusterMoment': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.CaloCluster_v1',
            'name': 'MomentType',
            'values': [
                'FIRST_PHI',
                'FIRST_ETA',
                'SECOND_R',
                'SECOND_LAMBDA',
                'DELTA_PHI',
                'DELTA_THETA',
                'DELTA_ALPHA',
                'CENTER_X',
                'CENTER_Y',
                'CENTER_Z',
                'CENTER_MAG',
                'CENTER_LAMBDA',
                'LATERAL',
                'LONGITUDINAL',
                'ENG_FRAC_EM',
                'ENG_FRAC_MAX',
                'ENG_FRAC_CORE',
                'FIRST_ENG_DENS',
                'SECOND_ENG_DENS',
                'ISOLATION',
                'ENG_BAD_CELLS',
                'N_BAD_CELLS',
                'N_BAD_CELLS_CORR',
                'BAD_CELLS_CORR_E',
                'BADLARQ_FRAC',
                'ENG_POS',
                'SIGNIFICANCE',
                'CELL_SIGNIFICANCE',
                'CELL_SIG_SAMPLING',
                'AVG_LAR_Q',
                'AVG_TILE_Q',
                'ENG_BAD_HV_CELLS',
                'N_BAD_HV_CELLS',
                'PTD',
                'MASS',
                'EM_PROBABILITY',
                'HAD_WEIGHT',
                'OOC_WEIGHT',
                'DM_WEIGHT',
                'TILE_CONFIDENCE_LEVEL',
                'SECOND_TIME',
                'NCELL_SAMPLING',
                'VERTEX_FRACTION',
                'NVERTEX_FRACTION',
                'ETACALOFRAME',
                'PHICALOFRAME',
                'ETA1CALOFRAME',
                'PHI1CALOFRAME',
                'ETA2CALOFRAME',
                'PHI2CALOFRAME',
                'ENG_CALIB_TOT',
                'ENG_CALIB_OUT_L',
                'ENG_CALIB_OUT_M',
                'ENG_CALIB_OUT_T',
                'ENG_CALIB_DEAD_L',
                'ENG_CALIB_DEAD_M',
                'ENG_CALIB_DEAD_T',
                'ENG_CALIB_EMB0',
                'ENG_CALIB_EME0',
                'ENG_CALIB_TILEG3',
                'ENG_CALIB_DEAD_TOT',
                'ENG_CALIB_DEAD_EMB0',
                'ENG_CALIB_DEAD_TILE0',
                'ENG_CALIB_DEAD_TILEG3',
                'ENG_CALIB_DEAD_EME0',
                'ENG_CALIB_DEAD_HEC0',
                'ENG_CALIB_DEAD_FCAL',
                'ENG_CALIB_DEAD_LEAKAGE',
                'ENG_CALIB_DEAD_UNCLASS',
                'ENG_CALIB_FRAC_EM',
                'ENG_CALIB_FRAC_HAD',
                'ENG_CALIB_FRAC_REST',
                'ENERGY_DigiHSTruth',
                'ETA_DigiHSTruth',
                'PHI_DigiHSTruth',
                'TIME_DigiHSTruth',
                'ENERGY_CALIB_DigiHSTruth',
                'ETA_CALIB_DigiHSTruth',
                'PHI_CALIB_DigiHSTruth',
                'TIME_CALIB_DigiHSTruth',
                'FIRST_PHI_DigiHSTruth',
                'FIRST_ETA_DigiHSTruth',
                'SECOND_R_DigiHSTruth',
                'SECOND_LAMBDA_DigiHSTruth',
                'DELTA_PHI_DigiHSTruth',
                'DELTA_THETA_DigiHSTruth',
                'DELTA_ALPHA_DigiHSTruth',
                'CENTER_X_DigiHSTruth',
                'CENTER_Y_DigiHSTruth',
                'CENTER_Z_DigiHSTruth',
                'CENTER_MAG_DigiHSTruth',
                'CENTER_LAMBDA_DigiHSTruth',
                'LATERAL_DigiHSTruth',
                'LONGITUDINAL_DigiHSTruth',
                'ENG_FRAC_EM_DigiHSTruth',
                'ENG_FRAC_MAX_DigiHSTruth',
                'ENG_FRAC_CORE_DigiHSTruth',
                'FIRST_ENG_DENS_DigiHSTruth',
                'SECOND_ENG_DENS_DigiHSTruth',
                'ISOLATION_DigiHSTruth',
                'ENG_BAD_CELLS_DigiHSTruth',
                'N_BAD_CELLS_DigiHSTruth',
                'N_BAD_CELLS_CORR_DigiHSTruth',
                'BAD_CELLS_CORR_E_DigiHSTruth',
                'BADLARQ_FRAC_DigiHSTruth',
                'ENG_POS_DigiHSTruth',
                'SIGNIFICANCE_DigiHSTruth',
                'CELL_SIGNIFICANCE_DigiHSTruth',
                'CELL_SIG_SAMPLING_DigiHSTruth',
                'AVG_LAR_Q_DigiHSTruth',
                'AVG_TILE_Q_DigiHSTruth',
                'ENG_BAD_HV_CELLS_DigiHSTruth',
                'N_BAD_HV_CELLS_DigiHSTruth',
                'EM_PROBABILITY_DigiHSTruth',
                'HAD_WEIGHT_DigiHSTruth',
                'OOC_WEIGHT_DigiHSTruth',
                'DM_WEIGHT_DigiHSTruth',
            ],
        },
    ],
    'setAssociatedParticleLink': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.PFODetails',
            'name': 'PFOParticleType',
            'values': [
                'CaloCluster',
                'Track',
                'TauShot',
                'HadronicCalo',
                'ChargedPFO',
                'NeutralPFO',
                'TauTrack',
            ],
        },
    ],
    'addAssociatedParticleLink': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.PFODetails',
            'name': 'PFOParticleType',
            'values': [
                'CaloCluster',
                'Track',
                'TauShot',
                'HadronicCalo',
                'ChargedPFO',
                'NeutralPFO',
                'TauTrack',
            ],
        },
    ],
    'setAssociatedParticleLinks': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.PFODetails',
            'name': 'PFOParticleType',
            'values': [
                'CaloCluster',
                'Track',
                'TauShot',
                'HadronicCalo',
                'ChargedPFO',
                'NeutralPFO',
                'TauTrack',
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
            'name': 'xAODPFlow/versions/PFO_v1.h',
            'body_includes': ["xAODPFlow/versions/PFO_v1.h"],
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
class PFO_v1:
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

    def p4EM(self) -> func_adl_servicex_xaodr22.tlorentzvector.TLorentzVector:
        "A method"
        ...

    def ptEM(self) -> float:
        "A method"
        ...

    def etaEM(self) -> float:
        "A method"
        ...

    def phiEM(self) -> float:
        "A method"
        ...

    def mEM(self) -> float:
        "A method"
        ...

    def eEM(self) -> float:
        "A method"
        ...

    def bdtPi0Score(self) -> float:
        "A method"
        ...

    def centerMag(self) -> float:
        "A method"
        ...

    def isCharged(self) -> bool:
        "A method"
        ...

    def charge(self) -> float:
        "A method"
        ...

    def getClusterMoment(self, theMoment: float, momentType: func_adl_servicex_xaodr22.xAOD.calocluster_v1.CaloCluster_v1.MomentType) -> bool:
        "A method"
        ...

    def nCaloCluster(self) -> int:
        "A method"
        ...

    def cluster(self, index: int) -> func_adl_servicex_xaodr22.xAOD.calocluster_v1.CaloCluster_v1:
        "A method"
        ...

    def track(self, index: int) -> func_adl_servicex_xaodr22.xAOD.trackparticle_v1.TrackParticle_v1:
        "A method"
        ...

    def vertex(self) -> func_adl_servicex_xaodr22.xAOD.vertex_v1.Vertex_v1:
        "A method"
        ...

    def setVertexLink(self, theVertexLink: func_adl_servicex_xaodr22.elementlink_datavector_xaod_vertex_v1__.ElementLink_DataVector_xAOD_Vertex_v1__) -> bool:
        "A method"
        ...

    def setTrackLink(self, theTrack: func_adl_servicex_xaodr22.elementlink_datavector_xaod_trackparticle_v1__.ElementLink_DataVector_xAOD_TrackParticle_v1__) -> bool:
        "A method"
        ...

    def setClusterLink(self, theCluster: func_adl_servicex_xaodr22.elementlink_datavector_xaod_calocluster_v1__.ElementLink_DataVector_xAOD_CaloCluster_v1__) -> bool:
        "A method"
        ...

    def addClusterLink(self, theCluster: func_adl_servicex_xaodr22.elementlink_datavector_xaod_calocluster_v1__.ElementLink_DataVector_xAOD_CaloCluster_v1__) -> bool:
        "A method"
        ...

    def setAssociatedParticleLink(self, ParticleType: func_adl_servicex_xaodr22.xAOD.pfodetails.PFODetails.PFOParticleType, theParticle: func_adl_servicex_xaodr22.elementlink_datavector_xaod_iparticle__.ElementLink_DataVector_xAOD_IParticle__) -> bool:
        "A method"
        ...

    def addAssociatedParticleLink(self, ParticleType: func_adl_servicex_xaodr22.xAOD.pfodetails.PFODetails.PFOParticleType, theParticle: func_adl_servicex_xaodr22.elementlink_datavector_xaod_iparticle__.ElementLink_DataVector_xAOD_IParticle__) -> bool:
        "A method"
        ...

    def setAssociatedParticleLinks(self, ParticleType: func_adl_servicex_xaodr22.xAOD.pfodetails.PFODetails.PFOParticleType, theParticles: func_adl_servicex_xaodr22.vector_elementlink_datavector_xaod_iparticle___.vector_ElementLink_DataVector_xAOD_IParticle___) -> bool:
        "A method"
        ...

    def GetVertexCorrectedFourVec(self, vertexToCorrectTo: func_adl_servicex_xaodr22.xAOD.vertex_v1.Vertex_v1) -> func_adl_servicex_xaodr22.tlorentzvector.TLorentzVector:
        "A method"
        ...

    def GetVertexCorrectedEMFourVec(self, vertexToCorrectTo: func_adl_servicex_xaodr22.xAOD.vertex_v1.Vertex_v1) -> func_adl_servicex_xaodr22.tlorentzvector.TLorentzVector:
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
