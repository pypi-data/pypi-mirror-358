from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr25

_method_map = {
    'ex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigMissingET_v1',
        'method_name': 'ex',
        'return_type': 'float',
    },
    'ey': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigMissingET_v1',
        'method_name': 'ey',
        'return_type': 'float',
    },
    'ez': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigMissingET_v1',
        'method_name': 'ez',
        'return_type': 'float',
    },
    'sumEt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigMissingET_v1',
        'method_name': 'sumEt',
        'return_type': 'float',
    },
    'sumE': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigMissingET_v1',
        'method_name': 'sumE',
        'return_type': 'float',
    },
    'flag': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigMissingET_v1',
        'method_name': 'flag',
        'return_type': 'int',
    },
    'roiWord': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigMissingET_v1',
        'method_name': 'roiWord',
        'return_type': 'unsigned int',
    },
    'nameOfComponent': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigMissingET_v1',
        'method_name': 'nameOfComponent',
        'return_type': 'const string',
    },
    'getNumberOfComponents': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigMissingET_v1',
        'method_name': 'getNumberOfComponents',
        'return_type': 'unsigned int',
    },
    'exComponent': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigMissingET_v1',
        'method_name': 'exComponent',
        'return_type': 'float',
    },
    'eyComponent': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigMissingET_v1',
        'method_name': 'eyComponent',
        'return_type': 'float',
    },
    'ezComponent': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigMissingET_v1',
        'method_name': 'ezComponent',
        'return_type': 'float',
    },
    'sumEtComponent': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigMissingET_v1',
        'method_name': 'sumEtComponent',
        'return_type': 'float',
    },
    'sumEComponent': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigMissingET_v1',
        'method_name': 'sumEComponent',
        'return_type': 'float',
    },
    'calib0Component': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigMissingET_v1',
        'method_name': 'calib0Component',
        'return_type': 'float',
    },
    'calib1Component': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigMissingET_v1',
        'method_name': 'calib1Component',
        'return_type': 'float',
    },
    'sumOfSignsComponent': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigMissingET_v1',
        'method_name': 'sumOfSignsComponent',
        'return_type': 'float',
    },
    'statusComponent': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigMissingET_v1',
        'method_name': 'statusComponent',
        'return_type': 'short',
    },
    'usedChannelsComponent': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigMissingET_v1',
        'method_name': 'usedChannelsComponent',
        'return_type': 'unsigned short',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigMissingET_v1',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigMissingET_v1',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigMissingET_v1',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigMissingET_v1',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigMissingET_v1',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigMissingET_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigMissingET_v1',
        'method_name': 'trackIndices',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigMissingET_v1',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigMissingET_v1',
        'method_name': 'isAvailable',
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
            'name': 'xAODTrigMissingET/versions/TrigMissingET_v1.h',
            'body_includes': ["xAODTrigMissingET/versions/TrigMissingET_v1.h"],
        })


        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODTrigMissingET',
            'link_libraries': ["xAODTrigMissingET"],
        })

        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class TrigMissingET_v1:
    "A class"


    def ex(self) -> float:
        "A method"
        ...

    def ey(self) -> float:
        "A method"
        ...

    def ez(self) -> float:
        "A method"
        ...

    def sumEt(self) -> float:
        "A method"
        ...

    def sumE(self) -> float:
        "A method"
        ...

    def flag(self) -> int:
        "A method"
        ...

    def roiWord(self) -> int:
        "A method"
        ...

    def nameOfComponent(self, index: int) -> str:
        "A method"
        ...

    def getNumberOfComponents(self) -> int:
        "A method"
        ...

    def exComponent(self, index: int) -> float:
        "A method"
        ...

    def eyComponent(self, index: int) -> float:
        "A method"
        ...

    def ezComponent(self, index: int) -> float:
        "A method"
        ...

    def sumEtComponent(self, index: int) -> float:
        "A method"
        ...

    def sumEComponent(self, index: int) -> float:
        "A method"
        ...

    def calib0Component(self, index: int) -> float:
        "A method"
        ...

    def calib1Component(self, index: int) -> float:
        "A method"
        ...

    def sumOfSignsComponent(self, index: int) -> float:
        "A method"
        ...

    def statusComponent(self, index: int) -> int:
        "A method"
        ...

    def usedChannelsComponent(self, index: int) -> int:
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
