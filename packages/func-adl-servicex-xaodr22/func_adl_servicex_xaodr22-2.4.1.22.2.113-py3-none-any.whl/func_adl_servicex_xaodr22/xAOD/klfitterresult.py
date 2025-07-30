from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr22

_method_map = {
    'selectionCode': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'selectionCode',
        'return_type': 'unsigned int',
    },
    'minuitDidNotConverge': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'minuitDidNotConverge',
        'return_type': 'short',
    },
    'fitAbortedDueToNaN': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'fitAbortedDueToNaN',
        'return_type': 'short',
    },
    'atLeastOneFitParameterAtItsLimit': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'atLeastOneFitParameterAtItsLimit',
        'return_type': 'short',
    },
    'invalidTransferFunctionAtConvergence': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'invalidTransferFunctionAtConvergence',
        'return_type': 'short',
    },
    'bestPermutation': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'bestPermutation',
        'return_type': 'unsigned int',
    },
    'logLikelihood': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'logLikelihood',
        'return_type': 'float',
    },
    'eventProbability': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'eventProbability',
        'return_type': 'float',
    },
    'parameters': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'parameters',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<double>',
    },
    'parameterErrors': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'parameterErrors',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<double>',
    },
    'model_bhad_pt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_bhad_pt',
        'return_type': 'float',
    },
    'model_bhad_eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_bhad_eta',
        'return_type': 'float',
    },
    'model_bhad_phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_bhad_phi',
        'return_type': 'float',
    },
    'model_bhad_E': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_bhad_E',
        'return_type': 'float',
    },
    'model_bhad_jetIndex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_bhad_jetIndex',
        'return_type': 'unsigned int',
    },
    'model_blep_pt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_blep_pt',
        'return_type': 'float',
    },
    'model_blep_eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_blep_eta',
        'return_type': 'float',
    },
    'model_blep_phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_blep_phi',
        'return_type': 'float',
    },
    'model_blep_E': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_blep_E',
        'return_type': 'float',
    },
    'model_blep_jetIndex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_blep_jetIndex',
        'return_type': 'unsigned int',
    },
    'model_lq1_pt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lq1_pt',
        'return_type': 'float',
    },
    'model_lq1_eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lq1_eta',
        'return_type': 'float',
    },
    'model_lq1_phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lq1_phi',
        'return_type': 'float',
    },
    'model_lq1_E': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lq1_E',
        'return_type': 'float',
    },
    'model_lq1_jetIndex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lq1_jetIndex',
        'return_type': 'unsigned int',
    },
    'model_lq2_pt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lq2_pt',
        'return_type': 'float',
    },
    'model_lq2_eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lq2_eta',
        'return_type': 'float',
    },
    'model_lq2_phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lq2_phi',
        'return_type': 'float',
    },
    'model_lq2_E': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lq2_E',
        'return_type': 'float',
    },
    'model_lq2_jetIndex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lq2_jetIndex',
        'return_type': 'unsigned int',
    },
    'model_Higgs_b1_pt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_Higgs_b1_pt',
        'return_type': 'float',
    },
    'model_Higgs_b1_eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_Higgs_b1_eta',
        'return_type': 'float',
    },
    'model_Higgs_b1_phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_Higgs_b1_phi',
        'return_type': 'float',
    },
    'model_Higgs_b1_E': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_Higgs_b1_E',
        'return_type': 'float',
    },
    'model_Higgs_b1_jetIndex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_Higgs_b1_jetIndex',
        'return_type': 'unsigned int',
    },
    'model_Higgs_b2_pt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_Higgs_b2_pt',
        'return_type': 'float',
    },
    'model_Higgs_b2_eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_Higgs_b2_eta',
        'return_type': 'float',
    },
    'model_Higgs_b2_phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_Higgs_b2_phi',
        'return_type': 'float',
    },
    'model_Higgs_b2_E': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_Higgs_b2_E',
        'return_type': 'float',
    },
    'model_Higgs_b2_jetIndex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_Higgs_b2_jetIndex',
        'return_type': 'unsigned int',
    },
    'model_lep_pt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lep_pt',
        'return_type': 'float',
    },
    'model_lep_eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lep_eta',
        'return_type': 'float',
    },
    'model_lep_phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lep_phi',
        'return_type': 'float',
    },
    'model_lep_E': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lep_E',
        'return_type': 'float',
    },
    'model_lep_index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lep_index',
        'return_type': 'unsigned int',
    },
    'model_lepZ1_pt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lepZ1_pt',
        'return_type': 'float',
    },
    'model_lepZ1_eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lepZ1_eta',
        'return_type': 'float',
    },
    'model_lepZ1_phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lepZ1_phi',
        'return_type': 'float',
    },
    'model_lepZ1_E': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lepZ1_E',
        'return_type': 'float',
    },
    'model_lepZ1_index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lepZ1_index',
        'return_type': 'unsigned int',
    },
    'model_lepZ2_pt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lepZ2_pt',
        'return_type': 'float',
    },
    'model_lepZ2_eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lepZ2_eta',
        'return_type': 'float',
    },
    'model_lepZ2_phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lepZ2_phi',
        'return_type': 'float',
    },
    'model_lepZ2_E': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lepZ2_E',
        'return_type': 'float',
    },
    'model_lepZ2_index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lepZ2_index',
        'return_type': 'unsigned int',
    },
    'model_nu_pt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_nu_pt',
        'return_type': 'float',
    },
    'model_nu_eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_nu_eta',
        'return_type': 'float',
    },
    'model_nu_phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_nu_phi',
        'return_type': 'float',
    },
    'model_nu_E': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_nu_E',
        'return_type': 'float',
    },
    'model_b_from_top1_pt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_b_from_top1_pt',
        'return_type': 'float',
    },
    'model_b_from_top1_eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_b_from_top1_eta',
        'return_type': 'float',
    },
    'model_b_from_top1_phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_b_from_top1_phi',
        'return_type': 'float',
    },
    'model_b_from_top1_E': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_b_from_top1_E',
        'return_type': 'float',
    },
    'model_b_from_top1_jetIndex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_b_from_top1_jetIndex',
        'return_type': 'unsigned int',
    },
    'model_b_from_top2_pt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_b_from_top2_pt',
        'return_type': 'float',
    },
    'model_b_from_top2_eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_b_from_top2_eta',
        'return_type': 'float',
    },
    'model_b_from_top2_phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_b_from_top2_phi',
        'return_type': 'float',
    },
    'model_b_from_top2_E': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_b_from_top2_E',
        'return_type': 'float',
    },
    'model_b_from_top2_jetIndex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_b_from_top2_jetIndex',
        'return_type': 'unsigned int',
    },
    'model_lj1_from_top1_pt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lj1_from_top1_pt',
        'return_type': 'float',
    },
    'model_lj1_from_top1_eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lj1_from_top1_eta',
        'return_type': 'float',
    },
    'model_lj1_from_top1_phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lj1_from_top1_phi',
        'return_type': 'float',
    },
    'model_lj1_from_top1_E': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lj1_from_top1_E',
        'return_type': 'float',
    },
    'model_lj1_from_top1_jetIndex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lj1_from_top1_jetIndex',
        'return_type': 'unsigned int',
    },
    'model_lj2_from_top1_pt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lj2_from_top1_pt',
        'return_type': 'float',
    },
    'model_lj2_from_top1_eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lj2_from_top1_eta',
        'return_type': 'float',
    },
    'model_lj2_from_top1_phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lj2_from_top1_phi',
        'return_type': 'float',
    },
    'model_lj2_from_top1_E': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lj2_from_top1_E',
        'return_type': 'float',
    },
    'model_lj2_from_top1_jetIndex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lj2_from_top1_jetIndex',
        'return_type': 'unsigned int',
    },
    'model_lj1_from_top2_pt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lj1_from_top2_pt',
        'return_type': 'float',
    },
    'model_lj1_from_top2_eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lj1_from_top2_eta',
        'return_type': 'float',
    },
    'model_lj1_from_top2_phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lj1_from_top2_phi',
        'return_type': 'float',
    },
    'model_lj1_from_top2_E': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lj1_from_top2_E',
        'return_type': 'float',
    },
    'model_lj1_from_top2_jetIndex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lj1_from_top2_jetIndex',
        'return_type': 'unsigned int',
    },
    'model_lj2_from_top2_pt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lj2_from_top2_pt',
        'return_type': 'float',
    },
    'model_lj2_from_top2_eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lj2_from_top2_eta',
        'return_type': 'float',
    },
    'model_lj2_from_top2_phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lj2_from_top2_phi',
        'return_type': 'float',
    },
    'model_lj2_from_top2_E': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lj2_from_top2_E',
        'return_type': 'float',
    },
    'model_lj2_from_top2_jetIndex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'model_lj2_from_top2_jetIndex',
        'return_type': 'unsigned int',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'trackIndices',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::KLFitterResult',
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
            'name': 'TopEvent/KLFitterResult.h',
            'body_includes': ["TopEvent/KLFitterResult.h"],
        })


        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'TopEvent',
            'link_libraries': ["TopEvent"],
        })

        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class KLFitterResult:
    "A class"


    def selectionCode(self) -> int:
        "A method"
        ...

    def minuitDidNotConverge(self) -> int:
        "A method"
        ...

    def fitAbortedDueToNaN(self) -> int:
        "A method"
        ...

    def atLeastOneFitParameterAtItsLimit(self) -> int:
        "A method"
        ...

    def invalidTransferFunctionAtConvergence(self) -> int:
        "A method"
        ...

    def bestPermutation(self) -> int:
        "A method"
        ...

    def logLikelihood(self) -> float:
        "A method"
        ...

    def eventProbability(self) -> float:
        "A method"
        ...

    def parameters(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def parameterErrors(self) -> func_adl_servicex_xaodr22.vector_float_.vector_float_:
        "A method"
        ...

    def model_bhad_pt(self) -> float:
        "A method"
        ...

    def model_bhad_eta(self) -> float:
        "A method"
        ...

    def model_bhad_phi(self) -> float:
        "A method"
        ...

    def model_bhad_E(self) -> float:
        "A method"
        ...

    def model_bhad_jetIndex(self) -> int:
        "A method"
        ...

    def model_blep_pt(self) -> float:
        "A method"
        ...

    def model_blep_eta(self) -> float:
        "A method"
        ...

    def model_blep_phi(self) -> float:
        "A method"
        ...

    def model_blep_E(self) -> float:
        "A method"
        ...

    def model_blep_jetIndex(self) -> int:
        "A method"
        ...

    def model_lq1_pt(self) -> float:
        "A method"
        ...

    def model_lq1_eta(self) -> float:
        "A method"
        ...

    def model_lq1_phi(self) -> float:
        "A method"
        ...

    def model_lq1_E(self) -> float:
        "A method"
        ...

    def model_lq1_jetIndex(self) -> int:
        "A method"
        ...

    def model_lq2_pt(self) -> float:
        "A method"
        ...

    def model_lq2_eta(self) -> float:
        "A method"
        ...

    def model_lq2_phi(self) -> float:
        "A method"
        ...

    def model_lq2_E(self) -> float:
        "A method"
        ...

    def model_lq2_jetIndex(self) -> int:
        "A method"
        ...

    def model_Higgs_b1_pt(self) -> float:
        "A method"
        ...

    def model_Higgs_b1_eta(self) -> float:
        "A method"
        ...

    def model_Higgs_b1_phi(self) -> float:
        "A method"
        ...

    def model_Higgs_b1_E(self) -> float:
        "A method"
        ...

    def model_Higgs_b1_jetIndex(self) -> int:
        "A method"
        ...

    def model_Higgs_b2_pt(self) -> float:
        "A method"
        ...

    def model_Higgs_b2_eta(self) -> float:
        "A method"
        ...

    def model_Higgs_b2_phi(self) -> float:
        "A method"
        ...

    def model_Higgs_b2_E(self) -> float:
        "A method"
        ...

    def model_Higgs_b2_jetIndex(self) -> int:
        "A method"
        ...

    def model_lep_pt(self) -> float:
        "A method"
        ...

    def model_lep_eta(self) -> float:
        "A method"
        ...

    def model_lep_phi(self) -> float:
        "A method"
        ...

    def model_lep_E(self) -> float:
        "A method"
        ...

    def model_lep_index(self) -> int:
        "A method"
        ...

    def model_lepZ1_pt(self) -> float:
        "A method"
        ...

    def model_lepZ1_eta(self) -> float:
        "A method"
        ...

    def model_lepZ1_phi(self) -> float:
        "A method"
        ...

    def model_lepZ1_E(self) -> float:
        "A method"
        ...

    def model_lepZ1_index(self) -> int:
        "A method"
        ...

    def model_lepZ2_pt(self) -> float:
        "A method"
        ...

    def model_lepZ2_eta(self) -> float:
        "A method"
        ...

    def model_lepZ2_phi(self) -> float:
        "A method"
        ...

    def model_lepZ2_E(self) -> float:
        "A method"
        ...

    def model_lepZ2_index(self) -> int:
        "A method"
        ...

    def model_nu_pt(self) -> float:
        "A method"
        ...

    def model_nu_eta(self) -> float:
        "A method"
        ...

    def model_nu_phi(self) -> float:
        "A method"
        ...

    def model_nu_E(self) -> float:
        "A method"
        ...

    def model_b_from_top1_pt(self) -> float:
        "A method"
        ...

    def model_b_from_top1_eta(self) -> float:
        "A method"
        ...

    def model_b_from_top1_phi(self) -> float:
        "A method"
        ...

    def model_b_from_top1_E(self) -> float:
        "A method"
        ...

    def model_b_from_top1_jetIndex(self) -> int:
        "A method"
        ...

    def model_b_from_top2_pt(self) -> float:
        "A method"
        ...

    def model_b_from_top2_eta(self) -> float:
        "A method"
        ...

    def model_b_from_top2_phi(self) -> float:
        "A method"
        ...

    def model_b_from_top2_E(self) -> float:
        "A method"
        ...

    def model_b_from_top2_jetIndex(self) -> int:
        "A method"
        ...

    def model_lj1_from_top1_pt(self) -> float:
        "A method"
        ...

    def model_lj1_from_top1_eta(self) -> float:
        "A method"
        ...

    def model_lj1_from_top1_phi(self) -> float:
        "A method"
        ...

    def model_lj1_from_top1_E(self) -> float:
        "A method"
        ...

    def model_lj1_from_top1_jetIndex(self) -> int:
        "A method"
        ...

    def model_lj2_from_top1_pt(self) -> float:
        "A method"
        ...

    def model_lj2_from_top1_eta(self) -> float:
        "A method"
        ...

    def model_lj2_from_top1_phi(self) -> float:
        "A method"
        ...

    def model_lj2_from_top1_E(self) -> float:
        "A method"
        ...

    def model_lj2_from_top1_jetIndex(self) -> int:
        "A method"
        ...

    def model_lj1_from_top2_pt(self) -> float:
        "A method"
        ...

    def model_lj1_from_top2_eta(self) -> float:
        "A method"
        ...

    def model_lj1_from_top2_phi(self) -> float:
        "A method"
        ...

    def model_lj1_from_top2_E(self) -> float:
        "A method"
        ...

    def model_lj1_from_top2_jetIndex(self) -> int:
        "A method"
        ...

    def model_lj2_from_top2_pt(self) -> float:
        "A method"
        ...

    def model_lj2_from_top2_eta(self) -> float:
        "A method"
        ...

    def model_lj2_from_top2_phi(self) -> float:
        "A method"
        ...

    def model_lj2_from_top2_E(self) -> float:
        "A method"
        ...

    def model_lj2_from_top2_jetIndex(self) -> int:
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
