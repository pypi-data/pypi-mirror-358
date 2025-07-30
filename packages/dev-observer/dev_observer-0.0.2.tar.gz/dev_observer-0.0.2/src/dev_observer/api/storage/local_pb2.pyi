from dev_observer.api.types import processing_pb2 as _processing_pb2
from dev_observer.api.types import repo_pb2 as _repo_pb2
from dev_observer.api.types import config_pb2 as _config_pb2
from dev_observer.api.types import sites_pb2 as _sites_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LocalStorageData(_message.Message):
    __slots__ = ("github_repos", "processing_items", "global_config", "web_sites")
    GITHUB_REPOS_FIELD_NUMBER: _ClassVar[int]
    PROCESSING_ITEMS_FIELD_NUMBER: _ClassVar[int]
    GLOBAL_CONFIG_FIELD_NUMBER: _ClassVar[int]
    WEB_SITES_FIELD_NUMBER: _ClassVar[int]
    github_repos: _containers.RepeatedCompositeFieldContainer[_repo_pb2.GitHubRepository]
    processing_items: _containers.RepeatedCompositeFieldContainer[_processing_pb2.ProcessingItem]
    global_config: _config_pb2.GlobalConfig
    web_sites: _containers.RepeatedCompositeFieldContainer[_sites_pb2.WebSite]
    def __init__(self, github_repos: _Optional[_Iterable[_Union[_repo_pb2.GitHubRepository, _Mapping]]] = ..., processing_items: _Optional[_Iterable[_Union[_processing_pb2.ProcessingItem, _Mapping]]] = ..., global_config: _Optional[_Union[_config_pb2.GlobalConfig, _Mapping]] = ..., web_sites: _Optional[_Iterable[_Union[_sites_pb2.WebSite, _Mapping]]] = ...) -> None: ...
