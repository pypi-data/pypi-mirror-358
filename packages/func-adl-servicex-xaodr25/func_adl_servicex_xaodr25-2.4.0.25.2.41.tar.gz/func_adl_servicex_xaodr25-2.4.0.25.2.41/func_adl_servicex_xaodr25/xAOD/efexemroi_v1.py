from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr25

_method_map = {
    'word0': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::eFexEMRoI_v1',
        'method_name': 'word0',
        'return_type': 'unsigned int',
    },
    'word1': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::eFexEMRoI_v1',
        'method_name': 'word1',
        'return_type': 'unsigned int',
    },
    'et': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::eFexEMRoI_v1',
        'method_name': 'et',
        'return_type': 'float',
    },
    'eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::eFexEMRoI_v1',
        'method_name': 'eta',
        'return_type': 'float',
    },
    'iEta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::eFexEMRoI_v1',
        'method_name': 'iEta',
        'return_type': 'int',
    },
    'seed': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::eFexEMRoI_v1',
        'method_name': 'seed',
        'return_type': 'unsigned int',
    },
    'phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::eFexEMRoI_v1',
        'method_name': 'phi',
        'return_type': 'float',
    },
    'iPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::eFexEMRoI_v1',
        'method_name': 'iPhi',
        'return_type': 'int',
    },
    'iEtaTopo': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::eFexEMRoI_v1',
        'method_name': 'iEtaTopo',
        'return_type': 'int',
    },
    'iPhiTopo': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::eFexEMRoI_v1',
        'method_name': 'iPhiTopo',
        'return_type': 'int',
    },
    'Reta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::eFexEMRoI_v1',
        'method_name': 'Reta',
        'return_type': 'float',
    },
    'Rhad': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::eFexEMRoI_v1',
        'method_name': 'Rhad',
        'return_type': 'float',
    },
    'Wstot': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::eFexEMRoI_v1',
        'method_name': 'Wstot',
        'return_type': 'float',
    },
    'RetaCore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::eFexEMRoI_v1',
        'method_name': 'RetaCore',
        'return_type': 'uint16_t',
    },
    'RetaEnv': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::eFexEMRoI_v1',
        'method_name': 'RetaEnv',
        'return_type': 'uint16_t',
    },
    'RhadEM': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::eFexEMRoI_v1',
        'method_name': 'RhadEM',
        'return_type': 'uint16_t',
    },
    'RhadHad': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::eFexEMRoI_v1',
        'method_name': 'RhadHad',
        'return_type': 'uint16_t',
    },
    'WstotNumerator': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::eFexEMRoI_v1',
        'method_name': 'WstotNumerator',
        'return_type': 'uint16_t',
    },
    'WstotDenominator': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::eFexEMRoI_v1',
        'method_name': 'WstotDenominator',
        'return_type': 'uint16_t',
    },
    'isTOB': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::eFexEMRoI_v1',
        'method_name': 'isTOB',
        'return_type': 'char',
    },
    'tobWord': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::eFexEMRoI_v1',
        'method_name': 'tobWord',
        'return_type': 'unsigned int',
    },
    'type': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::eFexEMRoI_v1',
        'method_name': 'type',
        'return_type': 'xAOD::eFexEMRoI_v1::ObjectType',
    },
    'shelfNumber': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::eFexEMRoI_v1',
        'method_name': 'shelfNumber',
        'return_type': 'unsigned int',
    },
    'eFexNumber': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::eFexEMRoI_v1',
        'method_name': 'eFexNumber',
        'return_type': 'unsigned int',
    },
    'fpga': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::eFexEMRoI_v1',
        'method_name': 'fpga',
        'return_type': 'unsigned int',
    },
    'fpgaEta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::eFexEMRoI_v1',
        'method_name': 'fpgaEta',
        'return_type': 'unsigned int',
    },
    'fpgaPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::eFexEMRoI_v1',
        'method_name': 'fpgaPhi',
        'return_type': 'unsigned int',
    },
    'UpNotDown': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::eFexEMRoI_v1',
        'method_name': 'UpNotDown',
        'return_type': 'unsigned int',
    },
    'etTOB': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::eFexEMRoI_v1',
        'method_name': 'etTOB',
        'return_type': 'unsigned int',
    },
    'etXTOB': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::eFexEMRoI_v1',
        'method_name': 'etXTOB',
        'return_type': 'unsigned int',
    },
    'RetaThresholds': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::eFexEMRoI_v1',
        'method_name': 'RetaThresholds',
        'return_type': 'unsigned int',
    },
    'RhadThresholds': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::eFexEMRoI_v1',
        'method_name': 'RhadThresholds',
        'return_type': 'unsigned int',
    },
    'WstotThresholds': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::eFexEMRoI_v1',
        'method_name': 'WstotThresholds',
        'return_type': 'unsigned int',
    },
    'seedMax': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::eFexEMRoI_v1',
        'method_name': 'seedMax',
        'return_type': 'unsigned int',
    },
    'bcn4': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::eFexEMRoI_v1',
        'method_name': 'bcn4',
        'return_type': 'unsigned int',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::eFexEMRoI_v1',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::eFexEMRoI_v1',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::eFexEMRoI_v1',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::eFexEMRoI_v1',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::eFexEMRoI_v1',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::eFexEMRoI_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::eFexEMRoI_v1',
        'method_name': 'trackIndices',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::eFexEMRoI_v1',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::eFexEMRoI_v1',
        'method_name': 'isAvailable',
        'return_type': 'bool',
    },
}

