from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr25

_method_map = {
    'word': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexJetRoI_v1',
        'method_name': 'word',
        'return_type': 'unsigned int',
    },
    'menuEta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexJetRoI_v1',
        'method_name': 'menuEta',
        'return_type': 'int',
    },
    'tobEtScale': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexJetRoI_v1',
        'method_name': 'tobEtScale',
        'return_type': 'int',
    },
    'gFexTobEt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexJetRoI_v1',
        'method_name': 'gFexTobEt',
        'return_type': 'int16_t',
    },
    'unpackEt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexJetRoI_v1',
        'method_name': 'unpackEt',
        'return_type': 'int16_t',
    },
    'et': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexJetRoI_v1',
        'method_name': 'et',
        'return_type': 'float',
    },
    'iEta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexJetRoI_v1',
        'method_name': 'iEta',
        'return_type': 'uint8_t',
    },
    'unpackEtaIndex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexJetRoI_v1',
        'method_name': 'unpackEtaIndex',
        'return_type': 'unsigned int',
    },
    'eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexJetRoI_v1',
        'method_name': 'eta',
        'return_type': 'float',
    },
    'etaMin': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexJetRoI_v1',
        'method_name': 'etaMin',
        'return_type': 'float',
    },
    'etaMax': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexJetRoI_v1',
        'method_name': 'etaMax',
        'return_type': 'float',
    },
    'iPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexJetRoI_v1',
        'method_name': 'iPhi',
        'return_type': 'uint8_t',
    },
    'unpackPhiIndex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexJetRoI_v1',
        'method_name': 'unpackPhiIndex',
        'return_type': 'unsigned int',
    },
    'phi_gFex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexJetRoI_v1',
        'method_name': 'phi_gFex',
        'return_type': 'float',
    },
    'phiMin_gFex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexJetRoI_v1',
        'method_name': 'phiMin_gFex',
        'return_type': 'float',
    },
    'phiMax_gFex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexJetRoI_v1',
        'method_name': 'phiMax_gFex',
        'return_type': 'float',
    },
    'phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexJetRoI_v1',
        'method_name': 'phi',
        'return_type': 'float',
    },
    'phiMin': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexJetRoI_v1',
        'method_name': 'phiMin',
        'return_type': 'float',
    },
    'phiMax': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexJetRoI_v1',
        'method_name': 'phiMax',
        'return_type': 'float',
    },
    'iPhiTopo': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexJetRoI_v1',
        'method_name': 'iPhiTopo',
        'return_type': 'int',
    },
    'status': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexJetRoI_v1',
        'method_name': 'status',
        'return_type': 'uint8_t',
    },
    'unpackStatus': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexJetRoI_v1',
        'method_name': 'unpackStatus',
        'return_type': 'unsigned int',
    },
    'saturated': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexJetRoI_v1',
        'method_name': 'saturated',
        'return_type': 'uint8_t',
    },
    'unpackSaturated': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexJetRoI_v1',
        'method_name': 'unpackSaturated',
        'return_type': 'unsigned int',
    },
    'gFexType': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexJetRoI_v1',
        'method_name': 'gFexType',
        'return_type': 'int',
    },
    'unpackType': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexJetRoI_v1',
        'method_name': 'unpackType',
        'return_type': 'int',
    },
    'isgBlockLead': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexJetRoI_v1',
        'method_name': 'isgBlockLead',
        'return_type': 'bool',
    },
    'isgBlockSub': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexJetRoI_v1',
        'method_name': 'isgBlockSub',
        'return_type': 'bool',
    },
    'isgJet': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexJetRoI_v1',
        'method_name': 'isgJet',
        'return_type': 'bool',
    },
    'isgRho': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexJetRoI_v1',
        'method_name': 'isgRho',
        'return_type': 'bool',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexJetRoI_v1',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexJetRoI_v1',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexJetRoI_v1',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexJetRoI_v1',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexJetRoI_v1',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexJetRoI_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexJetRoI_v1',
        'method_name': 'trackIndices',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexJetRoI_v1',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::gFexJetRoI_v1',
        'method_name': 'isAvailable',
        'return_type': 'bool',
    },
}

_enum_function_map = {      
}

_defined_enums = {
    'ObjectType':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.gFexJetRoI_v1',
            'name': 'ObjectType',
            'values': [
                'gRho',
                'gBlockLead',
                'gBlockSub',
                'gJet',
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
            'name': 'xAODTrigger/versions/gFexJetRoI_v1.h',
            'body_includes': ["xAODTrigger/versions/gFexJetRoI_v1.h"],
        })


        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODTrigger',
            'link_libraries': ["xAODTrigger"],
        })

        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class gFexJetRoI_v1:
    "A class"

    class ObjectType(Enum):
        gRho = 0
        gBlockLead = 1
        gBlockSub = 2
        gJet = 3


    def word(self) -> int:
        "A method"
        ...

    def menuEta(self) -> int:
        "A method"
        ...

    def tobEtScale(self) -> int:
        "A method"
        ...

    def gFexTobEt(self) -> int:
        "A method"
        ...

    def unpackEt(self) -> int:
        "A method"
        ...

    def et(self) -> float:
        "A method"
        ...

    def iEta(self) -> int:
        "A method"
        ...

    def unpackEtaIndex(self) -> int:
        "A method"
        ...

    def eta(self) -> float:
        "A method"
        ...

    def etaMin(self) -> float:
        "A method"
        ...

    def etaMax(self) -> float:
        "A method"
        ...

    def iPhi(self) -> int:
        "A method"
        ...

    def unpackPhiIndex(self) -> int:
        "A method"
        ...

    def phi_gFex(self) -> float:
        "A method"
        ...

    def phiMin_gFex(self) -> float:
        "A method"
        ...

    def phiMax_gFex(self) -> float:
        "A method"
        ...

    def phi(self) -> float:
        "A method"
        ...

    def phiMin(self) -> float:
        "A method"
        ...

    def phiMax(self) -> float:
        "A method"
        ...

    def iPhiTopo(self) -> int:
        "A method"
        ...

    def status(self) -> int:
        "A method"
        ...

    def unpackStatus(self) -> int:
        "A method"
        ...

    def saturated(self) -> int:
        "A method"
        ...

    def unpackSaturated(self) -> int:
        "A method"
        ...

    def gFexType(self) -> int:
        "A method"
        ...

    def unpackType(self) -> int:
        "A method"
        ...

    def isgBlockLead(self) -> bool:
        "A method"
        ...

    def isgBlockSub(self) -> bool:
        "A method"
        ...

    def isgJet(self) -> bool:
        "A method"
        ...

    def isgRho(self) -> bool:
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
