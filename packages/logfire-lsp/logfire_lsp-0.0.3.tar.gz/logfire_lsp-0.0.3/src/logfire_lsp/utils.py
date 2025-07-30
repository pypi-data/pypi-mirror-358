from __future__ import annotations

import lsprotocol.types as lst
from libcst.metadata import CodeRange


def inner_string(value: str) -> str:
    if value.startswith("'") and value.endswith("'"):
        return value.removeprefix("'").removesuffix("'")
    return value.removeprefix('"').removesuffix('"')


def cst_to_lsp_range(cst_range: CodeRange) -> lst.Range:
    return lst.Range(
        start=lst.Position(
            line=cst_range.start.line - 1,
            character=cst_range.start.column,
        ),
        end=lst.Position(
            line=cst_range.end.line - 1,
            character=cst_range.end.column,
        ),
    )
