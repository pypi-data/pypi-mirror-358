from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr25

_method_map = {
    'eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloClusterBadChannelData_v1',
        'method_name': 'eta',
        'return_type': 'float',
    },
    'phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloClusterBadChannelData_v1',
        'method_name': 'phi',
        'return_type': 'float',
    },
    'layer': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloClusterBadChannelData_v1',
        'method_name': 'layer',
        'return_type': 'CaloSampling::CaloSample',
    },
    'badChannel': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloClusterBadChannelData_v1',
        'method_name': 'badChannel',
        'return_type': 'unsigned int',
    },
}

_enum_function_map = {
    'layer': [
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
            'name': 'xAODCaloEvent/versions/CaloClusterBadChannelData_v1.h',
            'body_includes': ["xAODCaloEvent/versions/CaloClusterBadChannelData_v1.h"],
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
class CaloClusterBadChannelData_v1:
    "A class"


    def eta(self) -> float:
        "A method"
        ...

    def phi(self) -> float:
        "A method"
        ...

    def layer(self) -> func_adl_servicex_xaodr25.calosampling.CaloSampling.CaloSample:
        "A method"
        ...

    def badChannel(self) -> int:
        "A method"
        ...
