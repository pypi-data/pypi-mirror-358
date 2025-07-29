"""
Adapt any [`numcodecs.abc.Codec`][numcodecs.abc.Codec] into a [`zarr.abc.codec.Codec`][zarr.abc.codec].

The adapted codecs can be configured as follows (here for an array-to-array
adapter over a codec with id `"my-codec"`):

```json
{
    "name": "any-numcodecs.array-array",
    "configuration": {
        "id": "my-codec",
        ...
    }
}
```
"""

__all__ = [
    "AnyNumcodecsArrayArrayCodec",
    "AnyNumcodecsArrayBytesCodec",
    "AnyNumcodecsBytesBytesCodec",
]

import asyncio
from dataclasses import dataclass
from typing import Self, ClassVar

import numcodecs.registry
import numpy as np
import zarr.registry
from numcodecs.abc import Codec
from zarr.abc.codec import ArrayArrayCodec, ArrayBytesCodec, BytesBytesCodec, BaseCodec
from zarr.core.array_spec import ArraySpec
from zarr.core.buffer import NDBuffer, Buffer
from zarr.core.common import JSON, parse_named_configuration


@dataclass(frozen=True, slots=True)
class _AnyNumcodecsCodec(BaseCodec):
    codec_name: ClassVar[str]
    codec: Codec

    is_fixed_size: ClassVar[bool] = False  # type: ignore

    def compute_encoded_size(
        self, input_byte_length: int, chunk_spec: ArraySpec
    ) -> int:
        raise NotImplementedError

    @classmethod
    def from_dict(cls, data: dict[str, JSON]) -> Self:
        _codec_name, codec_config = parse_named_configuration(data, cls.codec_name)
        return cls(numcodecs.registry.get_codec(codec_config))

    def to_dict(self) -> dict[str, JSON]:
        return dict(
            name=self.codec_name,
            configuration=self.codec.get_config(),
        )


class AnyNumcodecsArrayArrayCodec(_AnyNumcodecsCodec, ArrayArrayCodec):
    """
    Adapt a [`numcodecs.abc.Codec`][numcodecs.abc.Codec] into a [`zarr.abc.codec.ArrayArrayCodec`][zarr.abc.codec.ArrayArrayCodec].

    The inner codec must transform array shapes and dtypes deterministically
    and independent of the array's content, i.e. encoding two arrays with
    different contents but the same shape and dtype must produce two encoded
    arrays with matching dtype and shape (though their contents may differ).

    Parameters
    ----------
    codec : Codec
        The codec to wrap.
    """

    __slots__ = ()

    codec_name: ClassVar[str] = "any-numcodecs.array-array"

    def resolve_metadata(self, chunk_spec: ArraySpec) -> ArraySpec:
        dummy_data = chunk_spec.prototype.nd_buffer.create(
            shape=chunk_spec.shape, dtype=chunk_spec.dtype, fill_value=1
        )
        encoded = chunk_spec.prototype.nd_buffer.from_ndarray_like(
            self.codec.encode(_ChunkedNdArray(dummy_data.as_ndarray_like()))
        )
        return ArraySpec(
            encoded.shape, encoded.dtype, 0, chunk_spec.config, chunk_spec.prototype
        )

    async def _encode_single(
        self, chunk_array: NDBuffer, chunk_spec: ArraySpec
    ) -> NDBuffer:
        chunk_ndarray = chunk_array.as_ndarray_like()
        out = await asyncio.to_thread(self.codec.encode, _ChunkedNdArray(chunk_ndarray))
        return chunk_spec.prototype.nd_buffer.from_ndarray_like(out)

    async def _decode_single(
        self, chunk_array: NDBuffer, chunk_spec: ArraySpec
    ) -> NDBuffer:
        chunk_ndarray = chunk_array.as_ndarray_like()
        empty = chunk_spec.prototype.nd_buffer.create(
            shape=chunk_spec.shape, dtype=chunk_spec.dtype, fill_value=0
        ).as_ndarray_like()
        out = await asyncio.to_thread(
            self.codec.decode, chunk_ndarray, out=_ChunkedNdArray(empty)
        )
        decoded = chunk_spec.prototype.nd_buffer.from_ndarray_like(out).as_numpy_array()
        return chunk_spec.prototype.nd_buffer.from_ndarray_like(
            decoded.view(np.ndarray).view(chunk_spec.dtype).reshape(chunk_spec.shape)  # type: ignore
        )


