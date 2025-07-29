from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr21

_method_map = {
}

_enum_function_map = {      
}

_defined_enums = {
    'PFOAttributes':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.PFODetails',
            'name': 'PFOAttributes',
            'values': [
                'nPi0',
                'nPi0Proto',
                'eflowRec_EM_FRAC_ENHANCED',
                'eflowRec_ENG_FRAC_CORE',
                'eflowRec_FIRST_ENG_DENS',
                'eflowRec_CENTER_LAMBDA',
                'eflowRec_SECOND_R',
                'eflowRec_DELTA_ALPHA',
                'eflowRec_HOT_STRIP_FRAC',
                'eflowRec_THREE_CELL_STRIP_FRAC',
                'eflowRec_LATERAL',
                'eflowRec_LONGITUDINAL',
                'eflowRec_SECOND_LAMBDA',
                'eflowRec_ISOLATION',
                'eflowRec_ENG_FRAC_MAX',
                'eflowRec_ENG_BAD_CELLS',
                'eflowRec_N_BAD_CELLS',
                'eflowRec_BADLARQ_FRAC',
                'eflowRec_ENG_POS',
                'eflowRec_SIGNIFICANCE',
                'eflowRec_CELL_SIGNIFICANCE',
                'eflowRec_CELL_SIG_SAMPLING',
                'eflowRec_AVG_LAR_Q',
                'eflowRec_AVG_TILE_Q',
                'eflowRec_LAYERENERGY_EM3',
                'eflowRec_LAYERENERGY_HEC0',
                'eflowRec_LAYERENERGY_Tile0',
                'eflowRec_LAYERENERGY_HEC',
                'eflowRec_TIMING',
                'eflowRec_tracksExpectedEnergyDeposit',
                'eflowRec_isInDenseEnvironment',
                'eflowRec_LAYERENERGY_EM',
                'eflowRec_LAYERENERGY_PreSamplerB',
                'eflowRec_LAYERENERGY_EMB1',
                'eflowRec_LAYERENERGY_EMB2',
                'eflowRec_LAYERENERGY_EMB3',
                'eflowRec_LAYERENERGY_PreSamplerE',
                'eflowRec_LAYERENERGY_EME1',
                'eflowRec_LAYERENERGY_EME2',
                'eflowRec_LAYERENERGY_EME3',
                'eflowRec_LAYERENERGY_HEC1',
                'eflowRec_LAYERENERGY_HEC2',
                'eflowRec_LAYERENERGY_HEC3',
                'eflowRec_LAYERENERGY_TileBar0',
                'eflowRec_LAYERENERGY_TileBar1',
                'eflowRec_LAYERENERGY_TileBar2',
                'eflowRec_LAYERENERGY_TileGap1',
                'eflowRec_LAYERENERGY_TileGap2',
                'eflowRec_LAYERENERGY_TileGap3',
                'eflowRec_LAYERENERGY_TileExt0',
                'eflowRec_LAYERENERGY_TileExt1',
                'eflowRec_LAYERENERGY_TileExt2',
                'eflowRec_LAYERENERGY_FCAL0',
                'eflowRec_LAYERENERGY_FCAL1',
                'eflowRec_LAYERENERGY_FCAL2',
                'eflowRec_LAYERENERGY_MINIFCAL0',
                'eflowRec_LAYERENERGY_MINIFCAL1',
                'eflowRec_LAYERENERGY_MINIFCAL2',
                'eflowRec_LAYERENERGY_MINIFCAL3',
                'eflowRec_EM_PROBABILITY',
                'cellBased_FIRST_ETA',
                'cellBased_SECOND_R',
                'cellBased_SECOND_LAMBDA',
                'cellBased_DELTA_PHI',
                'cellBased_DELTA_THETA',
                'cellBased_CENTER_LAMBDA',
                'cellBased_LATERAL',
                'cellBased_LONGITUDINAL',
                'cellBased_ENG_FRAC_EM',
                'cellBased_ENG_FRAC_MAX',
                'cellBased_ENG_FRAC_CORE',
                'cellBased_SECOND_ENG_DENS',
                'cellBased_EM1CoreFrac',
                'cellBased_asymmetryInEM1WRTTrk',
                'cellBased_NHitsInEM1',
                'cellBased_NPosECells_PS',
                'cellBased_NPosECells_EM1',
                'cellBased_NPosECells_EM2',
                'cellBased_firstEtaWRTClusterPosition_EM1',
                'cellBased_firstEtaWRTClusterPosition_EM2',
                'cellBased_secondEtaWRTClusterPosition_EM1',
                'cellBased_secondEtaWRTClusterPosition_EM2',
                'cellBased_energy_EM1',
                'cellBased_energy_EM2',
                'tauShots_nCellsInEta',
                'tauShots_pt1',
                'tauShots_pt3',
                'tauShots_pt5',
                'tauShots_ws5',
                'tauShots_sdevEta5_WRTmean',
                'tauShots_sdevEta5_WRTmode',
                'tauShots_sdevPt5',
                'tauShots_deltaPt12_min',
                'tauShots_Fside_3not1',
                'tauShots_Fside_5not1',
                'tauShots_Fside_5not3',
                'tauShots_fracSide_3not1',
                'tauShots_fracSide_5not1',
                'tauShots_fracSide_5not3',
                'tauShots_pt1OverPt3',
                'tauShots_pt3OverPt5',
                'tauShots_mergedScore',
                'tauShots_signalScore',
                'tauShots_nPhotons',
                'tauShots_seedHash',
            ],
        },
    'PFOParticleType':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.PFODetails',
            'name': 'PFOParticleType',
            'values': [
                'CaloCluster',
                'Track',
                'TauShot',
                'HadronicCalo',
                'ChargedPFO',
                'NeutralPFO',
                'TauTrack',
            ],
        },
    'PFOLeptonType':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.PFODetails',
            'name': 'PFOLeptonType',
            'values': [
                'PFO_electron',
                'PFO_muon',
                'PFO_tau',
                'PFO_photon',
                'PFO_nonLeptonic',
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


        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class PFODetails:
    "A class"

    class PFOAttributes(Enum):
        nPi0 = 0
        nPi0Proto = 1
        eflowRec_EM_FRAC_ENHANCED = 200
        eflowRec_ENG_FRAC_CORE = 201
        eflowRec_FIRST_ENG_DENS = 202
        eflowRec_CENTER_LAMBDA = 203
        eflowRec_SECOND_R = 204
        eflowRec_DELTA_ALPHA = 205
        eflowRec_HOT_STRIP_FRAC = 206
        eflowRec_THREE_CELL_STRIP_FRAC = 207
        eflowRec_LATERAL = 208
        eflowRec_LONGITUDINAL = 209
        eflowRec_SECOND_LAMBDA = 210
        eflowRec_ISOLATION = 211
        eflowRec_ENG_FRAC_MAX = 212
        eflowRec_ENG_BAD_CELLS = 213
        eflowRec_N_BAD_CELLS = 214
        eflowRec_BADLARQ_FRAC = 215
        eflowRec_ENG_POS = 216
        eflowRec_SIGNIFICANCE = 217
        eflowRec_CELL_SIGNIFICANCE = 218
        eflowRec_CELL_SIG_SAMPLING = 219
        eflowRec_AVG_LAR_Q = 220
        eflowRec_AVG_TILE_Q = 221
        eflowRec_LAYERENERGY_EM3 = 222
        eflowRec_LAYERENERGY_HEC0 = 223
        eflowRec_LAYERENERGY_Tile0 = 224
        eflowRec_LAYERENERGY_HEC = 225
        eflowRec_TIMING = 226
        eflowRec_tracksExpectedEnergyDeposit = 227
        eflowRec_isInDenseEnvironment = 228
        eflowRec_LAYERENERGY_EM = 229
        eflowRec_LAYERENERGY_PreSamplerB = 230
        eflowRec_LAYERENERGY_EMB1 = 231
        eflowRec_LAYERENERGY_EMB2 = 232
        eflowRec_LAYERENERGY_EMB3 = 233
        eflowRec_LAYERENERGY_PreSamplerE = 234
        eflowRec_LAYERENERGY_EME1 = 235
        eflowRec_LAYERENERGY_EME2 = 236
        eflowRec_LAYERENERGY_EME3 = 237
        eflowRec_LAYERENERGY_HEC1 = 238
        eflowRec_LAYERENERGY_HEC2 = 239
        eflowRec_LAYERENERGY_HEC3 = 240
        eflowRec_LAYERENERGY_TileBar0 = 241
        eflowRec_LAYERENERGY_TileBar1 = 242
        eflowRec_LAYERENERGY_TileBar2 = 243
        eflowRec_LAYERENERGY_TileGap1 = 244
        eflowRec_LAYERENERGY_TileGap2 = 245
        eflowRec_LAYERENERGY_TileGap3 = 246
        eflowRec_LAYERENERGY_TileExt0 = 247
        eflowRec_LAYERENERGY_TileExt1 = 248
        eflowRec_LAYERENERGY_TileExt2 = 249
        eflowRec_LAYERENERGY_FCAL0 = 250
        eflowRec_LAYERENERGY_FCAL1 = 251
        eflowRec_LAYERENERGY_FCAL2 = 252
        eflowRec_LAYERENERGY_MINIFCAL0 = 253
        eflowRec_LAYERENERGY_MINIFCAL1 = 254
        eflowRec_LAYERENERGY_MINIFCAL2 = 255
        eflowRec_LAYERENERGY_MINIFCAL3 = 256
        eflowRec_EM_PROBABILITY = 257
        cellBased_FIRST_ETA = 400
        cellBased_SECOND_R = 401
        cellBased_SECOND_LAMBDA = 402
        cellBased_DELTA_PHI = 403
        cellBased_DELTA_THETA = 404
        cellBased_CENTER_LAMBDA = 405
        cellBased_LATERAL = 406
        cellBased_LONGITUDINAL = 407
        cellBased_ENG_FRAC_EM = 408
        cellBased_ENG_FRAC_MAX = 409
        cellBased_ENG_FRAC_CORE = 410
        cellBased_SECOND_ENG_DENS = 411
        cellBased_EM1CoreFrac = 412
        cellBased_asymmetryInEM1WRTTrk = 413
        cellBased_NHitsInEM1 = 414
        cellBased_NPosECells_PS = 415
        cellBased_NPosECells_EM1 = 416
        cellBased_NPosECells_EM2 = 417
        cellBased_firstEtaWRTClusterPosition_EM1 = 418
        cellBased_firstEtaWRTClusterPosition_EM2 = 419
        cellBased_secondEtaWRTClusterPosition_EM1 = 420
        cellBased_secondEtaWRTClusterPosition_EM2 = 421
        cellBased_energy_EM1 = 422
        cellBased_energy_EM2 = 423
        tauShots_nCellsInEta = 600
        tauShots_pt1 = 601
        tauShots_pt3 = 602
        tauShots_pt5 = 603
        tauShots_ws5 = 604
        tauShots_sdevEta5_WRTmean = 605
        tauShots_sdevEta5_WRTmode = 606
        tauShots_sdevPt5 = 607
        tauShots_deltaPt12_min = 608
        tauShots_Fside_3not1 = 609
        tauShots_Fside_5not1 = 610
        tauShots_Fside_5not3 = 611
        tauShots_fracSide_3not1 = 612
        tauShots_fracSide_5not1 = 613
        tauShots_fracSide_5not3 = 614
        tauShots_pt1OverPt3 = 615
        tauShots_pt3OverPt5 = 616
        tauShots_mergedScore = 617
        tauShots_signalScore = 618
        tauShots_nPhotons = 619
        tauShots_seedHash = 620

    class PFOParticleType(Enum):
        CaloCluster = 0
        Track = 1
        TauShot = 2
        HadronicCalo = 3
        ChargedPFO = 4
        NeutralPFO = 5
        TauTrack = 6

    class PFOLeptonType(Enum):
        PFO_electron = 0
        PFO_muon = 1
        PFO_tau = 2
        PFO_photon = 3
        PFO_nonLeptonic = 4

