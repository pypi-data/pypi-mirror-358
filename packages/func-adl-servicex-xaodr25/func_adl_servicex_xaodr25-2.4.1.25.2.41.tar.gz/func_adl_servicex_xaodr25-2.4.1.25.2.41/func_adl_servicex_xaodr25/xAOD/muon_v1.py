from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr25

_method_map = {
    'pt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'pt',
        'return_type': 'double',
    },
    'eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'eta',
        'return_type': 'double',
    },
    'phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'phi',
        'return_type': 'double',
    },
    'm': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'm',
        'return_type': 'double',
    },
    'e': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'e',
        'return_type': 'double',
    },
    'rapidity': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'rapidity',
        'return_type': 'double',
    },
    'p4': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'p4',
        'return_type': 'TLorentzVector',
    },
    'type': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'type',
        'return_type': 'xAODType::ObjectType',
    },
    'charge': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'charge',
        'return_type': 'float',
    },
    'author': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'author',
        'return_type': 'xAOD::Muon_v1::Author',
    },
    'isAuthor': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'isAuthor',
        'return_type': 'bool',
    },
    'allAuthors': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'allAuthors',
        'return_type': 'uint16_t',
    },
    'muonType': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'muonType',
        'return_type': 'xAOD::Muon_v1::MuonType',
    },
    'summaryValue': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'summaryValue',
        'return_type': 'bool',
    },
    'floatSummaryValue': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'floatSummaryValue',
        'return_type': 'float',
    },
    'uint8SummaryValue': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'uint8SummaryValue',
        'return_type': 'uint8_t',
    },
    'uint8MuonSummaryValue': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'uint8MuonSummaryValue',
        'return_type': 'float',
    },
    'parameter': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'parameter',
        'return_type': 'bool',
    },
    'floatParameter': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'floatParameter',
        'return_type': 'float',
    },
    'intParameter': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'intParameter',
        'return_type': 'int',
    },
    'quality': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'quality',
        'return_type': 'xAOD::Muon_v1::Quality',
    },
    'passesIDCuts': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'passesIDCuts',
        'return_type': 'bool',
    },
    'isolation': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'isolation',
        'return_type': 'bool',
    },
    'isolationCaloCorrection': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'isolationCaloCorrection',
        'return_type': 'bool',
    },
    'setIsolationCaloCorrection': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'setIsolationCaloCorrection',
        'return_type': 'bool',
    },
    'isolationTrackCorrection': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'isolationTrackCorrection',
        'return_type': 'bool',
    },
    'setIsolationTrackCorrection': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'setIsolationTrackCorrection',
        'return_type': 'bool',
    },
    'setIsolationCorrectionBitset': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'setIsolationCorrectionBitset',
        'return_type': 'bool',
    },
    'primaryTrackParticleLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'primaryTrackParticleLink',
        'return_type': 'const ElementLink<DataVector<xAOD::TrackParticle_v1>>',
    },
    'primaryTrackParticle': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'primaryTrackParticle',
        'return_type': 'const xAOD::TrackParticle_v1 *',
    },
    'inDetTrackParticleLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'inDetTrackParticleLink',
        'return_type': 'const ElementLink<DataVector<xAOD::TrackParticle_v1>>',
    },
    'muonSpectrometerTrackParticleLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'muonSpectrometerTrackParticleLink',
        'return_type': 'const ElementLink<DataVector<xAOD::TrackParticle_v1>>',
    },
    'combinedTrackParticleLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'combinedTrackParticleLink',
        'return_type': 'const ElementLink<DataVector<xAOD::TrackParticle_v1>>',
    },
    'extrapolatedMuonSpectrometerTrackParticleLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'extrapolatedMuonSpectrometerTrackParticleLink',
        'return_type': 'const ElementLink<DataVector<xAOD::TrackParticle_v1>>',
    },
    'msOnlyExtrapolatedMuonSpectrometerTrackParticleLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'msOnlyExtrapolatedMuonSpectrometerTrackParticleLink',
        'return_type': 'const ElementLink<DataVector<xAOD::TrackParticle_v1>>',
    },
    'trackParticleLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'trackParticleLink',
        'return_type': 'const ElementLink<DataVector<xAOD::TrackParticle_v1>>',
    },
    'trackParticle': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'trackParticle',
        'return_type': 'const xAOD::TrackParticle_v1 *',
    },
    'clusterLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'clusterLink',
        'return_type': 'const ElementLink<DataVector<xAOD::CaloCluster_v1>>',
    },
    'cluster': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'cluster',
        'return_type': 'const xAOD::CaloCluster_v1 *',
    },
    'energyLossType': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'energyLossType',
        'return_type': 'xAOD::Muon_v1::EnergyLossType',
    },
    'muonSegmentLinks': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'muonSegmentLinks',
        'return_type_element': 'ElementLink<DataVector<xAOD::MuonSegment_v1>>',
        'return_type_collection': 'const vector<ElementLink<DataVector<xAOD::MuonSegment_v1>>>',
    },
    'nMuonSegments': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'nMuonSegments',
        'return_type': 'unsigned int',
    },
    'muonSegment': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'muonSegment',
        'return_type': 'const xAOD::MuonSegment_v1 *',
    },
    'muonSegmentLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'muonSegmentLink',
        'return_type': 'const ElementLink<DataVector<xAOD::MuonSegment_v1>>',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'trackIndices',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
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
    'author': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.Muon_v1',
            'name': 'Author',
            'values': [
                'unknown',
                'MuidCo',
                'STACO',
                'MuTag',
                'MuTagIMO',
                'MuidSA',
                'MuGirl',
                'MuGirlLowBeta',
                'CaloTag',
                'CaloLikelihood',
                'CaloScore',
                'ExtrapolateMuonToIP',
                'Commissioning',
                'NumberOfMuonAuthors',
            ],
        },
    ],
    'isAuthor': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.Muon_v1',
            'name': 'Author',
            'values': [
                'unknown',
                'MuidCo',
                'STACO',
                'MuTag',
                'MuTagIMO',
                'MuidSA',
                'MuGirl',
                'MuGirlLowBeta',
                'CaloTag',
                'CaloLikelihood',
                'CaloScore',
                'ExtrapolateMuonToIP',
                'Commissioning',
                'NumberOfMuonAuthors',
            ],
        },
    ],
    'muonType': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.Muon_v1',
            'name': 'MuonType',
            'values': [
                'Combined',
                'MuonStandAlone',
                'SegmentTagged',
                'CaloTagged',
                'SiliconAssociatedForwardMuon',
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
                'numberOfInnermostPixelLayerEndcapHits',
                'numberOfInnermostPixelLayerEndcapOutliers',
                'numberOfInnermostPixelLayerSharedEndcapHits',
                'numberOfInnermostPixelLayerSplitEndcapHits',
                'expectNextToInnermostPixelLayerHit',
                'numberOfNextToInnermostPixelLayerHits',
                'numberOfNextToInnermostPixelLayerOutliers',
                'numberOfNextToInnermostPixelLayerSharedHits',
                'numberOfNextToInnermostPixelLayerSplitHits',
                'numberOfNextToInnermostPixelLayerEndcapHits',
                'numberOfNextToInnermostPixelLayerEndcapOutliers',
                'numberOfNextToInnermostPixelLayerSharedEndcapHits',
                'numberOfNextToInnermostPixelLayerSplitEndcapHits',
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
                'TRTTrackOccupancy',
                'numberOfContribPixelBarrelFlatLayers',
                'numberOfContribPixelBarrelInclinedLayers',
                'numberOfContribPixelEndcap',
                'numberOfPixelBarrelFlatHits',
                'numberOfPixelBarrelInclinedHits',
                'numberOfPixelEndcapHits',
                'numberOfPixelBarrelFlatHoles',
                'numberOfPixelBarrelInclinedHoles',
                'numberOfPixelEndcapHoles',
                'numberOfTrackSummaryTypes',
            ],
        },
    ],
    'floatSummaryValue': [
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
                'numberOfInnermostPixelLayerEndcapHits',
                'numberOfInnermostPixelLayerEndcapOutliers',
                'numberOfInnermostPixelLayerSharedEndcapHits',
                'numberOfInnermostPixelLayerSplitEndcapHits',
                'expectNextToInnermostPixelLayerHit',
                'numberOfNextToInnermostPixelLayerHits',
                'numberOfNextToInnermostPixelLayerOutliers',
                'numberOfNextToInnermostPixelLayerSharedHits',
                'numberOfNextToInnermostPixelLayerSplitHits',
                'numberOfNextToInnermostPixelLayerEndcapHits',
                'numberOfNextToInnermostPixelLayerEndcapOutliers',
                'numberOfNextToInnermostPixelLayerSharedEndcapHits',
                'numberOfNextToInnermostPixelLayerSplitEndcapHits',
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
                'TRTTrackOccupancy',
                'numberOfContribPixelBarrelFlatLayers',
                'numberOfContribPixelBarrelInclinedLayers',
                'numberOfContribPixelEndcap',
                'numberOfPixelBarrelFlatHits',
                'numberOfPixelBarrelInclinedHits',
                'numberOfPixelEndcapHits',
                'numberOfPixelBarrelFlatHoles',
                'numberOfPixelBarrelInclinedHoles',
                'numberOfPixelEndcapHoles',
                'numberOfTrackSummaryTypes',
            ],
        },
    ],
    'uint8SummaryValue': [
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
                'numberOfInnermostPixelLayerEndcapHits',
                'numberOfInnermostPixelLayerEndcapOutliers',
                'numberOfInnermostPixelLayerSharedEndcapHits',
                'numberOfInnermostPixelLayerSplitEndcapHits',
                'expectNextToInnermostPixelLayerHit',
                'numberOfNextToInnermostPixelLayerHits',
                'numberOfNextToInnermostPixelLayerOutliers',
                'numberOfNextToInnermostPixelLayerSharedHits',
                'numberOfNextToInnermostPixelLayerSplitHits',
                'numberOfNextToInnermostPixelLayerEndcapHits',
                'numberOfNextToInnermostPixelLayerEndcapOutliers',
                'numberOfNextToInnermostPixelLayerSharedEndcapHits',
                'numberOfNextToInnermostPixelLayerSplitEndcapHits',
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
                'TRTTrackOccupancy',
                'numberOfContribPixelBarrelFlatLayers',
                'numberOfContribPixelBarrelInclinedLayers',
                'numberOfContribPixelEndcap',
                'numberOfPixelBarrelFlatHits',
                'numberOfPixelBarrelInclinedHits',
                'numberOfPixelEndcapHits',
                'numberOfPixelBarrelFlatHoles',
                'numberOfPixelBarrelInclinedHoles',
                'numberOfPixelEndcapHoles',
                'numberOfTrackSummaryTypes',
            ],
        },
    ],
    'uint8MuonSummaryValue': [
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
                'MMHits',
                'MMHoles',
                'cscEtaHits',
                'cscUnspoiledEtaHits',
                'numberOfMuonSummaryTypes',
            ],
        },
    ],
    'parameter': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.Muon_v1',
            'name': 'ParamDef',
            'values': [
                'spectrometerFieldIntegral',
                'scatteringCurvatureSignificance',
                'scatteringNeighbourSignificance',
                'momentumBalanceSignificance',
                'segmentDeltaEta',
                'segmentDeltaPhi',
                'segmentChi2OverDoF',
                't0',
                'beta',
                'annBarrel',
                'annEndCap',
                'innAngle',
                'midAngle',
                'msInnerMatchChi2',
                'msInnerMatchDOF',
                'msOuterMatchChi2',
                'msOuterMatchDOF',
                'meanDeltaADCCountsMDT',
                'CaloLRLikelihood',
                'CaloMuonIDTag',
                'FSR_CandidateEnergy',
                'EnergyLoss',
                'ParamEnergyLoss',
                'MeasEnergyLoss',
                'EnergyLossSigma',
                'ParamEnergyLossSigmaPlus',
                'ParamEnergyLossSigmaMinus',
                'MeasEnergyLossSigma',
                'CaloMuonScore',
            ],
        },
    ],
    'floatParameter': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.Muon_v1',
            'name': 'ParamDef',
            'values': [
                'spectrometerFieldIntegral',
                'scatteringCurvatureSignificance',
                'scatteringNeighbourSignificance',
                'momentumBalanceSignificance',
                'segmentDeltaEta',
                'segmentDeltaPhi',
                'segmentChi2OverDoF',
                't0',
                'beta',
                'annBarrel',
                'annEndCap',
                'innAngle',
                'midAngle',
                'msInnerMatchChi2',
                'msInnerMatchDOF',
                'msOuterMatchChi2',
                'msOuterMatchDOF',
                'meanDeltaADCCountsMDT',
                'CaloLRLikelihood',
                'CaloMuonIDTag',
                'FSR_CandidateEnergy',
                'EnergyLoss',
                'ParamEnergyLoss',
                'MeasEnergyLoss',
                'EnergyLossSigma',
                'ParamEnergyLossSigmaPlus',
                'ParamEnergyLossSigmaMinus',
                'MeasEnergyLossSigma',
                'CaloMuonScore',
            ],
        },
    ],
    'intParameter': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.Muon_v1',
            'name': 'ParamDef',
            'values': [
                'spectrometerFieldIntegral',
                'scatteringCurvatureSignificance',
                'scatteringNeighbourSignificance',
                'momentumBalanceSignificance',
                'segmentDeltaEta',
                'segmentDeltaPhi',
                'segmentChi2OverDoF',
                't0',
                'beta',
                'annBarrel',
                'annEndCap',
                'innAngle',
                'midAngle',
                'msInnerMatchChi2',
                'msInnerMatchDOF',
                'msOuterMatchChi2',
                'msOuterMatchDOF',
                'meanDeltaADCCountsMDT',
                'CaloLRLikelihood',
                'CaloMuonIDTag',
                'FSR_CandidateEnergy',
                'EnergyLoss',
                'ParamEnergyLoss',
                'MeasEnergyLoss',
                'EnergyLossSigma',
                'ParamEnergyLossSigmaPlus',
                'ParamEnergyLossSigmaMinus',
                'MeasEnergyLossSigma',
                'CaloMuonScore',
            ],
        },
    ],
    'quality': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.Muon_v1',
            'name': 'Quality',
            'values': [
                'Tight',
                'Medium',
                'Loose',
                'VeryLoose',
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
                'ptvarcone20_Nonprompt_All_MaxWeightTTVA_pt500',
                'ptvarcone30_Nonprompt_All_MaxWeightTTVA_pt500',
                'ptvarcone40_Nonprompt_All_MaxWeightTTVA_pt500',
                'ptvarcone20_Nonprompt_All_MaxWeightTTVA_pt1000',
                'ptvarcone30_Nonprompt_All_MaxWeightTTVA_pt1000',
                'ptvarcone40_Nonprompt_All_MaxWeightTTVA_pt1000',
                'ptcone20_Nonprompt_All_MaxWeightTTVA_pt500',
                'ptcone30_Nonprompt_All_MaxWeightTTVA_pt500',
                'ptcone40_Nonprompt_All_MaxWeightTTVA_pt500',
                'ptcone20_Nonprompt_All_MaxWeightTTVA_pt1000',
                'ptcone30_Nonprompt_All_MaxWeightTTVA_pt1000',
                'ptcone40_Nonprompt_All_MaxWeightTTVA_pt1000',
                'ptvarcone20_Nonprompt_All_MaxWeightTTVALooseCone_pt500',
                'ptvarcone30_Nonprompt_All_MaxWeightTTVALooseCone_pt500',
                'ptvarcone40_Nonprompt_All_MaxWeightTTVALooseCone_pt500',
                'ptvarcone20_Nonprompt_All_MaxWeightTTVALooseCone_pt1000',
                'ptvarcone30_Nonprompt_All_MaxWeightTTVALooseCone_pt1000',
                'ptvarcone40_Nonprompt_All_MaxWeightTTVALooseCone_pt1000',
                'ptcone20_Nonprompt_All_MaxWeightTTVALooseCone_pt500',
                'ptcone30_Nonprompt_All_MaxWeightTTVALooseCone_pt500',
                'ptcone40_Nonprompt_All_MaxWeightTTVALooseCone_pt500',
                'ptcone20_Nonprompt_All_MaxWeightTTVALooseCone_pt1000',
                'ptcone30_Nonprompt_All_MaxWeightTTVALooseCone_pt1000',
                'ptcone40_Nonprompt_All_MaxWeightTTVALooseCone_pt1000',
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
                'ptvarcone_Nonprompt_All_MaxWeightTTVA_pt500',
                'ptvarcone_Nonprompt_All_MaxWeightTTVA_pt1000',
                'ptcone_Nonprompt_All_MaxWeightTTVA_pt500',
                'ptcone_Nonprompt_All_MaxWeightTTVA_pt1000',
                'ptvarcone_Nonprompt_All_MaxWeightTTVALooseCone_pt500',
                'ptvarcone_Nonprompt_All_MaxWeightTTVALooseCone_pt1000',
                'ptcone_Nonprompt_All_MaxWeightTTVALooseCone_pt500',
                'ptcone_Nonprompt_All_MaxWeightTTVALooseCone_pt1000',
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
                'ptvarcone_Nonprompt_All_MaxWeightTTVA_pt500',
                'ptvarcone_Nonprompt_All_MaxWeightTTVA_pt1000',
                'ptcone_Nonprompt_All_MaxWeightTTVA_pt500',
                'ptcone_Nonprompt_All_MaxWeightTTVA_pt1000',
                'ptvarcone_Nonprompt_All_MaxWeightTTVALooseCone_pt500',
                'ptvarcone_Nonprompt_All_MaxWeightTTVALooseCone_pt1000',
                'ptcone_Nonprompt_All_MaxWeightTTVALooseCone_pt500',
                'ptcone_Nonprompt_All_MaxWeightTTVALooseCone_pt1000',
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
                'ptvarcone_Nonprompt_All_MaxWeightTTVA_pt500',
                'ptvarcone_Nonprompt_All_MaxWeightTTVA_pt1000',
                'ptcone_Nonprompt_All_MaxWeightTTVA_pt500',
                'ptcone_Nonprompt_All_MaxWeightTTVA_pt1000',
                'ptvarcone_Nonprompt_All_MaxWeightTTVALooseCone_pt500',
                'ptvarcone_Nonprompt_All_MaxWeightTTVALooseCone_pt1000',
                'ptcone_Nonprompt_All_MaxWeightTTVALooseCone_pt500',
                'ptcone_Nonprompt_All_MaxWeightTTVALooseCone_pt1000',
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
                'ptvarcone_Nonprompt_All_MaxWeightTTVA_pt500',
                'ptvarcone_Nonprompt_All_MaxWeightTTVA_pt1000',
                'ptcone_Nonprompt_All_MaxWeightTTVA_pt500',
                'ptcone_Nonprompt_All_MaxWeightTTVA_pt1000',
                'ptvarcone_Nonprompt_All_MaxWeightTTVALooseCone_pt500',
                'ptvarcone_Nonprompt_All_MaxWeightTTVALooseCone_pt1000',
                'ptcone_Nonprompt_All_MaxWeightTTVALooseCone_pt500',
                'ptcone_Nonprompt_All_MaxWeightTTVALooseCone_pt1000',
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
                'ptvarcone_Nonprompt_All_MaxWeightTTVA_pt500',
                'ptvarcone_Nonprompt_All_MaxWeightTTVA_pt1000',
                'ptcone_Nonprompt_All_MaxWeightTTVA_pt500',
                'ptcone_Nonprompt_All_MaxWeightTTVA_pt1000',
                'ptvarcone_Nonprompt_All_MaxWeightTTVALooseCone_pt500',
                'ptvarcone_Nonprompt_All_MaxWeightTTVALooseCone_pt1000',
                'ptcone_Nonprompt_All_MaxWeightTTVALooseCone_pt500',
                'ptcone_Nonprompt_All_MaxWeightTTVALooseCone_pt1000',
                'numIsolationFlavours',
            ],
        },
    ],
    'trackParticleLink': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.Muon_v1',
            'name': 'TrackParticleType',
            'values': [
                'Primary',
                'InnerDetectorTrackParticle',
                'MuonSpectrometerTrackParticle',
                'CombinedTrackParticle',
                'ExtrapolatedMuonSpectrometerTrackParticle',
                'MSOnlyExtrapolatedMuonSpectrometerTrackParticle',
            ],
        },
    ],
    'trackParticle': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.Muon_v1',
            'name': 'TrackParticleType',
            'values': [
                'Primary',
                'InnerDetectorTrackParticle',
                'MuonSpectrometerTrackParticle',
                'CombinedTrackParticle',
                'ExtrapolatedMuonSpectrometerTrackParticle',
                'MSOnlyExtrapolatedMuonSpectrometerTrackParticle',
            ],
        },
    ],
    'energyLossType': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.Muon_v1',
            'name': 'EnergyLossType',
            'values': [
                'Parametrized',
                'NotIsolated',
                'MOP',
                'Tail',
                'FSRcandidate',
            ],
        },
    ],      
}

