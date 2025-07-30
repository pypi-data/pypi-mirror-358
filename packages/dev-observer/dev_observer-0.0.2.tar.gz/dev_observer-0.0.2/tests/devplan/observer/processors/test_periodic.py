import unittest
from datetime import timedelta

from dev_observer.analysis.stub import StubAnalysisProvider
from dev_observer.api.types.config_pb2 import GlobalConfig, AnalysisConfig
from dev_observer.api.types.observations_pb2 import Analyzer, ObservationKey
from dev_observer.api.types.repo_pb2 import GitHubRepository
from dev_observer.observations.memory import MemoryObservationsProvider
from dev_observer.processors.periodic import PeriodicProcessor
from dev_observer.processors.repos import ReposProcessor
from dev_observer.prompts.stub import StubPromptsProvider
from dev_observer.repository.copying import CopyingGitRepositoryProvider
from dev_observer.storage.memory import MemoryStorageProvider
from dev_observer.tokenizer.stub import StubTokenizerProvider
from dev_observer.util import MockClock


class TestPeriodicProcessor(unittest.IsolatedAsyncioTestCase):
    async def test_list_files(self):
        clock = MockClock()
        storage = MemoryStorageProvider(clock)
        await storage.set_global_config(GlobalConfig(analysis=AnalysisConfig(repo_analyzers=[
            Analyzer(name="test", prompt_prefix="test_pref", file_name="test.md"),
        ])))
        analysis = StubAnalysisProvider()
        repos = CopyingGitRepositoryProvider(shallow=True)
        prompts = StubPromptsProvider()
        observations = MemoryObservationsProvider()
        repos_processor = ReposProcessor(
            analysis=analysis,
            repository=repos,
            prompts=prompts,
            observations=observations,
            tokenizer=StubTokenizerProvider(),
        )
        p = PeriodicProcessor(storage=storage, repos_processor=repos_processor, clock=clock)
        self.assertIsNone(await p.process_next())
        await storage.add_github_repo(GitHubRepository(
            name="test1", id="r1", full_name="devplan/test1", url="https://github.com/devplan/test1",
        ))
        items = await storage.get_processing_items()
        self.assertEqual(1, len(items))
        item1_key = items[0].key
        self.assertEqual("r1", items[0].key.github_repo_id)
        await storage.add_github_repo(GitHubRepository(
            name="test2", id="r2", full_name="devplan/test2", url="https://github.com/devplan/test2",
        ))
        items = await storage.get_processing_items()
        self.assertEqual(2, len(items))
        self.assertTrue(items[0].HasField("next_processing"))
        self.assertTrue(items[1].HasField("next_processing"))

        await storage.set_next_processing_time(items[0].key, None)
        await storage.set_next_processing_time(items[1].key, None)

        items = await storage.get_processing_items()
        self.assertEqual(2, len(items))
        self.assertFalse(items[0].HasField("next_processing"))
        self.assertFalse(items[1].HasField("next_processing"))

        self.assertIsNone(await p.process_next())
        await storage.set_next_processing_time(item1_key, clock.now() + timedelta(seconds=1))
        self.assertIsNone(await p.process_next())
        clock.bump(timedelta(minutes=5))
        item = await p.process_next()
        self.assertIsNotNone(item)
        self.assertEqual("r1", item.key.github_repo_id)

        self.assertIsNone(await p.process_next())

        items = await storage.get_processing_items()
        self.assertEqual(2, len(items))
        self.assertFalse(items[0].HasField("next_processing"))
        self.assertFalse(items[1].HasField("next_processing"))

        obs = await observations.list("repos")
        self.assertEqual(1, len(obs))
        self.assertEqual(
            ObservationKey(kind="repos", name="test.md", key="devplan/test1/test.md"),
            obs[0],
        )
