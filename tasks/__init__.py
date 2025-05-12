from invoke import Collection

from . import clean, deps, docs, pypi, tox, act

namespace = Collection(
    clean, deps, docs, tox, pypi, act
)