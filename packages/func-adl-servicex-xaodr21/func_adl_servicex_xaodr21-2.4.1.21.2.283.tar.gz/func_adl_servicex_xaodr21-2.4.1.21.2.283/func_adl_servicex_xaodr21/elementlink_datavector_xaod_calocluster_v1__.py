from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr21

_method_map = {
    'isValid': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'isValid',
        'return_type': 'bool',
    },
    'pt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'pt',
        'return_type': 'double',
        'deref_count': 2
    },
    'eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'eta',
        'return_type': 'double',
        'deref_count': 2
    },
    'phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'phi',
        'return_type': 'double',
        'deref_count': 2
    },
    'm': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'm',
        'return_type': 'double',
        'deref_count': 2
    },
    'e': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'e',
        'return_type': 'double',
        'deref_count': 2
    },
    'rapidity': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'rapidity',
        'return_type': 'double',
        'deref_count': 2
    },
    'p4': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'p4',
        'return_type': 'const TLorentzVector',
        'deref_count': 2
    },
    'type': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'type',
        'return_type': 'xAOD::Type::ObjectType',
        'deref_count': 2
    },
    'et': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'et',
        'return_type': 'double',
        'deref_count': 2
    },
    'eSample': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'eSample',
        'return_type': 'float',
        'deref_count': 2
    },
    'etaSample': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'etaSample',
        'return_type': 'float',
        'deref_count': 2
    },
    'phiSample': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'phiSample',
        'return_type': 'float',
        'deref_count': 2
    },
    'energy_max': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'energy_max',
        'return_type': 'float',
        'deref_count': 2
    },
    'etamax': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'etamax',
        'return_type': 'float',
        'deref_count': 2
    },
    'phimax': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'phimax',
        'return_type': 'float',
        'deref_count': 2
    },
    'etasize': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'etasize',
        'return_type': 'float',
        'deref_count': 2
    },
    'phisize': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'phisize',
        'return_type': 'float',
        'deref_count': 2
    },
    'energyBE': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'energyBE',
        'return_type': 'float',
        'deref_count': 2
    },
    'etaBE': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'etaBE',
        'return_type': 'float',
        'deref_count': 2
    },
    'phiBE': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'phiBE',
        'return_type': 'float',
        'deref_count': 2
    },
    'setEnergy': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'setEnergy',
        'return_type': 'bool',
        'deref_count': 2
    },
    'setEta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'setEta',
        'return_type': 'bool',
        'deref_count': 2
    },
    'setPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'setPhi',
        'return_type': 'bool',
        'deref_count': 2
    },
    'setEmax': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'setEmax',
        'return_type': 'bool',
        'deref_count': 2
    },
    'setEtamax': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'setEtamax',
        'return_type': 'bool',
        'deref_count': 2
    },
    'setPhimax': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'setPhimax',
        'return_type': 'bool',
        'deref_count': 2
    },
    'setEtasize': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'setEtasize',
        'return_type': 'bool',
        'deref_count': 2
    },
    'setPhisize': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'setPhisize',
        'return_type': 'bool',
        'deref_count': 2
    },
    'retrieveMoment': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'retrieveMoment',
        'return_type': 'bool',
        'deref_count': 2
    },
    'getMomentValue': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'getMomentValue',
        'return_type': 'double',
        'deref_count': 2
    },
    'eta0': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'eta0',
        'return_type': 'float',
        'deref_count': 2
    },
    'phi0': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'phi0',
        'return_type': 'float',
        'deref_count': 2
    },
    'time': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'time',
        'return_type': 'float',
        'deref_count': 2
    },
    'samplingPattern': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'samplingPattern',
        'return_type': 'unsigned int',
        'deref_count': 2
    },
    'nSamples': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'nSamples',
        'return_type': 'unsigned int',
        'deref_count': 2
    },
    'hasSampling': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'hasSampling',
        'return_type': 'bool',
        'deref_count': 2
    },
    'clusterSize': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'clusterSize',
        'return_type': 'xAOD::CaloCluster_v1::ClusterSize',
        'deref_count': 2
    },
    'inBarrel': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'inBarrel',
        'return_type': 'bool',
        'deref_count': 2
    },
    'inEndcap': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'inEndcap',
        'return_type': 'bool',
        'deref_count': 2
    },
    'rawE': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'rawE',
        'return_type': 'float',
        'deref_count': 2
    },
    'rawEta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'rawEta',
        'return_type': 'float',
        'deref_count': 2
    },
    'rawPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'rawPhi',
        'return_type': 'float',
        'deref_count': 2
    },
    'rawM': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'rawM',
        'return_type': 'float',
        'deref_count': 2
    },
    'altE': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'altE',
        'return_type': 'float',
        'deref_count': 2
    },
    'altEta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'altEta',
        'return_type': 'float',
        'deref_count': 2
    },
    'altPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'altPhi',
        'return_type': 'float',
        'deref_count': 2
    },
    'altM': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'altM',
        'return_type': 'float',
        'deref_count': 2
    },
    'calE': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'calE',
        'return_type': 'float',
        'deref_count': 2
    },
    'calEta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'calEta',
        'return_type': 'float',
        'deref_count': 2
    },
    'calPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'calPhi',
        'return_type': 'float',
        'deref_count': 2
    },
    'calM': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'calM',
        'return_type': 'float',
        'deref_count': 2
    },
    'setSignalState': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'setSignalState',
        'return_type': 'bool',
        'deref_count': 2
    },
    'signalState': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'signalState',
        'return_type': 'xAOD::CaloCluster_v1::State',
        'deref_count': 2
    },
    'getClusterEtaSize': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'getClusterEtaSize',
        'return_type': 'unsigned int',
        'deref_count': 2
    },
    'getClusterPhiSize': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'getClusterPhiSize',
        'return_type': 'unsigned int',
        'deref_count': 2
    },
    'badChannelList': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'badChannelList',
        'return_type_element': 'xAOD::CaloClusterBadChannelData_v1',
        'return_type_collection': 'const vector<xAOD::CaloClusterBadChannelData_v1>',
        'deref_count': 2
    },
    'getSisterCluster': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'getSisterCluster',
        'return_type': 'const xAOD::CaloCluster_v1 *',
        'deref_count': 2
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'index',
        'return_type': 'unsigned int',
        'deref_count': 2
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
        'deref_count': 2
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
        'deref_count': 2
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'hasStore',
        'return_type': 'bool',
        'deref_count': 2
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
        'deref_count': 2
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
        'deref_count': 2
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'auxdataConst',
        'return_type': 'U',
        'deref_count': 2
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'method_name': 'isAvailable',
        'return_type': 'bool',
        'deref_count': 2
    },
}

