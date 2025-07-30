from __future__ import annotations
from typing import Any, Dict, Iterable, List, Tuple, TypeVar, Union, Optional
from func_adl import ObjectStream, func_adl_callback
import ast
import copy
import func_adl_servicex_xaodr22

# The map for collection definitions in ATLAS
_collection_map = {
    'TrigMissingETs': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'TrigMissingETs',
        'include_files': ['xAODTrigMissingET/TrigMissingETContainer.h',],
        'container_type': 'DataVector<xAOD::TrigMissingET_v1>',
        'element_type': 'xAOD::TrigMissingET_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigMissingET'],
    },
    'TrackParticleClusterAssociations': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'TrackParticleClusterAssociations',
        'include_files': ['xAODAssociations/TrackParticleClusterAssociationContainer.h',],
        'container_type': 'DataVector<xAOD::TrackParticleClusterAssociation_v1>',
        'element_type': 'xAOD::TrackParticleClusterAssociation_v1',
        'contains_collection': True,
        'link_libraries': ['xAODAssociations'],
    },
    'KLFitterResults': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'KLFitterResults',
        'include_files': ['TopEvent/KLFitterResultContainer.h',],
        'container_type': 'DataVector<xAOD::KLFitterResult>',
        'element_type': 'xAOD::KLFitterResult',
        'contains_collection': True,
        'link_libraries': ['TopEvent'],
    },
    'SystematicEvents': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'SystematicEvents',
        'include_files': ['TopEvent/SystematicEventContainer.h',],
        'container_type': 'DataVector<xAOD::SystematicEvent>',
        'element_type': 'xAOD::SystematicEvent',
        'contains_collection': True,
        'link_libraries': ['TopEvent'],
    },
    'PseudoTopResults': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'PseudoTopResults',
        'include_files': ['TopEvent/PseudoTopResultContainer.h',],
        'container_type': 'DataVector<xAOD::PseudoTopResult>',
        'element_type': 'xAOD::PseudoTopResult',
        'contains_collection': True,
        'link_libraries': ['TopEvent'],
    },
    'Vertices': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'Vertices',
        'include_files': ['xAODTracking/VertexContainer.h',],
        'container_type': 'DataVector<xAOD::Vertex_v1>',
        'element_type': 'xAOD::Vertex_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTracking'],
    },
    'SCTRawHitValidations': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'SCTRawHitValidations',
        'include_files': ['xAODTracking/SCTRawHitValidationContainer.h',],
        'container_type': 'DataVector<xAOD::SCTRawHitValidation_v1>',
        'element_type': 'xAOD::SCTRawHitValidation_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTracking'],
    },
    'TrackMeasurementValidations': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'TrackMeasurementValidations',
        'include_files': ['xAODTracking/TrackMeasurementValidationContainer.h',],
        'container_type': 'DataVector<xAOD::TrackMeasurementValidation_v1>',
        'element_type': 'xAOD::TrackMeasurementValidation_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTracking'],
    },
    'TrackStates': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'TrackStates',
        'include_files': ['xAODTracking/TrackStateContainer.h',],
        'container_type': 'DataVector<xAOD::TrackState_v1>',
        'element_type': 'xAOD::TrackState_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTracking'],
    },
    'TrackJacobians': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'TrackJacobians',
        'include_files': ['xAODTracking/TrackJacobianContainer.h',],
        'container_type': 'DataVector<xAOD::TrackJacobian_v1>',
        'element_type': 'xAOD::TrackJacobian_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTracking'],
    },
    'TrackStateValidations': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'TrackStateValidations',
        'include_files': ['xAODTracking/TrackStateValidationContainer.h',],
        'container_type': 'DataVector<xAOD::TrackStateValidation_v1>',
        'element_type': 'xAOD::TrackStateValidation_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTracking'],
    },
    'TrackParticles': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'TrackParticles',
        'include_files': ['xAODTracking/TrackParticleContainer.h',],
        'container_type': 'DataVector<xAOD::TrackParticle_v1>',
        'element_type': 'xAOD::TrackParticle_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTracking'],
    },
    'NeutralParticles': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'NeutralParticles',
        'include_files': ['xAODTracking/NeutralParticleContainer.h',],
        'container_type': 'DataVector<xAOD::NeutralParticle_v1>',
        'element_type': 'xAOD::NeutralParticle_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTracking'],
    },
    'TrackParameterss': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'TrackParameterss',
        'include_files': ['xAODTracking/TrackParametersContainer.h',],
        'container_type': 'DataVector<xAOD::TrackParameters_v1>',
        'element_type': 'xAOD::TrackParameters_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTracking'],
    },
    'TrackMeasurements': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'TrackMeasurements',
        'include_files': ['xAODTracking/TrackMeasurementContainer.h',],
        'container_type': 'DataVector<xAOD::TrackMeasurement_v1>',
        'element_type': 'xAOD::TrackMeasurement_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTracking'],
    },
    'UncalibratedMeasurements': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'UncalibratedMeasurements',
        'include_files': ['xAODMeasurementBase/UncalibratedMeasurementContainer.h',],
        'container_type': 'DataVector<xAOD::UncalibratedMeasurement_v1>',
        'element_type': 'xAOD::UncalibratedMeasurement_v1',
        'contains_collection': True,
        'link_libraries': ['xAODMeasurementBase'],
    },
    'TrackCaloClusters': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'TrackCaloClusters',
        'include_files': ['xAODPFlow/TrackCaloClusterContainer.h',],
        'container_type': 'DataVector<xAOD::TrackCaloCluster_v1>',
        'element_type': 'xAOD::TrackCaloCluster_v1',
        'contains_collection': True,
        'link_libraries': ['xAODPFlow'],
    },
    'PFOs': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'PFOs',
        'include_files': ['xAODPFlow/PFOContainer.h',],
        'container_type': 'DataVector<xAOD::PFO_v1>',
        'element_type': 'xAOD::PFO_v1',
        'contains_collection': True,
        'link_libraries': ['xAODPFlow'],
    },
    'CaloClusters': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'CaloClusters',
        'include_files': ['xAODCaloEvent/CaloClusterContainer.h',],
        'container_type': 'DataVector<xAOD::CaloCluster_v1>',
        'element_type': 'xAOD::CaloCluster_v1',
        'contains_collection': True,
        'link_libraries': ['xAODCaloEvent'],
    },
    'CaloTowers': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'CaloTowers',
        'include_files': ['xAODCaloEvent/CaloTowerContainer.h',],
        'container_type': 'xAOD::CaloTowerContainer_v1',
        'element_type': 'xAOD::CaloTower_v1',
        'contains_collection': True,
        'link_libraries': ['xAODCaloEvent'],
    },
    'AFPSiHits': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'AFPSiHits',
        'include_files': ['xAODForward/AFPSiHitContainer.h',],
        'container_type': 'DataVector<xAOD::AFPSiHit_v2>',
        'element_type': 'xAOD::AFPSiHit_v2',
        'contains_collection': True,
        'link_libraries': ['xAODForward'],
    },
    'ForwardEventInfos': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'ForwardEventInfos',
        'include_files': ['xAODForward/ForwardEventInfoContainer.h',],
        'container_type': 'DataVector<xAOD::ForwardEventInfo_v1>',
        'element_type': 'xAOD::ForwardEventInfo_v1',
        'contains_collection': True,
        'link_libraries': ['xAODForward'],
    },
    'AFPToFTracks': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'AFPToFTracks',
        'include_files': ['xAODForward/AFPToFTrackContainer.h',],
        'container_type': 'DataVector<xAOD::AFPToFTrack_v1>',
        'element_type': 'xAOD::AFPToFTrack_v1',
        'contains_collection': True,
        'link_libraries': ['xAODForward'],
    },
    'AFPVertexs': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'AFPVertexs',
        'include_files': ['xAODForward/AFPVertexContainer.h',],
        'container_type': 'DataVector<xAOD::AFPVertex_v1>',
        'element_type': 'xAOD::AFPVertex_v1',
        'contains_collection': True,
        'link_libraries': ['xAODForward'],
    },
    'ALFADatas': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'ALFADatas',
        'include_files': ['xAODForward/ALFADataContainer.h',],
        'container_type': 'DataVector<xAOD::ALFAData_v1>',
        'element_type': 'xAOD::ALFAData_v1',
        'contains_collection': True,
        'link_libraries': ['xAODForward'],
    },
    'AFPDatas': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'AFPDatas',
        'include_files': ['xAODForward/AFPDataContainer.h',],
        'container_type': 'DataVector<xAOD::AFPData_v1>',
        'element_type': 'xAOD::AFPData_v1',
        'contains_collection': True,
        'link_libraries': ['xAODForward'],
    },
    'ZdcModules': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'ZdcModules',
        'include_files': ['xAODForward/ZdcModuleContainer.h',],
        'container_type': 'DataVector<xAOD::ZdcModule_v1>',
        'element_type': 'xAOD::ZdcModule_v1',
        'contains_collection': True,
        'link_libraries': ['xAODForward'],
    },
    'AFPProtons': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'AFPProtons',
        'include_files': ['xAODForward/AFPProtonContainer.h',],
        'container_type': 'DataVector<xAOD::AFPProton_v1>',
        'element_type': 'xAOD::AFPProton_v1',
        'contains_collection': True,
        'link_libraries': ['xAODForward'],
    },
    'AFPSiHitsClusters': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'AFPSiHitsClusters',
        'include_files': ['xAODForward/AFPSiHitsClusterContainer.h',],
        'container_type': 'DataVector<xAOD::AFPSiHitsCluster_v1>',
        'element_type': 'xAOD::AFPSiHitsCluster_v1',
        'contains_collection': True,
        'link_libraries': ['xAODForward'],
    },
    'AFPToFHits': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'AFPToFHits',
        'include_files': ['xAODForward/AFPToFHitContainer.h',],
        'container_type': 'DataVector<xAOD::AFPToFHit_v1>',
        'element_type': 'xAOD::AFPToFHit_v1',
        'contains_collection': True,
        'link_libraries': ['xAODForward'],
    },
    'MBTSModules': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'MBTSModules',
        'include_files': ['xAODForward/MBTSModuleContainer.h',],
        'container_type': 'DataVector<xAOD::MBTSModule_v1>',
        'element_type': 'xAOD::MBTSModule_v1',
        'contains_collection': True,
        'link_libraries': ['xAODForward'],
    },
    'AFPTracks': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'AFPTracks',
        'include_files': ['xAODForward/AFPTrackContainer.h',],
        'container_type': 'DataVector<xAOD::AFPTrack_v2>',
        'element_type': 'xAOD::AFPTrack_v2',
        'contains_collection': True,
        'link_libraries': ['xAODForward'],
    },
    'CMMCPHitss': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'CMMCPHitss',
        'include_files': ['xAODTrigL1Calo/CMMCPHitsContainer.h',],
        'container_type': 'DataVector<xAOD::CMMCPHits_v1>',
        'element_type': 'xAOD::CMMCPHits_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigL1Calo'],
    },
    'JEMHitss': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'JEMHitss',
        'include_files': ['xAODTrigL1Calo/JEMHitsContainer.h',],
        'container_type': 'DataVector<xAOD::JEMHits_v1>',
        'element_type': 'xAOD::JEMHits_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigL1Calo'],
    },
    'CMXCPHitss': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'CMXCPHitss',
        'include_files': ['xAODTrigL1Calo/CMXCPHitsContainer.h',],
        'container_type': 'DataVector<xAOD::CMXCPHits_v1>',
        'element_type': 'xAOD::CMXCPHits_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigL1Calo'],
    },
    'CMXEtSumss': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'CMXEtSumss',
        'include_files': ['xAODTrigL1Calo/CMXEtSumsContainer.h',],
        'container_type': 'DataVector<xAOD::CMXEtSums_v1>',
        'element_type': 'xAOD::CMXEtSums_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigL1Calo'],
    },
    'CPMRoIs': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'CPMRoIs',
        'include_files': ['xAODTrigL1Calo/CPMRoIContainer.h',],
        'container_type': 'DataVector<xAOD::CPMRoI_v1>',
        'element_type': 'xAOD::CPMRoI_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigL1Calo'],
    },
    'CMXRoIs': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'CMXRoIs',
        'include_files': ['xAODTrigL1Calo/CMXRoIContainer.h',],
        'container_type': 'DataVector<xAOD::CMXRoI_v1>',
        'element_type': 'xAOD::CMXRoI_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigL1Calo'],
    },
    'jFexTowers': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'jFexTowers',
        'include_files': ['xAODTrigL1Calo/jFexTowerContainer.h',],
        'container_type': 'DataVector<xAOD::jFexTower_v1>',
        'element_type': 'xAOD::jFexTower_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigL1Calo'],
    },
    'TriggerTowers': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'TriggerTowers',
        'include_files': ['xAODTrigL1Calo/TriggerTowerContainer.h',],
        'container_type': 'DataVector<xAOD::TriggerTower_v2>',
        'element_type': 'xAOD::TriggerTower_v2',
        'contains_collection': True,
        'link_libraries': ['xAODTrigL1Calo'],
    },
    'JEMTobRoIs': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'JEMTobRoIs',
        'include_files': ['xAODTrigL1Calo/JEMTobRoIContainer.h',],
        'container_type': 'DataVector<xAOD::JEMTobRoI_v1>',
        'element_type': 'xAOD::JEMTobRoI_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigL1Calo'],
    },
    'CPMTowers': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'CPMTowers',
        'include_files': ['xAODTrigL1Calo/CPMTowerContainer.h',],
        'container_type': 'DataVector<xAOD::CPMTower_v2>',
        'element_type': 'xAOD::CPMTower_v2',
        'contains_collection': True,
        'link_libraries': ['xAODTrigL1Calo'],
    },
    'JEMRoIs': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'JEMRoIs',
        'include_files': ['xAODTrigL1Calo/JEMRoIContainer.h',],
        'container_type': 'DataVector<xAOD::JEMRoI_v1>',
        'element_type': 'xAOD::JEMRoI_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigL1Calo'],
    },
    'CPMHitss': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'CPMHitss',
        'include_files': ['xAODTrigL1Calo/CPMHitsContainer.h',],
        'container_type': 'DataVector<xAOD::CPMHits_v1>',
        'element_type': 'xAOD::CPMHits_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigL1Calo'],
    },
    'JEMEtSumss': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'JEMEtSumss',
        'include_files': ['xAODTrigL1Calo/JEMEtSumsContainer.h',],
        'container_type': 'DataVector<xAOD::JEMEtSums_v2>',
        'element_type': 'xAOD::JEMEtSums_v2',
        'contains_collection': True,
        'link_libraries': ['xAODTrigL1Calo'],
    },
    'CPMTobRoIs': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'CPMTobRoIs',
        'include_files': ['xAODTrigL1Calo/CPMTobRoIContainer.h',],
        'container_type': 'DataVector<xAOD::CPMTobRoI_v1>',
        'element_type': 'xAOD::CPMTobRoI_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigL1Calo'],
    },
    'CMXJetTobs': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'CMXJetTobs',
        'include_files': ['xAODTrigL1Calo/CMXJetTobContainer.h',],
        'container_type': 'DataVector<xAOD::CMXJetTob_v1>',
        'element_type': 'xAOD::CMXJetTob_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigL1Calo'],
    },
    'CMMEtSumss': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'CMMEtSumss',
        'include_files': ['xAODTrigL1Calo/CMMEtSumsContainer.h',],
        'container_type': 'DataVector<xAOD::CMMEtSums_v1>',
        'element_type': 'xAOD::CMMEtSums_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigL1Calo'],
    },
    'CMXJetHitss': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'CMXJetHitss',
        'include_files': ['xAODTrigL1Calo/CMXJetHitsContainer.h',],
        'container_type': 'DataVector<xAOD::CMXJetHits_v1>',
        'element_type': 'xAOD::CMXJetHits_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigL1Calo'],
    },
    'CMMJetHitss': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'CMMJetHitss',
        'include_files': ['xAODTrigL1Calo/CMMJetHitsContainer.h',],
        'container_type': 'DataVector<xAOD::CMMJetHits_v1>',
        'element_type': 'xAOD::CMMJetHits_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigL1Calo'],
    },
    'eFexTowers': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'eFexTowers',
        'include_files': ['xAODTrigL1Calo/eFexTowerContainer.h',],
        'container_type': 'DataVector<xAOD::eFexTower_v1>',
        'element_type': 'xAOD::eFexTower_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigL1Calo'],
    },
    'gFexTowers': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'gFexTowers',
        'include_files': ['xAODTrigL1Calo/gFexTowerContainer.h',],
        'container_type': 'DataVector<xAOD::gFexTower_v1>',
        'element_type': 'xAOD::gFexTower_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigL1Calo'],
    },
    'JetElements': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'JetElements',
        'include_files': ['xAODTrigL1Calo/JetElementContainer.h',],
        'container_type': 'DataVector<xAOD::JetElement_v2>',
        'element_type': 'xAOD::JetElement_v2',
        'contains_collection': True,
        'link_libraries': ['xAODTrigL1Calo'],
    },
    'L1TopoRawDatas': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'L1TopoRawDatas',
        'include_files': ['xAODTrigL1Calo/L1TopoRawDataContainer.h',],
        'container_type': 'DataVector<xAOD::L1TopoRawData_v1>',
        'element_type': 'xAOD::L1TopoRawData_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigL1Calo'],
    },
    'CMXCPTobs': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'CMXCPTobs',
        'include_files': ['xAODTrigL1Calo/CMXCPTobContainer.h',],
        'container_type': 'DataVector<xAOD::CMXCPTob_v1>',
        'element_type': 'xAOD::CMXCPTob_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigL1Calo'],
    },
    'RODHeaders': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'RODHeaders',
        'include_files': ['xAODTrigL1Calo/RODHeaderContainer.h',],
        'container_type': 'DataVector<xAOD::RODHeader_v2>',
        'element_type': 'xAOD::RODHeader_v2',
        'contains_collection': True,
        'link_libraries': ['xAODTrigL1Calo'],
    },
    'jFexMETRoIs': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'jFexMETRoIs',
        'include_files': ['xAODTrigger/jFexMETRoIContainer.h',],
        'container_type': 'DataVector<xAOD::jFexMETRoI_v1>',
        'element_type': 'xAOD::jFexMETRoI_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigger'],
    },
    'TrigPassBitss': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'TrigPassBitss',
        'include_files': ['xAODTrigger/TrigPassBitsContainer.h',],
        'container_type': 'DataVector<xAOD::TrigPassBits_v1>',
        'element_type': 'xAOD::TrigPassBits_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigger'],
    },
    'EmTauRoIs': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'EmTauRoIs',
        'include_files': ['xAODTrigger/EmTauRoIContainer.h',],
        'container_type': 'DataVector<xAOD::EmTauRoI_v2>',
        'element_type': 'xAOD::EmTauRoI_v2',
        'contains_collection': True,
        'link_libraries': ['xAODTrigger'],
    },
    'jFexSumETRoIs': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'jFexSumETRoIs',
        'include_files': ['xAODTrigger/jFexSumETRoIContainer.h',],
        'container_type': 'DataVector<xAOD::jFexSumETRoI_v1>',
        'element_type': 'xAOD::jFexSumETRoI_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigger'],
    },
    'jFexSRJetRoIs': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'jFexSRJetRoIs',
        'include_files': ['xAODTrigger/jFexSRJetRoIContainer.h',],
        'container_type': 'DataVector<xAOD::jFexSRJetRoI_v1>',
        'element_type': 'xAOD::jFexSRJetRoI_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigger'],
    },
    'TriggerMenus': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'TriggerMenus',
        'include_files': ['xAODTrigger/TriggerMenuContainer.h',],
        'container_type': 'DataVector<xAOD::TriggerMenu_v1>',
        'element_type': 'xAOD::TriggerMenu_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigger'],
    },
    'gFexJetRoIs': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'gFexJetRoIs',
        'include_files': ['xAODTrigger/gFexJetRoIContainer.h',],
        'container_type': 'DataVector<xAOD::gFexJetRoI_v1>',
        'element_type': 'xAOD::gFexJetRoI_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigger'],
    },
    'jFexLRJetRoIs': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'jFexLRJetRoIs',
        'include_files': ['xAODTrigger/jFexLRJetRoIContainer.h',],
        'container_type': 'DataVector<xAOD::jFexLRJetRoI_v1>',
        'element_type': 'xAOD::jFexLRJetRoI_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigger'],
    },
    'MuonRoIs': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'MuonRoIs',
        'include_files': ['xAODTrigger/MuonRoIContainer.h',],
        'container_type': 'DataVector<xAOD::MuonRoI_v1>',
        'element_type': 'xAOD::MuonRoI_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigger'],
    },
    'eFexEMRoIs': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'eFexEMRoIs',
        'include_files': ['xAODTrigger/eFexEMRoIContainer.h',],
        'container_type': 'DataVector<xAOD::eFexEMRoI_v1>',
        'element_type': 'xAOD::eFexEMRoI_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigger'],
    },
    'JetRoIs': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'JetRoIs',
        'include_files': ['xAODTrigger/JetRoIContainer.h',],
        'container_type': 'DataVector<xAOD::JetRoI_v2>',
        'element_type': 'xAOD::JetRoI_v2',
        'contains_collection': True,
        'link_libraries': ['xAODTrigger'],
    },
    'jFexTauRoIs': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'jFexTauRoIs',
        'include_files': ['xAODTrigger/jFexTauRoIContainer.h',],
        'container_type': 'DataVector<xAOD::jFexTauRoI_v1>',
        'element_type': 'xAOD::jFexTauRoI_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigger'],
    },
    'BunchConfs': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'BunchConfs',
        'include_files': ['xAODTrigger/BunchConfContainer.h',],
        'container_type': 'DataVector<xAOD::BunchConf_v1>',
        'element_type': 'xAOD::BunchConf_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigger'],
    },
    'TriggerMenuJsons': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'TriggerMenuJsons',
        'include_files': ['xAODTrigger/TriggerMenuJsonContainer.h',],
        'container_type': 'DataVector<xAOD::TriggerMenuJson_v1>',
        'element_type': 'xAOD::TriggerMenuJson_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigger'],
    },
    'gFexGlobalRoIs': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'gFexGlobalRoIs',
        'include_files': ['xAODTrigger/gFexGlobalRoIContainer.h',],
        'container_type': 'DataVector<xAOD::gFexGlobalRoI_v1>',
        'element_type': 'xAOD::gFexGlobalRoI_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigger'],
    },
    'TrigComposites': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'TrigComposites',
        'include_files': ['xAODTrigger/TrigCompositeContainer.h',],
        'container_type': 'DataVector<xAOD::TrigComposite_v1>',
        'element_type': 'xAOD::TrigComposite_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigger'],
    },
    'jFexFwdElRoIs': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'jFexFwdElRoIs',
        'include_files': ['xAODTrigger/jFexFwdElRoIContainer.h',],
        'container_type': 'DataVector<xAOD::jFexFwdElRoI_v1>',
        'element_type': 'xAOD::jFexFwdElRoI_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigger'],
    },
    'L1TopoSimResultss': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'L1TopoSimResultss',
        'include_files': ['xAODTrigger/L1TopoSimResultsContainer.h',],
        'container_type': 'DataVector<xAOD::L1TopoSimResults_v1>',
        'element_type': 'xAOD::L1TopoSimResults_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigger'],
    },
    'eFexTauRoIs': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'eFexTauRoIs',
        'include_files': ['xAODTrigger/eFexTauRoIContainer.h',],
        'container_type': 'DataVector<xAOD::eFexTauRoI_v1>',
        'element_type': 'xAOD::eFexTauRoI_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigger'],
    },
    'IParticles': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'IParticles',
        'include_files': ['xAODBase/IParticleContainer.h',],
        'container_type': 'DataVector<xAOD::IParticle>',
        'element_type': 'xAOD::IParticle',
        'contains_collection': True,
        'link_libraries': ['xAODBase'],
    },
    'TrigEMClusters': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'TrigEMClusters',
        'include_files': ['xAODTrigCalo/TrigEMClusterContainer.h',],
        'container_type': 'DataVector<xAOD::TrigEMCluster_v1>',
        'element_type': 'xAOD::TrigEMCluster_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigCalo'],
    },
    'TrigCaloClusters': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'TrigCaloClusters',
        'include_files': ['xAODTrigCalo/TrigCaloClusterContainer.h',],
        'container_type': 'DataVector<xAOD::TrigCaloCluster_v1>',
        'element_type': 'xAOD::TrigCaloCluster_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigCalo'],
    },
    'Muons': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'Muons',
        'include_files': ['xAODMuon/MuonContainer.h',],
        'container_type': 'DataVector<xAOD::Muon_v1>',
        'element_type': 'xAOD::Muon_v1',
        'contains_collection': True,
        'link_libraries': ['xAODMuon'],
    },
    'MuonSegments': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'MuonSegments',
        'include_files': ['xAODMuon/MuonSegmentContainer.h',],
        'container_type': 'DataVector<xAOD::MuonSegment_v1>',
        'element_type': 'xAOD::MuonSegment_v1',
        'contains_collection': True,
        'link_libraries': ['xAODMuon'],
    },
    'SlowMuons': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'SlowMuons',
        'include_files': ['xAODMuon/SlowMuonContainer.h',],
        'container_type': 'DataVector<xAOD::SlowMuon_v1>',
        'element_type': 'xAOD::SlowMuon_v1',
        'contains_collection': True,
        'link_libraries': ['xAODMuon'],
    },
    'CompositeParticles': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'CompositeParticles',
        'include_files': ['xAODParticleEvent/CompositeParticleContainer.h',],
        'container_type': 'DataVector<xAOD::CompositeParticle_v1>',
        'element_type': 'xAOD::CompositeParticle_v1',
        'contains_collection': True,
        'link_libraries': ['xAODParticleEvent'],
    },
    'Particles': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'Particles',
        'include_files': ['xAODParticleEvent/ParticleContainer.h',],
        'container_type': 'DataVector<xAOD::Particle_v1>',
        'element_type': 'xAOD::Particle_v1',
        'contains_collection': True,
        'link_libraries': ['xAODParticleEvent'],
    },
    'HIEventShapes': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'HIEventShapes',
        'include_files': ['xAODHIEvent/HIEventShapeContainer.h',],
        'container_type': 'DataVector<xAOD::HIEventShape_v2>',
        'element_type': 'xAOD::HIEventShape_v2',
        'contains_collection': True,
        'link_libraries': ['xAODHIEvent'],
    },
    'TrigPhotons': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'TrigPhotons',
        'include_files': ['xAODTrigEgamma/TrigPhotonContainer.h',],
        'container_type': 'DataVector<xAOD::TrigPhoton_v1>',
        'element_type': 'xAOD::TrigPhoton_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigEgamma'],
    },
    'TrigElectrons': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'TrigElectrons',
        'include_files': ['xAODTrigEgamma/TrigElectronContainer.h',],
        'container_type': 'DataVector<xAOD::TrigElectron_v1>',
        'element_type': 'xAOD::TrigElectron_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigEgamma'],
    },
    'TauTracks': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'TauTracks',
        'include_files': ['xAODTau/TauTrackContainer.h',],
        'container_type': 'DataVector<xAOD::TauTrack_v1>',
        'element_type': 'xAOD::TauTrack_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTau'],
    },
    'TauJets': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'TauJets',
        'include_files': ['xAODTau/TauJetContainer.h',],
        'container_type': 'DataVector<xAOD::TauJet_v3>',
        'element_type': 'xAOD::TauJet_v3',
        'contains_collection': True,
        'link_libraries': ['xAODTau'],
    },
    'DiTauJets': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'DiTauJets',
        'include_files': ['xAODTau/DiTauJetContainer.h',],
        'container_type': 'DataVector<xAOD::DiTauJet_v1>',
        'element_type': 'xAOD::DiTauJet_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTau'],
    },
    'CutBookkeepers': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'CutBookkeepers',
        'include_files': ['xAODCutFlow/CutBookkeeperContainer.h',],
        'container_type': 'xAOD::CutBookkeeperContainer_v1',
        'element_type': 'xAOD::CutBookkeeper_v1',
        'contains_collection': True,
        'link_libraries': ['xAODCutFlow'],
    },
    'Jets': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'Jets',
        'include_files': ['xAODJet/JetContainer.h',],
        'container_type': 'DataVector<xAOD::Jet_v1>',
        'element_type': 'xAOD::Jet_v1',
        'contains_collection': True,
        'link_libraries': ['xAODJet'],
    },
    'TrigVertexCountss': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'TrigVertexCountss',
        'include_files': ['xAODTrigMinBias/TrigVertexCountsContainer.h',],
        'container_type': 'DataVector<xAOD::TrigVertexCounts_v1>',
        'element_type': 'xAOD::TrigVertexCounts_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigMinBias'],
    },
    'TrigHisto2Ds': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'TrigHisto2Ds',
        'include_files': ['xAODTrigMinBias/TrigHisto2DContainer.h',],
        'container_type': 'DataVector<xAOD::TrigHisto2D_v1>',
        'element_type': 'xAOD::TrigHisto2D_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigMinBias'],
    },
    'TrigTrackCountss': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'TrigTrackCountss',
        'include_files': ['xAODTrigMinBias/TrigTrackCountsContainer.h',],
        'container_type': 'DataVector<xAOD::TrigTrackCounts_v1>',
        'element_type': 'xAOD::TrigTrackCounts_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigMinBias'],
    },
    'TrigT2ZdcSignalss': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'TrigT2ZdcSignalss',
        'include_files': ['xAODTrigMinBias/TrigT2ZdcSignalsContainer.h',],
        'container_type': 'DataVector<xAOD::TrigT2ZdcSignals_v1>',
        'element_type': 'xAOD::TrigT2ZdcSignals_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigMinBias'],
    },
    'TrigT2MbtsBitss': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'TrigT2MbtsBitss',
        'include_files': ['xAODTrigMinBias/TrigT2MbtsBitsContainer.h',],
        'container_type': 'DataVector<xAOD::TrigT2MbtsBits_v1>',
        'element_type': 'xAOD::TrigT2MbtsBits_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigMinBias'],
    },
    'TrigSpacePointCountss': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'TrigSpacePointCountss',
        'include_files': ['xAODTrigMinBias/TrigSpacePointCountsContainer.h',],
        'container_type': 'DataVector<xAOD::TrigSpacePointCounts_v1>',
        'element_type': 'xAOD::TrigSpacePointCounts_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigMinBias'],
    },
    'TrigRNNOutputs': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'TrigRNNOutputs',
        'include_files': ['xAODTrigRinger/TrigRNNOutputContainer.h',],
        'container_type': 'DataVector<xAOD::TrigRNNOutput_v2>',
        'element_type': 'xAOD::TrigRNNOutput_v2',
        'contains_collection': True,
        'link_libraries': ['xAODTrigRinger'],
    },
    'TrigRingerRingss': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'TrigRingerRingss',
        'include_files': ['xAODTrigRinger/TrigRingerRingsContainer.h',],
        'container_type': 'DataVector<xAOD::TrigRingerRings_v2>',
        'element_type': 'xAOD::TrigRingerRings_v2',
        'contains_collection': True,
        'link_libraries': ['xAODTrigRinger'],
    },
    'BTaggings': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'BTaggings',
        'include_files': ['xAODBTagging/BTaggingContainer.h',],
        'container_type': 'DataVector<xAOD::BTagging_v1>',
        'element_type': 'xAOD::BTagging_v1',
        'contains_collection': True,
        'link_libraries': ['xAODBTagging'],
    },
    'BTagVertices': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'BTagVertices',
        'include_files': ['xAODBTagging/BTagVertexContainer.h',],
        'container_type': 'DataVector<xAOD::BTagVertex_v1>',
        'element_type': 'xAOD::BTagVertex_v1',
        'contains_collection': True,
        'link_libraries': ['xAODBTagging'],
    },
    'L2IsoMuons': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'L2IsoMuons',
        'include_files': ['xAODTrigMuon/L2IsoMuonContainer.h',],
        'container_type': 'DataVector<xAOD::L2IsoMuon_v1>',
        'element_type': 'xAOD::L2IsoMuon_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigMuon'],
    },
    'L2StandAloneMuons': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'L2StandAloneMuons',
        'include_files': ['xAODTrigMuon/L2StandAloneMuonContainer.h',],
        'container_type': 'DataVector<xAOD::L2StandAloneMuon_v2>',
        'element_type': 'xAOD::L2StandAloneMuon_v2',
        'contains_collection': True,
        'link_libraries': ['xAODTrigMuon'],
    },
    'L2CombinedMuons': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'L2CombinedMuons',
        'include_files': ['xAODTrigMuon/L2CombinedMuonContainer.h',],
        'container_type': 'DataVector<xAOD::L2CombinedMuon_v1>',
        'element_type': 'xAOD::L2CombinedMuon_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigMuon'],
    },
    'Electrons': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'Electrons',
        'include_files': ['xAODEgamma/ElectronContainer.h',],
        'container_type': 'DataVector<xAOD::Electron_v1>',
        'element_type': 'xAOD::Electron_v1',
        'contains_collection': True,
        'link_libraries': ['xAODEgamma'],
    },
    'Egammas': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'Egammas',
        'include_files': ['xAODEgamma/EgammaContainer.h',],
        'container_type': 'DataVector<xAOD::Egamma_v1>',
        'element_type': 'xAOD::Egamma_v1',
        'contains_collection': True,
        'link_libraries': ['xAODEgamma'],
    },
    'Photons': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'Photons',
        'include_files': ['xAODEgamma/PhotonContainer.h',],
        'container_type': 'DataVector<xAOD::Photon_v1>',
        'element_type': 'xAOD::Photon_v1',
        'contains_collection': True,
        'link_libraries': ['xAODEgamma'],
    },
    'TruthMetaDatas': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'TruthMetaDatas',
        'include_files': ['xAODTruth/TruthMetaDataContainer.h',],
        'container_type': 'DataVector<xAOD::TruthMetaData_v1>',
        'element_type': 'xAOD::TruthMetaData_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTruth'],
    },
    'TruthVertices': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'TruthVertices',
        'include_files': ['xAODTruth/TruthVertexContainer.h',],
        'container_type': 'DataVector<xAOD::TruthVertex_v1>',
        'element_type': 'xAOD::TruthVertex_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTruth'],
    },
    'TruthEventBases': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'TruthEventBases',
        'include_files': ['xAODTruth/TruthEventBaseContainer.h',],
        'container_type': 'DataVector<xAOD::TruthEventBase_v1>',
        'element_type': 'xAOD::TruthEventBase_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTruth'],
    },
    'TruthPileupEvents': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'TruthPileupEvents',
        'include_files': ['xAODTruth/TruthPileupEventContainer.h',],
        'container_type': 'DataVector<xAOD::TruthPileupEvent_v1>',
        'element_type': 'xAOD::TruthPileupEvent_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTruth'],
    },
    'TruthEvents': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'TruthEvents',
        'include_files': ['xAODTruth/TruthEventContainer.h',],
        'container_type': 'DataVector<xAOD::TruthEvent_v1>',
        'element_type': 'xAOD::TruthEvent_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTruth'],
    },
    'TruthParticles': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'TruthParticles',
        'include_files': ['xAODTruth/TruthParticleContainer.h',],
        'container_type': 'DataVector<xAOD::TruthParticle_v1>',
        'element_type': 'xAOD::TruthParticle_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTruth'],
    },
    'BCMRawDatas': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'BCMRawDatas',
        'include_files': ['xAODLuminosity/BCMRawDataContainer.h',],
        'container_type': 'DataVector<xAOD::BCMRawData_v1>',
        'element_type': 'xAOD::BCMRawData_v1',
        'contains_collection': True,
        'link_libraries': ['xAODLuminosity'],
    },
    'LumiBlockRanges': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'LumiBlockRanges',
        'include_files': ['xAODLuminosity/LumiBlockRangeContainer.h',],
        'container_type': 'DataVector<xAOD::LumiBlockRange_v1>',
        'element_type': 'xAOD::LumiBlockRange_v1',
        'contains_collection': True,
        'link_libraries': ['xAODLuminosity'],
    },
    'RingSetConfs': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'RingSetConfs',
        'include_files': ['xAODCaloRings/RingSetConfContainer.h',],
        'container_type': 'DataVector<xAOD::RingSetConf_v1>',
        'element_type': 'xAOD::RingSetConf_v1',
        'contains_collection': True,
        'link_libraries': ['xAODCaloRings'],
    },
    'CaloRingss': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'CaloRingss',
        'include_files': ['xAODCaloRings/CaloRingsContainer.h',],
        'container_type': 'DataVector<xAOD::CaloRings_v1>',
        'element_type': 'xAOD::CaloRings_v1',
        'contains_collection': True,
        'link_libraries': ['xAODCaloRings'],
    },
    'RingSets': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'RingSets',
        'include_files': ['xAODCaloRings/RingSetContainer.h',],
        'container_type': 'DataVector<xAOD::RingSet_v1>',
        'element_type': 'xAOD::RingSet_v1',
        'contains_collection': True,
        'link_libraries': ['xAODCaloRings'],
    },
    'EventInfos': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'EventInfos',
        'include_files': ['xAODEventInfo/EventInfoContainer.h',],
        'container_type': 'DataVector<xAOD::EventInfo_v1>',
        'element_type': 'xAOD::EventInfo_v1',
        'contains_collection': True,
        'link_libraries': ['xAODEventInfo'],
    },
    'MissingET': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'MissingET',
        'include_files': ['xAODMissingET/MissingETContainer.h',],
        'container_type': 'xAOD::MissingETContainer_v1',
        'element_type': 'xAOD::MissingET_v1',
        'contains_collection': True,
        'link_libraries': ['xAODMissingET'],
    },
    'TrigBphyss': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'TrigBphyss',
        'include_files': ['xAODTrigBphys/TrigBphysContainer.h',],
        'container_type': 'DataVector<xAOD::TrigBphys_v1>',
        'element_type': 'xAOD::TrigBphys_v1',
        'contains_collection': True,
        'link_libraries': ['xAODTrigBphys'],
    },
    'EventInfo': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': 'EventInfo',
        'include_files': ['xAODEventInfo/versions/EventInfo_v1.h',],
        'container_type': 'xAOD::EventInfo_v1',
        'contains_collection': False,
        'link_libraries': ['xAODEventInfo'],
    },
}

