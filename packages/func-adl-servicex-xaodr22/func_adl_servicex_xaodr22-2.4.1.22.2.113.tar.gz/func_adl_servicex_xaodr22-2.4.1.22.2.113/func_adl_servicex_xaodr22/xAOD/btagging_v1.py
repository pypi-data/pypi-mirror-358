from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr22

_method_map = {
    'SV0_significance3D': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'SV0_significance3D',
        'return_type': 'float',
    },
    'SV0_TrackParticleLinks': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'SV0_TrackParticleLinks',
        'return_type_element': 'ElementLink<DataVector<xAOD::TrackParticle_v1>>',
        'return_type_collection': 'const vector<ElementLink<DataVector<xAOD::TrackParticle_v1>>>',
    },
    'SV0_TrackParticle': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'SV0_TrackParticle',
        'return_type': 'const xAOD::TrackParticle_v1 *',
    },
    'nSV0_TrackParticles': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'nSV0_TrackParticles',
        'return_type': 'unsigned int',
    },
    'SV1_pb': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'SV1_pb',
        'return_type': 'float',
    },
    'SV1_pc': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'SV1_pc',
        'return_type': 'float',
    },
    'SV1_pu': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'SV1_pu',
        'return_type': 'float',
    },
    'SV1_loglikelihoodratio': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'SV1_loglikelihoodratio',
        'return_type': 'double',
    },
    'SV1_TrackParticleLinks': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'SV1_TrackParticleLinks',
        'return_type_element': 'ElementLink<DataVector<xAOD::TrackParticle_v1>>',
        'return_type_collection': 'const vector<ElementLink<DataVector<xAOD::TrackParticle_v1>>>',
    },
    'SV1_TrackParticle': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'SV1_TrackParticle',
        'return_type': 'const xAOD::TrackParticle_v1 *',
    },
    'nSV1_TrackParticles': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'nSV1_TrackParticles',
        'return_type': 'unsigned int',
    },
    'IP2D_pb': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'IP2D_pb',
        'return_type': 'float',
    },
    'IP2D_pc': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'IP2D_pc',
        'return_type': 'float',
    },
    'IP2D_pu': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'IP2D_pu',
        'return_type': 'float',
    },
    'IP2D_loglikelihoodratio': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'IP2D_loglikelihoodratio',
        'return_type': 'float',
    },
    'IP2D_TrackParticleLinks': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'IP2D_TrackParticleLinks',
        'return_type_element': 'ElementLink<DataVector<xAOD::TrackParticle_v1>>',
        'return_type_collection': 'const vector<ElementLink<DataVector<xAOD::TrackParticle_v1>>>',
    },
    'IP2D_TrackParticle': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'IP2D_TrackParticle',
        'return_type': 'const xAOD::TrackParticle_v1 *',
    },
    'nIP2D_TrackParticles': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'nIP2D_TrackParticles',
        'return_type': 'unsigned int',
    },
    'IP3D_pb': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'IP3D_pb',
        'return_type': 'float',
    },
    'IP3D_pc': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'IP3D_pc',
        'return_type': 'float',
    },
    'IP3D_pu': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'IP3D_pu',
        'return_type': 'float',
    },
    'IP3D_loglikelihoodratio': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'IP3D_loglikelihoodratio',
        'return_type': 'float',
    },
    'IP3D_TrackParticleLinks': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'IP3D_TrackParticleLinks',
        'return_type_element': 'ElementLink<DataVector<xAOD::TrackParticle_v1>>',
        'return_type_collection': 'const vector<ElementLink<DataVector<xAOD::TrackParticle_v1>>>',
    },
    'IP3D_TrackParticle': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'IP3D_TrackParticle',
        'return_type': 'const xAOD::TrackParticle_v1 *',
    },
    'nIP3D_TrackParticles': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'nIP3D_TrackParticles',
        'return_type': 'unsigned int',
    },
    'SV1plusIP3D_discriminant': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'SV1plusIP3D_discriminant',
        'return_type': 'float',
    },
    'JetFitter_pb': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'JetFitter_pb',
        'return_type': 'float',
    },
    'JetFitter_pc': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'JetFitter_pc',
        'return_type': 'float',
    },
    'JetFitter_pu': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'JetFitter_pu',
        'return_type': 'float',
    },
    'JetFitter_loglikelihoodratio': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'JetFitter_loglikelihoodratio',
        'return_type': 'float',
    },
    'MV1_discriminant': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'MV1_discriminant',
        'return_type': 'float',
    },
    'loglikelihoodratio': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'loglikelihoodratio',
        'return_type': 'bool',
    },
    'MVx_discriminant': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'MVx_discriminant',
        'return_type': 'bool',
    },
    'pu': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'pu',
        'return_type': 'bool',
    },
    'pb': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'pb',
        'return_type': 'bool',
    },
    'pc': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'pc',
        'return_type': 'bool',
    },
    'calcLLR': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'calcLLR',
        'return_type': 'float',
    },
    'taggerInfo': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'taggerInfo',
        'return_type': 'bool',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'trackIndices',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::BTagging_v1',
        'method_name': 'isAvailable',
        'return_type': 'bool',
    },
}

