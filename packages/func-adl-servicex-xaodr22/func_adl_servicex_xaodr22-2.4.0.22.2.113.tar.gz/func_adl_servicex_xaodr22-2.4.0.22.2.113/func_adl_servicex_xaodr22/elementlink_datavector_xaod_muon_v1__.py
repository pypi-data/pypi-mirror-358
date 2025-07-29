from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr22

_method_map = {
    'isValid': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'isValid',
        'return_type': 'bool',
    },
    'pt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'pt',
        'return_type': 'double',
        'deref_count': 2
    },
    'eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'eta',
        'return_type': 'double',
        'deref_count': 2
    },
    'phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'phi',
        'return_type': 'double',
        'deref_count': 2
    },
    'm': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'm',
        'return_type': 'double',
        'deref_count': 2
    },
    'e': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'e',
        'return_type': 'double',
        'deref_count': 2
    },
    'rapidity': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'rapidity',
        'return_type': 'double',
        'deref_count': 2
    },
    'p4': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'p4',
        'return_type': 'TLorentzVector',
        'deref_count': 2
    },
    'type': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'type',
        'return_type': 'xAODType::ObjectType',
        'deref_count': 2
    },
    'charge': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'charge',
        'return_type': 'float',
        'deref_count': 2
    },
    'author': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'author',
        'return_type': 'xAOD::Muon_v1::Author',
        'deref_count': 2
    },
    'isAuthor': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'isAuthor',
        'return_type': 'bool',
        'deref_count': 2
    },
    'allAuthors': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'allAuthors',
        'return_type': 'uint16_t',
        'deref_count': 2
    },
    'muonType': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'muonType',
        'return_type': 'xAOD::Muon_v1::MuonType',
        'deref_count': 2
    },
    'summaryValue': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'summaryValue',
        'return_type': 'bool',
        'deref_count': 2
    },
    'floatSummaryValue': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'floatSummaryValue',
        'return_type': 'float',
        'deref_count': 2
    },
    'uint8SummaryValue': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'uint8SummaryValue',
        'return_type': 'uint8_t',
        'deref_count': 2
    },
    'uint8MuonSummaryValue': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'uint8MuonSummaryValue',
        'return_type': 'float',
        'deref_count': 2
    },
    'parameter': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'parameter',
        'return_type': 'bool',
        'deref_count': 2
    },
    'floatParameter': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'floatParameter',
        'return_type': 'float',
        'deref_count': 2
    },
    'intParameter': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'intParameter',
        'return_type': 'int',
        'deref_count': 2
    },
    'quality': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'quality',
        'return_type': 'xAOD::Muon_v1::Quality',
        'deref_count': 2
    },
    'passesIDCuts': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'passesIDCuts',
        'return_type': 'bool',
        'deref_count': 2
    },
    'passesHighPtCuts': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'passesHighPtCuts',
        'return_type': 'bool',
        'deref_count': 2
    },
    'isolation': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'isolation',
        'return_type': 'bool',
        'deref_count': 2
    },
    'isolationCaloCorrection': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'isolationCaloCorrection',
        'return_type': 'bool',
        'deref_count': 2
    },
    'setIsolationCaloCorrection': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'setIsolationCaloCorrection',
        'return_type': 'bool',
        'deref_count': 2
    },
    'isolationTrackCorrection': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'isolationTrackCorrection',
        'return_type': 'bool',
        'deref_count': 2
    },
    'setIsolationTrackCorrection': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'setIsolationTrackCorrection',
        'return_type': 'bool',
        'deref_count': 2
    },
    'setIsolationCorrectionBitset': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'setIsolationCorrectionBitset',
        'return_type': 'bool',
        'deref_count': 2
    },
    'primaryTrackParticleLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'primaryTrackParticleLink',
        'return_type': 'const ElementLink<DataVector<xAOD::TrackParticle_v1>>',
        'deref_count': 2
    },
    'primaryTrackParticle': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'primaryTrackParticle',
        'return_type': 'const xAOD::TrackParticle_v1 *',
        'deref_count': 2
    },
    'inDetTrackParticleLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'inDetTrackParticleLink',
        'return_type': 'const ElementLink<DataVector<xAOD::TrackParticle_v1>>',
        'deref_count': 2
    },
    'muonSpectrometerTrackParticleLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'muonSpectrometerTrackParticleLink',
        'return_type': 'const ElementLink<DataVector<xAOD::TrackParticle_v1>>',
        'deref_count': 2
    },
    'combinedTrackParticleLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'combinedTrackParticleLink',
        'return_type': 'const ElementLink<DataVector<xAOD::TrackParticle_v1>>',
        'deref_count': 2
    },
    'extrapolatedMuonSpectrometerTrackParticleLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'extrapolatedMuonSpectrometerTrackParticleLink',
        'return_type': 'const ElementLink<DataVector<xAOD::TrackParticle_v1>>',
        'deref_count': 2
    },
    'msOnlyExtrapolatedMuonSpectrometerTrackParticleLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'msOnlyExtrapolatedMuonSpectrometerTrackParticleLink',
        'return_type': 'const ElementLink<DataVector<xAOD::TrackParticle_v1>>',
        'deref_count': 2
    },
    'trackParticleLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'trackParticleLink',
        'return_type': 'const ElementLink<DataVector<xAOD::TrackParticle_v1>>',
        'deref_count': 2
    },
    'trackParticle': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'trackParticle',
        'return_type': 'const xAOD::TrackParticle_v1 *',
        'deref_count': 2
    },
    'clusterLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'clusterLink',
        'return_type': 'const ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'deref_count': 2
    },
    'cluster': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'cluster',
        'return_type': 'const xAOD::CaloCluster_v1 *',
        'deref_count': 2
    },
    'energyLossType': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'energyLossType',
        'return_type': 'xAOD::Muon_v1::EnergyLossType',
        'deref_count': 2
    },
    'muonSegmentLinks': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'muonSegmentLinks',
        'return_type_element': 'ElementLink<DataVector<xAOD::MuonSegment_v1>>',
        'return_type_collection': 'const vector<ElementLink<DataVector<xAOD::MuonSegment_v1>>>',
        'deref_count': 2
    },
    'nMuonSegments': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'nMuonSegments',
        'return_type': 'unsigned int',
        'deref_count': 2
    },
    'muonSegment': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'muonSegment',
        'return_type': 'const xAOD::MuonSegment_v1 *',
        'deref_count': 2
    },
    'muonSegmentLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'muonSegmentLink',
        'return_type': 'const ElementLink<DataVector<xAOD::MuonSegment_v1>>',
        'deref_count': 2
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'index',
        'return_type': 'unsigned int',
        'deref_count': 2
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
        'deref_count': 2
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
        'deref_count': 2
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'hasStore',
        'return_type': 'bool',
        'deref_count': 2
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
        'deref_count': 2
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
        'deref_count': 2
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'trackIndices',
        'return_type': 'bool',
        'deref_count': 2
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
        'method_name': 'auxdataConst',
        'return_type': 'U',
        'deref_count': 2
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::Muon_v1>>',
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
            'name': 'xAODMuon/versions/Muon_v1.h',
            'body_includes': ["xAODMuon/versions/Muon_v1.h"],
        })


        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODMuon',
            'link_libraries': ["xAODMuon"],
        })

        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class ElementLink_DataVector_xAOD_Muon_v1__:
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

    def charge(self) -> float:
        "A method"
        ...

    def author(self) -> func_adl_servicex_xaodr22.xAOD.muon_v1.Muon_v1.Author:
        "A method"
        ...

    def isAuthor(self, author: func_adl_servicex_xaodr22.xAOD.muon_v1.Muon_v1.Author) -> bool:
        "A method"
        ...

    def allAuthors(self) -> int:
        "A method"
        ...

    def muonType(self) -> func_adl_servicex_xaodr22.xAOD.muon_v1.Muon_v1.MuonType:
        "A method"
        ...

    def summaryValue(self, value: int, information: func_adl_servicex_xaodr22.xaod.xAOD.SummaryType) -> bool:
        "A method"
        ...

    def floatSummaryValue(self, information: func_adl_servicex_xaodr22.xaod.xAOD.SummaryType) -> float:
        "A method"
        ...

    def uint8SummaryValue(self, information: func_adl_servicex_xaodr22.xaod.xAOD.SummaryType) -> int:
        "A method"
        ...

    def uint8MuonSummaryValue(self, information: func_adl_servicex_xaodr22.xaod.xAOD.MuonSummaryType) -> float:
        "A method"
        ...

    def parameter(self, value: float, parameter: func_adl_servicex_xaodr22.xAOD.muon_v1.Muon_v1.ParamDef) -> bool:
        "A method"
        ...

    def floatParameter(self, parameter: func_adl_servicex_xaodr22.xAOD.muon_v1.Muon_v1.ParamDef) -> float:
        "A method"
        ...

    def intParameter(self, parameter: func_adl_servicex_xaodr22.xAOD.muon_v1.Muon_v1.ParamDef) -> int:
        "A method"
        ...

    def quality(self) -> func_adl_servicex_xaodr22.xAOD.muon_v1.Muon_v1.Quality:
        "A method"
        ...

    def passesIDCuts(self) -> bool:
        "A method"
        ...

    def passesHighPtCuts(self) -> bool:
        "A method"
        ...

    def isolation(self, value: float, information: func_adl_servicex_xaodr22.xAOD.iso.Iso.IsolationType) -> bool:
        "A method"
        ...

    def isolationCaloCorrection(self, value: float, flavour: func_adl_servicex_xaodr22.xAOD.iso.Iso.IsolationFlavour, type: func_adl_servicex_xaodr22.xAOD.iso.Iso.IsolationCaloCorrection, param: func_adl_servicex_xaodr22.xAOD.iso.Iso.IsolationCorrectionParameter) -> bool:
        "A method"
        ...

    def setIsolationCaloCorrection(self, value: float, flavour: func_adl_servicex_xaodr22.xAOD.iso.Iso.IsolationFlavour, type: func_adl_servicex_xaodr22.xAOD.iso.Iso.IsolationCaloCorrection, param: func_adl_servicex_xaodr22.xAOD.iso.Iso.IsolationCorrectionParameter) -> bool:
        "A method"
        ...

    def isolationTrackCorrection(self, value: float, flavour: func_adl_servicex_xaodr22.xAOD.iso.Iso.IsolationFlavour, type: func_adl_servicex_xaodr22.xAOD.iso.Iso.IsolationTrackCorrection) -> bool:
        "A method"
        ...

    def setIsolationTrackCorrection(self, value: float, flavour: func_adl_servicex_xaodr22.xAOD.iso.Iso.IsolationFlavour, type: func_adl_servicex_xaodr22.xAOD.iso.Iso.IsolationTrackCorrection) -> bool:
        "A method"
        ...

    def setIsolationCorrectionBitset(self, value: int, flavour: func_adl_servicex_xaodr22.xAOD.iso.Iso.IsolationFlavour) -> bool:
        "A method"
        ...

    def primaryTrackParticleLink(self) -> func_adl_servicex_xaodr22.elementlink_datavector_xaod_trackparticle_v1__.ElementLink_DataVector_xAOD_TrackParticle_v1__:
        "A method"
        ...

    def primaryTrackParticle(self) -> func_adl_servicex_xaodr22.xAOD.trackparticle_v1.TrackParticle_v1:
        "A method"
        ...

    def inDetTrackParticleLink(self) -> func_adl_servicex_xaodr22.elementlink_datavector_xaod_trackparticle_v1__.ElementLink_DataVector_xAOD_TrackParticle_v1__:
        "A method"
        ...

    def muonSpectrometerTrackParticleLink(self) -> func_adl_servicex_xaodr22.elementlink_datavector_xaod_trackparticle_v1__.ElementLink_DataVector_xAOD_TrackParticle_v1__:
        "A method"
        ...

    def combinedTrackParticleLink(self) -> func_adl_servicex_xaodr22.elementlink_datavector_xaod_trackparticle_v1__.ElementLink_DataVector_xAOD_TrackParticle_v1__:
        "A method"
        ...

    def extrapolatedMuonSpectrometerTrackParticleLink(self) -> func_adl_servicex_xaodr22.elementlink_datavector_xaod_trackparticle_v1__.ElementLink_DataVector_xAOD_TrackParticle_v1__:
        "A method"
        ...

    def msOnlyExtrapolatedMuonSpectrometerTrackParticleLink(self) -> func_adl_servicex_xaodr22.elementlink_datavector_xaod_trackparticle_v1__.ElementLink_DataVector_xAOD_TrackParticle_v1__:
        "A method"
        ...

    def trackParticleLink(self, type: func_adl_servicex_xaodr22.xAOD.muon_v1.Muon_v1.TrackParticleType) -> func_adl_servicex_xaodr22.elementlink_datavector_xaod_trackparticle_v1__.ElementLink_DataVector_xAOD_TrackParticle_v1__:
        "A method"
        ...

    def trackParticle(self, type: func_adl_servicex_xaodr22.xAOD.muon_v1.Muon_v1.TrackParticleType) -> func_adl_servicex_xaodr22.xAOD.trackparticle_v1.TrackParticle_v1:
        "A method"
        ...

    def clusterLink(self) -> func_adl_servicex_xaodr22.elementlink_datavector_xaod_calocluster_v1__.ElementLink_DataVector_xAOD_CaloCluster_v1__:
        "A method"
        ...

    def cluster(self) -> func_adl_servicex_xaodr22.xAOD.calocluster_v1.CaloCluster_v1:
        "A method"
        ...

    def energyLossType(self) -> func_adl_servicex_xaodr22.xAOD.muon_v1.Muon_v1.EnergyLossType:
        "A method"
        ...

    def muonSegmentLinks(self) -> func_adl_servicex_xaodr22.vector_elementlink_datavector_xaod_muonsegment_v1___.vector_ElementLink_DataVector_xAOD_MuonSegment_v1___:
        "A method"
        ...

    def nMuonSegments(self) -> int:
        "A method"
        ...

    def muonSegment(self, i: int) -> func_adl_servicex_xaodr22.xAOD.muonsegment_v1.MuonSegment_v1:
        "A method"
        ...

    def muonSegmentLink(self, i: int) -> func_adl_servicex_xaodr22.elementlink_datavector_xaod_muonsegment_v1__.ElementLink_DataVector_xAOD_MuonSegment_v1__:
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
