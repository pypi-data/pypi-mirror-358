from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr21

_method_map = {
    'pt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'pt',
        'return_type': 'double',
    },
    'eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'eta',
        'return_type': 'double',
    },
    'phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'phi',
        'return_type': 'double',
    },
    'm': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'm',
        'return_type': 'double',
    },
    'e': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'e',
        'return_type': 'double',
    },
    'rapidity': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'rapidity',
        'return_type': 'double',
    },
    'type': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'type',
        'return_type': 'xAOD::Type::ObjectType',
    },
    'rawConstituent': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'rawConstituent',
        'return_type': 'const xAOD::IParticle *',
    },
    'Px': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'Px',
        'return_type': 'double',
    },
    'X': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'X',
        'return_type': 'double',
    },
    'Py': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'Py',
        'return_type': 'double',
    },
    'Y': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'Y',
        'return_type': 'double',
    },
    'Pz': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'Pz',
        'return_type': 'double',
    },
    'Z': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'Z',
        'return_type': 'double',
    },
    'E': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'E',
        'return_type': 'double',
    },
    'T': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'T',
        'return_type': 'double',
    },
    'M2': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'M2',
        'return_type': 'double',
    },
    'M': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'M',
        'return_type': 'double',
    },
    'R': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'R',
        'return_type': 'double',
    },
    'P': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'P',
        'return_type': 'double',
    },
    'P2': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'P2',
        'return_type': 'double',
    },
    'Perp2': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'Perp2',
        'return_type': 'double',
    },
    'Pt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'Pt',
        'return_type': 'double',
    },
    'Rho': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'Rho',
        'return_type': 'double',
    },
    'Mt2': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'Mt2',
        'return_type': 'double',
    },
    'Mt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'Mt',
        'return_type': 'double',
    },
    'Et2': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'Et2',
        'return_type': 'double',
    },
    'Et': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'Et',
        'return_type': 'double',
    },
    'Phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'Phi',
        'return_type': 'double',
    },
    'Theta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'Theta',
        'return_type': 'double',
    },
    'Eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'Eta',
        'return_type': 'double',
    },
    'Rapidity': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'Rapidity',
        'return_type': 'double',
    },
    'ColinearRapidity': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'ColinearRapidity',
        'return_type': 'double',
    },
    'isTimelike': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'isTimelike',
        'return_type': 'bool',
    },
    'isLightlike': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'isLightlike',
        'return_type': 'bool',
    },
    'isSpacelike': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'isSpacelike',
        'return_type': 'bool',
    },
    'Beta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'Beta',
        'return_type': 'double',
    },
    'Gamma': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'Gamma',
        'return_type': 'double',
    },
    'x': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'x',
        'return_type': 'double',
    },
    'y': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'y',
        'return_type': 'double',
    },
    'z': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'z',
        'return_type': 'double',
    },
    't': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 't',
        'return_type': 'double',
    },
    'px': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'px',
        'return_type': 'double',
    },
    'py': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'py',
        'return_type': 'double',
    },
    'pz': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'pz',
        'return_type': 'double',
    },
    'r': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'r',
        'return_type': 'double',
    },
    'theta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'theta',
        'return_type': 'double',
    },
    'rho': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'rho',
        'return_type': 'double',
    },
    'perp2': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'perp2',
        'return_type': 'double',
    },
    'mag2': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'mag2',
        'return_type': 'double',
    },
    'mag': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'mag',
        'return_type': 'double',
    },
    'mt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'mt',
        'return_type': 'double',
    },
    'mt2': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'mt2',
        'return_type': 'double',
    },
    'energy': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'energy',
        'return_type': 'double',
    },
    'mass': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'mass',
        'return_type': 'double',
    },
    'mass2': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetConstituent',
        'method_name': 'mass2',
        'return_type': 'double',
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


        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class JetConstituent:
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

    def m(self) -> float:
        "A method"
        ...

    def e(self) -> float:
        "A method"
        ...

    def rapidity(self) -> float:
        "A method"
        ...

    def type(self) -> func_adl_servicex_xaodr21.xAOD.type.Type.ObjectType:
        "A method"
        ...

    def rawConstituent(self) -> func_adl_servicex_xaodr21.xAOD.iparticle.IParticle:
        "A method"
        ...

    def Px(self) -> float:
        "A method"
        ...

    def X(self) -> float:
        "A method"
        ...

    def Py(self) -> float:
        "A method"
        ...

    def Y(self) -> float:
        "A method"
        ...

    def Pz(self) -> float:
        "A method"
        ...

    def Z(self) -> float:
        "A method"
        ...

    def E(self) -> float:
        "A method"
        ...

    def T(self) -> float:
        "A method"
        ...

    def M2(self) -> float:
        "A method"
        ...

    def M(self) -> float:
        "A method"
        ...

    def R(self) -> float:
        "A method"
        ...

    def P(self) -> float:
        "A method"
        ...

    def P2(self) -> float:
        "A method"
        ...

    def Perp2(self) -> float:
        "A method"
        ...

    def Pt(self) -> float:
        "A method"
        ...

    def Rho(self) -> float:
        "A method"
        ...

    def Mt2(self) -> float:
        "A method"
        ...

    def Mt(self) -> float:
        "A method"
        ...

    def Et2(self) -> float:
        "A method"
        ...

    def Et(self) -> float:
        "A method"
        ...

    def Phi(self) -> float:
        "A method"
        ...

    def Theta(self) -> float:
        "A method"
        ...

    def Eta(self) -> float:
        "A method"
        ...

    def Rapidity(self) -> float:
        "A method"
        ...

    def ColinearRapidity(self) -> float:
        "A method"
        ...

    def isTimelike(self) -> bool:
        "A method"
        ...

    def isLightlike(self, tolerance: float) -> bool:
        "A method"
        ...

    def isSpacelike(self) -> bool:
        "A method"
        ...

    def Beta(self) -> float:
        "A method"
        ...

    def Gamma(self) -> float:
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

    def t(self) -> float:
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

    def r(self) -> float:
        "A method"
        ...

    def theta(self) -> float:
        "A method"
        ...

    def rho(self) -> float:
        "A method"
        ...

    def perp2(self) -> float:
        "A method"
        ...

    def mag2(self) -> float:
        "A method"
        ...

    def mag(self) -> float:
        "A method"
        ...

    def mt(self) -> float:
        "A method"
        ...

    def mt2(self) -> float:
        "A method"
        ...

    def energy(self) -> float:
        "A method"
        ...

    def mass(self) -> float:
        "A method"
        ...

    def mass2(self) -> float:
        "A method"
        ...
