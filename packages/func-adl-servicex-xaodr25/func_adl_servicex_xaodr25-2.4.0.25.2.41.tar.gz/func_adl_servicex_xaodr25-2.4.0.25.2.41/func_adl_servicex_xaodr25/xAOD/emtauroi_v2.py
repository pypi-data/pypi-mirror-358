from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr25

_method_map = {
    'roiType': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EmTauRoI_v2',
        'method_name': 'roiType',
        'return_type': 'xAOD::EmTauRoI_v2::RoIType',
    },
    'eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EmTauRoI_v2',
        'method_name': 'eta',
        'return_type': 'float',
    },
    'phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EmTauRoI_v2',
        'method_name': 'phi',
        'return_type': 'float',
    },
    'roiWord': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EmTauRoI_v2',
        'method_name': 'roiWord',
        'return_type': 'unsigned int',
    },
    'etScale': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EmTauRoI_v2',
        'method_name': 'etScale',
        'return_type': 'float',
    },
    'eT': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EmTauRoI_v2',
        'method_name': 'eT',
        'return_type': 'float',
    },
    'isol': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EmTauRoI_v2',
        'method_name': 'isol',
        'return_type': 'uint8_t',
    },
    'thrPattern': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EmTauRoI_v2',
        'method_name': 'thrPattern',
        'return_type': 'unsigned int',
    },
    'core': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EmTauRoI_v2',
        'method_name': 'core',
        'return_type': 'float',
    },
    'emClus': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EmTauRoI_v2',
        'method_name': 'emClus',
        'return_type': 'float',
    },
    'tauClus': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EmTauRoI_v2',
        'method_name': 'tauClus',
        'return_type': 'float',
    },
    'emIsol': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EmTauRoI_v2',
        'method_name': 'emIsol',
        'return_type': 'float',
    },
    'hadIsol': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EmTauRoI_v2',
        'method_name': 'hadIsol',
        'return_type': 'float',
    },
    'hadCore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EmTauRoI_v2',
        'method_name': 'hadCore',
        'return_type': 'float',
    },
    'thrNames': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EmTauRoI_v2',
        'method_name': 'thrNames',
        'return_type_element': 'string',
        'return_type_collection': 'const vector<string>',
    },
    'thrValues': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EmTauRoI_v2',
        'method_name': 'thrValues',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EmTauRoI_v2',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EmTauRoI_v2',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EmTauRoI_v2',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EmTauRoI_v2',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EmTauRoI_v2',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EmTauRoI_v2',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EmTauRoI_v2',
        'method_name': 'trackIndices',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EmTauRoI_v2',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EmTauRoI_v2',
        'method_name': 'isAvailable',
        'return_type': 'bool',
    },
}

_enum_function_map = {
    'roiType': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.EmTauRoI_v2',
            'name': 'RoIType',
            'values': [
                'CPRoIWord',
                'EMRoIWord',
                'TauRoIWord',
            ],
        },
    ],      
}

_defined_enums = {
    'RoIType':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.EmTauRoI_v2',
            'name': 'RoIType',
            'values': [
                'CPRoIWord',
                'EMRoIWord',
                'TauRoIWord',
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
            'name': 'xAODTrigger/versions/EmTauRoI_v2.h',
            'body_includes': ["xAODTrigger/versions/EmTauRoI_v2.h"],
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
class EmTauRoI_v2:
    "A class"

    class RoIType(Enum):
        CPRoIWord = 0
        EMRoIWord = 1
        TauRoIWord = 2


    def roiType(self) -> func_adl_servicex_xaodr25.xAOD.emtauroi_v2.EmTauRoI_v2.RoIType:
        "A method"
        ...

    def eta(self) -> float:
        "A method"
        ...

    def phi(self) -> float:
        "A method"
        ...

    def roiWord(self) -> int:
        "A method"
        ...

    def etScale(self) -> float:
        "A method"
        ...

    def eT(self) -> float:
        "A method"
        ...

    def isol(self) -> int:
        "A method"
        ...

    def thrPattern(self) -> int:
        "A method"
        ...

    def core(self) -> float:
        "A method"
        ...

    def emClus(self) -> float:
        "A method"
        ...

    def tauClus(self) -> float:
        "A method"
        ...

    def emIsol(self) -> float:
        "A method"
        ...

    def hadIsol(self) -> float:
        "A method"
        ...

    def hadCore(self) -> float:
        "A method"
        ...

    def thrNames(self) -> func_adl_servicex_xaodr25.vector_str_.vector_str_:
        "A method"
        ...

    def thrValues(self) -> func_adl_servicex_xaodr25.vector_float_.vector_float_:
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
