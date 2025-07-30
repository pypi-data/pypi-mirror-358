from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr21

_method_map = {
    'DefaultMinimizerType': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::Math::MinimizerOptions',
        'method_name': 'DefaultMinimizerType',
        'return_type': 'const string',
    },
    'DefaultMinimizerAlgo': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::Math::MinimizerOptions',
        'method_name': 'DefaultMinimizerAlgo',
        'return_type': 'const string',
    },
    'DefaultErrorDef': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::Math::MinimizerOptions',
        'method_name': 'DefaultErrorDef',
        'return_type': 'double',
    },
    'DefaultTolerance': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::Math::MinimizerOptions',
        'method_name': 'DefaultTolerance',
        'return_type': 'double',
    },
    'DefaultPrecision': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::Math::MinimizerOptions',
        'method_name': 'DefaultPrecision',
        'return_type': 'double',
    },
    'DefaultMaxFunctionCalls': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::Math::MinimizerOptions',
        'method_name': 'DefaultMaxFunctionCalls',
        'return_type': 'int',
    },
    'DefaultMaxIterations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::Math::MinimizerOptions',
        'method_name': 'DefaultMaxIterations',
        'return_type': 'int',
    },
    'DefaultStrategy': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::Math::MinimizerOptions',
        'method_name': 'DefaultStrategy',
        'return_type': 'int',
    },
    'DefaultPrintLevel': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::Math::MinimizerOptions',
        'method_name': 'DefaultPrintLevel',
        'return_type': 'int',
    },
    'DefaultExtraOptions': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::Math::MinimizerOptions',
        'method_name': 'DefaultExtraOptions',
        'return_type': 'ROOT::Math::IOptions *',
    },
    'Default': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::Math::MinimizerOptions',
        'method_name': 'Default',
        'return_type': 'ROOT::Math::IOptions',
    },
    'FindDefault': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::Math::MinimizerOptions',
        'method_name': 'FindDefault',
        'return_type': 'ROOT::Math::IOptions *',
    },
    'PrintLevel': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::Math::MinimizerOptions',
        'method_name': 'PrintLevel',
        'return_type': 'int',
    },
    'MaxFunctionCalls': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::Math::MinimizerOptions',
        'method_name': 'MaxFunctionCalls',
        'return_type': 'unsigned int',
    },
    'MaxIterations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::Math::MinimizerOptions',
        'method_name': 'MaxIterations',
        'return_type': 'unsigned int',
    },
    'Strategy': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::Math::MinimizerOptions',
        'method_name': 'Strategy',
        'return_type': 'int',
    },
    'Tolerance': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::Math::MinimizerOptions',
        'method_name': 'Tolerance',
        'return_type': 'double',
    },
    'Precision': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::Math::MinimizerOptions',
        'method_name': 'Precision',
        'return_type': 'double',
    },
    'ErrorDef': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::Math::MinimizerOptions',
        'method_name': 'ErrorDef',
        'return_type': 'double',
    },
    'ExtraOptions': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::Math::MinimizerOptions',
        'method_name': 'ExtraOptions',
        'return_type': 'const ROOT::Math::IOptions *',
    },
    'MinimizerType': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::Math::MinimizerOptions',
        'method_name': 'MinimizerType',
        'return_type': 'const string',
    },
    'MinimizerAlgorithm': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::Math::MinimizerOptions',
        'method_name': 'MinimizerAlgorithm',
        'return_type': 'const string',
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
class MinimizerOptions:
    "A class"


    def DefaultMinimizerType(self) -> str:
        "A method"
        ...

    def DefaultMinimizerAlgo(self) -> str:
        "A method"
        ...

    def DefaultErrorDef(self) -> float:
        "A method"
        ...

    def DefaultTolerance(self) -> float:
        "A method"
        ...

    def DefaultPrecision(self) -> float:
        "A method"
        ...

    def DefaultMaxFunctionCalls(self) -> int:
        "A method"
        ...

    def DefaultMaxIterations(self) -> int:
        "A method"
        ...

    def DefaultStrategy(self) -> int:
        "A method"
        ...

    def DefaultPrintLevel(self) -> int:
        "A method"
        ...

    def DefaultExtraOptions(self) -> func_adl_servicex_xaodr21.ROOT.Math.ioptions.IOptions:
        "A method"
        ...

    def Default(self, name: int) -> func_adl_servicex_xaodr21.ROOT.Math.ioptions.IOptions:
        "A method"
        ...

    def FindDefault(self, name: int) -> func_adl_servicex_xaodr21.ROOT.Math.ioptions.IOptions:
        "A method"
        ...

    def PrintLevel(self) -> int:
        "A method"
        ...

    def MaxFunctionCalls(self) -> int:
        "A method"
        ...

    def MaxIterations(self) -> int:
        "A method"
        ...

    def Strategy(self) -> int:
        "A method"
        ...

    def Tolerance(self) -> float:
        "A method"
        ...

    def Precision(self) -> float:
        "A method"
        ...

    def ErrorDef(self) -> float:
        "A method"
        ...

    def ExtraOptions(self) -> func_adl_servicex_xaodr21.ROOT.Math.ioptions.IOptions:
        "A method"
        ...

    def MinimizerType(self) -> str:
        "A method"
        ...

    def MinimizerAlgorithm(self) -> str:
        "A method"
        ...