_enum_function_map = {
    'taggerInfo': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD',
            'name': 'BTagInfo',
            'values': [
                'SV0_NGTinJet',
                'SV0_NGTinSvx',
                'SV0_N2Tpair',
                'SV0_masssvx',
                'SV0_efracsvx',
                'SV0_normdist',
                'SV1_NGTinJet',
                'SV1_NGTinSvx',
                'SV1_N2Tpair',
                'SV1_masssvx',
                'SV1_efracsvx',
                'SV1_normdist',
                'JetFitter_nVTX',
                'JetFitter_nSingleTracks',
                'JetFitter_nTracksAtVtx',
                'JetFitter_mass',
                'JetFitter_energyFraction',
                'JetFitter_significance3d',
                'JetFitter_deltaeta',
                'JetFitter_deltaphi',
                'JetFitter_N2Tpair',
                'IP2D_ntrk',
                'IP2D_gradeOfTracks',
                'IP2D_flagFromV0ofTracks',
                'IP2D_valD0wrtPVofTracks',
                'IP2D_sigD0wrtPVofTracks',
                'IP2D_weightBofTracks',
                'IP2D_weightUofTracks',
                'IP2D_weightCofTracks',
                'IP3D_ntrk',
                'IP3D_gradeOfTracks',
                'IP3D_flagFromV0ofTracks',
                'IP3D_valD0wrtPVofTracks',
                'IP3D_sigD0wrtPVofTracks',
                'IP3D_valZ0wrtPVofTracks',
                'IP3D_sigZ0wrtPVofTracks',
                'IP3D_weightBofTracks',
                'IP3D_weightUofTracks',
                'IP3D_weightCofTracks',
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
            'name': 'xAODBTagging/versions/BTagging_v1.h',
            'body_includes': ["xAODBTagging/versions/BTagging_v1.h"],
        })


        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODBTagging',
            'link_libraries': ["xAODBTagging"],
        })

        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class BTagging_v1:
    "A class"


    def SV0_significance3D(self) -> float:
        "A method"
        ...

    def SV0_TrackParticleLinks(self) -> func_adl_servicex_xaodr22.vector_elementlink_datavector_xaod_trackparticle_v1___.vector_ElementLink_DataVector_xAOD_TrackParticle_v1___:
        "A method"
        ...

    def SV0_TrackParticle(self, i: int) -> func_adl_servicex_xaodr22.xAOD.trackparticle_v1.TrackParticle_v1:
        "A method"
        ...

    def nSV0_TrackParticles(self) -> int:
        "A method"
        ...

    def SV1_pb(self) -> float:
        "A method"
        ...

    def SV1_pc(self) -> float:
        "A method"
        ...

    def SV1_pu(self) -> float:
        "A method"
        ...

    def SV1_loglikelihoodratio(self) -> float:
        "A method"
        ...

    def SV1_TrackParticleLinks(self) -> func_adl_servicex_xaodr22.vector_elementlink_datavector_xaod_trackparticle_v1___.vector_ElementLink_DataVector_xAOD_TrackParticle_v1___:
        "A method"
        ...

    def SV1_TrackParticle(self, i: int) -> func_adl_servicex_xaodr22.xAOD.trackparticle_v1.TrackParticle_v1:
        "A method"
        ...

    def nSV1_TrackParticles(self) -> int:
        "A method"
        ...

    def IP2D_pb(self) -> float:
        "A method"
        ...

    def IP2D_pc(self) -> float:
        "A method"
        ...

    def IP2D_pu(self) -> float:
        "A method"
        ...

    def IP2D_loglikelihoodratio(self) -> float:
        "A method"
        ...

    def IP2D_TrackParticleLinks(self) -> func_adl_servicex_xaodr22.vector_elementlink_datavector_xaod_trackparticle_v1___.vector_ElementLink_DataVector_xAOD_TrackParticle_v1___:
        "A method"
        ...

    def IP2D_TrackParticle(self, i: int) -> func_adl_servicex_xaodr22.xAOD.trackparticle_v1.TrackParticle_v1:
        "A method"
        ...

    def nIP2D_TrackParticles(self) -> int:
        "A method"
        ...

    def IP3D_pb(self) -> float:
        "A method"
        ...

    def IP3D_pc(self) -> float:
        "A method"
        ...

    def IP3D_pu(self) -> float:
        "A method"
        ...

    def IP3D_loglikelihoodratio(self) -> float:
        "A method"
        ...

    def IP3D_TrackParticleLinks(self) -> func_adl_servicex_xaodr22.vector_elementlink_datavector_xaod_trackparticle_v1___.vector_ElementLink_DataVector_xAOD_TrackParticle_v1___:
        "A method"
        ...

    def IP3D_TrackParticle(self, i: int) -> func_adl_servicex_xaodr22.xAOD.trackparticle_v1.TrackParticle_v1:
        "A method"
        ...

    def nIP3D_TrackParticles(self) -> int:
        "A method"
        ...

    def SV1plusIP3D_discriminant(self) -> float:
        "A method"
        ...

    def JetFitter_pb(self) -> float:
        "A method"
        ...

    def JetFitter_pc(self) -> float:
        "A method"
        ...

    def JetFitter_pu(self) -> float:
        "A method"
        ...

    def JetFitter_loglikelihoodratio(self) -> float:
        "A method"
        ...

    def MV1_discriminant(self) -> float:
        "A method"
        ...

    def loglikelihoodratio(self, taggername: str, value: float, signal: str, bckgd: str) -> bool:
        "A method"
        ...

    def MVx_discriminant(self, taggername: str, value: float) -> bool:
        "A method"
        ...

    def pu(self, taggername: str, value: float) -> bool:
        "A method"
        ...

    def pb(self, taggername: str, value: float) -> bool:
        "A method"
        ...

    def pc(self, taggername: str, value: float) -> bool:
        "A method"
        ...

    def calcLLR(self, num: float, den: float) -> float:
        "A method"
        ...

    def taggerInfo(self, value: int, info: func_adl_servicex_xaodr22.xaod.xAOD.BTagInfo) -> bool:
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
