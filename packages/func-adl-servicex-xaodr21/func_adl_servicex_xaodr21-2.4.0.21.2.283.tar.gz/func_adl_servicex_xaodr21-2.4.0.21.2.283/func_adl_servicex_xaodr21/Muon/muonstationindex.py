from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr21

_method_map = {
    'toStationIndex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'Muon::MuonStationIndex',
        'method_name': 'toStationIndex',
        'return_type': 'Muon::MuonStationIndex::StIndex',
    },
    'toLayerIndex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'Muon::MuonStationIndex',
        'method_name': 'toLayerIndex',
        'return_type': 'Muon::MuonStationIndex::LayerIndex',
    },
    'toChamberIndex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'Muon::MuonStationIndex',
        'method_name': 'toChamberIndex',
        'return_type': 'Muon::MuonStationIndex::ChIndex',
    },
    'phiName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'Muon::MuonStationIndex',
        'method_name': 'phiName',
        'return_type': 'const string',
    },
    'stName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'Muon::MuonStationIndex',
        'method_name': 'stName',
        'return_type': 'const string',
    },
    'chName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'Muon::MuonStationIndex',
        'method_name': 'chName',
        'return_type': 'const string',
    },
    'regionName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'Muon::MuonStationIndex',
        'method_name': 'regionName',
        'return_type': 'const string',
    },
    'layerName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'Muon::MuonStationIndex',
        'method_name': 'layerName',
        'return_type': 'const string',
    },
    'technologyName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'Muon::MuonStationIndex',
        'method_name': 'technologyName',
        'return_type': 'const string',
    },
    'sectorLayerHash': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'Muon::MuonStationIndex',
        'method_name': 'sectorLayerHash',
        'return_type': 'unsigned int',
    },
    'sectorLayerHashMax': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'Muon::MuonStationIndex',
        'method_name': 'sectorLayerHashMax',
        'return_type': 'unsigned int',
    },
    'numberOfSectors': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'Muon::MuonStationIndex',
        'method_name': 'numberOfSectors',
        'return_type': 'unsigned int',
    },
    'chIndex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'Muon::MuonStationIndex',
        'method_name': 'chIndex',
        'return_type': 'Muon::MuonStationIndex::ChIndex',
    },
}

_enum_function_map = {
    'toStationIndex': [
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
        {
            'metadata_type': 'define_enum',
            'namespace': 'Muon.MuonStationIndex',
            'name': 'StIndex',
            'values': [
                'StUnknown',
                'BI',
                'BM',
                'BO',
                'BE',
                'EI',
                'EM',
                'EO',
                'EE',
                'StIndexMax',
            ],
        },
    ],
    'toLayerIndex': [
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
        {
            'metadata_type': 'define_enum',
            'namespace': 'Muon.MuonStationIndex',
            'name': 'LayerIndex',
            'values': [
                'LayerUnknown',
                'Inner',
                'Middle',
                'Outer',
                'Extended',
                'BarrelExtended',
                'LayerIndexMax',
            ],
        },
    ],
    'toChamberIndex': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'Muon.MuonStationIndex',
            'name': 'DetectorRegionIndex',
            'values': [
                'DetectorRegionUnknown',
                'EndcapA',
                'Barrel',
                'EndcapC',
                'DetectorRegionIndexMax',
            ],
        },
        {
            'metadata_type': 'define_enum',
            'namespace': 'Muon.MuonStationIndex',
            'name': 'LayerIndex',
            'values': [
                'LayerUnknown',
                'Inner',
                'Middle',
                'Outer',
                'Extended',
                'BarrelExtended',
                'LayerIndexMax',
            ],
        },
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
    'phiName': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'Muon.MuonStationIndex',
            'name': 'PhiIndex',
            'values': [
                'PhiUnknown',
                'BM1',
                'BM2',
                'BO1',
                'BO2',
                'T1',
                'T2',
                'T3',
                'T4',
                'CSC',
                'STGC1',
                'STGC2',
                'PhiIndexMax',
            ],
        },
    ],
    'stName': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'Muon.MuonStationIndex',
            'name': 'StIndex',
            'values': [
                'StUnknown',
                'BI',
                'BM',
                'BO',
                'BE',
                'EI',
                'EM',
                'EO',
                'EE',
                'StIndexMax',
            ],
        },
    ],
    'chName': [
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
    'regionName': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'Muon.MuonStationIndex',
            'name': 'DetectorRegionIndex',
            'values': [
                'DetectorRegionUnknown',
                'EndcapA',
                'Barrel',
                'EndcapC',
                'DetectorRegionIndexMax',
            ],
        },
    ],
    'layerName': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'Muon.MuonStationIndex',
            'name': 'LayerIndex',
            'values': [
                'LayerUnknown',
                'Inner',
                'Middle',
                'Outer',
                'Extended',
                'BarrelExtended',
                'LayerIndexMax',
            ],
        },
    ],
    'technologyName': [
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
    'sectorLayerHash': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'Muon.MuonStationIndex',
            'name': 'DetectorRegionIndex',
            'values': [
                'DetectorRegionUnknown',
                'EndcapA',
                'Barrel',
                'EndcapC',
                'DetectorRegionIndexMax',
            ],
        },
        {
            'metadata_type': 'define_enum',
            'namespace': 'Muon.MuonStationIndex',
            'name': 'LayerIndex',
            'values': [
                'LayerUnknown',
                'Inner',
                'Middle',
                'Outer',
                'Extended',
                'BarrelExtended',
                'LayerIndexMax',
            ],
        },
    ],
    'chIndex': [
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
}

