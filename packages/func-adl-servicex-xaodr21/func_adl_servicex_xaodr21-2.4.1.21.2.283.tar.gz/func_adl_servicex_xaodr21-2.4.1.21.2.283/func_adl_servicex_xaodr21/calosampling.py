from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr21

_method_map = {
    'getNumberOfSamplings': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'CaloSampling',
        'method_name': 'getNumberOfSamplings',
        'return_type': 'unsigned int',
    },
    'getSamplingPattern': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'CaloSampling',
        'method_name': 'getSamplingPattern',
        'return_type': 'unsigned int',
    },
    'barrelPattern': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'CaloSampling',
        'method_name': 'barrelPattern',
        'return_type': 'unsigned int',
    },
    'endcapPattern': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'CaloSampling',
        'method_name': 'endcapPattern',
        'return_type': 'unsigned int',
    },
    'getSamplingName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'CaloSampling',
        'method_name': 'getSamplingName',
        'return_type': 'string',
    },
}

_enum_function_map = {
    'getSamplingPattern': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'CaloSampling',
            'name': 'CaloSample',
            'values': [
                'PreSamplerB',
                'EMB1',
                'EMB2',
                'EMB3',
                'PreSamplerE',
                'EME1',
                'EME2',
                'EME3',
                'HEC0',
                'HEC1',
                'HEC2',
                'HEC3',
                'TileBar0',
                'TileBar1',
                'TileBar2',
                'TileGap1',
                'TileGap2',
                'TileGap3',
                'TileExt0',
                'TileExt1',
                'TileExt2',
                'FCAL0',
                'FCAL1',
                'FCAL2',
                'MINIFCAL0',
                'MINIFCAL1',
                'MINIFCAL2',
                'MINIFCAL3',
                'Unknown',
            ],
        },
    ],
    'getSamplingName': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'CaloSampling',
            'name': 'CaloSample',
            'values': [
                'PreSamplerB',
                'EMB1',
                'EMB2',
                'EMB3',
                'PreSamplerE',
                'EME1',
                'EME2',
                'EME3',
                'HEC0',
                'HEC1',
                'HEC2',
                'HEC3',
                'TileBar0',
                'TileBar1',
                'TileBar2',
                'TileGap1',
                'TileGap2',
                'TileGap3',
                'TileExt0',
                'TileExt1',
                'TileExt2',
                'FCAL0',
                'FCAL1',
                'FCAL2',
                'MINIFCAL0',
                'MINIFCAL1',
                'MINIFCAL2',
                'MINIFCAL3',
                'Unknown',
            ],
        },
    ],      
}

_defined_enums = {
    'CaloSample':
        {
            'metadata_type': 'define_enum',
            'namespace': 'CaloSampling',
            'name': 'CaloSample',
            'values': [
                'PreSamplerB',
                'EMB1',
                'EMB2',
                'EMB3',
                'PreSamplerE',
                'EME1',
                'EME2',
                'EME3',
                'HEC0',
                'HEC1',
                'HEC2',
                'HEC3',
                'TileBar0',
                'TileBar1',
                'TileBar2',
                'TileGap1',
                'TileGap2',
                'TileGap3',
                'TileExt0',
                'TileExt1',
                'TileExt2',
                'FCAL0',
                'FCAL1',
                'FCAL2',
                'MINIFCAL0',
                'MINIFCAL1',
                'MINIFCAL2',
                'MINIFCAL3',
                'Unknown',
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
class CaloSampling:
    "A class"

    class CaloSample(Enum):
        PreSamplerB = 0
        EMB1 = 1
        EMB2 = 2
        EMB3 = 3
        PreSamplerE = 4
        EME1 = 5
        EME2 = 6
        EME3 = 7
        HEC0 = 8
        HEC1 = 9
        HEC2 = 10
        HEC3 = 11
        TileBar0 = 12
        TileBar1 = 13
        TileBar2 = 14
        TileGap1 = 15
        TileGap2 = 16
        TileGap3 = 17
        TileExt0 = 18
        TileExt1 = 19
        TileExt2 = 20
        FCAL0 = 21
        FCAL1 = 22
        FCAL2 = 23
        MINIFCAL0 = 24
        MINIFCAL1 = 25
        MINIFCAL2 = 26
        MINIFCAL3 = 27
        Unknown = 28


    def getNumberOfSamplings(self) -> int:
        "A method"
        ...

    def getSamplingPattern(self, s: CaloSampling.CaloSample) -> int:
        "A method"
        ...

    def barrelPattern(self) -> int:
        "A method"
        ...

    def endcapPattern(self) -> int:
        "A method"
        ...

    def getSamplingName(self, theSample: CaloSampling.CaloSample) -> str:
        "A method"
        ...
