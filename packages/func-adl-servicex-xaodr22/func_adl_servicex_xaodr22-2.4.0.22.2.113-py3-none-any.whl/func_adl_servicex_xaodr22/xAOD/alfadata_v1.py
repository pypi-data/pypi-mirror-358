from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr22

_method_map = {
    'detectorPartID': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::ALFAData_v1',
        'method_name': 'detectorPartID',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'maxTrackCnt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::ALFAData_v1',
        'method_name': 'maxTrackCnt',
        'return_type': 'int',
    },
    'overU': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::ALFAData_v1',
        'method_name': 'overU',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'overV': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::ALFAData_v1',
        'method_name': 'overV',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'overY': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::ALFAData_v1',
        'method_name': 'overY',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'numU': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::ALFAData_v1',
        'method_name': 'numU',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'numV': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::ALFAData_v1',
        'method_name': 'numV',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'numY': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::ALFAData_v1',
        'method_name': 'numY',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'mdFibSel': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::ALFAData_v1',
        'method_name': 'mdFibSel',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'odFibSel': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::ALFAData_v1',
        'method_name': 'odFibSel',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'xDetCS': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::ALFAData_v1',
        'method_name': 'xDetCS',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'yDetCS': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::ALFAData_v1',
        'method_name': 'yDetCS',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'xLhcCS': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::ALFAData_v1',
        'method_name': 'xLhcCS',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'yLhcCS': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::ALFAData_v1',
        'method_name': 'yLhcCS',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'zLhcCS': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::ALFAData_v1',
        'method_name': 'zLhcCS',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'xRPotCS': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::ALFAData_v1',
        'method_name': 'xRPotCS',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'yRPotCS': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::ALFAData_v1',
        'method_name': 'yRPotCS',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'xStatCS': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::ALFAData_v1',
        'method_name': 'xStatCS',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'yStatCS': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::ALFAData_v1',
        'method_name': 'yStatCS',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'xBeamCS': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::ALFAData_v1',
        'method_name': 'xBeamCS',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'yBeamCS': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::ALFAData_v1',
        'method_name': 'yBeamCS',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'scaler': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::ALFAData_v1',
        'method_name': 'scaler',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'trigPat': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::ALFAData_v1',
        'method_name': 'trigPat',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'mdFiberHits': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::ALFAData_v1',
        'method_name': 'mdFiberHits',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'mdMultiplicity': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::ALFAData_v1',
        'method_name': 'mdMultiplicity',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'odFiberHitsPos': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::ALFAData_v1',
        'method_name': 'odFiberHitsPos',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'odFiberHitsNeg': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::ALFAData_v1',
        'method_name': 'odFiberHitsNeg',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'odMultiplicityPos': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::ALFAData_v1',
        'method_name': 'odMultiplicityPos',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'odMultiplicityNeg': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::ALFAData_v1',
        'method_name': 'odMultiplicityNeg',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::ALFAData_v1',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::ALFAData_v1',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::ALFAData_v1',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::ALFAData_v1',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::ALFAData_v1',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::ALFAData_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::ALFAData_v1',
        'method_name': 'trackIndices',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::ALFAData_v1',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::ALFAData_v1',
        'method_name': 'isAvailable',
        'return_type': 'bool',
    },
}

_enum_function_map = {      
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
            'name': 'xAODForward/versions/ALFAData_v1.h',
            'body_includes': ["xAODForward/versions/ALFAData_v1.h"],
        })


        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODForward',
            'link_libraries': ["xAODForward"],
        })

        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class ALFAData_v1:
    "A class"


    def detectorPartID(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def maxTrackCnt(self) -> int:
        "A method"
        ...

    def overU(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def overV(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def overY(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def numU(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def numV(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def numY(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def mdFibSel(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def odFibSel(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def xDetCS(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def yDetCS(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def xLhcCS(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def yLhcCS(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def zLhcCS(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def xRPotCS(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def yRPotCS(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def xStatCS(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def yStatCS(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def xBeamCS(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def yBeamCS(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def scaler(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def trigPat(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def mdFiberHits(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def mdMultiplicity(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def odFiberHitsPos(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def odFiberHitsNeg(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def odMultiplicityPos(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def odMultiplicityNeg(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
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
