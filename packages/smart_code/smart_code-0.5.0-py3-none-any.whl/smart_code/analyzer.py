import os
import json
import sys
from typing import Optional, Iterable, Sequence

import libcst as cst
from libcst import metadata

from .detectors import BaseDetector, RepeatedSortDetector, ListQueueUsageDetector


class CodeAnalyzer(cst.CSTVisitor):
    """Static analyzer implemented using libcst with type inference."""

    METADATA_DEPENDENCIES = (metadata.PositionProvider, metadata.TypeInferenceProvider)

    def __init__(self, lang: str = "zh"):
        self.lang = lang
        self.reset_state()

    # ------------------------------------------------------------------
    def reset_state(self) -> None:
        self.issues = []
        self.loop_stack: list[cst.For] = []
        self.loop_vars_stack: list[set[str]] = []
        self.df_vars: set[str] = set()
        self.pd_aliases: set[str] = set()
        self.df_aliases: set[str] = set()
        self.read_csv_aliases: set[str] = set()
        self.list_vars: set[str] = set()
        self.set_vars: set[str] = set()
        self.str_vars: set[str] = set()
        self.patterns = self._load_patterns()
        self.detectors: list[BaseDetector] = [
            RepeatedSortDetector(self),
            ListQueueUsageDetector(self),
        ]

    # ------------------------------------------------------------------
    def _load_patterns(self) -> dict:
        path = os.path.join(os.path.dirname(__file__), "patterns.json")
        try:
            with open(path, encoding="utf-8") as f:
                patterns = json.load(f)
        except Exception as e:  # pragma: no cover - loading failure
            sys.stderr.write(f"Error loading patterns.json: {e}\n")
            return {}
        return {p["id"]: p for p in patterns if "id" in p}

    # ------------------------------------------------------------------
    def analyze(self, code: str) -> list[dict]:
        self.reset_state()
        try:
            module = cst.parse_module(code)
        except cst.ParserSyntaxError as e:
            self.issues.append(self._make_error_issue(e.raw_line or 0, f"SyntaxError: {e}"))
            return self.issues
        # TypeInferenceProvider requires a cache even if it's empty, otherwise
        # MetadataWrapper will raise an exception during resolution. Provide a
        # minimal empty cache so analysis can run without Pyre type inference
        # data available.
        wrapper = metadata.MetadataWrapper(
            module,
            cache={metadata.TypeInferenceProvider: {}}
        )
        wrapper.visit(self)
        return self.issues

    def analyze_file(self, filepath: str) -> list[dict]:
        try:
            with open(filepath, encoding="utf-8") as f:
                code = f.read()
        except Exception as e:  # pragma: no cover - IO errors
            sys.stderr.write(f"Error reading {filepath}: {e}\n")
            return []
        return self.analyze(code)

    # ------------------------------------------------------------------
    def _make_error_issue(self, lineno: int, msg: str) -> dict:
        return {
            "pattern": "SYNTAX_ERROR",
            "lineno": lineno,
            "description": msg,
            "suggestion": "Fix syntax errors before analysis.",
            "complexity": "",
            "hint": "",
        }

    def _line(self, node: cst.CSTNode) -> int:
        pos = self.get_metadata(metadata.PositionProvider, node)
        return pos.start.line

    def _dispatch(self, method: str, node: cst.CSTNode) -> None:
        for det in self.detectors:
            func = getattr(det, method, None)
            if func:
                func(node)

    # Utility to extract dotted name from ImportAlias or Attribute
    def _full_name(self, node: Optional[cst.CSTNode]) -> str:
        if node is None:
            return ""
        if isinstance(node, cst.Name):
            return node.value
        if isinstance(node, cst.Attribute):
            return f"{self._full_name(node.value)}.{node.attr.value}"
        return ""

    # ------------------------------------------------------------------
    # Imports
    def visit_Import(self, node: cst.Import) -> None:
        for alias in node.names:
            if self._full_name(alias.name) == "pandas":
                asname = alias.asname.name.value if alias.asname else "pandas"
                self.pd_aliases.add(asname)
        self._dispatch("visit_Import", node)

    def visit_ImportFrom(self, node: cst.ImportFrom) -> None:
        if self._full_name(node.module) == "pandas":
            for alias in node.names:
                if not isinstance(alias, cst.ImportAlias):
                    continue
                name = self._full_name(alias.name)
                asname = alias.asname.name.value if alias.asname else name
                if name == "DataFrame":
                    self.df_aliases.add(asname)
                elif name == "read_csv":
                    self.read_csv_aliases.add(asname)
        self._dispatch("visit_ImportFrom", node)

    # ------------------------------------------------------------------
    # Assignments
    def visit_Assign(self, node: cst.Assign) -> None:
        value = node.value

        if self.loop_stack:
            for tgt in node.targets:
                if isinstance(tgt.target, cst.Name):
                    self.loop_vars_stack[-1].add(tgt.target.value)

        if isinstance(value, cst.Call):
            func = value.func
            if isinstance(func, cst.Attribute) and isinstance(func.value, cst.Name):
                if func.value.value in self.pd_aliases and func.attr.value in {"DataFrame", "read_csv"}:
                    self._track_targets(node.targets)
            elif isinstance(func, cst.Name):
                if func.value in self.df_aliases.union(self.read_csv_aliases):
                    self._track_targets(node.targets)

        if isinstance(value, cst.Name) and value.value in self.df_vars:
            self._track_targets(node.targets)

        typ = self.get_metadata(metadata.TypeInferenceProvider, value, None)
        if typ and "DataFrame" in str(typ):
            self._track_targets(node.targets)

        if isinstance(value, cst.SimpleString):
            for tgt in node.targets:
                if isinstance(tgt.target, cst.Name):
                    self.str_vars.add(tgt.target.value)

        if isinstance(value, (cst.List, cst.ListComp)) or (
            isinstance(value, cst.Call)
            and isinstance(value.func, cst.Name)
            and value.func.value == "list"
        ):
            for tgt in node.targets:
                if isinstance(tgt.target, cst.Name):
                    self.list_vars.add(tgt.target.value)

        if isinstance(value, (cst.Set, cst.SetComp)) or (
            isinstance(value, cst.Call)
            and isinstance(value.func, cst.Name)
            and value.func.value == "set"
        ):
            for tgt in node.targets:
                if isinstance(tgt.target, cst.Name):
                    self.set_vars.add(tgt.target.value)

        if (
            self.loop_stack
            and isinstance(value, cst.BinaryOperation)
            and isinstance(value.operator, cst.Add)
            and len(node.targets) == 1
            and isinstance(node.targets[0].target, cst.Name)
        ):
            target_name = node.targets[0].target.value
            if target_name in self.str_vars:
                left = value.left
                right = value.right
                is_left = isinstance(left, cst.Name) and left.value == target_name
                is_right = isinstance(right, cst.Name) and right.value == target_name
                if is_left or is_right:
                    self._add_issue("STRING_CONCAT_IN_LOOP", self._line(node))

        if self.loop_stack and isinstance(node.targets[0].target, cst.Subscript):
            if self._is_simple_dict_build(node):
                self._add_issue("DICT_SETITEM_IN_LOOP", self._line(node))

        self._dispatch("visit_Assign", node)

    def _track_targets(self, targets: Sequence[cst.AssignTarget]) -> None:
        for tgt in targets:
            if isinstance(tgt.target, cst.Name):
                self.df_vars.add(tgt.target.value)

    # ------------------------------------------------------------------
    def visit_For(self, node: cst.For) -> None:
        self.loop_stack.append(node)
        self.loop_vars_stack.append(set())
        if len(self.loop_stack) > 1:
            class MatrixAccessVisitor(cst.CSTVisitor):
                def __init__(self) -> None:
                    self.has_matrix_access = False

                def visit_Subscript(self, n: cst.Subscript) -> None:
                    if isinstance(n.value, cst.Subscript):
                        self.has_matrix_access = True

            visitor = MatrixAccessVisitor()
            node.body.visit(visitor)
            if visitor.has_matrix_access:
                self._add_issue("NESTED_LOOP_FOR_MATRIX", self._line(node))
        self._dispatch("visit_For", node)

    def leave_For(self, original_node: cst.For) -> None:
        self.loop_stack.pop()
        self.loop_vars_stack.pop()
        self._dispatch("leave_For", original_node)

    def visit_While(self, node: cst.While) -> None:
        self.loop_stack.append(node)
        self.loop_vars_stack.append(set())
        self._dispatch("visit_While", node)

    def leave_While(self, original_node: cst.While) -> None:
        self.loop_stack.pop()
        self.loop_vars_stack.pop()
        self._dispatch("leave_While", original_node)

    # ------------------------------------------------------------------
    def visit_AugAssign(self, node: cst.AugAssign) -> None:
        if (
            self.loop_stack
            and isinstance(node.operator, cst.AddAssign)
            and isinstance(node.target, cst.Name)
            and node.target.value in self.str_vars
        ):
            self._add_issue("STRING_CONCAT_IN_LOOP", self._line(node))
        self._dispatch("visit_AugAssign", node)

    # ------------------------------------------------------------------
    def visit_Call(self, node: cst.Call) -> None:
        if not isinstance(node.func, cst.Attribute):
            return
        owner = node.func.value
        method = node.func.attr.value
        line = self._line(node)

        if method == "iterrows":
            self._add_issue("PANDAS_ITERROWS", line)
        elif (
            isinstance(owner, cst.Name)
            and owner.value in self.df_vars
            and method == "apply"
        ):
            for arg in node.args:
                if arg.keyword and arg.keyword.value == "axis":
                    val = arg.value
                    if (
                        isinstance(val, cst.Integer)
                        and val.value == "1"
                    ) or (
                        isinstance(val, cst.SimpleString)
                        and val.evaluated_value == "columns"
                    ):
                        self._add_issue("PANDAS_APPLY_AXIS1", line)
        elif (
            isinstance(owner, cst.Name)
            and owner.value in self.df_vars
            and method == "append"
            and self.loop_stack
        ):
            self._add_issue("DATAFRAME_APPEND_LOOP", line)
        elif method == "append" and isinstance(owner, cst.Name) and self.loop_stack:
            if self._is_simple_append_loop(node):
                self._add_issue("LIST_APPEND_IN_LOOP", line)
        elif (
            method == "add"
            and isinstance(owner, cst.Name)
            and owner.value in self.set_vars
            and self.loop_stack
        ):
            self._add_issue("SET_ADD_IN_LOOP", line)
        elif method == "replace" and self.loop_stack:
            self._add_issue("STRING_REPLACE_IN_LOOP", line)

        self._dispatch("visit_Call", node)

    # ------------------------------------------------------------------
    def visit_Comparison(self, node: cst.Comparison) -> None:
        if (
            self.loop_stack
            and len(node.comparisons) == 1
            and isinstance(node.comparisons[0].operator, cst.In)
            and isinstance(node.comparisons[0].comparator, cst.Name)
        ):
            container = node.comparisons[0].comparator.value
            if container in self.list_vars:
                self._add_issue("LINEAR_SEARCH_IN_LOOP", self._line(node))

        self._dispatch("visit_Comparison", node)

    # ------------------------------------------------------------------
    def _add_issue(self, pid: str, lineno: int) -> None:
        meta = self.patterns.get(pid)
        if not meta:
            return
        msg = meta.get("messages", {}).get(self.lang, {})
        issue = {
            "pattern": pid,
            "lineno": lineno,
            "description": msg.get("description", ""),
            "suggestion": msg.get("suggestion", ""),
            "complexity": meta.get("complexity", ""),
            "hint": msg.get("hint", ""),
            "suggestion_code": msg.get("suggestion_code"),
        }
        self.issues.append(issue)

    # ------------------------------------------------------------------
    def _is_simple_append_loop(self, call_node: cst.Call) -> bool:
        if not self.loop_stack:
            return False
        loop = self.loop_stack[-1]
        body = getattr(loop.body, "body", [])
        if len(body) != 1:
            return False
        stmt = body[0]
        if not isinstance(stmt, cst.SimpleStatementLine):
            return False
        if len(stmt.body) != 1:
            return False
        expr = stmt.body[0]
        return isinstance(expr, cst.Expr) and expr.value is call_node

    def _is_simple_dict_build(self, node: cst.Assign) -> bool:
        if not self.loop_stack:
            return False
        loop = self.loop_stack[-1]
        body = getattr(loop.body, "body", [])
        for stmt in body:
            if not isinstance(stmt, cst.SimpleStatementLine):
                return False
            if len(stmt.body) != 1 or not isinstance(stmt.body[0], cst.Assign):
                return False
            assign = stmt.body[0]
            if not assign.targets or not isinstance(assign.targets[0].target, cst.Subscript):
                return False
        return True


# ----------------------------------------------------------------------
# Convenience wrappers

def analyze_code_str(code: str) -> list[dict]:
    return CodeAnalyzer().analyze(code)

from .patterns import all_patterns

def analyze_code(code: str):
    """Analyze code using simple Pattern classes.

    Returns a list of tuples ``(filename, lineno, pattern_name, message)``.
    This keeps backward compatibility with older tests that rely on AST based
    pattern matching.
    """
    import ast

    tree = ast.parse(code)
    results = []
    for n in ast.walk(tree):
        for pattern in all_patterns():
            try:
                if pattern.match(n):
                    results.append(
                        ("", getattr(n, "lineno", 0), pattern.name, pattern.suggest(n))
                    )
            except Exception:
                # Ignore individual pattern errors to keep analysis robust
                pass
    return results

