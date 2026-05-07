from __future__ import annotations

import argparse
import asyncio
import logging
from collections.abc import Sequence

from mnemos import __version__
from mnemos.app.bootstrap import run
from mnemos.app.errors import ConfigError

LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"
LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mnemos",
        description="Run the Mnemos Discord bot.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--log-level",
        choices=LOG_LEVELS,
        default="INFO",
        help="Minimum log level to print.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    configure_logging(args.log_level)

    try:
        asyncio.run(run())
    except ConfigError as exc:
        logging.getLogger("mnemos").error("Configuration error: %s", exc)
        raise SystemExit(2) from exc
    except KeyboardInterrupt:
        logging.getLogger("mnemos").info("Shutdown requested")


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level),
        format=LOG_FORMAT,
    )
