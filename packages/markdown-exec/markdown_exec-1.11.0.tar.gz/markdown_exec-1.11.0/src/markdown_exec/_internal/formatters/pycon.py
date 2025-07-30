# Formatter for executing `pycon` code.

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from markdown_exec._internal.formatters.base import base_format
from markdown_exec._internal.formatters.python import _run_python

if TYPE_CHECKING:
    from markupsafe import Markup


def _transform_source(code: str) -> tuple[str, str]:
    python_lines = []
    pycon_lines = []
    for line in code.split("\n"):
        if line.startswith((">>> ", "... ")):
            pycon_lines.append(line)
            python_lines.append(line[4:])
    python_code = "\n".join(python_lines)
    return python_code, "\n".join(pycon_lines)


def _format_pycon(**kwargs: Any) -> Markup:
    return base_format(language="pycon", run=_run_python, transform_source=_transform_source, **kwargs)
