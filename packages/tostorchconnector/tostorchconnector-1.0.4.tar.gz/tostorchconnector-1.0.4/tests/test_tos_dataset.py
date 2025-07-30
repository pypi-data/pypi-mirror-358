import os
import unittest

from tostorchconnector import TosMapDataset, TosIterableDataset, TosCheckpoint
from tostorchconnector.tos_client import CredentialProvider, TosLogConfig


class TestTosDataSet(unittest.TestCase):

    def test_from_urls(self):
        region = os.getenv('TOS_REGION')
        endpoint = os.getenv('TOS_ENDPOINT')
        ak = os.getenv('TOS_ACCESS_KEY')
        sk = os.getenv('TOS_SECRET_KEY')
        bucket = 'tos-pytorch-connector'
        datasets = TosMapDataset.from_urls(iter([f'tos://{bucket}/key1', f'tos://{bucket}/key2', f'{bucket}/key3']),
                                           region=region, endpoint=endpoint, cred=CredentialProvider(ak, sk))

        for i in range(len(datasets)):
            print(datasets[i].bucket, datasets[i].key)

    def test_from_prefix(self):
        region = os.getenv('TOS_REGION')
        endpoint = os.getenv('TOS_ENDPOINT')
        ak = os.getenv('TOS_ACCESS_KEY')
        sk = os.getenv('TOS_SECRET_KEY')
        bucket = 'tos-pytorch-connector'
        datasets = TosMapDataset.from_prefix(f'tos://{bucket}/prefix', region=region,
                                             endpoint=endpoint, cred=CredentialProvider(ak, sk))
        for i in range(len(datasets)):
            item = datasets[i]
            print(item.bucket, item.key)
            if i == 1:
                item = datasets[i]
                data = item.read(100)
                print(data)
                print(len(data))

    def test_from_prefix_iter(self):
        region = os.getenv('TOS_REGION')
        endpoint = os.getenv('TOS_ENDPOINT')
        ak = os.getenv('TOS_ACCESS_KEY')
        sk = os.getenv('TOS_SECRET_KEY')
        bucket = 'tos-pytorch-connector'
        datasets = TosIterableDataset.from_prefix(f'tos://{bucket}/prefix', region=region,
                                                  endpoint=endpoint, cred=CredentialProvider(ak, sk))
        i = 0
        for dataset in datasets:
            print(dataset.bucket, dataset.key)
            if i == 1:
                data = dataset.read(100)
                print(data)
                print(len(data))
            i += 1

    def test_checkpoint(self):
        region = os.getenv('TOS_REGION')
        endpoint = os.getenv('TOS_ENDPOINT')
        ak = os.getenv('TOS_ACCESS_KEY')
        sk = os.getenv('TOS_SECRET_KEY')
        bucket = 'tos-pytorch-connector'
        checkpoint = TosCheckpoint(region, endpoint, cred=CredentialProvider(ak, sk), use_native_client=True)
        url = f'tos://{bucket}/key1'
        with checkpoint.writer(url) as writer:
            writer.write(b'hello world')
            writer.write(b'hi world')

        reader = checkpoint.reader(url)
        print(reader.read())


if __name__ == '__main__':
    unittest.main()
