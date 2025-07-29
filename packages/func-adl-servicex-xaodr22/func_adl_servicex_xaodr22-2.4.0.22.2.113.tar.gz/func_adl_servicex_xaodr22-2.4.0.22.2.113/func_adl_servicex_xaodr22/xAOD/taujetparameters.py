from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr22

_method_map = {
}

_enum_function_map = {      
}

_defined_enums = {
    'TauID':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.TauJetParameters',
            'name': 'TauID',
            'values': [
                'EleMatchLikelihoodScore',
                'Likelihood',
                'BDTJetScore',
                'BDTEleScore',
                'SafeLikelihood',
                'BDTJetScoreSigTrans',
                'PanTauScore',
                'RNNJetScore',
                'RNNJetScoreSigTrans',
                'RNNEleScore',
                'RNNEleScoreSigTrans',
            ],
        },
    'VetoFlags':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.TauJetParameters',
            'name': 'VetoFlags',
            'values': [
                'ElectronFlag',
                'EgammaFlag',
                'MuonFlag',
            ],
        },
    'IsTauFlag':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.TauJetParameters',
            'name': 'IsTauFlag',
            'values': [
                'PassEleOLR',
                'MuonVeto',
                'EleRNNLoose',
                'EleRNNMedium',
                'EleRNNTight',
                'JetBDTSigVeryLoose',
                'JetBDTSigLoose',
                'JetBDTSigMedium',
                'JetBDTSigTight',
                'EleBDTLoose',
                'EleBDTMedium',
                'EleBDTTight',
                'JetBDTBkgLoose',
                'JetBDTBkgMedium',
                'JetBDTBkgTight',
                'JetRNNSigVeryLoose',
                'JetRNNSigLoose',
                'JetRNNSigMedium',
                'JetRNNSigTight',
            ],
        },
    'Detail':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.TauJetParameters',
            'name': 'Detail',
            'values': [
                'ipZ0SinThetaSigLeadTrk',
                'etOverPtLeadTrk',
                'leadTrkPt',
                'ipSigLeadTrk',
                'massTrkSys',
                'trkWidth2',
                'trFlightPathSig',
                'numCells',
                'numTopoClusters',
                'numEffTopoClusters',
                'topoInvMass',
                'effTopoInvMass',
                'topoMeanDeltaR',
                'effTopoMeanDeltaR',
                'EMRadius',
                'hadRadius',
                'etEMAtEMScale',
                'etHadAtEMScale',
                'isolFrac',
                'centFrac',
                'stripWidth2',
                'nStrip',
                'trkAvgDist',
                'trkRmsDist',
                'lead2ClusterEOverAllClusterE',
                'lead3ClusterEOverAllClusterE',
                'caloIso',
                'caloIsoCorrected',
                'dRmax',
                'secMaxStripEt',
                'sumEMCellEtOverLeadTrkPt',
                'hadLeakEt',
                'cellBasedEnergyRing1',
                'cellBasedEnergyRing2',
                'cellBasedEnergyRing3',
                'cellBasedEnergyRing4',
                'cellBasedEnergyRing5',
                'cellBasedEnergyRing6',
                'cellBasedEnergyRing7',
                'TRT_NHT_OVER_NLT',
                'TauJetVtxFraction',
                'nCharged',
                'PSSFraction',
                'ChPiEMEOverCaloEME',
                'EMPOverTrkSysP',
                'TESOffset',
                'TESCalibConstant',
                'centFracCorrected',
                'etOverPtLeadTrkCorrected',
                'innerTrkAvgDist',
                'innerTrkAvgDistCorrected',
                'SumPtTrkFrac',
                'SumPtTrkFracCorrected',
                'mEflowApprox',
                'ptRatioEflowApprox',
                'ipSigLeadTrkCorrected',
                'trFlightPathSigCorrected',
                'massTrkSysCorrected',
                'dRmaxCorrected',
                'ChPiEMEOverCaloEMECorrected',
                'EMPOverTrkSysPCorrected',
                'ptRatioEflowApproxCorrected',
                'mEflowApproxCorrected',
                'ClustersMeanCenterLambda',
                'ClustersMeanEMProbability',
                'ClustersMeanFirstEngDens',
                'ClustersMeanSecondLambda',
                'ClustersMeanPresamplerFrac',
                'GhostMuonSegmentCount',
                'PFOEngRelDiff',
                'LC_pantau_interpolPt',
                'electronLink',
                'nChargedTracks',
                'nIsolatedTracks',
                'nModifiedIsolationTracks',
                'nAllTracks',
                'nLargeRadiusTracks',
            ],
        },
    'TauCalibType':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.TauJetParameters',
            'name': 'TauCalibType',
            'values': [
                'JetSeed',
                'DetectorAxis',
                'IntermediateAxis',
                'TauEnergyScale',
                'TauEtaCalib',
                'PanTauCellBasedProto',
                'PanTauCellBased',
                'TrigCaloOnly',
                'FinalCalib',
            ],
        },
    'PanTauDetails':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.TauJetParameters',
            'name': 'PanTauDetails',
            'values': [
                'PanTau_isPanTauCandidate',
                'PanTau_DecayModeProto',
                'PanTau_DecayMode',
                'PanTau_BDTValue_1p0n_vs_1p1n',
                'PanTau_BDTValue_1p1n_vs_1pXn',
                'PanTau_BDTValue_3p0n_vs_3pXn',
                'PanTau_BDTVar_Basic_NNeutralConsts',
                'PanTau_BDTVar_Charged_JetMoment_EtDRxTotalEt',
                'PanTau_BDTVar_Charged_StdDev_Et_WrtEtAllConsts',
                'PanTau_BDTVar_Neutral_HLV_SumM',
                'PanTau_BDTVar_Neutral_PID_BDTValues_BDTSort_1',
                'PanTau_BDTVar_Neutral_PID_BDTValues_BDTSort_2',
                'PanTau_BDTVar_Neutral_Ratio_1stBDTEtOverEtAllConsts',
                'PanTau_BDTVar_Neutral_Ratio_EtOverEtAllConsts',
                'PanTau_BDTVar_Neutral_Shots_NPhotonsInSeed',
                'PanTau_BDTVar_Combined_DeltaR1stNeutralTo1stCharged',
                'PanTau_DecayModeExtended',
                'PanTau_BDTVar_Charged_HLV_SumM',
            ],
        },
    'DecayMode':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.TauJetParameters',
            'name': 'DecayMode',
            'values': [
                'Mode_1p0n',
                'Mode_1p1n',
                'Mode_1pXn',
                'Mode_3p0n',
                'Mode_3pXn',
                'Mode_Other',
                'Mode_NotSet',
                'Mode_Error',
            ],
        },
    'TauTrackFlag':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.TauJetParameters',
            'name': 'TauTrackFlag',
            'values': [
                'isConversionOld',
                'failTrackFilter',
                'coreTrack',
                'wideTrack',
                'passTrkSelector',
                'classifiedCharged',
                'classifiedIsolation',
                'classifiedConversion',
                'classifiedFake',
                'unclassified',
                'passTrkSelectionTight',
                'modifiedIsolationTrack',
                'LargeRadiusTrack',
            ],
        },
    'TrackDetail':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.TauJetParameters',
            'name': 'TrackDetail',
            'values': [
                'CaloSamplingEtaEM',
                'CaloSamplingEtaHad',
                'CaloSamplingPhiEM',
                'CaloSamplingPhiHad',
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


        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class TauJetParameters:
    "A class"

    class TauID(Enum):
        EleMatchLikelihoodScore = 1
        Likelihood = 2
        BDTJetScore = 15
        BDTEleScore = 16
        SafeLikelihood = 17
        BDTJetScoreSigTrans = 18
        PanTauScore = 20
        RNNJetScore = 21
        RNNJetScoreSigTrans = 22
        RNNEleScore = 23
        RNNEleScoreSigTrans = 24

    class VetoFlags(Enum):
        ElectronFlag = 0
        EgammaFlag = 1
        MuonFlag = 2

    class IsTauFlag(Enum):
        PassEleOLR = 0
        MuonVeto = 4
        EleRNNLoose = 15
        EleRNNMedium = 16
        EleRNNTight = 17
        JetBDTSigVeryLoose = 18
        JetBDTSigLoose = 19
        JetBDTSigMedium = 20
        JetBDTSigTight = 21
        EleBDTLoose = 22
        EleBDTMedium = 23
        EleBDTTight = 24
        JetBDTBkgLoose = 25
        JetBDTBkgMedium = 26
        JetBDTBkgTight = 27
        JetRNNSigVeryLoose = 28
        JetRNNSigLoose = 29
        JetRNNSigMedium = 30
        JetRNNSigTight = 31

    class Detail(Enum):
        ipZ0SinThetaSigLeadTrk = 0
        etOverPtLeadTrk = 1
        leadTrkPt = 2
        ipSigLeadTrk = 3
        massTrkSys = 4
        trkWidth2 = 5
        trFlightPathSig = 6
        numCells = 12
        numTopoClusters = 13
        numEffTopoClusters = 14
        topoInvMass = 15
        effTopoInvMass = 16
        topoMeanDeltaR = 17
        effTopoMeanDeltaR = 18
        EMRadius = 19
        hadRadius = 20
        etEMAtEMScale = 21
        etHadAtEMScale = 22
        isolFrac = 23
        centFrac = 24
        stripWidth2 = 25
        nStrip = 26
        trkAvgDist = 31
        trkRmsDist = 32
        lead2ClusterEOverAllClusterE = 33
        lead3ClusterEOverAllClusterE = 34
        caloIso = 35
        caloIsoCorrected = 36
        dRmax = 37
        secMaxStripEt = 38
        sumEMCellEtOverLeadTrkPt = 39
        hadLeakEt = 40
        cellBasedEnergyRing1 = 43
        cellBasedEnergyRing2 = 44
        cellBasedEnergyRing3 = 45
        cellBasedEnergyRing4 = 46
        cellBasedEnergyRing5 = 47
        cellBasedEnergyRing6 = 48
        cellBasedEnergyRing7 = 49
        TRT_NHT_OVER_NLT = 50
        TauJetVtxFraction = 51
        nCharged = 53
        PSSFraction = 60
        ChPiEMEOverCaloEME = 61
        EMPOverTrkSysP = 62
        TESOffset = 63
        TESCalibConstant = 64
        centFracCorrected = 65
        etOverPtLeadTrkCorrected = 66
        innerTrkAvgDist = 67
        innerTrkAvgDistCorrected = 68
        SumPtTrkFrac = 69
        SumPtTrkFracCorrected = 70
        mEflowApprox = 71
        ptRatioEflowApprox = 72
        ipSigLeadTrkCorrected = 73
        trFlightPathSigCorrected = 74
        massTrkSysCorrected = 75
        dRmaxCorrected = 76
        ChPiEMEOverCaloEMECorrected = 77
        EMPOverTrkSysPCorrected = 78
        ptRatioEflowApproxCorrected = 79
        mEflowApproxCorrected = 80
        ClustersMeanCenterLambda = 100
        ClustersMeanEMProbability = 101
        ClustersMeanFirstEngDens = 102
        ClustersMeanSecondLambda = 103
        ClustersMeanPresamplerFrac = 104
        GhostMuonSegmentCount = 105
        PFOEngRelDiff = 106
        LC_pantau_interpolPt = 107
        electronLink = 108
        nChargedTracks = 109
        nIsolatedTracks = 110
        nModifiedIsolationTracks = 111
        nAllTracks = 112
        nLargeRadiusTracks = 113

    class TauCalibType(Enum):
        JetSeed = 0
        DetectorAxis = 1
        IntermediateAxis = 2
        TauEnergyScale = 3
        TauEtaCalib = 4
        PanTauCellBasedProto = 7
        PanTauCellBased = 8
        TrigCaloOnly = 9
        FinalCalib = 10

    class PanTauDetails(Enum):
        PanTau_isPanTauCandidate = 0
        PanTau_DecayModeProto = 1
        PanTau_DecayMode = 2
        PanTau_BDTValue_1p0n_vs_1p1n = 3
        PanTau_BDTValue_1p1n_vs_1pXn = 4
        PanTau_BDTValue_3p0n_vs_3pXn = 5
        PanTau_BDTVar_Basic_NNeutralConsts = 6
        PanTau_BDTVar_Charged_JetMoment_EtDRxTotalEt = 7
        PanTau_BDTVar_Charged_StdDev_Et_WrtEtAllConsts = 8
        PanTau_BDTVar_Neutral_HLV_SumM = 9
        PanTau_BDTVar_Neutral_PID_BDTValues_BDTSort_1 = 10
        PanTau_BDTVar_Neutral_PID_BDTValues_BDTSort_2 = 11
        PanTau_BDTVar_Neutral_Ratio_1stBDTEtOverEtAllConsts = 12
        PanTau_BDTVar_Neutral_Ratio_EtOverEtAllConsts = 13
        PanTau_BDTVar_Neutral_Shots_NPhotonsInSeed = 14
        PanTau_BDTVar_Combined_DeltaR1stNeutralTo1stCharged = 15
        PanTau_DecayModeExtended = 16
        PanTau_BDTVar_Charged_HLV_SumM = 32

    class DecayMode(Enum):
        Mode_1p0n = 0
        Mode_1p1n = 1
        Mode_1pXn = 2
        Mode_3p0n = 3
        Mode_3pXn = 4
        Mode_Other = 5
        Mode_NotSet = 6
        Mode_Error = 7

    class TauTrackFlag(Enum):
        isConversionOld = 0
        failTrackFilter = 1
        coreTrack = 2
        wideTrack = 3
        passTrkSelector = 4
        classifiedCharged = 5
        classifiedIsolation = 6
        classifiedConversion = 7
        classifiedFake = 8
        unclassified = 9
        passTrkSelectionTight = 10
        modifiedIsolationTrack = 11
        LargeRadiusTrack = 12

    class TrackDetail(Enum):
        CaloSamplingEtaEM = 0
        CaloSamplingEtaHad = 1
        CaloSamplingPhiEM = 2
        CaloSamplingPhiHad = 3

