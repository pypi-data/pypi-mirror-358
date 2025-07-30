from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr22

_method_map = {
    'isValid': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'isValid',
        'return_type': 'bool',
    },
    'runNumber': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'runNumber',
        'return_type': 'unsigned int',
        'deref_count': 2
    },
    'eventNumber': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'eventNumber',
        'return_type': 'unsigned long long',
        'deref_count': 2
    },
    'lumiBlock': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'lumiBlock',
        'return_type': 'unsigned int',
        'deref_count': 2
    },
    'timeStamp': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'timeStamp',
        'return_type': 'unsigned int',
        'deref_count': 2
    },
    'timeStampNSOffset': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'timeStampNSOffset',
        'return_type': 'unsigned int',
        'deref_count': 2
    },
    'bcid': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'bcid',
        'return_type': 'unsigned int',
        'deref_count': 2
    },
    'detectorMask0': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'detectorMask0',
        'return_type': 'unsigned int',
        'deref_count': 2
    },
    'detectorMask1': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'detectorMask1',
        'return_type': 'unsigned int',
        'deref_count': 2
    },
    'detectorMask2': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'detectorMask2',
        'return_type': 'unsigned int',
        'deref_count': 2
    },
    'detectorMask3': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'detectorMask3',
        'return_type': 'unsigned int',
        'deref_count': 2
    },
    'detectorMask': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'detectorMask',
        'return_type': 'uint64_t',
        'deref_count': 2
    },
    'detectorMaskExt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'detectorMaskExt',
        'return_type': 'uint64_t',
        'deref_count': 2
    },
    'mcChannelNumber': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'mcChannelNumber',
        'return_type': 'unsigned int',
        'deref_count': 2
    },
    'mcEventNumber': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'mcEventNumber',
        'return_type': 'unsigned long long',
        'deref_count': 2
    },
    'mcEventWeights': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'mcEventWeights',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
        'deref_count': 2
    },
    'mcEventWeight': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'mcEventWeight',
        'return_type': 'float',
        'deref_count': 2
    },
    'eventTypeBitmask': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'eventTypeBitmask',
        'return_type': 'unsigned int',
        'deref_count': 2
    },
    'eventType': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'eventType',
        'return_type': 'bool',
        'deref_count': 2
    },
    'statusElement': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'statusElement',
        'return_type': 'unsigned int',
        'deref_count': 2
    },
    'extendedLevel1ID': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'extendedLevel1ID',
        'return_type': 'unsigned int',
        'deref_count': 2
    },
    'level1TriggerType': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'level1TriggerType',
        'return_type': 'uint16_t',
        'deref_count': 2
    },
    'streamTags': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'streamTags',
        'return_type_element': 'xAOD::EventInfo_v1::StreamTag',
        'return_type_collection': 'const vector<xAOD::EventInfo_v1::StreamTag>',
        'deref_count': 2
    },
    'actualInteractionsPerCrossing': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'actualInteractionsPerCrossing',
        'return_type': 'float',
        'deref_count': 2
    },
    'averageInteractionsPerCrossing': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'averageInteractionsPerCrossing',
        'return_type': 'float',
        'deref_count': 2
    },
    'pileUpMixtureIDLowBits': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'pileUpMixtureIDLowBits',
        'return_type': 'unsigned long long',
        'deref_count': 2
    },
    'pileUpMixtureIDHighBits': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'pileUpMixtureIDHighBits',
        'return_type': 'unsigned long long',
        'deref_count': 2
    },
    'PileUpType2Name': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'PileUpType2Name',
        'return_type': 'const string',
        'deref_count': 2
    },
    'PileUpInt2Type': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'PileUpInt2Type',
        'return_type': 'xAOD::EventInfo_v1::PileUpType',
        'deref_count': 2
    },
    'subEvents': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'subEvents',
        'return_type_element': 'xAOD::EventInfo_v1::SubEvent',
        'return_type_collection': 'const vector<xAOD::EventInfo_v1::SubEvent>',
        'deref_count': 2
    },
    'eventFlags': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'eventFlags',
        'return_type': 'unsigned int',
        'deref_count': 2
    },
    'isEventFlagBitSet': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'isEventFlagBitSet',
        'return_type': 'bool',
        'deref_count': 2
    },
    'setEventFlags': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'setEventFlags',
        'return_type': 'bool',
        'deref_count': 2
    },
    'setEventFlagBit': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'setEventFlagBit',
        'return_type': 'bool',
        'deref_count': 2
    },
    'resetEventFlagBit': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'resetEventFlagBit',
        'return_type': 'bool',
        'deref_count': 2
    },
    'errorState': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'errorState',
        'return_type': 'xAOD::EventInfo_v1::EventFlagErrorState',
        'deref_count': 2
    },
    'setErrorState': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'setErrorState',
        'return_type': 'bool',
        'deref_count': 2
    },
    'updateEventFlagBit': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'updateEventFlagBit',
        'return_type': 'bool',
        'deref_count': 2
    },
    'updateEventFlags': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'updateEventFlags',
        'return_type': 'bool',
        'deref_count': 2
    },
    'updateErrorState': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'updateErrorState',
        'return_type': 'bool',
        'deref_count': 2
    },
    'beamPosX': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'beamPosX',
        'return_type': 'float',
        'deref_count': 2
    },
    'beamPosY': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'beamPosY',
        'return_type': 'float',
        'deref_count': 2
    },
    'beamPosZ': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'beamPosZ',
        'return_type': 'float',
        'deref_count': 2
    },
    'beamPosSigmaX': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'beamPosSigmaX',
        'return_type': 'float',
        'deref_count': 2
    },
    'beamPosSigmaY': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'beamPosSigmaY',
        'return_type': 'float',
        'deref_count': 2
    },
    'beamPosSigmaZ': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'beamPosSigmaZ',
        'return_type': 'float',
        'deref_count': 2
    },
    'beamPosSigmaXY': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'beamPosSigmaXY',
        'return_type': 'float',
        'deref_count': 2
    },
    'beamTiltXZ': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'beamTiltXZ',
        'return_type': 'float',
        'deref_count': 2
    },
    'beamTiltYZ': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'beamTiltYZ',
        'return_type': 'float',
        'deref_count': 2
    },
    'beamStatus': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'beamStatus',
        'return_type': 'unsigned int',
        'deref_count': 2
    },
    'beamSpotWeight': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'beamSpotWeight',
        'return_type': 'float',
        'deref_count': 2
    },
    'hasBeamSpotWeight': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'hasBeamSpotWeight',
        'return_type': 'bool',
        'deref_count': 2
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'index',
        'return_type': 'unsigned int',
        'deref_count': 2
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
        'deref_count': 2
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
        'deref_count': 2
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'hasStore',
        'return_type': 'bool',
        'deref_count': 2
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
        'deref_count': 2
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
        'deref_count': 2
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'trackIndices',
        'return_type': 'bool',
        'deref_count': 2
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
        'method_name': 'auxdataConst',
        'return_type': 'U',
        'deref_count': 2
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::EventInfo_v1>>',
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
            'name': 'xAODEventInfo/versions/EventInfo_v1.h',
            'body_includes': ["xAODEventInfo/versions/EventInfo_v1.h"],
        })


        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODEventInfo',
            'link_libraries': ["xAODEventInfo"],
        })

        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class ElementLink_DataVector_xAOD_EventInfo_v1__:
    "A class"


    def isValid(self) -> bool:
        "A method"
        ...

    def runNumber(self) -> int:
        "A method"
        ...

    def eventNumber(self) -> int:
        "A method"
        ...

    def lumiBlock(self) -> int:
        "A method"
        ...

    def timeStamp(self) -> int:
        "A method"
        ...

    def timeStampNSOffset(self) -> int:
        "A method"
        ...

    def bcid(self) -> int:
        "A method"
        ...

    def detectorMask0(self) -> int:
        "A method"
        ...

    def detectorMask1(self) -> int:
        "A method"
        ...

    def detectorMask2(self) -> int:
        "A method"
        ...

    def detectorMask3(self) -> int:
        "A method"
        ...

    def detectorMask(self) -> int:
        "A method"
        ...

    def detectorMaskExt(self) -> int:
        "A method"
        ...

    def mcChannelNumber(self) -> int:
        "A method"
        ...

    def mcEventNumber(self) -> int:
        "A method"
        ...

    def mcEventWeights(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def mcEventWeight(self, i: int) -> float:
        "A method"
        ...

    def eventTypeBitmask(self) -> int:
        "A method"
        ...

    def eventType(self, type: func_adl_servicex_xaodr22.xAOD.eventinfo_v1.EventInfo_v1.EventType) -> bool:
        "A method"
        ...

    def statusElement(self) -> int:
        "A method"
        ...

    def extendedLevel1ID(self) -> int:
        "A method"
        ...

    def level1TriggerType(self) -> int:
        "A method"
        ...

    def streamTags(self) -> func_adl_servicex_xaodr22.vector_xaod_eventinfo_v1_streamtag_.vector_xAOD_EventInfo_v1_StreamTag_:
        "A method"
        ...

    def actualInteractionsPerCrossing(self) -> float:
        "A method"
        ...

    def averageInteractionsPerCrossing(self) -> float:
        "A method"
        ...

    def pileUpMixtureIDLowBits(self) -> int:
        "A method"
        ...

    def pileUpMixtureIDHighBits(self) -> int:
        "A method"
        ...

    def PileUpType2Name(self, typ: func_adl_servicex_xaodr22.xAOD.eventinfo_v1.EventInfo_v1.PileUpType) -> str:
        "A method"
        ...

    def PileUpInt2Type(self, typ: int) -> func_adl_servicex_xaodr22.xAOD.eventinfo_v1.EventInfo_v1.PileUpType:
        "A method"
        ...

    def subEvents(self) -> func_adl_servicex_xaodr22.vector_xaod_eventinfo_v1_subevent_.vector_xAOD_EventInfo_v1_SubEvent_:
        "A method"
        ...

    def eventFlags(self, subDet: func_adl_servicex_xaodr22.xAOD.eventinfo_v1.EventInfo_v1.EventFlagSubDet) -> int:
        "A method"
        ...

    def isEventFlagBitSet(self, subDet: func_adl_servicex_xaodr22.xAOD.eventinfo_v1.EventInfo_v1.EventFlagSubDet, bit: int) -> bool:
        "A method"
        ...

    def setEventFlags(self, subDet: func_adl_servicex_xaodr22.xAOD.eventinfo_v1.EventInfo_v1.EventFlagSubDet, flags: int) -> bool:
        "A method"
        ...

    def setEventFlagBit(self, subDet: func_adl_servicex_xaodr22.xAOD.eventinfo_v1.EventInfo_v1.EventFlagSubDet, bit: int) -> bool:
        "A method"
        ...

    def resetEventFlagBit(self, subDet: func_adl_servicex_xaodr22.xAOD.eventinfo_v1.EventInfo_v1.EventFlagSubDet, bit: int) -> bool:
        "A method"
        ...

    def errorState(self, subDet: func_adl_servicex_xaodr22.xAOD.eventinfo_v1.EventInfo_v1.EventFlagSubDet) -> func_adl_servicex_xaodr22.xAOD.eventinfo_v1.EventInfo_v1.EventFlagErrorState:
        "A method"
        ...

    def setErrorState(self, subDet: func_adl_servicex_xaodr22.xAOD.eventinfo_v1.EventInfo_v1.EventFlagSubDet, state: func_adl_servicex_xaodr22.xAOD.eventinfo_v1.EventInfo_v1.EventFlagErrorState) -> bool:
        "A method"
        ...

    def updateEventFlagBit(self, subDet: func_adl_servicex_xaodr22.xAOD.eventinfo_v1.EventInfo_v1.EventFlagSubDet, bit: int) -> bool:
        "A method"
        ...

    def updateEventFlags(self, subDet: func_adl_servicex_xaodr22.xAOD.eventinfo_v1.EventInfo_v1.EventFlagSubDet, flags_in: int) -> bool:
        "A method"
        ...

    def updateErrorState(self, subDet: func_adl_servicex_xaodr22.xAOD.eventinfo_v1.EventInfo_v1.EventFlagSubDet, state: func_adl_servicex_xaodr22.xAOD.eventinfo_v1.EventInfo_v1.EventFlagErrorState) -> bool:
        "A method"
        ...

    def beamPosX(self) -> float:
        "A method"
        ...

    def beamPosY(self) -> float:
        "A method"
        ...

    def beamPosZ(self) -> float:
        "A method"
        ...

    def beamPosSigmaX(self) -> float:
        "A method"
        ...

    def beamPosSigmaY(self) -> float:
        "A method"
        ...

    def beamPosSigmaZ(self) -> float:
        "A method"
        ...

    def beamPosSigmaXY(self) -> float:
        "A method"
        ...

    def beamTiltXZ(self) -> float:
        "A method"
        ...

    def beamTiltYZ(self) -> float:
        "A method"
        ...

    def beamStatus(self) -> int:
        "A method"
        ...

    def beamSpotWeight(self) -> float:
        "A method"
        ...

    def hasBeamSpotWeight(self) -> bool:
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
