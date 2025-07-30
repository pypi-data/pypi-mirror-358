from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr21

_method_map = {
    'sync_with_stdio': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ios_base',
        'method_name': 'sync_with_stdio',
        'return_type': 'bool',
    },
    'imbue': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ios_base',
        'method_name': 'imbue',
        'return_type': 'locale',
    },
    'getloc': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ios_base',
        'method_name': 'getloc',
        'return_type': 'locale',
    },
    '_M_getloc': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ios_base',
        'method_name': '_M_getloc',
        'return_type': 'const locale',
    },
    'xalloc': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ios_base',
        'method_name': 'xalloc',
        'return_type': 'int',
    },
    'iword': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ios_base',
        'method_name': 'iword',
        'return_type': 'long',
    },
}

_enum_function_map = {      
}

_defined_enums = {
    'event':
        {
            'metadata_type': 'define_enum',
            'namespace': 'ios_base',
            'name': 'event',
            'values': [
                'erase_event',
                'imbue_event',
                'copyfmt_event',
            ],
        },      
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


        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class ios_base:
    "A class"

    class event(Enum):
        erase_event = 0
        imbue_event = 1
        copyfmt_event = 2


    def sync_with_stdio(self, __sync: bool) -> bool:
        "A method"
        ...

    def imbue(self, __loc: func_adl_servicex_xaodr21.locale.locale) -> func_adl_servicex_xaodr21.locale.locale:
        "A method"
        ...

    def getloc(self) -> func_adl_servicex_xaodr21.locale.locale:
        "A method"
        ...

    def _M_getloc(self) -> func_adl_servicex_xaodr21.locale.locale:
        "A method"
        ...

    def xalloc(self) -> int:
        "A method"
        ...

    def iword(self, __ix: int) -> int:
        "A method"
        ...
