from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr25

_method_map = {
    'pdgId': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'pdgId',
        'return_type': 'int',
    },
    'pdg_id': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'pdg_id',
        'return_type': 'int',
    },
    'absPdgId': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'absPdgId',
        'return_type': 'int',
    },
    'barcode': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'barcode',
        'return_type': 'int',
    },
    'id': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'id',
        'return_type': 'int',
    },
    'status': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'status',
        'return_type': 'int',
    },
    'hasProdVtx': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'hasProdVtx',
        'return_type': 'bool',
    },
    'prodVtx': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'prodVtx',
        'return_type': 'const xAOD::TruthVertex_v1 *',
    },
    'production_vertex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'production_vertex',
        'return_type': 'const xAOD::TruthVertex_v1 *',
    },
    'prodVtxLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'prodVtxLink',
        'return_type': 'const ElementLink<DataVector<xAOD::TruthVertex_v1>>',
    },
    'hasDecayVtx': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'hasDecayVtx',
        'return_type': 'bool',
    },
    'decayVtx': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'decayVtx',
        'return_type': 'const xAOD::TruthVertex_v1 *',
    },
    'end_vertex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'end_vertex',
        'return_type': 'const xAOD::TruthVertex_v1 *',
    },
    'decayVtxLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'decayVtxLink',
        'return_type': 'const ElementLink<DataVector<xAOD::TruthVertex_v1>>',
    },
    'nParents': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'nParents',
        'return_type': 'unsigned int',
    },
    'parent': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'parent',
        'return_type': 'const xAOD::TruthParticle_v1 *',
    },
    'nChildren': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'nChildren',
        'return_type': 'unsigned int',
    },
    'child': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'child',
        'return_type': 'const xAOD::TruthParticle_v1 *',
    },
    'pt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'pt',
        'return_type': 'double',
    },
    'eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'eta',
        'return_type': 'double',
    },
    'phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'phi',
        'return_type': 'double',
    },
    'm': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'm',
        'return_type': 'double',
    },
    'e': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'e',
        'return_type': 'double',
    },
    'rapidity': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'rapidity',
        'return_type': 'double',
    },
    'p4': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'p4',
        'return_type': 'TLorentzVector',
    },
    'type': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'type',
        'return_type': 'xAODType::ObjectType',
    },
    'abseta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'abseta',
        'return_type': 'double',
    },
    'absrapidity': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'absrapidity',
        'return_type': 'double',
    },
    'px': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'px',
        'return_type': 'float',
    },
    'py': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'py',
        'return_type': 'float',
    },
    'pz': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'pz',
        'return_type': 'float',
    },
    'charge': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'charge',
        'return_type': 'double',
    },
    'threeCharge': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'threeCharge',
        'return_type': 'int',
    },
    'isCharged': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'isCharged',
        'return_type': 'bool',
    },
    'isNeutral': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'isNeutral',
        'return_type': 'bool',
    },
    'isPhoton': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'isPhoton',
        'return_type': 'bool',
    },
    'isLepton': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'isLepton',
        'return_type': 'bool',
    },
    'isChLepton': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'isChLepton',
        'return_type': 'bool',
    },
    'isElectron': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'isElectron',
        'return_type': 'bool',
    },
    'isMuon': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'isMuon',
        'return_type': 'bool',
    },
    'isTau': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'isTau',
        'return_type': 'bool',
    },
    'isNeutrino': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'isNeutrino',
        'return_type': 'bool',
    },
    'isHadron': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'isHadron',
        'return_type': 'bool',
    },
    'isMeson': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'isMeson',
        'return_type': 'bool',
    },
    'isBaryon': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'isBaryon',
        'return_type': 'bool',
    },
    'hasStrange': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'hasStrange',
        'return_type': 'bool',
    },
    'hasCharm': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'hasCharm',
        'return_type': 'bool',
    },
    'hasBottom': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'hasBottom',
        'return_type': 'bool',
    },
    'isLightMeson': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'isLightMeson',
        'return_type': 'bool',
    },
    'isLightBaryon': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'isLightBaryon',
        'return_type': 'bool',
    },
    'isLightHadron': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'isLightHadron',
        'return_type': 'bool',
    },
    'isHeavyMeson': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'isHeavyMeson',
        'return_type': 'bool',
    },
    'isHeavyBaryon': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'isHeavyBaryon',
        'return_type': 'bool',
    },
    'isHeavyHadron': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'isHeavyHadron',
        'return_type': 'bool',
    },
    'isBottomMeson': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'isBottomMeson',
        'return_type': 'bool',
    },
    'isBottomBaryon': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'isBottomBaryon',
        'return_type': 'bool',
    },
    'isBottomHadron': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'isBottomHadron',
        'return_type': 'bool',
    },
    'isCharmMeson': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'isCharmMeson',
        'return_type': 'bool',
    },
    'isCharmBaryon': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'isCharmBaryon',
        'return_type': 'bool',
    },
    'isCharmHadron': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'isCharmHadron',
        'return_type': 'bool',
    },
    'isStrangeMeson': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'isStrangeMeson',
        'return_type': 'bool',
    },
    'isStrangeBaryon': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'isStrangeBaryon',
        'return_type': 'bool',
    },
    'isStrangeHadron': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'isStrangeHadron',
        'return_type': 'bool',
    },
    'isQuark': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'isQuark',
        'return_type': 'bool',
    },
    'isParton': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'isParton',
        'return_type': 'bool',
    },
    'isTop': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'isTop',
        'return_type': 'bool',
    },
    'isW': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'isW',
        'return_type': 'bool',
    },
    'isZ': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'isZ',
        'return_type': 'bool',
    },
    'isHiggs': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'isHiggs',
        'return_type': 'bool',
    },
    'isResonance': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'isResonance',
        'return_type': 'bool',
    },
    'isGenSpecific': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'isGenSpecific',
        'return_type': 'bool',
    },
    'isBSM': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'isBSM',
        'return_type': 'bool',
    },
    'isGenStable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'isGenStable',
        'return_type': 'bool',
    },
    'polarizationParameter': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'polarizationParameter',
        'return_type': 'bool',
    },
    'setPolarizationParameter': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'setPolarizationParameter',
        'return_type': 'bool',
    },
    'polarization': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'polarization',
        'return_type': 'xAOD::TruthParticle_v1::Polarization',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'trackIndices',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TruthParticle_v1',
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
    'polarizationParameter': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.TruthParticle_v1',
            'name': 'PolParam',
            'values': [
                'polarizationPhi',
                'polarizationTheta',
            ],
        },
    ],
    'setPolarizationParameter': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.TruthParticle_v1',
            'name': 'PolParam',
            'values': [
                'polarizationPhi',
                'polarizationTheta',
            ],
        },
    ],      
}

