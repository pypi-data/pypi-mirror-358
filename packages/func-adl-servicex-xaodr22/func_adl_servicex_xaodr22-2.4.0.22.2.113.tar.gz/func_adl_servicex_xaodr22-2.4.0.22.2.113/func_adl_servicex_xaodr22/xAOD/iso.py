from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr22

_method_map = {
    'toCString': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Iso',
        'method_name': 'toCString',
        'return_type': 'const char *',
    },
}

_enum_function_map = {
    'toCString': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.Iso',
            'name': 'IsolationCaloCorrection',
            'values': [
                'noneCaloCorrection',
                'coreMuon',
                'core57cells',
                'coreCone',
                'ptCorrection',
                'pileupCorrection',
                'coreConeSC',
                'numIsolationCaloCorrections',
            ],
        },
    ],      
}

_defined_enums = {
    'IsolationType':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.Iso',
            'name': 'IsolationType',
            'values': [
                'etcone20',
                'etcone30',
                'etcone40',
                'ptcone20',
                'ptcone30',
                'ptcone40',
                'ptcone50',
                'topoetcone20',
                'topoetcone30',
                'topoetcone40',
                'ptvarcone20',
                'ptvarcone30',
                'ptvarcone40',
                'neflowisol20',
                'neflowisol30',
                'neflowisol40',
                'ptvarcone20_Nonprompt_All_MaxWeightTTVA_pt500',
                'ptvarcone30_Nonprompt_All_MaxWeightTTVA_pt500',
                'ptvarcone40_Nonprompt_All_MaxWeightTTVA_pt500',
                'ptvarcone20_Nonprompt_All_MaxWeightTTVA_pt1000',
                'ptvarcone30_Nonprompt_All_MaxWeightTTVA_pt1000',
                'ptvarcone40_Nonprompt_All_MaxWeightTTVA_pt1000',
                'ptcone20_Nonprompt_All_MaxWeightTTVA_pt500',
                'ptcone30_Nonprompt_All_MaxWeightTTVA_pt500',
                'ptcone40_Nonprompt_All_MaxWeightTTVA_pt500',
                'ptcone20_Nonprompt_All_MaxWeightTTVA_pt1000',
                'ptcone30_Nonprompt_All_MaxWeightTTVA_pt1000',
                'ptcone40_Nonprompt_All_MaxWeightTTVA_pt1000',
                'ptvarcone20_Nonprompt_All_MaxWeightTTVALooseCone_pt500',
                'ptvarcone30_Nonprompt_All_MaxWeightTTVALooseCone_pt500',
                'ptvarcone40_Nonprompt_All_MaxWeightTTVALooseCone_pt500',
                'ptvarcone20_Nonprompt_All_MaxWeightTTVALooseCone_pt1000',
                'ptvarcone30_Nonprompt_All_MaxWeightTTVALooseCone_pt1000',
                'ptvarcone40_Nonprompt_All_MaxWeightTTVALooseCone_pt1000',
                'ptcone20_Nonprompt_All_MaxWeightTTVALooseCone_pt500',
                'ptcone30_Nonprompt_All_MaxWeightTTVALooseCone_pt500',
                'ptcone40_Nonprompt_All_MaxWeightTTVALooseCone_pt500',
                'ptcone20_Nonprompt_All_MaxWeightTTVALooseCone_pt1000',
                'ptcone30_Nonprompt_All_MaxWeightTTVALooseCone_pt1000',
                'ptcone40_Nonprompt_All_MaxWeightTTVALooseCone_pt1000',
                'numIsolationTypes',
            ],
        },
    'IsolationCaloCorrection':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.Iso',
            'name': 'IsolationCaloCorrection',
            'values': [
                'noneCaloCorrection',
                'coreMuon',
                'core57cells',
                'coreCone',
                'ptCorrection',
                'pileupCorrection',
                'coreConeSC',
                'numIsolationCaloCorrections',
            ],
        },
    'IsolationTrackCorrection':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.Iso',
            'name': 'IsolationTrackCorrection',
            'values': [
                'noneTrackCorrection',
                'coreTrackPtr',
                'coreTrackCone',
                'coreTrackPt',
                'numIsolationTrackCorrections',
            ],
        },
    'IsolationCorrectionParameter':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.Iso',
            'name': 'IsolationCorrectionParameter',
            'values': [
                'coreEnergy',
                'coreArea',
                'NumCorrParameters',
            ],
        },
    'IsolationFlavour':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.Iso',
            'name': 'IsolationFlavour',
            'values': [
                'etcone',
                'ptcone',
                'topoetcone',
                'ptvarcone',
                'neflowisol',
                'ptvarcone_Nonprompt_All_MaxWeightTTVA_pt500',
                'ptvarcone_Nonprompt_All_MaxWeightTTVA_pt1000',
                'ptcone_Nonprompt_All_MaxWeightTTVA_pt500',
                'ptcone_Nonprompt_All_MaxWeightTTVA_pt1000',
                'ptvarcone_Nonprompt_All_MaxWeightTTVALooseCone_pt500',
                'ptvarcone_Nonprompt_All_MaxWeightTTVALooseCone_pt1000',
                'ptcone_Nonprompt_All_MaxWeightTTVALooseCone_pt500',
                'ptcone_Nonprompt_All_MaxWeightTTVALooseCone_pt1000',
                'numIsolationFlavours',
            ],
        },
    'IsolationConeSize':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.Iso',
            'name': 'IsolationConeSize',
            'values': [
                'cone10',
                'cone15',
                'cone20',
                'cone25',
                'cone30',
                'cone35',
                'cone40',
                'cone45',
                'cone50',
                'numIsolationConeSizes',
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


        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class Iso:
    "A class"

    class IsolationType(Enum):
        etcone20 = 2
        etcone30 = 4
        etcone40 = 6
        ptcone20 = 12
        ptcone30 = 14
        ptcone40 = 16
        ptcone50 = 18
        topoetcone20 = 22
        topoetcone30 = 24
        topoetcone40 = 26
        ptvarcone20 = 32
        ptvarcone30 = 34
        ptvarcone40 = 36
        neflowisol20 = 42
        neflowisol30 = 44
        neflowisol40 = 46
        ptvarcone20_Nonprompt_All_MaxWeightTTVA_pt500 = 52
        ptvarcone30_Nonprompt_All_MaxWeightTTVA_pt500 = 54
        ptvarcone40_Nonprompt_All_MaxWeightTTVA_pt500 = 56
        ptvarcone20_Nonprompt_All_MaxWeightTTVA_pt1000 = 62
        ptvarcone30_Nonprompt_All_MaxWeightTTVA_pt1000 = 64
        ptvarcone40_Nonprompt_All_MaxWeightTTVA_pt1000 = 66
        ptcone20_Nonprompt_All_MaxWeightTTVA_pt500 = 72
        ptcone30_Nonprompt_All_MaxWeightTTVA_pt500 = 74
        ptcone40_Nonprompt_All_MaxWeightTTVA_pt500 = 76
        ptcone20_Nonprompt_All_MaxWeightTTVA_pt1000 = 82
        ptcone30_Nonprompt_All_MaxWeightTTVA_pt1000 = 84
        ptcone40_Nonprompt_All_MaxWeightTTVA_pt1000 = 86
        ptvarcone20_Nonprompt_All_MaxWeightTTVALooseCone_pt500 = 92
        ptvarcone30_Nonprompt_All_MaxWeightTTVALooseCone_pt500 = 94
        ptvarcone40_Nonprompt_All_MaxWeightTTVALooseCone_pt500 = 96
        ptvarcone20_Nonprompt_All_MaxWeightTTVALooseCone_pt1000 = 102
        ptvarcone30_Nonprompt_All_MaxWeightTTVALooseCone_pt1000 = 104
        ptvarcone40_Nonprompt_All_MaxWeightTTVALooseCone_pt1000 = 106
        ptcone20_Nonprompt_All_MaxWeightTTVALooseCone_pt500 = 112
        ptcone30_Nonprompt_All_MaxWeightTTVALooseCone_pt500 = 114
        ptcone40_Nonprompt_All_MaxWeightTTVALooseCone_pt500 = 116
        ptcone20_Nonprompt_All_MaxWeightTTVALooseCone_pt1000 = 122
        ptcone30_Nonprompt_All_MaxWeightTTVALooseCone_pt1000 = 124
        ptcone40_Nonprompt_All_MaxWeightTTVALooseCone_pt1000 = 126
        numIsolationTypes = 127

    class IsolationCaloCorrection(Enum):
        noneCaloCorrection = 0
        coreMuon = 1
        core57cells = 2
        coreCone = 3
        ptCorrection = 4
        pileupCorrection = 5
        coreConeSC = 6
        numIsolationCaloCorrections = 7

    class IsolationTrackCorrection(Enum):
        noneTrackCorrection = 0
        coreTrackPtr = 1
        coreTrackCone = 2
        coreTrackPt = 3
        numIsolationTrackCorrections = 4

    class IsolationCorrectionParameter(Enum):
        coreEnergy = 0
        coreArea = 1
        NumCorrParameters = 2

    class IsolationFlavour(Enum):
        etcone = 0
        ptcone = 1
        topoetcone = 2
        ptvarcone = 3
        neflowisol = 4
        ptvarcone_Nonprompt_All_MaxWeightTTVA_pt500 = 5
        ptvarcone_Nonprompt_All_MaxWeightTTVA_pt1000 = 6
        ptcone_Nonprompt_All_MaxWeightTTVA_pt500 = 7
        ptcone_Nonprompt_All_MaxWeightTTVA_pt1000 = 8
        ptvarcone_Nonprompt_All_MaxWeightTTVALooseCone_pt500 = 9
        ptvarcone_Nonprompt_All_MaxWeightTTVALooseCone_pt1000 = 10
        ptcone_Nonprompt_All_MaxWeightTTVALooseCone_pt500 = 11
        ptcone_Nonprompt_All_MaxWeightTTVALooseCone_pt1000 = 12
        numIsolationFlavours = 13

    class IsolationConeSize(Enum):
        cone10 = 0
        cone15 = 1
        cone20 = 2
        cone25 = 3
        cone30 = 4
        cone35 = 5
        cone40 = 6
        cone45 = 7
        cone50 = 8
        numIsolationConeSizes = 9


    def toCString(self, corr: func_adl_servicex_xaodr22.xAOD.iso.Iso.IsolationCaloCorrection) -> str:
        "A method"
        ...
