from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr22

_method_map = {
    'word': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexGlobalRoI_v1',
        'method_name': 'word',
        'return_type': 'unsigned int',
    },
    'tobEtScaleOne': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexGlobalRoI_v1',
        'method_name': 'tobEtScaleOne',
        'return_type': 'int',
    },
    'tobEtScaleTwo': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexGlobalRoI_v1',
        'method_name': 'tobEtScaleTwo',
        'return_type': 'int',
    },
    'quantityOne': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexGlobalRoI_v1',
        'method_name': 'quantityOne',
        'return_type': 'int16_t',
    },
    'unpackQuantityOne': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexGlobalRoI_v1',
        'method_name': 'unpackQuantityOne',
        'return_type': 'int16_t',
    },
    'quantityTwo': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexGlobalRoI_v1',
        'method_name': 'quantityTwo',
        'return_type': 'int16_t',
    },
    'unpackQuantityTwo': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexGlobalRoI_v1',
        'method_name': 'unpackQuantityTwo',
        'return_type': 'int16_t',
    },
    'METquantityOne': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexGlobalRoI_v1',
        'method_name': 'METquantityOne',
        'return_type': 'float',
    },
    'METquantityTwo': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexGlobalRoI_v1',
        'method_name': 'METquantityTwo',
        'return_type': 'float',
    },
    'SumEt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexGlobalRoI_v1',
        'method_name': 'SumEt',
        'return_type': 'float',
    },
    'statusOne': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexGlobalRoI_v1',
        'method_name': 'statusOne',
        'return_type': 'uint8_t',
    },
    'statusTwo': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexGlobalRoI_v1',
        'method_name': 'statusTwo',
        'return_type': 'uint8_t',
    },
    'unpackStatusOne': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexGlobalRoI_v1',
        'method_name': 'unpackStatusOne',
        'return_type': 'unsigned int',
    },
    'unpackStatusTwo': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexGlobalRoI_v1',
        'method_name': 'unpackStatusTwo',
        'return_type': 'unsigned int',
    },
    'saturated': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexGlobalRoI_v1',
        'method_name': 'saturated',
        'return_type': 'uint8_t',
    },
    'unpackSaturated': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexGlobalRoI_v1',
        'method_name': 'unpackSaturated',
        'return_type': 'unsigned int',
    },
    'globalType': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexGlobalRoI_v1',
        'method_name': 'globalType',
        'return_type': 'int',
    },
    'unpackType': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexGlobalRoI_v1',
        'method_name': 'unpackType',
        'return_type': 'int',
    },
    'isgScalar': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexGlobalRoI_v1',
        'method_name': 'isgScalar',
        'return_type': 'bool',
    },
    'isgMET': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexGlobalRoI_v1',
        'method_name': 'isgMET',
        'return_type': 'bool',
    },
    'isgMHT': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexGlobalRoI_v1',
        'method_name': 'isgMHT',
        'return_type': 'bool',
    },
    'isgMST': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexGlobalRoI_v1',
        'method_name': 'isgMST',
        'return_type': 'bool',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexGlobalRoI_v1',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexGlobalRoI_v1',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexGlobalRoI_v1',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexGlobalRoI_v1',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexGlobalRoI_v1',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexGlobalRoI_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexGlobalRoI_v1',
        'method_name': 'trackIndices',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexGlobalRoI_v1',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexGlobalRoI_v1',
        'method_name': 'isAvailable',
        'return_type': 'bool',
    },
}

_enum_function_map = {      
}

_defined_enums = {
    'ObjectType':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.gFexGlobalRoI_v1',
            'name': 'ObjectType',
            'values': [
                'gNull',
                'gScalar',
                'gMET',
                'gMHT',
                'gMST',
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
            'name': 'xAODTrigger/versions/gFexGlobalRoI_v1.h',
            'body_includes': ["xAODTrigger/versions/gFexGlobalRoI_v1.h"],
        })


        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODTrigger',
            'link_libraries': ["xAODTrigger"],
        })

        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class gFexGlobalRoI_v1:
    "A class"

    class ObjectType(Enum):
        gNull = 0
        gScalar = 1
        gMET = 2
        gMHT = 3
        gMST = 4


    def word(self) -> int:
        "A method"
        ...

    def tobEtScaleOne(self) -> int:
        "A method"
        ...

    def tobEtScaleTwo(self) -> int:
        "A method"
        ...

    def quantityOne(self) -> int:
        "A method"
        ...

    def unpackQuantityOne(self) -> int:
        "A method"
        ...

    def quantityTwo(self) -> int:
        "A method"
        ...

    def unpackQuantityTwo(self) -> int:
        "A method"
        ...

    def METquantityOne(self) -> float:
        "A method"
        ...

    def METquantityTwo(self) -> float:
        "A method"
        ...

    def SumEt(self) -> float:
        "A method"
        ...

    def statusOne(self) -> int:
        "A method"
        ...

    def statusTwo(self) -> int:
        "A method"
        ...

    def unpackStatusOne(self) -> int:
        "A method"
        ...

    def unpackStatusTwo(self) -> int:
        "A method"
        ...

    def saturated(self) -> int:
        "A method"
        ...

    def unpackSaturated(self) -> int:
        "A method"
        ...

    def globalType(self) -> int:
        "A method"
        ...

    def unpackType(self) -> int:
        "A method"
        ...

    def isgScalar(self) -> bool:
        "A method"
        ...

    def isgMET(self) -> bool:
        "A method"
        ...

    def isgMHT(self) -> bool:
        "A method"
        ...

    def isgMST(self) -> bool:
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
