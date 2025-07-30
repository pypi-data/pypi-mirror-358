from make87_messages.core import header_pb2 as _header_pb2
from make87_messages.spatial.translation import translation_2d_pb2 as _translation_2d_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Pose2D(_message.Message):
    __slots__ = ("header", "translation", "rotation")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    TRANSLATION_FIELD_NUMBER: _ClassVar[int]
    ROTATION_FIELD_NUMBER: _ClassVar[int]
    header: _header_pb2.Header
    translation: _translation_2d_pb2.Translation2D
    rotation: float
    def __init__(self, header: _Optional[_Union[_header_pb2.Header, _Mapping]] = ..., translation: _Optional[_Union[_translation_2d_pb2.Translation2D, _Mapping]] = ..., rotation: _Optional[float] = ...) -> None: ...
