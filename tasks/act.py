from pathlib import Path
from invoke import task

PROJECT_ROOT = Path(__file__).absolute().parent.parent

def get_runner_args(c) -> list[str]:
    args = []
    for platform, runner in c.config.act.runners.items():
        args.extend(("-P", f"{platform}={runner}"))
    return args


@task(name="run", default=True)
def run_act(c, job_id=None, args_str = None):
    """Run github actions locally with `act` (requires act installation and docker to be running)"""
    args_str = args_str or ""
    args = [
        "act",
        "-C",
        str(PROJECT_ROOT),
        "--artifact-server-path",
        f"{PROJECT_ROOT}/.artifacts",
        *get_runner_args(c),
        *args_str.split(" "),
    ]
    if job_id:
        args.extend(("-j", str(job_id)))
    c.run(" ".join(args), pty=True)  # pty=True (pseudoterminal) keeps ANSI colours
