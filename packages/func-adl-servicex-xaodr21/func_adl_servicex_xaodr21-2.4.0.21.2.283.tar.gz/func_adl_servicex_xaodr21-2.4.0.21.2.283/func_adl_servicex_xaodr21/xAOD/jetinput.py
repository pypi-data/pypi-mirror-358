from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr21

_method_map = {
    'isValidConstitType': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetInput',
        'method_name': 'isValidConstitType',
        'return_type': 'bool',
    },
    'typeName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetInput',
        'method_name': 'typeName',
        'return_type': 'const string',
    },
    'inputType': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetInput',
        'method_name': 'inputType',
        'return_type': 'xAOD::JetInput::Type',
    },
}

_enum_function_map = {
    'isValidConstitType': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.JetInput',
            'name': 'Type',
            'values': [
                'LCTopo',
                'EMTopo',
                'TopoTower',
                'Tower',
                'Truth',
                'TruthWZ',
                'Track',
                'PFlow',
                'LCPFlow',
                'EMPFlow',
                'EMCPFlow',
                'Jet',
                'LCTopoOrigin',
                'EMTopoOrigin',
                'TrackCaloCluster',
                'UFO',
                'UFOCHS',
                'UFOCSSK',
                'TruthDressedWZ',
                'EMTopoOriginSK',
                'EMTopoOriginCS',
                'EMTopoOriginVor',
                'EMTopoOriginCSSK',
                'EMTopoOriginVorSK',
                'LCTopoOriginSK',
                'LCTopoOriginCS',
                'LCTopoOriginVor',
                'LCTopoOriginCSSK',
                'LCTopoOriginVorSK',
                'EMPFlowSK',
                'EMPFlowCS',
                'EMPFlowVor',
                'EMPFlowCSSK',
                'EMPFlowVorSK',
                'HI',
                'TruthCharged',
                'EMTopoOriginTime',
                'EMTopoOriginSKTime',
                'EMTopoOriginCSSKTime',
                'EMTopoOriginVorSKTime',
                'EMPFlowTime',
                'EMPFlowSKTime',
                'EMPFlowCSSKTime',
                'EMPFlowVorSKTime',
                'PFlowCustomVtx',
                'EMPFlowByVertex',
                'Other',
                'Uncategorized',
            ],
        },
    ],
    'typeName': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.JetInput',
            'name': 'Type',
            'values': [
                'LCTopo',
                'EMTopo',
                'TopoTower',
                'Tower',
                'Truth',
                'TruthWZ',
                'Track',
                'PFlow',
                'LCPFlow',
                'EMPFlow',
                'EMCPFlow',
                'Jet',
                'LCTopoOrigin',
                'EMTopoOrigin',
                'TrackCaloCluster',
                'UFO',
                'UFOCHS',
                'UFOCSSK',
                'TruthDressedWZ',
                'EMTopoOriginSK',
                'EMTopoOriginCS',
                'EMTopoOriginVor',
                'EMTopoOriginCSSK',
                'EMTopoOriginVorSK',
                'LCTopoOriginSK',
                'LCTopoOriginCS',
                'LCTopoOriginVor',
                'LCTopoOriginCSSK',
                'LCTopoOriginVorSK',
                'EMPFlowSK',
                'EMPFlowCS',
                'EMPFlowVor',
                'EMPFlowCSSK',
                'EMPFlowVorSK',
                'HI',
                'TruthCharged',
                'EMTopoOriginTime',
                'EMTopoOriginSKTime',
                'EMTopoOriginCSSKTime',
                'EMTopoOriginVorSKTime',
                'EMPFlowTime',
                'EMPFlowSKTime',
                'EMPFlowCSSKTime',
                'EMPFlowVorSKTime',
                'PFlowCustomVtx',
                'EMPFlowByVertex',
                'Other',
                'Uncategorized',
            ],
        },
    ],
    'inputType': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.JetInput',
            'name': 'Type',
            'values': [
                'LCTopo',
                'EMTopo',
                'TopoTower',
                'Tower',
                'Truth',
                'TruthWZ',
                'Track',
                'PFlow',
                'LCPFlow',
                'EMPFlow',
                'EMCPFlow',
                'Jet',
                'LCTopoOrigin',
                'EMTopoOrigin',
                'TrackCaloCluster',
                'UFO',
                'UFOCHS',
                'UFOCSSK',
                'TruthDressedWZ',
                'EMTopoOriginSK',
                'EMTopoOriginCS',
                'EMTopoOriginVor',
                'EMTopoOriginCSSK',
                'EMTopoOriginVorSK',
                'LCTopoOriginSK',
                'LCTopoOriginCS',
                'LCTopoOriginVor',
                'LCTopoOriginCSSK',
                'LCTopoOriginVorSK',
                'EMPFlowSK',
                'EMPFlowCS',
                'EMPFlowVor',
                'EMPFlowCSSK',
                'EMPFlowVorSK',
                'HI',
                'TruthCharged',
                'EMTopoOriginTime',
                'EMTopoOriginSKTime',
                'EMTopoOriginCSSKTime',
                'EMTopoOriginVorSKTime',
                'EMPFlowTime',
                'EMPFlowSKTime',
                'EMPFlowCSSKTime',
                'EMPFlowVorSKTime',
                'PFlowCustomVtx',
                'EMPFlowByVertex',
                'Other',
                'Uncategorized',
            ],
        },
    ],      
}

