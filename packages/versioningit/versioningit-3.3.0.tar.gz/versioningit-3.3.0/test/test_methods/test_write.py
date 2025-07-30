from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import pytest
from versioningit.basics import basic_write
from versioningit.errors import ConfigError


@pytest.mark.parametrize(
    "filename,params,content",
    [
        ("foo/bar.txt", {}, "1.2.3\n"),
        ("foo/bar.py", {}, '__version__ = "1.2.3"\n'),
        ("foo/bar", {}, "1.2.3\n"),
        (
            "foo/bar.py",
            {"template": "__version__ = {version!r}"},
            "__version__ = '1.2.3'\n",
        ),
        ("foo/bar.tex", {"template": r"$v = {version}$\bye"}, "$v = 1.2.3$\\bye\n"),
        (
            "foo/bar.py",
            {
                "template": (
                    "__version__ = {version!r}\n"
                    '__build_date__ = "{build_date:%Y-%m-%dT%H:%M:%SZ}"'
                )
            },
            "__version__ = '1.2.3'\n__build_date__ = \"2038-01-19T03:14:07Z\"\n",
        ),
    ],
)
def test_basic_write(
    filename: str, params: dict[str, Any], content: str, tmp_path: Path
) -> None:
    basic_write(
        project_dir=tmp_path,
        template_fields={
            "version": "1.2.3",
            "build_date": datetime(2038, 1, 19, 3, 14, 7, tzinfo=timezone.utc),
        },
        params={"file": filename, **params},
    )
    assert (tmp_path / filename).read_text(encoding="utf-8") == content


def test_basic_write_no_file(tmp_path: Path) -> None:
    with pytest.raises(ConfigError) as excinfo:
        basic_write(
            project_dir=tmp_path, template_fields={"version": "1.2.3"}, params={}
        )
    assert str(excinfo.value) == "versioningit's write.file must be set to a string"


def test_basic_write_bad_ext(tmp_path: Path) -> None:
    with pytest.raises(ConfigError) as excinfo:
        basic_write(
            project_dir=tmp_path,
            template_fields={"version": "1.2.3"},
            params={"file": "foo/bar.tex"},
        )
    assert str(excinfo.value) == (
        "versioningit: write.template not specified and file has unknown"
        " suffix '.tex'"
    )
    assert list(tmp_path.iterdir()) == []
