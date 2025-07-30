from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr25

_method_map = {
    'configureGrid': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloTowerContainer_v1',
        'method_name': 'configureGrid',
        'return_type': 'bool',
    },
    'nEtaBins': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloTowerContainer_v1',
        'method_name': 'nEtaBins',
        'return_type': 'int',
    },
    'etaMin': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloTowerContainer_v1',
        'method_name': 'etaMin',
        'return_type': 'double',
    },
    'etaMax': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloTowerContainer_v1',
        'method_name': 'etaMax',
        'return_type': 'double',
    },
    'deltaEta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloTowerContainer_v1',
        'method_name': 'deltaEta',
        'return_type': 'double',
    },
    'nPhiBins': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloTowerContainer_v1',
        'method_name': 'nPhiBins',
        'return_type': 'int',
    },
    'phiMin': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloTowerContainer_v1',
        'method_name': 'phiMin',
        'return_type': 'double',
    },
    'phiMax': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloTowerContainer_v1',
        'method_name': 'phiMax',
        'return_type': 'double',
    },
    'deltaPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloTowerContainer_v1',
        'method_name': 'deltaPhi',
        'return_type': 'double',
    },
    'nTowers': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloTowerContainer_v1',
        'method_name': 'nTowers',
        'return_type': 'int',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloTowerContainer_v1',
        'method_name': 'index',
        'return_type': 'int',
    },
    'eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloTowerContainer_v1',
        'method_name': 'eta',
        'return_type': 'double',
    },
    'phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloTowerContainer_v1',
        'method_name': 'phi',
        'return_type': 'double',
    },
    'tower': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloTowerContainer_v1',
        'method_name': 'tower',
        'return_type': 'const xAOD::CaloTower_v1 *',
    },
    'front': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloTowerContainer_v1',
        'method_name': 'front',
        'return_type': 'const xAOD::CaloTower_v1 *',
    },
    'back': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloTowerContainer_v1',
        'method_name': 'back',
        'return_type': 'const xAOD::CaloTower_v1 *',
    },
    'dvlinfo': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloTowerContainer_v1',
        'method_name': 'dvlinfo',
        'return_type': 'const DataModel_detail::DVLInfoBase',
    },
    'dvlinfo_v': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloTowerContainer_v1',
        'method_name': 'dvlinfo_v',
        'return_type': 'const DataModel_detail::DVLInfoBase',
    },
    'empty': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloTowerContainer_v1',
        'method_name': 'empty',
        'return_type': 'bool',
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloTowerContainer_v1',
        'method_name': 'trackIndices',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloTowerContainer_v1',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloTowerContainer_v1',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloTowerContainer_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
}

_enum_function_map = {      
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
            'name': 'xAODCaloEvent/CaloTowerContainer.h',
            'body_includes': ["xAODCaloEvent/CaloTowerContainer.h"],
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
class CaloTowerContainer_v1:
    "A class"


    def configureGrid(self, nEtaBins: int, etaMin: float, etaMax: float, nPhiBins: int) -> bool:
        "A method"
        ...

    def nEtaBins(self) -> int:
        "A method"
        ...

    def etaMin(self) -> float:
        "A method"
        ...

    def etaMax(self) -> float:
        "A method"
        ...

    def deltaEta(self) -> float:
        "A method"
        ...

    def nPhiBins(self) -> int:
        "A method"
        ...

    def phiMin(self) -> float:
        "A method"
        ...

    def phiMax(self) -> float:
        "A method"
        ...

    def deltaPhi(self) -> float:
        "A method"
        ...

    def nTowers(self) -> int:
        "A method"
        ...

    def index(self, eta: float, phi: float) -> int:
        "A method"
        ...

    def eta(self, index: int) -> float:
        "A method"
        ...

    def phi(self, index: int) -> float:
        "A method"
        ...

    def tower(self, eta: float, phi: float) -> func_adl_servicex_xaodr25.xAOD.calotower_v1.CaloTower_v1:
        "A method"
        ...

    def front(self) -> func_adl_servicex_xaodr25.xAOD.calotower_v1.CaloTower_v1:
        "A method"
        ...

    def back(self) -> func_adl_servicex_xaodr25.xAOD.calotower_v1.CaloTower_v1:
        "A method"
        ...

    def dvlinfo(self) -> func_adl_servicex_xaodr25.DataModel_detail.dvlinfobase.DVLInfoBase:
        "A method"
        ...

    def dvlinfo_v(self) -> func_adl_servicex_xaodr25.DataModel_detail.dvlinfobase.DVLInfoBase:
        "A method"
        ...

    def empty(self) -> bool:
        "A method"
        ...

    def trackIndices(self) -> bool:
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
