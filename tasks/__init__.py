from invoke import Collection

from . import act, clean, deps, docs, pypi, tox

namespace = Collection(clean, deps, docs, tox, pypi, act)
