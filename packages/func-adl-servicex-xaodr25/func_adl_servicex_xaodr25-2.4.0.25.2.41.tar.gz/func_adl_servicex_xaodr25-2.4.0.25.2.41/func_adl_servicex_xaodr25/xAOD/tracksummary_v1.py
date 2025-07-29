from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr25

_method_map = {
    'params': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackSummary_v1',
        'method_name': 'params',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<double>',
    },
    'covParams': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackSummary_v1',
        'method_name': 'covParams',
        'return_type_element': 'float',
        'return_type_collection': 'const vector<double>',
    },
    'nMeasurements': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackSummary_v1',
        'method_name': 'nMeasurements',
        'return_type': 'unsigned int',
    },
    'nMeasurementsPtr': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackSummary_v1',
        'method_name': 'nMeasurementsPtr',
        'return_type': 'const unsigned int *',
    },
    'nHoles': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackSummary_v1',
        'method_name': 'nHoles',
        'return_type': 'unsigned int',
    },
    'nHolesPtr': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackSummary_v1',
        'method_name': 'nHolesPtr',
        'return_type': 'const unsigned int *',
    },
    'chi2f': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackSummary_v1',
        'method_name': 'chi2f',
        'return_type': 'float',
    },
    'chi2fPtr': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackSummary_v1',
        'method_name': 'chi2fPtr',
        'return_type': 'const float *',
    },
    'ndf': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackSummary_v1',
        'method_name': 'ndf',
        'return_type': 'unsigned int',
    },
    'ndfPtr': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackSummary_v1',
        'method_name': 'ndfPtr',
        'return_type': 'const unsigned int *',
    },
    'nOutliers': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackSummary_v1',
        'method_name': 'nOutliers',
        'return_type': 'unsigned int',
    },
    'nOutliersPtr': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackSummary_v1',
        'method_name': 'nOutliersPtr',
        'return_type': 'const unsigned int *',
    },
    'nSharedHits': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackSummary_v1',
        'method_name': 'nSharedHits',
        'return_type': 'unsigned int',
    },
    'nSharedHitsPtr': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackSummary_v1',
        'method_name': 'nSharedHitsPtr',
        'return_type': 'const unsigned int *',
    },
    'tipIndex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackSummary_v1',
        'method_name': 'tipIndex',
        'return_type': 'unsigned int',
    },
    'tipIndexPtr': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackSummary_v1',
        'method_name': 'tipIndexPtr',
        'return_type': 'const unsigned int *',
    },
    'stemIndex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackSummary_v1',
        'method_name': 'stemIndex',
        'return_type': 'unsigned int',
    },
    'stemIndexPtr': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackSummary_v1',
        'method_name': 'stemIndexPtr',
        'return_type': 'const unsigned int *',
    },
    'surfaceIndex': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackSummary_v1',
        'method_name': 'surfaceIndex',
        'return_type': 'unsigned int',
    },
    'particleHypothesis': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackSummary_v1',
        'method_name': 'particleHypothesis',
        'return_type': 'const uint8_t',
    },
    'size': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackSummary_v1',
        'method_name': 'size',
        'return_type': 'unsigned int',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackSummary_v1',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackSummary_v1',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackSummary_v1',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackSummary_v1',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackSummary_v1',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackSummary_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackSummary_v1',
        'method_name': 'trackIndices',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackSummary_v1',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::TrackSummary_v1',
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
            'name': 'xAODTracking/versions/TrackSummary_v1.h',
            'body_includes': ["xAODTracking/versions/TrackSummary_v1.h"],
        })


        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODTracking',
            'link_libraries': ["xAODTracking"],
        })

        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class TrackSummary_v1:
    "A class"


    def params(self) -> func_adl_servicex_xaodr25.vector_float_.vector_float_:
        "A method"
        ...

    def covParams(self) -> func_adl_servicex_xaodr25.vector_float_.vector_float_:
        "A method"
        ...

    def nMeasurements(self) -> int:
        "A method"
        ...

    def nMeasurementsPtr(self) -> int:
        "A method"
        ...

    def nHoles(self) -> int:
        "A method"
        ...

    def nHolesPtr(self) -> int:
        "A method"
        ...

    def chi2f(self) -> float:
        "A method"
        ...

    def chi2fPtr(self) -> float:
        "A method"
        ...

    def ndf(self) -> int:
        "A method"
        ...

    def ndfPtr(self) -> int:
        "A method"
        ...

    def nOutliers(self) -> int:
        "A method"
        ...

    def nOutliersPtr(self) -> int:
        "A method"
        ...

    def nSharedHits(self) -> int:
        "A method"
        ...

    def nSharedHitsPtr(self) -> int:
        "A method"
        ...

    def tipIndex(self) -> int:
        "A method"
        ...

    def tipIndexPtr(self) -> int:
        "A method"
        ...

    def stemIndex(self) -> int:
        "A method"
        ...

    def stemIndexPtr(self) -> int:
        "A method"
        ...

    def surfaceIndex(self) -> int:
        "A method"
        ...

    def particleHypothesis(self) -> int:
        "A method"
        ...

    def size(self) -> int:
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
