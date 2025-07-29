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
    afpdataauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.afpdataauxcontainer_v1")
    afpdata_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.afpdata_v1")
    afpprotonauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.afpprotonauxcontainer_v1")
    afpproton_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.afpproton_v1")
    afpsihitauxcontainer_v2 = _load_me("func_adl_servicex_xaodr22.xAOD.afpsihitauxcontainer_v2")
    afpsihit_v2 = _load_me("func_adl_servicex_xaodr22.xAOD.afpsihit_v2")
    afpsihitsclusterauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.afpsihitsclusterauxcontainer_v1")
    afpsihitscluster_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.afpsihitscluster_v1")
    afptofhitauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.afptofhitauxcontainer_v1")
    afptofhit_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.afptofhit_v1")
    afptoftrackauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.afptoftrackauxcontainer_v1")
    afptoftrack_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.afptoftrack_v1")
    afptrackauxcontainer_v2 = _load_me("func_adl_servicex_xaodr22.xAOD.afptrackauxcontainer_v2")
    afptrack_v2 = _load_me("func_adl_servicex_xaodr22.xAOD.afptrack_v2")
    afpvertexauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.afpvertexauxcontainer_v1")
    afpvertex_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.afpvertex_v1")
    alfadataauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.alfadataauxcontainer_v1")
    alfadata_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.alfadata_v1")
    auxcontainerbase = _load_me("func_adl_servicex_xaodr22.xAOD.auxcontainerbase")
    bcmrawdataauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.bcmrawdataauxcontainer_v1")
    bcmrawdata_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.bcmrawdata_v1")
    btagvertexauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.btagvertexauxcontainer_v1")
    btagvertex_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.btagvertex_v1")
    btaggingauxcontainer_v2 = _load_me("func_adl_servicex_xaodr22.xAOD.btaggingauxcontainer_v2")
    btaggingtrigauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.btaggingtrigauxcontainer_v1")
    btagging_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.btagging_v1")
    bunchconfauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.bunchconfauxcontainer_v1")
    bunchconf_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.bunchconf_v1")
    cmmcphitsauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.cmmcphitsauxcontainer_v1")
    cmmcphits_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.cmmcphits_v1")
    cmmetsumsauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.cmmetsumsauxcontainer_v1")
    cmmetsums_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.cmmetsums_v1")
    cmmjethitsauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.cmmjethitsauxcontainer_v1")
    cmmjethits_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.cmmjethits_v1")
    cmxcphitsauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.cmxcphitsauxcontainer_v1")
    cmxcphits_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.cmxcphits_v1")
    cmxcptobauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.cmxcptobauxcontainer_v1")
    cmxcptob_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.cmxcptob_v1")
    cmxetsumsauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.cmxetsumsauxcontainer_v1")
    cmxetsums_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.cmxetsums_v1")
    cmxjethitsauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.cmxjethitsauxcontainer_v1")
    cmxjethits_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.cmxjethits_v1")
    cmxjettobauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.cmxjettobauxcontainer_v1")
    cmxjettob_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.cmxjettob_v1")
    cmxroiauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.cmxroiauxcontainer_v1")
    cmxroi_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.cmxroi_v1")
    cpmhitsauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.cpmhitsauxcontainer_v1")
    cpmhits_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.cpmhits_v1")
    cpmroiauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.cpmroiauxcontainer_v1")
    cpmroi_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.cpmroi_v1")
    cpmtobroiauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.cpmtobroiauxcontainer_v1")
    cpmtobroi_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.cpmtobroi_v1")
    cpmtowerauxcontainer_v2 = _load_me("func_adl_servicex_xaodr22.xAOD.cpmtowerauxcontainer_v2")
    cpmtower_v2 = _load_me("func_adl_servicex_xaodr22.xAOD.cpmtower_v2")
    caloclusterauxcontainer_v2 = _load_me("func_adl_servicex_xaodr22.xAOD.caloclusterauxcontainer_v2")
    caloclusterbadchanneldata_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.caloclusterbadchanneldata_v1")
    caloclustertrigauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.caloclustertrigauxcontainer_v1")
    calocluster_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.calocluster_v1")
    caloringsauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.caloringsauxcontainer_v1")
    calorings_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.calorings_v1")
    calotowerauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.calotowerauxcontainer_v1")
    calotowercontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.calotowercontainer_v1")
    calotower_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.calotower_v1")
    calovertexedclusterbase = _load_me("func_adl_servicex_xaodr22.xAOD.calovertexedclusterbase")
    calovertexedtopocluster = _load_me("func_adl_servicex_xaodr22.xAOD.calovertexedtopocluster")
    compositeparticleauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.compositeparticleauxcontainer_v1")
    compositeparticle_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.compositeparticle_v1")
    cutbookkeeperauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.cutbookkeeperauxcontainer_v1")
    cutbookkeepercontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.cutbookkeepercontainer_v1")
    cutbookkeeper_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.cutbookkeeper_v1")
    ditaujetauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.ditaujetauxcontainer_v1")
    ditaujetparameters = _load_me("func_adl_servicex_xaodr22.xAOD.ditaujetparameters")
    ditaujet_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.ditaujet_v1")
    egammaauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.egammaauxcontainer_v1")
    egammaparameters = _load_me("func_adl_servicex_xaodr22.xAOD.egammaparameters")
    egamma_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.egamma_v1")
    electronauxcontainer_v3 = _load_me("func_adl_servicex_xaodr22.xAOD.electronauxcontainer_v3")
    electrontrigauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.electrontrigauxcontainer_v1")
    electron_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.electron_v1")
    emtauroiauxcontainer_v2 = _load_me("func_adl_servicex_xaodr22.xAOD.emtauroiauxcontainer_v2")
    emtauroi_v2 = _load_me("func_adl_servicex_xaodr22.xAOD.emtauroi_v2")
    eventformatelement = _load_me("func_adl_servicex_xaodr22.xAOD.eventformatelement")
    eventformat_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.eventformat_v1")
    eventinfo_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.eventinfo_v1")
    forwardeventinfoauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.forwardeventinfoauxcontainer_v1")
    forwardeventinfo_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.forwardeventinfo_v1")
    gblockauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.gblockauxcontainer_v1")
    hieventshapeauxcontainer_v2 = _load_me("func_adl_servicex_xaodr22.xAOD.hieventshapeauxcontainer_v2")
    hieventshape_v2 = _load_me("func_adl_servicex_xaodr22.xAOD.hieventshape_v2")
    iparticle = _load_me("func_adl_servicex_xaodr22.xAOD.iparticle")
    iso = _load_me("func_adl_servicex_xaodr22.xAOD.iso")
    jemetsumsauxcontainer_v2 = _load_me("func_adl_servicex_xaodr22.xAOD.jemetsumsauxcontainer_v2")
    jemetsums_v2 = _load_me("func_adl_servicex_xaodr22.xAOD.jemetsums_v2")
    jemhitsauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.jemhitsauxcontainer_v1")
    jemhits_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.jemhits_v1")
    jemroiauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.jemroiauxcontainer_v1")
    jemroi_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.jemroi_v1")
    jemtobroiauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.jemtobroiauxcontainer_v1")
    jemtobroi_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.jemtobroi_v1")
    jgtowerauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.jgtowerauxcontainer_v1")
    jgtower_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.jgtower_v1")
    jetalgorithmtype = _load_me("func_adl_servicex_xaodr22.xAOD.jetalgorithmtype")
    jetauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.jetauxcontainer_v1")
    jetconstituent = _load_me("func_adl_servicex_xaodr22.xAOD.jetconstituent")
    jetconstituentvector = _load_me("func_adl_servicex_xaodr22.xAOD.jetconstituentvector")
    jetelementauxcontainer_v2 = _load_me("func_adl_servicex_xaodr22.xAOD.jetelementauxcontainer_v2")
    jetelement_v2 = _load_me("func_adl_servicex_xaodr22.xAOD.jetelement_v2")
    jetinput = _load_me("func_adl_servicex_xaodr22.xAOD.jetinput")
    jetroiauxcontainer_v2 = _load_me("func_adl_servicex_xaodr22.xAOD.jetroiauxcontainer_v2")
    jetroi_v2 = _load_me("func_adl_servicex_xaodr22.xAOD.jetroi_v2")
    jet_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.jet_v1")
    klfitterresult = _load_me("func_adl_servicex_xaodr22.xAOD.klfitterresult")
    klfitterresultauxcontainer = _load_me("func_adl_servicex_xaodr22.xAOD.klfitterresultauxcontainer")
    l1toporawdataauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.l1toporawdataauxcontainer_v1")
    l1toporawdata_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.l1toporawdata_v1")
    l1toposimresultsauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.l1toposimresultsauxcontainer_v1")
    l1toposimresults_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.l1toposimresults_v1")
    l2combinedmuonauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.l2combinedmuonauxcontainer_v1")
    l2combinedmuon_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.l2combinedmuon_v1")
    l2isomuonauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.l2isomuonauxcontainer_v1")
    l2isomuon_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.l2isomuon_v1")
    l2standalonemuonauxcontainer_v2 = _load_me("func_adl_servicex_xaodr22.xAOD.l2standalonemuonauxcontainer_v2")
    l2standalonemuon_v2 = _load_me("func_adl_servicex_xaodr22.xAOD.l2standalonemuon_v2")
    lumiblockrangeauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.lumiblockrangeauxcontainer_v1")
    lumiblockrange_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.lumiblockrange_v1")
    mbtsmoduleauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.mbtsmoduleauxcontainer_v1")
    mbtsmodule_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.mbtsmodule_v1")
    missingetauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.missingetauxcontainer_v1")
    missingetcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.missingetcontainer_v1")
    missinget_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.missinget_v1")
    muonauxcontainer_v5 = _load_me("func_adl_servicex_xaodr22.xAOD.muonauxcontainer_v5")
    muonroiauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.muonroiauxcontainer_v1")
    muonroi_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.muonroi_v1")
    muonsegmentauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.muonsegmentauxcontainer_v1")
    muonsegment_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.muonsegment_v1")
    muon_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.muon_v1")
    neutralparticleauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.neutralparticleauxcontainer_v1")
    neutralparticle_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.neutralparticle_v1")
    pfoauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.pfoauxcontainer_v1")
    pfodetails = _load_me("func_adl_servicex_xaodr22.xAOD.pfodetails")
    pfo_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.pfo_v1")
    particleauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.particleauxcontainer_v1")
    particle_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.particle_v1")
    photonauxcontainer_v3 = _load_me("func_adl_servicex_xaodr22.xAOD.photonauxcontainer_v3")
    photontrigauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.photontrigauxcontainer_v1")
    photon_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.photon_v1")
    pseudotopresult = _load_me("func_adl_servicex_xaodr22.xAOD.pseudotopresult")
    rodheaderauxcontainer_v2 = _load_me("func_adl_servicex_xaodr22.xAOD.rodheaderauxcontainer_v2")
    rodheader_v2 = _load_me("func_adl_servicex_xaodr22.xAOD.rodheader_v2")
    ringsetauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.ringsetauxcontainer_v1")
    ringsetconfauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.ringsetconfauxcontainer_v1")
    ringsetconf_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.ringsetconf_v1")
    ringset_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.ringset_v1")
    sctrawhitvalidationauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.sctrawhitvalidationauxcontainer_v1")
    sctrawhitvalidation_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.sctrawhitvalidation_v1")
    shallowauxcontainer = _load_me("func_adl_servicex_xaodr22.xAOD.shallowauxcontainer")
    slowmuonauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.slowmuonauxcontainer_v1")
    slowmuon_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.slowmuon_v1")
    systematicevent = _load_me("func_adl_servicex_xaodr22.xAOD.systematicevent")
    systematiceventauxcontainer = _load_me("func_adl_servicex_xaodr22.xAOD.systematiceventauxcontainer")
    tevent = _load_me("func_adl_servicex_xaodr22.xAOD.tevent")
    tvirtualevent = _load_me("func_adl_servicex_xaodr22.xAOD.tvirtualevent")
    taujetauxcontainer_v3 = _load_me("func_adl_servicex_xaodr22.xAOD.taujetauxcontainer_v3")
    taujetparameters = _load_me("func_adl_servicex_xaodr22.xAOD.taujetparameters")
    taujet_v3 = _load_me("func_adl_servicex_xaodr22.xAOD.taujet_v3")
    tautrackauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.tautrackauxcontainer_v1")
    tautrack_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.tautrack_v1")
    trackcaloclusterauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trackcaloclusterauxcontainer_v1")
    trackcalocluster_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trackcalocluster_v1")
    trackjacobianauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trackjacobianauxcontainer_v1")
    trackjacobian_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trackjacobian_v1")
    trackmeasurementauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trackmeasurementauxcontainer_v1")
    trackmeasurementvalidationauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trackmeasurementvalidationauxcontainer_v1")
    trackmeasurementvalidation_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trackmeasurementvalidation_v1")
    trackmeasurement_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trackmeasurement_v1")
    trackparametersauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trackparametersauxcontainer_v1")
    trackparameters_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trackparameters_v1")
    trackparticleauxcontainer_v5 = _load_me("func_adl_servicex_xaodr22.xAOD.trackparticleauxcontainer_v5")
    trackparticleclusterassociationauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trackparticleclusterassociationauxcontainer_v1")
    trackparticleclusterassociation_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trackparticleclusterassociation_v1")
    trackparticle_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trackparticle_v1")
    trackstateauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trackstateauxcontainer_v1")
    trackstatevalidationauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trackstatevalidationauxcontainer_v1")
    trackstatevalidation_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trackstatevalidation_v1")
    trackstate_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trackstate_v1")
    trigbphysauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trigbphysauxcontainer_v1")
    trigbphys_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trigbphys_v1")
    trigcaloclusterauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trigcaloclusterauxcontainer_v1")
    trigcalocluster_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trigcalocluster_v1")
    trigcompositeauxcontainer_v2 = _load_me("func_adl_servicex_xaodr22.xAOD.trigcompositeauxcontainer_v2")
    trigcomposite_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trigcomposite_v1")
    trigemclusterauxcontainer_v2 = _load_me("func_adl_servicex_xaodr22.xAOD.trigemclusterauxcontainer_v2")
    trigemcluster_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trigemcluster_v1")
    trigelectronauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trigelectronauxcontainer_v1")
    trigelectron_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trigelectron_v1")
    trighisto2dauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trighisto2dauxcontainer_v1")
    trighisto2d_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trighisto2d_v1")
    trigmissingetauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trigmissingetauxcontainer_v1")
    trigmissinget_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trigmissinget_v1")
    trigpassbitsauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trigpassbitsauxcontainer_v1")
    trigpassbits_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trigpassbits_v1")
    trigphotonauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trigphotonauxcontainer_v1")
    trigphoton_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trigphoton_v1")
    trigrnnoutputauxcontainer_v2 = _load_me("func_adl_servicex_xaodr22.xAOD.trigrnnoutputauxcontainer_v2")
    trigrnnoutput_v2 = _load_me("func_adl_servicex_xaodr22.xAOD.trigrnnoutput_v2")
    trigringerringsauxcontainer_v2 = _load_me("func_adl_servicex_xaodr22.xAOD.trigringerringsauxcontainer_v2")
    trigringerrings_v2 = _load_me("func_adl_servicex_xaodr22.xAOD.trigringerrings_v2")
    trigspacepointcountsauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trigspacepointcountsauxcontainer_v1")
    trigspacepointcounts_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trigspacepointcounts_v1")
    trigt2mbtsbitsauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trigt2mbtsbitsauxcontainer_v1")
    trigt2mbtsbits_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trigt2mbtsbits_v1")
    trigt2zdcsignalsauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trigt2zdcsignalsauxcontainer_v1")
    trigt2zdcsignals_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trigt2zdcsignals_v1")
    trigtrackcountsauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trigtrackcountsauxcontainer_v1")
    trigtrackcounts_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trigtrackcounts_v1")
    trigvertexcountsauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trigvertexcountsauxcontainer_v1")
    trigvertexcounts_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trigvertexcounts_v1")
    triggermenuauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.triggermenuauxcontainer_v1")
    triggermenujsonauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.triggermenujsonauxcontainer_v1")
    triggermenujson_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.triggermenujson_v1")
    triggermenu_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.triggermenu_v1")
    triggertowerauxcontainer_v2 = _load_me("func_adl_servicex_xaodr22.xAOD.triggertowerauxcontainer_v2")
    triggertower_v2 = _load_me("func_adl_servicex_xaodr22.xAOD.triggertower_v2")
    trutheventauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trutheventauxcontainer_v1")
    trutheventbase_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.trutheventbase_v1")
    truthevent_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.truthevent_v1")
    truthmetadataauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.truthmetadataauxcontainer_v1")
    truthmetadata_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.truthmetadata_v1")
    truthparticleauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.truthparticleauxcontainer_v1")
    truthparticle_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.truthparticle_v1")
    truthpileupeventauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.truthpileupeventauxcontainer_v1")
    truthpileupevent_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.truthpileupevent_v1")
    truthvertexauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.truthvertexauxcontainer_v1")
    truthvertex_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.truthvertex_v1")
    uncalibratedmeasurement_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.uncalibratedmeasurement_v1")
    vertexauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.vertexauxcontainer_v1")
    vertex_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.vertex_v1")
    vxtype = _load_me("func_adl_servicex_xaodr22.xAOD.vxtype")
    zdcmoduleauxcontainer_v2 = _load_me("func_adl_servicex_xaodr22.xAOD.zdcmoduleauxcontainer_v2")
    zdcmodule_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.zdcmodule_v1")
    efexemroiauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.efexemroiauxcontainer_v1")
    efexemroi_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.efexemroi_v1")
    efextauroiauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.efextauroiauxcontainer_v1")
    efextauroi_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.efextauroi_v1")
    efextowerauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.efextowerauxcontainer_v1")
    efextower_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.efextower_v1")
    gfexglobalroiauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.gfexglobalroiauxcontainer_v1")
    gfexglobalroi_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.gfexglobalroi_v1")
    gfexjetroiauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.gfexjetroiauxcontainer_v1")
    gfexjetroi_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.gfexjetroi_v1")
    gfextowerauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.gfextowerauxcontainer_v1")
    gfextower_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.gfextower_v1")
    jfexfwdelroiauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.jfexfwdelroiauxcontainer_v1")
    jfexfwdelroi_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.jfexfwdelroi_v1")
    jfexlrjetroiauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.jfexlrjetroiauxcontainer_v1")
    jfexlrjetroi_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.jfexlrjetroi_v1")
    jfexmetroiauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.jfexmetroiauxcontainer_v1")
    jfexmetroi_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.jfexmetroi_v1")
    jfexsrjetroiauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.jfexsrjetroiauxcontainer_v1")
    jfexsrjetroi_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.jfexsrjetroi_v1")
    jfexsumetroiauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.jfexsumetroiauxcontainer_v1")
    jfexsumetroi_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.jfexsumetroi_v1")
    jfextauroiauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.jfextauroiauxcontainer_v1")
    jfextauroi_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.jfextauroi_v1")
    jfextowerauxcontainer_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.jfextowerauxcontainer_v1")
    jfextower_v1 = _load_me("func_adl_servicex_xaodr22.xAOD.jfextower_v1")
