from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr22

_method_map = {
    'pt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerTower_v2',
        'method_name': 'pt',
        'return_type': 'double',
    },
    'eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerTower_v2',
        'method_name': 'eta',
        'return_type': 'double',
    },
    'phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerTower_v2',
        'method_name': 'phi',
        'return_type': 'double',
    },
    'm': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerTower_v2',
        'method_name': 'm',
        'return_type': 'double',
    },
    'e': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerTower_v2',
        'method_name': 'e',
        'return_type': 'double',
    },
    'rapidity': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerTower_v2',
        'method_name': 'rapidity',
        'return_type': 'double',
    },
    'p4': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerTower_v2',
        'method_name': 'p4',
        'return_type': 'TLorentzVector',
    },
    'type': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerTower_v2',
        'method_name': 'type',
        'return_type': 'xAODType::ObjectType',
    },
    'coolId': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerTower_v2',
        'method_name': 'coolId',
        'return_type': 'unsigned int',
    },
    'layer': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerTower_v2',
        'method_name': 'layer',
        'return_type': 'int',
    },
    'sampling': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerTower_v2',
        'method_name': 'sampling',
        'return_type': 'int',
    },
    'lut_cp': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerTower_v2',
        'method_name': 'lut_cp',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned char>',
    },
    'lut_jep': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerTower_v2',
        'method_name': 'lut_jep',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned char>',
    },
    'correction': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerTower_v2',
        'method_name': 'correction',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<short>',
    },
    'correctionEnabled': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerTower_v2',
        'method_name': 'correctionEnabled',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned char>',
    },
    'bcidVec': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerTower_v2',
        'method_name': 'bcidVec',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned char>',
    },
    'adc': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerTower_v2',
        'method_name': 'adc',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned short>',
    },
    'bcidExt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerTower_v2',
        'method_name': 'bcidExt',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned char>',
    },
    'sat80Vec': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerTower_v2',
        'method_name': 'sat80Vec',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned char>',
    },
    'errorWord': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerTower_v2',
        'method_name': 'errorWord',
        'return_type': 'unsigned int',
    },
    'peak': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerTower_v2',
        'method_name': 'peak',
        'return_type': 'uint8_t',
    },
    'adcPeak': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerTower_v2',
        'method_name': 'adcPeak',
        'return_type': 'uint8_t',
    },
    'cpET': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerTower_v2',
        'method_name': 'cpET',
        'return_type': 'uint8_t',
    },
    'jepET': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerTower_v2',
        'method_name': 'jepET',
        'return_type': 'uint8_t',
    },
    'isCpSaturated': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerTower_v2',
        'method_name': 'isCpSaturated',
        'return_type': 'bool',
    },
    'isJepSaturated': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerTower_v2',
        'method_name': 'isJepSaturated',
        'return_type': 'bool',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerTower_v2',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerTower_v2',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerTower_v2',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerTower_v2',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerTower_v2',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerTower_v2',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerTower_v2',
        'method_name': 'trackIndices',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerTower_v2',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerTower_v2',
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
            'name': 'xAODTrigL1Calo/versions/TriggerTower_v2.h',
            'body_includes': ["xAODTrigL1Calo/versions/TriggerTower_v2.h"],
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
class TriggerTower_v2:
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

    def coolId(self) -> int:
        "A method"
        ...

    def layer(self) -> int:
        "A method"
        ...

    def sampling(self) -> int:
        "A method"
        ...

    def lut_cp(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def lut_jep(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def correction(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def correctionEnabled(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def bcidVec(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def adc(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def bcidExt(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def sat80Vec(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def errorWord(self) -> int:
        "A method"
        ...

    def peak(self) -> int:
        "A method"
        ...

    def adcPeak(self) -> int:
        "A method"
        ...

    def cpET(self) -> int:
        "A method"
        ...

    def jepET(self) -> int:
        "A method"
        ...

    def isCpSaturated(self) -> bool:
        "A method"
        ...

    def isJepSaturated(self) -> bool:
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
