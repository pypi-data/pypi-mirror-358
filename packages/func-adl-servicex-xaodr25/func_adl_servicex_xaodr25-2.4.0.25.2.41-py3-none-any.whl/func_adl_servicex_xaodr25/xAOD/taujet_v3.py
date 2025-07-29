from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr25

_method_map = {
    'pt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'pt',
        'return_type': 'double',
    },
    'eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'eta',
        'return_type': 'double',
    },
    'phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'phi',
        'return_type': 'double',
    },
    'e': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'e',
        'return_type': 'double',
    },
    'm': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'm',
        'return_type': 'double',
    },
    'rapidity': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'rapidity',
        'return_type': 'double',
    },
    'p4': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'p4',
        'return_type': 'TLorentzVector',
    },
    'ptJetSeed': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'ptJetSeed',
        'return_type': 'double',
    },
    'etaJetSeed': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'etaJetSeed',
        'return_type': 'double',
    },
    'phiJetSeed': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'phiJetSeed',
        'return_type': 'double',
    },
    'mJetSeed': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'mJetSeed',
        'return_type': 'double',
    },
    'ptDetectorAxis': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'ptDetectorAxis',
        'return_type': 'double',
    },
    'etaDetectorAxis': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'etaDetectorAxis',
        'return_type': 'double',
    },
    'phiDetectorAxis': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'phiDetectorAxis',
        'return_type': 'double',
    },
    'mDetectorAxis': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'mDetectorAxis',
        'return_type': 'double',
    },
    'ptIntermediateAxis': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'ptIntermediateAxis',
        'return_type': 'double',
    },
    'etaIntermediateAxis': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'etaIntermediateAxis',
        'return_type': 'double',
    },
    'phiIntermediateAxis': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'phiIntermediateAxis',
        'return_type': 'double',
    },
    'mIntermediateAxis': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'mIntermediateAxis',
        'return_type': 'double',
    },
    'ptTauEnergyScale': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'ptTauEnergyScale',
        'return_type': 'double',
    },
    'etaTauEnergyScale': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'etaTauEnergyScale',
        'return_type': 'double',
    },
    'phiTauEnergyScale': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'phiTauEnergyScale',
        'return_type': 'double',
    },
    'mTauEnergyScale': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'mTauEnergyScale',
        'return_type': 'double',
    },
    'ptTauEtaCalib': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'ptTauEtaCalib',
        'return_type': 'double',
    },
    'etaTauEtaCalib': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'etaTauEtaCalib',
        'return_type': 'double',
    },
    'phiTauEtaCalib': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'phiTauEtaCalib',
        'return_type': 'double',
    },
    'mTauEtaCalib': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'mTauEtaCalib',
        'return_type': 'double',
    },
    'ptPanTauCellBasedProto': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'ptPanTauCellBasedProto',
        'return_type': 'double',
    },
    'etaPanTauCellBasedProto': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'etaPanTauCellBasedProto',
        'return_type': 'double',
    },
    'phiPanTauCellBasedProto': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'phiPanTauCellBasedProto',
        'return_type': 'double',
    },
    'mPanTauCellBasedProto': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'mPanTauCellBasedProto',
        'return_type': 'double',
    },
    'ptPanTauCellBased': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'ptPanTauCellBased',
        'return_type': 'double',
    },
    'etaPanTauCellBased': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'etaPanTauCellBased',
        'return_type': 'double',
    },
    'phiPanTauCellBased': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'phiPanTauCellBased',
        'return_type': 'double',
    },
    'mPanTauCellBased': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'mPanTauCellBased',
        'return_type': 'double',
    },
    'ptTrigCaloOnly': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'ptTrigCaloOnly',
        'return_type': 'double',
    },
    'etaTrigCaloOnly': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'etaTrigCaloOnly',
        'return_type': 'double',
    },
    'phiTrigCaloOnly': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'phiTrigCaloOnly',
        'return_type': 'double',
    },
    'mTrigCaloOnly': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'mTrigCaloOnly',
        'return_type': 'double',
    },
    'ptFinalCalib': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'ptFinalCalib',
        'return_type': 'double',
    },
    'etaFinalCalib': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'etaFinalCalib',
        'return_type': 'double',
    },
    'phiFinalCalib': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'phiFinalCalib',
        'return_type': 'double',
    },
    'mFinalCalib': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'mFinalCalib',
        'return_type': 'double',
    },
    'type': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'type',
        'return_type': 'xAODType::ObjectType',
    },
    'charge': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'charge',
        'return_type': 'float',
    },
    'ROIWord': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'ROIWord',
        'return_type': 'unsigned int',
    },
    'hasDiscriminant': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'hasDiscriminant',
        'return_type': 'bool',
    },
    'discriminant': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'discriminant',
        'return_type': 'double',
    },
    'isTau': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'isTau',
        'return_type': 'bool',
    },
    'detail': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'detail',
        'return_type': 'bool',
    },
    'panTauDetail': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'panTauDetail',
        'return_type': 'bool',
    },
    'jetLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'jetLink',
        'return_type': 'const ElementLink<DataVector<xAOD::Jet_v1>>',
    },
    'jet': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'jet',
        'return_type': 'const xAOD::Jet_v1 *',
    },
    'vertexLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'vertexLink',
        'return_type': 'const ElementLink<DataVector<xAOD::Vertex_v1>>',
    },
    'vertex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'vertex',
        'return_type': 'const xAOD::Vertex_v1 *',
    },
    'secondaryVertexLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'secondaryVertexLink',
        'return_type': 'const ElementLink<DataVector<xAOD::Vertex_v1>>',
    },
    'secondaryVertex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'secondaryVertex',
        'return_type': 'const xAOD::Vertex_v1 *',
    },
    'tauTrackLinks': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'tauTrackLinks',
        'return_type_element': 'ElementLink<DataVector<xAOD::TauTrack_v1>>',
        'return_type_collection': 'const vector<ElementLink<DataVector<xAOD::TauTrack_v1>>>',
    },
    'tauTrackLinksWithMask': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'tauTrackLinksWithMask',
        'return_type_element': 'ElementLink<DataVector<xAOD::TauTrack_v1>>',
        'return_type_collection': 'const vector<ElementLink<DataVector<xAOD::TauTrack_v1>>>',
    },
    'allTauTrackLinksNonConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'allTauTrackLinksNonConst',
        'return_type_element': 'ElementLink<DataVector<xAOD::TauTrack_v1>>',
        'return_type_collection': 'vector<ElementLink<DataVector<xAOD::TauTrack_v1>>>',
    },
    'allTauTrackLinks': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'allTauTrackLinks',
        'return_type_element': 'ElementLink<DataVector<xAOD::TauTrack_v1>>',
        'return_type_collection': 'const vector<ElementLink<DataVector<xAOD::TauTrack_v1>>>',
    },
    'track': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'track',
        'return_type': 'const xAOD::TauTrack_v1 *',
    },
    'trackWithMask': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'trackWithMask',
        'return_type': 'const xAOD::TauTrack_v1 *',
    },
    'nTracks': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'nTracks',
        'return_type': 'unsigned int',
    },
    'nTracksCharged': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'nTracksCharged',
        'return_type': 'unsigned int',
    },
    'nTracksIsolation': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'nTracksIsolation',
        'return_type': 'unsigned int',
    },
    'nTracksWithMask': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'nTracksWithMask',
        'return_type': 'unsigned int',
    },
    'nAllTracks': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'nAllTracks',
        'return_type': 'unsigned int',
    },
    'clusterLinks': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'clusterLinks',
        'return_type_element': 'ElementLink<DataVector<xAOD::IParticle>>',
        'return_type_collection': 'const vector<ElementLink<DataVector<xAOD::IParticle>>>',
    },
    'cluster': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'cluster',
        'return_type': 'const xAOD::IParticle *',
    },
    'calibratedCluster': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'calibratedCluster',
        'return_type': 'TLorentzVector',
    },
    'nClusters': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'nClusters',
        'return_type': 'unsigned int',
    },
    'vertexedClusters': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'vertexedClusters',
        'return_type_element': 'xAOD::CaloVertexedTopoCluster',
        'return_type_collection': 'vector<xAOD::CaloVertexedTopoCluster>',
    },
    'pi0Links': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'pi0Links',
        'return_type_element': 'ElementLink<DataVector<xAOD::IParticle>>',
        'return_type_collection': 'const vector<ElementLink<DataVector<xAOD::IParticle>>>',
    },
    'pi0': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'pi0',
        'return_type': 'const xAOD::IParticle *',
    },
    'nPi0s': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'nPi0s',
        'return_type': 'unsigned int',
    },
    'trackFilterProngs': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'trackFilterProngs',
        'return_type': 'int',
    },
    'trackFilterQuality': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'trackFilterQuality',
        'return_type': 'int',
    },
    'pi0ConeDR': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'pi0ConeDR',
        'return_type': 'float',
    },
    'hadronicPFOLinks': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'hadronicPFOLinks',
        'return_type_element': 'ElementLink<DataVector<xAOD::PFO_v1>>',
        'return_type_collection': 'const vector<ElementLink<DataVector<xAOD::PFO_v1>>>',
    },
    'hadronicPFO': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'hadronicPFO',
        'return_type': 'const xAOD::PFO_v1 *',
    },
    'nHadronicPFOs': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'nHadronicPFOs',
        'return_type': 'unsigned int',
    },
    'shotPFOLinks': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'shotPFOLinks',
        'return_type_element': 'ElementLink<DataVector<xAOD::PFO_v1>>',
        'return_type_collection': 'const vector<ElementLink<DataVector<xAOD::PFO_v1>>>',
    },
    'shotPFO': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'shotPFO',
        'return_type': 'const xAOD::PFO_v1 *',
    },
    'nShotPFOs': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'nShotPFOs',
        'return_type': 'unsigned int',
    },
    'chargedPFOLinks': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'chargedPFOLinks',
        'return_type_element': 'ElementLink<DataVector<xAOD::PFO_v1>>',
        'return_type_collection': 'const vector<ElementLink<DataVector<xAOD::PFO_v1>>>',
    },
    'chargedPFO': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'chargedPFO',
        'return_type': 'const xAOD::PFO_v1 *',
    },
    'nChargedPFOs': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'nChargedPFOs',
        'return_type': 'unsigned int',
    },
    'neutralPFOLinks': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'neutralPFOLinks',
        'return_type_element': 'ElementLink<DataVector<xAOD::PFO_v1>>',
        'return_type_collection': 'const vector<ElementLink<DataVector<xAOD::PFO_v1>>>',
    },
    'neutralPFO': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'neutralPFO',
        'return_type': 'const xAOD::PFO_v1 *',
    },
    'nNeutralPFOs': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'nNeutralPFOs',
        'return_type': 'unsigned int',
    },
    'pi0PFOLinks': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'pi0PFOLinks',
        'return_type_element': 'ElementLink<DataVector<xAOD::PFO_v1>>',
        'return_type_collection': 'const vector<ElementLink<DataVector<xAOD::PFO_v1>>>',
    },
    'pi0PFO': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'pi0PFO',
        'return_type': 'const xAOD::PFO_v1 *',
    },
    'nPi0PFOs': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'nPi0PFOs',
        'return_type': 'unsigned int',
    },
    'protoChargedPFOLinks': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'protoChargedPFOLinks',
        'return_type_element': 'ElementLink<DataVector<xAOD::PFO_v1>>',
        'return_type_collection': 'const vector<ElementLink<DataVector<xAOD::PFO_v1>>>',
    },
    'protoChargedPFO': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'protoChargedPFO',
        'return_type': 'const xAOD::PFO_v1 *',
    },
    'nProtoChargedPFOs': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'nProtoChargedPFOs',
        'return_type': 'unsigned int',
    },
    'protoNeutralPFOLinks': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'protoNeutralPFOLinks',
        'return_type_element': 'ElementLink<DataVector<xAOD::PFO_v1>>',
        'return_type_collection': 'const vector<ElementLink<DataVector<xAOD::PFO_v1>>>',
    },
    'protoNeutralPFO': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'protoNeutralPFO',
        'return_type': 'const xAOD::PFO_v1 *',
    },
    'nProtoNeutralPFOs': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'nProtoNeutralPFOs',
        'return_type': 'unsigned int',
    },
    'protoPi0PFOLinks': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'protoPi0PFOLinks',
        'return_type_element': 'ElementLink<DataVector<xAOD::PFO_v1>>',
        'return_type_collection': 'const vector<ElementLink<DataVector<xAOD::PFO_v1>>>',
    },
    'protoPi0PFO': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'protoPi0PFO',
        'return_type': 'const xAOD::PFO_v1 *',
    },
    'nProtoPi0PFOs': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'nProtoPi0PFOs',
        'return_type': 'unsigned int',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'trackIndices',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TauJet_v3',
        'method_name': 'isAvailable',
        'return_type': 'bool',
    },
}

