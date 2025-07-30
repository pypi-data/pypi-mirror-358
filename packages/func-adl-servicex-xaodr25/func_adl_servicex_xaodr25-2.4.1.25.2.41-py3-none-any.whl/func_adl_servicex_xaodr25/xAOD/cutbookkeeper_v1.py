from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr25

_method_map = {
    'nameIdentifier': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeper_v1',
        'method_name': 'nameIdentifier',
        'return_type': 'unsigned int',
    },
    'uniqueIdentifier': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeper_v1',
        'method_name': 'uniqueIdentifier',
        'return_type': 'unsigned int',
    },
    'name': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeper_v1',
        'method_name': 'name',
        'return_type': 'const string',
    },
    'description': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeper_v1',
        'method_name': 'description',
        'return_type': 'const string',
    },
    'isTopFilter': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeper_v1',
        'method_name': 'isTopFilter',
        'return_type': 'bool',
    },
    'cutLogic': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeper_v1',
        'method_name': 'cutLogic',
        'return_type': 'xAOD::CutBookkeeper_v1::CutLogic',
    },
    'cycle': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeper_v1',
        'method_name': 'cycle',
        'return_type': 'int',
    },
    'inputStream': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeper_v1',
        'method_name': 'inputStream',
        'return_type': 'const string',
    },
    'outputStreams': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeper_v1',
        'method_name': 'outputStreams',
        'return_type_element': 'string',
        'return_type_collection': 'const vector<string>',
    },
    'hasOutputStream': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeper_v1',
        'method_name': 'hasOutputStream',
        'return_type': 'bool',
    },
    'nAcceptedEvents': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeper_v1',
        'method_name': 'nAcceptedEvents',
        'return_type': 'uint64_t',
    },
    'sumOfEventWeights': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeper_v1',
        'method_name': 'sumOfEventWeights',
        'return_type': 'double',
    },
    'sumOfEventWeightsSquared': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeper_v1',
        'method_name': 'sumOfEventWeightsSquared',
        'return_type': 'double',
    },
    'isEqualTo': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeper_v1',
        'method_name': 'isEqualTo',
        'return_type': 'bool',
    },
    'hasParent': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeper_v1',
        'method_name': 'hasParent',
        'return_type': 'bool',
    },
    'parent': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeper_v1',
        'method_name': 'parent',
        'return_type': 'const xAOD::CutBookkeeper_v1 *',
    },
    'nChildren': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeper_v1',
        'method_name': 'nChildren',
        'return_type': 'unsigned int',
    },
    'hasChild': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeper_v1',
        'method_name': 'hasChild',
        'return_type': 'bool',
    },
    'child': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeper_v1',
        'method_name': 'child',
        'return_type': 'const xAOD::CutBookkeeper_v1 *',
    },
    'addNewChild': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeper_v1',
        'method_name': 'addNewChild',
        'return_type': 'xAOD::CutBookkeeper_v1 *',
    },
    'nUsedOthers': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeper_v1',
        'method_name': 'nUsedOthers',
        'return_type': 'unsigned int',
    },
    'hasUsedOther': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeper_v1',
        'method_name': 'hasUsedOther',
        'return_type': 'bool',
    },
    'usedOther': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeper_v1',
        'method_name': 'usedOther',
        'return_type': 'const xAOD::CutBookkeeper_v1 *',
    },
    'nSiblings': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeper_v1',
        'method_name': 'nSiblings',
        'return_type': 'unsigned int',
    },
    'hasSibling': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeper_v1',
        'method_name': 'hasSibling',
        'return_type': 'bool',
    },
    'sibling': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeper_v1',
        'method_name': 'sibling',
        'return_type': 'const xAOD::CutBookkeeper_v1 *',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeper_v1',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeper_v1',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeper_v1',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeper_v1',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeper_v1',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeper_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeper_v1',
        'method_name': 'trackIndices',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeper_v1',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeper_v1',
        'method_name': 'isAvailable',
        'return_type': 'bool',
    },
}

