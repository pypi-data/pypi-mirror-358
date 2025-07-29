import io
import logging
import threading
from typing import Callable, Any

from tos.models2 import PutObjectOutput

log = logging.getLogger(__name__)


class PutObjectStream(object):
    def __init__(self, put_object: Callable[[io.BytesIO], PutObjectOutput]):
        self._put_object = put_object
        self._buffer = io.BytesIO()

    def write(self, data):
        self._buffer.write(data)

    def close(self):
        self._buffer.seek(0)
        _ = self._put_object(self._buffer)


class TosObjectWriter(io.BufferedIOBase):

    def __init__(self, bucket: str, key: str, put_object_stream: Any):
        if not bucket:
            raise ValueError('bucket is empty')
        self._bucket = bucket
        self._key = key
        self._put_object_stream = put_object_stream
        self._write_offset = 0
        self._closed = False
        self._lock = threading.Lock()

    @property
    def bucket(self) -> str:
        return self._bucket

    @property
    def key(self) -> str:
        return self._key

    def __enter__(self):
        self._write_offset = 0
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            try:
                log.info(f'Exception occurred before closing stream: {exc_type.__name__}: {exc_val}')
            except:
                pass
        else:
            self.close()

    def write(self, data) -> int:
        self._put_object_stream.write(data)
        self._write_offset += len(data)
        return len(data)

    def close(self) -> None:
        with self._lock:
            if self._closed:
                return
            self._closed = True
            self._put_object_stream.close()

    def tell(self) -> int:
        return self._write_offset

    def flush(self) -> None:
        pass

    def readable(self):
        return False

    def writable(self):
        return True

    def seekable(self):
        return False
