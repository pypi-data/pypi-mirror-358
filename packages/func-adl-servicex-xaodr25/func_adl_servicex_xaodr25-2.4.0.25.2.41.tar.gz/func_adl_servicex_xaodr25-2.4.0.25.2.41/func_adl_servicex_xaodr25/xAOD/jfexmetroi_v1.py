from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr25

_method_map = {
    'tobWord': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexMETRoI_v1',
        'method_name': 'tobWord',
        'return_type': 'unsigned int',
    },
    'jFexNumber': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexMETRoI_v1',
        'method_name': 'jFexNumber',
        'return_type': 'uint8_t',
    },
    'fpgaNumber': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexMETRoI_v1',
        'method_name': 'fpgaNumber',
        'return_type': 'uint8_t',
    },
    'tobEx': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexMETRoI_v1',
        'method_name': 'tobEx',
        'return_type': 'int',
    },
    'tobEy': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexMETRoI_v1',
        'method_name': 'tobEy',
        'return_type': 'int',
    },
    'tobRes': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexMETRoI_v1',
        'method_name': 'tobRes',
        'return_type': 'uint8_t',
    },
    'tobSat': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexMETRoI_v1',
        'method_name': 'tobSat',
        'return_type': 'uint8_t',
    },
    'tobEtScale': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexMETRoI_v1',
        'method_name': 'tobEtScale',
        'return_type': 'int',
    },
    'unpackEx': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexMETRoI_v1',
        'method_name': 'unpackEx',
        'return_type': 'int',
    },
    'Ex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexMETRoI_v1',
        'method_name': 'Ex',
        'return_type': 'int',
    },
    'unpackEy': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexMETRoI_v1',
        'method_name': 'unpackEy',
        'return_type': 'int',
    },
    'Ey': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexMETRoI_v1',
        'method_name': 'Ey',
        'return_type': 'int',
    },
    'unpackRes': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexMETRoI_v1',
        'method_name': 'unpackRes',
        'return_type': 'unsigned int',
    },
    'unpackSat': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexMETRoI_v1',
        'method_name': 'unpackSat',
        'return_type': 'unsigned int',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexMETRoI_v1',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexMETRoI_v1',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexMETRoI_v1',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexMETRoI_v1',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexMETRoI_v1',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexMETRoI_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexMETRoI_v1',
        'method_name': 'trackIndices',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexMETRoI_v1',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexMETRoI_v1',
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
            'name': 'xAODTrigger/versions/jFexMETRoI_v1.h',
            'body_includes': ["xAODTrigger/versions/jFexMETRoI_v1.h"],
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
class jFexMETRoI_v1:
    "A class"


    def tobWord(self) -> int:
        "A method"
        ...

    def jFexNumber(self) -> int:
        "A method"
        ...

    def fpgaNumber(self) -> int:
        "A method"
        ...

    def tobEx(self) -> int:
        "A method"
        ...

    def tobEy(self) -> int:
        "A method"
        ...

    def tobRes(self) -> int:
        "A method"
        ...

    def tobSat(self) -> int:
        "A method"
        ...

    def tobEtScale(self) -> int:
        "A method"
        ...

    def unpackEx(self) -> int:
        "A method"
        ...

    def Ex(self) -> int:
        "A method"
        ...

    def unpackEy(self) -> int:
        "A method"
        ...

    def Ey(self) -> int:
        "A method"
        ...

    def unpackRes(self) -> int:
        "A method"
        ...

    def unpackSat(self) -> int:
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