_defined_enums = {
    'Author':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.Muon_v1',
            'name': 'Author',
            'values': [
                'unknown',
                'MuidCo',
                'STACO',
                'MuTag',
                'MuTagIMO',
                'MuidSA',
                'MuGirl',
                'MuGirlLowBeta',
                'CaloTag',
                'CaloLikelihood',
                'CaloScore',
                'ExtrapolateMuonToIP',
                'Commissioning',
                'NumberOfMuonAuthors',
            ],
        },
    'MuonType':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.Muon_v1',
            'name': 'MuonType',
            'values': [
                'Combined',
                'MuonStandAlone',
                'SegmentTagged',
                'CaloTagged',
                'SiliconAssociatedForwardMuon',
            ],
        },
    'ParamDef':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.Muon_v1',
            'name': 'ParamDef',
            'values': [
                'spectrometerFieldIntegral',
                'scatteringCurvatureSignificance',
                'scatteringNeighbourSignificance',
                'momentumBalanceSignificance',
                'segmentDeltaEta',
                'segmentDeltaPhi',
                'segmentChi2OverDoF',
                't0',
                'beta',
                'annBarrel',
                'annEndCap',
                'innAngle',
                'midAngle',
                'msInnerMatchChi2',
                'msInnerMatchDOF',
                'msOuterMatchChi2',
                'msOuterMatchDOF',
                'meanDeltaADCCountsMDT',
                'CaloLRLikelihood',
                'CaloMuonIDTag',
                'FSR_CandidateEnergy',
                'EnergyLoss',
                'ParamEnergyLoss',
                'MeasEnergyLoss',
                'EnergyLossSigma',
                'ParamEnergyLossSigmaPlus',
                'ParamEnergyLossSigmaMinus',
                'MeasEnergyLossSigma',
                'CaloMuonScore',
            ],
        },
    'TrackParticleType':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.Muon_v1',
            'name': 'TrackParticleType',
            'values': [
                'Primary',
                'InnerDetectorTrackParticle',
                'MuonSpectrometerTrackParticle',
                'CombinedTrackParticle',
                'ExtrapolatedMuonSpectrometerTrackParticle',
                'MSOnlyExtrapolatedMuonSpectrometerTrackParticle',
            ],
        },
    'EnergyLossType':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.Muon_v1',
            'name': 'EnergyLossType',
            'values': [
                'Parametrized',
                'NotIsolated',
                'MOP',
                'Tail',
                'FSRcandidate',
            ],
        },
    'Quality':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.Muon_v1',
            'name': 'Quality',
            'values': [
                'Tight',
                'Medium',
                'Loose',
                'VeryLoose',
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
            'name': 'xAODMuon/versions/Muon_v1.h',
            'body_includes': ["xAODMuon/versions/Muon_v1.h"],
        })


        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODMuon',
            'link_libraries': ["xAODMuon"],
        })

        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class Muon_v1:
    "A class"

    class Author(Enum):
        unknown = 0
        MuidCo = 1
        STACO = 2
        MuTag = 3
        MuTagIMO = 4
        MuidSA = 5
        MuGirl = 6
        MuGirlLowBeta = 7
        CaloTag = 8
        CaloLikelihood = 9
        CaloScore = 10
        ExtrapolateMuonToIP = 11
        Commissioning = 12
        NumberOfMuonAuthors = 13

    class MuonType(Enum):
        Combined = 0
        MuonStandAlone = 1
        SegmentTagged = 2
        CaloTagged = 3
        SiliconAssociatedForwardMuon = 4

    class ParamDef(Enum):
        spectrometerFieldIntegral = 0
        scatteringCurvatureSignificance = 1
        scatteringNeighbourSignificance = 2
        momentumBalanceSignificance = 3
        segmentDeltaEta = 4
        segmentDeltaPhi = 5
        segmentChi2OverDoF = 6
        t0 = 7
        beta = 8
        annBarrel = 9
        annEndCap = 10
        innAngle = 11
        midAngle = 12
        msInnerMatchChi2 = 13
        msInnerMatchDOF = 14
        msOuterMatchChi2 = 15
        msOuterMatchDOF = 16
        meanDeltaADCCountsMDT = 17
        CaloLRLikelihood = 18
        CaloMuonIDTag = 19
        FSR_CandidateEnergy = 20
        EnergyLoss = 21
        ParamEnergyLoss = 22
        MeasEnergyLoss = 23
        EnergyLossSigma = 24
        ParamEnergyLossSigmaPlus = 25
        ParamEnergyLossSigmaMinus = 26
        MeasEnergyLossSigma = 27
        CaloMuonScore = 28

    class TrackParticleType(Enum):
        Primary = 0
        InnerDetectorTrackParticle = 1
        MuonSpectrometerTrackParticle = 2
        CombinedTrackParticle = 3
        ExtrapolatedMuonSpectrometerTrackParticle = 4
        MSOnlyExtrapolatedMuonSpectrometerTrackParticle = 5

    class EnergyLossType(Enum):
        Parametrized = 0
        NotIsolated = 1
        MOP = 2
        Tail = 3
        FSRcandidate = 4

    class Quality(Enum):
        Tight = 0
        Medium = 1
        Loose = 2
        VeryLoose = 3


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

    def p4(self) -> func_adl_servicex_xaodr25.tlorentzvector.TLorentzVector:
        "A method"
        ...

    def type(self) -> func_adl_servicex_xaodr25.xaodtype.xAODType.ObjectType:
        "A method"
        ...

    def charge(self) -> float:
        "A method"
        ...

    def author(self) -> func_adl_servicex_xaodr25.xAOD.muon_v1.Muon_v1.Author:
        "A method"
        ...

    def isAuthor(self, author: func_adl_servicex_xaodr25.xAOD.muon_v1.Muon_v1.Author) -> bool:
        "A method"
        ...

    def allAuthors(self) -> int:
        "A method"
        ...

    def muonType(self) -> func_adl_servicex_xaodr25.xAOD.muon_v1.Muon_v1.MuonType:
        "A method"
        ...

    def summaryValue(self, value: int, information: func_adl_servicex_xaodr25.xaod.xAOD.SummaryType) -> bool:
        "A method"
        ...

    def floatSummaryValue(self, information: func_adl_servicex_xaodr25.xaod.xAOD.SummaryType) -> float:
        "A method"
        ...

    def uint8SummaryValue(self, information: func_adl_servicex_xaodr25.xaod.xAOD.SummaryType) -> int:
        "A method"
        ...

    def uint8MuonSummaryValue(self, information: func_adl_servicex_xaodr25.xaod.xAOD.MuonSummaryType) -> float:
        "A method"
        ...

    def parameter(self, value: float, parameter: func_adl_servicex_xaodr25.xAOD.muon_v1.Muon_v1.ParamDef) -> bool:
        "A method"
        ...

    def floatParameter(self, parameter: func_adl_servicex_xaodr25.xAOD.muon_v1.Muon_v1.ParamDef) -> float:
        "A method"
        ...

    def intParameter(self, parameter: func_adl_servicex_xaodr25.xAOD.muon_v1.Muon_v1.ParamDef) -> int:
        "A method"
        ...

    def quality(self) -> func_adl_servicex_xaodr25.xAOD.muon_v1.Muon_v1.Quality:
        "A method"
        ...

    def passesIDCuts(self) -> bool:
        "A method"
        ...

    def isolation(self, value: float, information: func_adl_servicex_xaodr25.xAOD.iso.Iso.IsolationType) -> bool:
        "A method"
        ...

    def isolationCaloCorrection(self, value: float, flavour: func_adl_servicex_xaodr25.xAOD.iso.Iso.IsolationFlavour, type: func_adl_servicex_xaodr25.xAOD.iso.Iso.IsolationCaloCorrection, param: func_adl_servicex_xaodr25.xAOD.iso.Iso.IsolationCorrectionParameter) -> bool:
        "A method"
        ...

    def setIsolationCaloCorrection(self, value: float, flavour: func_adl_servicex_xaodr25.xAOD.iso.Iso.IsolationFlavour, type: func_adl_servicex_xaodr25.xAOD.iso.Iso.IsolationCaloCorrection, param: func_adl_servicex_xaodr25.xAOD.iso.Iso.IsolationCorrectionParameter) -> bool:
        "A method"
        ...

    def isolationTrackCorrection(self, value: float, flavour: func_adl_servicex_xaodr25.xAOD.iso.Iso.IsolationFlavour, type: func_adl_servicex_xaodr25.xAOD.iso.Iso.IsolationTrackCorrection) -> bool:
        "A method"
        ...

    def setIsolationTrackCorrection(self, value: float, flavour: func_adl_servicex_xaodr25.xAOD.iso.Iso.IsolationFlavour, type: func_adl_servicex_xaodr25.xAOD.iso.Iso.IsolationTrackCorrection) -> bool:
        "A method"
        ...

    def setIsolationCorrectionBitset(self, value: int, flavour: func_adl_servicex_xaodr25.xAOD.iso.Iso.IsolationFlavour) -> bool:
        "A method"
        ...

    def primaryTrackParticleLink(self) -> func_adl_servicex_xaodr25.elementlink_datavector_xaod_trackparticle_v1__.ElementLink_DataVector_xAOD_TrackParticle_v1__:
        "A method"
        ...

    def primaryTrackParticle(self) -> func_adl_servicex_xaodr25.xAOD.trackparticle_v1.TrackParticle_v1:
        "A method"
        ...

    def inDetTrackParticleLink(self) -> func_adl_servicex_xaodr25.elementlink_datavector_xaod_trackparticle_v1__.ElementLink_DataVector_xAOD_TrackParticle_v1__:
        "A method"
        ...

    def muonSpectrometerTrackParticleLink(self) -> func_adl_servicex_xaodr25.elementlink_datavector_xaod_trackparticle_v1__.ElementLink_DataVector_xAOD_TrackParticle_v1__:
        "A method"
        ...

    def combinedTrackParticleLink(self) -> func_adl_servicex_xaodr25.elementlink_datavector_xaod_trackparticle_v1__.ElementLink_DataVector_xAOD_TrackParticle_v1__:
        "A method"
        ...

    def extrapolatedMuonSpectrometerTrackParticleLink(self) -> func_adl_servicex_xaodr25.elementlink_datavector_xaod_trackparticle_v1__.ElementLink_DataVector_xAOD_TrackParticle_v1__:
        "A method"
        ...

    def msOnlyExtrapolatedMuonSpectrometerTrackParticleLink(self) -> func_adl_servicex_xaodr25.elementlink_datavector_xaod_trackparticle_v1__.ElementLink_DataVector_xAOD_TrackParticle_v1__:
        "A method"
        ...

    def trackParticleLink(self, type: func_adl_servicex_xaodr25.xAOD.muon_v1.Muon_v1.TrackParticleType) -> func_adl_servicex_xaodr25.elementlink_datavector_xaod_trackparticle_v1__.ElementLink_DataVector_xAOD_TrackParticle_v1__:
        "A method"
        ...

    def trackParticle(self, type: func_adl_servicex_xaodr25.xAOD.muon_v1.Muon_v1.TrackParticleType) -> func_adl_servicex_xaodr25.xAOD.trackparticle_v1.TrackParticle_v1:
        "A method"
        ...

    def clusterLink(self) -> func_adl_servicex_xaodr25.elementlink_datavector_xaod_calocluster_v1__.ElementLink_DataVector_xAOD_CaloCluster_v1__:
        "A method"
        ...

    def cluster(self) -> func_adl_servicex_xaodr25.xAOD.calocluster_v1.CaloCluster_v1:
        "A method"
        ...

    def energyLossType(self) -> func_adl_servicex_xaodr25.xAOD.muon_v1.Muon_v1.EnergyLossType:
        "A method"
        ...

    def muonSegmentLinks(self) -> func_adl_servicex_xaodr25.vector_elementlink_datavector_xaod_muonsegment_v1___.vector_ElementLink_DataVector_xAOD_MuonSegment_v1___:
        "A method"
        ...

    def nMuonSegments(self) -> int:
        "A method"
        ...

    def muonSegment(self, i: int) -> func_adl_servicex_xaodr25.xAOD.muonsegment_v1.MuonSegment_v1:
        "A method"
        ...

    def muonSegmentLink(self, i: int) -> func_adl_servicex_xaodr25.elementlink_datavector_xaod_muonsegment_v1__.ElementLink_DataVector_xAOD_MuonSegment_v1__:
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
