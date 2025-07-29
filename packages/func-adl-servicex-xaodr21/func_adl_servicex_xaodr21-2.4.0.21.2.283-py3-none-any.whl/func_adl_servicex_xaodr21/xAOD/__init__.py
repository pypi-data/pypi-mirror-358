from typing import Any, TYPE_CHECKING


class _load_me:
    """Python's type resolution system demands that types be already loaded
    when they are resolved by the type hinting system. Unfortunately,
    for us to do that for classes with circular references, this fails. In order
    to have everything loaded, we would be triggering the circular references
    during the import process.

    This loader gets around that by delay-loading the files that contain the
    classes, but also tapping into anyone that wants to load the classes.
    """

    def __init__(self, name: str):
        self._name = name
        self._loaded = None

    def __getattr__(self, __name: str) -> Any:
        if self._loaded is None:
            import importlib

            self._loaded = importlib.import_module(self._name)
        return getattr(self._loaded, __name)


# Class loads. We do this to both enable type checking and also
# get around potential circular references in the C++ data model.
if not TYPE_CHECKING:
    auxcontainerbase = _load_me("func_adl_servicex_xaodr21.xAOD.auxcontainerbase")
    btagvertexauxcontainer_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.btagvertexauxcontainer_v1")
    btagvertex_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.btagvertex_v1")
    btaggingauxcontainer_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.btaggingauxcontainer_v1")
    btaggingtrigauxcontainer_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.btaggingtrigauxcontainer_v1")
    btagging_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.btagging_v1")
    caloclusterauxcontainer_v2 = _load_me("func_adl_servicex_xaodr21.xAOD.caloclusterauxcontainer_v2")
    caloclusterbadchanneldata_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.caloclusterbadchanneldata_v1")
    calocluster_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.calocluster_v1")
    calotowerauxcontainer_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.calotowerauxcontainer_v1")
    calotowercontainer_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.calotowercontainer_v1")
    calotower_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.calotower_v1")
    ditaujetauxcontainer_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.ditaujetauxcontainer_v1")
    ditaujetparameters = _load_me("func_adl_servicex_xaodr21.xAOD.ditaujetparameters")
    ditaujet_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.ditaujet_v1")
    egammaauxcontainer_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.egammaauxcontainer_v1")
    egammaparameters = _load_me("func_adl_servicex_xaodr21.xAOD.egammaparameters")
    egamma_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.egamma_v1")
    electronauxcontainer_v3 = _load_me("func_adl_servicex_xaodr21.xAOD.electronauxcontainer_v3")
    electron_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.electron_v1")
    eventinfoauxcontainer_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.eventinfoauxcontainer_v1")
    eventinfo_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.eventinfo_v1")
    iparticle = _load_me("func_adl_servicex_xaodr21.xAOD.iparticle")
    iso = _load_me("func_adl_servicex_xaodr21.xAOD.iso")
    jetalgorithmtype = _load_me("func_adl_servicex_xaodr21.xAOD.jetalgorithmtype")
    jetauxcontainer_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.jetauxcontainer_v1")
    jetconstituent = _load_me("func_adl_servicex_xaodr21.xAOD.jetconstituent")
    jetconstituentvector = _load_me("func_adl_servicex_xaodr21.xAOD.jetconstituentvector")
    jetinput = _load_me("func_adl_servicex_xaodr21.xAOD.jetinput")
    jet_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.jet_v1")
    missingetauxcontainer_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.missingetauxcontainer_v1")
    missingetcontainer_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.missingetcontainer_v1")
    missinget_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.missinget_v1")
    muonauxcontainer_v4 = _load_me("func_adl_servicex_xaodr21.xAOD.muonauxcontainer_v4")
    muonsegmentauxcontainer_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.muonsegmentauxcontainer_v1")
    muonsegment_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.muonsegment_v1")
    muon_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.muon_v1")
    neutralparticleauxcontainer_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.neutralparticleauxcontainer_v1")
    neutralparticle_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.neutralparticle_v1")
    pfoauxcontainer_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.pfoauxcontainer_v1")
    pfodetails = _load_me("func_adl_servicex_xaodr21.xAOD.pfodetails")
    pfo_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.pfo_v1")
    photonauxcontainer_v3 = _load_me("func_adl_servicex_xaodr21.xAOD.photonauxcontainer_v3")
    photon_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.photon_v1")
    sctrawhitvalidationauxcontainer_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.sctrawhitvalidationauxcontainer_v1")
    sctrawhitvalidation_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.sctrawhitvalidation_v1")
    shallowauxcontainer = _load_me("func_adl_servicex_xaodr21.xAOD.shallowauxcontainer")
    slowmuonauxcontainer_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.slowmuonauxcontainer_v1")
    slowmuon_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.slowmuon_v1")
    taujetauxcontainer_v3 = _load_me("func_adl_servicex_xaodr21.xAOD.taujetauxcontainer_v3")
    taujetparameters = _load_me("func_adl_servicex_xaodr21.xAOD.taujetparameters")
    taujet_v3 = _load_me("func_adl_servicex_xaodr21.xAOD.taujet_v3")
    tautrackauxcontainer_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.tautrackauxcontainer_v1")
    tautrack_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.tautrack_v1")
    trackcaloclusterauxcontainer_v2 = _load_me("func_adl_servicex_xaodr21.xAOD.trackcaloclusterauxcontainer_v2")
    trackcalocluster_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.trackcalocluster_v1")
    trackmeasurementvalidation_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.trackmeasurementvalidation_v1")
    trackparticleauxcontainer_v3 = _load_me("func_adl_servicex_xaodr21.xAOD.trackparticleauxcontainer_v3")
    trackparticle_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.trackparticle_v1")
    trackstatevalidationauxcontainer_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.trackstatevalidationauxcontainer_v1")
    trackstatevalidation_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.trackstatevalidation_v1")
    trutheventauxcontainer_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.trutheventauxcontainer_v1")
    trutheventbase_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.trutheventbase_v1")
    truthevent_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.truthevent_v1")
    truthmetadataauxcontainer_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.truthmetadataauxcontainer_v1")
    truthmetadata_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.truthmetadata_v1")
    truthparticleauxcontainer_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.truthparticleauxcontainer_v1")
    truthparticle_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.truthparticle_v1")
    truthpileupevent_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.truthpileupevent_v1")
    truthvertexauxcontainer_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.truthvertexauxcontainer_v1")
    truthvertex_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.truthvertex_v1")
    type = _load_me("func_adl_servicex_xaodr21.xAOD.type")
    vertexauxcontainer_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.vertexauxcontainer_v1")
    vertex_v1 = _load_me("func_adl_servicex_xaodr21.xAOD.vertex_v1")
    vxtype = _load_me("func_adl_servicex_xaodr21.xAOD.vxtype")
