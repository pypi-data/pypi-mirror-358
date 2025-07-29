from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr25

_method_map = {
    'smk': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'smk',
        'return_type': 'unsigned int',
    },
    'l1psk': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'l1psk',
        'return_type': 'unsigned int',
    },
    'hltpsk': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'hltpsk',
        'return_type': 'unsigned int',
    },
    'itemCtpIds': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'itemCtpIds',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned short>',
    },
    'itemCtpIdsAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'itemCtpIdsAvailable',
        'return_type': 'bool',
    },
    'itemNames': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'itemNames',
        'return_type_element': 'string',
        'return_type_collection': 'const vector<string>',
    },
    'itemNamesAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'itemNamesAvailable',
        'return_type': 'bool',
    },
    'itemPrescales': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'itemPrescales',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'itemPrescalesAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'itemPrescalesAvailable',
        'return_type': 'bool',
    },
    'chainIds': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'chainIds',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned short>',
    },
    'chainIdsAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'chainIdsAvailable',
        'return_type': 'bool',
    },
    'chainNames': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'chainNames',
        'return_type_element': 'string',
        'return_type_collection': 'const vector<string>',
    },
    'chainNamesAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'chainNamesAvailable',
        'return_type': 'bool',
    },
    'chainParentNames': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'chainParentNames',
        'return_type_element': 'string',
        'return_type_collection': 'const vector<string>',
    },
    'chainParentNamesAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'chainParentNamesAvailable',
        'return_type': 'bool',
    },
    'chainPrescales': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'chainPrescales',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'chainPrescalesAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'chainPrescalesAvailable',
        'return_type': 'bool',
    },
    'chainRerunPrescales': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'chainRerunPrescales',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'chainRerunPrescalesAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'chainRerunPrescalesAvailable',
        'return_type': 'bool',
    },
    'chainPassthroughPrescales': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'chainPassthroughPrescales',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<float>',
    },
    'chainPassthroughPrescalesAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'chainPassthroughPrescalesAvailable',
        'return_type': 'bool',
    },
    'chainSignatureCounters': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'chainSignatureCounters',
        'return_type_element': 'vector<unsigned short>',
        'return_type_collection': 'const vector<vector<unsigned int>>',
    },
    'chainSignatureCountersAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'chainSignatureCountersAvailable',
        'return_type': 'bool',
    },
    'chainSignatureLogics': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'chainSignatureLogics',
        'return_type_element': 'vector<unsigned short>',
        'return_type_collection': 'const vector<vector<int>>',
    },
    'chainSignatureLogicsAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'chainSignatureLogicsAvailable',
        'return_type': 'bool',
    },
    'chainSignatureOutputTEs': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'chainSignatureOutputTEs',
        'return_type_element': 'vector<vector<string>>',
        'return_type_collection': 'const vector<vector<vector<string>>>',
    },
    'chainSignatureOutputTEsAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'chainSignatureOutputTEsAvailable',
        'return_type': 'bool',
    },
    'chainSignatureLabels': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'chainSignatureLabels',
        'return_type_element': 'vector<string>',
        'return_type_collection': 'const vector<vector<string>>',
    },
    'chainSignatureLabelsAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'chainSignatureLabelsAvailable',
        'return_type': 'bool',
    },
    'sequenceInputTEs': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'sequenceInputTEs',
        'return_type_element': 'vector<string>',
        'return_type_collection': 'const vector<vector<string>>',
    },
    'sequenceInputTEsAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'sequenceInputTEsAvailable',
        'return_type': 'bool',
    },
    'sequenceOutputTEs': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'sequenceOutputTEs',
        'return_type_element': 'string',
        'return_type_collection': 'const vector<string>',
    },
    'sequenceOutputTEsAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'sequenceOutputTEsAvailable',
        'return_type': 'bool',
    },
    'sequenceAlgorithms': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'sequenceAlgorithms',
        'return_type_element': 'vector<string>',
        'return_type_collection': 'const vector<vector<string>>',
    },
    'sequenceAlgorithmsAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'sequenceAlgorithmsAvailable',
        'return_type': 'bool',
    },
    'bunchGroupBunches': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'bunchGroupBunches',
        'return_type_element': 'vector<unsigned short>',
        'return_type_collection': 'const vector<vector<unsigned short>>',
    },
    'bunchGroupBunchesAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'bunchGroupBunchesAvailable',
        'return_type': 'bool',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'trackIndices',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TriggerMenu_v1',
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
            'name': 'xAODTrigger/versions/TriggerMenu_v1.h',
            'body_includes': ["xAODTrigger/versions/TriggerMenu_v1.h"],
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
class TriggerMenu_v1:
    "A class"


    def smk(self) -> int:
        "A method"
        ...

    def l1psk(self) -> int:
        "A method"
        ...

    def hltpsk(self) -> int:
        "A method"
        ...

    def itemCtpIds(self) -> func_adl_servicex_xaodr25.vector_int_.vector_int_:
        "A method"
        ...

    def itemCtpIdsAvailable(self) -> bool:
        "A method"
        ...

    def itemNames(self) -> func_adl_servicex_xaodr25.vector_str_.vector_str_:
        "A method"
        ...

    def itemNamesAvailable(self) -> bool:
        "A method"
        ...

    def itemPrescales(self) -> func_adl_servicex_xaodr25.vector_float_.vector_float_:
        "A method"
        ...

    def itemPrescalesAvailable(self) -> bool:
        "A method"
        ...

    def chainIds(self) -> func_adl_servicex_xaodr25.vector_int_.vector_int_:
        "A method"
        ...

    def chainIdsAvailable(self) -> bool:
        "A method"
        ...

    def chainNames(self) -> func_adl_servicex_xaodr25.vector_str_.vector_str_:
        "A method"
        ...

    def chainNamesAvailable(self) -> bool:
        "A method"
        ...

    def chainParentNames(self) -> func_adl_servicex_xaodr25.vector_str_.vector_str_:
        "A method"
        ...

    def chainParentNamesAvailable(self) -> bool:
        "A method"
        ...

    def chainPrescales(self) -> func_adl_servicex_xaodr25.vector_float_.vector_float_:
        "A method"
        ...

    def chainPrescalesAvailable(self) -> bool:
        "A method"
        ...

    def chainRerunPrescales(self) -> func_adl_servicex_xaodr25.vector_float_.vector_float_:
        "A method"
        ...

    def chainRerunPrescalesAvailable(self) -> bool:
        "A method"
        ...

    def chainPassthroughPrescales(self) -> func_adl_servicex_xaodr25.vector_float_.vector_float_:
        "A method"
        ...

    def chainPassthroughPrescalesAvailable(self) -> bool:
        "A method"
        ...

    def chainSignatureCounters(self) -> func_adl_servicex_xaodr25.vector_vector_int__.vector_vector_int__:
        "A method"
        ...

    def chainSignatureCountersAvailable(self) -> bool:
        "A method"
        ...

    def chainSignatureLogics(self) -> func_adl_servicex_xaodr25.vector_vector_int__.vector_vector_int__:
        "A method"
        ...

    def chainSignatureLogicsAvailable(self) -> bool:
        "A method"
        ...

    def chainSignatureOutputTEs(self) -> func_adl_servicex_xaodr25.vector_vector_vector_str___.vector_vector_vector_str___:
        "A method"
        ...

    def chainSignatureOutputTEsAvailable(self) -> bool:
        "A method"
        ...

    def chainSignatureLabels(self) -> func_adl_servicex_xaodr25.vector_vector_str__.vector_vector_str__:
        "A method"
        ...

    def chainSignatureLabelsAvailable(self) -> bool:
        "A method"
        ...

    def sequenceInputTEs(self) -> func_adl_servicex_xaodr25.vector_vector_str__.vector_vector_str__:
        "A method"
        ...

    def sequenceInputTEsAvailable(self) -> bool:
        "A method"
        ...

    def sequenceOutputTEs(self) -> func_adl_servicex_xaodr25.vector_str_.vector_str_:
        "A method"
        ...

    def sequenceOutputTEsAvailable(self) -> bool:
        "A method"
        ...

    def sequenceAlgorithms(self) -> func_adl_servicex_xaodr25.vector_vector_str__.vector_vector_str__:
        "A method"
        ...

    def sequenceAlgorithmsAvailable(self) -> bool:
        "A method"
        ...

    def bunchGroupBunches(self) -> func_adl_servicex_xaodr25.vector_vector_int__.vector_vector_int__:
        "A method"
        ...

    def bunchGroupBunchesAvailable(self) -> bool:
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
