from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr21

_method_map = {
    'runNumber': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'runNumber',
        'return_type': 'unsigned int',
    },
    'eventNumber': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'eventNumber',
        'return_type': 'unsigned long long',
    },
    'lumiBlock': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'lumiBlock',
        'return_type': 'unsigned int',
    },
    'timeStamp': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'timeStamp',
        'return_type': 'unsigned int',
    },
    'timeStampNSOffset': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'timeStampNSOffset',
        'return_type': 'unsigned int',
    },
    'bcid': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'bcid',
        'return_type': 'unsigned int',
    },
    'detectorMask0': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'detectorMask0',
        'return_type': 'unsigned int',
    },
    'detectorMask1': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'detectorMask1',
        'return_type': 'unsigned int',
    },
    'detectorMask2': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'detectorMask2',
        'return_type': 'unsigned int',
    },
    'detectorMask3': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'detectorMask3',
        'return_type': 'unsigned int',
    },
    'detectorMask': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'detectorMask',
        'return_type': 'uint64_t',
    },
    'detectorMaskExt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'detectorMaskExt',
        'return_type': 'uint64_t',
    },
    'mcChannelNumber': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'mcChannelNumber',
        'return_type': 'unsigned int',
    },
    'mcEventNumber': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'mcEventNumber',
        'return_type': 'unsigned long long',
    },
    'mcEventWeights': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'mcEventWeights',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'mcEventWeight': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'mcEventWeight',
        'return_type': 'float',
    },
    'hasMCEventWeights': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'hasMCEventWeights',
        'return_type': 'bool',
    },
    'eventTypeBitmask': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'eventTypeBitmask',
        'return_type': 'unsigned int',
    },
    'eventType': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'eventType',
        'return_type': 'bool',
    },
    'statusElement': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'statusElement',
        'return_type': 'unsigned int',
    },
    'extendedLevel1ID': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'extendedLevel1ID',
        'return_type': 'unsigned int',
    },
    'level1TriggerType': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'level1TriggerType',
        'return_type': 'uint16_t',
    },
    'streamTags': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'streamTags',
        'return_type_element': 'xAOD::EventInfo_v1::StreamTag',
        'return_type_collection': 'const vector<xAOD::EventInfo_v1::StreamTag>',
    },
    'actualInteractionsPerCrossing': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'actualInteractionsPerCrossing',
        'return_type': 'float',
    },
    'averageInteractionsPerCrossing': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'averageInteractionsPerCrossing',
        'return_type': 'float',
    },
    'subEvents': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'subEvents',
        'return_type_element': 'xAOD::EventInfo_v1::SubEvent',
        'return_type_collection': 'const vector<xAOD::EventInfo_v1::SubEvent>',
    },
    'eventFlags': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'eventFlags',
        'return_type': 'unsigned int',
    },
    'isEventFlagBitSet': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'isEventFlagBitSet',
        'return_type': 'bool',
    },
    'setEventFlags': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'setEventFlags',
        'return_type': 'bool',
    },
    'setEventFlagBit': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'setEventFlagBit',
        'return_type': 'bool',
    },
    'errorState': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'errorState',
        'return_type': 'xAOD::EventInfo_v1::EventFlagErrorState',
    },
    'setErrorState': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'setErrorState',
        'return_type': 'bool',
    },
    'beamPosX': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'beamPosX',
        'return_type': 'float',
    },
    'beamPosY': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'beamPosY',
        'return_type': 'float',
    },
    'beamPosZ': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'beamPosZ',
        'return_type': 'float',
    },
    'beamPosSigmaX': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'beamPosSigmaX',
        'return_type': 'float',
    },
    'beamPosSigmaY': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'beamPosSigmaY',
        'return_type': 'float',
    },
    'beamPosSigmaZ': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'beamPosSigmaZ',
        'return_type': 'float',
    },
    'beamPosSigmaXY': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'beamPosSigmaXY',
        'return_type': 'float',
    },
    'beamTiltXZ': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'beamTiltXZ',
        'return_type': 'float',
    },
    'beamTiltYZ': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'beamTiltYZ',
        'return_type': 'float',
    },
    'beamStatus': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'beamStatus',
        'return_type': 'unsigned int',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1',
        'method_name': 'isAvailable',
        'return_type': 'bool',
    },
}

