from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr21

_method_map = {
    'setOriginalObjectLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD',
        'method_name': 'setOriginalObjectLink',
        'return_type': 'bool',
    },
    'getOriginalObject': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD',
        'method_name': 'getOriginalObject',
        'return_type': 'const xAOD::IParticle *',
    },
}

_enum_function_map = {      
}

_defined_enums = {
    'TrackFitter':
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
    'TrackProperties':
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
    'TrackPatternRecoInfo':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD',
            'name': 'TrackPatternRecoInfo',
            'values': [
                'SiSPSeededFinder',
                'SiCTBTracking',
                'InDetAmbiguitySolver',
                'InDetExtensionProcessor',
                'TRTSeededTrackFinder',
                'Muonboy',
                'MuGirlUnrefitted',
                'STACO',
                'StacoLowPt',
                'MuTag',
                'MooreToTrackTool',
                'TrigIDSCAN',
                'TrigSiTrack',
                'TrigTRTxK',
                'TrigTRTLUT',
                'Fatras',
                'iPatLegacyCnv',
                'xKalmanLegacyCnv',
                'SimpleAmbiguityProcessorTool',
                'InDetAmbiTrackSelectionTool',
                'TRTStandalone',
                'MuidStandAlone',
                'TRTSeededSingleSpTrackFinder',
                'MooreLegacyCnv',
                'MuidComb',
                'Moore',
                'MuidCombined',
                'MuidVertexAssociator',
                'MuGirl',
                'iPatRec',
                'MuGirlLowBeta',
                'FatrasSimulation',
                'ReverseOrderedTrack',
                'MuonNotHittingTileVolume',
                'SiSpacePointsSeedMaker_Cosmic',
                'SiSpacePointsSeedMaker_HeavyIon',
                'SiSpacePointsSeedMaker_LowMomentum',
                'SiSpacePointsSeedMaker_BeamGas',
                'SiSpacePointsSeedMaker_VeryLowMomentum',
                'MuidMuonRecoveryTool',
                'MuidStandaloneRefit',
                'TrackInCaloROI',
                'SiSpacePointsSeedMaker_ForwardTracks',
                'strategyA',
                'strategyB',
                'strategyC',
                'FTK',
                'FastTrackFinderSeed',
                'SiSPSeededFinderSimple',
                'SiSpacePointsSeedMaker_LargeD0',
                'SiSpacePointsSeedMaker_SLHCConversionTracks',
                'Pseudotracking',
                'NumberOfTrackRecoInfo',
            ],
        },
    'ParticleHypothesis':
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
    'ParameterPosition':
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
    'SummaryType':
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
    'MuonSummaryType':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD',
            'name': 'MuonSummaryType',
            'values': [
                'primarySector',
                'secondarySector',
                'innerSmallHits',
                'innerLargeHits',
                'middleSmallHits',
                'middleLargeHits',
                'outerSmallHits',
                'outerLargeHits',
                'extendedSmallHits',
                'extendedLargeHits',
                'innerSmallHoles',
                'innerLargeHoles',
                'middleSmallHoles',
                'middleLargeHoles',
                'outerSmallHoles',
                'outerLargeHoles',
                'extendedSmallHoles',
                'extendedLargeHoles',
                'phiLayer1Hits',
                'phiLayer2Hits',
                'phiLayer3Hits',
                'phiLayer4Hits',
                'etaLayer1Hits',
                'etaLayer2Hits',
                'etaLayer3Hits',
                'etaLayer4Hits',
                'phiLayer1Holes',
                'phiLayer2Holes',
                'phiLayer3Holes',
                'phiLayer4Holes',
                'etaLayer1Holes',
                'etaLayer2Holes',
                'etaLayer3Holes',
                'etaLayer4Holes',
                'innerClosePrecisionHits',
                'middleClosePrecisionHits',
                'outerClosePrecisionHits',
                'extendedClosePrecisionHits',
                'innerOutBoundsPrecisionHits',
                'middleOutBoundsPrecisionHits',
                'outerOutBoundsPrecisionHits',
                'extendedOutBoundsPrecisionHits',
                'combinedTrackOutBoundsPrecisionHits',
                'isEndcapGoodLayers',
                'isSmallGoodSectors',
                'phiLayer1RPCHits',
                'phiLayer2RPCHits',
                'phiLayer3RPCHits',
                'phiLayer4RPCHits',
                'etaLayer1RPCHits',
                'etaLayer2RPCHits',
                'etaLayer3RPCHits',
                'etaLayer4RPCHits',
                'phiLayer1RPCHoles',
                'phiLayer2RPCHoles',
                'phiLayer3RPCHoles',
                'phiLayer4RPCHoles',
                'etaLayer1RPCHoles',
                'etaLayer2RPCHoles',
                'etaLayer3RPCHoles',
                'etaLayer4RPCHoles',
                'phiLayer1TGCHits',
                'phiLayer2TGCHits',
                'phiLayer3TGCHits',
                'phiLayer4TGCHits',
                'etaLayer1TGCHits',
                'etaLayer2TGCHits',
                'etaLayer3TGCHits',
                'etaLayer4TGCHits',
                'phiLayer1TGCHoles',
                'phiLayer2TGCHoles',
                'phiLayer3TGCHoles',
                'phiLayer4TGCHoles',
                'etaLayer1TGCHoles',
                'etaLayer2TGCHoles',
                'etaLayer3TGCHoles',
                'etaLayer4TGCHoles',
                'phiLayer1STGCHits',
                'phiLayer2STGCHits',
                'etaLayer1STGCHits',
                'etaLayer2STGCHits',
                'phiLayer1STGCHoles',
                'phiLayer2STGCHoles',
                'etaLayer1STGCHoles',
                'etaLayer2STGCHoles',
                'mmHits',
                'mmHoles',
                'cscEtaHits',
                'cscUnspoiledEtaHits',
                'numberOfMuonSummaryTypes',
            ],
        },
    'BTagInfo':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD',
            'name': 'BTagInfo',
            'values': [
                'SV0_NGTinJet',
                'SV0_NGTinSvx',
                'SV0_N2Tpair',
                'SV0_masssvx',
                'SV0_efracsvx',
                'SV0_normdist',
                'SV1_NGTinJet',
                'SV1_NGTinSvx',
                'SV1_N2Tpair',
                'SV1_masssvx',
                'SV1_efracsvx',
                'SV1_normdist',
                'JetFitter_nVTX',
                'JetFitter_nSingleTracks',
                'JetFitter_nTracksAtVtx',
                'JetFitter_mass',
                'JetFitter_energyFraction',
                'JetFitter_significance3d',
                'JetFitter_deltaeta',
                'JetFitter_deltaphi',
                'JetFitter_N2Tpair',
                'IP2D_ntrk',
                'IP2D_gradeOfTracks',
                'IP2D_flagFromV0ofTracks',
                'IP2D_valD0wrtPVofTracks',
                'IP2D_sigD0wrtPVofTracks',
                'IP2D_weightBofTracks',
                'IP2D_weightUofTracks',
                'IP2D_weightCofTracks',
                'IP3D_ntrk',
                'IP3D_gradeOfTracks',
                'IP3D_flagFromV0ofTracks',
                'IP3D_valD0wrtPVofTracks',
                'IP3D_sigD0wrtPVofTracks',
                'IP3D_valZ0wrtPVofTracks',
                'IP3D_sigZ0wrtPVofTracks',
                'IP3D_weightBofTracks',
                'IP3D_weightUofTracks',
                'IP3D_weightCofTracks',
            ],
        },
    'JetConstitScale':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD',
            'name': 'JetConstitScale',
            'values': [
                'UncalibratedJetConstituent',
                'CalibratedJetConstituent',
            ],
        },
    'JetScale':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD',
            'name': 'JetScale',
            'values': [
                'JetEMScaleMomentum',
                'JetConstitScaleMomentum',
                'JetAssignedScaleMomentum',
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
class xAOD:
    "A class"

    class TrackFitter(Enum):
        Unknown = 0
        iPatTrackFitter = 1
        xKalman = 2
        KalmanFitter = 3
        GaussianSumFilter = 4
        GlobalChi2Fitter = 5
        DistributedKalmanFilter = 6
        DeterministicAnnealingFilter = 7
        KalmanDNAFitter = 8
        MuonboyFitter = 9
        NumberOfTrackFitters = 10

    class TrackProperties(Enum):
        BremFit = 1
        BremFitSuccessful = 2
        StraightTrack = 3
        SlimmedTrack = 4
        HardScatterOrKink = 5
        LowPtTrack = 6
        NumberOfTrackProperties = 7

    class TrackPatternRecoInfo(Enum):
        SiSPSeededFinder = 0
        SiCTBTracking = 1
        InDetAmbiguitySolver = 2
        InDetExtensionProcessor = 3
        TRTSeededTrackFinder = 4
        Muonboy = 5
        MuGirlUnrefitted = 6
        STACO = 7
        StacoLowPt = 8
        MuTag = 9
        MooreToTrackTool = 10
        TrigIDSCAN = 11
        TrigSiTrack = 12
        TrigTRTxK = 13
        TrigTRTLUT = 14
        Fatras = 15
        iPatLegacyCnv = 16
        xKalmanLegacyCnv = 17
        SimpleAmbiguityProcessorTool = 18
        InDetAmbiTrackSelectionTool = 19
        TRTStandalone = 20
        MuidStandAlone = 21
        TRTSeededSingleSpTrackFinder = 22
        MooreLegacyCnv = 23
        MuidComb = 24
        Moore = 25
        MuidCombined = 26
        MuidVertexAssociator = 27
        MuGirl = 28
        iPatRec = 29
        MuGirlLowBeta = 30
        FatrasSimulation = 31
        ReverseOrderedTrack = 32
        MuonNotHittingTileVolume = 33
        SiSpacePointsSeedMaker_Cosmic = 34
        SiSpacePointsSeedMaker_HeavyIon = 35
        SiSpacePointsSeedMaker_LowMomentum = 36
        SiSpacePointsSeedMaker_BeamGas = 37
        SiSpacePointsSeedMaker_VeryLowMomentum = 38
        MuidMuonRecoveryTool = 39
        MuidStandaloneRefit = 40
        TrackInCaloROI = 41
        SiSpacePointsSeedMaker_ForwardTracks = 42
        strategyA = 43
        strategyB = 44
        strategyC = 45
        FTK = 46
        FastTrackFinderSeed = 47
        SiSPSeededFinderSimple = 48
        SiSpacePointsSeedMaker_LargeD0 = 49
        SiSpacePointsSeedMaker_SLHCConversionTracks = 50
        Pseudotracking = 51
        NumberOfTrackRecoInfo = 52

    class ParticleHypothesis(Enum):
        nonInteracting = 0
        geantino = 0
        electron = 1
        muon = 2
        pion = 3
        kaon = 4
        proton = 5
        photon = 6
        neutron = 7
        pi0 = 8
        k0 = 9
        nonInteractingMuon = 10
        noHypothesis = 99
        undefined = 99

    class ParameterPosition(Enum):
        BeamLine = 0
        FirstMeasurement = 1
        LastMeasurement = 2
        CalorimeterEntrance = 3
        CalorimeterExit = 4
        MuonSpectrometerEntrance = 5

    class SummaryType(Enum):
        numberOfContribPixelLayers = 29
        numberOfBLayerHits = 0
        numberOfBLayerOutliers = 31
        numberOfBLayerSharedHits = 16
        numberOfBLayerSplitHits = 43
        expectBLayerHit = 42
        expectInnermostPixelLayerHit = 52
        numberOfInnermostPixelLayerHits = 53
        numberOfInnermostPixelLayerOutliers = 54
        numberOfInnermostPixelLayerSharedHits = 55
        numberOfInnermostPixelLayerSplitHits = 56
        expectNextToInnermostPixelLayerHit = 57
        numberOfNextToInnermostPixelLayerHits = 58
        numberOfNextToInnermostPixelLayerOutliers = 59
        numberOfNextToInnermostPixelLayerSharedHits = 60
        numberOfNextToInnermostPixelLayerSplitHits = 61
        numberOfDBMHits = 63
        numberOfPixelHits = 2
        numberOfPixelOutliers = 41
        numberOfPixelHoles = 1
        numberOfPixelSharedHits = 17
        numberOfPixelSplitHits = 44
        numberOfGangedPixels = 14
        numberOfGangedFlaggedFakes = 32
        numberOfPixelDeadSensors = 33
        numberOfPixelSpoiltHits = 35
        numberOfSCTHits = 3
        numberOfSCTOutliers = 39
        numberOfSCTHoles = 4
        numberOfSCTDoubleHoles = 28
        numberOfSCTSharedHits = 18
        numberOfSCTDeadSensors = 34
        numberOfSCTSpoiltHits = 36
        numberOfTRTHits = 5
        numberOfTRTOutliers = 19
        numberOfTRTHoles = 40
        numberOfTRTHighThresholdHits = 6
        numberOfTRTHighThresholdHitsTotal = 64
        numberOfTRTHighThresholdOutliers = 20
        numberOfTRTDeadStraws = 37
        numberOfTRTTubeHits = 38
        numberOfTRTXenonHits = 46
        numberOfTRTSharedHits = 62
        numberOfPrecisionLayers = 7
        numberOfPrecisionHoleLayers = 8
        numberOfPhiLayers = 9
        numberOfPhiHoleLayers = 10
        numberOfTriggerEtaLayers = 11
        numberOfTriggerEtaHoleLayers = 12
        numberOfGoodPrecisionLayers = 66
        numberOfOutliersOnTrack = 15
        standardDeviationOfChi2OS = 30
        eProbabilityComb = 47
        eProbabilityHT = 48
        pixeldEdx = 51
        numberOfTrackSummaryTypes = 67

    class MuonSummaryType(Enum):
        primarySector = 0
        secondarySector = 1
        innerSmallHits = 2
        innerLargeHits = 3
        middleSmallHits = 4
        middleLargeHits = 5
        outerSmallHits = 6
        outerLargeHits = 7
        extendedSmallHits = 8
        extendedLargeHits = 9
        innerSmallHoles = 10
        innerLargeHoles = 11
        middleSmallHoles = 12
        middleLargeHoles = 13
        outerSmallHoles = 14
        outerLargeHoles = 15
        extendedSmallHoles = 16
        extendedLargeHoles = 17
        phiLayer1Hits = 18
        phiLayer2Hits = 19
        phiLayer3Hits = 20
        phiLayer4Hits = 21
        etaLayer1Hits = 22
        etaLayer2Hits = 23
        etaLayer3Hits = 24
        etaLayer4Hits = 25
        phiLayer1Holes = 26
        phiLayer2Holes = 27
        phiLayer3Holes = 28
        phiLayer4Holes = 29
        etaLayer1Holes = 30
        etaLayer2Holes = 31
        etaLayer3Holes = 32
        etaLayer4Holes = 33
        innerClosePrecisionHits = 34
        middleClosePrecisionHits = 35
        outerClosePrecisionHits = 36
        extendedClosePrecisionHits = 37
        innerOutBoundsPrecisionHits = 38
        middleOutBoundsPrecisionHits = 39
        outerOutBoundsPrecisionHits = 40
        extendedOutBoundsPrecisionHits = 41
        combinedTrackOutBoundsPrecisionHits = 42
        isEndcapGoodLayers = 43
        isSmallGoodSectors = 44
        phiLayer1RPCHits = 45
        phiLayer2RPCHits = 46
        phiLayer3RPCHits = 47
        phiLayer4RPCHits = 48
        etaLayer1RPCHits = 49
        etaLayer2RPCHits = 50
        etaLayer3RPCHits = 51
        etaLayer4RPCHits = 52
        phiLayer1RPCHoles = 53
        phiLayer2RPCHoles = 54
        phiLayer3RPCHoles = 55
        phiLayer4RPCHoles = 56
        etaLayer1RPCHoles = 57
        etaLayer2RPCHoles = 58
        etaLayer3RPCHoles = 59
        etaLayer4RPCHoles = 60
        phiLayer1TGCHits = 61
        phiLayer2TGCHits = 62
        phiLayer3TGCHits = 63
        phiLayer4TGCHits = 64
        etaLayer1TGCHits = 65
        etaLayer2TGCHits = 66
        etaLayer3TGCHits = 67
        etaLayer4TGCHits = 68
        phiLayer1TGCHoles = 69
        phiLayer2TGCHoles = 70
        phiLayer3TGCHoles = 71
        phiLayer4TGCHoles = 72
        etaLayer1TGCHoles = 73
        etaLayer2TGCHoles = 74
        etaLayer3TGCHoles = 75
        etaLayer4TGCHoles = 76
        phiLayer1STGCHits = 79
        phiLayer2STGCHits = 80
        etaLayer1STGCHits = 81
        etaLayer2STGCHits = 82
        phiLayer1STGCHoles = 83
        phiLayer2STGCHoles = 84
        etaLayer1STGCHoles = 85
        etaLayer2STGCHoles = 86
        mmHits = 87
        mmHoles = 88
        cscEtaHits = 77
        cscUnspoiledEtaHits = 78
        numberOfMuonSummaryTypes = 89

    class BTagInfo(Enum):
        SV0_NGTinJet = 100
        SV0_NGTinSvx = 101
        SV0_N2Tpair = 102
        SV0_masssvx = 103
        SV0_efracsvx = 104
        SV0_normdist = 105
        SV1_NGTinJet = 200
        SV1_NGTinSvx = 201
        SV1_N2Tpair = 202
        SV1_masssvx = 203
        SV1_efracsvx = 204
        SV1_normdist = 205
        JetFitter_nVTX = 300
        JetFitter_nSingleTracks = 301
        JetFitter_nTracksAtVtx = 302
        JetFitter_mass = 303
        JetFitter_energyFraction = 304
        JetFitter_significance3d = 305
        JetFitter_deltaeta = 306
        JetFitter_deltaphi = 307
        JetFitter_N2Tpair = 308
        IP2D_ntrk = 400
        IP2D_gradeOfTracks = 401
        IP2D_flagFromV0ofTracks = 404
        IP2D_valD0wrtPVofTracks = 405
        IP2D_sigD0wrtPVofTracks = 406
        IP2D_weightBofTracks = 409
        IP2D_weightUofTracks = 410
        IP2D_weightCofTracks = 411
        IP3D_ntrk = 500
        IP3D_gradeOfTracks = 501
        IP3D_flagFromV0ofTracks = 504
        IP3D_valD0wrtPVofTracks = 505
        IP3D_sigD0wrtPVofTracks = 506
        IP3D_valZ0wrtPVofTracks = 507
        IP3D_sigZ0wrtPVofTracks = 508
        IP3D_weightBofTracks = 509
        IP3D_weightUofTracks = 510
        IP3D_weightCofTracks = 511

    class JetConstitScale(Enum):
        UncalibratedJetConstituent = 0
        CalibratedJetConstituent = 1

    class JetScale(Enum):
        JetEMScaleMomentum = 0
        JetConstitScaleMomentum = 1
        JetAssignedScaleMomentum = 2


    def setOriginalObjectLink(self, original: func_adl_servicex_xaodr21.xAOD.iparticle.IParticle, copy: func_adl_servicex_xaodr21.xAOD.iparticle.IParticle) -> bool:
        "A method"
        ...

    def getOriginalObject(self, copy: func_adl_servicex_xaodr21.xAOD.iparticle.IParticle) -> func_adl_servicex_xaodr21.xAOD.iparticle.IParticle:
        "A method"
        ...
