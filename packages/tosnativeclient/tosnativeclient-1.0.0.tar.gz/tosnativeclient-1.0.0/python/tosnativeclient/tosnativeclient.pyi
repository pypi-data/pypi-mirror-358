from typing import List

from typing import Optional


class TosClient(object):
    region: str
    endpoint: str
    ak: str
    sk: str
    part_size: int
    max_retry_count: int
    max_prefetch_tasks: int

    def __init__(self, region: str, endpoint: str, ak: str = '', sk: str = '', part_size: int = 8388608,
                 max_retry_count: int = 3, max_prefetch_tasks: int = 3, directives: str = '', directory: str = '',
                 file_name_prefix: str = '', shared_prefetch_tasks: int = 20):
        ...

    def list_objects(self, bucket: str, prefix: str = '', max_keys: int = 1000, delimiter: str = '') -> ListStream:
        ...

    def head_object(self, bucket: str, key: str) -> TosObject:
        ...

    def get_object(self, bucket: str, key: str, etag: str, size: int) -> ReadStream:
        ...

    def put_object(self, bucket: str, key: str, storage_class: str = '') -> WriteStream:
        ...


class ListStream(object):
    bucket: str
    prefix: str
    delimiter: str
    max_keys: int

    def __iter__(self) -> ListStream: ...

    def __next__(self) -> ListObjectsResult: ...

    def close(self) -> None: ...


class ListObjectsResult(object):
    contents: List[TosObject]
    common_prefixes: List[str]


class TosObject(object):
    bucket: str
    key: str
    size: int
    etag: str


class ReadStream(object):
    bucket: str
    key: str
    size: int
    etag: str

    def read(self, offset: int, length: int) -> bytes:
        ...

    def close(self) -> None:
        ...


class WriteStream(object):
    bucket: str
    key: str
    storage_class: Optional[str]

    def write(self, data: bytes) -> int:
        ...

    def close(self) -> None:
        ...


class TosError(object):
    message: str
    status_code: Optional[int]
    ec: str
    request_id: str


class TosException(Exception):
    args: List[TosError]
