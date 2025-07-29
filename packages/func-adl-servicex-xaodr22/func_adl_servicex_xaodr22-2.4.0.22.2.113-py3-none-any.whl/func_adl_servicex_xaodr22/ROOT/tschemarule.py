from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr22

_method_map = {
    'SetFromRule': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::TSchemaRule',
        'method_name': 'SetFromRule',
        'return_type': 'bool',
    },
    'GetVersion': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::TSchemaRule',
        'method_name': 'GetVersion',
        'return_type': 'const char *',
    },
    'TestVersion': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::TSchemaRule',
        'method_name': 'TestVersion',
        'return_type': 'bool',
    },
    'TestChecksum': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::TSchemaRule',
        'method_name': 'TestChecksum',
        'return_type': 'bool',
    },
    'GetSourceClass': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::TSchemaRule',
        'method_name': 'GetSourceClass',
        'return_type': 'const char *',
    },
    'GetTargetClass': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::TSchemaRule',
        'method_name': 'GetTargetClass',
        'return_type': 'const char *',
    },
    'GetTargetString': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::TSchemaRule',
        'method_name': 'GetTargetString',
        'return_type': 'const char *',
    },
    'GetEmbed': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::TSchemaRule',
        'method_name': 'GetEmbed',
        'return_type': 'bool',
    },
    'IsAliasRule': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::TSchemaRule',
        'method_name': 'IsAliasRule',
        'return_type': 'bool',
    },
    'IsRenameRule': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::TSchemaRule',
        'method_name': 'IsRenameRule',
        'return_type': 'bool',
    },
    'IsValid': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::TSchemaRule',
        'method_name': 'IsValid',
        'return_type': 'bool',
    },
    'GetCode': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::TSchemaRule',
        'method_name': 'GetCode',
        'return_type': 'const char *',
    },
    'GetAttributes': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::TSchemaRule',
        'method_name': 'GetAttributes',
        'return_type': 'const char *',
    },
    'Conflicts': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::TSchemaRule',
        'method_name': 'Conflicts',
        'return_type': 'bool',
    },
    'DeclFileName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::TSchemaRule',
        'method_name': 'DeclFileName',
        'return_type': 'const char *',
    },
    'ImplFileLine': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::TSchemaRule',
        'method_name': 'ImplFileLine',
        'return_type': 'int',
    },
    'ImplFileName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::TSchemaRule',
        'method_name': 'ImplFileName',
        'return_type': 'const char *',
    },
    'Class_Name': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::TSchemaRule',
        'method_name': 'Class_Name',
        'return_type': 'const char *',
    },
    'DeclFileLine': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::TSchemaRule',
        'method_name': 'DeclFileLine',
        'return_type': 'int',
    },
    'Hash': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::TSchemaRule',
        'method_name': 'Hash',
        'return_type': 'unsigned long',
    },
    'ClassName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::TSchemaRule',
        'method_name': 'ClassName',
        'return_type': 'const char *',
    },
    'CheckedHash': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::TSchemaRule',
        'method_name': 'CheckedHash',
        'return_type': 'unsigned long',
    },
    'DistancetoPrimitive': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::TSchemaRule',
        'method_name': 'DistancetoPrimitive',
        'return_type': 'int',
    },
    'GetUniqueID': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::TSchemaRule',
        'method_name': 'GetUniqueID',
        'return_type': 'unsigned int',
    },
    'GetName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::TSchemaRule',
        'method_name': 'GetName',
        'return_type': 'const char *',
    },
    'GetIconName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::TSchemaRule',
        'method_name': 'GetIconName',
        'return_type': 'const char *',
    },
    'GetObjectInfo': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::TSchemaRule',
        'method_name': 'GetObjectInfo',
        'return_type': 'char *',
    },
    'GetTitle': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::TSchemaRule',
        'method_name': 'GetTitle',
        'return_type': 'const char *',
    },
    'HasInconsistentHash': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::TSchemaRule',
        'method_name': 'HasInconsistentHash',
        'return_type': 'bool',
    },
    'InheritsFrom': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::TSchemaRule',
        'method_name': 'InheritsFrom',
        'return_type': 'bool',
    },
    'IsFolder': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::TSchemaRule',
        'method_name': 'IsFolder',
        'return_type': 'bool',
    },
    'IsSortable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::TSchemaRule',
        'method_name': 'IsSortable',
        'return_type': 'bool',
    },
    'IsOnHeap': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::TSchemaRule',
        'method_name': 'IsOnHeap',
        'return_type': 'bool',
    },
    'IsZombie': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::TSchemaRule',
        'method_name': 'IsZombie',
        'return_type': 'bool',
    },
    'Notify': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::TSchemaRule',
        'method_name': 'Notify',
        'return_type': 'bool',
    },
    'Read': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::TSchemaRule',
        'method_name': 'Read',
        'return_type': 'int',
    },
    'Write': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::TSchemaRule',
        'method_name': 'Write',
        'return_type': 'int',
    },
    'IsDestructed': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::TSchemaRule',
        'method_name': 'IsDestructed',
        'return_type': 'bool',
    },
    'TestBit': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::TSchemaRule',
        'method_name': 'TestBit',
        'return_type': 'bool',
    },
    'TestBits': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::TSchemaRule',
        'method_name': 'TestBits',
        'return_type': 'int',
    },
    'GetObjectStat': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::TSchemaRule',
        'method_name': 'GetObjectStat',
        'return_type': 'bool',
    },
}