_enum_function_map = {
    'eventType': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.EventInfo_v1',
            'name': 'EventType',
            'values': [
                'IS_SIMULATION',
                'IS_TESTBEAM',
                'IS_CALIBRATION',
            ],
        },
    ],
    'eventFlags': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.EventInfo_v1',
            'name': 'EventFlagSubDet',
            'values': [
                'Pixel',
                'SCT',
                'TRT',
                'LAr',
                'Tile',
                'Muon',
                'ForwardDet',
                'Core',
                'Background',
                'Lumi',
                'nDets',
            ],
        },
    ],
    'isEventFlagBitSet': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.EventInfo_v1',
            'name': 'EventFlagSubDet',
            'values': [
                'Pixel',
                'SCT',
                'TRT',
                'LAr',
                'Tile',
                'Muon',
                'ForwardDet',
                'Core',
                'Background',
                'Lumi',
                'nDets',
            ],
        },
    ],
    'setEventFlags': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.EventInfo_v1',
            'name': 'EventFlagSubDet',
            'values': [
                'Pixel',
                'SCT',
                'TRT',
                'LAr',
                'Tile',
                'Muon',
                'ForwardDet',
                'Core',
                'Background',
                'Lumi',
                'nDets',
            ],
        },
    ],
    'setEventFlagBit': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.EventInfo_v1',
            'name': 'EventFlagSubDet',
            'values': [
                'Pixel',
                'SCT',
                'TRT',
                'LAr',
                'Tile',
                'Muon',
                'ForwardDet',
                'Core',
                'Background',
                'Lumi',
                'nDets',
            ],
        },
    ],
    'errorState': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.EventInfo_v1',
            'name': 'EventFlagSubDet',
            'values': [
                'Pixel',
                'SCT',
                'TRT',
                'LAr',
                'Tile',
                'Muon',
                'ForwardDet',
                'Core',
                'Background',
                'Lumi',
                'nDets',
            ],
        },
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.EventInfo_v1',
            'name': 'EventFlagErrorState',
            'values': [
                'NotSet',
                'Warning',
                'Error',
            ],
        },
    ],
    'setErrorState': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.EventInfo_v1',
            'name': 'EventFlagSubDet',
            'values': [
                'Pixel',
                'SCT',
                'TRT',
                'LAr',
                'Tile',
                'Muon',
                'ForwardDet',
                'Core',
                'Background',
                'Lumi',
                'nDets',
            ],
        },
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.EventInfo_v1',
            'name': 'EventFlagErrorState',
            'values': [
                'NotSet',
                'Warning',
                'Error',
            ],
        },
    ],      
}

