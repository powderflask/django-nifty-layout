from invoke import task
import tasks.docs as docs_task

get_args = lambda c, section: (c, c.config.clean[section].cleans, c.config.clean[section].paths)


def clean_files(c, cleans: str, paths: list[str]):
    cmd = f"rm -fr {' '.join(paths)}"
    print(f"Cleaning {cleans} with:\033[0m\n  \033[35m{cmd}\033[0m")
    c.run(cmd)
    print(f"\033[32mDone!\033[0m")


@task(name="build")
def clean_build(c):
    """Remove build artifacts"""
    clean_files(*get_args(c, "build"))


@task(name="cache")
def clean_cache(c):
    """Remove Python file artifacts"""
    clean_files(*get_args(c, "cache"))


@task(name="test")
def clean_test(c):
    """Remove test and coverage artifacts"""
    clean_files(*get_args(c, "test"))


@task(name="tox")
def clean_tox(c):
    """Remove tox artifacts"""
    clean_files(*get_args(c, "tox"))


@task(name="all")
def clean_all(c):
    """Remove all build, test, coverage, tox, and Python artifacts"""
    cleaners = [clean_tox, clean_build, clean_cache, clean_test]
    if c.config.docs.enabled:
        cleaners.append(docs_task.clean)
    for cleaner in cleaners:
        cleaner(c)
    print("\n\033[32mAll Cleaned up!\033[0m")
