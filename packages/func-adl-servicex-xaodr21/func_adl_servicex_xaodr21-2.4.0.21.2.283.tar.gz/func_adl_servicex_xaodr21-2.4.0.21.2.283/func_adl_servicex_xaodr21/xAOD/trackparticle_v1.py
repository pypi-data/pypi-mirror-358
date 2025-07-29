from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr21

_method_map = {
    'pt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'pt',
        'return_type': 'double',
    },
    'eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'eta',
        'return_type': 'double',
    },
    'phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'phi',
        'return_type': 'double',
    },
    'm': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'm',
        'return_type': 'double',
    },
    'e': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'e',
        'return_type': 'double',
    },
    'rapidity': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'rapidity',
        'return_type': 'double',
    },
    'p4': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'p4',
        'return_type': 'const TLorentzVector',
    },
    'type': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'type',
        'return_type': 'xAOD::Type::ObjectType',
    },
    'charge': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'charge',
        'return_type': 'float',
    },
    'd0': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'd0',
        'return_type': 'float',
    },
    'z0': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'z0',
        'return_type': 'float',
    },
    'phi0': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'phi0',
        'return_type': 'float',
    },
    'theta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'theta',
        'return_type': 'float',
    },
    'qOverP': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'qOverP',
        'return_type': 'float',
    },
    'definingParametersCovMatrixVec': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'definingParametersCovMatrixVec',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'vx': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'vx',
        'return_type': 'float',
    },
    'vy': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'vy',
        'return_type': 'float',
    },
    'vz': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'vz',
        'return_type': 'float',
    },
    'numberOfParameters': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'numberOfParameters',
        'return_type': 'unsigned int',
    },
    'parameterX': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'parameterX',
        'return_type': 'float',
    },
    'parameterY': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'parameterY',
        'return_type': 'float',
    },
    'parameterZ': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'parameterZ',
        'return_type': 'float',
    },
    'parameterPX': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'parameterPX',
        'return_type': 'float',
    },
    'parameterPY': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'parameterPY',
        'return_type': 'float',
    },
    'parameterPZ': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'parameterPZ',
        'return_type': 'float',
    },
    'parameterPosition': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'parameterPosition',
        'return_type': 'xAOD::ParameterPosition',
    },
    'indexOfParameterAtPosition': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'indexOfParameterAtPosition',
        'return_type': 'bool',
    },
    'radiusOfFirstHit': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'radiusOfFirstHit',
        'return_type': 'float',
    },
    'identifierOfFirstHit': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'identifierOfFirstHit',
        'return_type': 'uint64_t',
    },
    'beamlineTiltX': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'beamlineTiltX',
        'return_type': 'float',
    },
    'beamlineTiltY': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'beamlineTiltY',
        'return_type': 'float',
    },
    'hitPattern': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'hitPattern',
        'return_type': 'unsigned int',
    },
    'numberOfUsedHitsdEdx': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'numberOfUsedHitsdEdx',
        'return_type': 'uint8_t',
    },
    'numberOfIBLOverflowsdEdx': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'numberOfIBLOverflowsdEdx',
        'return_type': 'uint8_t',
    },
    'chiSquared': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'chiSquared',
        'return_type': 'float',
    },
    'numberDoF': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'numberDoF',
        'return_type': 'float',
    },
    'trackProperties': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'trackProperties',
        'return_type': 'xAOD::TrackProperties',
    },
    'particleHypothesis': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'particleHypothesis',
        'return_type': 'xAOD::ParticleHypothesis',
    },
    'trackFitter': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'trackFitter',
        'return_type': 'xAOD::TrackFitter',
    },
    'summaryValue': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'summaryValue',
        'return_type': 'bool',
    },
    'vertexLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'vertexLink',
        'return_type': 'const ElementLink<DataVector<xAOD::Vertex_v1>>',
    },
    'vertex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'vertex',
        'return_type': 'const xAOD::Vertex_v1 *',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackParticle_v1',
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
    'parameterPosition': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD',
            'name': 'ParameterPosition',
            'values': [
                'BeamLine',
                'FirstMeasurement',
                'LastMeasurement',
                'CalorimeterEntrance',
                'CalorimeterExit',
                'MuonSpectrometerEntrance',
            ],
        },
    ],
    'indexOfParameterAtPosition': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD',
            'name': 'ParameterPosition',
            'values': [
                'BeamLine',
                'FirstMeasurement',
                'LastMeasurement',
                'CalorimeterEntrance',
                'CalorimeterExit',
                'MuonSpectrometerEntrance',
            ],
        },
    ],
    'trackProperties': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD',
            'name': 'TrackProperties',
            'values': [
                'BremFit',
                'BremFitSuccessful',
                'StraightTrack',
                'SlimmedTrack',
                'HardScatterOrKink',
                'LowPtTrack',
                'NumberOfTrackProperties',
            ],
        },
    ],
    'particleHypothesis': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD',
            'name': 'ParticleHypothesis',
            'values': [
                'nonInteracting',
                'geantino',
                'electron',
                'muon',
                'pion',
                'kaon',
                'proton',
                'photon',
                'neutron',
                'pi0',
                'k0',
                'nonInteractingMuon',
                'noHypothesis',
                'undefined',
            ],
        },
    ],
    'trackFitter': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD',
            'name': 'TrackFitter',
            'values': [
                'Unknown',
                'iPatTrackFitter',
                'xKalman',
                'KalmanFitter',
                'GaussianSumFilter',
                'GlobalChi2Fitter',
                'DistributedKalmanFilter',
                'DeterministicAnnealingFilter',
                'KalmanDNAFitter',
                'MuonboyFitter',
                'NumberOfTrackFitters',
            ],
        },
    ],
    'summaryValue': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD',
            'name': 'SummaryType',
            'values': [
                'numberOfContribPixelLayers',
                'numberOfBLayerHits',
                'numberOfBLayerOutliers',
                'numberOfBLayerSharedHits',
                'numberOfBLayerSplitHits',
                'expectBLayerHit',
                'expectInnermostPixelLayerHit',
                'numberOfInnermostPixelLayerHits',
                'numberOfInnermostPixelLayerOutliers',
                'numberOfInnermostPixelLayerSharedHits',
                'numberOfInnermostPixelLayerSplitHits',
                'expectNextToInnermostPixelLayerHit',
                'numberOfNextToInnermostPixelLayerHits',
                'numberOfNextToInnermostPixelLayerOutliers',
                'numberOfNextToInnermostPixelLayerSharedHits',
                'numberOfNextToInnermostPixelLayerSplitHits',
                'numberOfDBMHits',
                'numberOfPixelHits',
                'numberOfPixelOutliers',
                'numberOfPixelHoles',
                'numberOfPixelSharedHits',
                'numberOfPixelSplitHits',
                'numberOfGangedPixels',
                'numberOfGangedFlaggedFakes',
                'numberOfPixelDeadSensors',
                'numberOfPixelSpoiltHits',
                'numberOfSCTHits',
                'numberOfSCTOutliers',
                'numberOfSCTHoles',
                'numberOfSCTDoubleHoles',
                'numberOfSCTSharedHits',
                'numberOfSCTDeadSensors',
                'numberOfSCTSpoiltHits',
                'numberOfTRTHits',
                'numberOfTRTOutliers',
                'numberOfTRTHoles',
                'numberOfTRTHighThresholdHits',
                'numberOfTRTHighThresholdHitsTotal',
                'numberOfTRTHighThresholdOutliers',
                'numberOfTRTDeadStraws',
                'numberOfTRTTubeHits',
                'numberOfTRTXenonHits',
                'numberOfTRTSharedHits',
                'numberOfPrecisionLayers',
                'numberOfPrecisionHoleLayers',
                'numberOfPhiLayers',
                'numberOfPhiHoleLayers',
                'numberOfTriggerEtaLayers',
                'numberOfTriggerEtaHoleLayers',
                'numberOfGoodPrecisionLayers',
                'numberOfOutliersOnTrack',
                'standardDeviationOfChi2OS',
                'eProbabilityComb',
                'eProbabilityHT',
                'pixeldEdx',
                'numberOfTrackSummaryTypes',
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
            'name': 'xAODTracking/versions/TrackParticle_v1.h',
            'body_includes': ["xAODTracking/versions/TrackParticle_v1.h"],
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
class TrackParticle_v1:
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

    def p4(self) -> func_adl_servicex_xaodr21.tlorentzvector.TLorentzVector:
        "A method"
        ...

    def type(self) -> func_adl_servicex_xaodr21.xAOD.type.Type.ObjectType:
        "A method"
        ...

    def charge(self) -> float:
        "A method"
        ...

    def d0(self) -> float:
        "A method"
        ...

    def z0(self) -> float:
        "A method"
        ...

    def phi0(self) -> float:
        "A method"
        ...

    def theta(self) -> float:
        "A method"
        ...

    def qOverP(self) -> float:
        "A method"
        ...

    def definingParametersCovMatrixVec(self) -> func_adl_servicex_xaodr21.vector_float_.vector_float_:
        "A method"
        ...

    def vx(self) -> float:
        "A method"
        ...

    def vy(self) -> float:
        "A method"
        ...

    def vz(self) -> float:
        "A method"
        ...

    def numberOfParameters(self) -> int:
        "A method"
        ...

    def parameterX(self, index: int) -> float:
        "A method"
        ...

    def parameterY(self, index: int) -> float:
        "A method"
        ...

    def parameterZ(self, index: int) -> float:
        "A method"
        ...

    def parameterPX(self, index: int) -> float:
        "A method"
        ...

    def parameterPY(self, index: int) -> float:
        "A method"
        ...

    def parameterPZ(self, index: int) -> float:
        "A method"
        ...

    def parameterPosition(self, index: int) -> func_adl_servicex_xaodr21.xaod.xAOD.ParameterPosition:
        "A method"
        ...

    def indexOfParameterAtPosition(self, index: int, position: func_adl_servicex_xaodr21.xaod.xAOD.ParameterPosition) -> bool:
        "A method"
        ...

    def radiusOfFirstHit(self) -> float:
        "A method"
        ...

    def identifierOfFirstHit(self) -> int:
        "A method"
        ...

    def beamlineTiltX(self) -> float:
        "A method"
        ...

    def beamlineTiltY(self) -> float:
        "A method"
        ...

    def hitPattern(self) -> int:
        "A method"
        ...

    def numberOfUsedHitsdEdx(self) -> int:
        "A method"
        ...

    def numberOfIBLOverflowsdEdx(self) -> int:
        "A method"
        ...

    def chiSquared(self) -> float:
        "A method"
        ...

    def numberDoF(self) -> float:
        "A method"
        ...

    def trackProperties(self) -> func_adl_servicex_xaodr21.xaod.xAOD.TrackProperties:
        "A method"
        ...

    def particleHypothesis(self) -> func_adl_servicex_xaodr21.xaod.xAOD.ParticleHypothesis:
        "A method"
        ...

    def trackFitter(self) -> func_adl_servicex_xaodr21.xaod.xAOD.TrackFitter:
        "A method"
        ...

    def summaryValue(self, value: int, information: func_adl_servicex_xaodr21.xaod.xAOD.SummaryType) -> bool:
        "A method"
        ...

    def vertexLink(self) -> func_adl_servicex_xaodr21.elementlink_datavector_xaod_vertex_v1__.ElementLink_DataVector_xAOD_Vertex_v1__:
        "A method"
        ...

    def vertex(self) -> func_adl_servicex_xaodr21.xAOD.vertex_v1.Vertex_v1:
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