_enum_function_map = {      
}

_defined_enums = {      
}

_object_cpp_as_py_namespace="ROOT"

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
class TSchemaRule:
    "A class"


    def SetFromRule(self, rule: int) -> bool:
        "A method"
        ...

    def GetVersion(self) -> str:
        "A method"
        ...

    def TestVersion(self, version: int) -> bool:
        "A method"
        ...

    def TestChecksum(self, checksum: int) -> bool:
        "A method"
        ...

    def GetSourceClass(self) -> str:
        "A method"
        ...

    def GetTargetClass(self) -> str:
        "A method"
        ...

    def GetTargetString(self) -> str:
        "A method"
        ...

    def GetEmbed(self) -> bool:
        "A method"
        ...

    def IsAliasRule(self) -> bool:
        "A method"
        ...

    def IsRenameRule(self) -> bool:
        "A method"
        ...

    def IsValid(self) -> bool:
        "A method"
        ...

    def GetCode(self) -> str:
        "A method"
        ...

    def GetAttributes(self) -> str:
        "A method"
        ...

    def Conflicts(self, rule: func_adl_servicex_xaodr22.ROOT.tschemarule.TSchemaRule) -> bool:
        "A method"
        ...

    def DeclFileName(self) -> str:
        "A method"
        ...

    def ImplFileLine(self) -> int:
        "A method"
        ...

    def ImplFileName(self) -> str:
        "A method"
        ...

    def Class_Name(self) -> str:
        "A method"
        ...

    def DeclFileLine(self) -> int:
        "A method"
        ...

    def Hash(self) -> int:
        "A method"
        ...

    def ClassName(self) -> str:
        "A method"
        ...

    def CheckedHash(self) -> int:
        "A method"
        ...

    def DistancetoPrimitive(self, px: int, py: int) -> int:
        "A method"
        ...

    def GetUniqueID(self) -> int:
        "A method"
        ...

    def GetName(self) -> str:
        "A method"
        ...

    def GetIconName(self) -> str:
        "A method"
        ...

    def GetObjectInfo(self, px: int, py: int) -> str:
        "A method"
        ...

    def GetTitle(self) -> str:
        "A method"
        ...

    def HasInconsistentHash(self) -> bool:
        "A method"
        ...

    def InheritsFrom(self, classname: int) -> bool:
        "A method"
        ...

    def IsFolder(self) -> bool:
        "A method"
        ...

    def IsSortable(self) -> bool:
        "A method"
        ...

    def IsOnHeap(self) -> bool:
        "A method"
        ...

    def IsZombie(self) -> bool:
        "A method"
        ...

    def Notify(self) -> bool:
        "A method"
        ...

    def Read(self, name: int) -> int:
        "A method"
        ...

    def Write(self, name: int, option: int, bufsize: int) -> int:
        "A method"
        ...

    def IsDestructed(self) -> bool:
        "A method"
        ...

    def TestBit(self, f: int) -> bool:
        "A method"
        ...

    def TestBits(self, f: int) -> int:
        "A method"
        ...

    def GetObjectStat(self) -> bool:
        "A method"
        ...
