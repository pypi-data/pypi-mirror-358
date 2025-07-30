from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr22

_method_map = {
    'version': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'version',
        'return_type': 'unsigned int',
    },
    'sourceId': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'sourceId',
        'return_type': 'unsigned int',
    },
    'run': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'run',
        'return_type': 'unsigned int',
    },
    'lvl1Id': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'lvl1Id',
        'return_type': 'unsigned int',
    },
    'bcid': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'bcid',
        'return_type': 'unsigned int',
    },
    'trigType': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'trigType',
        'return_type': 'unsigned int',
    },
    'lvl1DetType': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'lvl1DetType',
        'return_type': 'unsigned int',
    },
    'statusWords': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'statusWords',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned int>',
    },
    'payloadSize': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'payloadSize',
        'return_type': 'unsigned int',
    },
    'majorVersion': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'majorVersion',
        'return_type': 'int',
    },
    'minorVersion': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'minorVersion',
        'return_type': 'int',
    },
    'sourceID': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'sourceID',
        'return_type': 'int',
    },
    'subDetectorID': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'subDetectorID',
        'return_type': 'int',
    },
    'moduleID': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'moduleID',
        'return_type': 'int',
    },
    'crate': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'crate',
        'return_type': 'int',
    },
    'sLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'sLink',
        'return_type': 'int',
    },
    'dataType': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'dataType',
        'return_type': 'int',
    },
    'runType': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'runType',
        'return_type': 'int',
    },
    'runNumber': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'runNumber',
        'return_type': 'int',
    },
    'extendedL1ID': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'extendedL1ID',
        'return_type': 'int',
    },
    'ecrID': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'ecrID',
        'return_type': 'int',
    },
    'l1ID': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'l1ID',
        'return_type': 'int',
    },
    'bunchCrossing': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'bunchCrossing',
        'return_type': 'int',
    },
    'l1TriggerType': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'l1TriggerType',
        'return_type': 'int',
    },
    'detEventType': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'detEventType',
        'return_type': 'int',
    },
    'orbitCount': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'orbitCount',
        'return_type': 'int',
    },
    'stepNumber': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'stepNumber',
        'return_type': 'int',
    },
    'stepType': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'stepType',
        'return_type': 'int',
    },
    'bcnMismatch': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'bcnMismatch',
        'return_type': 'bool',
    },
    'gLinkTimeout': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'gLinkTimeout',
        'return_type': 'bool',
    },
    'dataTransportError': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'dataTransportError',
        'return_type': 'bool',
    },
    'rodFifoOverflow': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'rodFifoOverflow',
        'return_type': 'bool',
    },
    'lvdsLinkError': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'lvdsLinkError',
        'return_type': 'bool',
    },
    'cmmParityError': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'cmmParityError',
        'return_type': 'bool',
    },
    'gLinkError': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'gLinkError',
        'return_type': 'bool',
    },
    'limitedRoISet': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'limitedRoISet',
        'return_type': 'bool',
    },
    'triggerTypeTimeout': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'triggerTypeTimeout',
        'return_type': 'bool',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'trackIndices',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::RODHeader_v2',
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
            'name': 'xAODTrigL1Calo/versions/RODHeader_v2.h',
            'body_includes': ["xAODTrigL1Calo/versions/RODHeader_v2.h"],
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
class RODHeader_v2:
    "A class"


    def version(self) -> int:
        "A method"
        ...

    def sourceId(self) -> int:
        "A method"
        ...

    def run(self) -> int:
        "A method"
        ...

    def lvl1Id(self) -> int:
        "A method"
        ...

    def bcid(self) -> int:
        "A method"
        ...

    def trigType(self) -> int:
        "A method"
        ...

    def lvl1DetType(self) -> int:
        "A method"
        ...

    def statusWords(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def payloadSize(self) -> int:
        "A method"
        ...

    def majorVersion(self) -> int:
        "A method"
        ...

    def minorVersion(self) -> int:
        "A method"
        ...

    def sourceID(self) -> int:
        "A method"
        ...

    def subDetectorID(self) -> int:
        "A method"
        ...

    def moduleID(self) -> int:
        "A method"
        ...

    def crate(self) -> int:
        "A method"
        ...

    def sLink(self) -> int:
        "A method"
        ...

    def dataType(self) -> int:
        "A method"
        ...

    def runType(self) -> int:
        "A method"
        ...

    def runNumber(self) -> int:
        "A method"
        ...

    def extendedL1ID(self) -> int:
        "A method"
        ...

    def ecrID(self) -> int:
        "A method"
        ...

    def l1ID(self) -> int:
        "A method"
        ...

    def bunchCrossing(self) -> int:
        "A method"
        ...

    def l1TriggerType(self) -> int:
        "A method"
        ...

    def detEventType(self) -> int:
        "A method"
        ...

    def orbitCount(self) -> int:
        "A method"
        ...

    def stepNumber(self) -> int:
        "A method"
        ...

    def stepType(self) -> int:
        "A method"
        ...

    def bcnMismatch(self) -> bool:
        "A method"
        ...

    def gLinkTimeout(self) -> bool:
        "A method"
        ...

    def dataTransportError(self) -> bool:
        "A method"
        ...

    def rodFifoOverflow(self) -> bool:
        "A method"
        ...

    def lvdsLinkError(self) -> bool:
        "A method"
        ...

    def cmmParityError(self) -> bool:
        "A method"
        ...

    def gLinkError(self) -> bool:
        "A method"
        ...

    def limitedRoISet(self) -> bool:
        "A method"
        ...

    def triggerTypeTimeout(self) -> bool:
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
