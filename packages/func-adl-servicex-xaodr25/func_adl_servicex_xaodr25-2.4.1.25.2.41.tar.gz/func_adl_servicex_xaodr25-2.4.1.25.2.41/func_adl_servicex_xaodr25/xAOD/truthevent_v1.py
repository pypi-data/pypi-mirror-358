from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr25

_method_map = {
    'weights': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthEvent_v1',
        'method_name': 'weights',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'crossSection': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthEvent_v1',
        'method_name': 'crossSection',
        'return_type': 'float',
    },
    'crossSectionError': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthEvent_v1',
        'method_name': 'crossSectionError',
        'return_type': 'float',
    },
    'pdfInfoParameter': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthEvent_v1',
        'method_name': 'pdfInfoParameter',
        'return_type': 'bool',
    },
    'setPdfInfoParameter': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthEvent_v1',
        'method_name': 'setPdfInfoParameter',
        'return_type': 'bool',
    },
    'pdfInfo': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthEvent_v1',
        'method_name': 'pdfInfo',
        'return_type': 'xAOD::TruthEvent_v1::PdfInfo',
    },
    'heavyIonParameter': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthEvent_v1',
        'method_name': 'heavyIonParameter',
        'return_type': 'bool',
    },
    'setHeavyIonParameter': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthEvent_v1',
        'method_name': 'setHeavyIonParameter',
        'return_type': 'bool',
    },
    'signalProcessVertex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthEvent_v1',
        'method_name': 'signalProcessVertex',
        'return_type': 'const xAOD::TruthVertex_v1 *',
    },
    'signalProcessVertexLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthEvent_v1',
        'method_name': 'signalProcessVertexLink',
        'return_type': 'const ElementLink<DataVector<xAOD::TruthVertex_v1>>',
    },
    'beamParticle1Link': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthEvent_v1',
        'method_name': 'beamParticle1Link',
        'return_type': 'const ElementLink<DataVector<xAOD::TruthParticle_v1>>',
    },
    'beamParticle2Link': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthEvent_v1',
        'method_name': 'beamParticle2Link',
        'return_type': 'const ElementLink<DataVector<xAOD::TruthParticle_v1>>',
    },
    'type': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthEvent_v1',
        'method_name': 'type',
        'return_type': 'xAODType::ObjectType',
    },
    'truthParticleLinks': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthEvent_v1',
        'method_name': 'truthParticleLinks',
        'return_type_element': 'ElementLink<DataVector<xAOD::TruthParticle_v1>>',
        'return_type_collection': 'const vector<ElementLink<DataVector<xAOD::TruthParticle_v1>>>',
    },
    'nTruthParticles': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthEvent_v1',
        'method_name': 'nTruthParticles',
        'return_type': 'unsigned int',
    },
    'truthParticleLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthEvent_v1',
        'method_name': 'truthParticleLink',
        'return_type': 'const ElementLink<DataVector<xAOD::TruthParticle_v1>>',
    },
    'truthParticle': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthEvent_v1',
        'method_name': 'truthParticle',
        'return_type': 'const xAOD::TruthParticle_v1 *',
    },
    'truthVertexLinks': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthEvent_v1',
        'method_name': 'truthVertexLinks',
        'return_type_element': 'ElementLink<DataVector<xAOD::TruthVertex_v1>>',
        'return_type_collection': 'const vector<ElementLink<DataVector<xAOD::TruthVertex_v1>>>',
    },
    'nTruthVertices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthEvent_v1',
        'method_name': 'nTruthVertices',
        'return_type': 'unsigned int',
    },
    'truthVertexLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthEvent_v1',
        'method_name': 'truthVertexLink',
        'return_type': 'const ElementLink<DataVector<xAOD::TruthVertex_v1>>',
    },
    'truthVertex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthEvent_v1',
        'method_name': 'truthVertex',
        'return_type': 'const xAOD::TruthVertex_v1 *',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthEvent_v1',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthEvent_v1',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthEvent_v1',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthEvent_v1',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthEvent_v1',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthEvent_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthEvent_v1',
        'method_name': 'trackIndices',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthEvent_v1',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthEvent_v1',
        'method_name': 'isAvailable',
        'return_type': 'bool',
    },
}

