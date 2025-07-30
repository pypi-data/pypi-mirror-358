from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr21

_method_map = {
    'x': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonSegment_v1',
        'method_name': 'x',
        'return_type': 'float',
    },
    'y': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonSegment_v1',
        'method_name': 'y',
        'return_type': 'float',
    },
    'z': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonSegment_v1',
        'method_name': 'z',
        'return_type': 'float',
    },
    'px': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonSegment_v1',
        'method_name': 'px',
        'return_type': 'float',
    },
    'py': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonSegment_v1',
        'method_name': 'py',
        'return_type': 'float',
    },
    'pz': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonSegment_v1',
        'method_name': 'pz',
        'return_type': 'float',
    },
    't0': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonSegment_v1',
        'method_name': 't0',
        'return_type': 'float',
    },
    't0error': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonSegment_v1',
        'method_name': 't0error',
        'return_type': 'float',
    },
    'chiSquared': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonSegment_v1',
        'method_name': 'chiSquared',
        'return_type': 'float',
    },
    'numberDoF': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonSegment_v1',
        'method_name': 'numberDoF',
        'return_type': 'float',
    },
    'sector': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonSegment_v1',
        'method_name': 'sector',
        'return_type': 'int',
    },
    'chamberIndex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonSegment_v1',
        'method_name': 'chamberIndex',
        'return_type': 'Muon::MuonStationIndex::ChIndex',
    },
    'etaIndex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonSegment_v1',
        'method_name': 'etaIndex',
        'return_type': 'int',
    },
    'technology': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonSegment_v1',
        'method_name': 'technology',
        'return_type': 'Muon::MuonStationIndex::TechnologyIndex',
    },
    'nPrecisionHits': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonSegment_v1',
        'method_name': 'nPrecisionHits',
        'return_type': 'int',
    },
    'nPhiLayers': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonSegment_v1',
        'method_name': 'nPhiLayers',
        'return_type': 'int',
    },
    'nTrigEtaLayers': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonSegment_v1',
        'method_name': 'nTrigEtaLayers',
        'return_type': 'int',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonSegment_v1',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonSegment_v1',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonSegment_v1',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonSegment_v1',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonSegment_v1',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonSegment_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonSegment_v1',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::MuonSegment_v1',
        'method_name': 'isAvailable',
        'return_type': 'bool',
    },
}

_enum_function_map = {
    'chamberIndex': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'Muon.MuonStationIndex',
            'name': 'ChIndex',
            'values': [
                'ChUnknown',
                'BIS',
                'BIL',
                'BMS',
                'BML',
                'BOS',
                'BOL',
                'BEE',
                'EIS',
                'EIL',
                'EMS',
                'EML',
                'EOS',
                'EOL',
                'EES',
                'EEL',
                'CSS',
                'CSL',
                'ChIndexMax',
            ],
        },
    ],
    'technology': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'Muon.MuonStationIndex',
            'name': 'TechnologyIndex',
            'values': [
                'TechnologyUnknown',
                'MDT',
                'CSCI',
                'RPC',
                'TGC',
                'STGC',
                'MM',
                'TechnologyIndexMax',
            ],
        },
    ],      
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
            'name': 'xAODMuon/versions/MuonSegment_v1.h',
            'body_includes': ["xAODMuon/versions/MuonSegment_v1.h"],
        })


        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODMuon',
            'link_libraries': ["xAODMuon"],
        })

        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class MuonSegment_v1:
    "A class"


    def x(self) -> float:
        "A method"
        ...

    def y(self) -> float:
        "A method"
        ...

    def z(self) -> float:
        "A method"
        ...

    def px(self) -> float:
        "A method"
        ...

    def py(self) -> float:
        "A method"
        ...

    def pz(self) -> float:
        "A method"
        ...

    def t0(self) -> float:
        "A method"
        ...

    def t0error(self) -> float:
        "A method"
        ...

    def chiSquared(self) -> float:
        "A method"
        ...

    def numberDoF(self) -> float:
        "A method"
        ...

    def sector(self) -> int:
        "A method"
        ...

    def chamberIndex(self) -> func_adl_servicex_xaodr21.Muon.muonstationindex.MuonStationIndex.ChIndex:
        "A method"
        ...

    def etaIndex(self) -> int:
        "A method"
        ...

    def technology(self) -> func_adl_servicex_xaodr21.Muon.muonstationindex.MuonStationIndex.TechnologyIndex:
        "A method"
        ...

    def nPrecisionHits(self) -> int:
        "A method"
        ...

    def nPhiLayers(self) -> int:
        "A method"
        ...

    def nTrigEtaLayers(self) -> int:
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

    @func_adl_parameterized_call(lambda s, a, param_1: func_adl_servicex_xaodr21.type_support.cpp_generic_1arg_callback('auxdataConst', s, a, param_1))
    @property
    def auxdataConst(self) -> func_adl_servicex_xaodr21.type_support.index_type_forwarder[str]:
        "A method"
        ...

    @func_adl_parameterized_call(lambda s, a, param_1: func_adl_servicex_xaodr21.type_support.cpp_generic_1arg_callback('isAvailable', s, a, param_1))
    @property
    def isAvailable(self) -> func_adl_servicex_xaodr21.type_support.index_type_forwarder[str]:
        "A method"
        ...
