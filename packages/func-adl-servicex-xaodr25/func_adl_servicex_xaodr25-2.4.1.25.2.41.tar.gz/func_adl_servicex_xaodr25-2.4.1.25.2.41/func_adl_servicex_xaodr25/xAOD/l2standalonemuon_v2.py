from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr25

_method_map = {
    'pt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'pt',
        'return_type': 'double',
    },
    'eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'eta',
        'return_type': 'double',
    },
    'phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'phi',
        'return_type': 'double',
    },
    'm': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'm',
        'return_type': 'double',
    },
    'e': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'e',
        'return_type': 'double',
    },
    'rapidity': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'rapidity',
        'return_type': 'double',
    },
    'p4': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'p4',
        'return_type': 'TLorentzVector',
    },
    'type': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'type',
        'return_type': 'xAODType::ObjectType',
    },
    'roiWord': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'roiWord',
        'return_type': 'unsigned int',
    },
    'sAddress': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'sAddress',
        'return_type': 'int',
    },
    'etaMS': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'etaMS',
        'return_type': 'float',
    },
    'phiMS': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'phiMS',
        'return_type': 'float',
    },
    'dirPhiMS': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'dirPhiMS',
        'return_type': 'float',
    },
    'rMS': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'rMS',
        'return_type': 'float',
    },
    'zMS': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'zMS',
        'return_type': 'float',
    },
    'dirZMS': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'dirZMS',
        'return_type': 'float',
    },
    'beta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'beta',
        'return_type': 'float',
    },
    'barrelRadius': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'barrelRadius',
        'return_type': 'float',
    },
    'barrelSagitta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'barrelSagitta',
        'return_type': 'float',
    },
    'endcapAlpha': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'endcapAlpha',
        'return_type': 'float',
    },
    'endcapBeta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'endcapBeta',
        'return_type': 'float',
    },
    'endcapRadius': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'endcapRadius',
        'return_type': 'float',
    },
    'etaMap': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'etaMap',
        'return_type': 'float',
    },
    'phiMap': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'phiMap',
        'return_type': 'float',
    },
    'etaBin': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'etaBin',
        'return_type': 'int',
    },
    'phiBin': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'phiBin',
        'return_type': 'int',
    },
    'isTgcFailure': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'isTgcFailure',
        'return_type': 'int',
    },
    'isRpcFailure': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'isRpcFailure',
        'return_type': 'int',
    },
    'deltaPt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'deltaPt',
        'return_type': 'float',
    },
    'deltaPtParm1': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'deltaPtParm1',
        'return_type': 'float',
    },
    'deltaPtParm2': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'deltaPtParm2',
        'return_type': 'float',
    },
    'deltaPtParm3': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'deltaPtParm3',
        'return_type': 'float',
    },
    'deltaEta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'deltaEta',
        'return_type': 'float',
    },
    'deltaPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'deltaPhi',
        'return_type': 'float',
    },
    'superPointR': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'superPointR',
        'return_type': 'float',
    },
    'superPointZ': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'superPointZ',
        'return_type': 'float',
    },
    'superPointSlope': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'superPointSlope',
        'return_type': 'float',
    },
    'superPointIntercept': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'superPointIntercept',
        'return_type': 'float',
    },
    'superPointChi2': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'superPointChi2',
        'return_type': 'float',
    },
    'nTrackPositions': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'nTrackPositions',
        'return_type': 'unsigned int',
    },
    'trackPositionR': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'trackPositionR',
        'return_type': 'float',
    },
    'trackPositionZ': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'trackPositionZ',
        'return_type': 'float',
    },
    'trackPositionEta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'trackPositionEta',
        'return_type': 'float',
    },
    'trackPositionPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'trackPositionPhi',
        'return_type': 'float',
    },
    'algoId': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'algoId',
        'return_type': 'int',
    },
    'teId': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'teId',
        'return_type': 'unsigned int',
    },
    'lvl1Id': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'lvl1Id',
        'return_type': 'unsigned int',
    },
    'lumiBlock': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'lumiBlock',
        'return_type': 'unsigned int',
    },
    'muonDetMask': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'muonDetMask',
        'return_type': 'unsigned int',
    },
    'roiId': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'roiId',
        'return_type': 'unsigned int',
    },
    'roiSystem': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'roiSystem',
        'return_type': 'unsigned int',
    },
    'roiSubsystem': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'roiSubsystem',
        'return_type': 'unsigned int',
    },
    'roiSector': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'roiSector',
        'return_type': 'unsigned int',
    },
    'roiNumber': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'roiNumber',
        'return_type': 'unsigned int',
    },
    'roiThreshold': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'roiThreshold',
        'return_type': 'unsigned int',
    },
    'roiEta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'roiEta',
        'return_type': 'float',
    },
    'roiPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'roiPhi',
        'return_type': 'float',
    },
    'tgcPt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'tgcPt',
        'return_type': 'float',
    },
    'ptBarrelRadius': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'ptBarrelRadius',
        'return_type': 'float',
    },
    'ptBarrelSagitta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'ptBarrelSagitta',
        'return_type': 'float',
    },
    'ptEndcapAlpha': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'ptEndcapAlpha',
        'return_type': 'float',
    },
    'ptEndcapBeta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'ptEndcapBeta',
        'return_type': 'float',
    },
    'ptEndcapRadius': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'ptEndcapRadius',
        'return_type': 'float',
    },
    'ptCSC': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'ptCSC',
        'return_type': 'float',
    },
    'chamberType1': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'chamberType1',
        'return_type': 'int',
    },
    'chamberType2': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'chamberType2',
        'return_type': 'int',
    },
    'roadAw': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'roadAw',
        'return_type': 'float',
    },
    'roadBw': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'roadBw',
        'return_type': 'float',
    },
    'zMin': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'zMin',
        'return_type': 'float',
    },
    'zMax': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'zMax',
        'return_type': 'float',
    },
    'rMin': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'rMin',
        'return_type': 'float',
    },
    'rMax': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'rMax',
        'return_type': 'float',
    },
    'etaMin': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'etaMin',
        'return_type': 'float',
    },
    'etaMax': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'etaMax',
        'return_type': 'float',
    },
    'tgcInnEta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'tgcInnEta',
        'return_type': 'float',
    },
    'tgcInnPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'tgcInnPhi',
        'return_type': 'float',
    },
    'tgcInnR': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'tgcInnR',
        'return_type': 'float',
    },
    'tgcInnZ': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'tgcInnZ',
        'return_type': 'float',
    },
    'tgcInnRhoStd': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'tgcInnRhoStd',
        'return_type': 'float',
    },
    'tgcInnRhoN': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'tgcInnRhoN',
        'return_type': 'long',
    },
    'tgcInnPhiStd': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'tgcInnPhiStd',
        'return_type': 'float',
    },
    'tgcInnPhiN': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'tgcInnPhiN',
        'return_type': 'long',
    },
    'tgcMid1Eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'tgcMid1Eta',
        'return_type': 'float',
    },
    'tgcMid1Phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'tgcMid1Phi',
        'return_type': 'float',
    },
    'tgcMid1R': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'tgcMid1R',
        'return_type': 'float',
    },
    'tgcMid1Z': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'tgcMid1Z',
        'return_type': 'float',
    },
    'tgcMid2Eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'tgcMid2Eta',
        'return_type': 'float',
    },
    'tgcMid2Phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'tgcMid2Phi',
        'return_type': 'float',
    },
    'tgcMid2R': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'tgcMid2R',
        'return_type': 'float',
    },
    'tgcMid2Z': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'tgcMid2Z',
        'return_type': 'float',
    },
    'tgcMidRhoChi2': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'tgcMidRhoChi2',
        'return_type': 'float',
    },
    'tgcMidRhoN': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'tgcMidRhoN',
        'return_type': 'long',
    },
    'tgcMidPhiChi2': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'tgcMidPhiChi2',
        'return_type': 'float',
    },
    'tgcMidPhiN': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'tgcMidPhiN',
        'return_type': 'long',
    },
    'rpcFitInnPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'rpcFitInnPhi',
        'return_type': 'float',
    },
    'rpcFitInnSlope': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'rpcFitInnSlope',
        'return_type': 'float',
    },
    'rpcFitInnOffset': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'rpcFitInnOffset',
        'return_type': 'float',
    },
    'rpcFitMidPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'rpcFitMidPhi',
        'return_type': 'float',
    },
    'rpcFitMidSlope': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'rpcFitMidSlope',
        'return_type': 'float',
    },
    'rpcFitMidOffset': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'rpcFitMidOffset',
        'return_type': 'float',
    },
    'rpcFitOutPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'rpcFitOutPhi',
        'return_type': 'float',
    },
    'rpcFitOutSlope': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'rpcFitOutSlope',
        'return_type': 'float',
    },
    'rpcFitOutOffset': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'rpcFitOutOffset',
        'return_type': 'float',
    },
    'rpcHitsCapacity': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'rpcHitsCapacity',
        'return_type': 'int',
    },
    'tgcHitsCapacity': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'tgcHitsCapacity',
        'return_type': 'int',
    },
    'mdtHitsCapacity': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'mdtHitsCapacity',
        'return_type': 'int',
    },
    'cscHitsCapacity': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'cscHitsCapacity',
        'return_type': 'int',
    },
    'rpcHitLayer': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'rpcHitLayer',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned int>',
    },
    'rpcHitMeasuresPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'rpcHitMeasuresPhi',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned int>',
    },
    'rpcHitX': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'rpcHitX',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'rpcHitY': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'rpcHitY',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'rpcHitZ': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'rpcHitZ',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'rpcHitTime': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'rpcHitTime',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'rpcHitDistToEtaReadout': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'rpcHitDistToEtaReadout',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'rpcHitDistToPhiReadout': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'rpcHitDistToPhiReadout',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'rpcHitStationName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'rpcHitStationName',
        'return_type_element': 'string',
        'return_type_collection': 'const vector<string>',
    },
    'tgcHitEta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'tgcHitEta',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'tgcHitPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'tgcHitPhi',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'tgcHitR': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'tgcHitR',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'tgcHitZ': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'tgcHitZ',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'tgcHitWidth': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'tgcHitWidth',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'tgcHitStationNum': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'tgcHitStationNum',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'tgcHitIsStrip': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'tgcHitIsStrip',
        'return_type_element': 'bool',
        'return_type_collection': 'const vector<bool>',
    },
    'tgcHitBCTag': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'tgcHitBCTag',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'tgcHitInRoad': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'tgcHitInRoad',
        'return_type_element': 'bool',
        'return_type_collection': 'const vector<bool>',
    },
    'nMdtHits': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'nMdtHits',
        'return_type': 'unsigned int',
    },
    'mdtHitOnlineId': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'mdtHitOnlineId',
        'return_type': 'unsigned int',
    },
    'mdtHitOfflineId': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'mdtHitOfflineId',
        'return_type': 'int',
    },
    'mdtHitIsOutlier': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'mdtHitIsOutlier',
        'return_type': 'int',
    },
    'mdtHitChamber': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'mdtHitChamber',
        'return_type': 'int',
    },
    'mdtHitR': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'mdtHitR',
        'return_type': 'float',
    },
    'mdtHitZ': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'mdtHitZ',
        'return_type': 'float',
    },
    'mdtHitPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'mdtHitPhi',
        'return_type': 'float',
    },
    'mdtHitResidual': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'mdtHitResidual',
        'return_type': 'float',
    },
    'mdtHitTime': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'mdtHitTime',
        'return_type': 'float',
    },
    'mdtHitSpace': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'mdtHitSpace',
        'return_type': 'float',
    },
    'mdtHitSigma': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'mdtHitSigma',
        'return_type': 'float',
    },
    'nCscHits': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'nCscHits',
        'return_type': 'unsigned int',
    },
    'cscHitIsOutlier': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'cscHitIsOutlier',
        'return_type': 'int',
    },
    'cscHitChamber': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'cscHitChamber',
        'return_type': 'int',
    },
    'cscHitStationName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'cscHitStationName',
        'return_type': 'unsigned int',
    },
    'cscHitStationEta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'cscHitStationEta',
        'return_type': 'int',
    },
    'cscHitStationPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'cscHitStationPhi',
        'return_type': 'int',
    },
    'cscHitChamberLayer': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'cscHitChamberLayer',
        'return_type': 'int',
    },
    'cscHitWireLayer': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'cscHitWireLayer',
        'return_type': 'int',
    },
    'cscHitMeasuresPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'cscHitMeasuresPhi',
        'return_type': 'int',
    },
    'cscHitStrip': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'cscHitStrip',
        'return_type': 'int',
    },
    'cscHitEta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'cscHitEta',
        'return_type': 'float',
    },
    'cscHitPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'cscHitPhi',
        'return_type': 'float',
    },
    'cscHitR': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'cscHitR',
        'return_type': 'float',
    },
    'cscHitZ': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'cscHitZ',
        'return_type': 'float',
    },
    'cscHitCharge': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'cscHitCharge',
        'return_type': 'int',
    },
    'cscHitTime': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'cscHitTime',
        'return_type': 'float',
    },
    'cscHitResidual': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'cscHitResidual',
        'return_type': 'float',
    },
    'stgcClusterLayer': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'stgcClusterLayer',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned int>',
    },
    'stgcClusterIsOutlier': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'stgcClusterIsOutlier',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'stgcClusterType': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'stgcClusterType',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'stgcClusterEta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'stgcClusterEta',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'stgcClusterPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'stgcClusterPhi',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'stgcClusterR': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'stgcClusterR',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'stgcClusterZ': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'stgcClusterZ',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'stgcClusterResidualR': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'stgcClusterResidualR',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'stgcClusterResidualPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'stgcClusterResidualPhi',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'stgcClusterStationEta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'stgcClusterStationEta',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'stgcClusterStationPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'stgcClusterStationPhi',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'stgcClusterStationName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'stgcClusterStationName',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'mmClusterLayer': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'mmClusterLayer',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned int>',
    },
    'mmClusterIsOutlier': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'mmClusterIsOutlier',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'mmClusterEta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'mmClusterEta',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'mmClusterPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'mmClusterPhi',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'mmClusterR': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'mmClusterR',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'mmClusterZ': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'mmClusterZ',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'mmClusterResidualR': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'mmClusterResidualR',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'mmClusterResidualPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'mmClusterResidualPhi',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'mmClusterStationEta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'mmClusterStationEta',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'mmClusterStationPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'mmClusterStationPhi',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'mmClusterStationName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'mmClusterStationName',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<int>',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'trackIndices',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2StandAloneMuon_v2',
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
            'name': 'xAODTrigMuon/versions/L2StandAloneMuon_v2.h',
            'body_includes': ["xAODTrigMuon/versions/L2StandAloneMuon_v2.h"],
        })


        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODTrigMuon',
            'link_libraries': ["xAODTrigMuon"],
        })

        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class L2StandAloneMuon_v2:
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

    def p4(self) -> func_adl_servicex_xaodr25.tlorentzvector.TLorentzVector:
        "A method"
        ...

    def type(self) -> func_adl_servicex_xaodr25.xaodtype.xAODType.ObjectType:
        "A method"
        ...

    def roiWord(self) -> int:
        "A method"
        ...

    def sAddress(self) -> int:
        "A method"
        ...

    def etaMS(self) -> float:
        "A method"
        ...

    def phiMS(self) -> float:
        "A method"
        ...

    def dirPhiMS(self) -> float:
        "A method"
        ...

    def rMS(self) -> float:
        "A method"
        ...

    def zMS(self) -> float:
        "A method"
        ...

    def dirZMS(self) -> float:
        "A method"
        ...

    def beta(self) -> float:
        "A method"
        ...

    def barrelRadius(self) -> float:
        "A method"
        ...

    def barrelSagitta(self) -> float:
        "A method"
        ...

    def endcapAlpha(self) -> float:
        "A method"
        ...

    def endcapBeta(self) -> float:
        "A method"
        ...

    def endcapRadius(self) -> float:
        "A method"
        ...

    def etaMap(self) -> float:
        "A method"
        ...

    def phiMap(self) -> float:
        "A method"
        ...

    def etaBin(self) -> int:
        "A method"
        ...

    def phiBin(self) -> int:
        "A method"
        ...

    def isTgcFailure(self) -> int:
        "A method"
        ...

    def isRpcFailure(self) -> int:
        "A method"
        ...

    def deltaPt(self) -> float:
        "A method"
        ...

    def deltaPtParm1(self) -> float:
        "A method"
        ...

    def deltaPtParm2(self) -> float:
        "A method"
        ...

    def deltaPtParm3(self) -> float:
        "A method"
        ...

    def deltaEta(self) -> float:
        "A method"
        ...

    def deltaPhi(self) -> float:
        "A method"
        ...

    def superPointR(self, chamber: int) -> float:
        "A method"
        ...

    def superPointZ(self, chamber: int) -> float:
        "A method"
        ...

    def superPointSlope(self, chamber: int) -> float:
        "A method"
        ...

    def superPointIntercept(self, chamber: int) -> float:
        "A method"
        ...

    def superPointChi2(self, chamber: int) -> float:
        "A method"
        ...

    def nTrackPositions(self) -> int:
        "A method"
        ...

    def trackPositionR(self, n: int) -> float:
        "A method"
        ...

    def trackPositionZ(self, n: int) -> float:
        "A method"
        ...

    def trackPositionEta(self, n: int) -> float:
        "A method"
        ...

    def trackPositionPhi(self, n: int) -> float:
        "A method"
        ...

    def algoId(self) -> int:
        "A method"
        ...

    def teId(self) -> int:
        "A method"
        ...

    def lvl1Id(self) -> int:
        "A method"
        ...

    def lumiBlock(self) -> int:
        "A method"
        ...

    def muonDetMask(self) -> int:
        "A method"
        ...

    def roiId(self) -> int:
        "A method"
        ...

    def roiSystem(self) -> int:
        "A method"
        ...

    def roiSubsystem(self) -> int:
        "A method"
        ...

    def roiSector(self) -> int:
        "A method"
        ...

    def roiNumber(self) -> int:
        "A method"
        ...

    def roiThreshold(self) -> int:
        "A method"
        ...

    def roiEta(self) -> float:
        "A method"
        ...

    def roiPhi(self) -> float:
        "A method"
        ...

    def tgcPt(self) -> float:
        "A method"
        ...

    def ptBarrelRadius(self) -> float:
        "A method"
        ...

    def ptBarrelSagitta(self) -> float:
        "A method"
        ...

    def ptEndcapAlpha(self) -> float:
        "A method"
        ...

    def ptEndcapBeta(self) -> float:
        "A method"
        ...

    def ptEndcapRadius(self) -> float:
        "A method"
        ...

    def ptCSC(self) -> float:
        "A method"
        ...

    def chamberType1(self, station: int, sector: int) -> int:
        "A method"
        ...

    def chamberType2(self, station: int, sector: int) -> int:
        "A method"
        ...

    def roadAw(self, station: int, sector: int) -> float:
        "A method"
        ...

    def roadBw(self, station: int, sector: int) -> float:
        "A method"
        ...

    def zMin(self, station: int, sector: int) -> float:
        "A method"
        ...

    def zMax(self, station: int, sector: int) -> float:
        "A method"
        ...

    def rMin(self, station: int, sector: int) -> float:
        "A method"
        ...

    def rMax(self, station: int, sector: int) -> float:
        "A method"
        ...

    def etaMin(self, station: int, sector: int) -> float:
        "A method"
        ...

    def etaMax(self, station: int, sector: int) -> float:
        "A method"
        ...

    def tgcInnEta(self) -> float:
        "A method"
        ...

    def tgcInnPhi(self) -> float:
        "A method"
        ...

    def tgcInnR(self) -> float:
        "A method"
        ...

    def tgcInnZ(self) -> float:
        "A method"
        ...

    def tgcInnRhoStd(self) -> float:
        "A method"
        ...

    def tgcInnRhoN(self) -> int:
        "A method"
        ...

    def tgcInnPhiStd(self) -> float:
        "A method"
        ...

    def tgcInnPhiN(self) -> int:
        "A method"
        ...

    def tgcMid1Eta(self) -> float:
        "A method"
        ...

    def tgcMid1Phi(self) -> float:
        "A method"
        ...

    def tgcMid1R(self) -> float:
        "A method"
        ...

    def tgcMid1Z(self) -> float:
        "A method"
        ...

    def tgcMid2Eta(self) -> float:
        "A method"
        ...

    def tgcMid2Phi(self) -> float:
        "A method"
        ...

    def tgcMid2R(self) -> float:
        "A method"
        ...

    def tgcMid2Z(self) -> float:
        "A method"
        ...

    def tgcMidRhoChi2(self) -> float:
        "A method"
        ...

    def tgcMidRhoN(self) -> int:
        "A method"
        ...

    def tgcMidPhiChi2(self) -> float:
        "A method"
        ...

    def tgcMidPhiN(self) -> int:
        "A method"
        ...

    def rpcFitInnPhi(self) -> float:
        "A method"
        ...

    def rpcFitInnSlope(self) -> float:
        "A method"
        ...

    def rpcFitInnOffset(self) -> float:
        "A method"
        ...

    def rpcFitMidPhi(self) -> float:
        "A method"
        ...

    def rpcFitMidSlope(self) -> float:
        "A method"
        ...

    def rpcFitMidOffset(self) -> float:
        "A method"
        ...

    def rpcFitOutPhi(self) -> float:
        "A method"
        ...

    def rpcFitOutSlope(self) -> float:
        "A method"
        ...

    def rpcFitOutOffset(self) -> float:
        "A method"
        ...

    def rpcHitsCapacity(self) -> int:
        "A method"
        ...

    def tgcHitsCapacity(self) -> int:
        "A method"
        ...

    def mdtHitsCapacity(self) -> int:
        "A method"
        ...

    def cscHitsCapacity(self) -> int:
        "A method"
        ...

    def rpcHitLayer(self) -> func_adl_servicex_xaodr25.vector_int_.vector_int_:
        "A method"
        ...

    def rpcHitMeasuresPhi(self) -> func_adl_servicex_xaodr25.vector_int_.vector_int_:
        "A method"
        ...

    def rpcHitX(self) -> func_adl_servicex_xaodr25.vector_float_.vector_float_:
        "A method"
        ...

    def rpcHitY(self) -> func_adl_servicex_xaodr25.vector_float_.vector_float_:
        "A method"
        ...

    def rpcHitZ(self) -> func_adl_servicex_xaodr25.vector_float_.vector_float_:
        "A method"
        ...

    def rpcHitTime(self) -> func_adl_servicex_xaodr25.vector_float_.vector_float_:
        "A method"
        ...

    def rpcHitDistToEtaReadout(self) -> func_adl_servicex_xaodr25.vector_float_.vector_float_:
        "A method"
        ...

    def rpcHitDistToPhiReadout(self) -> func_adl_servicex_xaodr25.vector_float_.vector_float_:
        "A method"
        ...

    def rpcHitStationName(self) -> func_adl_servicex_xaodr25.vector_str_.vector_str_:
        "A method"
        ...

    def tgcHitEta(self) -> func_adl_servicex_xaodr25.vector_float_.vector_float_:
        "A method"
        ...

    def tgcHitPhi(self) -> func_adl_servicex_xaodr25.vector_float_.vector_float_:
        "A method"
        ...

    def tgcHitR(self) -> func_adl_servicex_xaodr25.vector_float_.vector_float_:
        "A method"
        ...

    def tgcHitZ(self) -> func_adl_servicex_xaodr25.vector_float_.vector_float_:
        "A method"
        ...

    def tgcHitWidth(self) -> func_adl_servicex_xaodr25.vector_float_.vector_float_:
        "A method"
        ...

    def tgcHitStationNum(self) -> func_adl_servicex_xaodr25.vector_int_.vector_int_:
        "A method"
        ...

    def tgcHitIsStrip(self) -> func_adl_servicex_xaodr25.vector_bool_.vector_bool_:
        "A method"
        ...

    def tgcHitBCTag(self) -> func_adl_servicex_xaodr25.vector_int_.vector_int_:
        "A method"
        ...

    def tgcHitInRoad(self) -> func_adl_servicex_xaodr25.vector_bool_.vector_bool_:
        "A method"
        ...

    def nMdtHits(self) -> int:
        "A method"
        ...

    def mdtHitOnlineId(self, tube: int) -> int:
        "A method"
        ...

    def mdtHitOfflineId(self, tube: int) -> int:
        "A method"
        ...

    def mdtHitIsOutlier(self, tube: int) -> int:
        "A method"
        ...

    def mdtHitChamber(self, tube: int) -> int:
        "A method"
        ...

    def mdtHitR(self, tube: int) -> float:
        "A method"
        ...

    def mdtHitZ(self, tube: int) -> float:
        "A method"
        ...

    def mdtHitPhi(self, tube: int) -> float:
        "A method"
        ...

    def mdtHitResidual(self, tube: int) -> float:
        "A method"
        ...

    def mdtHitTime(self, tube: int) -> float:
        "A method"
        ...

    def mdtHitSpace(self, tube: int) -> float:
        "A method"
        ...

    def mdtHitSigma(self, tube: int) -> float:
        "A method"
        ...

    def nCscHits(self) -> int:
        "A method"
        ...

    def cscHitIsOutlier(self, tube: int) -> int:
        "A method"
        ...

    def cscHitChamber(self, tube: int) -> int:
        "A method"
        ...

    def cscHitStationName(self, tube: int) -> int:
        "A method"
        ...

    def cscHitStationEta(self, tube: int) -> int:
        "A method"
        ...

    def cscHitStationPhi(self, tube: int) -> int:
        "A method"
        ...

    def cscHitChamberLayer(self, tube: int) -> int:
        "A method"
        ...

    def cscHitWireLayer(self, tube: int) -> int:
        "A method"
        ...

    def cscHitMeasuresPhi(self, tube: int) -> int:
        "A method"
        ...

    def cscHitStrip(self, tube: int) -> int:
        "A method"
        ...

    def cscHitEta(self, tube: int) -> float:
        "A method"
        ...

    def cscHitPhi(self, tube: int) -> float:
        "A method"
        ...

    def cscHitR(self, tube: int) -> float:
        "A method"
        ...

    def cscHitZ(self, tube: int) -> float:
        "A method"
        ...

    def cscHitCharge(self, tube: int) -> int:
        "A method"
        ...

    def cscHitTime(self, tube: int) -> float:
        "A method"
        ...

    def cscHitResidual(self, tube: int) -> float:
        "A method"
        ...

    def stgcClusterLayer(self) -> func_adl_servicex_xaodr25.vector_int_.vector_int_:
        "A method"
        ...

    def stgcClusterIsOutlier(self) -> func_adl_servicex_xaodr25.vector_int_.vector_int_:
        "A method"
        ...

    def stgcClusterType(self) -> func_adl_servicex_xaodr25.vector_int_.vector_int_:
        "A method"
        ...

    def stgcClusterEta(self) -> func_adl_servicex_xaodr25.vector_float_.vector_float_:
        "A method"
        ...

    def stgcClusterPhi(self) -> func_adl_servicex_xaodr25.vector_float_.vector_float_:
        "A method"
        ...

    def stgcClusterR(self) -> func_adl_servicex_xaodr25.vector_float_.vector_float_:
        "A method"
        ...

    def stgcClusterZ(self) -> func_adl_servicex_xaodr25.vector_float_.vector_float_:
        "A method"
        ...

    def stgcClusterResidualR(self) -> func_adl_servicex_xaodr25.vector_float_.vector_float_:
        "A method"
        ...

    def stgcClusterResidualPhi(self) -> func_adl_servicex_xaodr25.vector_float_.vector_float_:
        "A method"
        ...

    def stgcClusterStationEta(self) -> func_adl_servicex_xaodr25.vector_int_.vector_int_:
        "A method"
        ...

    def stgcClusterStationPhi(self) -> func_adl_servicex_xaodr25.vector_int_.vector_int_:
        "A method"
        ...

    def stgcClusterStationName(self) -> func_adl_servicex_xaodr25.vector_int_.vector_int_:
        "A method"
        ...

    def mmClusterLayer(self) -> func_adl_servicex_xaodr25.vector_int_.vector_int_:
        "A method"
        ...

    def mmClusterIsOutlier(self) -> func_adl_servicex_xaodr25.vector_int_.vector_int_:
        "A method"
        ...

    def mmClusterEta(self) -> func_adl_servicex_xaodr25.vector_float_.vector_float_:
        "A method"
        ...

    def mmClusterPhi(self) -> func_adl_servicex_xaodr25.vector_float_.vector_float_:
        "A method"
        ...

    def mmClusterR(self) -> func_adl_servicex_xaodr25.vector_float_.vector_float_:
        "A method"
        ...

    def mmClusterZ(self) -> func_adl_servicex_xaodr25.vector_float_.vector_float_:
        "A method"
        ...

    def mmClusterResidualR(self) -> func_adl_servicex_xaodr25.vector_float_.vector_float_:
        "A method"
        ...

    def mmClusterResidualPhi(self) -> func_adl_servicex_xaodr25.vector_float_.vector_float_:
        "A method"
        ...

    def mmClusterStationEta(self) -> func_adl_servicex_xaodr25.vector_int_.vector_int_:
        "A method"
        ...

    def mmClusterStationPhi(self) -> func_adl_servicex_xaodr25.vector_int_.vector_int_:
        "A method"
        ...

    def mmClusterStationName(self) -> func_adl_servicex_xaodr25.vector_int_.vector_int_:
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