_param_metadata : Dict[str, Dict[str, Any]] = {
    'sys_error_tool': {
        'metadata_type':"add_job_script",
        'name':"sys_error_tool",
        'script':[
                "# pulled from:https://gitlab.cern.ch/atlas/athena/-/blob/21.2/PhysicsAnalysis/Algorithms/JetAnalysisAlgorithms/python/JetAnalysisAlgorithmsTest.py ",
                "# Set up the systematics loader/handler service:",
                "from AnaAlgorithm.DualUseConfig import createService",
                "from AnaAlgorithm.AlgSequence import AlgSequence",
                "calibrationAlgSeq = AlgSequence()",
                "sysService = createService( 'CP::SystematicsSvc', 'SystematicsSvc', sequence = calibrationAlgSeq )",
                "sysService.systematicsList = ['{calibration}']",
                "# Add sequence to job",
            ],
    },
    'pileup_tool': {
        'metadata_type':"add_job_script",
        'name':"pileup_tool",
        'script':[
                "from AsgAnalysisAlgorithms.PileupAnalysisSequence import makePileupAnalysisSequence",
                "pileupSequence = makePileupAnalysisSequence( 'mc' )",
                "pileupSequence.configure( inputName = {}, outputName = {} )",
                "print( pileupSequence ) # For debugging",
                "calibrationAlgSeq += pileupSequence",
            ],
        'depends_on':[
                "sys_error_tool",
            ],
    },
    'common_corrections': {
        'metadata_type':"add_job_script",
        'name':"common_corrections",
        'script':[
                "jetContainer = '{calib.jet_collection}'",
                "from JetAnalysisAlgorithms.JetAnalysisSequence import makeJetAnalysisSequence",
                "jetSequence = makeJetAnalysisSequence( 'mc', jetContainer)",
                "jetSequence.configure( inputName = jetContainer, outputName = jetContainer + '_Base_%SYS%' )",
                "jetSequence.JvtEfficiencyAlg.truthJetCollection = '{calib.jet_calib_truth_collection}'",
                "jetSequence.ForwardJvtEfficiencyAlg.truthJetCollection = '{calib.jet_calib_truth_collection}'",
                "calibrationAlgSeq += jetSequence",
                "print( jetSequence ) # For debugging",
                "",
                "# Include, and then set up the jet analysis algorithm sequence:",
                "from JetAnalysisAlgorithms.JetJvtAnalysisSequence import makeJetJvtAnalysisSequence",
                "jvtSequence = makeJetJvtAnalysisSequence( 'mc', jetContainer, enableCutflow=True )",
                "jvtSequence.configure( inputName = {'jets'      : jetContainer + '_Base_%SYS%' },",
                "                       outputName = { 'jets'      : jetContainer + 'Calib_%SYS%' },",
                "                       )",
                "calibrationAlgSeq += jvtSequence",
                "print( jvtSequence ) # For debugging",
                "#",
                "muon_container = '{calib.muon_collection}'",
                "from MuonAnalysisAlgorithms.MuonAnalysisSequence import makeMuonAnalysisSequence",
                "muonSequence = makeMuonAnalysisSequence('mc', workingPoint='{calib.muon_working_point}.{calib.muon_isolation}', postfix = '{calib.muon_working_point}_{calib.muon_isolation}')",
                "muonSequence.configure( inputName = muon_container,",
                "                        outputName = muon_container + 'Calib_{calib.muon_working_point}{calib.muon_isolation}_%SYS%' )",
                "calibrationAlgSeq += muonSequence",
                "print( muonSequence ) # For debugging",
                "#",
                "from EgammaAnalysisAlgorithms.ElectronAnalysisSequence import makeElectronAnalysisSequence",
                "electronSequence = makeElectronAnalysisSequence( 'mc', '{working_point}.{isolation}', postfix = '{working_point}_{isolation}')",
                "electronSequence.configure( inputName = '{calib.electron_collection}',",
                "                            outputName = '{calib.electron_collection}_{working_point}_{isolation}_%SYS%' )",
                "calibrationAlgSeq += electronSequence",
                "print( electronSequence ) # For debugging",
                "#",
                "from EgammaAnalysisAlgorithms.PhotonAnalysisSequence import makePhotonAnalysisSequence",
                "photonSequence = makePhotonAnalysisSequence( 'mc', '{calib.photon_working_point}.{calib.photon_isolation}', postfix = '{calib.photon_working_point}_{calib.photon_isolation}')",
                "photonSequence.configure( inputName = '{calib.photon_collection}',",
                "                            outputName = '{calib.photon_collection}_{calib.photon_working_point}_{calib.photon_isolation}_%SYS%' )",
                "calibrationAlgSeq += photonSequence",
                "print( photonSequence ) # For debugging",
                "#",
                "from TauAnalysisAlgorithms.TauAnalysisSequence import makeTauAnalysisSequence",
                "tauSequence = makeTauAnalysisSequence( 'mc', '{calib.tau_working_point}', postfix = '{calib.tau_working_point}', rerunTruthMatching=False)",
                "tauSequence.configure( inputName = '{calib.tau_collection}',",
                "                       outputName = '{calib.tau_collection}_{calib.tau_working_point}_%SYS%' )",
                "calibrationAlgSeq += tauSequence",
                "print( tauSequence ) # For debugging",
            ],
        'depends_on':[
                "pileup_tool",
            ],
    },
    'ditau_corrections': {
        'metadata_type':"add_job_script",
        'name':"ditau_corrections",
        'script':[
                "from TauAnalysisAlgorithms.DiTauAnalysisSequence import makeDiTauAnalysisSequence",
                "diTauSequence = makeDiTauAnalysisSequence( 'mc', '{working_point}', postfix = '{working_point}')",
                "diTauSequence.configure( inputName = '{bank_name}',",
                "                       outputName = '{bank_name}_{working_point}_%SYS%' )",
                "calibrationAlgSeq += diTauSequence",
                "print( diTauSequence ) # For debugging",
            ],
        'depends_on':[
                "pileup_tool",
            ],
    },
    'add_calibration_to_job': {
        'metadata_type':"add_job_script",
        'name':"add_calibration_to_job",
        'script':[
                "calibrationAlgSeq.addSelfToJob( job )",
                "print(job) # for debugging",
            ],
        'depends_on':[
                "*PREVIOUS*",
            ],
    },
}

