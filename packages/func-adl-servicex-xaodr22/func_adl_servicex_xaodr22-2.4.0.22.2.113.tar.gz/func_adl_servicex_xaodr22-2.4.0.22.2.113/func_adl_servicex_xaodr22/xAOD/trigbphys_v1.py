from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr22

_method_map = {
    'roiId': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigBphys_v1',
        'method_name': 'roiId',
        'return_type': 'unsigned int',
    },
    'particleType': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigBphys_v1',
        'method_name': 'particleType',
        'return_type': 'xAOD::TrigBphys_v1::pType',
    },
    'level': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigBphys_v1',
        'method_name': 'level',
        'return_type': 'xAOD::TrigBphys_v1::levelType',
    },
    'eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigBphys_v1',
        'method_name': 'eta',
        'return_type': 'float',
    },
    'phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigBphys_v1',
        'method_name': 'phi',
        'return_type': 'float',
    },
    'pt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigBphys_v1',
        'method_name': 'pt',
        'return_type': 'float',
    },
    'mass': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigBphys_v1',
        'method_name': 'mass',
        'return_type': 'float',
    },
    'fitmass': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigBphys_v1',
        'method_name': 'fitmass',
        'return_type': 'float',
    },
    'fitchi2': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigBphys_v1',
        'method_name': 'fitchi2',
        'return_type': 'float',
    },
    'fitndof': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigBphys_v1',
        'method_name': 'fitndof',
        'return_type': 'int',
    },
    'fitx': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigBphys_v1',
        'method_name': 'fitx',
        'return_type': 'float',
    },
    'fity': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigBphys_v1',
        'method_name': 'fity',
        'return_type': 'float',
    },
    'fitz': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigBphys_v1',
        'method_name': 'fitz',
        'return_type': 'float',
    },
    'lxy': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigBphys_v1',
        'method_name': 'lxy',
        'return_type': 'float',
    },
    'lxyError': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigBphys_v1',
        'method_name': 'lxyError',
        'return_type': 'float',
    },
    'tau': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigBphys_v1',
        'method_name': 'tau',
        'return_type': 'float',
    },
    'tauError': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigBphys_v1',
        'method_name': 'tauError',
        'return_type': 'float',
    },
    'fitmassError': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigBphys_v1',
        'method_name': 'fitmassError',
        'return_type': 'float',
    },
    'secondaryDecay': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigBphys_v1',
        'method_name': 'secondaryDecay',
        'return_type': 'const xAOD::TrigBphys_v1 *',
    },
    'secondaryDecayLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigBphys_v1',
        'method_name': 'secondaryDecayLink',
        'return_type': 'const ElementLink<DataVector<xAOD::TrigBphys_v1>>',
    },
    'trackParticleLinks': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigBphys_v1',
        'method_name': 'trackParticleLinks',
        'return_type_element': 'ElementLink<DataVector<xAOD::TrackParticle_v1>>',
        'return_type_collection': 'const vector<ElementLink<DataVector<xAOD::TrackParticle_v1>>>',
    },
    'nTrackParticles': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigBphys_v1',
        'method_name': 'nTrackParticles',
        'return_type': 'unsigned int',
    },
    'trackParticle': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigBphys_v1',
        'method_name': 'trackParticle',
        'return_type': 'const xAOD::TrackParticle_v1 *',
    },
    'vecRoiIds': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigBphys_v1',
        'method_name': 'vecRoiIds',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned int>',
    },
    'nVecRoiIds': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigBphys_v1',
        'method_name': 'nVecRoiIds',
        'return_type': 'unsigned int',
    },
    'vecRoiId': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigBphys_v1',
        'method_name': 'vecRoiId',
        'return_type': 'unsigned int',
    },
    'lowerChain': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigBphys_v1',
        'method_name': 'lowerChain',
        'return_type': 'const xAOD::TrigBphys_v1 *',
    },
    'lowerChainLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigBphys_v1',
        'method_name': 'lowerChainLink',
        'return_type': 'const ElementLink<DataVector<xAOD::TrigBphys_v1>>',
    },
    'particleLinks': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigBphys_v1',
        'method_name': 'particleLinks',
        'return_type_element': 'ElementLink<DataVector<xAOD::IParticle>>',
        'return_type_collection': 'const vector<ElementLink<DataVector<xAOD::IParticle>>>',
    },
    'nParticles': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigBphys_v1',
        'method_name': 'nParticles',
        'return_type': 'unsigned int',
    },
    'particle': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigBphys_v1',
        'method_name': 'particle',
        'return_type': 'const xAOD::IParticle *',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigBphys_v1',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigBphys_v1',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigBphys_v1',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigBphys_v1',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigBphys_v1',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigBphys_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigBphys_v1',
        'method_name': 'trackIndices',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigBphys_v1',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigBphys_v1',
        'method_name': 'isAvailable',
        'return_type': 'bool',
    },
}

