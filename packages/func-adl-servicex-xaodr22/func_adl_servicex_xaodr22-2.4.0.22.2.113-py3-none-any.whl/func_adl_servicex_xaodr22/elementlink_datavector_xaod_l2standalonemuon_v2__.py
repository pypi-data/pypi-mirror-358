from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr22

_method_map = {
    'isValid': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'isValid',
        'return_type': 'bool',
    },
    'pt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'pt',
        'return_type': 'double',
        'deref_count': 2
    },
    'eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'eta',
        'return_type': 'double',
        'deref_count': 2
    },
    'phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'phi',
        'return_type': 'double',
        'deref_count': 2
    },
    'm': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'm',
        'return_type': 'double',
        'deref_count': 2
    },
    'e': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'e',
        'return_type': 'double',
        'deref_count': 2
    },
    'rapidity': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'rapidity',
        'return_type': 'double',
        'deref_count': 2
    },
    'p4': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'p4',
        'return_type': 'TLorentzVector',
        'deref_count': 2
    },
    'type': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'type',
        'return_type': 'xAODType::ObjectType',
        'deref_count': 2
    },
    'roiWord': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'roiWord',
        'return_type': 'unsigned int',
        'deref_count': 2
    },
    'sAddress': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'sAddress',
        'return_type': 'int',
        'deref_count': 2
    },
    'etaMS': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'etaMS',
        'return_type': 'float',
        'deref_count': 2
    },
    'phiMS': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'phiMS',
        'return_type': 'float',
        'deref_count': 2
    },
    'dirPhiMS': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'dirPhiMS',
        'return_type': 'float',
        'deref_count': 2
    },
    'rMS': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'rMS',
        'return_type': 'float',
        'deref_count': 2
    },
    'zMS': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'zMS',
        'return_type': 'float',
        'deref_count': 2
    },
    'dirZMS': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'dirZMS',
        'return_type': 'float',
        'deref_count': 2
    },
    'beta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'beta',
        'return_type': 'float',
        'deref_count': 2
    },
    'barrelRadius': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'barrelRadius',
        'return_type': 'float',
        'deref_count': 2
    },
    'barrelSagitta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'barrelSagitta',
        'return_type': 'float',
        'deref_count': 2
    },
    'endcapAlpha': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'endcapAlpha',
        'return_type': 'float',
        'deref_count': 2
    },
    'endcapBeta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'endcapBeta',
        'return_type': 'float',
        'deref_count': 2
    },
    'endcapRadius': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'endcapRadius',
        'return_type': 'float',
        'deref_count': 2
    },
    'etaMap': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'etaMap',
        'return_type': 'float',
        'deref_count': 2
    },
    'phiMap': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'phiMap',
        'return_type': 'float',
        'deref_count': 2
    },
    'etaBin': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'etaBin',
        'return_type': 'int',
        'deref_count': 2
    },
    'phiBin': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'phiBin',
        'return_type': 'int',
        'deref_count': 2
    },
    'isTgcFailure': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'isTgcFailure',
        'return_type': 'int',
        'deref_count': 2
    },
    'isRpcFailure': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'isRpcFailure',
        'return_type': 'int',
        'deref_count': 2
    },
    'deltaPt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'deltaPt',
        'return_type': 'float',
        'deref_count': 2
    },
    'deltaPtParm1': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'deltaPtParm1',
        'return_type': 'float',
        'deref_count': 2
    },
    'deltaPtParm2': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'deltaPtParm2',
        'return_type': 'float',
        'deref_count': 2
    },
    'deltaPtParm3': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'deltaPtParm3',
        'return_type': 'float',
        'deref_count': 2
    },
    'deltaEta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'deltaEta',
        'return_type': 'float',
        'deref_count': 2
    },
    'deltaPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'deltaPhi',
        'return_type': 'float',
        'deref_count': 2
    },
    'superPointR': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'superPointR',
        'return_type': 'float',
        'deref_count': 2
    },
    'superPointZ': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'superPointZ',
        'return_type': 'float',
        'deref_count': 2
    },
    'superPointSlope': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'superPointSlope',
        'return_type': 'float',
        'deref_count': 2
    },
    'superPointIntercept': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'superPointIntercept',
        'return_type': 'float',
        'deref_count': 2
    },
    'superPointChi2': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'superPointChi2',
        'return_type': 'float',
        'deref_count': 2
    },
    'nTrackPositions': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'nTrackPositions',
        'return_type': 'unsigned int',
        'deref_count': 2
    },
    'trackPositionR': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'trackPositionR',
        'return_type': 'float',
        'deref_count': 2
    },
    'trackPositionZ': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'trackPositionZ',
        'return_type': 'float',
        'deref_count': 2
    },
    'trackPositionEta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'trackPositionEta',
        'return_type': 'float',
        'deref_count': 2
    },
    'trackPositionPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'trackPositionPhi',
        'return_type': 'float',
        'deref_count': 2
    },
    'algoId': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'algoId',
        'return_type': 'int',
        'deref_count': 2
    },
    'teId': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'teId',
        'return_type': 'unsigned int',
        'deref_count': 2
    },
    'lvl1Id': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'lvl1Id',
        'return_type': 'unsigned int',
        'deref_count': 2
    },
    'lumiBlock': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'lumiBlock',
        'return_type': 'unsigned int',
        'deref_count': 2
    },
    'muonDetMask': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'muonDetMask',
        'return_type': 'unsigned int',
        'deref_count': 2
    },
    'roiId': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'roiId',
        'return_type': 'unsigned int',
        'deref_count': 2
    },
    'roiSystem': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'roiSystem',
        'return_type': 'unsigned int',
        'deref_count': 2
    },
    'roiSubsystem': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'roiSubsystem',
        'return_type': 'unsigned int',
        'deref_count': 2
    },
    'roiSector': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'roiSector',
        'return_type': 'unsigned int',
        'deref_count': 2
    },
    'roiNumber': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'roiNumber',
        'return_type': 'unsigned int',
        'deref_count': 2
    },
    'roiThreshold': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'roiThreshold',
        'return_type': 'unsigned int',
        'deref_count': 2
    },
    'roiEta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'roiEta',
        'return_type': 'float',
        'deref_count': 2
    },
    'roiPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'roiPhi',
        'return_type': 'float',
        'deref_count': 2
    },
    'tgcPt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'tgcPt',
        'return_type': 'float',
        'deref_count': 2
    },
    'ptBarrelRadius': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'ptBarrelRadius',
        'return_type': 'float',
        'deref_count': 2
    },
    'ptBarrelSagitta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'ptBarrelSagitta',
        'return_type': 'float',
        'deref_count': 2
    },
    'ptEndcapAlpha': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'ptEndcapAlpha',
        'return_type': 'float',
        'deref_count': 2
    },
    'ptEndcapBeta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'ptEndcapBeta',
        'return_type': 'float',
        'deref_count': 2
    },
    'ptEndcapRadius': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'ptEndcapRadius',
        'return_type': 'float',
        'deref_count': 2
    },
    'ptCSC': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'ptCSC',
        'return_type': 'float',
        'deref_count': 2
    },
    'chamberType1': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'chamberType1',
        'return_type': 'int',
        'deref_count': 2
    },
    'chamberType2': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'chamberType2',
        'return_type': 'int',
        'deref_count': 2
    },
    'roadAw': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'roadAw',
        'return_type': 'float',
        'deref_count': 2
    },
    'roadBw': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'roadBw',
        'return_type': 'float',
        'deref_count': 2
    },
    'zMin': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'zMin',
        'return_type': 'float',
        'deref_count': 2
    },
    'zMax': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'zMax',
        'return_type': 'float',
        'deref_count': 2
    },
    'rMin': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'rMin',
        'return_type': 'float',
        'deref_count': 2
    },
    'rMax': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'rMax',
        'return_type': 'float',
        'deref_count': 2
    },
    'etaMin': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'etaMin',
        'return_type': 'float',
        'deref_count': 2
    },
    'etaMax': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'etaMax',
        'return_type': 'float',
        'deref_count': 2
    },
    'tgcInnEta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'tgcInnEta',
        'return_type': 'float',
        'deref_count': 2
    },
    'tgcInnPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'tgcInnPhi',
        'return_type': 'float',
        'deref_count': 2
    },
    'tgcInnR': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'tgcInnR',
        'return_type': 'float',
        'deref_count': 2
    },
    'tgcInnZ': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'tgcInnZ',
        'return_type': 'float',
        'deref_count': 2
    },
    'tgcInnRhoStd': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'tgcInnRhoStd',
        'return_type': 'float',
        'deref_count': 2
    },
    'tgcInnRhoN': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'tgcInnRhoN',
        'return_type': 'long',
        'deref_count': 2
    },
    'tgcInnPhiStd': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'tgcInnPhiStd',
        'return_type': 'float',
        'deref_count': 2
    },
    'tgcInnPhiN': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'tgcInnPhiN',
        'return_type': 'long',
        'deref_count': 2
    },
    'tgcMid1Eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'tgcMid1Eta',
        'return_type': 'float',
        'deref_count': 2
    },
    'tgcMid1Phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'tgcMid1Phi',
        'return_type': 'float',
        'deref_count': 2
    },
    'tgcMid1R': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'tgcMid1R',
        'return_type': 'float',
        'deref_count': 2
    },
    'tgcMid1Z': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'tgcMid1Z',
        'return_type': 'float',
        'deref_count': 2
    },
    'tgcMid2Eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'tgcMid2Eta',
        'return_type': 'float',
        'deref_count': 2
    },
    'tgcMid2Phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'tgcMid2Phi',
        'return_type': 'float',
        'deref_count': 2
    },
    'tgcMid2R': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'tgcMid2R',
        'return_type': 'float',
        'deref_count': 2
    },
    'tgcMid2Z': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'tgcMid2Z',
        'return_type': 'float',
        'deref_count': 2
    },
    'tgcMidRhoChi2': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'tgcMidRhoChi2',
        'return_type': 'float',
        'deref_count': 2
    },
    'tgcMidRhoN': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'tgcMidRhoN',
        'return_type': 'long',
        'deref_count': 2
    },
    'tgcMidPhiChi2': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'tgcMidPhiChi2',
        'return_type': 'float',
        'deref_count': 2
    },
    'tgcMidPhiN': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'tgcMidPhiN',
        'return_type': 'long',
        'deref_count': 2
    },
    'rpcFitInnPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'rpcFitInnPhi',
        'return_type': 'float',
        'deref_count': 2
    },
    'rpcFitInnSlope': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'rpcFitInnSlope',
        'return_type': 'float',
        'deref_count': 2
    },
    'rpcFitInnOffset': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'rpcFitInnOffset',
        'return_type': 'float',
        'deref_count': 2
    },
    'rpcFitMidPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'rpcFitMidPhi',
        'return_type': 'float',
        'deref_count': 2
    },
    'rpcFitMidSlope': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'rpcFitMidSlope',
        'return_type': 'float',
        'deref_count': 2
    },
    'rpcFitMidOffset': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'rpcFitMidOffset',
        'return_type': 'float',
        'deref_count': 2
    },
    'rpcFitOutPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'rpcFitOutPhi',
        'return_type': 'float',
        'deref_count': 2
    },
    'rpcFitOutSlope': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'rpcFitOutSlope',
        'return_type': 'float',
        'deref_count': 2
    },
    'rpcFitOutOffset': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'rpcFitOutOffset',
        'return_type': 'float',
        'deref_count': 2
    },
    'rpcHitsCapacity': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'rpcHitsCapacity',
        'return_type': 'int',
        'deref_count': 2
    },
    'tgcHitsCapacity': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'tgcHitsCapacity',
        'return_type': 'int',
        'deref_count': 2
    },
    'mdtHitsCapacity': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'mdtHitsCapacity',
        'return_type': 'int',
        'deref_count': 2
    },
    'cscHitsCapacity': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'cscHitsCapacity',
        'return_type': 'int',
        'deref_count': 2
    },
    'rpcHitLayer': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'rpcHitLayer',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned int>',
        'deref_count': 2
    },
    'rpcHitMeasuresPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'rpcHitMeasuresPhi',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned int>',
        'deref_count': 2
    },
    'rpcHitX': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'rpcHitX',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
        'deref_count': 2
    },
    'rpcHitY': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'rpcHitY',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
        'deref_count': 2
    },
    'rpcHitZ': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'rpcHitZ',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
        'deref_count': 2
    },
    'rpcHitTime': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'rpcHitTime',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
        'deref_count': 2
    },
    'rpcHitDistToEtaReadout': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'rpcHitDistToEtaReadout',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
        'deref_count': 2
    },
    'rpcHitDistToPhiReadout': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'rpcHitDistToPhiReadout',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
        'deref_count': 2
    },
    'rpcHitStationName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'rpcHitStationName',
        'return_type_element': 'string',
        'return_type_collection': 'const vector<string>',
        'deref_count': 2
    },
    'tgcHitEta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'tgcHitEta',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
        'deref_count': 2
    },
    'tgcHitPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'tgcHitPhi',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
        'deref_count': 2
    },
    'tgcHitR': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'tgcHitR',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
        'deref_count': 2
    },
    'tgcHitZ': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'tgcHitZ',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
        'deref_count': 2
    },
    'tgcHitWidth': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'tgcHitWidth',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
        'deref_count': 2
    },
    'tgcHitStationNum': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'tgcHitStationNum',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
        'deref_count': 2
    },
    'tgcHitIsStrip': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'tgcHitIsStrip',
        'return_type_element': 'bool',
        'return_type_collection': 'const vector<bool>',
        'deref_count': 2
    },
    'tgcHitBCTag': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'tgcHitBCTag',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
        'deref_count': 2
    },
    'tgcHitInRoad': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'tgcHitInRoad',
        'return_type_element': 'bool',
        'return_type_collection': 'const vector<bool>',
        'deref_count': 2
    },
    'nMdtHits': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'nMdtHits',
        'return_type': 'unsigned int',
        'deref_count': 2
    },
    'mdtHitOnlineId': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'mdtHitOnlineId',
        'return_type': 'unsigned int',
        'deref_count': 2
    },
    'mdtHitOfflineId': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'mdtHitOfflineId',
        'return_type': 'int',
        'deref_count': 2
    },
    'mdtHitIsOutlier': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'mdtHitIsOutlier',
        'return_type': 'int',
        'deref_count': 2
    },
    'mdtHitChamber': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'mdtHitChamber',
        'return_type': 'int',
        'deref_count': 2
    },
    'mdtHitR': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'mdtHitR',
        'return_type': 'float',
        'deref_count': 2
    },
    'mdtHitZ': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'mdtHitZ',
        'return_type': 'float',
        'deref_count': 2
    },
    'mdtHitPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'mdtHitPhi',
        'return_type': 'float',
        'deref_count': 2
    },
    'mdtHitResidual': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'mdtHitResidual',
        'return_type': 'float',
        'deref_count': 2
    },
    'mdtHitTime': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'mdtHitTime',
        'return_type': 'float',
        'deref_count': 2
    },
    'mdtHitSpace': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'mdtHitSpace',
        'return_type': 'float',
        'deref_count': 2
    },
    'mdtHitSigma': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'mdtHitSigma',
        'return_type': 'float',
        'deref_count': 2
    },
    'nCscHits': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'nCscHits',
        'return_type': 'unsigned int',
        'deref_count': 2
    },
    'cscHitIsOutlier': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'cscHitIsOutlier',
        'return_type': 'int',
        'deref_count': 2
    },
    'cscHitChamber': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'cscHitChamber',
        'return_type': 'int',
        'deref_count': 2
    },
    'cscHitStationName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'cscHitStationName',
        'return_type': 'unsigned int',
        'deref_count': 2
    },
    'cscHitStationEta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'cscHitStationEta',
        'return_type': 'int',
        'deref_count': 2
    },
    'cscHitStationPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'cscHitStationPhi',
        'return_type': 'int',
        'deref_count': 2
    },
    'cscHitChamberLayer': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'cscHitChamberLayer',
        'return_type': 'int',
        'deref_count': 2
    },
    'cscHitWireLayer': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'cscHitWireLayer',
        'return_type': 'int',
        'deref_count': 2
    },
    'cscHitMeasuresPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'cscHitMeasuresPhi',
        'return_type': 'int',
        'deref_count': 2
    },
    'cscHitStrip': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'cscHitStrip',
        'return_type': 'int',
        'deref_count': 2
    },
    'cscHitEta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'cscHitEta',
        'return_type': 'float',
        'deref_count': 2
    },
    'cscHitPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'cscHitPhi',
        'return_type': 'float',
        'deref_count': 2
    },
    'cscHitR': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'cscHitR',
        'return_type': 'float',
        'deref_count': 2
    },
    'cscHitZ': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'cscHitZ',
        'return_type': 'float',
        'deref_count': 2
    },
    'cscHitCharge': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'cscHitCharge',
        'return_type': 'int',
        'deref_count': 2
    },
    'cscHitTime': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'cscHitTime',
        'return_type': 'float',
        'deref_count': 2
    },
    'cscHitResidual': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'cscHitResidual',
        'return_type': 'float',
        'deref_count': 2
    },
    'stgcClusterLayer': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'stgcClusterLayer',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned int>',
        'deref_count': 2
    },
    'stgcClusterIsOutlier': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'stgcClusterIsOutlier',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
        'deref_count': 2
    },
    'stgcClusterType': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'stgcClusterType',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
        'deref_count': 2
    },
    'stgcClusterEta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'stgcClusterEta',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
        'deref_count': 2
    },
    'stgcClusterPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'stgcClusterPhi',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
        'deref_count': 2
    },
    'stgcClusterR': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'stgcClusterR',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
        'deref_count': 2
    },
    'stgcClusterZ': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'stgcClusterZ',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
        'deref_count': 2
    },
    'stgcClusterResidualR': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'stgcClusterResidualR',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
        'deref_count': 2
    },
    'stgcClusterResidualPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'stgcClusterResidualPhi',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
        'deref_count': 2
    },
    'stgcClusterStationEta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'stgcClusterStationEta',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
        'deref_count': 2
    },
    'stgcClusterStationPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'stgcClusterStationPhi',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
        'deref_count': 2
    },
    'stgcClusterStationName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'stgcClusterStationName',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
        'deref_count': 2
    },
    'mmClusterLayer': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'mmClusterLayer',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned int>',
        'deref_count': 2
    },
    'mmClusterIsOutlier': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'mmClusterIsOutlier',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
        'deref_count': 2
    },
    'mmClusterEta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'mmClusterEta',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
        'deref_count': 2
    },
    'mmClusterPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'mmClusterPhi',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
        'deref_count': 2
    },
    'mmClusterR': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'mmClusterR',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
        'deref_count': 2
    },
    'mmClusterZ': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'mmClusterZ',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
        'deref_count': 2
    },
    'mmClusterResidualR': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'mmClusterResidualR',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
        'deref_count': 2
    },
    'mmClusterResidualPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'mmClusterResidualPhi',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
        'deref_count': 2
    },
    'mmClusterStationEta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'mmClusterStationEta',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
        'deref_count': 2
    },
    'mmClusterStationPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'mmClusterStationPhi',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
        'deref_count': 2
    },
    'mmClusterStationName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'mmClusterStationName',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
        'deref_count': 2
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'index',
        'return_type': 'unsigned int',
        'deref_count': 2
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
        'deref_count': 2
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
        'deref_count': 2
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'hasStore',
        'return_type': 'bool',
        'deref_count': 2
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
        'deref_count': 2
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
        'deref_count': 2
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'trackIndices',
        'return_type': 'bool',
        'deref_count': 2
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
        'method_name': 'auxdataConst',
        'return_type': 'U',
        'deref_count': 2
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::L2StandAloneMuon_v2>>',
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
            'name': 'xAODTrigMuon/versions/L2StandAloneMuon_v2.h',
            'body_includes': ["xAODTrigMuon/versions/L2StandAloneMuon_v2.h"],
        })


        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODTrigMuon',
            'link_libraries': ["xAODTrigMuon"],
        })

        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class ElementLink_DataVector_xAOD_L2StandAloneMuon_v2__:
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

    def sAddress(self) -> int:
        "A method"
        ...

    def etaMS(self) -> float:
        "A method"
        ...

    def phiMS(self) -> float:
        "A method"
        ...

    def dirPhiMS(self) -> float:
        "A method"
        ...

    def rMS(self) -> float:
        "A method"
        ...

    def zMS(self) -> float:
        "A method"
        ...

    def dirZMS(self) -> float:
        "A method"
        ...

    def beta(self) -> float:
        "A method"
        ...

    def barrelRadius(self) -> float:
        "A method"
        ...

    def barrelSagitta(self) -> float:
        "A method"
        ...

    def endcapAlpha(self) -> float:
        "A method"
        ...

    def endcapBeta(self) -> float:
        "A method"
        ...

    def endcapRadius(self) -> float:
        "A method"
        ...

    def etaMap(self) -> float:
        "A method"
        ...

    def phiMap(self) -> float:
        "A method"
        ...

    def etaBin(self) -> int:
        "A method"
        ...

    def phiBin(self) -> int:
        "A method"
        ...

    def isTgcFailure(self) -> int:
        "A method"
        ...

    def isRpcFailure(self) -> int:
        "A method"
        ...

    def deltaPt(self) -> float:
        "A method"
        ...

    def deltaPtParm1(self) -> float:
        "A method"
        ...

    def deltaPtParm2(self) -> float:
        "A method"
        ...

    def deltaPtParm3(self) -> float:
        "A method"
        ...

    def deltaEta(self) -> float:
        "A method"
        ...

    def deltaPhi(self) -> float:
        "A method"
        ...

    def superPointR(self, chamber: int) -> float:
        "A method"
        ...

    def superPointZ(self, chamber: int) -> float:
        "A method"
        ...

    def superPointSlope(self, chamber: int) -> float:
        "A method"
        ...

    def superPointIntercept(self, chamber: int) -> float:
        "A method"
        ...

    def superPointChi2(self, chamber: int) -> float:
        "A method"
        ...

    def nTrackPositions(self) -> int:
        "A method"
        ...

    def trackPositionR(self, n: int) -> float:
        "A method"
        ...

    def trackPositionZ(self, n: int) -> float:
        "A method"
        ...

    def trackPositionEta(self, n: int) -> float:
        "A method"
        ...

    def trackPositionPhi(self, n: int) -> float:
        "A method"
        ...

    def algoId(self) -> int:
        "A method"
        ...

    def teId(self) -> int:
        "A method"
        ...

    def lvl1Id(self) -> int:
        "A method"
        ...

    def lumiBlock(self) -> int:
        "A method"
        ...

    def muonDetMask(self) -> int:
        "A method"
        ...

    def roiId(self) -> int:
        "A method"
        ...

    def roiSystem(self) -> int:
        "A method"
        ...

    def roiSubsystem(self) -> int:
        "A method"
        ...

    def roiSector(self) -> int:
        "A method"
        ...

    def roiNumber(self) -> int:
        "A method"
        ...

    def roiThreshold(self) -> int:
        "A method"
        ...

    def roiEta(self) -> float:
        "A method"
        ...

    def roiPhi(self) -> float:
        "A method"
        ...

    def tgcPt(self) -> float:
        "A method"
        ...

    def ptBarrelRadius(self) -> float:
        "A method"
        ...

    def ptBarrelSagitta(self) -> float:
        "A method"
        ...

    def ptEndcapAlpha(self) -> float:
        "A method"
        ...

    def ptEndcapBeta(self) -> float:
        "A method"
        ...

    def ptEndcapRadius(self) -> float:
        "A method"
        ...

    def ptCSC(self) -> float:
        "A method"
        ...

    def chamberType1(self, station: int, sector: int) -> int:
        "A method"
        ...

    def chamberType2(self, station: int, sector: int) -> int:
        "A method"
        ...

    def roadAw(self, station: int, sector: int) -> float:
        "A method"
        ...

    def roadBw(self, station: int, sector: int) -> float:
        "A method"
        ...

    def zMin(self, station: int, sector: int) -> float:
        "A method"
        ...

    def zMax(self, station: int, sector: int) -> float:
        "A method"
        ...

    def rMin(self, station: int, sector: int) -> float:
        "A method"
        ...

    def rMax(self, station: int, sector: int) -> float:
        "A method"
        ...

    def etaMin(self, station: int, sector: int) -> float:
        "A method"
        ...

    def etaMax(self, station: int, sector: int) -> float:
        "A method"
        ...

    def tgcInnEta(self) -> float:
        "A method"
        ...

    def tgcInnPhi(self) -> float:
        "A method"
        ...

    def tgcInnR(self) -> float:
        "A method"
        ...

    def tgcInnZ(self) -> float:
        "A method"
        ...

    def tgcInnRhoStd(self) -> float:
        "A method"
        ...

    def tgcInnRhoN(self) -> int:
        "A method"
        ...

    def tgcInnPhiStd(self) -> float:
        "A method"
        ...

    def tgcInnPhiN(self) -> int:
        "A method"
        ...

    def tgcMid1Eta(self) -> float:
        "A method"
        ...

    def tgcMid1Phi(self) -> float:
        "A method"
        ...

    def tgcMid1R(self) -> float:
        "A method"
        ...

    def tgcMid1Z(self) -> float:
        "A method"
        ...

    def tgcMid2Eta(self) -> float:
        "A method"
        ...

    def tgcMid2Phi(self) -> float:
        "A method"
        ...

    def tgcMid2R(self) -> float:
        "A method"
        ...

    def tgcMid2Z(self) -> float:
        "A method"
        ...

    def tgcMidRhoChi2(self) -> float:
        "A method"
        ...

    def tgcMidRhoN(self) -> int:
        "A method"
        ...

    def tgcMidPhiChi2(self) -> float:
        "A method"
        ...

    def tgcMidPhiN(self) -> int:
        "A method"
        ...

    def rpcFitInnPhi(self) -> float:
        "A method"
        ...

    def rpcFitInnSlope(self) -> float:
        "A method"
        ...

    def rpcFitInnOffset(self) -> float:
        "A method"
        ...

    def rpcFitMidPhi(self) -> float:
        "A method"
        ...

    def rpcFitMidSlope(self) -> float:
        "A method"
        ...

    def rpcFitMidOffset(self) -> float:
        "A method"
        ...

    def rpcFitOutPhi(self) -> float:
        "A method"
        ...

    def rpcFitOutSlope(self) -> float:
        "A method"
        ...

    def rpcFitOutOffset(self) -> float:
        "A method"
        ...

    def rpcHitsCapacity(self) -> int:
        "A method"
        ...

    def tgcHitsCapacity(self) -> int:
        "A method"
        ...

    def mdtHitsCapacity(self) -> int:
        "A method"
        ...

    def cscHitsCapacity(self) -> int:
        "A method"
        ...

    def rpcHitLayer(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def rpcHitMeasuresPhi(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def rpcHitX(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def rpcHitY(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def rpcHitZ(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def rpcHitTime(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def rpcHitDistToEtaReadout(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def rpcHitDistToPhiReadout(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def rpcHitStationName(self) -> func_adl_servicex_xaodr22.vector_str_.vector_str_:
        "A method"
        ...

    def tgcHitEta(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def tgcHitPhi(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def tgcHitR(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def tgcHitZ(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def tgcHitWidth(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def tgcHitStationNum(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def tgcHitIsStrip(self) -> func_adl_servicex_xaodr22.vector_bool_.vector_bool_:
        "A method"
        ...

    def tgcHitBCTag(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def tgcHitInRoad(self) -> func_adl_servicex_xaodr22.vector_bool_.vector_bool_:
        "A method"
        ...

    def nMdtHits(self) -> int:
        "A method"
        ...

    def mdtHitOnlineId(self, tube: int) -> int:
        "A method"
        ...

    def mdtHitOfflineId(self, tube: int) -> int:
        "A method"
        ...

    def mdtHitIsOutlier(self, tube: int) -> int:
        "A method"
        ...

    def mdtHitChamber(self, tube: int) -> int:
        "A method"
        ...

    def mdtHitR(self, tube: int) -> float:
        "A method"
        ...

    def mdtHitZ(self, tube: int) -> float:
        "A method"
        ...

    def mdtHitPhi(self, tube: int) -> float:
        "A method"
        ...

    def mdtHitResidual(self, tube: int) -> float:
        "A method"
        ...

    def mdtHitTime(self, tube: int) -> float:
        "A method"
        ...

    def mdtHitSpace(self, tube: int) -> float:
        "A method"
        ...

    def mdtHitSigma(self, tube: int) -> float:
        "A method"
        ...

    def nCscHits(self) -> int:
        "A method"
        ...

    def cscHitIsOutlier(self, tube: int) -> int:
        "A method"
        ...

    def cscHitChamber(self, tube: int) -> int:
        "A method"
        ...

    def cscHitStationName(self, tube: int) -> int:
        "A method"
        ...

    def cscHitStationEta(self, tube: int) -> int:
        "A method"
        ...

    def cscHitStationPhi(self, tube: int) -> int:
        "A method"
        ...

    def cscHitChamberLayer(self, tube: int) -> int:
        "A method"
        ...

    def cscHitWireLayer(self, tube: int) -> int:
        "A method"
        ...

    def cscHitMeasuresPhi(self, tube: int) -> int:
        "A method"
        ...

    def cscHitStrip(self, tube: int) -> int:
        "A method"
        ...

    def cscHitEta(self, tube: int) -> float:
        "A method"
        ...

    def cscHitPhi(self, tube: int) -> float:
        "A method"
        ...

    def cscHitR(self, tube: int) -> float:
        "A method"
        ...

    def cscHitZ(self, tube: int) -> float:
        "A method"
        ...

    def cscHitCharge(self, tube: int) -> int:
        "A method"
        ...

    def cscHitTime(self, tube: int) -> float:
        "A method"
        ...

    def cscHitResidual(self, tube: int) -> float:
        "A method"
        ...

    def stgcClusterLayer(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def stgcClusterIsOutlier(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def stgcClusterType(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def stgcClusterEta(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def stgcClusterPhi(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def stgcClusterR(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def stgcClusterZ(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def stgcClusterResidualR(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def stgcClusterResidualPhi(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def stgcClusterStationEta(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def stgcClusterStationPhi(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def stgcClusterStationName(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def mmClusterLayer(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def mmClusterIsOutlier(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def mmClusterEta(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def mmClusterPhi(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def mmClusterR(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def mmClusterZ(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def mmClusterResidualR(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def mmClusterResidualPhi(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def mmClusterStationEta(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def mmClusterStationPhi(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def mmClusterStationName(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
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
