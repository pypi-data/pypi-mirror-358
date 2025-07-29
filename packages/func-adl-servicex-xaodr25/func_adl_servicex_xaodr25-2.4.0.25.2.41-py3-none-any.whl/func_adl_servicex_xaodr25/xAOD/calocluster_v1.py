from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr25

_method_map = {
    'pt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'pt',
        'return_type': 'double',
    },
    'eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'eta',
        'return_type': 'double',
    },
    'phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'phi',
        'return_type': 'double',
    },
    'm': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'm',
        'return_type': 'double',
    },
    'e': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'e',
        'return_type': 'double',
    },
    'rapidity': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'rapidity',
        'return_type': 'double',
    },
    'p4': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'p4',
        'return_type': 'TLorentzVector',
    },
    'type': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'type',
        'return_type': 'xAODType::ObjectType',
    },
    'et': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'et',
        'return_type': 'double',
    },
    'eSample': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'eSample',
        'return_type': 'float',
    },
    'etaSample': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'etaSample',
        'return_type': 'float',
    },
    'phiSample': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'phiSample',
        'return_type': 'float',
    },
    'energy_max': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'energy_max',
        'return_type': 'float',
    },
    'etamax': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'etamax',
        'return_type': 'float',
    },
    'phimax': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'phimax',
        'return_type': 'float',
    },
    'etasize': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'etasize',
        'return_type': 'float',
    },
    'phisize': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'phisize',
        'return_type': 'float',
    },
    'numberCellsInSampling': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'numberCellsInSampling',
        'return_type': 'int',
    },
    'numberCells': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'numberCells',
        'return_type': 'int',
    },
    'energyBE': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'energyBE',
        'return_type': 'float',
    },
    'etaBE': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'etaBE',
        'return_type': 'float',
    },
    'phiBE': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'phiBE',
        'return_type': 'float',
    },
    'setEnergy': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'setEnergy',
        'return_type': 'bool',
    },
    'setEta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'setEta',
        'return_type': 'bool',
    },
    'setPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'setPhi',
        'return_type': 'bool',
    },
    'setEmax': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'setEmax',
        'return_type': 'bool',
    },
    'setEtamax': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'setEtamax',
        'return_type': 'bool',
    },
    'setPhimax': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'setPhimax',
        'return_type': 'bool',
    },
    'setEtasize': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'setEtasize',
        'return_type': 'bool',
    },
    'setPhisize': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'setPhisize',
        'return_type': 'bool',
    },
    'retrieveMoment': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'retrieveMoment',
        'return_type': 'bool',
    },
    'getMomentValue': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'getMomentValue',
        'return_type': 'double',
    },
    'eta0': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'eta0',
        'return_type': 'float',
    },
    'phi0': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'phi0',
        'return_type': 'float',
    },
    'time': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'time',
        'return_type': 'float',
    },
    'secondTime': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'secondTime',
        'return_type': 'float',
    },
    'samplingPattern': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'samplingPattern',
        'return_type': 'unsigned int',
    },
    'nSamples': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'nSamples',
        'return_type': 'unsigned int',
    },
    'hasSampling': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'hasSampling',
        'return_type': 'bool',
    },
    'clusterSize': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'clusterSize',
        'return_type': 'xAOD::CaloCluster_v1::ClusterSize',
    },
    'inBarrel': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'inBarrel',
        'return_type': 'bool',
    },
    'inEndcap': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'inEndcap',
        'return_type': 'bool',
    },
    'rawE': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'rawE',
        'return_type': 'float',
    },
    'rawEta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'rawEta',
        'return_type': 'float',
    },
    'rawPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'rawPhi',
        'return_type': 'float',
    },
    'rawM': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'rawM',
        'return_type': 'float',
    },
    'altE': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'altE',
        'return_type': 'float',
    },
    'altEta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'altEta',
        'return_type': 'float',
    },
    'altPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'altPhi',
        'return_type': 'float',
    },
    'altM': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'altM',
        'return_type': 'float',
    },
    'calE': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'calE',
        'return_type': 'float',
    },
    'calEta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'calEta',
        'return_type': 'float',
    },
    'calPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'calPhi',
        'return_type': 'float',
    },
    'calM': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'calM',
        'return_type': 'float',
    },
    'setSignalState': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'setSignalState',
        'return_type': 'bool',
    },
    'signalState': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'signalState',
        'return_type': 'xAOD::CaloCluster_v1::State',
    },
    'getClusterEtaSize': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'getClusterEtaSize',
        'return_type': 'unsigned int',
    },
    'getClusterPhiSize': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'getClusterPhiSize',
        'return_type': 'unsigned int',
    },
    'badChannelList': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'badChannelList',
        'return_type_element': 'xAOD::CaloClusterBadChannelData_v1',
        'return_type_collection': 'const vector<xAOD::CaloClusterBadChannelData_v1>',
    },
    'getSisterCluster': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'getSisterCluster',
        'return_type': 'const xAOD::CaloCluster_v1 *',
    },
    'getSisterClusterLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'getSisterClusterLink',
        'return_type': 'const ElementLink<DataVector<xAOD::CaloCluster_v1>>',
    },
    'setSisterClusterLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'setSisterClusterLink',
        'return_type': 'bool',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'trackIndices',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloCluster_v1',
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
    'eSample': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'CaloSampling',
            'name': 'CaloSample',
            'values': [
                'PreSamplerB',
                'EMB1',
                'EMB2',
                'EMB3',
                'PreSamplerE',
                'EME1',
                'EME2',
                'EME3',
                'HEC0',
                'HEC1',
                'HEC2',
                'HEC3',
                'TileBar0',
                'TileBar1',
                'TileBar2',
                'TileGap1',
                'TileGap2',
                'TileGap3',
                'TileExt0',
                'TileExt1',
                'TileExt2',
                'FCAL0',
                'FCAL1',
                'FCAL2',
                'MINIFCAL0',
                'MINIFCAL1',
                'MINIFCAL2',
                'MINIFCAL3',
                'Unknown',
            ],
        },
    ],
    'etaSample': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'CaloSampling',
            'name': 'CaloSample',
            'values': [
                'PreSamplerB',
                'EMB1',
                'EMB2',
                'EMB3',
                'PreSamplerE',
                'EME1',
                'EME2',
                'EME3',
                'HEC0',
                'HEC1',
                'HEC2',
                'HEC3',
                'TileBar0',
                'TileBar1',
                'TileBar2',
                'TileGap1',
                'TileGap2',
                'TileGap3',
                'TileExt0',
                'TileExt1',
                'TileExt2',
                'FCAL0',
                'FCAL1',
                'FCAL2',
                'MINIFCAL0',
                'MINIFCAL1',
                'MINIFCAL2',
                'MINIFCAL3',
                'Unknown',
            ],
        },
    ],
    'phiSample': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'CaloSampling',
            'name': 'CaloSample',
            'values': [
                'PreSamplerB',
                'EMB1',
                'EMB2',
                'EMB3',
                'PreSamplerE',
                'EME1',
                'EME2',
                'EME3',
                'HEC0',
                'HEC1',
                'HEC2',
                'HEC3',
                'TileBar0',
                'TileBar1',
                'TileBar2',
                'TileGap1',
                'TileGap2',
                'TileGap3',
                'TileExt0',
                'TileExt1',
                'TileExt2',
                'FCAL0',
                'FCAL1',
                'FCAL2',
                'MINIFCAL0',
                'MINIFCAL1',
                'MINIFCAL2',
                'MINIFCAL3',
                'Unknown',
            ],
        },
    ],
    'energy_max': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'CaloSampling',
            'name': 'CaloSample',
            'values': [
                'PreSamplerB',
                'EMB1',
                'EMB2',
                'EMB3',
                'PreSamplerE',
                'EME1',
                'EME2',
                'EME3',
                'HEC0',
                'HEC1',
                'HEC2',
                'HEC3',
                'TileBar0',
                'TileBar1',
                'TileBar2',
                'TileGap1',
                'TileGap2',
                'TileGap3',
                'TileExt0',
                'TileExt1',
                'TileExt2',
                'FCAL0',
                'FCAL1',
                'FCAL2',
                'MINIFCAL0',
                'MINIFCAL1',
                'MINIFCAL2',
                'MINIFCAL3',
                'Unknown',
            ],
        },
    ],
    'etamax': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'CaloSampling',
            'name': 'CaloSample',
            'values': [
                'PreSamplerB',
                'EMB1',
                'EMB2',
                'EMB3',
                'PreSamplerE',
                'EME1',
                'EME2',
                'EME3',
                'HEC0',
                'HEC1',
                'HEC2',
                'HEC3',
                'TileBar0',
                'TileBar1',
                'TileBar2',
                'TileGap1',
                'TileGap2',
                'TileGap3',
                'TileExt0',
                'TileExt1',
                'TileExt2',
                'FCAL0',
                'FCAL1',
                'FCAL2',
                'MINIFCAL0',
                'MINIFCAL1',
                'MINIFCAL2',
                'MINIFCAL3',
                'Unknown',
            ],
        },
    ],
    'phimax': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'CaloSampling',
            'name': 'CaloSample',
            'values': [
                'PreSamplerB',
                'EMB1',
                'EMB2',
                'EMB3',
                'PreSamplerE',
                'EME1',
                'EME2',
                'EME3',
                'HEC0',
                'HEC1',
                'HEC2',
                'HEC3',
                'TileBar0',
                'TileBar1',
                'TileBar2',
                'TileGap1',
                'TileGap2',
                'TileGap3',
                'TileExt0',
                'TileExt1',
                'TileExt2',
                'FCAL0',
                'FCAL1',
                'FCAL2',
                'MINIFCAL0',
                'MINIFCAL1',
                'MINIFCAL2',
                'MINIFCAL3',
                'Unknown',
            ],
        },
    ],
    'etasize': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'CaloSampling',
            'name': 'CaloSample',
            'values': [
                'PreSamplerB',
                'EMB1',
                'EMB2',
                'EMB3',
                'PreSamplerE',
                'EME1',
                'EME2',
                'EME3',
                'HEC0',
                'HEC1',
                'HEC2',
                'HEC3',
                'TileBar0',
                'TileBar1',
                'TileBar2',
                'TileGap1',
                'TileGap2',
                'TileGap3',
                'TileExt0',
                'TileExt1',
                'TileExt2',
                'FCAL0',
                'FCAL1',
                'FCAL2',
                'MINIFCAL0',
                'MINIFCAL1',
                'MINIFCAL2',
                'MINIFCAL3',
                'Unknown',
            ],
        },
    ],
    'phisize': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'CaloSampling',
            'name': 'CaloSample',
            'values': [
                'PreSamplerB',
                'EMB1',
                'EMB2',
                'EMB3',
                'PreSamplerE',
                'EME1',
                'EME2',
                'EME3',
                'HEC0',
                'HEC1',
                'HEC2',
                'HEC3',
                'TileBar0',
                'TileBar1',
                'TileBar2',
                'TileGap1',
                'TileGap2',
                'TileGap3',
                'TileExt0',
                'TileExt1',
                'TileExt2',
                'FCAL0',
                'FCAL1',
                'FCAL2',
                'MINIFCAL0',
                'MINIFCAL1',
                'MINIFCAL2',
                'MINIFCAL3',
                'Unknown',
            ],
        },
    ],
    'numberCellsInSampling': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'CaloSampling',
            'name': 'CaloSample',
            'values': [
                'PreSamplerB',
                'EMB1',
                'EMB2',
                'EMB3',
                'PreSamplerE',
                'EME1',
                'EME2',
                'EME3',
                'HEC0',
                'HEC1',
                'HEC2',
                'HEC3',
                'TileBar0',
                'TileBar1',
                'TileBar2',
                'TileGap1',
                'TileGap2',
                'TileGap3',
                'TileExt0',
                'TileExt1',
                'TileExt2',
                'FCAL0',
                'FCAL1',
                'FCAL2',
                'MINIFCAL0',
                'MINIFCAL1',
                'MINIFCAL2',
                'MINIFCAL3',
                'Unknown',
            ],
        },
    ],
    'setEnergy': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'CaloSampling',
            'name': 'CaloSample',
            'values': [
                'PreSamplerB',
                'EMB1',
                'EMB2',
                'EMB3',
                'PreSamplerE',
                'EME1',
                'EME2',
                'EME3',
                'HEC0',
                'HEC1',
                'HEC2',
                'HEC3',
                'TileBar0',
                'TileBar1',
                'TileBar2',
                'TileGap1',
                'TileGap2',
                'TileGap3',
                'TileExt0',
                'TileExt1',
                'TileExt2',
                'FCAL0',
                'FCAL1',
                'FCAL2',
                'MINIFCAL0',
                'MINIFCAL1',
                'MINIFCAL2',
                'MINIFCAL3',
                'Unknown',
            ],
        },
    ],
    'setEta': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'CaloSampling',
            'name': 'CaloSample',
            'values': [
                'PreSamplerB',
                'EMB1',
                'EMB2',
                'EMB3',
                'PreSamplerE',
                'EME1',
                'EME2',
                'EME3',
                'HEC0',
                'HEC1',
                'HEC2',
                'HEC3',
                'TileBar0',
                'TileBar1',
                'TileBar2',
                'TileGap1',
                'TileGap2',
                'TileGap3',
                'TileExt0',
                'TileExt1',
                'TileExt2',
                'FCAL0',
                'FCAL1',
                'FCAL2',
                'MINIFCAL0',
                'MINIFCAL1',
                'MINIFCAL2',
                'MINIFCAL3',
                'Unknown',
            ],
        },
    ],
    'setPhi': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'CaloSampling',
            'name': 'CaloSample',
            'values': [
                'PreSamplerB',
                'EMB1',
                'EMB2',
                'EMB3',
                'PreSamplerE',
                'EME1',
                'EME2',
                'EME3',
                'HEC0',
                'HEC1',
                'HEC2',
                'HEC3',
                'TileBar0',
                'TileBar1',
                'TileBar2',
                'TileGap1',
                'TileGap2',
                'TileGap3',
                'TileExt0',
                'TileExt1',
                'TileExt2',
                'FCAL0',
                'FCAL1',
                'FCAL2',
                'MINIFCAL0',
                'MINIFCAL1',
                'MINIFCAL2',
                'MINIFCAL3',
                'Unknown',
            ],
        },
    ],
    'setEmax': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'CaloSampling',
            'name': 'CaloSample',
            'values': [
                'PreSamplerB',
                'EMB1',
                'EMB2',
                'EMB3',
                'PreSamplerE',
                'EME1',
                'EME2',
                'EME3',
                'HEC0',
                'HEC1',
                'HEC2',
                'HEC3',
                'TileBar0',
                'TileBar1',
                'TileBar2',
                'TileGap1',
                'TileGap2',
                'TileGap3',
                'TileExt0',
                'TileExt1',
                'TileExt2',
                'FCAL0',
                'FCAL1',
                'FCAL2',
                'MINIFCAL0',
                'MINIFCAL1',
                'MINIFCAL2',
                'MINIFCAL3',
                'Unknown',
            ],
        },
    ],
    'setEtamax': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'CaloSampling',
            'name': 'CaloSample',
            'values': [
                'PreSamplerB',
                'EMB1',
                'EMB2',
                'EMB3',
                'PreSamplerE',
                'EME1',
                'EME2',
                'EME3',
                'HEC0',
                'HEC1',
                'HEC2',
                'HEC3',
                'TileBar0',
                'TileBar1',
                'TileBar2',
                'TileGap1',
                'TileGap2',
                'TileGap3',
                'TileExt0',
                'TileExt1',
                'TileExt2',
                'FCAL0',
                'FCAL1',
                'FCAL2',
                'MINIFCAL0',
                'MINIFCAL1',
                'MINIFCAL2',
                'MINIFCAL3',
                'Unknown',
            ],
        },
    ],
    'setPhimax': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'CaloSampling',
            'name': 'CaloSample',
            'values': [
                'PreSamplerB',
                'EMB1',
                'EMB2',
                'EMB3',
                'PreSamplerE',
                'EME1',
                'EME2',
                'EME3',
                'HEC0',
                'HEC1',
                'HEC2',
                'HEC3',
                'TileBar0',
                'TileBar1',
                'TileBar2',
                'TileGap1',
                'TileGap2',
                'TileGap3',
                'TileExt0',
                'TileExt1',
                'TileExt2',
                'FCAL0',
                'FCAL1',
                'FCAL2',
                'MINIFCAL0',
                'MINIFCAL1',
                'MINIFCAL2',
                'MINIFCAL3',
                'Unknown',
            ],
        },
    ],
    'setEtasize': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'CaloSampling',
            'name': 'CaloSample',
            'values': [
                'PreSamplerB',
                'EMB1',
                'EMB2',
                'EMB3',
                'PreSamplerE',
                'EME1',
                'EME2',
                'EME3',
                'HEC0',
                'HEC1',
                'HEC2',
                'HEC3',
                'TileBar0',
                'TileBar1',
                'TileBar2',
                'TileGap1',
                'TileGap2',
                'TileGap3',
                'TileExt0',
                'TileExt1',
                'TileExt2',
                'FCAL0',
                'FCAL1',
                'FCAL2',
                'MINIFCAL0',
                'MINIFCAL1',
                'MINIFCAL2',
                'MINIFCAL3',
                'Unknown',
            ],
        },
    ],
    'setPhisize': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'CaloSampling',
            'name': 'CaloSample',
            'values': [
                'PreSamplerB',
                'EMB1',
                'EMB2',
                'EMB3',
                'PreSamplerE',
                'EME1',
                'EME2',
                'EME3',
                'HEC0',
                'HEC1',
                'HEC2',
                'HEC3',
                'TileBar0',
                'TileBar1',
                'TileBar2',
                'TileGap1',
                'TileGap2',
                'TileGap3',
                'TileExt0',
                'TileExt1',
                'TileExt2',
                'FCAL0',
                'FCAL1',
                'FCAL2',
                'MINIFCAL0',
                'MINIFCAL1',
                'MINIFCAL2',
                'MINIFCAL3',
                'Unknown',
            ],
        },
    ],
    'retrieveMoment': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.CaloCluster_v1',
            'name': 'MomentType',
            'values': [
                'FIRST_PHI',
                'FIRST_ETA',
                'SECOND_R',
                'SECOND_LAMBDA',
                'DELTA_PHI',
                'DELTA_THETA',
                'DELTA_ALPHA',
                'CENTER_X',
                'CENTER_Y',
                'CENTER_Z',
                'CENTER_MAG',
                'CENTER_LAMBDA',
                'LATERAL',
                'LONGITUDINAL',
                'ENG_FRAC_EM',
                'ENG_FRAC_MAX',
                'ENG_FRAC_CORE',
                'FIRST_ENG_DENS',
                'SECOND_ENG_DENS',
                'ISOLATION',
                'ENG_BAD_CELLS',
                'N_BAD_CELLS',
                'N_BAD_CELLS_CORR',
                'BAD_CELLS_CORR_E',
                'BADLARQ_FRAC',
                'ENG_POS',
                'SIGNIFICANCE',
                'CELL_SIGNIFICANCE',
                'CELL_SIG_SAMPLING',
                'AVG_LAR_Q',
                'AVG_TILE_Q',
                'ENG_BAD_HV_CELLS',
                'N_BAD_HV_CELLS',
                'PTD',
                'MASS',
                'EM_PROBABILITY',
                'HAD_WEIGHT',
                'OOC_WEIGHT',
                'DM_WEIGHT',
                'TILE_CONFIDENCE_LEVEL',
                'SECOND_TIME',
                'NCELL_SAMPLING',
                'VERTEX_FRACTION',
                'NVERTEX_FRACTION',
                'ETACALOFRAME',
                'PHICALOFRAME',
                'ETA1CALOFRAME',
                'PHI1CALOFRAME',
                'ETA2CALOFRAME',
                'PHI2CALOFRAME',
                'ENG_CALIB_TOT',
                'ENG_CALIB_OUT_L',
                'ENG_CALIB_OUT_M',
                'ENG_CALIB_OUT_T',
                'ENG_CALIB_DEAD_L',
                'ENG_CALIB_DEAD_M',
                'ENG_CALIB_DEAD_T',
                'ENG_CALIB_EMB0',
                'ENG_CALIB_EME0',
                'ENG_CALIB_TILEG3',
                'ENG_CALIB_DEAD_TOT',
                'ENG_CALIB_DEAD_EMB0',
                'ENG_CALIB_DEAD_TILE0',
                'ENG_CALIB_DEAD_TILEG3',
                'ENG_CALIB_DEAD_EME0',
                'ENG_CALIB_DEAD_HEC0',
                'ENG_CALIB_DEAD_FCAL',
                'ENG_CALIB_DEAD_LEAKAGE',
                'ENG_CALIB_DEAD_UNCLASS',
                'ENG_CALIB_FRAC_EM',
                'ENG_CALIB_FRAC_HAD',
                'ENG_CALIB_FRAC_REST',
                'ENERGY_DigiHSTruth',
                'ETA_DigiHSTruth',
                'PHI_DigiHSTruth',
                'TIME_DigiHSTruth',
                'ENERGY_CALIB_DigiHSTruth',
                'ETA_CALIB_DigiHSTruth',
                'PHI_CALIB_DigiHSTruth',
                'TIME_CALIB_DigiHSTruth',
                'FIRST_PHI_DigiHSTruth',
                'FIRST_ETA_DigiHSTruth',
                'SECOND_R_DigiHSTruth',
                'SECOND_LAMBDA_DigiHSTruth',
                'DELTA_PHI_DigiHSTruth',
                'DELTA_THETA_DigiHSTruth',
                'DELTA_ALPHA_DigiHSTruth',
                'CENTER_X_DigiHSTruth',
                'CENTER_Y_DigiHSTruth',
                'CENTER_Z_DigiHSTruth',
                'CENTER_MAG_DigiHSTruth',
                'CENTER_LAMBDA_DigiHSTruth',
                'LATERAL_DigiHSTruth',
                'LONGITUDINAL_DigiHSTruth',
                'ENG_FRAC_EM_DigiHSTruth',
                'ENG_FRAC_MAX_DigiHSTruth',
                'ENG_FRAC_CORE_DigiHSTruth',
                'FIRST_ENG_DENS_DigiHSTruth',
                'SECOND_ENG_DENS_DigiHSTruth',
                'ISOLATION_DigiHSTruth',
                'ENG_BAD_CELLS_DigiHSTruth',
                'N_BAD_CELLS_DigiHSTruth',
                'N_BAD_CELLS_CORR_DigiHSTruth',
                'BAD_CELLS_CORR_E_DigiHSTruth',
                'BADLARQ_FRAC_DigiHSTruth',
                'ENG_POS_DigiHSTruth',
                'SIGNIFICANCE_DigiHSTruth',
                'CELL_SIGNIFICANCE_DigiHSTruth',
                'CELL_SIG_SAMPLING_DigiHSTruth',
                'AVG_LAR_Q_DigiHSTruth',
                'AVG_TILE_Q_DigiHSTruth',
                'ENG_BAD_HV_CELLS_DigiHSTruth',
                'N_BAD_HV_CELLS_DigiHSTruth',
                'EM_PROBABILITY_DigiHSTruth',
                'HAD_WEIGHT_DigiHSTruth',
                'OOC_WEIGHT_DigiHSTruth',
                'DM_WEIGHT_DigiHSTruth',
            ],
        },
    ],
    'getMomentValue': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.CaloCluster_v1',
            'name': 'MomentType',
            'values': [
                'FIRST_PHI',
                'FIRST_ETA',
                'SECOND_R',
                'SECOND_LAMBDA',
                'DELTA_PHI',
                'DELTA_THETA',
                'DELTA_ALPHA',
                'CENTER_X',
                'CENTER_Y',
                'CENTER_Z',
                'CENTER_MAG',
                'CENTER_LAMBDA',
                'LATERAL',
                'LONGITUDINAL',
                'ENG_FRAC_EM',
                'ENG_FRAC_MAX',
                'ENG_FRAC_CORE',
                'FIRST_ENG_DENS',
                'SECOND_ENG_DENS',
                'ISOLATION',
                'ENG_BAD_CELLS',
                'N_BAD_CELLS',
                'N_BAD_CELLS_CORR',
                'BAD_CELLS_CORR_E',
                'BADLARQ_FRAC',
                'ENG_POS',
                'SIGNIFICANCE',
                'CELL_SIGNIFICANCE',
                'CELL_SIG_SAMPLING',
                'AVG_LAR_Q',
                'AVG_TILE_Q',
                'ENG_BAD_HV_CELLS',
                'N_BAD_HV_CELLS',
                'PTD',
                'MASS',
                'EM_PROBABILITY',
                'HAD_WEIGHT',
                'OOC_WEIGHT',
                'DM_WEIGHT',
                'TILE_CONFIDENCE_LEVEL',
                'SECOND_TIME',
                'NCELL_SAMPLING',
                'VERTEX_FRACTION',
                'NVERTEX_FRACTION',
                'ETACALOFRAME',
                'PHICALOFRAME',
                'ETA1CALOFRAME',
                'PHI1CALOFRAME',
                'ETA2CALOFRAME',
                'PHI2CALOFRAME',
                'ENG_CALIB_TOT',
                'ENG_CALIB_OUT_L',
                'ENG_CALIB_OUT_M',
                'ENG_CALIB_OUT_T',
                'ENG_CALIB_DEAD_L',
                'ENG_CALIB_DEAD_M',
                'ENG_CALIB_DEAD_T',
                'ENG_CALIB_EMB0',
                'ENG_CALIB_EME0',
                'ENG_CALIB_TILEG3',
                'ENG_CALIB_DEAD_TOT',
                'ENG_CALIB_DEAD_EMB0',
                'ENG_CALIB_DEAD_TILE0',
                'ENG_CALIB_DEAD_TILEG3',
                'ENG_CALIB_DEAD_EME0',
                'ENG_CALIB_DEAD_HEC0',
                'ENG_CALIB_DEAD_FCAL',
                'ENG_CALIB_DEAD_LEAKAGE',
                'ENG_CALIB_DEAD_UNCLASS',
                'ENG_CALIB_FRAC_EM',
                'ENG_CALIB_FRAC_HAD',
                'ENG_CALIB_FRAC_REST',
                'ENERGY_DigiHSTruth',
                'ETA_DigiHSTruth',
                'PHI_DigiHSTruth',
                'TIME_DigiHSTruth',
                'ENERGY_CALIB_DigiHSTruth',
                'ETA_CALIB_DigiHSTruth',
                'PHI_CALIB_DigiHSTruth',
                'TIME_CALIB_DigiHSTruth',
                'FIRST_PHI_DigiHSTruth',
                'FIRST_ETA_DigiHSTruth',
                'SECOND_R_DigiHSTruth',
                'SECOND_LAMBDA_DigiHSTruth',
                'DELTA_PHI_DigiHSTruth',
                'DELTA_THETA_DigiHSTruth',
                'DELTA_ALPHA_DigiHSTruth',
                'CENTER_X_DigiHSTruth',
                'CENTER_Y_DigiHSTruth',
                'CENTER_Z_DigiHSTruth',
                'CENTER_MAG_DigiHSTruth',
                'CENTER_LAMBDA_DigiHSTruth',
                'LATERAL_DigiHSTruth',
                'LONGITUDINAL_DigiHSTruth',
                'ENG_FRAC_EM_DigiHSTruth',
                'ENG_FRAC_MAX_DigiHSTruth',
                'ENG_FRAC_CORE_DigiHSTruth',
                'FIRST_ENG_DENS_DigiHSTruth',
                'SECOND_ENG_DENS_DigiHSTruth',
                'ISOLATION_DigiHSTruth',
                'ENG_BAD_CELLS_DigiHSTruth',
                'N_BAD_CELLS_DigiHSTruth',
                'N_BAD_CELLS_CORR_DigiHSTruth',
                'BAD_CELLS_CORR_E_DigiHSTruth',
                'BADLARQ_FRAC_DigiHSTruth',
                'ENG_POS_DigiHSTruth',
                'SIGNIFICANCE_DigiHSTruth',
                'CELL_SIGNIFICANCE_DigiHSTruth',
                'CELL_SIG_SAMPLING_DigiHSTruth',
                'AVG_LAR_Q_DigiHSTruth',
                'AVG_TILE_Q_DigiHSTruth',
                'ENG_BAD_HV_CELLS_DigiHSTruth',
                'N_BAD_HV_CELLS_DigiHSTruth',
                'EM_PROBABILITY_DigiHSTruth',
                'HAD_WEIGHT_DigiHSTruth',
                'OOC_WEIGHT_DigiHSTruth',
                'DM_WEIGHT_DigiHSTruth',
            ],
        },
    ],
    'hasSampling': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'CaloSampling',
            'name': 'CaloSample',
            'values': [
                'PreSamplerB',
                'EMB1',
                'EMB2',
                'EMB3',
                'PreSamplerE',
                'EME1',
                'EME2',
                'EME3',
                'HEC0',
                'HEC1',
                'HEC2',
                'HEC3',
                'TileBar0',
                'TileBar1',
                'TileBar2',
                'TileGap1',
                'TileGap2',
                'TileGap3',
                'TileExt0',
                'TileExt1',
                'TileExt2',
                'FCAL0',
                'FCAL1',
                'FCAL2',
                'MINIFCAL0',
                'MINIFCAL1',
                'MINIFCAL2',
                'MINIFCAL3',
                'Unknown',
            ],
        },
    ],
    'clusterSize': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.CaloCluster_v1',
            'name': 'ClusterSize',
            'values': [
                'SW_55ele',
                'SW_35ele',
                'SW_37ele',
                'SW_55gam',
                'SW_35gam',
                'SW_37gam',
                'SW_55Econv',
                'SW_35Econv',
                'SW_37Econv',
                'SW_softe',
                'Topo_420',
                'Topo_633',
                'SW_7_11',
                'SuperCluster',
                'Tower_01_01',
                'Tower_005_005',
                'Tower_fixed_area',
                'CSize_Unknown',
            ],
        },
    ],
    'setSignalState': [
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
    'signalState': [
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
    'State':
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
    'ClusterSize':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.CaloCluster_v1',
            'name': 'ClusterSize',
            'values': [
                'SW_55ele',
                'SW_35ele',
                'SW_37ele',
                'SW_55gam',
                'SW_35gam',
                'SW_37gam',
                'SW_55Econv',
                'SW_35Econv',
                'SW_37Econv',
                'SW_softe',
                'Topo_420',
                'Topo_633',
                'SW_7_11',
                'SuperCluster',
                'Tower_01_01',
                'Tower_005_005',
                'Tower_fixed_area',
                'CSize_Unknown',
            ],
        },
    'MomentType':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.CaloCluster_v1',
            'name': 'MomentType',
            'values': [
                'FIRST_PHI',
                'FIRST_ETA',
                'SECOND_R',
                'SECOND_LAMBDA',
                'DELTA_PHI',
                'DELTA_THETA',
                'DELTA_ALPHA',
                'CENTER_X',
                'CENTER_Y',
                'CENTER_Z',
                'CENTER_MAG',
                'CENTER_LAMBDA',
                'LATERAL',
                'LONGITUDINAL',
                'ENG_FRAC_EM',
                'ENG_FRAC_MAX',
                'ENG_FRAC_CORE',
                'FIRST_ENG_DENS',
                'SECOND_ENG_DENS',
                'ISOLATION',
                'ENG_BAD_CELLS',
                'N_BAD_CELLS',
                'N_BAD_CELLS_CORR',
                'BAD_CELLS_CORR_E',
                'BADLARQ_FRAC',
                'ENG_POS',
                'SIGNIFICANCE',
                'CELL_SIGNIFICANCE',
                'CELL_SIG_SAMPLING',
                'AVG_LAR_Q',
                'AVG_TILE_Q',
                'ENG_BAD_HV_CELLS',
                'N_BAD_HV_CELLS',
                'PTD',
                'MASS',
                'EM_PROBABILITY',
                'HAD_WEIGHT',
                'OOC_WEIGHT',
                'DM_WEIGHT',
                'TILE_CONFIDENCE_LEVEL',
                'SECOND_TIME',
                'NCELL_SAMPLING',
                'VERTEX_FRACTION',
                'NVERTEX_FRACTION',
                'ETACALOFRAME',
                'PHICALOFRAME',
                'ETA1CALOFRAME',
                'PHI1CALOFRAME',
                'ETA2CALOFRAME',
                'PHI2CALOFRAME',
                'ENG_CALIB_TOT',
                'ENG_CALIB_OUT_L',
                'ENG_CALIB_OUT_M',
                'ENG_CALIB_OUT_T',
                'ENG_CALIB_DEAD_L',
                'ENG_CALIB_DEAD_M',
                'ENG_CALIB_DEAD_T',
                'ENG_CALIB_EMB0',
                'ENG_CALIB_EME0',
                'ENG_CALIB_TILEG3',
                'ENG_CALIB_DEAD_TOT',
                'ENG_CALIB_DEAD_EMB0',
                'ENG_CALIB_DEAD_TILE0',
                'ENG_CALIB_DEAD_TILEG3',
                'ENG_CALIB_DEAD_EME0',
                'ENG_CALIB_DEAD_HEC0',
                'ENG_CALIB_DEAD_FCAL',
                'ENG_CALIB_DEAD_LEAKAGE',
                'ENG_CALIB_DEAD_UNCLASS',
                'ENG_CALIB_FRAC_EM',
                'ENG_CALIB_FRAC_HAD',
                'ENG_CALIB_FRAC_REST',
                'ENERGY_DigiHSTruth',
                'ETA_DigiHSTruth',
                'PHI_DigiHSTruth',
                'TIME_DigiHSTruth',
                'ENERGY_CALIB_DigiHSTruth',
                'ETA_CALIB_DigiHSTruth',
                'PHI_CALIB_DigiHSTruth',
                'TIME_CALIB_DigiHSTruth',
                'FIRST_PHI_DigiHSTruth',
                'FIRST_ETA_DigiHSTruth',
                'SECOND_R_DigiHSTruth',
                'SECOND_LAMBDA_DigiHSTruth',
                'DELTA_PHI_DigiHSTruth',
                'DELTA_THETA_DigiHSTruth',
                'DELTA_ALPHA_DigiHSTruth',
                'CENTER_X_DigiHSTruth',
                'CENTER_Y_DigiHSTruth',
                'CENTER_Z_DigiHSTruth',
                'CENTER_MAG_DigiHSTruth',
                'CENTER_LAMBDA_DigiHSTruth',
                'LATERAL_DigiHSTruth',
                'LONGITUDINAL_DigiHSTruth',
                'ENG_FRAC_EM_DigiHSTruth',
                'ENG_FRAC_MAX_DigiHSTruth',
                'ENG_FRAC_CORE_DigiHSTruth',
                'FIRST_ENG_DENS_DigiHSTruth',
                'SECOND_ENG_DENS_DigiHSTruth',
                'ISOLATION_DigiHSTruth',
                'ENG_BAD_CELLS_DigiHSTruth',
                'N_BAD_CELLS_DigiHSTruth',
                'N_BAD_CELLS_CORR_DigiHSTruth',
                'BAD_CELLS_CORR_E_DigiHSTruth',
                'BADLARQ_FRAC_DigiHSTruth',
                'ENG_POS_DigiHSTruth',
                'SIGNIFICANCE_DigiHSTruth',
                'CELL_SIGNIFICANCE_DigiHSTruth',
                'CELL_SIG_SAMPLING_DigiHSTruth',
                'AVG_LAR_Q_DigiHSTruth',
                'AVG_TILE_Q_DigiHSTruth',
                'ENG_BAD_HV_CELLS_DigiHSTruth',
                'N_BAD_HV_CELLS_DigiHSTruth',
                'EM_PROBABILITY_DigiHSTruth',
                'HAD_WEIGHT_DigiHSTruth',
                'OOC_WEIGHT_DigiHSTruth',
                'DM_WEIGHT_DigiHSTruth',
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
class CaloCluster_v1:
    "A class"

    class State(Enum):
        UNKNOWN = -1
        UNCALIBRATED = 0
        CALIBRATED = 1
        ALTCALIBRATED = 2
        NSTATES = 3

    class ClusterSize(Enum):
        SW_55ele = 1
        SW_35ele = 2
        SW_37ele = 3
        SW_55gam = 4
        SW_35gam = 5
        SW_37gam = 6
        SW_55Econv = 7
        SW_35Econv = 8
        SW_37Econv = 9
        SW_softe = 10
        Topo_420 = 11
        Topo_633 = 12
        SW_7_11 = 13
        SuperCluster = 14
        Tower_01_01 = 15
        Tower_005_005 = 16
        Tower_fixed_area = 17
        CSize_Unknown = 99

    class MomentType(Enum):
        FIRST_PHI = 101
        FIRST_ETA = 102
        SECOND_R = 201
        SECOND_LAMBDA = 202
        DELTA_PHI = 301
        DELTA_THETA = 302
        DELTA_ALPHA = 303
        CENTER_X = 401
        CENTER_Y = 402
        CENTER_Z = 403
        CENTER_MAG = 404
        CENTER_LAMBDA = 501
        LATERAL = 601
        LONGITUDINAL = 602
        ENG_FRAC_EM = 701
        ENG_FRAC_MAX = 702
        ENG_FRAC_CORE = 703
        FIRST_ENG_DENS = 804
        SECOND_ENG_DENS = 805
        ISOLATION = 806
        ENG_BAD_CELLS = 807
        N_BAD_CELLS = 808
        N_BAD_CELLS_CORR = 809
        BAD_CELLS_CORR_E = 813
        BADLARQ_FRAC = 821
        ENG_POS = 822
        SIGNIFICANCE = 823
        CELL_SIGNIFICANCE = 824
        CELL_SIG_SAMPLING = 825
        AVG_LAR_Q = 826
        AVG_TILE_Q = 827
        ENG_BAD_HV_CELLS = 828
        N_BAD_HV_CELLS = 829
        PTD = 830
        MASS = 831
        EM_PROBABILITY = 900
        HAD_WEIGHT = 901
        OOC_WEIGHT = 902
        DM_WEIGHT = 903
        TILE_CONFIDENCE_LEVEL = 904
        SECOND_TIME = 910
        NCELL_SAMPLING = 920
        VERTEX_FRACTION = 1000
        NVERTEX_FRACTION = 1001
        ETACALOFRAME = 1100
        PHICALOFRAME = 1101
        ETA1CALOFRAME = 1102
        PHI1CALOFRAME = 1103
        ETA2CALOFRAME = 1104
        PHI2CALOFRAME = 1105
        ENG_CALIB_TOT = 10001
        ENG_CALIB_OUT_L = 10010
        ENG_CALIB_OUT_M = 10011
        ENG_CALIB_OUT_T = 10012
        ENG_CALIB_DEAD_L = 10020
        ENG_CALIB_DEAD_M = 10021
        ENG_CALIB_DEAD_T = 10022
        ENG_CALIB_EMB0 = 10030
        ENG_CALIB_EME0 = 10031
        ENG_CALIB_TILEG3 = 10032
        ENG_CALIB_DEAD_TOT = 10040
        ENG_CALIB_DEAD_EMB0 = 10041
        ENG_CALIB_DEAD_TILE0 = 10042
        ENG_CALIB_DEAD_TILEG3 = 10043
        ENG_CALIB_DEAD_EME0 = 10044
        ENG_CALIB_DEAD_HEC0 = 10045
        ENG_CALIB_DEAD_FCAL = 10046
        ENG_CALIB_DEAD_LEAKAGE = 10047
        ENG_CALIB_DEAD_UNCLASS = 10048
        ENG_CALIB_FRAC_EM = 10051
        ENG_CALIB_FRAC_HAD = 10052
        ENG_CALIB_FRAC_REST = 10053
        ENERGY_DigiHSTruth = 40101
        ETA_DigiHSTruth = 401024
        PHI_DigiHSTruth = 401034
        TIME_DigiHSTruth = 40104
        ENERGY_CALIB_DigiHSTruth = 40105
        ETA_CALIB_DigiHSTruth = 40106
        PHI_CALIB_DigiHSTruth = 40107
        TIME_CALIB_DigiHSTruth = 40108
        FIRST_PHI_DigiHSTruth = 50101
        FIRST_ETA_DigiHSTruth = 50102
        SECOND_R_DigiHSTruth = 50201
        SECOND_LAMBDA_DigiHSTruth = 50202
        DELTA_PHI_DigiHSTruth = 50301
        DELTA_THETA_DigiHSTruth = 50302
        DELTA_ALPHA_DigiHSTruth = 50303
        CENTER_X_DigiHSTruth = 50401
        CENTER_Y_DigiHSTruth = 50402
        CENTER_Z_DigiHSTruth = 50403
        CENTER_MAG_DigiHSTruth = 50404
        CENTER_LAMBDA_DigiHSTruth = 50501
        LATERAL_DigiHSTruth = 50601
        LONGITUDINAL_DigiHSTruth = 50602
        ENG_FRAC_EM_DigiHSTruth = 50701
        ENG_FRAC_MAX_DigiHSTruth = 50702
        ENG_FRAC_CORE_DigiHSTruth = 75003
        FIRST_ENG_DENS_DigiHSTruth = 50804
        SECOND_ENG_DENS_DigiHSTruth = 50805
        ISOLATION_DigiHSTruth = 50806
        ENG_BAD_CELLS_DigiHSTruth = 50807
        N_BAD_CELLS_DigiHSTruth = 50808
        N_BAD_CELLS_CORR_DigiHSTruth = 50809
        BAD_CELLS_CORR_E_DigiHSTruth = 50813
        BADLARQ_FRAC_DigiHSTruth = 50821
        ENG_POS_DigiHSTruth = 50822
        SIGNIFICANCE_DigiHSTruth = 50823
        CELL_SIGNIFICANCE_DigiHSTruth = 50824
        CELL_SIG_SAMPLING_DigiHSTruth = 50825
        AVG_LAR_Q_DigiHSTruth = 50826
        AVG_TILE_Q_DigiHSTruth = 50827
        ENG_BAD_HV_CELLS_DigiHSTruth = 50828
        N_BAD_HV_CELLS_DigiHSTruth = 50829
        EM_PROBABILITY_DigiHSTruth = 50900
        HAD_WEIGHT_DigiHSTruth = 50901
        OOC_WEIGHT_DigiHSTruth = 50902
        DM_WEIGHT_DigiHSTruth = 50903


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

    def et(self) -> float:
        "A method"
        ...

    def eSample(self, sampling: func_adl_servicex_xaodr25.calosampling.CaloSampling.CaloSample) -> float:
        "A method"
        ...

    def etaSample(self, sampling: func_adl_servicex_xaodr25.calosampling.CaloSampling.CaloSample) -> float:
        "A method"
        ...

    def phiSample(self, sampling: func_adl_servicex_xaodr25.calosampling.CaloSampling.CaloSample) -> float:
        "A method"
        ...

    def energy_max(self, sampling: func_adl_servicex_xaodr25.calosampling.CaloSampling.CaloSample) -> float:
        "A method"
        ...

    def etamax(self, sampling: func_adl_servicex_xaodr25.calosampling.CaloSampling.CaloSample) -> float:
        "A method"
        ...

    def phimax(self, sampling: func_adl_servicex_xaodr25.calosampling.CaloSampling.CaloSample) -> float:
        "A method"
        ...

    def etasize(self, sampling: func_adl_servicex_xaodr25.calosampling.CaloSampling.CaloSample) -> float:
        "A method"
        ...

    def phisize(self, sampling: func_adl_servicex_xaodr25.calosampling.CaloSampling.CaloSample) -> float:
        "A method"
        ...

    def numberCellsInSampling(self, samp: func_adl_servicex_xaodr25.calosampling.CaloSampling.CaloSample, isInnerWheel: bool) -> int:
        "A method"
        ...

    def numberCells(self) -> int:
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

    def setEnergy(self, sampling: func_adl_servicex_xaodr25.calosampling.CaloSampling.CaloSample, e: float) -> bool:
        "A method"
        ...

    def setEta(self, sampling: func_adl_servicex_xaodr25.calosampling.CaloSampling.CaloSample, eta: float) -> bool:
        "A method"
        ...

    def setPhi(self, sampling: func_adl_servicex_xaodr25.calosampling.CaloSampling.CaloSample, phi: float) -> bool:
        "A method"
        ...

    def setEmax(self, sampling: func_adl_servicex_xaodr25.calosampling.CaloSampling.CaloSample, eMax: float) -> bool:
        "A method"
        ...

    def setEtamax(self, sampling: func_adl_servicex_xaodr25.calosampling.CaloSampling.CaloSample, etaMax: float) -> bool:
        "A method"
        ...

    def setPhimax(self, sampling: func_adl_servicex_xaodr25.calosampling.CaloSampling.CaloSample, phiMax: float) -> bool:
        "A method"
        ...

    def setEtasize(self, sampling: func_adl_servicex_xaodr25.calosampling.CaloSampling.CaloSample, etaSize: float) -> bool:
        "A method"
        ...

    def setPhisize(self, sampling: func_adl_servicex_xaodr25.calosampling.CaloSampling.CaloSample, phiSize: float) -> bool:
        "A method"
        ...

    def retrieveMoment(self, type: func_adl_servicex_xaodr25.xAOD.calocluster_v1.CaloCluster_v1.MomentType, value: float) -> bool:
        "A method"
        ...

    def getMomentValue(self, type: func_adl_servicex_xaodr25.xAOD.calocluster_v1.CaloCluster_v1.MomentType) -> float:
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

    def secondTime(self) -> float:
        "A method"
        ...

    def samplingPattern(self) -> int:
        "A method"
        ...

    def nSamples(self) -> int:
        "A method"
        ...

    def hasSampling(self, s: func_adl_servicex_xaodr25.calosampling.CaloSampling.CaloSample) -> bool:
        "A method"
        ...

    def clusterSize(self) -> func_adl_servicex_xaodr25.xAOD.calocluster_v1.CaloCluster_v1.ClusterSize:
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

    def setSignalState(self, s: func_adl_servicex_xaodr25.xAOD.calocluster_v1.CaloCluster_v1.State) -> bool:
        "A method"
        ...

    def signalState(self) -> func_adl_servicex_xaodr25.xAOD.calocluster_v1.CaloCluster_v1.State:
        "A method"
        ...

    def getClusterEtaSize(self) -> int:
        "A method"
        ...

    def getClusterPhiSize(self) -> int:
        "A method"
        ...

    def badChannelList(self) -> func_adl_servicex_xaodr25.vector_xaod_caloclusterbadchanneldata_v1_.vector_xAOD_CaloClusterBadChannelData_v1_:
        "A method"
        ...

    def getSisterCluster(self) -> func_adl_servicex_xaodr25.xAOD.calocluster_v1.CaloCluster_v1:
        "A method"
        ...

    def getSisterClusterLink(self) -> func_adl_servicex_xaodr25.elementlink_datavector_xaod_calocluster_v1__.ElementLink_DataVector_xAOD_CaloCluster_v1__:
        "A method"
        ...

    def setSisterClusterLink(self, sister: func_adl_servicex_xaodr25.elementlink_datavector_xaod_calocluster_v1__.ElementLink_DataVector_xAOD_CaloCluster_v1__) -> bool:
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
