from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr25

_method_map = {
    'pt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Jet_v1',
        'method_name': 'pt',
        'return_type': 'double',
    },
    'eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Jet_v1',
        'method_name': 'eta',
        'return_type': 'double',
    },
    'phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Jet_v1',
        'method_name': 'phi',
        'return_type': 'double',
    },
    'm': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Jet_v1',
        'method_name': 'm',
        'return_type': 'double',
    },
    'e': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Jet_v1',
        'method_name': 'e',
        'return_type': 'double',
    },
    'rapidity': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Jet_v1',
        'method_name': 'rapidity',
        'return_type': 'double',
    },
    'p4': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Jet_v1',
        'method_name': 'p4',
        'return_type': 'TLorentzVector',
    },
    'type': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Jet_v1',
        'method_name': 'type',
        'return_type': 'xAODType::ObjectType',
    },
    'px': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Jet_v1',
        'method_name': 'px',
        'return_type': 'float',
    },
    'py': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Jet_v1',
        'method_name': 'py',
        'return_type': 'float',
    },
    'pz': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Jet_v1',
        'method_name': 'pz',
        'return_type': 'float',
    },
    'getConstituentsSignalState': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Jet_v1',
        'method_name': 'getConstituentsSignalState',
        'return_type': 'xAOD::JetConstitScale',
    },
    'getConstituents': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Jet_v1',
        'method_name': 'getConstituents',
        'return_type_element': 'xAOD::JetConstituent *',
        'return_type_collection': 'xAOD::JetConstituentVector',
    },
    'numConstituents': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Jet_v1',
        'method_name': 'numConstituents',
        'return_type': 'unsigned int',
    },
    'rawConstituent': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Jet_v1',
        'method_name': 'rawConstituent',
        'return_type': 'const xAOD::IParticle *',
    },
    'constituentLinks': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Jet_v1',
        'method_name': 'constituentLinks',
        'return_type_element': 'ElementLink<DataVector<xAOD::IParticle>>',
        'return_type_collection': 'const vector<ElementLink<DataVector<xAOD::IParticle>>>',
    },
    'getSizeParameter': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Jet_v1',
        'method_name': 'getSizeParameter',
        'return_type': 'float',
    },
    'getAlgorithmType': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Jet_v1',
        'method_name': 'getAlgorithmType',
        'return_type': 'xAOD::JetAlgorithmType::ID',
    },
    'getInputType': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Jet_v1',
        'method_name': 'getInputType',
        'return_type': 'xAOD::JetInput::Type',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Jet_v1',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Jet_v1',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Jet_v1',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Jet_v1',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Jet_v1',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Jet_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Jet_v1',
        'method_name': 'trackIndices',
        'return_type': 'bool',
    },
    'getAttribute': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Jet_v1',
        'method_name': 'getAttribute',
        'return_type': 'U',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Jet_v1',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Jet_v1',
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
    'getConstituentsSignalState': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD',
            'name': 'JetConstitScale',
            'values': [
                'UncalibratedJetConstituent',
                'CalibratedJetConstituent',
                'UnknownConstitScale',
            ],
        },
    ],
    'getAlgorithmType': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.JetAlgorithmType',
            'name': 'ID',
            'values': [
                'kt_algorithm',
                'cambridge_algorithm',
                'antikt_algorithm',
                'genkt_algorithm',
                'cambridge_for_passive_algorithm',
                'genkt_for_passive_algorithm',
                'ee_kt_algorithm',
                'ee_genkt_algorithm',
                'plugin_algorithm',
                'undefined_jet_algorithm',
            ],
        },
    ],
    'getInputType': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.JetInput',
            'name': 'Type',
            'values': [
                'LCTopo',
                'EMTopo',
                'TopoTower',
                'Tower',
                'Truth',
                'TruthWZ',
                'Track',
                'PFlow',
                'LCPFlow',
                'EMPFlow',
                'EMCPFlow',
                'Jet',
                'LCTopoOrigin',
                'EMTopoOrigin',
                'TrackCaloCluster',
                'TruthDressedWZ',
                'EMTopoOriginSK',
                'EMTopoOriginCS',
                'EMTopoOriginVor',
                'EMTopoOriginCSSK',
                'EMTopoOriginVorSK',
                'LCTopoOriginSK',
                'LCTopoOriginCS',
                'LCTopoOriginVor',
                'LCTopoOriginCSSK',
                'LCTopoOriginVorSK',
                'EMPFlowSK',
                'EMPFlowCS',
                'EMPFlowVor',
                'EMPFlowCSSK',
                'EMPFlowVorSK',
                'TruthCharged',
                'EMTopoOriginTime',
                'EMTopoOriginSKTime',
                'EMTopoOriginCSSKTime',
                'EMTopoOriginVorSKTime',
                'EMPFlowTime',
                'EMPFlowSKTime',
                'EMPFlowCSSKTime',
                'EMPFlowVorSKTime',
                'HI',
                'HIClusters',
                'PFlowCustomVtx',
                'EMPFlowByVertex',
                'Other',
                'Uncategorized',
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
            'name': 'xAODJet/versions/Jet_v1.h',
            'body_includes': ["xAODJet/versions/Jet_v1.h"],
        })


        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODJet',
            'link_libraries': ["xAODJet"],
        })

        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class Jet_v1:
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

    def px(self) -> float:
        "A method"
        ...

    def py(self) -> float:
        "A method"
        ...

    def pz(self) -> float:
        "A method"
        ...

    def getConstituentsSignalState(self) -> func_adl_servicex_xaodr25.xaod.xAOD.JetConstitScale:
        "A method"
        ...

    def getConstituents(self) -> func_adl_servicex_xaodr25.xAOD.jetconstituentvector.JetConstituentVector:
        "A method"
        ...

    def numConstituents(self) -> int:
        "A method"
        ...

    def rawConstituent(self, i: int) -> func_adl_servicex_xaodr25.xAOD.iparticle.IParticle:
        "A method"
        ...

    def constituentLinks(self) -> func_adl_servicex_xaodr25.vector_elementlink_datavector_xaod_iparticle___.vector_ElementLink_DataVector_xAOD_IParticle___:
        "A method"
        ...

    def getSizeParameter(self) -> float:
        "A method"
        ...

    def getAlgorithmType(self) -> func_adl_servicex_xaodr25.xAOD.jetalgorithmtype.JetAlgorithmType.ID:
        "A method"
        ...

    def getInputType(self) -> func_adl_servicex_xaodr25.xAOD.jetinput.JetInput.Type:
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

    @func_adl_parameterized_call(lambda s, a, param_1: func_adl_servicex_xaodr25.type_support.cpp_generic_1arg_callback('getAttribute', s, a, param_1))
    @property
    def getAttribute(self) -> func_adl_servicex_xaodr25.type_support.index_type_forwarder[str]:
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