_enum_function_map = {
    'cutLogic': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.CutBookkeeper_v1',
            'name': 'CutLogic',
            'values': [
                'UNKNOWN',
                'ALLEVENTSPROCESSED',
                'ALLEVENTSWRITTEN',
                'OTHER',
                'ACCEPT',
                'REQUIRE',
                'VETO',
            ],
        },
    ],      
}

_defined_enums = {
    'CutLogic':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.CutBookkeeper_v1',
            'name': 'CutLogic',
            'values': [
                'UNKNOWN',
                'ALLEVENTSPROCESSED',
                'ALLEVENTSWRITTEN',
                'OTHER',
                'ACCEPT',
                'REQUIRE',
                'VETO',
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
            'name': 'xAODCutFlow/versions/CutBookkeeper_v1.h',
            'body_includes': ["xAODCutFlow/versions/CutBookkeeper_v1.h"],
        })


        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODCutFlow',
            'link_libraries': ["xAODCutFlow"],
        })

        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class CutBookkeeper_v1:
    "A class"

    class CutLogic(Enum):
        UNKNOWN = 0
        ALLEVENTSPROCESSED = 1
        ALLEVENTSWRITTEN = 2
        OTHER = 3
        ACCEPT = 4
        REQUIRE = 5
        VETO = 6


    def nameIdentifier(self) -> int:
        "A method"
        ...

    def uniqueIdentifier(self) -> int:
        "A method"
        ...

    def name(self) -> str:
        "A method"
        ...

    def description(self) -> str:
        "A method"
        ...

    def isTopFilter(self) -> bool:
        "A method"
        ...

    def cutLogic(self) -> func_adl_servicex_xaodr25.xAOD.cutbookkeeper_v1.CutBookkeeper_v1.CutLogic:
        "A method"
        ...

    def cycle(self) -> int:
        "A method"
        ...

    def inputStream(self) -> str:
        "A method"
        ...

    def outputStreams(self) -> func_adl_servicex_xaodr25.vector_str_.vector_str_:
        "A method"
        ...

    def hasOutputStream(self, outputstream: str) -> bool:
        "A method"
        ...

    def nAcceptedEvents(self) -> int:
        "A method"
        ...

    def sumOfEventWeights(self) -> float:
        "A method"
        ...

    def sumOfEventWeightsSquared(self) -> float:
        "A method"
        ...

    def isEqualTo(self, eb: func_adl_servicex_xaodr25.xAOD.cutbookkeeper_v1.CutBookkeeper_v1) -> bool:
        "A method"
        ...

    def hasParent(self) -> bool:
        "A method"
        ...

    def parent(self) -> func_adl_servicex_xaodr25.xAOD.cutbookkeeper_v1.CutBookkeeper_v1:
        "A method"
        ...

    def nChildren(self) -> int:
        "A method"
        ...

    def hasChild(self, testCBK: func_adl_servicex_xaodr25.xAOD.cutbookkeeper_v1.CutBookkeeper_v1) -> bool:
        "A method"
        ...

    def child(self, i: int) -> func_adl_servicex_xaodr25.xAOD.cutbookkeeper_v1.CutBookkeeper_v1:
        "A method"
        ...

    def addNewChild(self, name: str, description: str) -> func_adl_servicex_xaodr25.xAOD.cutbookkeeper_v1.CutBookkeeper_v1:
        "A method"
        ...

    def nUsedOthers(self) -> int:
        "A method"
        ...

    def hasUsedOther(self, testCBK: func_adl_servicex_xaodr25.xAOD.cutbookkeeper_v1.CutBookkeeper_v1) -> bool:
        "A method"
        ...

    def usedOther(self, i: int) -> func_adl_servicex_xaodr25.xAOD.cutbookkeeper_v1.CutBookkeeper_v1:
        "A method"
        ...

    def nSiblings(self) -> int:
        "A method"
        ...

    def hasSibling(self, testCBK: func_adl_servicex_xaodr25.xAOD.cutbookkeeper_v1.CutBookkeeper_v1) -> bool:
        "A method"
        ...

    def sibling(self, i: int) -> func_adl_servicex_xaodr25.xAOD.cutbookkeeper_v1.CutBookkeeper_v1:
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
