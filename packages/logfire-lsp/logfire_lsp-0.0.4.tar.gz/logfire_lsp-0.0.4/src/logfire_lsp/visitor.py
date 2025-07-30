import libcst as cst
from libcst.metadata import PositionProvider, QualifiedNameProvider, QualifiedNameSource

from .models import LEVEL_NAMES, LogfireCall
from .utils import cst_to_lsp_range, inner_string


class LogfireVisitor(cst.CSTVisitor):
    """A CST visitor gathering Logfire calls."""

    METADATA_DEPENDENCIES = (QualifiedNameProvider, PositionProvider)

    def __init__(self) -> None:
        self.calls: list[LogfireCall] = []

    def visit_Call(self, node: cst.Call) -> None:
        if qnames := self.get_metadata(QualifiedNameProvider, node, []):
            if not qnames:
                return
            qname = next(iter(qnames))
            if qname.source is not QualifiedNameSource.IMPORT:
                return

            parts = qname.name.split('.')

            if (
                len(parts) != 2
                or parts[0] != 'logfire'
                or parts[1] not in (*LEVEL_NAMES, 'span')
                or len(node.args) == 0
                or not isinstance(node.args[0].value, cst.SimpleString)
            ):
                return

            position = self.get_metadata(PositionProvider, node, None)
            assert position is not None

            self.calls.append(
                LogfireCall(
                    call_type='span' if parts[1] == 'span' else 'log',
                    span_name=inner_string(node.args[0].value.value),
                    code_range=cst_to_lsp_range(position),
                    level_name=parts[1] if parts[1] != 'span' else None,
                )
            )
