from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import lsprotocol.types as lst
from typing_extensions import TypeAlias, get_args

LevelName: TypeAlias = Literal['trace', 'debug', 'info', 'notice', 'warn', 'warning', 'error', 'fatal']
CallType: TypeAlias = Literal['span', 'log']

LEVEL_NAMES: tuple[LevelName, ...] = get_args(LevelName)


@dataclass
class LogfireCall:
    call_type: CallType
    span_name: str
    code_range: lst.Range
    level_name: LevelName | None = None
