from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr21

_method_map = {
    'pt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Egamma_v1',
        'method_name': 'pt',
        'return_type': 'double',
    },
    'eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Egamma_v1',
        'method_name': 'eta',
        'return_type': 'double',
    },
    'phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Egamma_v1',
        'method_name': 'phi',
        'return_type': 'double',
    },
    'm': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Egamma_v1',
        'method_name': 'm',
        'return_type': 'double',
    },
    'e': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Egamma_v1',
        'method_name': 'e',
        'return_type': 'double',
    },
    'rapidity': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Egamma_v1',
        'method_name': 'rapidity',
        'return_type': 'double',
    },
    'p4': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Egamma_v1',
        'method_name': 'p4',
        'return_type': 'const TLorentzVector',
    },
    'type': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Egamma_v1',
        'method_name': 'type',
        'return_type': 'xAOD::Type::ObjectType',
    },
    'nCaloClusters': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Egamma_v1',
        'method_name': 'nCaloClusters',
        'return_type': 'unsigned int',
    },
    'caloCluster': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Egamma_v1',
        'method_name': 'caloCluster',
        'return_type': 'const xAOD::CaloCluster_v1 *',
    },
    'caloClusterLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Egamma_v1',
        'method_name': 'caloClusterLink',
        'return_type': 'const ElementLink<DataVector<xAOD::CaloCluster_v1>>',
    },
    'caloClusterLinks': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Egamma_v1',
        'method_name': 'caloClusterLinks',
        'return_type_element': 'ElementLink<DataVector<xAOD::CaloCluster_v1>>',
        'return_type_collection': 'const vector<ElementLink<DataVector<xAOD::CaloCluster_v1>>>',
    },
    'author': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Egamma_v1',
        'method_name': 'author',
        'return_type': 'uint16_t',
    },
    'ambiguousObject': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Egamma_v1',
        'method_name': 'ambiguousObject',
        'return_type': 'const xAOD::Egamma_v1 *',
    },
    'showerShapeValue': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Egamma_v1',
        'method_name': 'showerShapeValue',
        'return_type': 'bool',
    },
    'setShowerShapeValue': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Egamma_v1',
        'method_name': 'setShowerShapeValue',
        'return_type': 'bool',
    },
    'isGoodOQ': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Egamma_v1',
        'method_name': 'isGoodOQ',
        'return_type': 'bool',
    },
    'OQ': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Egamma_v1',
        'method_name': 'OQ',
        'return_type': 'unsigned int',
    },
    'isolation': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Egamma_v1',
        'method_name': 'isolation',
        'return_type': 'bool',
    },
    'setIsolation': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Egamma_v1',
        'method_name': 'setIsolation',
        'return_type': 'bool',
    },
    'isolationValue': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Egamma_v1',
        'method_name': 'isolationValue',
        'return_type': 'bool',
    },
    'setIsolationValue': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Egamma_v1',
        'method_name': 'setIsolationValue',
        'return_type': 'bool',
    },
    'isolationCaloCorrection': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Egamma_v1',
        'method_name': 'isolationCaloCorrection',
        'return_type': 'bool',
    },
    'setIsolationCaloCorrection': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Egamma_v1',
        'method_name': 'setIsolationCaloCorrection',
        'return_type': 'bool',
    },
    'isolationTrackCorrection': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Egamma_v1',
        'method_name': 'isolationTrackCorrection',
        'return_type': 'bool',
    },
    'setIsolationTrackCorrection': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Egamma_v1',
        'method_name': 'setIsolationTrackCorrection',
        'return_type': 'bool',
    },
    'setIsolationCorrectionBitset': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Egamma_v1',
        'method_name': 'setIsolationCorrectionBitset',
        'return_type': 'bool',
    },
    'passSelection': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Egamma_v1',
        'method_name': 'passSelection',
        'return_type': 'bool',
    },
    'selectionisEM': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Egamma_v1',
        'method_name': 'selectionisEM',
        'return_type': 'bool',
    },
    'likelihoodValue': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Egamma_v1',
        'method_name': 'likelihoodValue',
        'return_type': 'bool',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Egamma_v1',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Egamma_v1',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Egamma_v1',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Egamma_v1',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Egamma_v1',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Egamma_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Egamma_v1',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Egamma_v1',
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
    'showerShapeValue': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.EgammaParameters',
            'name': 'ShowerShapeType',
            'values': [
                'e011',
                'e033',
                'e132',
                'e1152',
                'ethad1',
                'ethad',
                'ehad1',
                'f1',
                'f3',
                'f1core',
                'f3core',
                'e233',
                'e235',
                'e255',
                'e237',
                'e277',
                'e333',
                'e335',
                'e337',
                'e377',
                'weta1',
                'weta2',
                'e2ts1',
                'e2tsts1',
                'fracs1',
                'widths1',
                'widths2',
                'poscs1',
                'poscs2',
                'asy1',
                'pos',
                'pos7',
                'barys1',
                'wtots1',
                'emins1',
                'emaxs1',
                'r33over37allcalo',
                'ecore',
                'Reta',
                'Rphi',
                'Eratio',
                'Rhad',
                'Rhad1',
                'DeltaE',
                'NumberOfShowerShapes',
            ],
        },
    ],
    'setShowerShapeValue': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.EgammaParameters',
            'name': 'ShowerShapeType',
            'values': [
                'e011',
                'e033',
                'e132',
                'e1152',
                'ethad1',
                'ethad',
                'ehad1',
                'f1',
                'f3',
                'f1core',
                'f3core',
                'e233',
                'e235',
                'e255',
                'e237',
                'e277',
                'e333',
                'e335',
                'e337',
                'e377',
                'weta1',
                'weta2',
                'e2ts1',
                'e2tsts1',
                'fracs1',
                'widths1',
                'widths2',
                'poscs1',
                'poscs2',
                'asy1',
                'pos',
                'pos7',
                'barys1',
                'wtots1',
                'emins1',
                'emaxs1',
                'r33over37allcalo',
                'ecore',
                'Reta',
                'Rphi',
                'Eratio',
                'Rhad',
                'Rhad1',
                'DeltaE',
                'NumberOfShowerShapes',
            ],
        },
    ],
    'isolation': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.Iso',
            'name': 'IsolationType',
            'values': [
                'etcone20',
                'etcone30',
                'etcone40',
                'ptcone20',
                'ptcone30',
                'ptcone40',
                'ptcone50',
                'topoetcone20',
                'topoetcone30',
                'topoetcone40',
                'ptvarcone20',
                'ptvarcone30',
                'ptvarcone40',
                'neflowisol20',
                'neflowisol30',
                'neflowisol40',
                'ptvarcone20_TightTTVA_pt500',
                'ptvarcone30_TightTTVA_pt500',
                'ptvarcone40_TightTTVA_pt500',
                'ptvarcone20_TightTTVA_pt1000',
                'ptvarcone30_TightTTVA_pt1000',
                'ptvarcone40_TightTTVA_pt1000',
                'ptcone20_TightTTVA_pt500',
                'ptcone30_TightTTVA_pt500',
                'ptcone40_TightTTVA_pt500',
                'ptcone20_TightTTVA_pt1000',
                'ptcone30_TightTTVA_pt1000',
                'ptcone40_TightTTVA_pt1000',
                'ptvarcone20_TightTTVALooseCone_pt500',
                'ptvarcone30_TightTTVALooseCone_pt500',
                'ptvarcone40_TightTTVALooseCone_pt500',
                'ptvarcone20_TightTTVALooseCone_pt1000',
                'ptvarcone30_TightTTVALooseCone_pt1000',
                'ptvarcone40_TightTTVALooseCone_pt1000',
                'ptcone20_TightTTVALooseCone_pt500',
                'ptcone30_TightTTVALooseCone_pt500',
                'ptcone40_TightTTVALooseCone_pt500',
                'ptcone20_TightTTVALooseCone_pt1000',
                'ptcone30_TightTTVALooseCone_pt1000',
                'ptcone40_TightTTVALooseCone_pt1000',
                'numIsolationTypes',
            ],
        },
    ],
    'setIsolation': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.Iso',
            'name': 'IsolationType',
            'values': [
                'etcone20',
                'etcone30',
                'etcone40',
                'ptcone20',
                'ptcone30',
                'ptcone40',
                'ptcone50',
                'topoetcone20',
                'topoetcone30',
                'topoetcone40',
                'ptvarcone20',
                'ptvarcone30',
                'ptvarcone40',
                'neflowisol20',
                'neflowisol30',
                'neflowisol40',
                'ptvarcone20_TightTTVA_pt500',
                'ptvarcone30_TightTTVA_pt500',
                'ptvarcone40_TightTTVA_pt500',
                'ptvarcone20_TightTTVA_pt1000',
                'ptvarcone30_TightTTVA_pt1000',
                'ptvarcone40_TightTTVA_pt1000',
                'ptcone20_TightTTVA_pt500',
                'ptcone30_TightTTVA_pt500',
                'ptcone40_TightTTVA_pt500',
                'ptcone20_TightTTVA_pt1000',
                'ptcone30_TightTTVA_pt1000',
                'ptcone40_TightTTVA_pt1000',
                'ptvarcone20_TightTTVALooseCone_pt500',
                'ptvarcone30_TightTTVALooseCone_pt500',
                'ptvarcone40_TightTTVALooseCone_pt500',
                'ptvarcone20_TightTTVALooseCone_pt1000',
                'ptvarcone30_TightTTVALooseCone_pt1000',
                'ptvarcone40_TightTTVALooseCone_pt1000',
                'ptcone20_TightTTVALooseCone_pt500',
                'ptcone30_TightTTVALooseCone_pt500',
                'ptcone40_TightTTVALooseCone_pt500',
                'ptcone20_TightTTVALooseCone_pt1000',
                'ptcone30_TightTTVALooseCone_pt1000',
                'ptcone40_TightTTVALooseCone_pt1000',
                'numIsolationTypes',
            ],
        },
    ],
    'isolationValue': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.Iso',
            'name': 'IsolationType',
            'values': [
                'etcone20',
                'etcone30',
                'etcone40',
                'ptcone20',
                'ptcone30',
                'ptcone40',
                'ptcone50',
                'topoetcone20',
                'topoetcone30',
                'topoetcone40',
                'ptvarcone20',
                'ptvarcone30',
                'ptvarcone40',
                'neflowisol20',
                'neflowisol30',
                'neflowisol40',
                'ptvarcone20_TightTTVA_pt500',
                'ptvarcone30_TightTTVA_pt500',
                'ptvarcone40_TightTTVA_pt500',
                'ptvarcone20_TightTTVA_pt1000',
                'ptvarcone30_TightTTVA_pt1000',
                'ptvarcone40_TightTTVA_pt1000',
                'ptcone20_TightTTVA_pt500',
                'ptcone30_TightTTVA_pt500',
                'ptcone40_TightTTVA_pt500',
                'ptcone20_TightTTVA_pt1000',
                'ptcone30_TightTTVA_pt1000',
                'ptcone40_TightTTVA_pt1000',
                'ptvarcone20_TightTTVALooseCone_pt500',
                'ptvarcone30_TightTTVALooseCone_pt500',
                'ptvarcone40_TightTTVALooseCone_pt500',
                'ptvarcone20_TightTTVALooseCone_pt1000',
                'ptvarcone30_TightTTVALooseCone_pt1000',
                'ptvarcone40_TightTTVALooseCone_pt1000',
                'ptcone20_TightTTVALooseCone_pt500',
                'ptcone30_TightTTVALooseCone_pt500',
                'ptcone40_TightTTVALooseCone_pt500',
                'ptcone20_TightTTVALooseCone_pt1000',
                'ptcone30_TightTTVALooseCone_pt1000',
                'ptcone40_TightTTVALooseCone_pt1000',
                'numIsolationTypes',
            ],
        },
    ],
    'setIsolationValue': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.Iso',
            'name': 'IsolationType',
            'values': [
                'etcone20',
                'etcone30',
                'etcone40',
                'ptcone20',
                'ptcone30',
                'ptcone40',
                'ptcone50',
                'topoetcone20',
                'topoetcone30',
                'topoetcone40',
                'ptvarcone20',
                'ptvarcone30',
                'ptvarcone40',
                'neflowisol20',
                'neflowisol30',
                'neflowisol40',
                'ptvarcone20_TightTTVA_pt500',
                'ptvarcone30_TightTTVA_pt500',
                'ptvarcone40_TightTTVA_pt500',
                'ptvarcone20_TightTTVA_pt1000',
                'ptvarcone30_TightTTVA_pt1000',
                'ptvarcone40_TightTTVA_pt1000',
                'ptcone20_TightTTVA_pt500',
                'ptcone30_TightTTVA_pt500',
                'ptcone40_TightTTVA_pt500',
                'ptcone20_TightTTVA_pt1000',
                'ptcone30_TightTTVA_pt1000',
                'ptcone40_TightTTVA_pt1000',
                'ptvarcone20_TightTTVALooseCone_pt500',
                'ptvarcone30_TightTTVALooseCone_pt500',
                'ptvarcone40_TightTTVALooseCone_pt500',
                'ptvarcone20_TightTTVALooseCone_pt1000',
                'ptvarcone30_TightTTVALooseCone_pt1000',
                'ptvarcone40_TightTTVALooseCone_pt1000',
                'ptcone20_TightTTVALooseCone_pt500',
                'ptcone30_TightTTVALooseCone_pt500',
                'ptcone40_TightTTVALooseCone_pt500',
                'ptcone20_TightTTVALooseCone_pt1000',
                'ptcone30_TightTTVALooseCone_pt1000',
                'ptcone40_TightTTVALooseCone_pt1000',
                'numIsolationTypes',
            ],
        },
    ],
    'isolationCaloCorrection': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.Iso',
            'name': 'IsolationFlavour',
            'values': [
                'etcone',
                'ptcone',
                'topoetcone',
                'ptvarcone',
                'neflowisol',
                'ptvarcone_TightTTVA_pt500',
                'ptvarcone_TightTTVA_pt1000',
                'ptcone_TightTTVA_pt500',
                'ptcone_TightTTVA_pt1000',
                'ptvarcone_TightTTVALooseCone_pt500',
                'ptvarcone_TightTTVALooseCone_pt1000',
                'ptcone_TightTTVALooseCone_pt500',
                'ptcone_TightTTVALooseCone_pt1000',
                'numIsolationFlavours',
            ],
        },
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.Iso',
            'name': 'IsolationCaloCorrection',
            'values': [
                'noneCaloCorrection',
                'coreMuon',
                'core57cells',
                'coreCone',
                'ptCorrection',
                'pileupCorrection',
                'coreConeSC',
                'numIsolationCaloCorrections',
            ],
        },
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.Iso',
            'name': 'IsolationCorrectionParameter',
            'values': [
                'coreEnergy',
                'coreArea',
                'NumCorrParameters',
            ],
        },
    ],
    'setIsolationCaloCorrection': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.Iso',
            'name': 'IsolationFlavour',
            'values': [
                'etcone',
                'ptcone',
                'topoetcone',
                'ptvarcone',
                'neflowisol',
                'ptvarcone_TightTTVA_pt500',
                'ptvarcone_TightTTVA_pt1000',
                'ptcone_TightTTVA_pt500',
                'ptcone_TightTTVA_pt1000',
                'ptvarcone_TightTTVALooseCone_pt500',
                'ptvarcone_TightTTVALooseCone_pt1000',
                'ptcone_TightTTVALooseCone_pt500',
                'ptcone_TightTTVALooseCone_pt1000',
                'numIsolationFlavours',
            ],
        },
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.Iso',
            'name': 'IsolationCaloCorrection',
            'values': [
                'noneCaloCorrection',
                'coreMuon',
                'core57cells',
                'coreCone',
                'ptCorrection',
                'pileupCorrection',
                'coreConeSC',
                'numIsolationCaloCorrections',
            ],
        },
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.Iso',
            'name': 'IsolationCorrectionParameter',
            'values': [
                'coreEnergy',
                'coreArea',
                'NumCorrParameters',
            ],
        },
    ],
    'isolationTrackCorrection': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.Iso',
            'name': 'IsolationFlavour',
            'values': [
                'etcone',
                'ptcone',
                'topoetcone',
                'ptvarcone',
                'neflowisol',
                'ptvarcone_TightTTVA_pt500',
                'ptvarcone_TightTTVA_pt1000',
                'ptcone_TightTTVA_pt500',
                'ptcone_TightTTVA_pt1000',
                'ptvarcone_TightTTVALooseCone_pt500',
                'ptvarcone_TightTTVALooseCone_pt1000',
                'ptcone_TightTTVALooseCone_pt500',
                'ptcone_TightTTVALooseCone_pt1000',
                'numIsolationFlavours',
            ],
        },
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.Iso',
            'name': 'IsolationTrackCorrection',
            'values': [
                'noneTrackCorrection',
                'coreTrackPtr',
                'coreTrackCone',
                'coreTrackPt',
                'numIsolationTrackCorrections',
            ],
        },
    ],
    'setIsolationTrackCorrection': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.Iso',
            'name': 'IsolationFlavour',
            'values': [
                'etcone',
                'ptcone',
                'topoetcone',
                'ptvarcone',
                'neflowisol',
                'ptvarcone_TightTTVA_pt500',
                'ptvarcone_TightTTVA_pt1000',
                'ptcone_TightTTVA_pt500',
                'ptcone_TightTTVA_pt1000',
                'ptvarcone_TightTTVALooseCone_pt500',
                'ptvarcone_TightTTVALooseCone_pt1000',
                'ptcone_TightTTVALooseCone_pt500',
                'ptcone_TightTTVALooseCone_pt1000',
                'numIsolationFlavours',
            ],
        },
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.Iso',
            'name': 'IsolationTrackCorrection',
            'values': [
                'noneTrackCorrection',
                'coreTrackPtr',
                'coreTrackCone',
                'coreTrackPt',
                'numIsolationTrackCorrections',
            ],
        },
    ],
    'setIsolationCorrectionBitset': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.Iso',
            'name': 'IsolationFlavour',
            'values': [
                'etcone',
                'ptcone',
                'topoetcone',
                'ptvarcone',
                'neflowisol',
                'ptvarcone_TightTTVA_pt500',
                'ptvarcone_TightTTVA_pt1000',
                'ptcone_TightTTVA_pt500',
                'ptcone_TightTTVA_pt1000',
                'ptvarcone_TightTTVALooseCone_pt500',
                'ptvarcone_TightTTVALooseCone_pt1000',
                'ptcone_TightTTVALooseCone_pt500',
                'ptcone_TightTTVALooseCone_pt1000',
                'numIsolationFlavours',
            ],
        },
    ],
    'passSelection': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.EgammaParameters',
            'name': 'SelectionMenu',
            'values': [
                'Loose',
                'Medium',
                'Tight',
                'LHLoose',
                'LHMedium',
                'LHTight',
                'MultiLepton',
                'NumberOfMenus',
            ],
        },
    ],
    'selectionisEM': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.EgammaParameters',
            'name': 'SelectionisEM',
            'values': [
                'isEMLoose',
                'isEMMedium',
                'isEMTight',
                'isEMLHLoose',
                'isEMLHMedium',
                'isEMLHTight',
                'isEMMultiLepton',
                'NumberOfisEMs',
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
            'name': 'xAODEgamma/versions/Egamma_v1.h',
            'body_includes': ["xAODEgamma/versions/Egamma_v1.h"],
        })


        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODEgamma',
            'link_libraries': ["xAODEgamma"],
        })

        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class Egamma_v1:
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

    def nCaloClusters(self) -> int:
        "A method"
        ...

    def caloCluster(self, index: int) -> func_adl_servicex_xaodr21.xAOD.calocluster_v1.CaloCluster_v1:
        "A method"
        ...

    def caloClusterLink(self, index: int) -> func_adl_servicex_xaodr21.elementlink_datavector_xaod_calocluster_v1__.ElementLink_DataVector_xAOD_CaloCluster_v1__:
        "A method"
        ...

    def caloClusterLinks(self) -> func_adl_servicex_xaodr21.vector_elementlink_datavector_xaod_calocluster_v1___.vector_ElementLink_DataVector_xAOD_CaloCluster_v1___:
        "A method"
        ...

    def author(self, bitmask: int) -> int:
        "A method"
        ...

    def ambiguousObject(self) -> func_adl_servicex_xaodr21.xAOD.egamma_v1.Egamma_v1:
        "A method"
        ...

    def showerShapeValue(self, value: float, information: func_adl_servicex_xaodr21.xAOD.egammaparameters.EgammaParameters.ShowerShapeType) -> bool:
        "A method"
        ...

    def setShowerShapeValue(self, value: float, information: func_adl_servicex_xaodr21.xAOD.egammaparameters.EgammaParameters.ShowerShapeType) -> bool:
        "A method"
        ...

    def isGoodOQ(self, mask: int) -> bool:
        "A method"
        ...

    def OQ(self) -> int:
        "A method"
        ...

    def isolation(self, value: float, information: func_adl_servicex_xaodr21.xAOD.iso.Iso.IsolationType) -> bool:
        "A method"
        ...

    def setIsolation(self, value: float, information: func_adl_servicex_xaodr21.xAOD.iso.Iso.IsolationType) -> bool:
        "A method"
        ...

    def isolationValue(self, value: float, information: func_adl_servicex_xaodr21.xAOD.iso.Iso.IsolationType) -> bool:
        "A method"
        ...

    def setIsolationValue(self, value: float, information: func_adl_servicex_xaodr21.xAOD.iso.Iso.IsolationType) -> bool:
        "A method"
        ...

    def isolationCaloCorrection(self, value: float, flavour: func_adl_servicex_xaodr21.xAOD.iso.Iso.IsolationFlavour, corr: func_adl_servicex_xaodr21.xAOD.iso.Iso.IsolationCaloCorrection, param: func_adl_servicex_xaodr21.xAOD.iso.Iso.IsolationCorrectionParameter) -> bool:
        "A method"
        ...

    def setIsolationCaloCorrection(self, value: float, flavour: func_adl_servicex_xaodr21.xAOD.iso.Iso.IsolationFlavour, corr: func_adl_servicex_xaodr21.xAOD.iso.Iso.IsolationCaloCorrection, param: func_adl_servicex_xaodr21.xAOD.iso.Iso.IsolationCorrectionParameter) -> bool:
        "A method"
        ...

    def isolationTrackCorrection(self, value: float, flavour: func_adl_servicex_xaodr21.xAOD.iso.Iso.IsolationFlavour, corr: func_adl_servicex_xaodr21.xAOD.iso.Iso.IsolationTrackCorrection) -> bool:
        "A method"
        ...

    def setIsolationTrackCorrection(self, value: float, flavour: func_adl_servicex_xaodr21.xAOD.iso.Iso.IsolationFlavour, corr: func_adl_servicex_xaodr21.xAOD.iso.Iso.IsolationTrackCorrection) -> bool:
        "A method"
        ...

    def setIsolationCorrectionBitset(self, value: int, flavour: func_adl_servicex_xaodr21.xAOD.iso.Iso.IsolationFlavour) -> bool:
        "A method"
        ...

    def passSelection(self, value: bool, menu: func_adl_servicex_xaodr21.xAOD.egammaparameters.EgammaParameters.SelectionMenu) -> bool:
        "A method"
        ...

    def selectionisEM(self, value: int, isEM: func_adl_servicex_xaodr21.xAOD.egammaparameters.EgammaParameters.SelectionisEM) -> bool:
        "A method"
        ...

    def likelihoodValue(self, value: float, LHValue: str) -> bool:
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