_defined_enums = {
    'ChIndex':
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
    'TechnologyIndex':
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
    'StIndex':
        {
            'metadata_type': 'define_enum',
            'namespace': 'Muon.MuonStationIndex',
            'name': 'StIndex',
            'values': [
                'StUnknown',
                'BI',
                'BM',
                'BO',
                'BE',
                'EI',
                'EM',
                'EO',
                'EE',
                'StIndexMax',
            ],
        },
    'PhiIndex':
        {
            'metadata_type': 'define_enum',
            'namespace': 'Muon.MuonStationIndex',
            'name': 'PhiIndex',
            'values': [
                'PhiUnknown',
                'BM1',
                'BM2',
                'BO1',
                'BO2',
                'T1',
                'T2',
                'T3',
                'T4',
                'CSC',
                'STGC1',
                'STGC2',
                'PhiIndexMax',
            ],
        },
    'LayerIndex':
        {
            'metadata_type': 'define_enum',
            'namespace': 'Muon.MuonStationIndex',
            'name': 'LayerIndex',
            'values': [
                'LayerUnknown',
                'Inner',
                'Middle',
                'Outer',
                'Extended',
                'BarrelExtended',
                'LayerIndexMax',
            ],
        },
    'DetectorRegionIndex':
        {
            'metadata_type': 'define_enum',
            'namespace': 'Muon.MuonStationIndex',
            'name': 'DetectorRegionIndex',
            'values': [
                'DetectorRegionUnknown',
                'EndcapA',
                'Barrel',
                'EndcapC',
                'DetectorRegionIndexMax',
            ],
        },      
}

_object_cpp_as_py_namespace="Muon"

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
class MuonStationIndex:
    "A class"

    class ChIndex(Enum):
        ChUnknown = -1
        BIS = 0
        BIL = 1
        BMS = 2
        BML = 3
        BOS = 4
        BOL = 5
        BEE = 6
        EIS = 7
        EIL = 8
        EMS = 9
        EML = 10
        EOS = 11
        EOL = 12
        EES = 13
        EEL = 14
        CSS = 15
        CSL = 16
        ChIndexMax = 17

    class TechnologyIndex(Enum):
        TechnologyUnknown = -1
        MDT = 0
        CSCI = 1
        RPC = 2
        TGC = 3
        STGC = 4
        MM = 5
        TechnologyIndexMax = 6

    class StIndex(Enum):
        StUnknown = -1
        BI = 0
        BM = 1
        BO = 2
        BE = 3
        EI = 4
        EM = 5
        EO = 6
        EE = 7
        StIndexMax = 8

    class PhiIndex(Enum):
        PhiUnknown = -1
        BM1 = 0
        BM2 = 1
        BO1 = 2
        BO2 = 3
        T1 = 4
        T2 = 5
        T3 = 6
        T4 = 7
        CSC = 8
        STGC1 = 9
        STGC2 = 10
        PhiIndexMax = 11

    class LayerIndex(Enum):
        LayerUnknown = -1
        Inner = 0
        Middle = 1
        Outer = 2
        Extended = 3
        BarrelExtended = 4
        LayerIndexMax = 5

    class DetectorRegionIndex(Enum):
        DetectorRegionUnknown = -1
        EndcapA = 0
        Barrel = 1
        EndcapC = 2
        DetectorRegionIndexMax = 3


    def toStationIndex(self, index: func_adl_servicex_xaodr21.Muon.muonstationindex.MuonStationIndex.ChIndex) -> func_adl_servicex_xaodr21.Muon.muonstationindex.MuonStationIndex.StIndex:
        "A method"
        ...

    def toLayerIndex(self, index: func_adl_servicex_xaodr21.Muon.muonstationindex.MuonStationIndex.ChIndex) -> func_adl_servicex_xaodr21.Muon.muonstationindex.MuonStationIndex.LayerIndex:
        "A method"
        ...

    def toChamberIndex(self, region: func_adl_servicex_xaodr21.Muon.muonstationindex.MuonStationIndex.DetectorRegionIndex, layer: func_adl_servicex_xaodr21.Muon.muonstationindex.MuonStationIndex.LayerIndex, isSmall: bool) -> func_adl_servicex_xaodr21.Muon.muonstationindex.MuonStationIndex.ChIndex:
        "A method"
        ...

    def phiName(self, index: func_adl_servicex_xaodr21.Muon.muonstationindex.MuonStationIndex.PhiIndex) -> str:
        "A method"
        ...

    def stName(self, index: func_adl_servicex_xaodr21.Muon.muonstationindex.MuonStationIndex.StIndex) -> str:
        "A method"
        ...

    def chName(self, index: func_adl_servicex_xaodr21.Muon.muonstationindex.MuonStationIndex.ChIndex) -> str:
        "A method"
        ...

    def regionName(self, index: func_adl_servicex_xaodr21.Muon.muonstationindex.MuonStationIndex.DetectorRegionIndex) -> str:
        "A method"
        ...

    def layerName(self, index: func_adl_servicex_xaodr21.Muon.muonstationindex.MuonStationIndex.LayerIndex) -> str:
        "A method"
        ...

    def technologyName(self, index: func_adl_servicex_xaodr21.Muon.muonstationindex.MuonStationIndex.TechnologyIndex) -> str:
        "A method"
        ...

    def sectorLayerHash(self, detectorRegionIndex: func_adl_servicex_xaodr21.Muon.muonstationindex.MuonStationIndex.DetectorRegionIndex, layerIndex: func_adl_servicex_xaodr21.Muon.muonstationindex.MuonStationIndex.LayerIndex) -> int:
        "A method"
        ...

    def sectorLayerHashMax(self) -> int:
        "A method"
        ...

    def numberOfSectors(self) -> int:
        "A method"
        ...

    def chIndex(self, index: str) -> func_adl_servicex_xaodr21.Muon.muonstationindex.MuonStationIndex.ChIndex:
        "A method"
        ...
