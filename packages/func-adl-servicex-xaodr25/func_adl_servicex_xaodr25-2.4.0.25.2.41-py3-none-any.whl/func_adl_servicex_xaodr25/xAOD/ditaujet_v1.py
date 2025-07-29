from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr25

_method_map = {
    'pt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::DiTauJet_v1',
        'method_name': 'pt',
        'return_type': 'double',
    },
    'eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::DiTauJet_v1',
        'method_name': 'eta',
        'return_type': 'double',
    },
    'phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::DiTauJet_v1',
        'method_name': 'phi',
        'return_type': 'double',
    },
    'e': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::DiTauJet_v1',
        'method_name': 'e',
        'return_type': 'double',
    },
    'm': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::DiTauJet_v1',
        'method_name': 'm',
        'return_type': 'double',
    },
    'rapidity': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::DiTauJet_v1',
        'method_name': 'rapidity',
        'return_type': 'double',
    },
    'p4': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::DiTauJet_v1',
        'method_name': 'p4',
        'return_type': 'TLorentzVector',
    },
    'type': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::DiTauJet_v1',
        'method_name': 'type',
        'return_type': 'xAODType::ObjectType',
    },
    'jetLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::DiTauJet_v1',
        'method_name': 'jetLink',
        'return_type': 'const ElementLink<DataVector<xAOD::Jet_v1>>',
    },
    'jet': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::DiTauJet_v1',
        'method_name': 'jet',
        'return_type': 'const xAOD::Jet_v1 *',
    },
    'subjetPt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::DiTauJet_v1',
        'method_name': 'subjetPt',
        'return_type': 'float',
    },
    'subjetEta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::DiTauJet_v1',
        'method_name': 'subjetEta',
        'return_type': 'float',
    },
    'subjetPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::DiTauJet_v1',
        'method_name': 'subjetPhi',
        'return_type': 'float',
    },
    'subjetE': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::DiTauJet_v1',
        'method_name': 'subjetE',
        'return_type': 'float',
    },
    'nSubjets': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::DiTauJet_v1',
        'method_name': 'nSubjets',
        'return_type': 'float',
    },
    'fCore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::DiTauJet_v1',
        'method_name': 'fCore',
        'return_type': 'float',
    },
    'vertexLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::DiTauJet_v1',
        'method_name': 'vertexLink',
        'return_type': 'const ElementLink<DataVector<xAOD::Vertex_v1>>',
    },
    'vertex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::DiTauJet_v1',
        'method_name': 'vertex',
        'return_type': 'const xAOD::Vertex_v1 *',
    },
    'trackLinks': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::DiTauJet_v1',
        'method_name': 'trackLinks',
        'return_type_element': 'ElementLink<DataVector<xAOD::TrackParticle_v1>>',
        'return_type_collection': 'const vector<ElementLink<DataVector<xAOD::TrackParticle_v1>>>',
    },
    'track': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::DiTauJet_v1',
        'method_name': 'track',
        'return_type': 'const xAOD::TrackParticle_v1 *',
    },
    'nTracks': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::DiTauJet_v1',
        'method_name': 'nTracks',
        'return_type': 'unsigned int',
    },
    'otherTrackLinks': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::DiTauJet_v1',
        'method_name': 'otherTrackLinks',
        'return_type_element': 'ElementLink<DataVector<xAOD::TrackParticle_v1>>',
        'return_type_collection': 'const vector<ElementLink<DataVector<xAOD::TrackParticle_v1>>>',
    },
    'otherTrack': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::DiTauJet_v1',
        'method_name': 'otherTrack',
        'return_type': 'const xAOD::TrackParticle_v1 *',
    },
    'nOtherTracks': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::DiTauJet_v1',
        'method_name': 'nOtherTracks',
        'return_type': 'unsigned int',
    },
    'isoTrackLinks': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::DiTauJet_v1',
        'method_name': 'isoTrackLinks',
        'return_type_element': 'ElementLink<DataVector<xAOD::TrackParticle_v1>>',
        'return_type_collection': 'const vector<ElementLink<DataVector<xAOD::TrackParticle_v1>>>',
    },
    'isoTrack': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::DiTauJet_v1',
        'method_name': 'isoTrack',
        'return_type': 'const xAOD::TrackParticle_v1 *',
    },
    'nIsoTracks': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::DiTauJet_v1',
        'method_name': 'nIsoTracks',
        'return_type': 'unsigned int',
    },
    'detail': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::DiTauJet_v1',
        'method_name': 'detail',
        'return_type': 'bool',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::DiTauJet_v1',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::DiTauJet_v1',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::DiTauJet_v1',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::DiTauJet_v1',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::DiTauJet_v1',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::DiTauJet_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::DiTauJet_v1',
        'method_name': 'trackIndices',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::DiTauJet_v1',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::DiTauJet_v1',
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
    'detail': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.DiTauJetParameters',
            'name': 'Detail',
            'values': [
                'TauJetVtxFraction',
                'R_jet',
                'R_subjet',
                'R_core',
                'BDT',
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
            'name': 'xAODTau/versions/DiTauJet_v1.h',
            'body_includes': ["xAODTau/versions/DiTauJet_v1.h"],
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
class DiTauJet_v1:
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

    def type(self) -> func_adl_servicex_xaodr25.xaodtype.xAODType.ObjectType:
        "A method"
        ...

    def jetLink(self) -> func_adl_servicex_xaodr25.elementlink_datavector_xaod_jet_v1__.ElementLink_DataVector_xAOD_Jet_v1__:
        "A method"
        ...

    def jet(self) -> func_adl_servicex_xaodr25.xAOD.jet_v1.Jet_v1:
        "A method"
        ...

    def subjetPt(self, numSubjet: int) -> float:
        "A method"
        ...

    def subjetEta(self, numSubjet: int) -> float:
        "A method"
        ...

    def subjetPhi(self, numSubjet: int) -> float:
        "A method"
        ...

    def subjetE(self, numSubjet: int) -> float:
        "A method"
        ...

    def nSubjets(self) -> float:
        "A method"
        ...

    def fCore(self, numSubjet: int) -> float:
        "A method"
        ...

    def vertexLink(self) -> func_adl_servicex_xaodr25.elementlink_datavector_xaod_vertex_v1__.ElementLink_DataVector_xAOD_Vertex_v1__:
        "A method"
        ...

    def vertex(self) -> func_adl_servicex_xaodr25.xAOD.vertex_v1.Vertex_v1:
        "A method"
        ...

    def trackLinks(self) -> func_adl_servicex_xaodr25.vector_elementlink_datavector_xaod_trackparticle_v1___.vector_ElementLink_DataVector_xAOD_TrackParticle_v1___:
        "A method"
        ...

    def track(self, i: int) -> func_adl_servicex_xaodr25.xAOD.trackparticle_v1.TrackParticle_v1:
        "A method"
        ...

    def nTracks(self) -> int:
        "A method"
        ...

    def otherTrackLinks(self) -> func_adl_servicex_xaodr25.vector_elementlink_datavector_xaod_trackparticle_v1___.vector_ElementLink_DataVector_xAOD_TrackParticle_v1___:
        "A method"
        ...

    def otherTrack(self, i: int) -> func_adl_servicex_xaodr25.xAOD.trackparticle_v1.TrackParticle_v1:
        "A method"
        ...

    def nOtherTracks(self) -> int:
        "A method"
        ...

    def isoTrackLinks(self) -> func_adl_servicex_xaodr25.vector_elementlink_datavector_xaod_trackparticle_v1___.vector_ElementLink_DataVector_xAOD_TrackParticle_v1___:
        "A method"
        ...

    def isoTrack(self, i: int) -> func_adl_servicex_xaodr25.xAOD.trackparticle_v1.TrackParticle_v1:
        "A method"
        ...

    def nIsoTracks(self) -> int:
        "A method"
        ...

    def detail(self, detail: func_adl_servicex_xaodr25.xAOD.ditaujetparameters.DiTauJetParameters.Detail, value: int) -> bool:
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
