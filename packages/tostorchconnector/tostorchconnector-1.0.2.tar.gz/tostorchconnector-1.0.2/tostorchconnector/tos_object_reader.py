import io
import logging
from functools import cached_property
from os import SEEK_SET, SEEK_CUR, SEEK_END
from typing import Optional, Callable, Any

from tos.models2 import GetObjectOutput
from tosnativeclient.tosnativeclient import ReadStream

from .tos_object_meta import TosObjectMeta

log = logging.getLogger(__name__)


class TosObjectReader(io.BufferedIOBase):

    def __init__(self, bucket: str, key: str,
                 get_object_meta: Optional[Callable[[], TosObjectMeta]],
                 get_object_stream: Callable[[str, int], Any]):
        if not bucket:
            raise ValueError('bucket is empty')
        self._bucket = bucket
        self._key = key
        self._get_object_meta = get_object_meta
        self._get_object_stream = get_object_stream
        self._object_stream: Optional[Any] = None
        self._object_stream_offset = 0
        self._total_size: Optional[int] = None
        self._read_offset = 0
        self._buffer = io.BytesIO()

    @property
    def bucket(self) -> str:
        return self._bucket

    @property
    def key(self) -> str:
        return self._key

    def read(self, size: Optional[int] = None) -> Optional[bytes]:
        if self._is_read_to_end():
            return b''

        self._trigger_prefetch()
        current_read_offset = self._read_offset
        if size is None or size < 0:
            # means read all
            self._buffer.seek(0, SEEK_END)
            if isinstance(self._object_stream, ReadStream):
                try:
                    chunk_size = 1 * 1024 * 1024
                    while 1:
                        chunk = self._object_stream.read(self._object_stream_offset, chunk_size)
                        if not chunk:
                            break
                        self._object_stream_offset += len(chunk)
                        self._buffer.write(chunk)
                finally:
                    self._object_stream.close()
            elif isinstance(self._object_stream, GetObjectOutput):
                for chunk in self._object_stream:
                    self._buffer.write(chunk)

            self._total_size = self._buffer.tell()
        else:
            self.seek(size, SEEK_CUR)

        self._buffer.seek(current_read_offset)
        data = self._buffer.read(size)
        self._read_offset = self._buffer.tell()
        return data

    def readinto(self, buf) -> Optional[int]:
        size = len(buf)
        if self._is_read_to_end() or size == 0:
            return 0

        self._trigger_prefetch()
        current_read_offset = self._read_offset
        self.seek(size, SEEK_CUR)
        self._buffer.seek(current_read_offset)
        readed = self._buffer.readinto(buf)
        self._read_offset = self._buffer.tell()
        return readed

    def seek(self, offset: int, whence: int = SEEK_SET) -> int:
        if whence == SEEK_END:
            if offset >= 0:
                self._read_offset = self._get_total_size()
                return self._read_offset
            # offset is negative
            offset += self._get_total_size()
        elif whence == SEEK_CUR:
            if self._is_read_to_end() and offset >= 0:
                return self._read_offset
            offset += self._read_offset
        elif whence == SEEK_SET:
            pass
        else:
            raise ValueError('invalid whence')

        if offset < 0:
            raise ValueError(f'invalid seek offset {offset}')

        if offset > self._buffer_size():
            self._prefetch_to_offset(offset)

        self._read_offset = self._buffer.seek(offset)
        return self._read_offset

    def tell(self) -> int:
        return self._read_offset

    def readable(self):
        return True

    def writable(self):
        return False

    def seekable(self):
        return True

    @cached_property
    def _object_meta(self) -> TosObjectMeta:
        return self._get_object_meta()

    def _trigger_prefetch(self) -> None:
        if self._object_stream is None:
            object_meta = self._object_meta
            self._object_stream = self._get_object_stream(object_meta.etag, object_meta.size)
            self._object_stream_offset = 0

    def _is_read_to_end(self) -> bool:
        if self._total_size is None:
            return False
        return self._read_offset == self._total_size

    def _get_total_size(self) -> int:
        if self._total_size is None:
            self._total_size = self._object_meta.size
        return self._total_size

    def _prefetch_to_offset(self, offset: int) -> None:
        self._trigger_prefetch()
        size = self._buffer.seek(0, SEEK_END)
        if isinstance(self._object_stream, ReadStream):
            try:
                chunk_size = 1 * 1024 * 1024
                while offset > size:
                    chunk = self._object_stream.read(self._object_stream_offset, chunk_size)
                    if not chunk:
                        break
                    size += self._buffer.write(chunk)
                    self._object_stream_offset += len(chunk)
                self._total_size = self._buffer.tell()
            finally:
                self._object_stream.close()
        else:
            try:
                while offset > size:
                    size += self._buffer.write(next(self._object_stream))
            except StopIteration:
                self._total_size = self._buffer.tell()

    def _buffer_size(self) -> int:
        cur_pos = self._buffer.tell()
        self._buffer.seek(0, SEEK_END)
        buffer_size = self._buffer.tell()
        self._buffer.seek(cur_pos)
        return buffer_size
