import datetime
from typing import Optional

from google.protobuf import timestamp

from dev_observer.api.types.repo_pb2 import GitHubRepository, GitMeta, GitAppInfo


def get_valid_repo_meta(repo: GitHubRepository) -> Optional[GitMeta]:
    if repo.properties is None:
        return None
    if repo.properties.meta is None:
        return None
    last_refresh = repo.properties.meta.last_refresh
    if last_refresh is None:
        return None
    ts = timestamp.to_datetime(last_refresh)
    return repo.properties.meta if ts + datetime.timedelta(hours=3) > datetime.datetime.now() else None


def get_valid_repo_app_info(repo: GitHubRepository) -> Optional[GitAppInfo]:
    if repo.properties is None:
        return None
    if repo.properties.app_info is None:
        return None
    last_refresh = repo.properties.app_info.last_refresh
    if last_refresh is None:
        return None
    ts = timestamp.to_datetime(last_refresh)
    return repo.properties.app_info if ts + datetime.timedelta(hours=3) > datetime.datetime.now() else None
