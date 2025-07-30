from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class HealthCheckRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HealthCheckResponse(_message.Message):
    __slots__ = ("status", "message")
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[HealthCheckResponse.Status]
        SERVING: _ClassVar[HealthCheckResponse.Status]
        NOT_SERVING: _ClassVar[HealthCheckResponse.Status]
    UNKNOWN: HealthCheckResponse.Status
    SERVING: HealthCheckResponse.Status
    NOT_SERVING: HealthCheckResponse.Status
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    status: HealthCheckResponse.Status
    message: str
    def __init__(self, status: _Optional[_Union[HealthCheckResponse.Status, str]] = ..., message: _Optional[str] = ...) -> None: ...
