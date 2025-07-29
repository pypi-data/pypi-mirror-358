from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr22

_method_map = {
    'crate': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMEtSums_v1',
        'method_name': 'crate',
        'return_type': 'int',
    },
    'dataID': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMEtSums_v1',
        'method_name': 'dataID',
        'return_type': 'int',
    },
    'peak': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMEtSums_v1',
        'method_name': 'peak',
        'return_type': 'int',
    },
    'etVec': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMEtSums_v1',
        'method_name': 'etVec',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned int>',
    },
    'exVec': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMEtSums_v1',
        'method_name': 'exVec',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned int>',
    },
    'eyVec': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMEtSums_v1',
        'method_name': 'eyVec',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned int>',
    },
    'etErrorVec': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMEtSums_v1',
        'method_name': 'etErrorVec',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'exErrorVec': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMEtSums_v1',
        'method_name': 'exErrorVec',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'eyErrorVec': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMEtSums_v1',
        'method_name': 'eyErrorVec',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'et': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMEtSums_v1',
        'method_name': 'et',
        'return_type': 'unsigned int',
    },
    'ex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMEtSums_v1',
        'method_name': 'ex',
        'return_type': 'unsigned int',
    },
    'ey': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMEtSums_v1',
        'method_name': 'ey',
        'return_type': 'unsigned int',
    },
    'etError': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMEtSums_v1',
        'method_name': 'etError',
        'return_type': 'int',
    },
    'exError': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMEtSums_v1',
        'method_name': 'exError',
        'return_type': 'int',
    },
    'eyError': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMEtSums_v1',
        'method_name': 'eyError',
        'return_type': 'int',
    },
    'EtVec': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMEtSums_v1',
        'method_name': 'EtVec',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned int>',
    },
    'ExVec': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMEtSums_v1',
        'method_name': 'ExVec',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned int>',
    },
    'EyVec': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMEtSums_v1',
        'method_name': 'EyVec',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned int>',
    },
    'EtErrorVec': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMEtSums_v1',
        'method_name': 'EtErrorVec',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'ExErrorVec': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMEtSums_v1',
        'method_name': 'ExErrorVec',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'EyErrorVec': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMEtSums_v1',
        'method_name': 'EyErrorVec',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'Et': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMEtSums_v1',
        'method_name': 'Et',
        'return_type': 'unsigned int',
    },
    'Ex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMEtSums_v1',
        'method_name': 'Ex',
        'return_type': 'unsigned int',
    },
    'Ey': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMEtSums_v1',
        'method_name': 'Ey',
        'return_type': 'unsigned int',
    },
    'EtError': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMEtSums_v1',
        'method_name': 'EtError',
        'return_type': 'int',
    },
    'ExError': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMEtSums_v1',
        'method_name': 'ExError',
        'return_type': 'int',
    },
    'EyError': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMEtSums_v1',
        'method_name': 'EyError',
        'return_type': 'int',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMEtSums_v1',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMEtSums_v1',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMEtSums_v1',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMEtSums_v1',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMEtSums_v1',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMEtSums_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMEtSums_v1',
        'method_name': 'trackIndices',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMEtSums_v1',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMMEtSums_v1',
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
            'name': 'xAODTrigL1Calo/versions/CMMEtSums_v1.h',
            'body_includes': ["xAODTrigL1Calo/versions/CMMEtSums_v1.h"],
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
class CMMEtSums_v1:
    "A class"


    def crate(self) -> int:
        "A method"
        ...

    def dataID(self) -> int:
        "A method"
        ...

    def peak(self) -> int:
        "A method"
        ...

    def etVec(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def exVec(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def eyVec(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def etErrorVec(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def exErrorVec(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def eyErrorVec(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def et(self) -> int:
        "A method"
        ...

    def ex(self) -> int:
        "A method"
        ...

    def ey(self) -> int:
        "A method"
        ...

    def etError(self) -> int:
        "A method"
        ...

    def exError(self) -> int:
        "A method"
        ...

    def eyError(self) -> int:
        "A method"
        ...

    def EtVec(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def ExVec(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def EyVec(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def EtErrorVec(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def ExErrorVec(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def EyErrorVec(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def Et(self) -> int:
        "A method"
        ...

    def Ex(self) -> int:
        "A method"
        ...

    def Ey(self) -> int:
        "A method"
        ...

    def EtError(self) -> int:
        "A method"
        ...

    def ExError(self) -> int:
        "A method"
        ...

    def EyError(self) -> int:
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
