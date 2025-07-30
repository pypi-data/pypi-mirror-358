import os.path
import subprocess

from dev_observer.repository.types import ObservedRepo
from dev_observer.repository.parser import parse_github_url
from dev_observer.repository.provider import GitRepositoryProvider, RepositoryInfo


class CopyingGitRepositoryProvider(GitRepositoryProvider):
    _shallow: bool

    def __init__(self, shallow: bool = False):
        self._shallow = shallow


    async def get_repo(self, repo: ObservedRepo) -> RepositoryInfo:
        parsed = parse_github_url(repo.url)
        return RepositoryInfo(
            owner=parsed.owner,
            name=parsed.name,
            clone_url=repo.url,
            # TODO: collect actual size.
            size_kb=500,
        )

    async def clone(self, repo: ObservedRepo, info: RepositoryInfo, dest: str):
        repo_root = _get_git_root()
        if self._shallow:
            subprocess.run(
                ["cp", "-r", os.path.join(repo_root, ".git"), os.path.join(dest, ".git")],
                capture_output=True,
                text=True,
                check=False
            )
            result = subprocess.run(
                ["cp", os.path.join(repo_root, "README.md"), dest],
                capture_output=True,
                text=True,
                check=False
            )
        else:
            result = subprocess.run(
                ["cp", "-r", repo_root, dest],
                capture_output=True,
                text=True,
                check=False
            )

        if result.returncode != 0:
            raise RuntimeError(f"Failed to copy repository: {result.stderr}")


def _get_git_root() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True
    )
    return result.stdout.strip()
