from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr21

_method_map = {
    'x': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'x',
        'return_type': 'double',
    },
    'y': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'y',
        'return_type': 'double',
    },
    'z': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'z',
        'return_type': 'double',
    },
    'X': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'X',
        'return_type': 'double',
    },
    'Y': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'Y',
        'return_type': 'double',
    },
    'Z': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'Z',
        'return_type': 'double',
    },
    'Px': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'Px',
        'return_type': 'double',
    },
    'Py': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'Py',
        'return_type': 'double',
    },
    'Pz': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'Pz',
        'return_type': 'double',
    },
    'Phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'Phi',
        'return_type': 'double',
    },
    'Theta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'Theta',
        'return_type': 'double',
    },
    'CosTheta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'CosTheta',
        'return_type': 'double',
    },
    'Mag2': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'Mag2',
        'return_type': 'double',
    },
    'Mag': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'Mag',
        'return_type': 'double',
    },
    'Perp2': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'Perp2',
        'return_type': 'double',
    },
    'Pt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'Pt',
        'return_type': 'double',
    },
    'Perp': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'Perp',
        'return_type': 'double',
    },
    'DeltaPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'DeltaPhi',
        'return_type': 'double',
    },
    'DeltaR': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'DeltaR',
        'return_type': 'double',
    },
    'DrEtaPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'DrEtaPhi',
        'return_type': 'double',
    },
    'EtaPhiVector': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'EtaPhiVector',
        'return_type': 'TVector2',
    },
    'Unit': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'Unit',
        'return_type': 'TVector3',
    },
    'Orthogonal': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'Orthogonal',
        'return_type': 'TVector3',
    },
    'Dot': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'Dot',
        'return_type': 'double',
    },
    'Cross': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'Cross',
        'return_type': 'TVector3',
    },
    'Angle': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'Angle',
        'return_type': 'double',
    },
    'PseudoRapidity': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'PseudoRapidity',
        'return_type': 'double',
    },
    'Eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'Eta',
        'return_type': 'double',
    },
    'Transform': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'Transform',
        'return_type': 'TVector3',
    },
    'XYvector': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'XYvector',
        'return_type': 'TVector2',
    },
    'DeclFileName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'DeclFileName',
        'return_type': 'const char *',
    },
    'ImplFileLine': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'ImplFileLine',
        'return_type': 'int',
    },
    'ImplFileName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'ImplFileName',
        'return_type': 'const char *',
    },
    'Class_Name': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'Class_Name',
        'return_type': 'const char *',
    },
    'DeclFileLine': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'DeclFileLine',
        'return_type': 'int',
    },
    'Hash': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'Hash',
        'return_type': 'unsigned long',
    },
    'ClassName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'ClassName',
        'return_type': 'const char *',
    },
    'CheckedHash': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'CheckedHash',
        'return_type': 'unsigned long',
    },
    'DistancetoPrimitive': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'DistancetoPrimitive',
        'return_type': 'int',
    },
    'GetUniqueID': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'GetUniqueID',
        'return_type': 'unsigned int',
    },
    'GetName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'GetName',
        'return_type': 'const char *',
    },
    'GetIconName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'GetIconName',
        'return_type': 'const char *',
    },
    'GetObjectInfo': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'GetObjectInfo',
        'return_type': 'char *',
    },
    'GetTitle': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'GetTitle',
        'return_type': 'const char *',
    },
    'HasInconsistentHash': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'HasInconsistentHash',
        'return_type': 'bool',
    },
    'InheritsFrom': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'InheritsFrom',
        'return_type': 'bool',
    },
    'IsFolder': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'IsFolder',
        'return_type': 'bool',
    },
    'IsSortable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'IsSortable',
        'return_type': 'bool',
    },
    'IsOnHeap': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'IsOnHeap',
        'return_type': 'bool',
    },
    'IsZombie': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'IsZombie',
        'return_type': 'bool',
    },
    'Notify': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'Notify',
        'return_type': 'bool',
    },
    'Read': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'Read',
        'return_type': 'int',
    },
    'Write': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'Write',
        'return_type': 'int',
    },
    'TestBit': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'TestBit',
        'return_type': 'bool',
    },
    'TestBits': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'TestBits',
        'return_type': 'int',
    },
    'GetDtorOnly': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'GetDtorOnly',
        'return_type': 'long',
    },
    'GetObjectStat': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector3',
        'method_name': 'GetObjectStat',
        'return_type': 'bool',
    },
}