_enum_function_map = {
    'pdfInfoParameter': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.TruthEvent_v1',
            'name': 'PdfParam',
            'values': [
                'PDGID1',
                'PDGID2',
                'PDFID1',
                'PDFID2',
                'X1',
                'X2',
                'SCALE',
                'Q',
                'PDF1',
                'PDF2',
                'XF1',
                'XF2',
            ],
        },
    ],
    'setPdfInfoParameter': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.TruthEvent_v1',
            'name': 'PdfParam',
            'values': [
                'PDGID1',
                'PDGID2',
                'PDFID1',
                'PDFID2',
                'X1',
                'X2',
                'SCALE',
                'Q',
                'PDF1',
                'PDF2',
                'XF1',
                'XF2',
            ],
        },
    ],
    'heavyIonParameter': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.TruthEvent_v1',
            'name': 'HIParam',
            'values': [
                'NCOLLHARD',
                'NPARTPROJ',
                'NPARTTARG',
                'NCOLL',
                'SPECTATORNEUTRONS',
                'SPECTATORPROTONS',
                'NNWOUNDEDCOLLISIONS',
                'NWOUNDEDNCOLLISIONS',
                'NWOUNDEDNWOUNDEDCOLLISIONS',
                'IMPACTPARAMETER',
                'EVENTPLANEANGLE',
                'ECCENTRICITY',
                'SIGMAINELNN',
                'CENTRALITY',
            ],
        },
    ],
    'setHeavyIonParameter': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.TruthEvent_v1',
            'name': 'HIParam',
            'values': [
                'NCOLLHARD',
                'NPARTPROJ',
                'NPARTTARG',
                'NCOLL',
                'SPECTATORNEUTRONS',
                'SPECTATORPROTONS',
                'NNWOUNDEDCOLLISIONS',
                'NWOUNDEDNCOLLISIONS',
                'NWOUNDEDNWOUNDEDCOLLISIONS',
                'IMPACTPARAMETER',
                'EVENTPLANEANGLE',
                'ECCENTRICITY',
                'SIGMAINELNN',
                'CENTRALITY',
            ],
        },
    ],
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
    'PdfParam':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.TruthEvent_v1',
            'name': 'PdfParam',
            'values': [
                'PDGID1',
                'PDGID2',
                'PDFID1',
                'PDFID2',
                'X1',
                'X2',
                'SCALE',
                'Q',
                'PDF1',
                'PDF2',
                'XF1',
                'XF2',
            ],
        },
    'HIParam':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.TruthEvent_v1',
            'name': 'HIParam',
            'values': [
                'NCOLLHARD',
                'NPARTPROJ',
                'NPARTTARG',
                'NCOLL',
                'SPECTATORNEUTRONS',
                'SPECTATORPROTONS',
                'NNWOUNDEDCOLLISIONS',
                'NWOUNDEDNCOLLISIONS',
                'NWOUNDEDNWOUNDEDCOLLISIONS',
                'IMPACTPARAMETER',
                'EVENTPLANEANGLE',
                'ECCENTRICITY',
                'SIGMAINELNN',
                'CENTRALITY',
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
            'name': 'xAODTruth/versions/TruthEvent_v1.h',
            'body_includes': ["xAODTruth/versions/TruthEvent_v1.h"],
        })


        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODTruth',
            'link_libraries': ["xAODTruth"],
        })

        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class TruthEvent_v1:
    "A class"

    class PdfParam(Enum):
        PDGID1 = 0
        PDGID2 = 1
        PDFID1 = 2
        PDFID2 = 3
        X1 = 4
        X2 = 5
        SCALE = 6
        Q = 6
        PDF1 = 7
        PDF2 = 8
        XF1 = 7
        XF2 = 8

    class HIParam(Enum):
        NCOLLHARD = 0
        NPARTPROJ = 1
        NPARTTARG = 2
        NCOLL = 3
        SPECTATORNEUTRONS = 4
        SPECTATORPROTONS = 5
        NNWOUNDEDCOLLISIONS = 6
        NWOUNDEDNCOLLISIONS = 7
        NWOUNDEDNWOUNDEDCOLLISIONS = 8
        IMPACTPARAMETER = 9
        EVENTPLANEANGLE = 10
        ECCENTRICITY = 11
        SIGMAINELNN = 12
        CENTRALITY = 13


    def weights(self) -> func_adl_servicex_xaodr25.vector_float_.vector_float_:
        "A method"
        ...

    def crossSection(self) -> float:
        "A method"
        ...

    def crossSectionError(self) -> float:
        "A method"
        ...

    def pdfInfoParameter(self, value: int, parameter: func_adl_servicex_xaodr25.xAOD.truthevent_v1.TruthEvent_v1.PdfParam) -> bool:
        "A method"
        ...

    def setPdfInfoParameter(self, value: int, parameter: func_adl_servicex_xaodr25.xAOD.truthevent_v1.TruthEvent_v1.PdfParam) -> bool:
        "A method"
        ...

    def pdfInfo(self) -> func_adl_servicex_xaodr25.xAOD.TruthEvent_v1.pdfinfo.PdfInfo:
        "A method"
        ...

    def heavyIonParameter(self, value: int, parameter: func_adl_servicex_xaodr25.xAOD.truthevent_v1.TruthEvent_v1.HIParam) -> bool:
        "A method"
        ...

    def setHeavyIonParameter(self, value: int, parameter: func_adl_servicex_xaodr25.xAOD.truthevent_v1.TruthEvent_v1.HIParam) -> bool:
        "A method"
        ...

    def signalProcessVertex(self) -> func_adl_servicex_xaodr25.xAOD.truthvertex_v1.TruthVertex_v1:
        "A method"
        ...

    def signalProcessVertexLink(self) -> func_adl_servicex_xaodr25.elementlink_datavector_xaod_truthvertex_v1__.ElementLink_DataVector_xAOD_TruthVertex_v1__:
        "A method"
        ...

    def beamParticle1Link(self) -> func_adl_servicex_xaodr25.elementlink_datavector_xaod_truthparticle_v1__.ElementLink_DataVector_xAOD_TruthParticle_v1__:
        "A method"
        ...

    def beamParticle2Link(self) -> func_adl_servicex_xaodr25.elementlink_datavector_xaod_truthparticle_v1__.ElementLink_DataVector_xAOD_TruthParticle_v1__:
        "A method"
        ...

    def type(self) -> func_adl_servicex_xaodr25.xaodtype.xAODType.ObjectType:
        "A method"
        ...

    def truthParticleLinks(self) -> func_adl_servicex_xaodr25.vector_elementlink_datavector_xaod_truthparticle_v1___.vector_ElementLink_DataVector_xAOD_TruthParticle_v1___:
        "A method"
        ...

    def nTruthParticles(self) -> int:
        "A method"
        ...

    def truthParticleLink(self, index: int) -> func_adl_servicex_xaodr25.elementlink_datavector_xaod_truthparticle_v1__.ElementLink_DataVector_xAOD_TruthParticle_v1__:
        "A method"
        ...

    def truthParticle(self, index: int) -> func_adl_servicex_xaodr25.xAOD.truthparticle_v1.TruthParticle_v1:
        "A method"
        ...

    def truthVertexLinks(self) -> func_adl_servicex_xaodr25.vector_elementlink_datavector_xaod_truthvertex_v1___.vector_ElementLink_DataVector_xAOD_TruthVertex_v1___:
        "A method"
        ...

    def nTruthVertices(self) -> int:
        "A method"
        ...

    def truthVertexLink(self, index: int) -> func_adl_servicex_xaodr25.elementlink_datavector_xaod_truthvertex_v1__.ElementLink_DataVector_xAOD_TruthVertex_v1__:
        "A method"
        ...

    def truthVertex(self, index: int) -> func_adl_servicex_xaodr25.xAOD.truthvertex_v1.TruthVertex_v1:
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
