from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr25

_method_map = {
    'memResource': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigT2ZdcSignalsAuxContainer_v1',
        'method_name': 'memResource',
        'return_type': 'pmr::memory_resource *',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigT2ZdcSignalsAuxContainer_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'size': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigT2ZdcSignalsAuxContainer_v1',
        'method_name': 'size',
        'return_type': 'unsigned int',
    },
    'resize': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigT2ZdcSignalsAuxContainer_v1',
        'method_name': 'resize',
        'return_type': 'bool',
    },
    'name': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrigT2ZdcSignalsAuxContainer_v1',
        'method_name': 'name',
        'return_type': 'const char *',
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
            'name': 'xAODTrigMinBias/versions/TrigT2ZdcSignalsAuxContainer_v1.h',
            'body_includes': ["xAODTrigMinBias/versions/TrigT2ZdcSignalsAuxContainer_v1.h"],
        })


        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODTrigMinBias',
            'link_libraries': ["xAODTrigMinBias"],
        })

        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class TrigT2ZdcSignalsAuxContainer_v1:
    "A class"


    def memResource(self) -> func_adl_servicex_xaodr25.pmr.memory_resource.memory_resource:
        "A method"
        ...

    def clearDecorations(self) -> bool:
        "A method"
        ...

    def size(self) -> int:
        "A method"
        ...

    def resize(self, size: int) -> bool:
        "A method"
        ...

    def name(self) -> str:
        "A method"
        ...
