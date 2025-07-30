from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr21

_method_map = {
    'Kill': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'Kill',
        'return_type': 'int',
    },
    'GetPriority': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'GetPriority',
        'return_type': 'TThread::EPriority',
    },
    'GetState': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'GetState',
        'return_type': 'TThread::EState',
    },
    'GetId': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'GetId',
        'return_type': 'long',
    },
    'IsInitialized': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'IsInitialized',
        'return_type': 'bool',
    },
    'Exists': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'Exists',
        'return_type': 'int',
    },
    'GetThread': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'GetThread',
        'return_type': 'TThread *',
    },
    'Lock': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'Lock',
        'return_type': 'int',
    },
    'TryLock': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'TryLock',
        'return_type': 'int',
    },
    'UnLock': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'UnLock',
        'return_type': 'int',
    },
    'Self': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'Self',
        'return_type': 'TThread *',
    },
    'SelfId': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'SelfId',
        'return_type': 'long',
    },
    'Sleep': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'Sleep',
        'return_type': 'int',
    },
    'GetTime': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'GetTime',
        'return_type': 'int',
    },
    'SetCancelOn': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'SetCancelOn',
        'return_type': 'int',
    },
    'SetCancelOff': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'SetCancelOff',
        'return_type': 'int',
    },
    'SetCancelAsynchronous': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'SetCancelAsynchronous',
        'return_type': 'int',
    },
    'SetCancelDeferred': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'SetCancelDeferred',
        'return_type': 'int',
    },
    'CancelPoint': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'CancelPoint',
        'return_type': 'int',
    },
    'CleanUpPop': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'CleanUpPop',
        'return_type': 'int',
    },
    'CleanUp': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'CleanUp',
        'return_type': 'int',
    },
    'DeclFileName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'DeclFileName',
        'return_type': 'const char *',
    },
    'ImplFileLine': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'ImplFileLine',
        'return_type': 'int',
    },
    'ImplFileName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'ImplFileName',
        'return_type': 'const char *',
    },
    'Class_Name': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'Class_Name',
        'return_type': 'const char *',
    },
    'DeclFileLine': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'DeclFileLine',
        'return_type': 'int',
    },
    'Hash': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'Hash',
        'return_type': 'unsigned long',
    },
    'GetName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'GetName',
        'return_type': 'const char *',
    },
    'GetTitle': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'GetTitle',
        'return_type': 'const char *',
    },
    'IsSortable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'IsSortable',
        'return_type': 'bool',
    },
    'Sizeof': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'Sizeof',
        'return_type': 'int',
    },
    'ClassName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'ClassName',
        'return_type': 'const char *',
    },
    'CheckedHash': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'CheckedHash',
        'return_type': 'unsigned long',
    },
    'DistancetoPrimitive': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'DistancetoPrimitive',
        'return_type': 'int',
    },
    'GetUniqueID': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'GetUniqueID',
        'return_type': 'unsigned int',
    },
    'GetIconName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'GetIconName',
        'return_type': 'const char *',
    },
    'GetObjectInfo': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'GetObjectInfo',
        'return_type': 'char *',
    },
    'HasInconsistentHash': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'HasInconsistentHash',
        'return_type': 'bool',
    },
    'InheritsFrom': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'InheritsFrom',
        'return_type': 'bool',
    },
    'IsFolder': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'IsFolder',
        'return_type': 'bool',
    },
    'IsOnHeap': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'IsOnHeap',
        'return_type': 'bool',
    },
    'IsZombie': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'IsZombie',
        'return_type': 'bool',
    },
    'Notify': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'Notify',
        'return_type': 'bool',
    },
    'Read': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'Read',
        'return_type': 'int',
    },
    'Write': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'Write',
        'return_type': 'int',
    },
    'TestBit': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'TestBit',
        'return_type': 'bool',
    },
    'TestBits': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'TestBits',
        'return_type': 'int',
    },
    'GetDtorOnly': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'GetDtorOnly',
        'return_type': 'long',
    },
    'GetObjectStat': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TThread',
        'method_name': 'GetObjectStat',
        'return_type': 'bool',
    },
}

_enum_function_map = {
    'GetPriority': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'TThread',
            'name': 'EPriority',
            'values': [
                'kLowPriority',
                'kNormalPriority',
                'kHighPriority',
            ],
        },
    ],
    'GetState': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'TThread',
            'name': 'EState',
            'values': [
                'kInvalidState',
                'kNewState',
                'kRunningState',
                'kTerminatedState',
                'kFinishedState',
                'kCancelingState',
                'kCanceledState',
                'kDeletingState',
            ],
        },
    ],      
}

_defined_enums = {
    'EPriority':
        {
            'metadata_type': 'define_enum',
            'namespace': 'TThread',
            'name': 'EPriority',
            'values': [
                'kLowPriority',
                'kNormalPriority',
                'kHighPriority',
            ],
        },
    'EState':
        {
            'metadata_type': 'define_enum',
            'namespace': 'TThread',
            'name': 'EState',
            'values': [
                'kInvalidState',
                'kNewState',
                'kRunningState',
                'kTerminatedState',
                'kFinishedState',
                'kCancelingState',
                'kCanceledState',
                'kDeletingState',
            ],
        },      
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
class TThread:
    "A class"

    class EPriority(Enum):
        kLowPriority = 0
        kNormalPriority = 1
        kHighPriority = 2

    class EState(Enum):
        kInvalidState = 0
        kNewState = 1
        kRunningState = 2
        kTerminatedState = 3
        kFinishedState = 4
        kCancelingState = 5
        kCanceledState = 6
        kDeletingState = 7


    def Kill(self) -> int:
        "A method"
        ...

    def GetPriority(self) -> func_adl_servicex_xaodr21.tthread.TThread.EPriority:
        "A method"
        ...

    def GetState(self) -> func_adl_servicex_xaodr21.tthread.TThread.EState:
        "A method"
        ...

    def GetId(self) -> int:
        "A method"
        ...

    def IsInitialized(self) -> bool:
        "A method"
        ...

    def Exists(self) -> int:
        "A method"
        ...

    def GetThread(self, id: int) -> func_adl_servicex_xaodr21.tthread.TThread:
        "A method"
        ...

    def Lock(self) -> int:
        "A method"
        ...

    def TryLock(self) -> int:
        "A method"
        ...

    def UnLock(self) -> int:
        "A method"
        ...

    def Self(self) -> func_adl_servicex_xaodr21.tthread.TThread:
        "A method"
        ...

    def SelfId(self) -> int:
        "A method"
        ...

    def Sleep(self, secs: int, nanos: int) -> int:
        "A method"
        ...

    def GetTime(self, absSec: int, absNanoSec: int) -> int:
        "A method"
        ...

    def SetCancelOn(self) -> int:
        "A method"
        ...

    def SetCancelOff(self) -> int:
        "A method"
        ...

    def SetCancelAsynchronous(self) -> int:
        "A method"
        ...

    def SetCancelDeferred(self) -> int:
        "A method"
        ...

    def CancelPoint(self) -> int:
        "A method"
        ...

    def CleanUpPop(self, exe: int) -> int:
        "A method"
        ...

    def CleanUp(self) -> int:
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

    def GetName(self) -> str:
        "A method"
        ...

    def GetTitle(self) -> str:
        "A method"
        ...

    def IsSortable(self) -> bool:
        "A method"
        ...

    def Sizeof(self) -> int:
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

    def GetIconName(self) -> str:
        "A method"
        ...

    def GetObjectInfo(self, px: int, py: int) -> str:
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
