from make87_messages.core import header_pb2 as _header_pb2
from make87_messages.image.uncompressed import image_rgb888_pb2 as _image_rgb888_pb2
from make87_messages.image.uncompressed import image_rgba8888_pb2 as _image_rgba8888_pb2
from make87_messages.image.uncompressed import image_yuv420_pb2 as _image_yuv420_pb2
from make87_messages.image.uncompressed import image_yuv422_pb2 as _image_yuv422_pb2
from make87_messages.image.uncompressed import image_yuv444_pb2 as _image_yuv444_pb2
from make87_messages.image.uncompressed import image_nv12_pb2 as _image_nv12_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ImageRGBAny(_message.Message):
    __slots__ = ("header", "rgb888", "rgba8888")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    RGB888_FIELD_NUMBER: _ClassVar[int]
    RGBA8888_FIELD_NUMBER: _ClassVar[int]
    header: _header_pb2.Header
    rgb888: _image_rgb888_pb2.ImageRGB888
    rgba8888: _image_rgba8888_pb2.ImageRGBA8888
    def __init__(self, header: _Optional[_Union[_header_pb2.Header, _Mapping]] = ..., rgb888: _Optional[_Union[_image_rgb888_pb2.ImageRGB888, _Mapping]] = ..., rgba8888: _Optional[_Union[_image_rgba8888_pb2.ImageRGBA8888, _Mapping]] = ...) -> None: ...

class ImageYUVAny(_message.Message):
    __slots__ = ("header", "yuv420", "yuv422", "yuv444", "nv12")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    YUV420_FIELD_NUMBER: _ClassVar[int]
    YUV422_FIELD_NUMBER: _ClassVar[int]
    YUV444_FIELD_NUMBER: _ClassVar[int]
    NV12_FIELD_NUMBER: _ClassVar[int]
    header: _header_pb2.Header
    yuv420: _image_yuv420_pb2.ImageYUV420
    yuv422: _image_yuv422_pb2.ImageYUV422
    yuv444: _image_yuv444_pb2.ImageYUV444
    nv12: _image_nv12_pb2.ImageNV12
    def __init__(self, header: _Optional[_Union[_header_pb2.Header, _Mapping]] = ..., yuv420: _Optional[_Union[_image_yuv420_pb2.ImageYUV420, _Mapping]] = ..., yuv422: _Optional[_Union[_image_yuv422_pb2.ImageYUV422, _Mapping]] = ..., yuv444: _Optional[_Union[_image_yuv444_pb2.ImageYUV444, _Mapping]] = ..., nv12: _Optional[_Union[_image_nv12_pb2.ImageNV12, _Mapping]] = ...) -> None: ...

class ImageRawAny(_message.Message):
    __slots__ = ("header", "rgb888", "rgba8888", "yuv420", "yuv422", "yuv444", "nv12")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    RGB888_FIELD_NUMBER: _ClassVar[int]
    RGBA8888_FIELD_NUMBER: _ClassVar[int]
    YUV420_FIELD_NUMBER: _ClassVar[int]
    YUV422_FIELD_NUMBER: _ClassVar[int]
    YUV444_FIELD_NUMBER: _ClassVar[int]
    NV12_FIELD_NUMBER: _ClassVar[int]
    header: _header_pb2.Header
    rgb888: _image_rgb888_pb2.ImageRGB888
    rgba8888: _image_rgba8888_pb2.ImageRGBA8888
    yuv420: _image_yuv420_pb2.ImageYUV420
    yuv422: _image_yuv422_pb2.ImageYUV422
    yuv444: _image_yuv444_pb2.ImageYUV444
    nv12: _image_nv12_pb2.ImageNV12
    def __init__(self, header: _Optional[_Union[_header_pb2.Header, _Mapping]] = ..., rgb888: _Optional[_Union[_image_rgb888_pb2.ImageRGB888, _Mapping]] = ..., rgba8888: _Optional[_Union[_image_rgba8888_pb2.ImageRGBA8888, _Mapping]] = ..., yuv420: _Optional[_Union[_image_yuv420_pb2.ImageYUV420, _Mapping]] = ..., yuv422: _Optional[_Union[_image_yuv422_pb2.ImageYUV422, _Mapping]] = ..., yuv444: _Optional[_Union[_image_yuv444_pb2.ImageYUV444, _Mapping]] = ..., nv12: _Optional[_Union[_image_nv12_pb2.ImageNV12, _Mapping]] = ...) -> None: ...