_enum_function_map = {      
}

_defined_enums = {      
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

        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODCaloEvent/versions/CaloCluster_v1.h',
            'body_includes': ["xAODCaloEvent/versions/CaloCluster_v1.h"],
        })


        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODCaloEvent',
            'link_libraries': ["xAODCaloEvent"],
        })

        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class ElementLink_DataVector_xAOD_CaloCluster_v1__:
    "A class"


    def isValid(self) -> bool:
        "A method"
        ...

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

    def et(self) -> float:
        "A method"
        ...

    def eSample(self, sampling: func_adl_servicex_xaodr21.calosampling.CaloSampling.CaloSample) -> float:
        "A method"
        ...

    def etaSample(self, sampling: func_adl_servicex_xaodr21.calosampling.CaloSampling.CaloSample) -> float:
        "A method"
        ...

    def phiSample(self, sampling: func_adl_servicex_xaodr21.calosampling.CaloSampling.CaloSample) -> float:
        "A method"
        ...

    def energy_max(self, sampling: func_adl_servicex_xaodr21.calosampling.CaloSampling.CaloSample) -> float:
        "A method"
        ...

    def etamax(self, sampling: func_adl_servicex_xaodr21.calosampling.CaloSampling.CaloSample) -> float:
        "A method"
        ...

    def phimax(self, sampling: func_adl_servicex_xaodr21.calosampling.CaloSampling.CaloSample) -> float:
        "A method"
        ...

    def etasize(self, sampling: func_adl_servicex_xaodr21.calosampling.CaloSampling.CaloSample) -> float:
        "A method"
        ...

    def phisize(self, sampling: func_adl_servicex_xaodr21.calosampling.CaloSampling.CaloSample) -> float:
        "A method"
        ...

    def energyBE(self, layer: int) -> float:
        "A method"
        ...

    def etaBE(self, layer: int) -> float:
        "A method"
        ...

    def phiBE(self, layer: int) -> float:
        "A method"
        ...

    def setEnergy(self, sampling: func_adl_servicex_xaodr21.calosampling.CaloSampling.CaloSample, e: float) -> bool:
        "A method"
        ...

    def setEta(self, sampling: func_adl_servicex_xaodr21.calosampling.CaloSampling.CaloSample, eta: float) -> bool:
        "A method"
        ...

    def setPhi(self, sampling: func_adl_servicex_xaodr21.calosampling.CaloSampling.CaloSample, phi: float) -> bool:
        "A method"
        ...

    def setEmax(self, sampling: func_adl_servicex_xaodr21.calosampling.CaloSampling.CaloSample, eMax: float) -> bool:
        "A method"
        ...

    def setEtamax(self, sampling: func_adl_servicex_xaodr21.calosampling.CaloSampling.CaloSample, etaMax: float) -> bool:
        "A method"
        ...

    def setPhimax(self, sampling: func_adl_servicex_xaodr21.calosampling.CaloSampling.CaloSample, phiMax: float) -> bool:
        "A method"
        ...

    def setEtasize(self, sampling: func_adl_servicex_xaodr21.calosampling.CaloSampling.CaloSample, etaSize: float) -> bool:
        "A method"
        ...

    def setPhisize(self, sampling: func_adl_servicex_xaodr21.calosampling.CaloSampling.CaloSample, phiSize: float) -> bool:
        "A method"
        ...

    def retrieveMoment(self, type: func_adl_servicex_xaodr21.xAOD.calocluster_v1.CaloCluster_v1.MomentType, value: float) -> bool:
        "A method"
        ...

    def getMomentValue(self, type: func_adl_servicex_xaodr21.xAOD.calocluster_v1.CaloCluster_v1.MomentType) -> float:
        "A method"
        ...

    def eta0(self) -> float:
        "A method"
        ...

    def phi0(self) -> float:
        "A method"
        ...

    def time(self) -> float:
        "A method"
        ...

    def samplingPattern(self) -> int:
        "A method"
        ...

    def nSamples(self) -> int:
        "A method"
        ...

    def hasSampling(self, s: func_adl_servicex_xaodr21.calosampling.CaloSampling.CaloSample) -> bool:
        "A method"
        ...

    def clusterSize(self) -> func_adl_servicex_xaodr21.xAOD.calocluster_v1.CaloCluster_v1.ClusterSize:
        "A method"
        ...

    def inBarrel(self) -> bool:
        "A method"
        ...

    def inEndcap(self) -> bool:
        "A method"
        ...

    def rawE(self) -> float:
        "A method"
        ...

    def rawEta(self) -> float:
        "A method"
        ...

    def rawPhi(self) -> float:
        "A method"
        ...

    def rawM(self) -> float:
        "A method"
        ...

    def altE(self) -> float:
        "A method"
        ...

    def altEta(self) -> float:
        "A method"
        ...

    def altPhi(self) -> float:
        "A method"
        ...

    def altM(self) -> float:
        "A method"
        ...

    def calE(self) -> float:
        "A method"
        ...

    def calEta(self) -> float:
        "A method"
        ...

    def calPhi(self) -> float:
        "A method"
        ...

    def calM(self) -> float:
        "A method"
        ...

    def setSignalState(self, s: func_adl_servicex_xaodr21.xAOD.calocluster_v1.CaloCluster_v1.State) -> bool:
        "A method"
        ...

    def signalState(self) -> func_adl_servicex_xaodr21.xAOD.calocluster_v1.CaloCluster_v1.State:
        "A method"
        ...

    def getClusterEtaSize(self) -> int:
        "A method"
        ...

    def getClusterPhiSize(self) -> int:
        "A method"
        ...

    def badChannelList(self) -> func_adl_servicex_xaodr21.vector_xaod_caloclusterbadchanneldata_v1_.vector_xAOD_CaloClusterBadChannelData_v1_:
        "A method"
        ...

    def getSisterCluster(self) -> func_adl_servicex_xaodr21.xAOD.calocluster_v1.CaloCluster_v1:
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
