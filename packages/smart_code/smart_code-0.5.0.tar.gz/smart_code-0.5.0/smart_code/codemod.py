import libcst as cst
from libcst import metadata

class ListAppendTransformer(cst.CSTTransformer):
    """Transform ``list.append`` loops into list comprehensions."""

    def _maybe_transform(
        self,
        assign_stmt: cst.BaseStatement,
        for_stmt: cst.For,
    ) -> cst.BaseStatement | None:
        """Return a new assignment if the pattern matches."""
        if not isinstance(assign_stmt, cst.SimpleStatementLine):
            return None
        if len(assign_stmt.body) != 1:
            return None
        assign = assign_stmt.body[0]
        if not isinstance(assign, cst.Assign) or len(assign.targets) != 1:
            return None
        target = assign.targets[0].target
        if not isinstance(target, cst.Name):
            return None
        list_name = target.value
        value = assign.value
        if not isinstance(value, cst.List) or value.elements:
            return None

        if not isinstance(for_stmt, cst.For) or not isinstance(for_stmt.body, cst.IndentedBlock):
            return None
        body = for_stmt.body.body
        if len(body) != 1:
            return None
        stmt = body[0]
        if not isinstance(stmt, cst.SimpleStatementLine) or len(stmt.body) != 1:
            return None
        expr = stmt.body[0]
        if not isinstance(expr, cst.Expr):
            return None
        call = expr.value
        if not isinstance(call, cst.Call):
            return None
        func = call.func
        if not (isinstance(func, cst.Attribute) and func.attr.value == "append"):
            return None
        lst = func.value
        if not (isinstance(lst, cst.Name) and lst.value == list_name):
            return None
        target_name = for_stmt.target
        if not isinstance(target_name, cst.Name):
            return None
        iter_expr = for_stmt.iter
        elt = call.args[0].value if call.args else cst.Name(value=target_name.value)
        comp = cst.ListComp(elt=elt, for_in=cst.CompFor(target=target_name, iter=iter_expr))
        new_assign = cst.Assign(targets=[cst.AssignTarget(target=cst.Name(value=list_name))], value=comp)
        return cst.SimpleStatementLine([new_assign])

    def _transform_body(self, body: list[cst.BaseStatement]) -> list[cst.BaseStatement]:
        new_body: list[cst.BaseStatement] = []
        i = 0
        while i < len(body):
            if i + 1 < len(body):
                transformed = self._maybe_transform(body[i], body[i + 1])
                if transformed is not None:
                    new_body.append(transformed)
                    i += 2
                    continue
            new_body.append(body[i])
            i += 1
        return new_body

    def leave_IndentedBlock(self, original_node: cst.IndentedBlock, updated_node: cst.IndentedBlock) -> cst.IndentedBlock:
        return updated_node.with_changes(body=self._transform_body(list(updated_node.body)))

    def leave_Module(self, original_node: cst.Module, updated_node: cst.Module) -> cst.Module:
        return updated_node.with_changes(body=self._transform_body(list(updated_node.body)))

class DictSetItemTransformer(cst.CSTTransformer):
    """Transform simple dict-building loops into comprehensions."""

    def _maybe_transform(
        self,
        assign_stmt: cst.BaseStatement,
        for_stmt: cst.For,
    ) -> cst.BaseStatement | None:
        if not isinstance(assign_stmt, cst.SimpleStatementLine):
            return None
        if len(assign_stmt.body) != 1:
            return None
        assign = assign_stmt.body[0]
        if not isinstance(assign, cst.Assign) or len(assign.targets) != 1:
            return None
        target = assign.targets[0].target
        if not isinstance(target, cst.Name):
            return None
        dict_name = target.value
        value = assign.value
        if not isinstance(value, cst.Dict) or value.elements:
            return None

        if not isinstance(for_stmt, cst.For) or not isinstance(for_stmt.body, cst.IndentedBlock):
            return None
        body = for_stmt.body.body
        if len(body) != 1:
            return None
        stmt = body[0]
        if not isinstance(stmt, cst.SimpleStatementLine) or len(stmt.body) != 1:
            return None
        inner = stmt.body[0]
        if not isinstance(inner, cst.Assign) or len(inner.targets) != 1:
            return None
        tgt = inner.targets[0].target
        if not (isinstance(tgt, cst.Subscript) and isinstance(tgt.value, cst.Name) and tgt.value.value == dict_name and len(tgt.slice) == 1):
            return None
        sub = tgt.slice[0].slice
        if not isinstance(sub, cst.Index):
            return None
        key = sub.value
        val = inner.value
        comp = cst.DictComp(key=key, value=val, for_in=cst.CompFor(target=for_stmt.target, iter=for_stmt.iter))
        new_assign = cst.Assign(targets=[cst.AssignTarget(target=cst.Name(value=dict_name))], value=comp)
        return cst.SimpleStatementLine([new_assign])

    def _transform_body(self, body: list[cst.BaseStatement]) -> list[cst.BaseStatement]:
        new_body: list[cst.BaseStatement] = []
        i = 0
        while i < len(body):
            if i + 1 < len(body):
                transformed = self._maybe_transform(body[i], body[i + 1])
                if transformed is not None:
                    new_body.append(transformed)
                    i += 2
                    continue
            new_body.append(body[i])
            i += 1
        return new_body

    def leave_IndentedBlock(self, original_node: cst.IndentedBlock, updated_node: cst.IndentedBlock) -> cst.IndentedBlock:
        return updated_node.with_changes(body=self._transform_body(list(updated_node.body)))

    def leave_Module(self, original_node: cst.Module, updated_node: cst.Module) -> cst.Module:
        return updated_node.with_changes(body=self._transform_body(list(updated_node.body)))


class RefactorTransformer(cst.CSTTransformer):
    """Apply all available transformations."""

    def __init__(self) -> None:
        self.transforms = [ListAppendTransformer(), DictSetItemTransformer()]

    def leave_Module(self, original_node: cst.Module, updated_node: cst.Module) -> cst.Module:
        node = updated_node
        for t in self.transforms:
            node = t.leave_Module(original_node, node)
        return node

    def leave_IndentedBlock(self, original_node: cst.IndentedBlock, updated_node: cst.IndentedBlock) -> cst.IndentedBlock:
        node = updated_node
        for t in self.transforms:
            node = t.leave_IndentedBlock(original_node, node)
        return node


def refactor_code(code: str) -> str:
    """Refactor code string using available codemods."""
    module = cst.parse_module(code)
    wrapper = metadata.MetadataWrapper(module, unsafe_skip_copy=True)
    transformer = RefactorTransformer()
    modified = wrapper.visit(transformer)
    return modified.code


def refactor_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()
    new_code = refactor_code(code)
    if new_code != code:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_code)
    return new_code