_enum_function_map = {
    'particleType': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.TrigBphys_v1',
            'name': 'pType',
            'values': [
                'PHIKK',
                'DSPHIPI',
                'BMUMU',
                'BMUMUX',
                'JPSIEE',
                'JPSIMUMU',
                'MULTIMU',
                'BKMUMU',
                'BDKSTMUMU',
                'BSPHIMUMU',
                'LBLMUMU',
                'BCDSMUMU',
                'LAMBDAPIP',
                'BCDPMUMU',
                'BCDSTMUMU',
                'OMEGALAMK',
                'XILAMPI',
                'DSTDZPI',
                'DZMUKX',
                'DZKPI',
                'DPKPIPI',
                'BCPIMUMU',
                'LBPQMUMU',
                'B2D0MUX',
                'BD2DMMUX',
                'BD2DSTMUX',
                'BS2DSMUX',
                'LB2LCMUX',
                'UNKNOWNPTYPE',
            ],
        },
    ],
    'level': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.TrigBphys_v1',
            'name': 'levelType',
            'values': [
                'UNKOWNLEVEL',
                'L2',
                'EF',
                'HLT',
                'LASTLEVEL',
            ],
        },
    ],      
}

_defined_enums = {
    'pType':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.TrigBphys_v1',
            'name': 'pType',
            'values': [
                'PHIKK',
                'DSPHIPI',
                'BMUMU',
                'BMUMUX',
                'JPSIEE',
                'JPSIMUMU',
                'MULTIMU',
                'BKMUMU',
                'BDKSTMUMU',
                'BSPHIMUMU',
                'LBLMUMU',
                'BCDSMUMU',
                'LAMBDAPIP',
                'BCDPMUMU',
                'BCDSTMUMU',
                'OMEGALAMK',
                'XILAMPI',
                'DSTDZPI',
                'DZMUKX',
                'DZKPI',
                'DPKPIPI',
                'BCPIMUMU',
                'LBPQMUMU',
                'B2D0MUX',
                'BD2DMMUX',
                'BD2DSTMUX',
                'BS2DSMUX',
                'LB2LCMUX',
                'UNKNOWNPTYPE',
            ],
        },
    'levelType':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.TrigBphys_v1',
            'name': 'levelType',
            'values': [
                'UNKOWNLEVEL',
                'L2',
                'EF',
                'HLT',
                'LASTLEVEL',
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
            'name': 'xAODTrigBphys/versions/TrigBphys_v1.h',
            'body_includes': ["xAODTrigBphys/versions/TrigBphys_v1.h"],
        })


        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODTrigBphys',
            'link_libraries': ["xAODTrigBphys"],
        })

        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class TrigBphys_v1:
    "A class"

    class pType(Enum):
        PHIKK = 0
        DSPHIPI = 1
        BMUMU = 2
        BMUMUX = 3
        JPSIEE = 4
        JPSIMUMU = 5
        MULTIMU = 6
        BKMUMU = 7
        BDKSTMUMU = 8
        BSPHIMUMU = 9
        LBLMUMU = 10
        BCDSMUMU = 11
        LAMBDAPIP = 12
        BCDPMUMU = 13
        BCDSTMUMU = 14
        OMEGALAMK = 15
        XILAMPI = 16
        DSTDZPI = 17
        DZMUKX = 18
        DZKPI = 19
        DPKPIPI = 20
        BCPIMUMU = 21
        LBPQMUMU = 22
        B2D0MUX = 23
        BD2DMMUX = 24
        BD2DSTMUX = 25
        BS2DSMUX = 26
        LB2LCMUX = 27
        UNKNOWNPTYPE = 9999

    class levelType(Enum):
        UNKOWNLEVEL = 0
        L2 = 2
        EF = 3
        HLT = 4
        LASTLEVEL = 5


    def roiId(self) -> int:
        "A method"
        ...

    def particleType(self) -> func_adl_servicex_xaodr22.xAOD.trigbphys_v1.TrigBphys_v1.pType:
        "A method"
        ...

    def level(self) -> func_adl_servicex_xaodr22.xAOD.trigbphys_v1.TrigBphys_v1.levelType:
        "A method"
        ...

    def eta(self) -> float:
        "A method"
        ...

    def phi(self) -> float:
        "A method"
        ...

    def pt(self) -> float:
        "A method"
        ...

    def mass(self) -> float:
        "A method"
        ...

    def fitmass(self) -> float:
        "A method"
        ...

    def fitchi2(self) -> float:
        "A method"
        ...

    def fitndof(self) -> int:
        "A method"
        ...

    def fitx(self) -> float:
        "A method"
        ...

    def fity(self) -> float:
        "A method"
        ...

    def fitz(self) -> float:
        "A method"
        ...

    def lxy(self) -> float:
        "A method"
        ...

    def lxyError(self) -> float:
        "A method"
        ...

    def tau(self) -> float:
        "A method"
        ...

    def tauError(self) -> float:
        "A method"
        ...

    def fitmassError(self) -> float:
        "A method"
        ...

    def secondaryDecay(self) -> func_adl_servicex_xaodr22.xAOD.trigbphys_v1.TrigBphys_v1:
        "A method"
        ...

    def secondaryDecayLink(self) -> func_adl_servicex_xaodr22.elementlink_datavector_xaod_trigbphys_v1__.ElementLink_DataVector_xAOD_TrigBphys_v1__:
        "A method"
        ...

    def trackParticleLinks(self) -> func_adl_servicex_xaodr22.vector_elementlink_datavector_xaod_trackparticle_v1___.vector_ElementLink_DataVector_xAOD_TrackParticle_v1___:
        "A method"
        ...

    def nTrackParticles(self) -> int:
        "A method"
        ...

    def trackParticle(self, i: int) -> func_adl_servicex_xaodr22.xAOD.trackparticle_v1.TrackParticle_v1:
        "A method"
        ...

    def vecRoiIds(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def nVecRoiIds(self) -> int:
        "A method"
        ...

    def vecRoiId(self, i: int) -> int:
        "A method"
        ...

    def lowerChain(self) -> func_adl_servicex_xaodr22.xAOD.trigbphys_v1.TrigBphys_v1:
        "A method"
        ...

    def lowerChainLink(self) -> func_adl_servicex_xaodr22.elementlink_datavector_xaod_trigbphys_v1__.ElementLink_DataVector_xAOD_TrigBphys_v1__:
        "A method"
        ...

    def particleLinks(self) -> func_adl_servicex_xaodr22.vector_elementlink_datavector_xaod_iparticle___.vector_ElementLink_DataVector_xAOD_IParticle___:
        "A method"
        ...

    def nParticles(self) -> int:
        "A method"
        ...

    def particle(self, i: int) -> func_adl_servicex_xaodr22.xAOD.iparticle.IParticle:
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
