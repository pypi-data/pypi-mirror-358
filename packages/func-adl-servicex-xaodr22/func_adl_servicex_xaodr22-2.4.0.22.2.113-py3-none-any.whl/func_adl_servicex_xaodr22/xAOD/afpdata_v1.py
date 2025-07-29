from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr22

_method_map = {
    'pixelTotNum': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'pixelTotNum',
        'return_type': 'int',
    },
    'pixelStID': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'pixelStID',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'pixelLayerID': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'pixelLayerID',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'pixelRow': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'pixelRow',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'pixelCol': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'pixelCol',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'pixelE': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'pixelE',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'layerTotNum': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'layerTotNum',
        'return_type': 'int',
    },
    'layerStID': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'layerStID',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'layerLayerID': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'layerLayerID',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'layerNpix': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'layerNpix',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'layerEtot': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'layerEtot',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'statTotNum': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'statTotNum',
        'return_type': 'int',
    },
    'statStID': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'statStID',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'statNpix': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'statNpix',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'statEtot': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'statEtot',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'trkTotNumTracks': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'trkTotNumTracks',
        'return_type': 'int',
    },
    'trkStID': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'trkStID',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'trkX': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'trkX',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'trkY': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'trkY',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'trkZ': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'trkZ',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'trkXslope': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'trkXslope',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'trkYslope': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'trkYslope',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'trkNpix': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'trkNpix',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'trkNholes': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'trkNholes',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'trkQuality': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'trkQuality',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'simSidTotNumHits': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'simSidTotNumHits',
        'return_type': 'int',
    },
    'simSidHitID': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'simSidHitID',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'simSidTrackID': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'simSidTrackID',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'simSidEncoding': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'simSidEncoding',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'simSidKineticE': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'simSidKineticE',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'simSidDepE': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'simSidDepE',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'simSidPreStepX': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'simSidPreStepX',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'simSidPreStepY': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'simSidPreStepY',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'simSidPreStepZ': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'simSidPreStepZ',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'simSidPostStepX': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'simSidPostStepX',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'simSidPostStepY': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'simSidPostStepY',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'simSidPostStepZ': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'simSidPostStepZ',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'simSidTime': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'simSidTime',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'simSidStID': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'simSidStID',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'simSidLayerID': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'simSidLayerID',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'simSidIsVacLayer': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'simSidIsVacLayer',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'simSidPixelRow': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'simSidPixelRow',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'simSidPixelCol': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'simSidPixelCol',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'tidTotNumTracks': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'tidTotNumTracks',
        'return_type': 'int',
    },
    'tidStID': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'tidStID',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'tidQID': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'tidQID',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'tidTrainID': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'tidTrainID',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'tidTime': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'tidTime',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'tidAmplitude': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'tidAmplitude',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'tidNumSaturatedBars': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'tidNumSaturatedBars',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'simTidTotNumHits': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'simTidTotNumHits',
        'return_type': 'int',
    },
    'simTidHitID': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'simTidHitID',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'simTidTrackID': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'simTidTrackID',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'simTidEncoding': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'simTidEncoding',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'simTidKineticE': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'simTidKineticE',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'simTidDepE': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'simTidDepE',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'simTidPreStepX': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'simTidPreStepX',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'simTidPreStepY': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'simTidPreStepY',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'simTidPreStepZ': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'simTidPreStepZ',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'simTidPostStepX': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'simTidPostStepX',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'simTidPostStepY': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'simTidPostStepY',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'simTidPostStepZ': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'simTidPostStepZ',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'simTidTime': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'simTidTime',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'simTidStID': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'simTidStID',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'simTidLayerID': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'simTidLayerID',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'simTidSensElID': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'simTidSensElID',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'trackIndices',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::AFPData_v1',
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
            'name': 'xAODForward/versions/AFPData_v1.h',
            'body_includes': ["xAODForward/versions/AFPData_v1.h"],
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
class AFPData_v1:
    "A class"


    def pixelTotNum(self) -> int:
        "A method"
        ...

    def pixelStID(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def pixelLayerID(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def pixelRow(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def pixelCol(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def pixelE(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def layerTotNum(self) -> int:
        "A method"
        ...

    def layerStID(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def layerLayerID(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def layerNpix(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def layerEtot(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def statTotNum(self) -> int:
        "A method"
        ...

    def statStID(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def statNpix(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def statEtot(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def trkTotNumTracks(self) -> int:
        "A method"
        ...

    def trkStID(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def trkX(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def trkY(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def trkZ(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def trkXslope(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def trkYslope(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def trkNpix(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def trkNholes(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def trkQuality(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def simSidTotNumHits(self) -> int:
        "A method"
        ...

    def simSidHitID(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def simSidTrackID(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def simSidEncoding(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def simSidKineticE(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def simSidDepE(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def simSidPreStepX(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def simSidPreStepY(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def simSidPreStepZ(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def simSidPostStepX(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def simSidPostStepY(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def simSidPostStepZ(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def simSidTime(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def simSidStID(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def simSidLayerID(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def simSidIsVacLayer(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def simSidPixelRow(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def simSidPixelCol(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def tidTotNumTracks(self) -> int:
        "A method"
        ...

    def tidStID(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def tidQID(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def tidTrainID(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def tidTime(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def tidAmplitude(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def tidNumSaturatedBars(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def simTidTotNumHits(self) -> int:
        "A method"
        ...

    def simTidHitID(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def simTidTrackID(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def simTidEncoding(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def simTidKineticE(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def simTidDepE(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def simTidPreStepX(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def simTidPreStepY(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def simTidPreStepZ(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def simTidPostStepX(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def simTidPostStepY(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def simTidPostStepZ(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def simTidTime(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def simTidStID(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def simTidLayerID(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
        "A method"
        ...

    def simTidSensElID(self) -> func_adl_servicex_xaodr22.vector_int_.vector_int_:
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
