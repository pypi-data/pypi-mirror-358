from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr25

_method_map = {
    'ParSettings': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::Fit::FitConfig',
        'method_name': 'ParSettings',
        'return_type': 'const ROOT::Fit::ParameterSettings',
    },
    'ParamsSettings': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::Fit::FitConfig',
        'method_name': 'ParamsSettings',
        'return_type_element': 'ROOT::Fit::ParameterSettings',
        'return_type_collection': 'const vector<ROOT::Fit::ParameterSettings>',
    },
    'NPar': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::Fit::FitConfig',
        'method_name': 'NPar',
        'return_type': 'unsigned int',
    },
    'ParamsValues': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::Fit::FitConfig',
        'method_name': 'ParamsValues',
        'return_type_element': 'float',
        'return_type_collection': 'vector<double>',
    },
    'CreateMinimizer': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::Fit::FitConfig',
        'method_name': 'CreateMinimizer',
        'return_type': 'ROOT::Math::Minimizer *',
    },
    'MinimizerOptions': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::Fit::FitConfig',
        'method_name': 'MinimizerOptions',
        'return_type': 'ROOT::Math::MinimizerOptions',
    },
    'MinimizerType': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::Fit::FitConfig',
        'method_name': 'MinimizerType',
        'return_type': 'const string',
    },
    'MinimizerAlgoType': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::Fit::FitConfig',
        'method_name': 'MinimizerAlgoType',
        'return_type': 'const string',
    },
    'MinimizerName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::Fit::FitConfig',
        'method_name': 'MinimizerName',
        'return_type': 'string',
    },
    'NormalizeErrors': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::Fit::FitConfig',
        'method_name': 'NormalizeErrors',
        'return_type': 'bool',
    },
    'ParabErrors': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::Fit::FitConfig',
        'method_name': 'ParabErrors',
        'return_type': 'bool',
    },
    'MinosErrors': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::Fit::FitConfig',
        'method_name': 'MinosErrors',
        'return_type': 'bool',
    },
    'UpdateAfterFit': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::Fit::FitConfig',
        'method_name': 'UpdateAfterFit',
        'return_type': 'bool',
    },
    'UseWeightCorrection': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::Fit::FitConfig',
        'method_name': 'UseWeightCorrection',
        'return_type': 'bool',
    },
    'MinosParams': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ROOT::Fit::FitConfig',
        'method_name': 'MinosParams',
        'return_type_element': 'unsigned short',
        'return_type_collection': 'const vector<unsigned int>',
    },
}

_enum_function_map = {      
}

_defined_enums = {      
}

_object_cpp_as_py_namespace="ROOT.Fit"

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


        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class FitConfig:
    "A class"


    def ParSettings(self, i: int) -> func_adl_servicex_xaodr25.ROOT.Fit.parametersettings.ParameterSettings:
        "A method"
        ...

    def ParamsSettings(self) -> func_adl_servicex_xaodr25.vector_root_fit_parametersettings_.vector_ROOT_Fit_ParameterSettings_:
        "A method"
        ...

    def NPar(self) -> int:
        "A method"
        ...

    def ParamsValues(self) -> func_adl_servicex_xaodr25.vector_float_.vector_float_:
        "A method"
        ...

    def CreateMinimizer(self) -> func_adl_servicex_xaodr25.ROOT.Math.minimizer.Minimizer:
        "A method"
        ...

    def MinimizerOptions(self) -> func_adl_servicex_xaodr25.ROOT.Math.minimizeroptions.MinimizerOptions:
        "A method"
        ...

    def MinimizerType(self) -> str:
        "A method"
        ...

    def MinimizerAlgoType(self) -> str:
        "A method"
        ...

    def MinimizerName(self) -> str:
        "A method"
        ...

    def NormalizeErrors(self) -> bool:
        "A method"
        ...

    def ParabErrors(self) -> bool:
        "A method"
        ...

    def MinosErrors(self) -> bool:
        "A method"
        ...

    def UpdateAfterFit(self) -> bool:
        "A method"
        ...

    def UseWeightCorrection(self) -> bool:
        "A method"
        ...

    def MinosParams(self) -> func_adl_servicex_xaodr25.vector_int_.vector_int_:
        "A method"
        ...
