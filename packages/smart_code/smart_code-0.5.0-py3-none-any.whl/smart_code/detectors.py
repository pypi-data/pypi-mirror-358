import libcst as cst

class BaseDetector:
    """Base class for lightweight detection rules."""
    def __init__(self, analyzer) -> None:
        self.analyzer = analyzer

    def _add_issue(self, pattern_id: str, node: cst.CSTNode) -> None:
        self.analyzer._add_issue(pattern_id, self.analyzer._line(node))

class RepeatedSortDetector(BaseDetector):
    """Detect list.sort() calls inside loops."""

    def visit_Call(self, node: cst.Call) -> None:
        if (
            self.analyzer.loop_stack
            and isinstance(node.func, cst.Attribute)
            and node.func.attr.value == "sort"
        ):
            if isinstance(node.func.value, cst.Name):
                var = node.func.value.value
                if var not in self.analyzer.loop_vars_stack[-1]:
                    self._add_issue("REPEATED_SORT", node)

class ListQueueUsageDetector(BaseDetector):
    """Detect list used as queue via pop(0) or insert(0, x)."""

    def visit_Call(self, node: cst.Call) -> None:
        if not isinstance(node.func, cst.Attribute):
            return
        if node.func.attr.value == "pop" and node.args:
            arg = node.args[0].value
            if isinstance(arg, cst.Integer) and arg.value == "0":
                self._add_issue("LIST_QUEUE_USAGE", node)
        elif node.func.attr.value == "insert" and node.args:
            arg = node.args[0].value
            if isinstance(arg, cst.Integer) and arg.value == "0":
                self._add_issue("LIST_QUEUE_USAGE", node)
