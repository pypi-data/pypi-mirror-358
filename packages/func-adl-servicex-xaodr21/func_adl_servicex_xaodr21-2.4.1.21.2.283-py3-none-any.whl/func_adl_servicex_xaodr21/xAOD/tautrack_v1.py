from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr21

_method_map = {
    'pt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauTrack_v1',
        'method_name': 'pt',
        'return_type': 'double',
    },
    'eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauTrack_v1',
        'method_name': 'eta',
        'return_type': 'double',
    },
    'phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauTrack_v1',
        'method_name': 'phi',
        'return_type': 'double',
    },
    'e': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauTrack_v1',
        'method_name': 'e',
        'return_type': 'double',
    },
    'm': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauTrack_v1',
        'method_name': 'm',
        'return_type': 'double',
    },
    'rapidity': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauTrack_v1',
        'method_name': 'rapidity',
        'return_type': 'double',
    },
    'p4': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauTrack_v1',
        'method_name': 'p4',
        'return_type': 'const TLorentzVector',
    },
    'type': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauTrack_v1',
        'method_name': 'type',
        'return_type': 'xAOD::Type::ObjectType',
    },
    'flag': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauTrack_v1',
        'method_name': 'flag',
        'return_type': 'bool',
    },
    'flagWithMask': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauTrack_v1',
        'method_name': 'flagWithMask',
        'return_type': 'bool',
    },
    'z0sinThetaTJVA': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauTrack_v1',
        'method_name': 'z0sinThetaTJVA',
        'return_type': 'float',
    },
    'rConv': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauTrack_v1',
        'method_name': 'rConv',
        'return_type': 'float',
    },
    'rConvII': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauTrack_v1',
        'method_name': 'rConvII',
        'return_type': 'float',
    },
    'dRJetSeedAxis': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauTrack_v1',
        'method_name': 'dRJetSeedAxis',
        'return_type': 'float',
    },
    'bdtScores': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauTrack_v1',
        'method_name': 'bdtScores',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'bdtScore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauTrack_v1',
        'method_name': 'bdtScore',
        'return_type': 'float',
    },
    'nBdtScores': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauTrack_v1',
        'method_name': 'nBdtScores',
        'return_type': 'unsigned int',
    },
    'detail': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauTrack_v1',
        'method_name': 'detail',
        'return_type': 'bool',
    },
    'trackLinks': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauTrack_v1',
        'method_name': 'trackLinks',
        'return_type_element': 'ElementLink<DataVector<xAOD::TrackParticle_v1>>',
        'return_type_collection': 'const vector<ElementLink<DataVector<xAOD::TrackParticle_v1>>>',
    },
    'track': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauTrack_v1',
        'method_name': 'track',
        'return_type': 'const xAOD::TrackParticle_v1 *',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauTrack_v1',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauTrack_v1',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauTrack_v1',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauTrack_v1',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauTrack_v1',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauTrack_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauTrack_v1',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauTrack_v1',
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
    'flag': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.TauJetParameters',
            'name': 'TauTrackFlag',
            'values': [
                'isConversionOld',
                'failTrackFilter',
                'coreTrack',
                'wideTrack',
                'passTrkSelector',
                'classifiedCharged',
                'classifiedIsolation',
                'classifiedConversion',
                'classifiedFake',
                'unclassified',
                'passTrkSelectionTight',
                'modifiedIsolationTrack',
            ],
        },
    ],
    'detail': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.TauJetParameters',
            'name': 'TrackDetail',
            'values': [
                'CaloSamplingEtaEM',
                'CaloSamplingEtaHad',
                'CaloSamplingPhiEM',
                'CaloSamplingPhiHad',
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
            'name': 'xAODTau/versions/TauTrack_v1.h',
            'body_includes': ["xAODTau/versions/TauTrack_v1.h"],
        })


        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODTau',
            'link_libraries': ["xAODTau"],
        })

        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class TauTrack_v1:
    "A class"


    def pt(self) -> float:
        "A method"
        ...

    def eta(self) -> float:
        "A method"
        ...

    def phi(self) -> float:
        "A method"
        ...

    def e(self) -> float:
        "A method"
        ...

    def m(self) -> float:
        "A method"
        ...

    def rapidity(self) -> float:
        "A method"
        ...

    def p4(self) -> func_adl_servicex_xaodr21.tlorentzvector.TLorentzVector:
        "A method"
        ...

    def type(self) -> func_adl_servicex_xaodr21.xAOD.type.Type.ObjectType:
        "A method"
        ...

    def flag(self, flag: func_adl_servicex_xaodr21.xAOD.taujetparameters.TauJetParameters.TauTrackFlag) -> bool:
        "A method"
        ...

    def flagWithMask(self, noname_arg: int) -> bool:
        "A method"
        ...

    def z0sinThetaTJVA(self, noname_arg: func_adl_servicex_xaodr21.xAOD.iparticle.IParticle) -> float:
        "A method"
        ...

    def rConv(self, noname_arg: func_adl_servicex_xaodr21.xAOD.iparticle.IParticle) -> float:
        "A method"
        ...

    def rConvII(self, noname_arg: func_adl_servicex_xaodr21.xAOD.iparticle.IParticle) -> float:
        "A method"
        ...

    def dRJetSeedAxis(self, noname_arg: func_adl_servicex_xaodr21.xAOD.iparticle.IParticle) -> float:
        "A method"
        ...

    def bdtScores(self) -> func_adl_servicex_xaodr21.vector_float_.vector_float_:
        "A method"
        ...

    def bdtScore(self, i: int) -> float:
        "A method"
        ...

    def nBdtScores(self) -> int:
        "A method"
        ...

    def detail(self, detail: func_adl_servicex_xaodr21.xAOD.taujetparameters.TauJetParameters.TrackDetail, value: float) -> bool:
        "A method"
        ...

    def trackLinks(self) -> func_adl_servicex_xaodr21.vector_elementlink_datavector_xaod_trackparticle_v1___.vector_ElementLink_DataVector_xAOD_TrackParticle_v1___:
        "A method"
        ...

    def track(self) -> func_adl_servicex_xaodr21.xAOD.trackparticle_v1.TrackParticle_v1:
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