_enum_function_map = {
    'type': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAODType',
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
                'FlowElement',
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
    'hasDiscriminant': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.TauJetParameters',
            'name': 'TauID',
            'values': [
                'EleMatchLikelihoodScore',
                'Likelihood',
                'BDTJetScore',
                'BDTEleScore',
                'SafeLikelihood',
                'BDTJetScoreSigTrans',
                'PanTauScore',
                'RNNJetScore',
                'RNNJetScoreSigTrans',
                'RNNEleScore',
                'RNNEleScoreSigTrans',
            ],
        },
    ],
    'discriminant': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.TauJetParameters',
            'name': 'TauID',
            'values': [
                'EleMatchLikelihoodScore',
                'Likelihood',
                'BDTJetScore',
                'BDTEleScore',
                'SafeLikelihood',
                'BDTJetScoreSigTrans',
                'PanTauScore',
                'RNNJetScore',
                'RNNJetScoreSigTrans',
                'RNNEleScore',
                'RNNEleScoreSigTrans',
            ],
        },
    ],
    'isTau': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.TauJetParameters',
            'name': 'IsTauFlag',
            'values': [
                'PassEleOLR',
                'MuonVeto',
                'EleRNNLoose',
                'EleRNNMedium',
                'EleRNNTight',
                'JetBDTSigVeryLoose',
                'JetBDTSigLoose',
                'JetBDTSigMedium',
                'JetBDTSigTight',
                'EleBDTLoose',
                'EleBDTMedium',
                'EleBDTTight',
                'JetBDTBkgLoose',
                'JetBDTBkgMedium',
                'JetBDTBkgTight',
                'JetRNNSigVeryLoose',
                'JetRNNSigLoose',
                'JetRNNSigMedium',
                'JetRNNSigTight',
            ],
        },
    ],
    'detail': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.TauJetParameters',
            'name': 'Detail',
            'values': [
                'ipZ0SinThetaSigLeadTrk',
                'etOverPtLeadTrk',
                'leadTrkPt',
                'ipSigLeadTrk',
                'massTrkSys',
                'trkWidth2',
                'trFlightPathSig',
                'numCells',
                'numTopoClusters',
                'numEffTopoClusters',
                'topoInvMass',
                'effTopoInvMass',
                'topoMeanDeltaR',
                'effTopoMeanDeltaR',
                'EMRadius',
                'hadRadius',
                'etEMAtEMScale',
                'etHadAtEMScale',
                'isolFrac',
                'centFrac',
                'stripWidth2',
                'nStrip',
                'trkAvgDist',
                'trkRmsDist',
                'lead2ClusterEOverAllClusterE',
                'lead3ClusterEOverAllClusterE',
                'caloIso',
                'caloIsoCorrected',
                'dRmax',
                'secMaxStripEt',
                'sumEMCellEtOverLeadTrkPt',
                'hadLeakEt',
                'cellBasedEnergyRing1',
                'cellBasedEnergyRing2',
                'cellBasedEnergyRing3',
                'cellBasedEnergyRing4',
                'cellBasedEnergyRing5',
                'cellBasedEnergyRing6',
                'cellBasedEnergyRing7',
                'TRT_NHT_OVER_NLT',
                'TauJetVtxFraction',
                'nCharged',
                'PSSFraction',
                'ChPiEMEOverCaloEME',
                'EMPOverTrkSysP',
                'TESOffset',
                'TESCalibConstant',
                'centFracCorrected',
                'etOverPtLeadTrkCorrected',
                'innerTrkAvgDist',
                'innerTrkAvgDistCorrected',
                'SumPtTrkFrac',
                'SumPtTrkFracCorrected',
                'mEflowApprox',
                'ptRatioEflowApprox',
                'ipSigLeadTrkCorrected',
                'trFlightPathSigCorrected',
                'massTrkSysCorrected',
                'dRmaxCorrected',
                'ChPiEMEOverCaloEMECorrected',
                'EMPOverTrkSysPCorrected',
                'ptRatioEflowApproxCorrected',
                'mEflowApproxCorrected',
                'ClustersMeanCenterLambda',
                'ClustersMeanEMProbability',
                'ClustersMeanFirstEngDens',
                'ClustersMeanSecondLambda',
                'ClustersMeanPresamplerFrac',
                'GhostMuonSegmentCount',
                'PFOEngRelDiff',
                'LC_pantau_interpolPt',
                'electronLink',
                'nChargedTracks',
                'nIsolatedTracks',
                'nModifiedIsolationTracks',
                'nAllTracks',
                'nLargeRadiusTracks',
            ],
        },
    ],
    'panTauDetail': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.TauJetParameters',
            'name': 'PanTauDetails',
            'values': [
                'PanTau_isPanTauCandidate',
                'PanTau_DecayModeProto',
                'PanTau_DecayMode',
                'PanTau_BDTValue_1p0n_vs_1p1n',
                'PanTau_BDTValue_1p1n_vs_1pXn',
                'PanTau_BDTValue_3p0n_vs_3pXn',
                'PanTau_BDTVar_Basic_NNeutralConsts',
                'PanTau_BDTVar_Charged_JetMoment_EtDRxTotalEt',
                'PanTau_BDTVar_Charged_StdDev_Et_WrtEtAllConsts',
                'PanTau_BDTVar_Neutral_HLV_SumM',
                'PanTau_BDTVar_Neutral_PID_BDTValues_BDTSort_1',
                'PanTau_BDTVar_Neutral_PID_BDTValues_BDTSort_2',
                'PanTau_BDTVar_Neutral_Ratio_1stBDTEtOverEtAllConsts',
                'PanTau_BDTVar_Neutral_Ratio_EtOverEtAllConsts',
                'PanTau_BDTVar_Neutral_Shots_NPhotonsInSeed',
                'PanTau_BDTVar_Combined_DeltaR1stNeutralTo1stCharged',
                'PanTau_DecayModeExtended',
                'PanTau_BDTVar_Charged_HLV_SumM',
            ],
        },
    ],
    'tauTrackLinks': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.TauJetParameters',
            'name': 'TauTrackFlag',
            'values': [
                'isConversionOld',
                'failTrackFilter',
                'coreTrack',
                'wideTrack',
                'passTrkSelector',
                'classifiedCharged',
                'classifiedIsolation',
                'classifiedConversion',
                'classifiedFake',
                'unclassified',
                'passTrkSelectionTight',
                'modifiedIsolationTrack',
                'LargeRadiusTrack',
            ],
        },
    ],
    'track': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.TauJetParameters',
            'name': 'TauTrackFlag',
            'values': [
                'isConversionOld',
                'failTrackFilter',
                'coreTrack',
                'wideTrack',
                'passTrkSelector',
                'classifiedCharged',
                'classifiedIsolation',
                'classifiedConversion',
                'classifiedFake',
                'unclassified',
                'passTrkSelectionTight',
                'modifiedIsolationTrack',
                'LargeRadiusTrack',
            ],
        },
    ],
    'nTracks': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.TauJetParameters',
            'name': 'TauTrackFlag',
            'values': [
                'isConversionOld',
                'failTrackFilter',
                'coreTrack',
                'wideTrack',
                'passTrkSelector',
                'classifiedCharged',
                'classifiedIsolation',
                'classifiedConversion',
                'classifiedFake',
                'unclassified',
                'passTrkSelectionTight',
                'modifiedIsolationTrack',
                'LargeRadiusTrack',
            ],
        },
    ],
    'calibratedCluster': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.CaloCluster_v1',
            'name': 'State',
            'values': [
                'UNKNOWN',
                'UNCALIBRATED',
                'CALIBRATED',
                'ALTCALIBRATED',
                'NSTATES',
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
            'name': 'xAODTau/versions/TauJet_v3.h',
            'body_includes': ["xAODTau/versions/TauJet_v3.h"],
        })


        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODTau',
            'link_libraries': ["xAODTau"],
        })

        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class TauJet_v3:
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

    def e(self) -> float:
        "A method"
        ...

    def m(self) -> float:
        "A method"
        ...

    def rapidity(self) -> float:
        "A method"
        ...

    def p4(self) -> func_adl_servicex_xaodr25.tlorentzvector.TLorentzVector:
        "A method"
        ...

    def ptJetSeed(self) -> float:
        "A method"
        ...

    def etaJetSeed(self) -> float:
        "A method"
        ...

    def phiJetSeed(self) -> float:
        "A method"
        ...

    def mJetSeed(self) -> float:
        "A method"
        ...

    def ptDetectorAxis(self) -> float:
        "A method"
        ...

    def etaDetectorAxis(self) -> float:
        "A method"
        ...

    def phiDetectorAxis(self) -> float:
        "A method"
        ...

    def mDetectorAxis(self) -> float:
        "A method"
        ...

    def ptIntermediateAxis(self) -> float:
        "A method"
        ...

    def etaIntermediateAxis(self) -> float:
        "A method"
        ...

    def phiIntermediateAxis(self) -> float:
        "A method"
        ...

    def mIntermediateAxis(self) -> float:
        "A method"
        ...

    def ptTauEnergyScale(self) -> float:
        "A method"
        ...

    def etaTauEnergyScale(self) -> float:
        "A method"
        ...

    def phiTauEnergyScale(self) -> float:
        "A method"
        ...

    def mTauEnergyScale(self) -> float:
        "A method"
        ...

    def ptTauEtaCalib(self) -> float:
        "A method"
        ...

    def etaTauEtaCalib(self) -> float:
        "A method"
        ...

    def phiTauEtaCalib(self) -> float:
        "A method"
        ...

    def mTauEtaCalib(self) -> float:
        "A method"
        ...

    def ptPanTauCellBasedProto(self) -> float:
        "A method"
        ...

    def etaPanTauCellBasedProto(self) -> float:
        "A method"
        ...

    def phiPanTauCellBasedProto(self) -> float:
        "A method"
        ...

    def mPanTauCellBasedProto(self) -> float:
        "A method"
        ...

    def ptPanTauCellBased(self) -> float:
        "A method"
        ...

    def etaPanTauCellBased(self) -> float:
        "A method"
        ...

    def phiPanTauCellBased(self) -> float:
        "A method"
        ...

    def mPanTauCellBased(self) -> float:
        "A method"
        ...

    def ptTrigCaloOnly(self) -> float:
        "A method"
        ...

    def etaTrigCaloOnly(self) -> float:
        "A method"
        ...

    def phiTrigCaloOnly(self) -> float:
        "A method"
        ...

    def mTrigCaloOnly(self) -> float:
        "A method"
        ...

    def ptFinalCalib(self) -> float:
        "A method"
        ...

    def etaFinalCalib(self) -> float:
        "A method"
        ...

    def phiFinalCalib(self) -> float:
        "A method"
        ...

    def mFinalCalib(self) -> float:
        "A method"
        ...

    def type(self) -> func_adl_servicex_xaodr25.xaodtype.xAODType.ObjectType:
        "A method"
        ...

    def charge(self) -> float:
        "A method"
        ...

    def ROIWord(self) -> int:
        "A method"
        ...

    def hasDiscriminant(self, discID: func_adl_servicex_xaodr25.xAOD.taujetparameters.TauJetParameters.TauID) -> bool:
        "A method"
        ...

    def discriminant(self, discID: func_adl_servicex_xaodr25.xAOD.taujetparameters.TauJetParameters.TauID) -> float:
        "A method"
        ...

    def isTau(self, flag: func_adl_servicex_xaodr25.xAOD.taujetparameters.TauJetParameters.IsTauFlag) -> bool:
        "A method"
        ...

    def detail(self, detail: func_adl_servicex_xaodr25.xAOD.taujetparameters.TauJetParameters.Detail, value: int) -> bool:
        "A method"
        ...

    def panTauDetail(self, panTauDetail: func_adl_servicex_xaodr25.xAOD.taujetparameters.TauJetParameters.PanTauDetails, value: int) -> bool:
        "A method"
        ...

    def jetLink(self) -> func_adl_servicex_xaodr25.elementlink_datavector_xaod_jet_v1__.ElementLink_DataVector_xAOD_Jet_v1__:
        "A method"
        ...

    def jet(self) -> func_adl_servicex_xaodr25.xAOD.jet_v1.Jet_v1:
        "A method"
        ...

    def vertexLink(self) -> func_adl_servicex_xaodr25.elementlink_datavector_xaod_vertex_v1__.ElementLink_DataVector_xAOD_Vertex_v1__:
        "A method"
        ...

    def vertex(self) -> func_adl_servicex_xaodr25.xAOD.vertex_v1.Vertex_v1:
        "A method"
        ...

    def secondaryVertexLink(self) -> func_adl_servicex_xaodr25.elementlink_datavector_xaod_vertex_v1__.ElementLink_DataVector_xAOD_Vertex_v1__:
        "A method"
        ...

    def secondaryVertex(self) -> func_adl_servicex_xaodr25.xAOD.vertex_v1.Vertex_v1:
        "A method"
        ...

    def tauTrackLinks(self, noname_arg: func_adl_servicex_xaodr25.xAOD.taujetparameters.TauJetParameters.TauTrackFlag) -> func_adl_servicex_xaodr25.vector_elementlink_datavector_xaod_tautrack_v1___.vector_ElementLink_DataVector_xAOD_TauTrack_v1___:
        "A method"
        ...

    def tauTrackLinksWithMask(self, noname_arg: int) -> func_adl_servicex_xaodr25.vector_elementlink_datavector_xaod_tautrack_v1___.vector_ElementLink_DataVector_xAOD_TauTrack_v1___:
        "A method"
        ...

    def allTauTrackLinksNonConst(self) -> func_adl_servicex_xaodr25.vector_elementlink_datavector_xaod_tautrack_v1___.vector_ElementLink_DataVector_xAOD_TauTrack_v1___:
        "A method"
        ...

    def allTauTrackLinks(self) -> func_adl_servicex_xaodr25.vector_elementlink_datavector_xaod_tautrack_v1___.vector_ElementLink_DataVector_xAOD_TauTrack_v1___:
        "A method"
        ...

    def track(self, i: int, flag: func_adl_servicex_xaodr25.xAOD.taujetparameters.TauJetParameters.TauTrackFlag, container_index: int) -> func_adl_servicex_xaodr25.xAOD.tautrack_v1.TauTrack_v1:
        "A method"
        ...

    def trackWithMask(self, i: int, mask: int, container_index: int) -> func_adl_servicex_xaodr25.xAOD.tautrack_v1.TauTrack_v1:
        "A method"
        ...

    def nTracks(self, flag: func_adl_servicex_xaodr25.xAOD.taujetparameters.TauJetParameters.TauTrackFlag) -> int:
        "A method"
        ...

    def nTracksCharged(self) -> int:
        "A method"
        ...

    def nTracksIsolation(self) -> int:
        "A method"
        ...

    def nTracksWithMask(self, classification: int) -> int:
        "A method"
        ...

    def nAllTracks(self) -> int:
        "A method"
        ...

    def clusterLinks(self) -> func_adl_servicex_xaodr25.vector_elementlink_datavector_xaod_iparticle___.vector_ElementLink_DataVector_xAOD_IParticle___:
        "A method"
        ...

    def cluster(self, i: int) -> func_adl_servicex_xaodr25.xAOD.iparticle.IParticle:
        "A method"
        ...

    def calibratedCluster(self, i: int, state: func_adl_servicex_xaodr25.xAOD.calocluster_v1.CaloCluster_v1.State) -> func_adl_servicex_xaodr25.tlorentzvector.TLorentzVector:
        "A method"
        ...

    def nClusters(self) -> int:
        "A method"
        ...

    def vertexedClusters(self) -> func_adl_servicex_xaodr25.vector_xaod_calovertexedtopocluster_.vector_xAOD_CaloVertexedTopoCluster_:
        "A method"
        ...

    def pi0Links(self) -> func_adl_servicex_xaodr25.vector_elementlink_datavector_xaod_iparticle___.vector_ElementLink_DataVector_xAOD_IParticle___:
        "A method"
        ...

    def pi0(self, i: int) -> func_adl_servicex_xaodr25.xAOD.iparticle.IParticle:
        "A method"
        ...

    def nPi0s(self) -> int:
        "A method"
        ...

    def trackFilterProngs(self) -> int:
        "A method"
        ...

    def trackFilterQuality(self) -> int:
        "A method"
        ...

    def pi0ConeDR(self) -> float:
        "A method"
        ...

    def hadronicPFOLinks(self) -> func_adl_servicex_xaodr25.vector_elementlink_datavector_xaod_pfo_v1___.vector_ElementLink_DataVector_xAOD_PFO_v1___:
        "A method"
        ...

    def hadronicPFO(self, i: int) -> func_adl_servicex_xaodr25.xAOD.pfo_v1.PFO_v1:
        "A method"
        ...

    def nHadronicPFOs(self) -> int:
        "A method"
        ...

    def shotPFOLinks(self) -> func_adl_servicex_xaodr25.vector_elementlink_datavector_xaod_pfo_v1___.vector_ElementLink_DataVector_xAOD_PFO_v1___:
        "A method"
        ...

    def shotPFO(self, i: int) -> func_adl_servicex_xaodr25.xAOD.pfo_v1.PFO_v1:
        "A method"
        ...

    def nShotPFOs(self) -> int:
        "A method"
        ...

    def chargedPFOLinks(self) -> func_adl_servicex_xaodr25.vector_elementlink_datavector_xaod_pfo_v1___.vector_ElementLink_DataVector_xAOD_PFO_v1___:
        "A method"
        ...

    def chargedPFO(self, i: int) -> func_adl_servicex_xaodr25.xAOD.pfo_v1.PFO_v1:
        "A method"
        ...

    def nChargedPFOs(self) -> int:
        "A method"
        ...

    def neutralPFOLinks(self) -> func_adl_servicex_xaodr25.vector_elementlink_datavector_xaod_pfo_v1___.vector_ElementLink_DataVector_xAOD_PFO_v1___:
        "A method"
        ...

    def neutralPFO(self, i: int) -> func_adl_servicex_xaodr25.xAOD.pfo_v1.PFO_v1:
        "A method"
        ...

    def nNeutralPFOs(self) -> int:
        "A method"
        ...

    def pi0PFOLinks(self) -> func_adl_servicex_xaodr25.vector_elementlink_datavector_xaod_pfo_v1___.vector_ElementLink_DataVector_xAOD_PFO_v1___:
        "A method"
        ...

    def pi0PFO(self, i: int) -> func_adl_servicex_xaodr25.xAOD.pfo_v1.PFO_v1:
        "A method"
        ...

    def nPi0PFOs(self) -> int:
        "A method"
        ...

    def protoChargedPFOLinks(self) -> func_adl_servicex_xaodr25.vector_elementlink_datavector_xaod_pfo_v1___.vector_ElementLink_DataVector_xAOD_PFO_v1___:
        "A method"
        ...

    def protoChargedPFO(self, i: int) -> func_adl_servicex_xaodr25.xAOD.pfo_v1.PFO_v1:
        "A method"
        ...

    def nProtoChargedPFOs(self) -> int:
        "A method"
        ...

    def protoNeutralPFOLinks(self) -> func_adl_servicex_xaodr25.vector_elementlink_datavector_xaod_pfo_v1___.vector_ElementLink_DataVector_xAOD_PFO_v1___:
        "A method"
        ...

    def protoNeutralPFO(self, i: int) -> func_adl_servicex_xaodr25.xAOD.pfo_v1.PFO_v1:
        "A method"
        ...

    def nProtoNeutralPFOs(self) -> int:
        "A method"
        ...

    def protoPi0PFOLinks(self) -> func_adl_servicex_xaodr25.vector_elementlink_datavector_xaod_pfo_v1___.vector_ElementLink_DataVector_xAOD_PFO_v1___:
        "A method"
        ...

    def protoPi0PFO(self, i: int) -> func_adl_servicex_xaodr25.xAOD.pfo_v1.PFO_v1:
        "A method"
        ...

    def nProtoPi0PFOs(self) -> int:
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

    def trackIndices(self) -> bool:
        "A method"
        ...

    @func_adl_parameterized_call(lambda s, a, param_1: func_adl_servicex_xaodr25.type_support.cpp_generic_1arg_callback('auxdataConst', s, a, param_1))
    @property
    def auxdataConst(self) -> func_adl_servicex_xaodr25.type_support.index_type_forwarder[str]:
        "A method"
        ...

    @func_adl_parameterized_call(lambda s, a, param_1: func_adl_servicex_xaodr25.type_support.cpp_generic_1arg_callback('isAvailable', s, a, param_1))
    @property
    def isAvailable(self) -> func_adl_servicex_xaodr25.type_support.index_type_forwarder[str]:
        "A method"
        ...
