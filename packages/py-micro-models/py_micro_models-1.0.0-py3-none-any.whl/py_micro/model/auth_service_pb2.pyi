from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import field_mask_pb2 as _field_mask_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Role(_message.Message):
    __slots__ = ("id", "name", "description", "permission_ids", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PERMISSION_IDS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    permission_ids: _containers.RepeatedScalarFieldContainer[str]
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., permission_ids: _Optional[_Iterable[str]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Permission(_message.Message):
    __slots__ = ("id", "resource", "action", "description", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    resource: str
    action: str
    description: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., resource: _Optional[str] = ..., action: _Optional[str] = ..., description: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class CreateRoleRequest(_message.Message):
    __slots__ = ("name", "description", "permission_ids")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PERMISSION_IDS_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    permission_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., permission_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class GetRoleRequest(_message.Message):
    __slots__ = ("id", "name")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class UpdateRoleRequest(_message.Message):
    __slots__ = ("id", "role", "update_mask")
    ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    UPDATE_MASK_FIELD_NUMBER: _ClassVar[int]
    id: str
    role: Role
    update_mask: _field_mask_pb2.FieldMask
    def __init__(self, id: _Optional[str] = ..., role: _Optional[_Union[Role, _Mapping]] = ..., update_mask: _Optional[_Union[_field_mask_pb2.FieldMask, _Mapping]] = ...) -> None: ...

class DeleteRoleRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class ListRolesRequest(_message.Message):
    __slots__ = ("page_size", "page_token", "filter")
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    page_size: int
    page_token: str
    filter: str
    def __init__(self, page_size: _Optional[int] = ..., page_token: _Optional[str] = ..., filter: _Optional[str] = ...) -> None: ...

class ListRolesResponse(_message.Message):
    __slots__ = ("roles", "next_page_token", "total_count")
    ROLES_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    roles: _containers.RepeatedCompositeFieldContainer[Role]
    next_page_token: str
    total_count: int
    def __init__(self, roles: _Optional[_Iterable[_Union[Role, _Mapping]]] = ..., next_page_token: _Optional[str] = ..., total_count: _Optional[int] = ...) -> None: ...

class AssignRoleToUserRequest(_message.Message):
    __slots__ = ("user_id", "role_id")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    role_id: str
    def __init__(self, user_id: _Optional[str] = ..., role_id: _Optional[str] = ...) -> None: ...

class RemoveRoleFromUserRequest(_message.Message):
    __slots__ = ("user_id", "role_id")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    role_id: str
    def __init__(self, user_id: _Optional[str] = ..., role_id: _Optional[str] = ...) -> None: ...

class CreatePermissionRequest(_message.Message):
    __slots__ = ("resource", "action", "description")
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    resource: str
    action: str
    description: str
    def __init__(self, resource: _Optional[str] = ..., action: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class GetPermissionRequest(_message.Message):
    __slots__ = ("id", "resource_action")
    ID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_ACTION_FIELD_NUMBER: _ClassVar[int]
    id: str
    resource_action: str
    def __init__(self, id: _Optional[str] = ..., resource_action: _Optional[str] = ...) -> None: ...

class UpdatePermissionRequest(_message.Message):
    __slots__ = ("id", "permission", "update_mask")
    ID_FIELD_NUMBER: _ClassVar[int]
    PERMISSION_FIELD_NUMBER: _ClassVar[int]
    UPDATE_MASK_FIELD_NUMBER: _ClassVar[int]
    id: str
    permission: Permission
    update_mask: _field_mask_pb2.FieldMask
    def __init__(self, id: _Optional[str] = ..., permission: _Optional[_Union[Permission, _Mapping]] = ..., update_mask: _Optional[_Union[_field_mask_pb2.FieldMask, _Mapping]] = ...) -> None: ...

class DeletePermissionRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class ListPermissionsRequest(_message.Message):
    __slots__ = ("page_size", "page_token", "filter")
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    page_size: int
    page_token: str
    filter: str
    def __init__(self, page_size: _Optional[int] = ..., page_token: _Optional[str] = ..., filter: _Optional[str] = ...) -> None: ...

class ListPermissionsResponse(_message.Message):
    __slots__ = ("permissions", "next_page_token", "total_count")
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    permissions: _containers.RepeatedCompositeFieldContainer[Permission]
    next_page_token: str
    total_count: int
    def __init__(self, permissions: _Optional[_Iterable[_Union[Permission, _Mapping]]] = ..., next_page_token: _Optional[str] = ..., total_count: _Optional[int] = ...) -> None: ...

class AssignPermissionToRoleRequest(_message.Message):
    __slots__ = ("role_id", "permission_id")
    ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    PERMISSION_ID_FIELD_NUMBER: _ClassVar[int]
    role_id: str
    permission_id: str
    def __init__(self, role_id: _Optional[str] = ..., permission_id: _Optional[str] = ...) -> None: ...

class RemovePermissionFromRoleRequest(_message.Message):
    __slots__ = ("role_id", "permission_id")
    ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    PERMISSION_ID_FIELD_NUMBER: _ClassVar[int]
    role_id: str
    permission_id: str
    def __init__(self, role_id: _Optional[str] = ..., permission_id: _Optional[str] = ...) -> None: ...

class LoginRequest(_message.Message):
    __slots__ = ("username", "email", "password")
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    username: str
    email: str
    password: str
    def __init__(self, username: _Optional[str] = ..., email: _Optional[str] = ..., password: _Optional[str] = ...) -> None: ...

class LoginResponse(_message.Message):
    __slots__ = ("access_token", "refresh_token", "expires_in")
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    REFRESH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_IN_FIELD_NUMBER: _ClassVar[int]
    access_token: str
    refresh_token: str
    expires_in: int
    def __init__(self, access_token: _Optional[str] = ..., refresh_token: _Optional[str] = ..., expires_in: _Optional[int] = ...) -> None: ...

class LogoutRequest(_message.Message):
    __slots__ = ("access_token",)
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    access_token: str
    def __init__(self, access_token: _Optional[str] = ...) -> None: ...

class RefreshTokenRequest(_message.Message):
    __slots__ = ("refresh_token",)
    REFRESH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    refresh_token: str
    def __init__(self, refresh_token: _Optional[str] = ...) -> None: ...

class RefreshTokenResponse(_message.Message):
    __slots__ = ("access_token", "refresh_token", "expires_in")
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    REFRESH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_IN_FIELD_NUMBER: _ClassVar[int]
    access_token: str
    refresh_token: str
    expires_in: int
    def __init__(self, access_token: _Optional[str] = ..., refresh_token: _Optional[str] = ..., expires_in: _Optional[int] = ...) -> None: ...

class VerifyTokenRequest(_message.Message):
    __slots__ = ("token",)
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    token: str
    def __init__(self, token: _Optional[str] = ...) -> None: ...

class VerifyTokenResponse(_message.Message):
    __slots__ = ("valid", "user_id", "roles", "permissions")
    VALID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    ROLES_FIELD_NUMBER: _ClassVar[int]
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    valid: bool
    user_id: str
    roles: _containers.RepeatedScalarFieldContainer[str]
    permissions: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, valid: bool = ..., user_id: _Optional[str] = ..., roles: _Optional[_Iterable[str]] = ..., permissions: _Optional[_Iterable[str]] = ...) -> None: ...

class CheckPermissionRequest(_message.Message):
    __slots__ = ("user_id", "resource", "action")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    resource: str
    action: str
    def __init__(self, user_id: _Optional[str] = ..., resource: _Optional[str] = ..., action: _Optional[str] = ...) -> None: ...

class CheckPermissionResponse(_message.Message):
    __slots__ = ("has_permission",)
    HAS_PERMISSION_FIELD_NUMBER: _ClassVar[int]
    has_permission: bool
    def __init__(self, has_permission: bool = ...) -> None: ...

class CheckUserPermissionsRequest(_message.Message):
    __slots__ = ("user_id", "permissions")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    permissions: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, user_id: _Optional[str] = ..., permissions: _Optional[_Iterable[str]] = ...) -> None: ...

class CheckUserPermissionsResponse(_message.Message):
    __slots__ = ("permissions",)
    class PermissionsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: bool
        def __init__(self, key: _Optional[str] = ..., value: bool = ...) -> None: ...
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    permissions: _containers.ScalarMap[str, bool]
    def __init__(self, permissions: _Optional[_Mapping[str, bool]] = ...) -> None: ...

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
