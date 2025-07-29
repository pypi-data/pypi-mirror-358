from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr25

_method_map = {
}

_enum_function_map = {      
}

_defined_enums = {
    'EgammaType':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.EgammaParameters',
            'name': 'EgammaType',
            'values': [
                'electron',
                'unconvertedPhoton',
                'convertedPhoton',
                'NumberOfEgammaTypes',
            ],
        },
    'ShowerShapeType':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.EgammaParameters',
            'name': 'ShowerShapeType',
            'values': [
                'e011',
                'e033',
                'e132',
                'e1152',
                'ethad1',
                'ethad',
                'ehad1',
                'f1',
                'f3',
                'f1core',
                'f3core',
                'e233',
                'e235',
                'e255',
                'e237',
                'e277',
                'e333',
                'e335',
                'e337',
                'e377',
                'weta1',
                'weta2',
                'e2ts1',
                'e2tsts1',
                'fracs1',
                'widths1',
                'widths2',
                'poscs1',
                'poscs2',
                'asy1',
                'pos',
                'pos7',
                'barys1',
                'wtots1',
                'emins1',
                'emaxs1',
                'r33over37allcalo',
                'ecore',
                'Reta',
                'Rphi',
                'Eratio',
                'Rhad',
                'Rhad1',
                'DeltaE',
                'NumberOfShowerShapes',
            ],
        },
    'TrackCaloMatchType':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.EgammaParameters',
            'name': 'TrackCaloMatchType',
            'values': [
                'deltaEta0',
                'deltaEta1',
                'deltaEta2',
                'deltaEta3',
                'deltaPhi0',
                'deltaPhi1',
                'deltaPhi2',
                'deltaPhi3',
                'deltaPhiFromLastMeasurement',
                'deltaPhiRescaled0',
                'deltaPhiRescaled1',
                'deltaPhiRescaled2',
                'deltaPhiRescaled3',
                'NumberOfTrackMatchProperties',
            ],
        },
    'VertexCaloMatchType':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.EgammaParameters',
            'name': 'VertexCaloMatchType',
            'values': [
                'convMatchDeltaEta1',
                'convMatchDeltaEta2',
                'convMatchDeltaPhi1',
                'convMatchDeltaPhi2',
                'NumberOfVertexMatchProperties',
            ],
        },
    'ConversionType':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.EgammaParameters',
            'name': 'ConversionType',
            'values': [
                'unconverted',
                'singleSi',
                'singleTRT',
                'doubleSi',
                'doubleTRT',
                'doubleSiTRT',
                'NumberOfVertexConversionTypes',
            ],
        },
    'BitDefOQ':
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD.EgammaParameters',
            'name': 'BitDefOQ',
            'values': [
                'DeadHVPS',
                'DeadHVS1S2S3Core',
                'DeadHVS1S2S3Edge',
                'NonNominalHVPS',
                'NonNominalHVS1S2S3',
                'MissingFEBCellCore',
                'MissingFEBCellEdgePS',
                'MissingFEBCellEdgeS1',
                'MissingFEBCellEdgeS2',
                'MissingFEBCellEdgeS3',
                'MaskedCellCore',
                'MaskedCellEdgePS',
                'MaskedCellEdgeS1',
                'MaskedCellEdgeS2',
                'MaskedCellEdgeS3',
                'BadS1Core',
                'SporadicNoiseLowQCore',
                'SporadicNoiseLowQEdge',
                'HighQCore',
                'HighQEdge',
                'AffectedCellCore',
                'AffectedCellEdgePS',
                'AffectedCellEdgeS1',
                'AffectedCellEdgeS2',
                'AffectedCellEdgeS3',
                'HECHighQ',
                'OutTime',
                'LArQCleaning',
                'DeadCellTileS0',
                'DeadCellTileS1S2',
                'HighRcell',
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


        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class EgammaParameters:
    "A class"

    class EgammaType(Enum):
        electron = 0
        unconvertedPhoton = 1
        convertedPhoton = 2
        NumberOfEgammaTypes = 3

    class ShowerShapeType(Enum):
        e011 = 0
        e033 = 1
        e132 = 2
        e1152 = 3
        ethad1 = 4
        ethad = 5
        ehad1 = 6
        f1 = 7
        f3 = 8
        f1core = 9
        f3core = 10
        e233 = 11
        e235 = 12
        e255 = 13
        e237 = 14
        e277 = 15
        e333 = 16
        e335 = 17
        e337 = 18
        e377 = 19
        weta1 = 20
        weta2 = 21
        e2ts1 = 22
        e2tsts1 = 23
        fracs1 = 24
        widths1 = 25
        widths2 = 26
        poscs1 = 27
        poscs2 = 28
        asy1 = 29
        pos = 30
        pos7 = 31
        barys1 = 32
        wtots1 = 33
        emins1 = 34
        emaxs1 = 35
        r33over37allcalo = 36
        ecore = 37
        Reta = 38
        Rphi = 39
        Eratio = 40
        Rhad = 41
        Rhad1 = 42
        DeltaE = 43
        NumberOfShowerShapes = 44

    class TrackCaloMatchType(Enum):
        deltaEta0 = 0
        deltaEta1 = 1
        deltaEta2 = 2
        deltaEta3 = 3
        deltaPhi0 = 4
        deltaPhi1 = 5
        deltaPhi2 = 6
        deltaPhi3 = 7
        deltaPhiFromLastMeasurement = 8
        deltaPhiRescaled0 = 9
        deltaPhiRescaled1 = 10
        deltaPhiRescaled2 = 11
        deltaPhiRescaled3 = 12
        NumberOfTrackMatchProperties = 13

    class VertexCaloMatchType(Enum):
        convMatchDeltaEta1 = 0
        convMatchDeltaEta2 = 1
        convMatchDeltaPhi1 = 2
        convMatchDeltaPhi2 = 3
        NumberOfVertexMatchProperties = 4

    class ConversionType(Enum):
        unconverted = 0
        singleSi = 1
        singleTRT = 2
        doubleSi = 3
        doubleTRT = 4
        doubleSiTRT = 5
        NumberOfVertexConversionTypes = 6

    class BitDefOQ(Enum):
        DeadHVPS = 0
        DeadHVS1S2S3Core = 1
        DeadHVS1S2S3Edge = 2
        NonNominalHVPS = 3
        NonNominalHVS1S2S3 = 4
        MissingFEBCellCore = 5
        MissingFEBCellEdgePS = 6
        MissingFEBCellEdgeS1 = 7
        MissingFEBCellEdgeS2 = 8
        MissingFEBCellEdgeS3 = 9
        MaskedCellCore = 10
        MaskedCellEdgePS = 11
        MaskedCellEdgeS1 = 12
        MaskedCellEdgeS2 = 13
        MaskedCellEdgeS3 = 14
        BadS1Core = 15
        SporadicNoiseLowQCore = 16
        SporadicNoiseLowQEdge = 17
        HighQCore = 18
        HighQEdge = 19
        AffectedCellCore = 20
        AffectedCellEdgePS = 21
        AffectedCellEdgeS1 = 22
        AffectedCellEdgeS2 = 23
        AffectedCellEdgeS3 = 24
        HECHighQ = 25
        OutTime = 26
        LArQCleaning = 27
        DeadCellTileS0 = 28
        DeadCellTileS1S2 = 29
        HighRcell = 30