_defined_enums = {
    'EventType':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.EventInfo_v1',
            'name': 'EventType',
            'values': [
                'IS_SIMULATION',
                'IS_TESTBEAM',
                'IS_CALIBRATION',
            ],
        },
    'PileUpType':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.EventInfo_v1',
            'name': 'PileUpType',
            'values': [
                'Unknown',
                'Signal',
                'MinimumBias',
                'Cavern',
                'HaloGas',
                'ZeroBias',
            ],
        },
    'EventFlagSubDet':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.EventInfo_v1',
            'name': 'EventFlagSubDet',
            'values': [
                'Pixel',
                'SCT',
                'TRT',
                'LAr',
                'Tile',
                'Muon',
                'ForwardDet',
                'Core',
                'Background',
                'Lumi',
                'nDets',
            ],
        },
    'EventFlagErrorState':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.EventInfo_v1',
            'name': 'EventFlagErrorState',
            'values': [
                'NotSet',
                'Warning',
                'Error',
            ],
        },
    'BackgroundEventFlag':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.EventInfo_v1',
            'name': 'BackgroundEventFlag',
            'values': [
                'MBTSTimeDiffHalo',
                'MBTSTimeDiffCol',
                'LArECTimeDiffHalo',
                'LArECTimeDiffCol',
                'PixMultiplicityHuge',
                'PixSPNonEmpty',
                'SCTMultiplicityHuge',
                'SCTSPNonEmpty',
                'CSCTimeDiffHalo',
                'CSCTimeDiffCol',
                'BCMTimeDiffHalo',
                'BCMTimeDiffCol',
                'MuonTimingCol',
                'MuonTimingCosmic',
                'MBTSBeamVeto',
                'BCMBeamVeto',
                'LUCIDBeamVeto',
                'HaloMuonSegment',
                'HaloClusterShape',
                'HaloMuonOneSided',
                'HaloMuonTwoSided',
                'HaloTileClusterPattern',
                'BeamGasPixel',
                'CosmicStandAlone',
                'CosmicStandAloneTight',
                'CosmicCombined',
                'CosmicCombinedTight',
                'BkgdResvBit1',
                'BkgdResvBit2',
                'BkgdResvBit3',
                'BkgdResvBit4',
                'BkgdResvBit5',
                'NBackgroundWords',
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

        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODEventInfo/versions/EventInfo_v1.h',
            'body_includes': ["xAODEventInfo/versions/EventInfo_v1.h"],
        })


        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODEventInfo',
            'link_libraries': ["xAODEventInfo"],
        })

        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class EventInfo_v1:
    "A class"

    class EventType(Enum):
        IS_SIMULATION = 1
        IS_TESTBEAM = 2
        IS_CALIBRATION = 4

    class PileUpType(Enum):
        Unknown = 99
        Signal = 0
        MinimumBias = 1
        Cavern = 2
        HaloGas = 3
        ZeroBias = 4

    class EventFlagSubDet(Enum):
        Pixel = 0
        SCT = 1
        TRT = 2
        LAr = 3
        Tile = 4
        Muon = 5
        ForwardDet = 6
        Core = 7
        Background = 8
        Lumi = 9
        nDets = 10

    class EventFlagErrorState(Enum):
        NotSet = 0
        Warning = 1
        Error = 2

    class BackgroundEventFlag(Enum):
        MBTSTimeDiffHalo = 0
        MBTSTimeDiffCol = 1
        LArECTimeDiffHalo = 2
        LArECTimeDiffCol = 3
        PixMultiplicityHuge = 4
        PixSPNonEmpty = 5
        SCTMultiplicityHuge = 6
        SCTSPNonEmpty = 7
        CSCTimeDiffHalo = 8
        CSCTimeDiffCol = 9
        BCMTimeDiffHalo = 10
        BCMTimeDiffCol = 11
        MuonTimingCol = 12
        MuonTimingCosmic = 13
        MBTSBeamVeto = 14
        BCMBeamVeto = 15
        LUCIDBeamVeto = 16
        HaloMuonSegment = 17
        HaloClusterShape = 18
        HaloMuonOneSided = 19
        HaloMuonTwoSided = 20
        HaloTileClusterPattern = 21
        BeamGasPixel = 22
        CosmicStandAlone = 23
        CosmicStandAloneTight = 24
        CosmicCombined = 25
        CosmicCombinedTight = 26
        BkgdResvBit1 = 27
        BkgdResvBit2 = 28
        BkgdResvBit3 = 29
        BkgdResvBit4 = 30
        BkgdResvBit5 = 31
        NBackgroundWords = 32


    def runNumber(self) -> int:
        "A method"
        ...

    def eventNumber(self) -> int:
        "A method"
        ...

    def lumiBlock(self) -> int:
        "A method"
        ...

    def timeStamp(self) -> int:
        "A method"
        ...

    def timeStampNSOffset(self) -> int:
        "A method"
        ...

    def bcid(self) -> int:
        "A method"
        ...

    def detectorMask0(self) -> int:
        "A method"
        ...

    def detectorMask1(self) -> int:
        "A method"
        ...

    def detectorMask2(self) -> int:
        "A method"
        ...

    def detectorMask3(self) -> int:
        "A method"
        ...

    def detectorMask(self) -> int:
        "A method"
        ...

    def detectorMaskExt(self) -> int:
        "A method"
        ...

    def mcChannelNumber(self) -> int:
        "A method"
        ...

    def mcEventNumber(self) -> int:
        "A method"
        ...

    def mcEventWeights(self) -> func_adl_servicex_xaodr21.vector_float_.vector_float_:
        "A method"
        ...

    def mcEventWeight(self, i: int) -> float:
        "A method"
        ...

    def hasMCEventWeights(self) -> bool:
        "A method"
        ...

    def eventTypeBitmask(self) -> int:
        "A method"
        ...

    def eventType(self, type: func_adl_servicex_xaodr21.xAOD.eventinfo_v1.EventInfo_v1.EventType) -> bool:
        "A method"
        ...

    def statusElement(self) -> int:
        "A method"
        ...

    def extendedLevel1ID(self) -> int:
        "A method"
        ...

    def level1TriggerType(self) -> int:
        "A method"
        ...

    def streamTags(self) -> func_adl_servicex_xaodr21.vector_xaod_eventinfo_v1_streamtag_.vector_xAOD_EventInfo_v1_StreamTag_:
        "A method"
        ...

    def actualInteractionsPerCrossing(self) -> float:
        "A method"
        ...

    def averageInteractionsPerCrossing(self) -> float:
        "A method"
        ...

    def subEvents(self) -> func_adl_servicex_xaodr21.vector_xaod_eventinfo_v1_subevent_.vector_xAOD_EventInfo_v1_SubEvent_:
        "A method"
        ...

    def eventFlags(self, subDet: func_adl_servicex_xaodr21.xAOD.eventinfo_v1.EventInfo_v1.EventFlagSubDet) -> int:
        "A method"
        ...

    def isEventFlagBitSet(self, subDet: func_adl_servicex_xaodr21.xAOD.eventinfo_v1.EventInfo_v1.EventFlagSubDet, bit: int) -> bool:
        "A method"
        ...

    def setEventFlags(self, subDet: func_adl_servicex_xaodr21.xAOD.eventinfo_v1.EventInfo_v1.EventFlagSubDet, flags: int) -> bool:
        "A method"
        ...

    def setEventFlagBit(self, subDet: func_adl_servicex_xaodr21.xAOD.eventinfo_v1.EventInfo_v1.EventFlagSubDet, bit: int, set: bool) -> bool:
        "A method"
        ...

    def errorState(self, subDet: func_adl_servicex_xaodr21.xAOD.eventinfo_v1.EventInfo_v1.EventFlagSubDet) -> func_adl_servicex_xaodr21.xAOD.eventinfo_v1.EventInfo_v1.EventFlagErrorState:
        "A method"
        ...

    def setErrorState(self, subDet: func_adl_servicex_xaodr21.xAOD.eventinfo_v1.EventInfo_v1.EventFlagSubDet, state: func_adl_servicex_xaodr21.xAOD.eventinfo_v1.EventInfo_v1.EventFlagErrorState) -> bool:
        "A method"
        ...

    def beamPosX(self) -> float:
        "A method"
        ...

    def beamPosY(self) -> float:
        "A method"
        ...

    def beamPosZ(self) -> float:
        "A method"
        ...

    def beamPosSigmaX(self) -> float:
        "A method"
        ...

    def beamPosSigmaY(self) -> float:
        "A method"
        ...

    def beamPosSigmaZ(self) -> float:
        "A method"
        ...

    def beamPosSigmaXY(self) -> float:
        "A method"
        ...

    def beamTiltXZ(self) -> float:
        "A method"
        ...

    def beamTiltYZ(self) -> float:
        "A method"
        ...

    def beamStatus(self) -> int:
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
