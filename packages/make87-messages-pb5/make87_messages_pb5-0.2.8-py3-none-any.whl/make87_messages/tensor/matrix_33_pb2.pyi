from make87_messages.core import header_pb2 as _header_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Matrix33(_message.Message):
    __slots__ = ("header", "m00", "m01", "m02", "m10", "m11", "m12", "m20", "m21", "m22")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    M00_FIELD_NUMBER: _ClassVar[int]
    M01_FIELD_NUMBER: _ClassVar[int]
    M02_FIELD_NUMBER: _ClassVar[int]
    M10_FIELD_NUMBER: _ClassVar[int]
    M11_FIELD_NUMBER: _ClassVar[int]
    M12_FIELD_NUMBER: _ClassVar[int]
    M20_FIELD_NUMBER: _ClassVar[int]
    M21_FIELD_NUMBER: _ClassVar[int]
    M22_FIELD_NUMBER: _ClassVar[int]
    header: _header_pb2.Header
    m00: float
    m01: float
    m02: float
    m10: float
    m11: float
    m12: float
    m20: float
    m21: float
    m22: float
    def __init__(self, header: _Optional[_Union[_header_pb2.Header, _Mapping]] = ..., m00: _Optional[float] = ..., m01: _Optional[float] = ..., m02: _Optional[float] = ..., m10: _Optional[float] = ..., m11: _Optional[float] = ..., m12: _Optional[float] = ..., m20: _Optional[float] = ..., m21: _Optional[float] = ..., m22: _Optional[float] = ...) -> None: ...