else:
    from . import afpdataauxcontainer_v1
    from . import afpdata_v1
    from . import afpprotonauxcontainer_v1
    from . import afpproton_v1
    from . import afpsihitauxcontainer_v2
    from . import afpsihit_v2
    from . import afpsihitsclusterauxcontainer_v1
    from . import afpsihitscluster_v1
    from . import afptofhitauxcontainer_v1
    from . import afptofhit_v1
    from . import afptoftrackauxcontainer_v1
    from . import afptoftrack_v1
    from . import afptrackauxcontainer_v2
    from . import afptrack_v2
    from . import afpvertexauxcontainer_v1
    from . import afpvertex_v1
    from . import alfadataauxcontainer_v1
    from . import alfadata_v1
    from . import auxcontainerbase
    from . import bcmrawdataauxcontainer_v1
    from . import bcmrawdata_v1
    from . import btagvertexauxcontainer_v1
    from . import btagvertex_v1
    from . import btaggingauxcontainer_v2
    from . import btaggingtrigauxcontainer_v1
    from . import btagging_v1
    from . import bunchconfauxcontainer_v1
    from . import bunchconf_v1
    from . import cmmcphitsauxcontainer_v1
    from . import cmmcphits_v1
    from . import cmmetsumsauxcontainer_v1
    from . import cmmetsums_v1
    from . import cmmjethitsauxcontainer_v1
    from . import cmmjethits_v1
    from . import cmxcphitsauxcontainer_v1
    from . import cmxcphits_v1
    from . import cmxcptobauxcontainer_v1
    from . import cmxcptob_v1
    from . import cmxetsumsauxcontainer_v1
    from . import cmxetsums_v1
    from . import cmxjethitsauxcontainer_v1
    from . import cmxjethits_v1
    from . import cmxjettobauxcontainer_v1
    from . import cmxjettob_v1
    from . import cmxroiauxcontainer_v1
    from . import cmxroi_v1
    from . import cpmhitsauxcontainer_v1
    from . import cpmhits_v1
    from . import cpmroiauxcontainer_v1
    from . import cpmroi_v1
    from . import cpmtobroiauxcontainer_v1
    from . import cpmtobroi_v1
    from . import cpmtowerauxcontainer_v2
    from . import cpmtower_v2
    from . import caloclusterauxcontainer_v2
    from . import caloclusterbadchanneldata_v1
    from . import caloclustertrigauxcontainer_v1
    from . import calocluster_v1
    from . import caloringsauxcontainer_v1
    from . import calorings_v1
    from . import calotowerauxcontainer_v1
    from . import calotowercontainer_v1
    from . import calotower_v1
    from . import calovertexedclusterbase
    from . import calovertexedtopocluster
    from . import compositeparticleauxcontainer_v1
    from . import compositeparticle_v1
    from . import cutbookkeeperauxcontainer_v1
    from . import cutbookkeepercontainer_v1
    from . import cutbookkeeper_v1
    from . import ditaujetauxcontainer_v1
    from . import ditaujetparameters
    from . import ditaujet_v1
    from . import egammaauxcontainer_v1
    from . import egammaparameters
    from . import egamma_v1
    from . import electronauxcontainer_v3
    from . import electrontrigauxcontainer_v1
    from . import electron_v1
    from . import emtauroiauxcontainer_v2
    from . import emtauroi_v2
    from . import eventformatelement
    from . import eventformat_v1
    from . import eventinfo_v1
    from . import forwardeventinfoauxcontainer_v1
    from . import forwardeventinfo_v1
    from . import gblockauxcontainer_v1
    from . import hieventshapeauxcontainer_v2
    from . import hieventshape_v2
    from . import iparticle
    from . import iso
    from . import jemetsumsauxcontainer_v2
    from . import jemetsums_v2
    from . import jemhitsauxcontainer_v1
    from . import jemhits_v1
    from . import jemroiauxcontainer_v1
    from . import jemroi_v1
    from . import jemtobroiauxcontainer_v1
    from . import jemtobroi_v1
    from . import jgtowerauxcontainer_v1
    from . import jgtower_v1
    from . import jetalgorithmtype
    from . import jetauxcontainer_v1
    from . import jetconstituent
    from . import jetconstituentvector
    from . import jetelementauxcontainer_v2
    from . import jetelement_v2
    from . import jetinput
    from . import jetroiauxcontainer_v2
    from . import jetroi_v2
    from . import jet_v1
    from . import klfitterresult
    from . import klfitterresultauxcontainer
    from . import l1toporawdataauxcontainer_v1
    from . import l1toporawdata_v1
    from . import l1toposimresultsauxcontainer_v1
    from . import l1toposimresults_v1
    from . import l2combinedmuonauxcontainer_v1
    from . import l2combinedmuon_v1
    from . import l2isomuonauxcontainer_v1
    from . import l2isomuon_v1
    from . import l2standalonemuonauxcontainer_v2
    from . import l2standalonemuon_v2
    from . import lumiblockrangeauxcontainer_v1
    from . import lumiblockrange_v1
    from . import mbtsmoduleauxcontainer_v1
    from . import mbtsmodule_v1
    from . import missingetauxcontainer_v1
    from . import missingetcontainer_v1
    from . import missinget_v1
    from . import muonauxcontainer_v5
    from . import muonroiauxcontainer_v1
    from . import muonroi_v1
    from . import muonsegmentauxcontainer_v1
    from . import muonsegment_v1
    from . import muon_v1
    from . import neutralparticleauxcontainer_v1
    from . import neutralparticle_v1
    from . import pfoauxcontainer_v1
    from . import pfodetails
    from . import pfo_v1
    from . import particleauxcontainer_v1
    from . import particle_v1
    from . import photonauxcontainer_v3
    from . import photontrigauxcontainer_v1
    from . import photon_v1
    from . import pseudotopresult
    from . import rodheaderauxcontainer_v2
    from . import rodheader_v2
    from . import ringsetauxcontainer_v1
    from . import ringsetconfauxcontainer_v1
    from . import ringsetconf_v1
    from . import ringset_v1
    from . import sctrawhitvalidationauxcontainer_v1
    from . import sctrawhitvalidation_v1
    from . import shallowauxcontainer
    from . import slowmuonauxcontainer_v1
    from . import slowmuon_v1
    from . import systematicevent
    from . import systematiceventauxcontainer
    from . import tevent
    from . import tvirtualevent
    from . import taujetauxcontainer_v3
    from . import taujetparameters
    from . import taujet_v3
    from . import tautrackauxcontainer_v1
    from . import tautrack_v1
    from . import trackcaloclusterauxcontainer_v1
    from . import trackcalocluster_v1
    from . import trackjacobianauxcontainer_v1
    from . import trackjacobian_v1
    from . import trackmeasurementauxcontainer_v1
    from . import trackmeasurementvalidationauxcontainer_v1
    from . import trackmeasurementvalidation_v1
    from . import trackmeasurement_v1
    from . import trackparametersauxcontainer_v1
    from . import trackparameters_v1
    from . import trackparticleauxcontainer_v5
    from . import trackparticleclusterassociationauxcontainer_v1
    from . import trackparticleclusterassociation_v1
    from . import trackparticle_v1
    from . import trackstateauxcontainer_v1
    from . import trackstatevalidationauxcontainer_v1
    from . import trackstatevalidation_v1
    from . import trackstate_v1
    from . import trigbphysauxcontainer_v1
    from . import trigbphys_v1
    from . import trigcaloclusterauxcontainer_v1
    from . import trigcalocluster_v1
    from . import trigcompositeauxcontainer_v2
    from . import trigcomposite_v1
    from . import trigemclusterauxcontainer_v2
    from . import trigemcluster_v1
    from . import trigelectronauxcontainer_v1
    from . import trigelectron_v1
    from . import trighisto2dauxcontainer_v1
    from . import trighisto2d_v1
    from . import trigmissingetauxcontainer_v1
    from . import trigmissinget_v1
    from . import trigpassbitsauxcontainer_v1
    from . import trigpassbits_v1
    from . import trigphotonauxcontainer_v1
    from . import trigphoton_v1
    from . import trigrnnoutputauxcontainer_v2
    from . import trigrnnoutput_v2
    from . import trigringerringsauxcontainer_v2
    from . import trigringerrings_v2
    from . import trigspacepointcountsauxcontainer_v1
    from . import trigspacepointcounts_v1
    from . import trigt2mbtsbitsauxcontainer_v1
    from . import trigt2mbtsbits_v1
    from . import trigt2zdcsignalsauxcontainer_v1
    from . import trigt2zdcsignals_v1
    from . import trigtrackcountsauxcontainer_v1
    from . import trigtrackcounts_v1
    from . import trigvertexcountsauxcontainer_v1
    from . import trigvertexcounts_v1
    from . import triggermenuauxcontainer_v1
    from . import triggermenujsonauxcontainer_v1
    from . import triggermenujson_v1
    from . import triggermenu_v1
    from . import triggertowerauxcontainer_v2
    from . import triggertower_v2
    from . import trutheventauxcontainer_v1
    from . import trutheventbase_v1
    from . import truthevent_v1
    from . import truthmetadataauxcontainer_v1
    from . import truthmetadata_v1
    from . import truthparticleauxcontainer_v1
    from . import truthparticle_v1
    from . import truthpileupeventauxcontainer_v1
    from . import truthpileupevent_v1
    from . import truthvertexauxcontainer_v1
    from . import truthvertex_v1
    from . import uncalibratedmeasurement_v1
    from . import vertexauxcontainer_v1
    from . import vertex_v1
    from . import vxtype
    from . import zdcmoduleauxcontainer_v2
    from . import zdcmodule_v1
    from . import efexemroiauxcontainer_v1
    from . import efexemroi_v1
    from . import efextauroiauxcontainer_v1
    from . import efextauroi_v1
    from . import efextowerauxcontainer_v1
    from . import efextower_v1
    from . import gfexglobalroiauxcontainer_v1
    from . import gfexglobalroi_v1
    from . import gfexjetroiauxcontainer_v1
    from . import gfexjetroi_v1
    from . import gfextowerauxcontainer_v1
    from . import gfextower_v1
    from . import jfexfwdelroiauxcontainer_v1
    from . import jfexfwdelroi_v1
    from . import jfexlrjetroiauxcontainer_v1
    from . import jfexlrjetroi_v1
    from . import jfexmetroiauxcontainer_v1
    from . import jfexmetroi_v1
    from . import jfexsrjetroiauxcontainer_v1
    from . import jfexsrjetroi_v1
    from . import jfexsumetroiauxcontainer_v1
    from . import jfexsumetroi_v1
    from . import jfextauroiauxcontainer_v1
    from . import jfextauroi_v1
    from . import jfextowerauxcontainer_v1
    from . import jfextower_v1

# Include sub-namespace items
from . import EventInfo_v1
from . import TruthParticle_v1
from . import JetConstituentVector
from . import TruthEvent_v1
from . import CompositeParticle_v1
