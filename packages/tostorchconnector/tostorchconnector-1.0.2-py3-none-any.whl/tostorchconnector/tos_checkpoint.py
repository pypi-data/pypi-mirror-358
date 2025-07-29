import logging
from typing import Optional

from . import TosObjectReader, TosObjectWriter
from .tos_client import CredentialProvider, TosClientConfig, TosClient, TosLogConfig
from .tos_common import parse_tos_url

log = logging.getLogger(__name__)


class TosCheckpoint(object):
    def __init__(self, region: str,
                 endpoint: Optional[str] = None,
                 cred: Optional[CredentialProvider] = None,
                 client_conf: Optional[TosClientConfig] = None,
                 log_conf: Optional[TosLogConfig] = None, use_native_client=True):
        self._client = None
        self._native_client = None
        self._region = region
        self._endpoint = endpoint
        self._cred = cred
        self._client_conf = client_conf
        self._log_conf = log_conf
        self._use_native_client = use_native_client

    def reader(self, url: str) -> TosObjectReader:
        bucket, key = parse_tos_url(url)
        return self._get_tos_client().get_object(bucket, key)

    def writer(self, url: str) -> TosObjectWriter:
        bucket, key = parse_tos_url(url)
        return self._get_tos_client().put_object(bucket, key)

    def _get_tos_client(self):
        if self._client is None:
            self._client = TosClient(self._region, self._endpoint, self._cred, self._client_conf, self._log_conf,
                                     self._use_native_client)
            log.info('TosIterableDataset init tos client succeed')
        return self._client
