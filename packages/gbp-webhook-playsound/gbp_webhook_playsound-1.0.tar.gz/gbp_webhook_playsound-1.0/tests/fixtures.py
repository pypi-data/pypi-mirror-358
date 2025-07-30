# pylint: disable=missing-docstring,redefined-outer-name
import os
import subprocess
from collections.abc import Mapping, MutableMapping
from unittest import mock

from unittest_fixtures import FixtureContext, Fixtures, fixture


@fixture()
def environ(
    _fixtures: Fixtures, *, environ: Mapping[str, str] | None = None
) -> FixtureContext[MutableMapping[str, str]]:
    environ = environ or {}

    with mock.patch.dict(os.environ, clear=True):
        os.environ.update(environ)
        yield os.environ


@fixture()
def popen(_fixtures: Fixtures) -> FixtureContext[mock.Mock]:
    with mock.patch.object(subprocess, "Popen") as mock_popen:
        yield mock_popen
