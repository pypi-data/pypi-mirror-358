from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr21

_method_map = {
    'Clone': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::Math::IOptions',
        'method_name': 'Clone',
        'return_type': 'ROOT::Math::IOptions *',
    },
    'RValue': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::Math::IOptions',
        'method_name': 'RValue',
        'return_type': 'double',
    },
    'IValue': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::Math::IOptions',
        'method_name': 'IValue',
        'return_type': 'int',
    },
    'NamedValue': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::Math::IOptions',
        'method_name': 'NamedValue',
        'return_type': 'string',
    },
    'GetRealValue': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::Math::IOptions',
        'method_name': 'GetRealValue',
        'return_type': 'bool',
    },
    'GetIntValue': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::Math::IOptions',
        'method_name': 'GetIntValue',
        'return_type': 'bool',
    },
    'GetNamedValue': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::Math::IOptions',
        'method_name': 'GetNamedValue',
        'return_type': 'bool',
    },
}

_enum_function_map = {      
}

_defined_enums = {      
}

_object_cpp_as_py_namespace="ROOT.Math"

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
class IOptions:
    "A class"


    def Clone(self) -> func_adl_servicex_xaodr21.ROOT.Math.ioptions.IOptions:
        "A method"
        ...

    def RValue(self, name: int) -> float:
        "A method"
        ...

    def IValue(self, name: int) -> int:
        "A method"
        ...

    def NamedValue(self, name: int) -> str:
        "A method"
        ...

    def GetRealValue(self, noname_arg: int, noname_arg_1: float) -> bool:
        "A method"
        ...

    def GetIntValue(self, noname_arg: int, noname_arg_1: int) -> bool:
        "A method"
        ...

    def GetNamedValue(self, noname_arg: int, noname_arg_1: str) -> bool:
        "A method"
        ...
