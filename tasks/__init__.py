import os

from invoke import task


SOURCE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../homebot'))
TEST_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../tests'))


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
    pass


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


@task(pytest)
def test(ctx):
    """Runs all tests against codebase."""
    pass
