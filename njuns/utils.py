import logging
import os
import sys
from typing import Any, Union, Dict

Response = Union[Dict[str, Any], str]


class _MissingSentinel:
    """A sentinel value that represents a non-optional value,
    but can be missing as in the value has not been populated yet."""

    __slots__ = ()

    def __eq__(self, other) -> bool:
        return False

    def __bool__(self) -> bool:
        return False

    def __hash__(self) -> int:
        return 0

    def __repr__(self) -> str:
        return "..."

    def __str__(self) -> None:
        return None


MISSING: Any = _MissingSentinel()


class _ColourFormatter(logging.Formatter):
    LEVEL_COLOURS = [
        (logging.DEBUG, "\x1b[40;1m"),
        (logging.INFO, "\x1b[34;1m"),
        (logging.WARNING, "\x1b[33;1m"),
        (logging.ERROR, "\x1b[31m"),
        (logging.CRITICAL, "\x1b[41m"),
    ]

    FORMATS = {
        level: logging.Formatter(
            f"\x1b[30;1m%(asctime)s\x1b[0m {colour}%(levelname)-8s\x1b[0m \x1b[35m%(name)s\x1b[0m %(message)s",
            "%Y-%m-%d %H:%M:%S",
        )
        for level, colour in LEVEL_COLOURS
    }

    def format(self, record):
        formatter = self.FORMATS.get(record.levelno)
        if formatter is None:
            formatter = self.FORMATS[logging.DEBUG]

        # Override the traceback to always print in red
        if record.exc_info:
            text = formatter.formatException(record.exc_info)
            record.exc_text = f"\x1b[31m{text}\x1b[0m"

        output = formatter.format(record)

        # Remove the cache layer
        record.exc_text = None
        return output


def stream_supports_colour(stream: Any) -> bool:
    is_a_tty = hasattr(stream, "isatty") and stream.isatty()

    # Pycharm and Vscode support colour in their inbuilt editors
    if "PYCHARM_HOSTED" in os.environ or os.environ.get("TERM_PROGRAM") == "vscode":
        return is_a_tty

    if sys.platform != "win32":
        # Docker does not consistently have a tty attached to it
        return is_a_tty

    # ANSICON checks for things like ConEmu
    # WT_SESSION checks if this is Windows Terminal
    return is_a_tty and ("ANSICON" in os.environ or "WT_SESSION" in os.environ)


def setup_logging(
    *,
    handler: logging.Handler = MISSING,
    formatter: logging.Formatter = MISSING,
    level: int = MISSING,
    root: bool = True,
) -> None:
    """A helper to set up logging.

    :param handler: The log handler to use for logging. Default is :class:`logging.StreamHandler`.
    :type handler: logging.Handler
    :param formatter: The formatter to use with the given handler.
    :type formatter: logging.Formatter
    :param level: The default log level for the library's logger. Default is ``logging.INFO``
    :type level: int
    :param root: Whether to use the root logger than the library logger. Default is ``True``.
    :type root: bool
    """
    if level is MISSING:
        level = logging.INFO

    if handler is MISSING:
        handler = logging.StreamHandler()

    if formatter is MISSING:
        if isinstance(handler, logging.StreamHandler) and stream_supports_colour(
            handler.stream
        ):
            formatter = _ColourFormatter()
        else:
            dt_fmt = "%Y-%m-%d %H:%M:%S"
            formatter = logging.Formatter(
                "[{asctime}] [{levelname:<8}] {name}: {message}", dt_fmt, style="{"
            )

    if root:
        logger = logging.getLogger()
    else:
        library, _, _ = str(__name__).partition(".")
        logger = logging.getLogger(library)

    handler.setFormatter(formatter)
    logger.setLevel(level)
    logger.addHandler(handler)
