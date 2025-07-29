import numcodecs.compat
import numcodecs.registry
import numpy as np
import zarr.registry
from numcodecs.abc import Codec


def test_registry():
    aa_cls = zarr.registry.get_codec_class("any-numcodecs.array-array")
    assert aa_cls.__name__ == "AnyNumcodecsArrayArrayCodec"
    assert aa_cls.__module__ == "zarr_any_numcodecs"

    ab_cls = zarr.registry.get_codec_class("any-numcodecs.array-bytes")
    assert ab_cls.__name__ == "AnyNumcodecsArrayBytesCodec"
    assert ab_cls.__module__ == "zarr_any_numcodecs"

    bb_cls = zarr.registry.get_codec_class("any-numcodecs.bytes-bytes")
    assert bb_cls.__name__ == "AnyNumcodecsBytesBytesCodec"
    assert bb_cls.__module__ == "zarr_any_numcodecs"


def test_from_config():
    data = np.linspace(0, 100, 101)
    store = zarr.storage.MemoryStore()

    zarr.save_array(
        store,
        data,
        codecs=[
            dict(
                name="any-numcodecs.array-array",
                configuration=dict(id="bitround", keepbits=6),
            ),
            dict(name="any-numcodecs.array-bytes", configuration=dict(id="crc32")),
            dict(
                name="any-numcodecs.bytes-bytes", configuration=dict(id="zstd", level=3)
            ),
        ],
    )

    a = zarr.open_array(store)

    assert np.all(np.asarray(a) == data)


def test_weird_bytes():
    data = np.linspace(0, 100, 101)

    for codec in ["as-bytes-u8", "as-bytes"]:
        store = zarr.storage.MemoryStore()

        zarr.save_array(
            store,
            data,
            codecs=[
                dict(name="any-numcodecs.array-bytes", configuration=dict(id=codec)),
                dict(
                    name="any-numcodecs.bytes-bytes",
                    configuration=dict(id="as-bytes-u8"),
                ),
                dict(
                    name="any-numcodecs.bytes-bytes",
                    configuration=dict(id="as-bytes-u8"),
                ),
                dict(
                    name="any-numcodecs.bytes-bytes", configuration=dict(id="as-bytes")
                ),
                dict(
                    name="any-numcodecs.bytes-bytes", configuration=dict(id="as-bytes")
                ),
                dict(
                    name="any-numcodecs.bytes-bytes", configuration=dict(id="as-bytes")
                ),
            ],
        )

        a = zarr.open_array(store)

        assert np.all(np.asarray(a) == data)


def test_chunked_encode_decode():
    data = np.array([1.0, 2.0, 3.0])

    store = zarr.storage.MemoryStore()
    zarr.save_array(
        store,
        data,
        codecs=[
            dict(
                name="any-numcodecs.array-array",
                configuration=dict(id="check-is-chunked"),
            ),
            dict(
                name="any-numcodecs.array-bytes",
                configuration=dict(id="as-bytes"),
            ),
        ],
    )
    a = zarr.open_array(store)
    assert np.all(np.asarray(a) == data)

    store = zarr.storage.MemoryStore()
    zarr.save_array(
        store,
        data,
        codecs=[
            dict(
                name="any-numcodecs.array-bytes",
                configuration=dict(
                    id="combinators.stack",
                    codecs=[dict(id="check-is-chunked"), dict(id="as-bytes")],
                ),
            ),
        ],
    )
    a = zarr.open_array(store)
    assert np.all(np.asarray(a) == data)


class AsBytesU8Codec(Codec):
    codec_id = "as-bytes-u8"

    def encode(self, buf):
        return numcodecs.compat.ensure_ndarray_like(buf).view(np.uint8)

    def decode(self, buf, out=None):
        decoded = numcodecs.compat.ensure_ndarray_like(buf)
        if out is not None:
            decoded = decoded.view(out.dtype).reshape(out.shape)
        return numcodecs.compat.ndarray_copy(decoded, out)


class AsBytesCodec(Codec):
    codec_id = "as-bytes"

    def encode(self, buf):
        return np.asarray(numcodecs.compat.ensure_ndarray_like(buf)).tobytes()

    def decode(self, buf, out=None):
        decoded = numcodecs.compat.ensure_ndarray_like(buf)
        if out is not None:
            decoded = decoded.view(out.dtype).reshape(out.shape)
        return numcodecs.compat.ndarray_copy(decoded, out)


class CheckChunkedCodec(Codec):
    __slots__ = ()

    codec_id = "check-is-chunked"

    def encode(self, buf):
        assert getattr(buf, "chunked", False)
        return buf

    def decode(self, buf, out=None):
        assert getattr(buf, "chunked", False) is False
        assert (out is None) or getattr(out, "chunked", False)
        return numcodecs.compat.ndarray_copy(buf, out)


numcodecs.registry.register_codec(AsBytesCodec)
numcodecs.registry.register_codec(AsBytesU8Codec)
numcodecs.registry.register_codec(CheckChunkedCodec)