PType = TypeVar('PType')


def _get_param(call_ast: ast.Call, arg_index: int, arg_name: str, default_value: PType) -> PType:
    'Fetch the argument from the arg list'
    # Look for it as a positional argument
    if len(call_ast.args) > arg_index:
        return ast.literal_eval(call_ast.args[arg_index])

    # Look for it as a keyword argument
    kw_args = [kwa for kwa in call_ast.keywords if kwa.arg == arg_name]
    if len(kw_args) > 0:
        return ast.literal_eval(kw_args[0].value)
    
    # We can't find it - return the default value.
    return default_value


MDReplType = TypeVar('MDReplType', bound=Union[str, List[str]])



def _replace_md_value(v: MDReplType, p_name: str, new_value: str) -> MDReplType:
    'Replace one MD item'
    if isinstance(v, str):
        return v.replace('{' + p_name + '}', str(new_value))
    else:
        return [x.replace('{' + p_name + '}', str(new_value)) for x in v]


def _replace_param_values(source: MDReplType, param_values: Dict[str, Any]) -> MDReplType:
    'Replace parameter types in a string or list of strings'
    result = source
    for k, v in param_values.items():
        result = _replace_md_value(result, k, v)
    return result


def _resolve_md_params(md: Dict[str, Any], param_values: Dict[str, Any]):
    'Do parameter subst in the metadata'
    for k, v in param_values.items():
        result = {}
        for mk_key, mk_value in md.items():
            new_value = _replace_md_value(mk_value, k, v)
            if new_value != mk_value:
                result[mk_key] = new_value
        if len(result) > 0:
            md = dict(md)
            md.update(result)
            md['name'] = f"{md['name']}_{v}"
    return md

