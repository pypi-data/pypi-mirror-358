from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr21

_method_map = {
    'XX': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'XX',
        'return_type': 'double',
    },
    'XY': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'XY',
        'return_type': 'double',
    },
    'XZ': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'XZ',
        'return_type': 'double',
    },
    'YX': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'YX',
        'return_type': 'double',
    },
    'YY': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'YY',
        'return_type': 'double',
    },
    'YZ': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'YZ',
        'return_type': 'double',
    },
    'ZX': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'ZX',
        'return_type': 'double',
    },
    'ZY': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'ZY',
        'return_type': 'double',
    },
    'ZZ': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'ZZ',
        'return_type': 'double',
    },
    'IsIdentity': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'IsIdentity',
        'return_type': 'bool',
    },
    'Transform': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'Transform',
        'return_type': 'TRotation',
    },
    'Inverse': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'Inverse',
        'return_type': 'TRotation',
    },
    'Invert': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'Invert',
        'return_type': 'TRotation',
    },
    'RotateX': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'RotateX',
        'return_type': 'TRotation',
    },
    'RotateY': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'RotateY',
        'return_type': 'TRotation',
    },
    'RotateZ': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'RotateZ',
        'return_type': 'TRotation',
    },
    'Rotate': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'Rotate',
        'return_type': 'TRotation',
    },
    'RotateAxes': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'RotateAxes',
        'return_type': 'TRotation',
    },
    'PhiX': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'PhiX',
        'return_type': 'double',
    },
    'PhiY': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'PhiY',
        'return_type': 'double',
    },
    'PhiZ': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'PhiZ',
        'return_type': 'double',
    },
    'ThetaX': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'ThetaX',
        'return_type': 'double',
    },
    'ThetaY': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'ThetaY',
        'return_type': 'double',
    },
    'ThetaZ': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'ThetaZ',
        'return_type': 'double',
    },
    'SetToIdentity': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'SetToIdentity',
        'return_type': 'TRotation',
    },
    'SetXEulerAngles': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'SetXEulerAngles',
        'return_type': 'TRotation',
    },
    'RotateXEulerAngles': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'RotateXEulerAngles',
        'return_type': 'TRotation',
    },
    'GetXPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'GetXPhi',
        'return_type': 'double',
    },
    'GetXTheta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'GetXTheta',
        'return_type': 'double',
    },
    'GetXPsi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'GetXPsi',
        'return_type': 'double',
    },
    'SetYEulerAngles': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'SetYEulerAngles',
        'return_type': 'TRotation',
    },
    'RotateYEulerAngles': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'RotateYEulerAngles',
        'return_type': 'TRotation',
    },
    'GetYPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'GetYPhi',
        'return_type': 'double',
    },
    'GetYTheta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'GetYTheta',
        'return_type': 'double',
    },
    'GetYPsi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'GetYPsi',
        'return_type': 'double',
    },
    'SetXAxis': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'SetXAxis',
        'return_type': 'TRotation',
    },
    'SetYAxis': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'SetYAxis',
        'return_type': 'TRotation',
    },
    'SetZAxis': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'SetZAxis',
        'return_type': 'TRotation',
    },
    'DeclFileName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'DeclFileName',
        'return_type': 'const char *',
    },
    'ImplFileLine': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'ImplFileLine',
        'return_type': 'int',
    },
    'ImplFileName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'ImplFileName',
        'return_type': 'const char *',
    },
    'Class_Name': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'Class_Name',
        'return_type': 'const char *',
    },
    'DeclFileLine': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'DeclFileLine',
        'return_type': 'int',
    },
    'Hash': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'Hash',
        'return_type': 'unsigned long',
    },
    'ClassName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'ClassName',
        'return_type': 'const char *',
    },
    'CheckedHash': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'CheckedHash',
        'return_type': 'unsigned long',
    },
    'DistancetoPrimitive': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'DistancetoPrimitive',
        'return_type': 'int',
    },
    'GetUniqueID': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'GetUniqueID',
        'return_type': 'unsigned int',
    },
    'GetName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'GetName',
        'return_type': 'const char *',
    },
    'GetIconName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'GetIconName',
        'return_type': 'const char *',
    },
    'GetObjectInfo': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'GetObjectInfo',
        'return_type': 'char *',
    },
    'GetTitle': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'GetTitle',
        'return_type': 'const char *',
    },
    'HasInconsistentHash': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'HasInconsistentHash',
        'return_type': 'bool',
    },
    'InheritsFrom': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'InheritsFrom',
        'return_type': 'bool',
    },
    'IsFolder': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'IsFolder',
        'return_type': 'bool',
    },
    'IsSortable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'IsSortable',
        'return_type': 'bool',
    },
    'IsOnHeap': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'IsOnHeap',
        'return_type': 'bool',
    },
    'IsZombie': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'IsZombie',
        'return_type': 'bool',
    },
    'Notify': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'Notify',
        'return_type': 'bool',
    },
    'Read': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'Read',
        'return_type': 'int',
    },
    'Write': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'Write',
        'return_type': 'int',
    },
    'TestBit': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'TestBit',
        'return_type': 'bool',
    },
    'TestBits': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'TestBits',
        'return_type': 'int',
    },
    'GetDtorOnly': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
        'method_name': 'GetDtorOnly',
        'return_type': 'long',
    },
    'GetObjectStat': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TRotation',
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
class TRotation:
    "A class"


    def XX(self) -> float:
        "A method"
        ...

    def XY(self) -> float:
        "A method"
        ...

    def XZ(self) -> float:
        "A method"
        ...

    def YX(self) -> float:
        "A method"
        ...

    def YY(self) -> float:
        "A method"
        ...

    def YZ(self) -> float:
        "A method"
        ...

    def ZX(self) -> float:
        "A method"
        ...

    def ZY(self) -> float:
        "A method"
        ...

    def ZZ(self) -> float:
        "A method"
        ...

    def IsIdentity(self) -> bool:
        "A method"
        ...

    def Transform(self, noname_arg: TRotation) -> func_adl_servicex_xaodr21.trotation.TRotation:
        "A method"
        ...

    def Inverse(self) -> func_adl_servicex_xaodr21.trotation.TRotation:
        "A method"
        ...

    def Invert(self) -> func_adl_servicex_xaodr21.trotation.TRotation:
        "A method"
        ...

    def RotateX(self, noname_arg: float) -> func_adl_servicex_xaodr21.trotation.TRotation:
        "A method"
        ...

    def RotateY(self, noname_arg: float) -> func_adl_servicex_xaodr21.trotation.TRotation:
        "A method"
        ...

    def RotateZ(self, noname_arg: float) -> func_adl_servicex_xaodr21.trotation.TRotation:
        "A method"
        ...

    def Rotate(self, noname_arg: float, noname_arg_1: func_adl_servicex_xaodr21.tvector3.TVector3) -> func_adl_servicex_xaodr21.trotation.TRotation:
        "A method"
        ...

    def RotateAxes(self, newX: func_adl_servicex_xaodr21.tvector3.TVector3, newY: func_adl_servicex_xaodr21.tvector3.TVector3, newZ: func_adl_servicex_xaodr21.tvector3.TVector3) -> func_adl_servicex_xaodr21.trotation.TRotation:
        "A method"
        ...

    def PhiX(self) -> float:
        "A method"
        ...

    def PhiY(self) -> float:
        "A method"
        ...

    def PhiZ(self) -> float:
        "A method"
        ...

    def ThetaX(self) -> float:
        "A method"
        ...

    def ThetaY(self) -> float:
        "A method"
        ...

    def ThetaZ(self) -> float:
        "A method"
        ...

    def SetToIdentity(self) -> func_adl_servicex_xaodr21.trotation.TRotation:
        "A method"
        ...

    def SetXEulerAngles(self, phi: float, theta: float, psi: float) -> func_adl_servicex_xaodr21.trotation.TRotation:
        "A method"
        ...

    def RotateXEulerAngles(self, phi: float, theta: float, psi: float) -> func_adl_servicex_xaodr21.trotation.TRotation:
        "A method"
        ...

    def GetXPhi(self) -> float:
        "A method"
        ...

    def GetXTheta(self) -> float:
        "A method"
        ...

    def GetXPsi(self) -> float:
        "A method"
        ...

    def SetYEulerAngles(self, phi: float, theta: float, psi: float) -> func_adl_servicex_xaodr21.trotation.TRotation:
        "A method"
        ...

    def RotateYEulerAngles(self, phi: float, theta: float, psi: float) -> func_adl_servicex_xaodr21.trotation.TRotation:
        "A method"
        ...

    def GetYPhi(self) -> float:
        "A method"
        ...

    def GetYTheta(self) -> float:
        "A method"
        ...

    def GetYPsi(self) -> float:
        "A method"
        ...

    def SetXAxis(self, axis: func_adl_servicex_xaodr21.tvector3.TVector3) -> func_adl_servicex_xaodr21.trotation.TRotation:
        "A method"
        ...

    def SetYAxis(self, axis: func_adl_servicex_xaodr21.tvector3.TVector3) -> func_adl_servicex_xaodr21.trotation.TRotation:
        "A method"
        ...

    def SetZAxis(self, axis: func_adl_servicex_xaodr21.tvector3.TVector3) -> func_adl_servicex_xaodr21.trotation.TRotation:
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
