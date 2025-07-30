from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr21

_method_map = {
    'id': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthVertex_v1',
        'method_name': 'id',
        'return_type': 'int',
    },
    'barcode': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthVertex_v1',
        'method_name': 'barcode',
        'return_type': 'int',
    },
    'incomingParticleLinks': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthVertex_v1',
        'method_name': 'incomingParticleLinks',
        'return_type_element': 'ElementLink<DataVector<xAOD::TruthParticle_v1>>',
        'return_type_collection': 'const vector<ElementLink<DataVector<xAOD::TruthParticle_v1>>>',
    },
    'nIncomingParticles': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthVertex_v1',
        'method_name': 'nIncomingParticles',
        'return_type': 'unsigned int',
    },
    'incomingParticle': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthVertex_v1',
        'method_name': 'incomingParticle',
        'return_type': 'const xAOD::TruthParticle_v1 *',
    },
    'outgoingParticleLinks': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthVertex_v1',
        'method_name': 'outgoingParticleLinks',
        'return_type_element': 'ElementLink<DataVector<xAOD::TruthParticle_v1>>',
        'return_type_collection': 'const vector<ElementLink<DataVector<xAOD::TruthParticle_v1>>>',
    },
    'nOutgoingParticles': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthVertex_v1',
        'method_name': 'nOutgoingParticles',
        'return_type': 'unsigned int',
    },
    'outgoingParticle': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthVertex_v1',
        'method_name': 'outgoingParticle',
        'return_type': 'const xAOD::TruthParticle_v1 *',
    },
    'x': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthVertex_v1',
        'method_name': 'x',
        'return_type': 'float',
    },
    'y': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthVertex_v1',
        'method_name': 'y',
        'return_type': 'float',
    },
    'z': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthVertex_v1',
        'method_name': 'z',
        'return_type': 'float',
    },
    'perp': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthVertex_v1',
        'method_name': 'perp',
        'return_type': 'float',
    },
    'eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthVertex_v1',
        'method_name': 'eta',
        'return_type': 'float',
    },
    'phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthVertex_v1',
        'method_name': 'phi',
        'return_type': 'float',
    },
    't': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthVertex_v1',
        'method_name': 't',
        'return_type': 'float',
    },
    'v4': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthVertex_v1',
        'method_name': 'v4',
        'return_type': 'const TLorentzVector',
    },
    'type': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthVertex_v1',
        'method_name': 'type',
        'return_type': 'xAOD::Type::ObjectType',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthVertex_v1',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthVertex_v1',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthVertex_v1',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthVertex_v1',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthVertex_v1',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthVertex_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthVertex_v1',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthVertex_v1',
        'method_name': 'isAvailable',
        'return_type': 'bool',
    },
}

_enum_function_map = {
    'type': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.Type',
            'name': 'ObjectType',
            'values': [
                'Other',
                'CaloCluster',
                'Jet',
                'ParticleFlow',
                'TrackParticle',
                'NeutralParticle',
                'Electron',
                'Photon',
                'Muon',
                'Tau',
                'TrackCaloCluster',
                'Vertex',
                'BTag',
                'TruthParticle',
                'TruthVertex',
                'TruthEvent',
                'TruthPileupEvent',
                'L2StandAloneMuon',
                'L2IsoMuon',
                'L2CombinedMuon',
                'TrigElectron',
                'TrigPhoton',
                'TrigCaloCluster',
                'TrigEMCluster',
                'EventInfo',
                'EventFormat',
                'Particle',
                'CompositeParticle',
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
            'name': 'xAODTruth/versions/TruthVertex_v1.h',
            'body_includes': ["xAODTruth/versions/TruthVertex_v1.h"],
        })


        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODTruth',
            'link_libraries': ["xAODTruth"],
        })

        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class TruthVertex_v1:
    "A class"


    def id(self) -> int:
        "A method"
        ...

    def barcode(self) -> int:
        "A method"
        ...

    def incomingParticleLinks(self) -> func_adl_servicex_xaodr21.vector_elementlink_datavector_xaod_truthparticle_v1___.vector_ElementLink_DataVector_xAOD_TruthParticle_v1___:
        "A method"
        ...

    def nIncomingParticles(self) -> int:
        "A method"
        ...

    def incomingParticle(self, index: int) -> func_adl_servicex_xaodr21.xAOD.truthparticle_v1.TruthParticle_v1:
        "A method"
        ...

    def outgoingParticleLinks(self) -> func_adl_servicex_xaodr21.vector_elementlink_datavector_xaod_truthparticle_v1___.vector_ElementLink_DataVector_xAOD_TruthParticle_v1___:
        "A method"
        ...

    def nOutgoingParticles(self) -> int:
        "A method"
        ...

    def outgoingParticle(self, index: int) -> func_adl_servicex_xaodr21.xAOD.truthparticle_v1.TruthParticle_v1:
        "A method"
        ...

    def x(self) -> float:
        "A method"
        ...

    def y(self) -> float:
        "A method"
        ...

    def z(self) -> float:
        "A method"
        ...

    def perp(self) -> float:
        "A method"
        ...

    def eta(self) -> float:
        "A method"
        ...

    def phi(self) -> float:
        "A method"
        ...

    def t(self) -> float:
        "A method"
        ...

    def v4(self) -> func_adl_servicex_xaodr21.tlorentzvector.TLorentzVector:
        "A method"
        ...

    def type(self) -> func_adl_servicex_xaodr21.xAOD.type.Type.ObjectType:
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
