from __future__ import annotations
from collections.abc import Sequence
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
from typing import Any, Optional
from packaging.version import Version
from .errors import ConfigError, InvalidVersionError
from .logging import log


def str_guard(v: Any, fieldname: str) -> str:
    """
    If ``v`` is a `str`, return it; otherwise, raise a `ConfigError`.
    ``fieldname`` is an identifier for ``v`` to include in the error message.
    """
    if isinstance(v, str):
        return v
    else:
        raise ConfigError(f"versioningit's {fieldname} must be set to a string")


def optional_str_guard(v: Any, fieldname: str) -> Optional[str]:
    """
    If ``v`` is a `str` or `None`, return it; otherwise, raise a `ConfigError`.
    ``fieldname`` is an identifier for ``v`` to include in the error message.
    """
    if v is None or isinstance(v, str):
        return v
    else:
        raise ConfigError(f"versioningit's {fieldname} must be a string")


def list_str_guard(v: Any, fieldname: str) -> list[str]:
    """
    If ``v`` is a `list` of `str`\\s, return it; otherwise, raise a
    `ConfigError`.  ``fieldname`` is an identifier for ``v`` to include in the
    error message.
    """
    if isinstance(v, list) and all(isinstance(e, str) for e in v):
        return v
    else:
        raise ConfigError(f"versioningit's {fieldname} must be a list of strings")


def bool_guard(v: Any, fieldname: str) -> bool:
    """
    If ``v`` is a `bool`, return it; otherwise, raise a `ConfigError`.
    ``fieldname`` is an identifier for ``v`` to include in the error message.
    """
    if isinstance(v, bool):
        return v
    else:
        raise ConfigError(f"versioningit's {fieldname} must be set to a boolean")


def runcmd(*args: str | Path, **kwargs: Any) -> subprocess.CompletedProcess:
    """Run and log a given command"""
    arglist = [str(a) for a in args]
    log.debug("Running: %s", showcmd(arglist))
    kwargs.setdefault("check", True)
    return subprocess.run(arglist, **kwargs)


def readcmd(*args: str | Path, **kwargs: Any) -> str:
    """Run a command, capturing & returning its stdout"""
    s = runcmd(*args, stdout=subprocess.PIPE, text=True, **kwargs).stdout
    assert isinstance(s, str)
    return s.strip()


def get_build_date() -> datetime:
    """
    Return the current date & time as an aware UTC `~datetime.datetime`.  If
    :envvar:`SOURCE_DATE_EPOCH` is set, use that value instead (See
    <https://reproducible-builds.org/specs/source-date-epoch/>).
    """
    try:
        source_date_epoch = int(os.environ["SOURCE_DATE_EPOCH"])
    except (KeyError, ValueError):
        return datetime.now(timezone.utc)
    else:
        return fromtimestamp(source_date_epoch)


def fromtimestamp(ts: int) -> datetime:
    """
    Convert an integer number of seconds since the epoch to an aware UTC
    `~datetime.datetime`
    """
    return datetime.fromtimestamp(ts, tz=timezone.utc)


def strip_prefix(s: str, prefix: str) -> str:
    """
    If ``s`` starts with ``prefix``, return the rest of ``s`` after ``prefix``;
    otherwise, return ``s`` unchanged.
    """
    # cf. str.removeprefix, introduced in Python 3.9
    n = len(prefix)
    return s[n:] if s[:n] == prefix else s


def strip_suffix(s: str, suffix: str) -> str:
    """
    If ``s`` ends with ``suffix``, return the rest of ``s`` before ``suffix``;
    otherwise, return ``s`` unchanged.
    """
    # cf. str.removesuffix, introduced in Python 3.9
    n = len(suffix)
    return s[:-n] if s[-n:] == suffix else s


def parse_version_from_metadata(metadata: str) -> str:
    """
    Given a string containing Python packaging metadata, return the value of
    the :mailheader:`Version` field

    :raises ValueError: if there is no :mailheader:`Version` field
    """
    for line in metadata.splitlines():
        m = re.match(r"Version\s*:\s*", line)
        if m:
            return line[m.end() :].strip()
        elif not line:
            break
    raise ValueError("Metadata does not contain a Version field")


def showcmd(args: list) -> str:
    """
    Stringify the elements of ``args``, shell-quote them, and join the results
    with a space
    """
    return " ".join(shlex.quote(os.fsdecode(a)) for a in args)


def is_sdist(project_dir: str | Path) -> bool:
    """
    Performs a simplistic check whether ``project_dir`` (which presumably is
    not under version control) is an unpacked sdist by testing whether
    :file:`PKG-INFO` exists
    """
    if Path(project_dir, "PKG-INFO").exists():
        log.info(
            "Directory is not under version control, and PKG-INFO is present;"
            " assuming this is an sdist"
        )
        return True
    else:
        return False


def split_version(
    v: str, split_on: Optional[str] = None, double_quote: bool = True
) -> str:
    if split_on is None:
        split_on = r"[-_.+!]"
    parts = [int(p) if p.isdigit() else p for p in re.split(split_on, v) if p]
    return repr_tuple(parts, double_quote)


def split_pep440_version(
    v: str, double_quote: bool = True, epoch: Optional[bool] = None
) -> str:
    try:
        vobj = Version(v)
    except ValueError:
        raise InvalidVersionError(f"{v!r} is not a valid PEP 440 version")
    parts: list[str | int] = []
    if epoch or (vobj.epoch and epoch is None):
        parts.append(vobj.epoch)
    parts.extend(vobj.release)
    if vobj.pre is not None:
        phase, num = vobj.pre
        parts.append(f"{phase}{num}")
    if vobj.post is not None:
        parts.append(f"post{vobj.post}")
    if vobj.dev is not None:
        parts.append(f"dev{vobj.dev}")
    if vobj.local is not None:
        parts.append(f"+{vobj.local}")
    return repr_tuple(parts, double_quote)


def repr_tuple(parts: Sequence[str | int], double_quote: bool = True) -> str:
    strparts: list[str] = []
    for p in parts:
        if isinstance(p, int):
            strparts.append(str(p))
        elif double_quote:
            strparts.append(qqrepr(p))
        else:
            strparts.append(repr(p))
    return "(" + ", ".join(strparts) + ")"


def qqrepr(s: str) -> str:
    """Produce a repr(string) enclosed in double quotes"""
    return json.dumps(s, ensure_ascii=False)


def ensure_terminated(s: str) -> str:
    """Append a newline to ``s`` if it doesn't already end with one"""
    lines = s.splitlines(keepends=True)
    if not lines or lines[-1].splitlines() == [lines[-1]]:
        return s + "\n"
    else:
        return s
