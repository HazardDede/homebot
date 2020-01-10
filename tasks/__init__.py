import glob
import os

import MarkdownPP
from argresolver.utils import modified_environ
from invoke import task


ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
CONFIGS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../configs'))
SOURCE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../homebot'))
TEST_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../tests'))


@task
def docs(ctx):
    """Pre-processes the docs (*.mdpp)."""
    def _process(file_path):
        modules = MarkdownPP.modules.keys()
        with open(file_path, 'r') as mdpp:
            # Output file takes filename from input file but has .md extension
            with open(os.path.splitext(file_path)[0] + '.md', 'w') as md:
                MarkdownPP.MarkdownPP(input=mdpp, output=md, modules=modules)

    for file_path in glob.iglob(os.path.join(ROOT_PATH, '**/*.mdpp'), recursive=True):
        _process(file_path)


@task
def flake8(ctx):
    """Runs flake8 linter against codebase."""
    ctx.run(
        "flake8 "
        "--exclude=.tox "
        "--max-line-length 120 "
        "--ignore=E704,E722,E731,F401,F811,W503 "
        "{}".format(SOURCE_PATH)
    )


@task
def pylint(ctx):
    """Runs pylint linter against codebase."""
    ctx.run("pylint {}".format(SOURCE_PATH))


@task
def mypy(ctx):
    """Runs mypy linter against codebase."""
    ctx.run("mypy --strict {}".format(SOURCE_PATH))


@task(flake8, pylint, mypy)
def lint(ctx):
    """Run all linters against codebase."""


@task
def pytest(ctx):
    """Runs pytest testing framework against codebase."""
    import sys
    sys.path.append(SOURCE_PATH)
    ctx.run(
        "pytest "
        "--verbose "
        "--color=yes "
        "--durations=10 "
        "--doctest-modules "
        "--cov={source} --cov-report html --cov-report term "
        "{test} {source}".format(source=SOURCE_PATH, test=TEST_PATH)
    )


@task
def doctest(ctx):
    """Runs codebase's doctests."""
    ctx.run(
        "pytest "
        "--verbose "
        "--color=yes "
        "--doctest-modules {}".format(SOURCE_PATH)
    )


@task
def test_configs(ctx):
    """Tests the configs using the homebot validator."""
    from homebot.__main__ import Runner
    context = {
        'HASS_TOKEN': 'hass_token',
        'HASS_URI': 'http://i-do-not-exist:8123',
        'SLACK_TOKEN': 'slack_token',
    }
    with modified_environ(**context):
        for file_path in glob.iglob(os.path.join(CONFIGS_PATH, '**/run.py'), recursive=True):
            Runner.validate(file_path)


@task(pytest, test_configs)
def test(ctx):
    """Runs all tests against codebase."""


@task(lint, test, docs)
def commit(ctx):
    """Runs the linter, test suite and creates the docs."""