T = TypeVar('T')


def match_param_value(value, to_match) -> bool:
    'Match a parameter with special values'
    if isinstance(to_match, str):
        if to_match == "*None*":
            return value is None
        if to_match == "*Any*":
            return True
    
    return value == to_match


class _process_extra_arguments:
    'Static class that will deal with the extra arguments for each collection'
    @staticmethod
    def process_DiTauJets(bank_name: str, s: ObjectStream[T], a: ast.Call) -> Tuple[str, ObjectStream[T], ast.AST]:
        param_values = {}
        i_param = 0
        i_param += 1
        param_values['calibration'] = _get_param(a, i_param, "calibration", 'NOSYS')
        # assert isinstance(param_values['calibration'], str), f'Parameter calibration must be of type str, not {type(param_values["calibration"])}'
        i_param += 1
        param_values['working_point'] = _get_param(a, i_param, "working_point", 'Tight')
        # assert isinstance(param_values['working_point'], str), f'Parameter working_point must be of type str, not {type(param_values["working_point"])}'
        param_values['bank_name'] = bank_name

        md_name_mapping: Dict[str, str] = {}
        md_list: List[Dict[str, Any]] = []
        p_matched = False
        last_md_name = None
        if not p_matched and match_param_value(param_values['calibration'], '*None*'):
            p_matched = True
            bank_name = _replace_param_values('{bank_name}', param_values)
        if not p_matched and match_param_value(param_values['calibration'], '*Any*'):
            p_matched = True
            old_md = _param_metadata['sys_error_tool']
            md = _resolve_md_params(old_md, param_values)
            if 'depends_on' in md:
                if '*PREVIOUS*' in md['depends_on']:
                    md = dict(md)
                    md['depends_on'] = [x for x in md['depends_on'] if x != '*PREVIOUS*']
                    if last_md_name is not None:
                        md['depends_on'].append(last_md_name)
            last_md_name = md['name']
            md_list.append(md)
            md_name_mapping[old_md['name']] = md['name']
            old_md = _param_metadata['pileup_tool']
            md = _resolve_md_params(old_md, param_values)
            if 'depends_on' in md:
                if '*PREVIOUS*' in md['depends_on']:
                    md = dict(md)
                    md['depends_on'] = [x for x in md['depends_on'] if x != '*PREVIOUS*']
                    if last_md_name is not None:
                        md['depends_on'].append(last_md_name)
            last_md_name = md['name']
            md_list.append(md)
            md_name_mapping[old_md['name']] = md['name']
            old_md = _param_metadata['ditau_corrections']
            md = _resolve_md_params(old_md, param_values)
            if 'depends_on' in md:
                if '*PREVIOUS*' in md['depends_on']:
                    md = dict(md)
                    md['depends_on'] = [x for x in md['depends_on'] if x != '*PREVIOUS*']
                    if last_md_name is not None:
                        md['depends_on'].append(last_md_name)
            last_md_name = md['name']
            md_list.append(md)
            md_name_mapping[old_md['name']] = md['name']
            old_md = _param_metadata['add_calibration_to_job']
            md = _resolve_md_params(old_md, param_values)
            if 'depends_on' in md:
                if '*PREVIOUS*' in md['depends_on']:
                    md = dict(md)
                    md['depends_on'] = [x for x in md['depends_on'] if x != '*PREVIOUS*']
                    if last_md_name is not None:
                        md['depends_on'].append(last_md_name)
            last_md_name = md['name']
            md_list.append(md)
            md_name_mapping[old_md['name']] = md['name']
            bank_name = _replace_param_values('{bank_name}_{working_point}_{calibration}', param_values)
        p_matched = False
        last_md_name = None

        for md in md_list:
            if 'depends_on' in md:
                md = dict(md) # Make a copy so we don't mess up downstream queries
                md['depends_on'] = [(md_name_mapping[x] if x in md_name_mapping else x) for x in md['depends_on']]
            s = s.MetaData(md)

        return bank_name, s, a


