from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr22

_method_map = {
    'isValid': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::TrigEMCluster_v1>>',
        'method_name': 'isValid',
        'return_type': 'bool',
    },
    'energy': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::TrigEMCluster_v1>>',
        'method_name': 'energy',
        'return_type': 'float',
        'deref_count': 2
    },
    'energySample': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::TrigEMCluster_v1>>',
        'method_name': 'energySample',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
        'deref_count': 2
    },
    'et': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::TrigEMCluster_v1>>',
        'method_name': 'et',
        'return_type': 'float',
        'deref_count': 2
    },
    'eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::TrigEMCluster_v1>>',
        'method_name': 'eta',
        'return_type': 'float',
        'deref_count': 2
    },
    'phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::TrigEMCluster_v1>>',
        'method_name': 'phi',
        'return_type': 'float',
        'deref_count': 2
    },
    'e237': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::TrigEMCluster_v1>>',
        'method_name': 'e237',
        'return_type': 'float',
        'deref_count': 2
    },
    'e277': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::TrigEMCluster_v1>>',
        'method_name': 'e277',
        'return_type': 'float',
        'deref_count': 2
    },
    'fracs1': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::TrigEMCluster_v1>>',
        'method_name': 'fracs1',
        'return_type': 'float',
        'deref_count': 2
    },
    'weta2': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::TrigEMCluster_v1>>',
        'method_name': 'weta2',
        'return_type': 'float',
        'deref_count': 2
    },
    'ehad1': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::TrigEMCluster_v1>>',
        'method_name': 'ehad1',
        'return_type': 'float',
        'deref_count': 2
    },
    'eta1': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::TrigEMCluster_v1>>',
        'method_name': 'eta1',
        'return_type': 'float',
        'deref_count': 2
    },
    'emaxs1': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::TrigEMCluster_v1>>',
        'method_name': 'emaxs1',
        'return_type': 'float',
        'deref_count': 2
    },
    'e2tsts1': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::TrigEMCluster_v1>>',
        'method_name': 'e2tsts1',
        'return_type': 'float',
        'deref_count': 2
    },
    'e233': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::TrigEMCluster_v1>>',
        'method_name': 'e233',
        'return_type': 'float',
        'deref_count': 2
    },
    'wstot': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::TrigEMCluster_v1>>',
        'method_name': 'wstot',
        'return_type': 'float',
        'deref_count': 2
    },
    'rawEnergy': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::TrigEMCluster_v1>>',
        'method_name': 'rawEnergy',
        'return_type': 'float',
        'deref_count': 2
    },
    'rawEnergySample': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::TrigEMCluster_v1>>',
        'method_name': 'rawEnergySample',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
        'deref_count': 2
    },
    'rawEt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::TrigEMCluster_v1>>',
        'method_name': 'rawEt',
        'return_type': 'float',
        'deref_count': 2
    },
    'rawEta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::TrigEMCluster_v1>>',
        'method_name': 'rawEta',
        'return_type': 'float',
        'deref_count': 2
    },
    'rawPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::TrigEMCluster_v1>>',
        'method_name': 'rawPhi',
        'return_type': 'float',
        'deref_count': 2
    },
    'RoIword': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::TrigEMCluster_v1>>',
        'method_name': 'RoIword',
        'return_type': 'long',
        'deref_count': 2
    },
    'nCells': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::TrigEMCluster_v1>>',
        'method_name': 'nCells',
        'return_type': 'int',
        'deref_count': 2
    },
    'clusterQuality': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::TrigEMCluster_v1>>',
        'method_name': 'clusterQuality',
        'return_type': 'unsigned int',
        'deref_count': 2
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::TrigEMCluster_v1>>',
        'method_name': 'index',
        'return_type': 'unsigned int',
        'deref_count': 2
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::TrigEMCluster_v1>>',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
        'deref_count': 2
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::TrigEMCluster_v1>>',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
        'deref_count': 2
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::TrigEMCluster_v1>>',
        'method_name': 'hasStore',
        'return_type': 'bool',
        'deref_count': 2
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::TrigEMCluster_v1>>',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
        'deref_count': 2
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::TrigEMCluster_v1>>',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
        'deref_count': 2
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::TrigEMCluster_v1>>',
        'method_name': 'trackIndices',
        'return_type': 'bool',
        'deref_count': 2
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::TrigEMCluster_v1>>',
        'method_name': 'auxdataConst',
        'return_type': 'U',
        'deref_count': 2
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::TrigEMCluster_v1>>',
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
            'name': 'xAODTrigCalo/versions/TrigEMCluster_v1.h',
            'body_includes': ["xAODTrigCalo/versions/TrigEMCluster_v1.h"],
        })


        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODTrigCalo',
            'link_libraries': ["xAODTrigCalo"],
        })

        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class ElementLink_DataVector_xAOD_TrigEMCluster_v1__:
    "A class"


    def isValid(self) -> bool:
        "A method"
        ...

    def energy(self) -> float:
        "A method"
        ...

    def energySample(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def et(self) -> float:
        "A method"
        ...

    def eta(self) -> float:
        "A method"
        ...

    def phi(self) -> float:
        "A method"
        ...

    def e237(self) -> float:
        "A method"
        ...

    def e277(self) -> float:
        "A method"
        ...

    def fracs1(self) -> float:
        "A method"
        ...

    def weta2(self) -> float:
        "A method"
        ...

    def ehad1(self) -> float:
        "A method"
        ...

    def eta1(self) -> float:
        "A method"
        ...

    def emaxs1(self) -> float:
        "A method"
        ...

    def e2tsts1(self) -> float:
        "A method"
        ...

    def e233(self) -> float:
        "A method"
        ...

    def wstot(self) -> float:
        "A method"
        ...

    def rawEnergy(self) -> float:
        "A method"
        ...

    def rawEnergySample(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def rawEt(self) -> float:
        "A method"
        ...

    def rawEta(self) -> float:
        "A method"
        ...

    def rawPhi(self) -> float:
        "A method"
        ...

    def RoIword(self) -> int:
        "A method"
        ...

    def nCells(self) -> int:
        "A method"
        ...

    def clusterQuality(self) -> int:
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
