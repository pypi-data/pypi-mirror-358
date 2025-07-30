from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr25

_method_map = {
    'pt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'pt',
        'return_type': 'double',
    },
    'eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'eta',
        'return_type': 'double',
    },
    'phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'phi',
        'return_type': 'double',
    },
    'm': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'm',
        'return_type': 'double',
    },
    'e': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'e',
        'return_type': 'double',
    },
    'rapidity': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'rapidity',
        'return_type': 'double',
    },
    'p4': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'p4',
        'return_type': 'TLorentzVector',
    },
    'type': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'type',
        'return_type': 'xAODType::ObjectType',
    },
    'px': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'px',
        'return_type': 'double',
    },
    'py': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'py',
        'return_type': 'double',
    },
    'pz': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'pz',
        'return_type': 'double',
    },
    'et': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'et',
        'return_type': 'double',
    },
    'hasCharge': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'hasCharge',
        'return_type': 'bool',
    },
    'charge': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'charge',
        'return_type': 'float',
    },
    'hasPdgId': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'hasPdgId',
        'return_type': 'bool',
    },
    'pdgId': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'pdgId',
        'return_type': 'int',
    },
    'p': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'p',
        'return_type': 'double',
    },
    'mt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'mt',
        'return_type': 'double',
    },
    'weight': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'weight',
        'return_type': 'float',
    },
    'missingET': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'missingET',
        'return_type': 'const xAOD::MissingET_v1 *',
    },
    'contains': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'contains',
        'return_type': 'bool',
    },
    'nParts': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'nParts',
        'return_type': 'unsigned int',
    },
    'nCompParts': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'nCompParts',
        'return_type': 'unsigned int',
    },
    'nPhotons': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'nPhotons',
        'return_type': 'unsigned int',
    },
    'nTruthPhotons': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'nTruthPhotons',
        'return_type': 'unsigned int',
    },
    'nElectrons': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'nElectrons',
        'return_type': 'unsigned int',
    },
    'nTruthElectrons': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'nTruthElectrons',
        'return_type': 'unsigned int',
    },
    'nMuons': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'nMuons',
        'return_type': 'unsigned int',
    },
    'nTruthMuons': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'nTruthMuons',
        'return_type': 'unsigned int',
    },
    'nTaus': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'nTaus',
        'return_type': 'unsigned int',
    },
    'nTruthTaus': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'nTruthTaus',
        'return_type': 'unsigned int',
    },
    'nLeptons': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'nLeptons',
        'return_type': 'unsigned int',
    },
    'nTruthLeptons': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'nTruthLeptons',
        'return_type': 'unsigned int',
    },
    'nJets': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'nJets',
        'return_type': 'unsigned int',
    },
    'nTruthParts': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'nTruthParts',
        'return_type': 'unsigned int',
    },
    'part': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'part',
        'return_type': 'const xAOD::IParticle *',
    },
    'partLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'partLink',
        'return_type': 'const ElementLink<DataVector<xAOD::IParticle>>',
    },
    'partLinks': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'partLinks',
        'return_type_element': 'ElementLink<DataVector<xAOD::IParticle>>',
        'return_type_collection': 'const vector<ElementLink<DataVector<xAOD::IParticle>>>',
    },
    'compPart': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'compPart',
        'return_type': 'xAOD::CompositeParticle_v1 *',
    },
    'photon': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'photon',
        'return_type': 'const xAOD::Photon_v1 *',
    },
    'electron': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'electron',
        'return_type': 'const xAOD::Electron_v1 *',
    },
    'muon': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'muon',
        'return_type': 'const xAOD::Muon_v1 *',
    },
    'tau': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'tau',
        'return_type': 'const xAOD::TauJet_v3 *',
    },
    'jet': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'jet',
        'return_type': 'const xAOD::Jet_v1 *',
    },
    'truthPart': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'truthPart',
        'return_type': 'const xAOD::TruthParticle_v1 *',
    },
    'containsOther': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'containsOther',
        'return_type': 'bool',
    },
    'nOtherParts': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'nOtherParts',
        'return_type': 'unsigned int',
    },
    'nOtherCompParts': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'nOtherCompParts',
        'return_type': 'unsigned int',
    },
    'nOtherPhotons': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'nOtherPhotons',
        'return_type': 'unsigned int',
    },
    'nOtherTruthPhotons': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'nOtherTruthPhotons',
        'return_type': 'unsigned int',
    },
    'nOtherElectrons': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'nOtherElectrons',
        'return_type': 'unsigned int',
    },
    'nOtherTruthElectrons': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'nOtherTruthElectrons',
        'return_type': 'unsigned int',
    },
    'nOtherMuons': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'nOtherMuons',
        'return_type': 'unsigned int',
    },
    'nOtherTruthMuons': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'nOtherTruthMuons',
        'return_type': 'unsigned int',
    },
    'nOtherTaus': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'nOtherTaus',
        'return_type': 'unsigned int',
    },
    'nOtherTruthTaus': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'nOtherTruthTaus',
        'return_type': 'unsigned int',
    },
    'nOtherLeptons': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'nOtherLeptons',
        'return_type': 'unsigned int',
    },
    'nOtherTruthLeptons': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'nOtherTruthLeptons',
        'return_type': 'unsigned int',
    },
    'nOtherJets': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'nOtherJets',
        'return_type': 'unsigned int',
    },
    'nOtherTruthParts': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'nOtherTruthParts',
        'return_type': 'unsigned int',
    },
    'otherPart': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'otherPart',
        'return_type': 'const xAOD::IParticle *',
    },
    'otherPartLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'otherPartLink',
        'return_type': 'const ElementLink<DataVector<xAOD::IParticle>>',
    },
    'otherPartLinks': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'otherPartLinks',
        'return_type_element': 'ElementLink<DataVector<xAOD::IParticle>>',
        'return_type_collection': 'const vector<ElementLink<DataVector<xAOD::IParticle>>>',
    },
    'otherCompPart': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'otherCompPart',
        'return_type': 'const xAOD::CompositeParticle_v1 *',
    },
    'otherPhoton': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'otherPhoton',
        'return_type': 'const xAOD::Photon_v1 *',
    },
    'otherElectron': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'otherElectron',
        'return_type': 'const xAOD::Electron_v1 *',
    },
    'otherMuon': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'otherMuon',
        'return_type': 'const xAOD::Muon_v1 *',
    },
    'otherTau': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'otherTau',
        'return_type': 'const xAOD::TauJet_v3 *',
    },
    'otherJet': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'otherJet',
        'return_type': 'const xAOD::Jet_v1 *',
    },
    'otherTruthPart': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'otherTruthPart',
        'return_type': 'const xAOD::TruthParticle_v1 *',
    },
    'getBool': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'getBool',
        'return_type': 'bool',
    },
    'getInt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'getInt',
        'return_type': 'int',
    },
    'getUInt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'getUInt',
        'return_type': 'unsigned int',
    },
    'getFloat': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'getFloat',
        'return_type': 'float',
    },
    'getDouble': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'getDouble',
        'return_type': 'double',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'trackIndices',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CompositeParticle_v1',
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
    'mt': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.CompositeParticle_v1.MT',
            'name': 'Method',
            'values': [
                'DEFAULT',
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
            'name': 'xAODParticleEvent/versions/CompositeParticle_v1.h',
            'body_includes': ["xAODParticleEvent/versions/CompositeParticle_v1.h"],
        })


        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODParticleEvent',
            'link_libraries': ["xAODParticleEvent"],
        })

        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class CompositeParticle_v1:
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

    def et(self) -> float:
        "A method"
        ...

    def hasCharge(self) -> bool:
        "A method"
        ...

    def charge(self) -> float:
        "A method"
        ...

    def hasPdgId(self) -> bool:
        "A method"
        ...

    def pdgId(self) -> int:
        "A method"
        ...

    def p(self, partIndices: func_adl_servicex_xaodr25.vector_int_.vector_int_) -> float:
        "A method"
        ...

    def mt(self, partIndices: func_adl_servicex_xaodr25.vector_int_.vector_int_, method: func_adl_servicex_xaodr25.xAOD.CompositeParticle_v1.mt.MT.Method) -> float:
        "A method"
        ...

    def weight(self, varNames: func_adl_servicex_xaodr25.vector_str_.vector_str_, partIndices: func_adl_servicex_xaodr25.vector_int_.vector_int_) -> float:
        "A method"
        ...

    def missingET(self) -> func_adl_servicex_xaodr25.xAOD.missinget_v1.MissingET_v1:
        "A method"
        ...

    def contains(self, met: func_adl_servicex_xaodr25.xAOD.missinget_v1.MissingET_v1) -> bool:
        "A method"
        ...

    def nParts(self) -> int:
        "A method"
        ...

    def nCompParts(self) -> int:
        "A method"
        ...

    def nPhotons(self) -> int:
        "A method"
        ...

    def nTruthPhotons(self) -> int:
        "A method"
        ...

    def nElectrons(self) -> int:
        "A method"
        ...

    def nTruthElectrons(self) -> int:
        "A method"
        ...

    def nMuons(self) -> int:
        "A method"
        ...

    def nTruthMuons(self) -> int:
        "A method"
        ...

    def nTaus(self) -> int:
        "A method"
        ...

    def nTruthTaus(self) -> int:
        "A method"
        ...

    def nLeptons(self) -> int:
        "A method"
        ...

    def nTruthLeptons(self) -> int:
        "A method"
        ...

    def nJets(self) -> int:
        "A method"
        ...

    def nTruthParts(self) -> int:
        "A method"
        ...

    def part(self, index: int) -> func_adl_servicex_xaodr25.xAOD.iparticle.IParticle:
        "A method"
        ...

    def partLink(self, index: int) -> func_adl_servicex_xaodr25.elementlink_datavector_xaod_iparticle__.ElementLink_DataVector_xAOD_IParticle__:
        "A method"
        ...

    def partLinks(self) -> func_adl_servicex_xaodr25.vector_elementlink_datavector_xaod_iparticle___.vector_ElementLink_DataVector_xAOD_IParticle___:
        "A method"
        ...

    def compPart(self, partIndices: func_adl_servicex_xaodr25.vector_int_.vector_int_, otherPartIndices: func_adl_servicex_xaodr25.vector_int_.vector_int_, updateFourMom: bool) -> func_adl_servicex_xaodr25.xAOD.compositeparticle_v1.CompositeParticle_v1:
        "A method"
        ...

    def photon(self, index: int) -> func_adl_servicex_xaodr25.xAOD.photon_v1.Photon_v1:
        "A method"
        ...

    def electron(self, index: int) -> func_adl_servicex_xaodr25.xAOD.electron_v1.Electron_v1:
        "A method"
        ...

    def muon(self, index: int) -> func_adl_servicex_xaodr25.xAOD.muon_v1.Muon_v1:
        "A method"
        ...

    def tau(self, index: int) -> func_adl_servicex_xaodr25.xAOD.taujet_v3.TauJet_v3:
        "A method"
        ...

    def jet(self, index: int) -> func_adl_servicex_xaodr25.xAOD.jet_v1.Jet_v1:
        "A method"
        ...

    def truthPart(self, index: int) -> func_adl_servicex_xaodr25.xAOD.truthparticle_v1.TruthParticle_v1:
        "A method"
        ...

    def containsOther(self, part: func_adl_servicex_xaodr25.xAOD.iparticle.IParticle) -> bool:
        "A method"
        ...

    def nOtherParts(self) -> int:
        "A method"
        ...

    def nOtherCompParts(self) -> int:
        "A method"
        ...

    def nOtherPhotons(self) -> int:
        "A method"
        ...

    def nOtherTruthPhotons(self) -> int:
        "A method"
        ...

    def nOtherElectrons(self) -> int:
        "A method"
        ...

    def nOtherTruthElectrons(self) -> int:
        "A method"
        ...

    def nOtherMuons(self) -> int:
        "A method"
        ...

    def nOtherTruthMuons(self) -> int:
        "A method"
        ...

    def nOtherTaus(self) -> int:
        "A method"
        ...

    def nOtherTruthTaus(self) -> int:
        "A method"
        ...

    def nOtherLeptons(self) -> int:
        "A method"
        ...

    def nOtherTruthLeptons(self) -> int:
        "A method"
        ...

    def nOtherJets(self) -> int:
        "A method"
        ...

    def nOtherTruthParts(self) -> int:
        "A method"
        ...

    def otherPart(self, index: int) -> func_adl_servicex_xaodr25.xAOD.iparticle.IParticle:
        "A method"
        ...

    def otherPartLink(self, index: int) -> func_adl_servicex_xaodr25.elementlink_datavector_xaod_iparticle__.ElementLink_DataVector_xAOD_IParticle__:
        "A method"
        ...

    def otherPartLinks(self) -> func_adl_servicex_xaodr25.vector_elementlink_datavector_xaod_iparticle___.vector_ElementLink_DataVector_xAOD_IParticle___:
        "A method"
        ...

    def otherCompPart(self, index: int) -> func_adl_servicex_xaodr25.xAOD.compositeparticle_v1.CompositeParticle_v1:
        "A method"
        ...

    def otherPhoton(self, index: int) -> func_adl_servicex_xaodr25.xAOD.photon_v1.Photon_v1:
        "A method"
        ...

    def otherElectron(self, index: int) -> func_adl_servicex_xaodr25.xAOD.electron_v1.Electron_v1:
        "A method"
        ...

    def otherMuon(self, index: int) -> func_adl_servicex_xaodr25.xAOD.muon_v1.Muon_v1:
        "A method"
        ...

    def otherTau(self, index: int) -> func_adl_servicex_xaodr25.xAOD.taujet_v3.TauJet_v3:
        "A method"
        ...

    def otherJet(self, index: int) -> func_adl_servicex_xaodr25.xAOD.jet_v1.Jet_v1:
        "A method"
        ...

    def otherTruthPart(self, index: int) -> func_adl_servicex_xaodr25.xAOD.truthparticle_v1.TruthParticle_v1:
        "A method"
        ...

    def getBool(self, varName: str) -> bool:
        "A method"
        ...

    def getInt(self, varName: str) -> int:
        "A method"
        ...

    def getUInt(self, varName: str) -> int:
        "A method"
        ...

    def getFloat(self, varName: str) -> float:
        "A method"
        ...

    def getDouble(self, varName: str) -> float:
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
