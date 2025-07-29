import os

from decouple import RepositoryEmpty


class RepositorySecret(RepositoryEmpty):
    def __init__(self, source):  # noqa
        self.data = {}

        if not os.path.isdir(source):
            return

        ls = os.listdir(source)

        for file in ls:
            path = os.path.join(source, file)

            if os.path.isdir(path):
                continue

            with open(path, encoding="utf-8") as f:
                self.data[file.upper()] = f.read()

    def __contains__(self, key):
        return key in os.environ or key in self.data

    def __getitem__(self, key):
        return self.data[key]


class CompositeRepository:
    def __init__(self, *repositories):
        self.repositories = repositories

    def __contains__(self, key):
        return any(key in repo for repo in self.repositories)

    def __getitem__(self, key):
        for repo in self.repositories:
            if key in repo:
                return repo[key]
        raise KeyError(key)
