from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr21

_method_map = {
    'type': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackStateValidation_v1',
        'method_name': 'type',
        'return_type': 'int',
    },
    'detElementId': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackStateValidation_v1',
        'method_name': 'detElementId',
        'return_type': 'uint64_t',
    },
    'detType': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackStateValidation_v1',
        'method_name': 'detType',
        'return_type': 'char',
    },
    'localX': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackStateValidation_v1',
        'method_name': 'localX',
        'return_type': 'float',
    },
    'localY': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackStateValidation_v1',
        'method_name': 'localY',
        'return_type': 'float',
    },
    'localTheta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackStateValidation_v1',
        'method_name': 'localTheta',
        'return_type': 'float',
    },
    'localPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackStateValidation_v1',
        'method_name': 'localPhi',
        'return_type': 'float',
    },
    'unbiasedResidualX': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackStateValidation_v1',
        'method_name': 'unbiasedResidualX',
        'return_type': 'float',
    },
    'unbiasedResidualY': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackStateValidation_v1',
        'method_name': 'unbiasedResidualY',
        'return_type': 'float',
    },
    'unbiasedPullX': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackStateValidation_v1',
        'method_name': 'unbiasedPullX',
        'return_type': 'float',
    },
    'unbiasedPullY': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackStateValidation_v1',
        'method_name': 'unbiasedPullY',
        'return_type': 'float',
    },
    'biasedResidualX': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackStateValidation_v1',
        'method_name': 'biasedResidualX',
        'return_type': 'float',
    },
    'biasedResidualY': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackStateValidation_v1',
        'method_name': 'biasedResidualY',
        'return_type': 'float',
    },
    'biasedPullX': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackStateValidation_v1',
        'method_name': 'biasedPullX',
        'return_type': 'float',
    },
    'biasedPullY': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackStateValidation_v1',
        'method_name': 'biasedPullY',
        'return_type': 'float',
    },
    'trackMeasurementValidationLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackStateValidation_v1',
        'method_name': 'trackMeasurementValidationLink',
        'return_type': 'ElementLink<DataVector<xAOD::TrackMeasurementValidation_v1>>',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackStateValidation_v1',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackStateValidation_v1',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackStateValidation_v1',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackStateValidation_v1',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackStateValidation_v1',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackStateValidation_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackStateValidation_v1',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackStateValidation_v1',
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
            'name': 'xAODTracking/versions/TrackStateValidation_v1.h',
            'body_includes': ["xAODTracking/versions/TrackStateValidation_v1.h"],
        })


        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODTracking',
            'link_libraries': ["xAODTracking"],
        })

        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class TrackStateValidation_v1:
    "A class"


    def type(self) -> int:
        "A method"
        ...

    def detElementId(self) -> int:
        "A method"
        ...

    def detType(self) -> str:
        "A method"
        ...

    def localX(self) -> float:
        "A method"
        ...

    def localY(self) -> float:
        "A method"
        ...

    def localTheta(self) -> float:
        "A method"
        ...

    def localPhi(self) -> float:
        "A method"
        ...

    def unbiasedResidualX(self) -> float:
        "A method"
        ...

    def unbiasedResidualY(self) -> float:
        "A method"
        ...

    def unbiasedPullX(self) -> float:
        "A method"
        ...

    def unbiasedPullY(self) -> float:
        "A method"
        ...

    def biasedResidualX(self) -> float:
        "A method"
        ...

    def biasedResidualY(self) -> float:
        "A method"
        ...

    def biasedPullX(self) -> float:
        "A method"
        ...

    def biasedPullY(self) -> float:
        "A method"
        ...

    def trackMeasurementValidationLink(self) -> func_adl_servicex_xaodr21.elementlink_datavector_xaod_trackmeasurementvalidation_v1__.ElementLink_DataVector_xAOD_TrackMeasurementValidation_v1__:
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