class AnyNumcodecsArrayBytesCodec(_AnyNumcodecsCodec, ArrayBytesCodec):
    """
    Adapt a [`numcodecs.abc.Codec`][numcodecs.abc.Codec] into a [`zarr.abc.codec.ArrayBytesCodec`][zarr.abc.codec.ArrayBytesCodec].

    The inner codec must encode arrays into bytes-like outputs, e.g. 1d arrays
    of a byte-like dtype.

    Parameters
    ----------
    codec : Codec
        The codec to wrap.
    """

    __slots__ = ()

    codec_name: ClassVar[str] = "any-numcodecs.array-bytes"

    async def _encode_single(
        self, chunk_array: NDBuffer, chunk_spec: ArraySpec
    ) -> Buffer:
        chunk_ndarray = chunk_array.as_ndarray_like()
        out = await asyncio.to_thread(self.codec.encode, _ChunkedNdArray(chunk_ndarray))
        return chunk_spec.prototype.buffer.from_bytes(out)

    async def _decode_single(
        self, chunk_array: Buffer, chunk_spec: ArraySpec
    ) -> NDBuffer:
        empty = chunk_spec.prototype.nd_buffer.create(
            shape=chunk_spec.shape, dtype=chunk_spec.dtype, fill_value=0
        ).as_ndarray_like()
        out = await asyncio.to_thread(
            self.codec.decode, chunk_array.as_array_like(), out=_ChunkedNdArray(empty)
        )
        decoded = chunk_spec.prototype.nd_buffer.from_ndarray_like(out).as_numpy_array()
        return chunk_spec.prototype.nd_buffer.from_ndarray_like(
            decoded.view(np.ndarray).view(chunk_spec.dtype).reshape(chunk_spec.shape)  # type: ignore
        )


class AnyNumcodecsBytesBytesCodec(_AnyNumcodecsCodec, BytesBytesCodec):
    """
    Adapt a [`numcodecs.abc.Codec`][numcodecs.abc.Codec] into a [`zarr.abc.codec.BytesBytesCodec`][zarr.abc.codec.BytesBytesCodec].

    The inner codec must encode byte-like inputs into bytes-like outputs, e.g.
    1d arrays of a byte-like dtype.

    Parameters
    ----------
    codec : Codec
        The codec to wrap.
    """

    __slots__ = ()

    codec_name: ClassVar[str] = "any-numcodecs.bytes-bytes"

    async def _encode_single(
        self, chunk_array: Buffer, chunk_spec: ArraySpec
    ) -> Buffer:
        out = await asyncio.to_thread(self.codec.encode, chunk_array.as_array_like())
        return chunk_spec.prototype.buffer.from_bytes(out)

    async def _decode_single(
        self, chunk_array: Buffer, chunk_spec: ArraySpec
    ) -> Buffer:
        out = await asyncio.to_thread(self.codec.decode, chunk_array.as_array_like())
        return chunk_spec.prototype.buffer.from_bytes(out)


zarr.registry.register_codec(
    AnyNumcodecsArrayArrayCodec.codec_name, AnyNumcodecsArrayArrayCodec
)
zarr.registry.register_codec(
    AnyNumcodecsArrayBytesCodec.codec_name, AnyNumcodecsArrayBytesCodec
)
zarr.registry.register_codec(
    AnyNumcodecsBytesBytesCodec.codec_name, AnyNumcodecsBytesBytesCodec
)


class _ChunkedNdArray(np.ndarray):
    __slots__ = ()

    def __new__(cls, array):
        return np.asarray(array).view(cls)

    @property
    def chunked(self) -> bool:
        return True
