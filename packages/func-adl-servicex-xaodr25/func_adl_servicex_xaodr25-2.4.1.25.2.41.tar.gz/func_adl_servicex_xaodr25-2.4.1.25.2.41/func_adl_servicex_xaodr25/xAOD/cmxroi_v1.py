from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr25

_method_map = {
    'cmxRoIWords': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMXRoI_v1',
        'method_name': 'cmxRoIWords',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned int>',
    },
    'ex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMXRoI_v1',
        'method_name': 'ex',
        'return_type': 'unsigned int',
    },
    'ey': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMXRoI_v1',
        'method_name': 'ey',
        'return_type': 'unsigned int',
    },
    'et': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMXRoI_v1',
        'method_name': 'et',
        'return_type': 'unsigned int',
    },
    'exError': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMXRoI_v1',
        'method_name': 'exError',
        'return_type': 'int',
    },
    'eyError': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMXRoI_v1',
        'method_name': 'eyError',
        'return_type': 'int',
    },
    'etError': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMXRoI_v1',
        'method_name': 'etError',
        'return_type': 'int',
    },
    'sumEtHits': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMXRoI_v1',
        'method_name': 'sumEtHits',
        'return_type': 'unsigned int',
    },
    'missingEtHits': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMXRoI_v1',
        'method_name': 'missingEtHits',
        'return_type': 'unsigned int',
    },
    'missingEtSigHits': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMXRoI_v1',
        'method_name': 'missingEtSigHits',
        'return_type': 'unsigned int',
    },
    'roiWord': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMXRoI_v1',
        'method_name': 'roiWord',
        'return_type': 'unsigned int',
    },
    'exWord': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMXRoI_v1',
        'method_name': 'exWord',
        'return_type': 'unsigned int',
    },
    'eyWord': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMXRoI_v1',
        'method_name': 'eyWord',
        'return_type': 'unsigned int',
    },
    'etWord': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMXRoI_v1',
        'method_name': 'etWord',
        'return_type': 'unsigned int',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMXRoI_v1',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMXRoI_v1',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMXRoI_v1',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMXRoI_v1',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMXRoI_v1',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMXRoI_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMXRoI_v1',
        'method_name': 'trackIndices',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMXRoI_v1',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CMXRoI_v1',
        'method_name': 'isAvailable',
        'return_type': 'bool',
    },
}

_enum_function_map = {
    'ex': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.CMXRoI_v1',
            'name': 'SumType',
            'values': [
                'NORMAL',
                'MASKED',
            ],
        },
    ],
    'ey': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.CMXRoI_v1',
            'name': 'SumType',
            'values': [
                'NORMAL',
                'MASKED',
            ],
        },
    ],
    'et': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.CMXRoI_v1',
            'name': 'SumType',
            'values': [
                'NORMAL',
                'MASKED',
            ],
        },
    ],
    'exError': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.CMXRoI_v1',
            'name': 'SumType',
            'values': [
                'NORMAL',
                'MASKED',
            ],
        },
    ],
    'eyError': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.CMXRoI_v1',
            'name': 'SumType',
            'values': [
                'NORMAL',
                'MASKED',
            ],
        },
    ],
    'etError': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.CMXRoI_v1',
            'name': 'SumType',
            'values': [
                'NORMAL',
                'MASKED',
            ],
        },
    ],
    'sumEtHits': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.CMXRoI_v1',
            'name': 'SumType',
            'values': [
                'NORMAL',
                'MASKED',
            ],
        },
    ],
    'missingEtHits': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.CMXRoI_v1',
            'name': 'SumType',
            'values': [
                'NORMAL',
                'MASKED',
            ],
        },
    ],
    'exWord': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.CMXRoI_v1',
            'name': 'SumType',
            'values': [
                'NORMAL',
                'MASKED',
            ],
        },
    ],
    'eyWord': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.CMXRoI_v1',
            'name': 'SumType',
            'values': [
                'NORMAL',
                'MASKED',
            ],
        },
    ],
    'etWord': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.CMXRoI_v1',
            'name': 'SumType',
            'values': [
                'NORMAL',
                'MASKED',
            ],
        },
    ],      
}

_defined_enums = {
    'SumType':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.CMXRoI_v1',
            'name': 'SumType',
            'values': [
                'NORMAL',
                'MASKED',
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
            'name': 'xAODTrigL1Calo/versions/CMXRoI_v1.h',
            'body_includes': ["xAODTrigL1Calo/versions/CMXRoI_v1.h"],
        })


        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODTrigL1Calo',
            'link_libraries': ["xAODTrigL1Calo"],
        })

        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class CMXRoI_v1:
    "A class"

    class SumType(Enum):
        NORMAL = 0
        MASKED = 1


    def cmxRoIWords(self) -> func_adl_servicex_xaodr25.vector_int_.vector_int_:
        "A method"
        ...

    def ex(self, type: func_adl_servicex_xaodr25.xAOD.cmxroi_v1.CMXRoI_v1.SumType) -> int:
        "A method"
        ...

    def ey(self, type: func_adl_servicex_xaodr25.xAOD.cmxroi_v1.CMXRoI_v1.SumType) -> int:
        "A method"
        ...

    def et(self, type: func_adl_servicex_xaodr25.xAOD.cmxroi_v1.CMXRoI_v1.SumType) -> int:
        "A method"
        ...

    def exError(self, type: func_adl_servicex_xaodr25.xAOD.cmxroi_v1.CMXRoI_v1.SumType) -> int:
        "A method"
        ...

    def eyError(self, type: func_adl_servicex_xaodr25.xAOD.cmxroi_v1.CMXRoI_v1.SumType) -> int:
        "A method"
        ...

    def etError(self, type: func_adl_servicex_xaodr25.xAOD.cmxroi_v1.CMXRoI_v1.SumType) -> int:
        "A method"
        ...

    def sumEtHits(self, type: func_adl_servicex_xaodr25.xAOD.cmxroi_v1.CMXRoI_v1.SumType) -> int:
        "A method"
        ...

    def missingEtHits(self, type: func_adl_servicex_xaodr25.xAOD.cmxroi_v1.CMXRoI_v1.SumType) -> int:
        "A method"
        ...

    def missingEtSigHits(self) -> int:
        "A method"
        ...

    def roiWord(self, word: int) -> int:
        "A method"
        ...

    def exWord(self, type: func_adl_servicex_xaodr25.xAOD.cmxroi_v1.CMXRoI_v1.SumType) -> int:
        "A method"
        ...

    def eyWord(self, type: func_adl_servicex_xaodr25.xAOD.cmxroi_v1.CMXRoI_v1.SumType) -> int:
        "A method"
        ...

    def etWord(self, type: func_adl_servicex_xaodr25.xAOD.cmxroi_v1.CMXRoI_v1.SumType) -> int:
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