_enum_function_map = {
    'type': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.eFexEMRoI_v1',
            'name': 'ObjectType',
            'values': [
                'xTOB',
                'TOB',
            ],
        },
    ],      
}

_defined_enums = {
    'ObjectType':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.eFexEMRoI_v1',
            'name': 'ObjectType',
            'values': [
                'xTOB',
                'TOB',
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
            'name': 'xAODTrigger/versions/eFexEMRoI_v1.h',
            'body_includes': ["xAODTrigger/versions/eFexEMRoI_v1.h"],
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
class eFexEMRoI_v1:
    "A class"

    class ObjectType(Enum):
        xTOB = 0
        TOB = 1


    def word0(self) -> int:
        "A method"
        ...

    def word1(self) -> int:
        "A method"
        ...

    def et(self) -> float:
        "A method"
        ...

    def eta(self) -> float:
        "A method"
        ...

    def iEta(self) -> int:
        "A method"
        ...

    def seed(self) -> int:
        "A method"
        ...

    def phi(self) -> float:
        "A method"
        ...

    def iPhi(self) -> int:
        "A method"
        ...

    def iEtaTopo(self) -> int:
        "A method"
        ...

    def iPhiTopo(self) -> int:
        "A method"
        ...

    def Reta(self) -> float:
        "A method"
        ...

    def Rhad(self) -> float:
        "A method"
        ...

    def Wstot(self) -> float:
        "A method"
        ...

    def RetaCore(self) -> int:
        "A method"
        ...

    def RetaEnv(self) -> int:
        "A method"
        ...

    def RhadEM(self) -> int:
        "A method"
        ...

    def RhadHad(self) -> int:
        "A method"
        ...

    def WstotNumerator(self) -> int:
        "A method"
        ...

    def WstotDenominator(self) -> int:
        "A method"
        ...

    def isTOB(self) -> str:
        "A method"
        ...

    def tobWord(self) -> int:
        "A method"
        ...

    def type(self) -> func_adl_servicex_xaodr25.xAOD.efexemroi_v1.eFexEMRoI_v1.ObjectType:
        "A method"
        ...

    def shelfNumber(self) -> int:
        "A method"
        ...

    def eFexNumber(self) -> int:
        "A method"
        ...

    def fpga(self) -> int:
        "A method"
        ...

    def fpgaEta(self) -> int:
        "A method"
        ...

    def fpgaPhi(self) -> int:
        "A method"
        ...

    def UpNotDown(self) -> int:
        "A method"
        ...

    def etTOB(self) -> int:
        "A method"
        ...

    def etXTOB(self) -> int:
        "A method"
        ...

    def RetaThresholds(self) -> int:
        "A method"
        ...

    def RhadThresholds(self) -> int:
        "A method"
        ...

    def WstotThresholds(self) -> int:
        "A method"
        ...

    def seedMax(self) -> int:
        "A method"
        ...

    def bcn4(self) -> int:
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