_enum_function_map = {      
}

_defined_enums = {      
}

_object_cpp_as_py_namespace=""

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
class TVector3:
    "A class"


    def x(self) -> float:
        "A method"
        ...

    def y(self) -> float:
        "A method"
        ...

    def z(self) -> float:
        "A method"
        ...

    def X(self) -> float:
        "A method"
        ...

    def Y(self) -> float:
        "A method"
        ...

    def Z(self) -> float:
        "A method"
        ...

    def Px(self) -> float:
        "A method"
        ...

    def Py(self) -> float:
        "A method"
        ...

    def Pz(self) -> float:
        "A method"
        ...

    def Phi(self) -> float:
        "A method"
        ...

    def Theta(self) -> float:
        "A method"
        ...

    def CosTheta(self) -> float:
        "A method"
        ...

    def Mag2(self) -> float:
        "A method"
        ...

    def Mag(self) -> float:
        "A method"
        ...

    def Perp2(self) -> float:
        "A method"
        ...

    def Pt(self) -> float:
        "A method"
        ...

    def Perp(self) -> float:
        "A method"
        ...

    def DeltaPhi(self, noname_arg: TVector3) -> float:
        "A method"
        ...

    def DeltaR(self, noname_arg: TVector3) -> float:
        "A method"
        ...

    def DrEtaPhi(self, noname_arg: TVector3) -> float:
        "A method"
        ...

    def EtaPhiVector(self) -> func_adl_servicex_xaodr21.tvector2.TVector2:
        "A method"
        ...

    def Unit(self) -> func_adl_servicex_xaodr21.tvector3.TVector3:
        "A method"
        ...

    def Orthogonal(self) -> func_adl_servicex_xaodr21.tvector3.TVector3:
        "A method"
        ...

    def Dot(self, noname_arg: TVector3) -> float:
        "A method"
        ...

    def Cross(self, noname_arg: TVector3) -> func_adl_servicex_xaodr21.tvector3.TVector3:
        "A method"
        ...

    def Angle(self, noname_arg: TVector3) -> float:
        "A method"
        ...

    def PseudoRapidity(self) -> float:
        "A method"
        ...

    def Eta(self) -> float:
        "A method"
        ...

    def Transform(self, noname_arg: func_adl_servicex_xaodr21.trotation.TRotation) -> func_adl_servicex_xaodr21.tvector3.TVector3:
        "A method"
        ...

    def XYvector(self) -> func_adl_servicex_xaodr21.tvector2.TVector2:
        "A method"
        ...

    def DeclFileName(self) -> str:
        "A method"
        ...

    def ImplFileLine(self) -> int:
        "A method"
        ...

    def ImplFileName(self) -> str:
        "A method"
        ...

    def Class_Name(self) -> str:
        "A method"
        ...

    def DeclFileLine(self) -> int:
        "A method"
        ...

    def Hash(self) -> int:
        "A method"
        ...

    def ClassName(self) -> str:
        "A method"
        ...

    def CheckedHash(self) -> int:
        "A method"
        ...

    def DistancetoPrimitive(self, px: int, py: int) -> int:
        "A method"
        ...

    def GetUniqueID(self) -> int:
        "A method"
        ...

    def GetName(self) -> str:
        "A method"
        ...

    def GetIconName(self) -> str:
        "A method"
        ...

    def GetObjectInfo(self, px: int, py: int) -> str:
        "A method"
        ...

    def GetTitle(self) -> str:
        "A method"
        ...

    def HasInconsistentHash(self) -> bool:
        "A method"
        ...

    def InheritsFrom(self, classname: int) -> bool:
        "A method"
        ...

    def IsFolder(self) -> bool:
        "A method"
        ...

    def IsSortable(self) -> bool:
        "A method"
        ...

    def IsOnHeap(self) -> bool:
        "A method"
        ...

    def IsZombie(self) -> bool:
        "A method"
        ...

    def Notify(self) -> bool:
        "A method"
        ...

    def Read(self, name: int) -> int:
        "A method"
        ...

    def Write(self, name: int, option: int, bufsize: int) -> int:
        "A method"
        ...

    def TestBit(self, f: int) -> bool:
        "A method"
        ...

    def TestBits(self, f: int) -> int:
        "A method"
        ...

    def GetDtorOnly(self) -> int:
        "A method"
        ...

    def GetObjectStat(self) -> bool:
        "A method"
        ...
