import dataclasses
from typing import List

from dev_observer.observations.provider import ObservationsProvider
from dev_observer.processors.periodic import PeriodicProcessor
from dev_observer.processors.repos import ReposProcessor
from dev_observer.storage.provider import StorageProvider
from dev_observer.users.provider import UsersProvider


@dataclasses.dataclass
class ServerEnv:
    observations: ObservationsProvider
    storage: StorageProvider
    repos_processor: ReposProcessor
    periodic_processor: PeriodicProcessor
    users: UsersProvider
    api_keys: List[str]