else:
    from . import auxcontainerbase
    from . import btagvertexauxcontainer_v1
    from . import btagvertex_v1
    from . import btaggingauxcontainer_v1
    from . import btaggingtrigauxcontainer_v1
    from . import btagging_v1
    from . import caloclusterauxcontainer_v2
    from . import caloclusterbadchanneldata_v1
    from . import calocluster_v1
    from . import calotowerauxcontainer_v1
    from . import calotowercontainer_v1
    from . import calotower_v1
    from . import ditaujetauxcontainer_v1
    from . import ditaujetparameters
    from . import ditaujet_v1
    from . import egammaauxcontainer_v1
    from . import egammaparameters
    from . import egamma_v1
    from . import electronauxcontainer_v3
    from . import electron_v1
    from . import eventinfoauxcontainer_v1
    from . import eventinfo_v1
    from . import iparticle
    from . import iso
    from . import jetalgorithmtype
    from . import jetauxcontainer_v1
    from . import jetconstituent
    from . import jetconstituentvector
    from . import jetinput
    from . import jet_v1
    from . import missingetauxcontainer_v1
    from . import missingetcontainer_v1
    from . import missinget_v1
    from . import muonauxcontainer_v4
    from . import muonsegmentauxcontainer_v1
    from . import muonsegment_v1
    from . import muon_v1
    from . import neutralparticleauxcontainer_v1
    from . import neutralparticle_v1
    from . import pfoauxcontainer_v1
    from . import pfodetails
    from . import pfo_v1
    from . import photonauxcontainer_v3
    from . import photon_v1
    from . import sctrawhitvalidationauxcontainer_v1
    from . import sctrawhitvalidation_v1
    from . import shallowauxcontainer
    from . import slowmuonauxcontainer_v1
    from . import slowmuon_v1
    from . import taujetauxcontainer_v3
    from . import taujetparameters
    from . import taujet_v3
    from . import tautrackauxcontainer_v1
    from . import tautrack_v1
    from . import trackcaloclusterauxcontainer_v2
    from . import trackcalocluster_v1
    from . import trackmeasurementvalidation_v1
    from . import trackparticleauxcontainer_v3
    from . import trackparticle_v1
    from . import trackstatevalidationauxcontainer_v1
    from . import trackstatevalidation_v1
    from . import trutheventauxcontainer_v1
    from . import trutheventbase_v1
    from . import truthevent_v1
    from . import truthmetadataauxcontainer_v1
    from . import truthmetadata_v1
    from . import truthparticleauxcontainer_v1
    from . import truthparticle_v1
    from . import truthpileupevent_v1
    from . import truthvertexauxcontainer_v1
    from . import truthvertex_v1
    from . import type
    from . import vertexauxcontainer_v1
    from . import vertex_v1
    from . import vxtype

# Include sub-namespace items
from . import TruthParticle_v1
from . import EventInfo_v1
from . import TruthEvent_v1
from . import JetConstituentVector