def _add_collection_metadata(s: ObjectStream[T], a: ast.Call) -> Tuple[ObjectStream[T], ast.Call]:
    '''Add metadata for a collection to the func_adl stream if we know about it
    '''
    # Unpack the call as needed
    assert isinstance(a.func, ast.Attribute)
    collection_name = a.func.attr
    # collection_bank = ast.literal_eval(a.args[0])

    # # If it has extra arguments, we need to process those.
    # arg_processor = getattr(_process_extra_arguments, f'process_{collection_name}', None)
    # if arg_processor is not None:
    #     new_a = copy.deepcopy(a)
    #     new_bank, s, a = arg_processor(collection_bank, s, new_a)
    #     a.args = [ast.Constant(new_bank)]


    # Finally, add the collection defining metadata so the backend
    # knows about this collection and how to access it.
    if collection_name in _collection_map:
        s_update = s.MetaData(_collection_map[collection_name])
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_collection_metadata)
class Event:
    '''The top level event class. All data in the event is accessed from here
    '''



    def TrigMissingETs(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.trigmissinget_v1.TrigMissingET_v1]:
        ...

    def TrackParticleClusterAssociations(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.trackparticleclusterassociation_v1.TrackParticleClusterAssociation_v1]:
        ...

    def KLFitterResults(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.klfitterresult.KLFitterResult]:
        ...

    def SystematicEvents(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.systematicevent.SystematicEvent]:
        ...

    def PseudoTopResults(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.pseudotopresult.PseudoTopResult]:
        ...

    def Vertices(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.vertex_v1.Vertex_v1]:
        ...

    def SCTRawHitValidations(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.sctrawhitvalidation_v1.SCTRawHitValidation_v1]:
        ...

    def TrackMeasurementValidations(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.trackmeasurementvalidation_v1.TrackMeasurementValidation_v1]:
        ...

    def TrackStates(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.trackstate_v1.TrackState_v1]:
        ...

    def TrackJacobians(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.trackjacobian_v1.TrackJacobian_v1]:
        ...

    def TrackStateValidations(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.trackstatevalidation_v1.TrackStateValidation_v1]:
        ...

    def TrackParticles(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.trackparticle_v1.TrackParticle_v1]:
        ...

    def NeutralParticles(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.neutralparticle_v1.NeutralParticle_v1]:
        ...

    def TrackParameterss(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.trackparameters_v1.TrackParameters_v1]:
        ...

    def TrackMeasurements(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.trackmeasurement_v1.TrackMeasurement_v1]:
        ...

    def UncalibratedMeasurements(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.uncalibratedmeasurement_v1.UncalibratedMeasurement_v1]:
        ...

    def TrackCaloClusters(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.trackcalocluster_v1.TrackCaloCluster_v1]:
        ...

    def PFOs(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.pfo_v1.PFO_v1]:
        ...

    def CaloClusters(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.calocluster_v1.CaloCluster_v1]:
        ...

    def CaloTowers(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.calotower_v1.CaloTower_v1]:
        ...

    def AFPSiHits(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.afpsihit_v2.AFPSiHit_v2]:
        ...

    def ForwardEventInfos(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.forwardeventinfo_v1.ForwardEventInfo_v1]:
        ...

    def AFPToFTracks(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.afptoftrack_v1.AFPToFTrack_v1]:
        ...

    def AFPVertexs(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.afpvertex_v1.AFPVertex_v1]:
        ...

    def ALFADatas(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.alfadata_v1.ALFAData_v1]:
        ...

    def AFPDatas(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.afpdata_v1.AFPData_v1]:
        ...

    def ZdcModules(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.zdcmodule_v1.ZdcModule_v1]:
        ...

    def AFPProtons(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.afpproton_v1.AFPProton_v1]:
        ...

    def AFPSiHitsClusters(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.afpsihitscluster_v1.AFPSiHitsCluster_v1]:
        ...

    def AFPToFHits(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.afptofhit_v1.AFPToFHit_v1]:
        ...

    def MBTSModules(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.mbtsmodule_v1.MBTSModule_v1]:
        ...

    def AFPTracks(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.afptrack_v2.AFPTrack_v2]:
        ...

    def CMMCPHitss(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.cmmcphits_v1.CMMCPHits_v1]:
        ...

    def JEMHitss(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.jemhits_v1.JEMHits_v1]:
        ...

    def CMXCPHitss(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.cmxcphits_v1.CMXCPHits_v1]:
        ...

    def CMXEtSumss(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.cmxetsums_v1.CMXEtSums_v1]:
        ...

    def CPMRoIs(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.cpmroi_v1.CPMRoI_v1]:
        ...

    def CMXRoIs(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.cmxroi_v1.CMXRoI_v1]:
        ...

    def jFexTowers(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.jfextower_v1.jFexTower_v1]:
        ...

    def TriggerTowers(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.triggertower_v2.TriggerTower_v2]:
        ...

    def JEMTobRoIs(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.jemtobroi_v1.JEMTobRoI_v1]:
        ...

    def CPMTowers(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.cpmtower_v2.CPMTower_v2]:
        ...

    def JEMRoIs(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.jemroi_v1.JEMRoI_v1]:
        ...

    def CPMHitss(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.cpmhits_v1.CPMHits_v1]:
        ...

    def JEMEtSumss(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.jemetsums_v2.JEMEtSums_v2]:
        ...

    def CPMTobRoIs(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.cpmtobroi_v1.CPMTobRoI_v1]:
        ...

    def CMXJetTobs(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.cmxjettob_v1.CMXJetTob_v1]:
        ...

    def CMMEtSumss(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.cmmetsums_v1.CMMEtSums_v1]:
        ...

    def CMXJetHitss(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.cmxjethits_v1.CMXJetHits_v1]:
        ...

    def CMMJetHitss(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.cmmjethits_v1.CMMJetHits_v1]:
        ...

    def eFexTowers(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.efextower_v1.eFexTower_v1]:
        ...

    def gFexTowers(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.gfextower_v1.gFexTower_v1]:
        ...

    def JetElements(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.jetelement_v2.JetElement_v2]:
        ...

    def L1TopoRawDatas(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.l1toporawdata_v1.L1TopoRawData_v1]:
        ...

    def CMXCPTobs(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.cmxcptob_v1.CMXCPTob_v1]:
        ...

    def RODHeaders(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.rodheader_v2.RODHeader_v2]:
        ...

    def jFexMETRoIs(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.jfexmetroi_v1.jFexMETRoI_v1]:
        ...

    def TrigPassBitss(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.trigpassbits_v1.TrigPassBits_v1]:
        ...

    def EmTauRoIs(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.emtauroi_v2.EmTauRoI_v2]:
        ...

    def jFexSumETRoIs(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.jfexsumetroi_v1.jFexSumETRoI_v1]:
        ...

    def jFexSRJetRoIs(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.jfexsrjetroi_v1.jFexSRJetRoI_v1]:
        ...

    def TriggerMenus(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.triggermenu_v1.TriggerMenu_v1]:
        ...

    def gFexJetRoIs(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.gfexjetroi_v1.gFexJetRoI_v1]:
        ...

    def jFexLRJetRoIs(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.jfexlrjetroi_v1.jFexLRJetRoI_v1]:
        ...

    def MuonRoIs(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.muonroi_v1.MuonRoI_v1]:
        ...

    def eFexEMRoIs(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.efexemroi_v1.eFexEMRoI_v1]:
        ...

    def JetRoIs(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.jetroi_v2.JetRoI_v2]:
        ...

    def jFexTauRoIs(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.jfextauroi_v1.jFexTauRoI_v1]:
        ...

    def BunchConfs(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.bunchconf_v1.BunchConf_v1]:
        ...

    def TriggerMenuJsons(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.triggermenujson_v1.TriggerMenuJson_v1]:
        ...

    def gFexGlobalRoIs(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.gfexglobalroi_v1.gFexGlobalRoI_v1]:
        ...

    def TrigComposites(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.trigcomposite_v1.TrigComposite_v1]:
        ...

    def jFexFwdElRoIs(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.jfexfwdelroi_v1.jFexFwdElRoI_v1]:
        ...

    def L1TopoSimResultss(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.l1toposimresults_v1.L1TopoSimResults_v1]:
        ...

    def eFexTauRoIs(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.efextauroi_v1.eFexTauRoI_v1]:
        ...

    def IParticles(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.iparticle.IParticle]:
        ...

    def TrigEMClusters(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.trigemcluster_v1.TrigEMCluster_v1]:
        ...

    def TrigCaloClusters(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.trigcalocluster_v1.TrigCaloCluster_v1]:
        ...

    @func_adl_callback(lambda s, a: func_adl_servicex_xaodr22.calibration_support.fixup_collection_call(s, a, 'muon_collection'))
    def Muons(self, collection: Optional[str] = None, calibrate: Optional[bool] = True) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.muon_v1.Muon_v1]:
        ...

    def MuonSegments(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.muonsegment_v1.MuonSegment_v1]:
        ...

    def SlowMuons(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.slowmuon_v1.SlowMuon_v1]:
        ...

    def CompositeParticles(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.compositeparticle_v1.CompositeParticle_v1]:
        ...

    def Particles(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.particle_v1.Particle_v1]:
        ...

    def HIEventShapes(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.hieventshape_v2.HIEventShape_v2]:
        ...

    def TrigPhotons(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.trigphoton_v1.TrigPhoton_v1]:
        ...

    def TrigElectrons(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.trigelectron_v1.TrigElectron_v1]:
        ...

    def TauTracks(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.tautrack_v1.TauTrack_v1]:
        ...

    @func_adl_callback(lambda s, a: func_adl_servicex_xaodr22.calibration_support.fixup_collection_call(s, a, 'tau_collection'))
    def TauJets(self, collection: Optional[str] = None, calibrate: Optional[bool] = True) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.taujet_v3.TauJet_v3]:
        ...

    def DiTauJets(self, calibration: str = 'NOSYS', working_point: str = 'Tight') -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.ditaujet_v1.DiTauJet_v1]:
        ...

    def CutBookkeepers(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.cutbookkeeper_v1.CutBookkeeper_v1]:
        ...

    @func_adl_callback(lambda s, a: func_adl_servicex_xaodr22.calibration_support.fixup_collection_call(s, a, 'jet_collection'))
    def Jets(self, collection: Optional[str] = None, calibrate: Optional[bool] = True) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.jet_v1.Jet_v1]:
        ...

    def TrigVertexCountss(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.trigvertexcounts_v1.TrigVertexCounts_v1]:
        ...

    def TrigHisto2Ds(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.trighisto2d_v1.TrigHisto2D_v1]:
        ...

    def TrigTrackCountss(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.trigtrackcounts_v1.TrigTrackCounts_v1]:
        ...

    def TrigT2ZdcSignalss(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.trigt2zdcsignals_v1.TrigT2ZdcSignals_v1]:
        ...

    def TrigT2MbtsBitss(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.trigt2mbtsbits_v1.TrigT2MbtsBits_v1]:
        ...

    def TrigSpacePointCountss(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.trigspacepointcounts_v1.TrigSpacePointCounts_v1]:
        ...

    def TrigRNNOutputs(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.trigrnnoutput_v2.TrigRNNOutput_v2]:
        ...

    def TrigRingerRingss(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.trigringerrings_v2.TrigRingerRings_v2]:
        ...

    def BTaggings(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.btagging_v1.BTagging_v1]:
        ...

    def BTagVertices(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.btagvertex_v1.BTagVertex_v1]:
        ...

    def L2IsoMuons(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.l2isomuon_v1.L2IsoMuon_v1]:
        ...

    def L2StandAloneMuons(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.l2standalonemuon_v2.L2StandAloneMuon_v2]:
        ...

    def L2CombinedMuons(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.l2combinedmuon_v1.L2CombinedMuon_v1]:
        ...

    @func_adl_callback(lambda s, a: func_adl_servicex_xaodr22.calibration_support.fixup_collection_call(s, a, 'electron_collection'))
    def Electrons(self, collection: Optional[str] = None, calibrate: Optional[bool] = True) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.electron_v1.Electron_v1]:
        ...

    def Egammas(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.egamma_v1.Egamma_v1]:
        ...

    @func_adl_callback(lambda s, a: func_adl_servicex_xaodr22.calibration_support.fixup_collection_call(s, a, 'photon_collection'))
    def Photons(self, collection: Optional[str] = None, calibrate: Optional[bool] = True) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.photon_v1.Photon_v1]:
        ...

    def TruthMetaDatas(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.truthmetadata_v1.TruthMetaData_v1]:
        ...

    def TruthVertices(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.truthvertex_v1.TruthVertex_v1]:
        ...

    def TruthEventBases(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.trutheventbase_v1.TruthEventBase_v1]:
        ...

    def TruthPileupEvents(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.truthpileupevent_v1.TruthPileupEvent_v1]:
        ...

    def TruthEvents(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.truthevent_v1.TruthEvent_v1]:
        ...

    def TruthParticles(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.truthparticle_v1.TruthParticle_v1]:
        ...

    def BCMRawDatas(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.bcmrawdata_v1.BCMRawData_v1]:
        ...

    def LumiBlockRanges(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.lumiblockrange_v1.LumiBlockRange_v1]:
        ...

    def RingSetConfs(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.ringsetconf_v1.RingSetConf_v1]:
        ...

    def CaloRingss(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.calorings_v1.CaloRings_v1]:
        ...

    def RingSets(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.ringset_v1.RingSet_v1]:
        ...

    def EventInfos(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.eventinfo_v1.EventInfo_v1]:
        ...

    @func_adl_callback(lambda s, a: func_adl_servicex_xaodr22.calibration_support.fixup_collection_call(s, a, 'met_collection'))
    def MissingET(self, collection: Optional[str] = None, calibrate: Optional[bool] = True) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.missinget_v1.MissingET_v1]:
        ...

    def TrigBphyss(self, name: str) -> func_adl_servicex_xaodr22.FADLStream[func_adl_servicex_xaodr22.xAOD.trigbphys_v1.TrigBphys_v1]:
        ...

    def EventInfo(self, name: str) -> func_adl_servicex_xaodr22.xAOD.eventinfo_v1.EventInfo_v1:
        ...
