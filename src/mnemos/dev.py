from __future__ import annotations

import subprocess
import sys


def _run(*args: str) -> None:
    completed = subprocess.run(
        [sys.executable, "-m", *args],
        check=False,
        capture_output=True,
        text=True,
    )

    print(" ".join(args))

    for stream in (completed.stdout, completed.stderr):
        for line in stream.splitlines():
            print(f"  {line}")

    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def _ruff_check(*args: str) -> None:
    _run("ruff", "check", *args, ".")


def lint() -> None:
    _ruff_check()


def format() -> None:
    _ruff_check("--fix")
    _run("ruff", "format", ".")


def typecheck() -> None:
    _run("ty", "check")


def check() -> None:
    lint()
    _run("ruff", "format", "--check", ".")
    typecheck()
    test()


def test() -> None:
    _run("pytest")