_defined_enums = {
    'PolParam':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.TruthParticle_v1',
            'name': 'PolParam',
            'values': [
                'polarizationPhi',
                'polarizationTheta',
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
            'name': 'xAODTruth/versions/TruthParticle_v1.h',
            'body_includes': ["xAODTruth/versions/TruthParticle_v1.h"],
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
class TruthParticle_v1:
    "A class"

    class PolParam(Enum):
        polarizationPhi = 0
        polarizationTheta = 1


    def pdgId(self) -> int:
        "A method"
        ...

    def pdg_id(self) -> int:
        "A method"
        ...

    def absPdgId(self) -> int:
        "A method"
        ...

    def barcode(self) -> int:
        "A method"
        ...

    def id(self) -> int:
        "A method"
        ...

    def status(self) -> int:
        "A method"
        ...

    def hasProdVtx(self) -> bool:
        "A method"
        ...

    def prodVtx(self) -> func_adl_servicex_xaodr25.xAOD.truthvertex_v1.TruthVertex_v1:
        "A method"
        ...

    def production_vertex(self) -> func_adl_servicex_xaodr25.xAOD.truthvertex_v1.TruthVertex_v1:
        "A method"
        ...

    def prodVtxLink(self) -> func_adl_servicex_xaodr25.elementlink_datavector_xaod_truthvertex_v1__.ElementLink_DataVector_xAOD_TruthVertex_v1__:
        "A method"
        ...

    def hasDecayVtx(self) -> bool:
        "A method"
        ...

    def decayVtx(self) -> func_adl_servicex_xaodr25.xAOD.truthvertex_v1.TruthVertex_v1:
        "A method"
        ...

    def end_vertex(self) -> func_adl_servicex_xaodr25.xAOD.truthvertex_v1.TruthVertex_v1:
        "A method"
        ...

    def decayVtxLink(self) -> func_adl_servicex_xaodr25.elementlink_datavector_xaod_truthvertex_v1__.ElementLink_DataVector_xAOD_TruthVertex_v1__:
        "A method"
        ...

    def nParents(self) -> int:
        "A method"
        ...

    def parent(self, i: int) -> func_adl_servicex_xaodr25.xAOD.truthparticle_v1.TruthParticle_v1:
        "A method"
        ...

    def nChildren(self) -> int:
        "A method"
        ...

    def child(self, i: int) -> func_adl_servicex_xaodr25.xAOD.truthparticle_v1.TruthParticle_v1:
        "A method"
        ...

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

    def abseta(self) -> float:
        "A method"
        ...

    def absrapidity(self) -> float:
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

    def charge(self) -> float:
        "A method"
        ...

    def threeCharge(self) -> int:
        "A method"
        ...

    def isCharged(self) -> bool:
        "A method"
        ...

    def isNeutral(self) -> bool:
        "A method"
        ...

    def isPhoton(self) -> bool:
        "A method"
        ...

    def isLepton(self) -> bool:
        "A method"
        ...

    def isChLepton(self) -> bool:
        "A method"
        ...

    def isElectron(self) -> bool:
        "A method"
        ...

    def isMuon(self) -> bool:
        "A method"
        ...

    def isTau(self) -> bool:
        "A method"
        ...

    def isNeutrino(self) -> bool:
        "A method"
        ...

    def isHadron(self) -> bool:
        "A method"
        ...

    def isMeson(self) -> bool:
        "A method"
        ...

    def isBaryon(self) -> bool:
        "A method"
        ...

    def hasStrange(self) -> bool:
        "A method"
        ...

    def hasCharm(self) -> bool:
        "A method"
        ...

    def hasBottom(self) -> bool:
        "A method"
        ...

    def isLightMeson(self) -> bool:
        "A method"
        ...

    def isLightBaryon(self) -> bool:
        "A method"
        ...

    def isLightHadron(self) -> bool:
        "A method"
        ...

    def isHeavyMeson(self) -> bool:
        "A method"
        ...

    def isHeavyBaryon(self) -> bool:
        "A method"
        ...

    def isHeavyHadron(self) -> bool:
        "A method"
        ...

    def isBottomMeson(self) -> bool:
        "A method"
        ...

    def isBottomBaryon(self) -> bool:
        "A method"
        ...

    def isBottomHadron(self) -> bool:
        "A method"
        ...

    def isCharmMeson(self) -> bool:
        "A method"
        ...

    def isCharmBaryon(self) -> bool:
        "A method"
        ...

    def isCharmHadron(self) -> bool:
        "A method"
        ...

    def isStrangeMeson(self) -> bool:
        "A method"
        ...

    def isStrangeBaryon(self) -> bool:
        "A method"
        ...

    def isStrangeHadron(self) -> bool:
        "A method"
        ...

    def isQuark(self) -> bool:
        "A method"
        ...

    def isParton(self) -> bool:
        "A method"
        ...

    def isTop(self) -> bool:
        "A method"
        ...

    def isW(self) -> bool:
        "A method"
        ...

    def isZ(self) -> bool:
        "A method"
        ...

    def isHiggs(self) -> bool:
        "A method"
        ...

    def isResonance(self) -> bool:
        "A method"
        ...

    def isGenSpecific(self) -> bool:
        "A method"
        ...

    def isBSM(self) -> bool:
        "A method"
        ...

    def isGenStable(self) -> bool:
        "A method"
        ...

    def polarizationParameter(self, value: float, parameter: func_adl_servicex_xaodr25.xAOD.truthparticle_v1.TruthParticle_v1.PolParam) -> bool:
        "A method"
        ...

    def setPolarizationParameter(self, value: float, parameter: func_adl_servicex_xaodr25.xAOD.truthparticle_v1.TruthParticle_v1.PolParam) -> bool:
        "A method"
        ...

    def polarization(self) -> func_adl_servicex_xaodr25.xAOD.TruthParticle_v1.polarization.Polarization:
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