_defined_enums = {
    'Type':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.JetInput',
            'name': 'Type',
            'values': [
                'LCTopo',
                'EMTopo',
                'TopoTower',
                'Tower',
                'Truth',
                'TruthWZ',
                'Track',
                'PFlow',
                'LCPFlow',
                'EMPFlow',
                'EMCPFlow',
                'Jet',
                'LCTopoOrigin',
                'EMTopoOrigin',
                'TrackCaloCluster',
                'UFO',
                'UFOCHS',
                'UFOCSSK',
                'TruthDressedWZ',
                'EMTopoOriginSK',
                'EMTopoOriginCS',
                'EMTopoOriginVor',
                'EMTopoOriginCSSK',
                'EMTopoOriginVorSK',
                'LCTopoOriginSK',
                'LCTopoOriginCS',
                'LCTopoOriginVor',
                'LCTopoOriginCSSK',
                'LCTopoOriginVorSK',
                'EMPFlowSK',
                'EMPFlowCS',
                'EMPFlowVor',
                'EMPFlowCSSK',
                'EMPFlowVorSK',
                'HI',
                'TruthCharged',
                'EMTopoOriginTime',
                'EMTopoOriginSKTime',
                'EMTopoOriginCSSKTime',
                'EMTopoOriginVorSKTime',
                'EMPFlowTime',
                'EMPFlowSKTime',
                'EMPFlowCSSKTime',
                'EMPFlowVorSKTime',
                'PFlowCustomVtx',
                'EMPFlowByVertex',
                'Other',
                'Uncategorized',
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
class JetInput:
    "A class"

    class Type(Enum):
        LCTopo = 0
        EMTopo = 1
        TopoTower = 2
        Tower = 3
        Truth = 4
        TruthWZ = 5
        Track = 6
        PFlow = 7
        LCPFlow = 8
        EMPFlow = 9
        EMCPFlow = 10
        Jet = 11
        LCTopoOrigin = 12
        EMTopoOrigin = 13
        TrackCaloCluster = 14
        UFO = 15
        UFOCHS = 16
        UFOCSSK = 17
        TruthDressedWZ = 18
        EMTopoOriginSK = 19
        EMTopoOriginCS = 20
        EMTopoOriginVor = 21
        EMTopoOriginCSSK = 22
        EMTopoOriginVorSK = 23
        LCTopoOriginSK = 24
        LCTopoOriginCS = 25
        LCTopoOriginVor = 26
        LCTopoOriginCSSK = 27
        LCTopoOriginVorSK = 28
        EMPFlowSK = 29
        EMPFlowCS = 30
        EMPFlowVor = 31
        EMPFlowCSSK = 32
        EMPFlowVorSK = 33
        HI = 34
        TruthCharged = 35
        EMTopoOriginTime = 36
        EMTopoOriginSKTime = 37
        EMTopoOriginCSSKTime = 38
        EMTopoOriginVorSKTime = 39
        EMPFlowTime = 40
        EMPFlowSKTime = 41
        EMPFlowCSSKTime = 42
        EMPFlowVorSKTime = 43
        PFlowCustomVtx = 44
        EMPFlowByVertex = 45
        Other = 100
        Uncategorized = 1000


    def isValidConstitType(self, t: func_adl_servicex_xaodr21.xAOD.jetinput.JetInput.Type) -> bool:
        "A method"
        ...

    def typeName(self, t: func_adl_servicex_xaodr21.xAOD.jetinput.JetInput.Type) -> str:
        "A method"
        ...

    def inputType(self, n: str) -> func_adl_servicex_xaodr21.xAOD.jetinput.JetInput.Type:
        "A method"
        ...
