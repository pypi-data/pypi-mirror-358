import ast
from typing import List

class Pattern:
    name: str
    description: str

    def match(self, node: ast.AST) -> bool:
        raise NotImplementedError

    def suggest(self, node: ast.AST) -> str:
        raise NotImplementedError

_patterns: List[Pattern] = []

def register(pattern_cls):
    _patterns.append(pattern_cls())
    return pattern_cls

def all_patterns():
    return _patterns

@register
class BadListMemberCheck(Pattern):
    name = "bad_list_member_check"
    description = "list member check inside loop; use set for O(1) membership"

    def match(self, node):
        if not isinstance(node, ast.If):
            return False
        test = node.test
        return (isinstance(test, ast.Compare)
                and isinstance(test.ops[0], ast.In)
                and isinstance(test.left, ast.Name)
                and isinstance(test.comparators[0], ast.Name))

    def suggest(self, node):
        list_name = node.test.comparators[0].id
        return (
            f"将列表 '{list_name}' 转为集合："
            f"  {list_name}_set = set({list_name})"
            f"并在循环中使用集合进行成员检查，提高到 O(1) 复杂度。"
        )

@register
class BadSortTakeFirst(Pattern):
    name = "bad_sort_take_first"
    description = "sorting whole list to take min/max; use min()/max()"

    def match(self, node):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Subscript):
            val = node.value
            if (isinstance(val.value, ast.Call) and
                isinstance(val.value.func, ast.Name) and val.value.func.id == 'sorted'):
                return True
        return False

    def suggest(self, node):
        target = node.targets[0].id if hasattr(node, 'targets') else 'result'
        iter_expr = ast.unparse(node.value.value.args[0])
        return (
            "无需对整个列表排序后取第一个元素，建议："
            f"  # 原代码 {target} = sorted({iter_expr})[0]"
            f"  # 优化后 {target} = min({iter_expr})"
        )

@register
class BadSortSlice(Pattern):
    name = "bad_sort_slice"
    description = "sorting then slicing; use heapq.nsmallest/nlargest"

    def match(self, node):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Subscript):
            return isinstance(node.value.value, ast.Call) and isinstance(node.value.value.func, ast.Name) and node.value.value.func.id == 'sorted'
        return False

    def suggest(self, node):
        iter_expr = ast.unparse(node.value.value.args[0])
        slice_part = ast.unparse(node.value.slice)
        return (
            "排序后切片取前 N 项可使用 heapq："
            f"  # 原代码  top_n = sorted({iter_expr}){slice_part}"
            f"  # 优化后  import heapq  top_n = heapq.nsmallest({slice_part.strip('[]')}, {iter_expr})"
        )

@register
class BadLoopSum(Pattern):
    name = "bad_loop_sum"
    description = "loop-based sum; use built-in sum()"

    def match(self, node):
        return (isinstance(node, ast.AugAssign)
                and isinstance(node.op, ast.Add)
                and isinstance(node.target, ast.Name))

    def suggest(self, node):
        var = node.target.id
        return (
            f"循环累加可使用内置 sum()："
            f"  # 原代码"
            f"  {var} = 0"
            f"  for x in data:"
            f"      {var} += x"
            f"  # 优化后"
            f"  {var} = sum(data)"
        )

@register
class BadStringConcat(Pattern):
    name = "bad_string_concat"
    description = "string concatenation inside loop; use str.join()"

    def match(self, node):
        return (isinstance(node, ast.AugAssign)
                and isinstance(node.op, ast.Add)
                and isinstance(node.value, ast.Name)
                and isinstance(node.target, ast.Name))

    def suggest(self, node):
        var = node.target.id
        return (
            f"循环中字符串拼接效率低，建议收集后一次性 join："
            f"  # 原代码"
            f"  {var} = ''"
            f"  for part in parts:"
            f"      {var} += part"
            f"  # 优化后"
            f"  {var} = ''.join(parts)"
        )

@register
class BadNestedLoopFlatten(Pattern):
    name = "bad_nested_loop_flatten"
    description = "nested loops for flattening; use itertools.chain.from_iterable()"

    def match(self, node):
        if isinstance(node, ast.For):
            for stmt in node.body:
                if isinstance(stmt, ast.For):
                    inner = stmt
                    for s in inner.body:
                        if (isinstance(s, ast.Expr) and isinstance(s.value, ast.Call)
                            and isinstance(s.value.func, ast.Attribute)
                            and s.value.func.attr == 'append'):
                            return True
        return False

    def suggest(self, node):
        outer = node.iter.id if isinstance(node.iter, ast.Name) else 'lists'
        return (
            "嵌套循环扁平化可使用 itertools："
            f"  # 原代码"
            f"  flat = []"
            f"  for sub in {outer}:"
            f"      for x in sub:"
            f"          flat.append(x)"
            f"  # 优化后"
            f"  import itertools"
            f"  flat = list(itertools.chain.from_iterable({outer}))"
        )

@register
class BadManualIndexLoop(Pattern):
    name = "bad_manual_index_loop"
    description = "loop over range(len()) and index list; use direct iteration"

    def match(self, node):
        if isinstance(node, ast.For) and isinstance(node.iter, ast.Call):
            func = node.iter.func
            if isinstance(func, ast.Name) and func.id == 'range':
                args = node.iter.args
                if len(args) == 1 and isinstance(args[0], ast.Call):
                    inner = args[0]
                    if (isinstance(inner.func, ast.Name) and inner.func.id == 'len'):
                        return True
        return False

    def suggest(self, node):
        list_name = node.iter.args[0].args[0].id
        return (
            "直接迭代列表无需索引："
            f"  # 原代码"
            f"  for i in range(len({list_name})):"
            f"      val = {list_name}[i]"
            f"  # 优化后"
            f"  for val in {list_name}:"
        )

@register
class BadFilterToList(Pattern):
    name = "bad_filter_to_list"
    description = "list(filter(...)) usage; use list comprehension"

    def match(self, node):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            val = node.value
            if (isinstance(val.func, ast.Name) and val.func.id == 'list'
                and val.args and isinstance(val.args[0], ast.Call)
                and isinstance(val.args[0].func, ast.Name)
                and val.args[0].func.id == 'filter'):
                return True
        return False

    def suggest(self, node):
        target = node.targets[0].id
        iterable = ast.unparse(node.value.args[0].args[1])
        return (
            "使用列表推导替换 filter："
            f"  # 原代码"
            f"  {target} = list(filter(lambda x: x>0, {iterable}))"
            f"  # 优化后"
            f"  {target} = [x for x in {iterable} if x > 0]"
        )

@register
class GeneralDictComprehension(Pattern):
    # Historical name kept for backward compatibility
    name = "bad_dict_comprehension"
    description = "循环赋值构建 dict；可用 dict comprehension"

    def match(self, node: ast.For) -> bool:
        # 只看 for 结构
        if not isinstance(node, ast.For):
            return False

        # 先找到前面的 x = {}，确认字典名
        # 假设 AST 中 x = {} 出现在模块顶层或函数体中时已经被解析过
        # 这里简化为只要在循环内部看到 x[...] = ... 就认为 x 是目标字典
        for stmt in node.body:
            if isinstance(stmt, ast.Assign):
                tgt = stmt.targets[0]
                # 目标必须是 x[key] 这种下标形式
                if isinstance(tgt, ast.Subscript) and isinstance(tgt.value, ast.Name):
                    return True
        return False

    def suggest(self, node: ast.For) -> str:
        # 循环变量名和可迭代对象
        loop_var = node.target.id                           # 比如 i
        iter_expr = ast.unparse(node.iter)                  # 比如 items
        # 取出第一条赋值语句，构造 RHS 表达式
        assign = next(stmt for stmt in node.body if isinstance(stmt, ast.Assign))
        dict_name = assign.targets[0].value.id               # 比如 x
        value_expr = ast.unparse(assign.value)              # 比如 i * 2

        return (
            "可以将循环写成字典推导式：\n"
            f"  # 原代码\n"
            f"  {dict_name} = {{}}\n"
            f"  for {loop_var} in {iter_expr}:\n"
            f"      {dict_name}[{loop_var}] = {value_expr}\n\n"
            "  # 优化后\n"
            f"  {dict_name} = {{{loop_var}: {value_expr} for {loop_var} in {iter_expr}}}"
        )

@register
class BadMapToList(Pattern):
    name = "bad_map_to_list"
    description = "map + list; use list comprehension"

    def match(self, node):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            call = node.value
            if (isinstance(call.func, ast.Name) and call.func.id == "list"
                and call.args and isinstance(call.args[0], ast.Call)
                and isinstance(call.args[0].func, ast.Name)
                and call.args[0].func.id == "map"):
                return True
        return False

    def suggest(self, node):
        call = node.value.args[0]
        func = call.args[0]
        iterable = call.args[1]
        target = node.targets[0].id
        func_src = ast.unparse(func)
        iterable_src = ast.unparse(iterable)
        return (
            "使用列表推导替换 map:"
            f"  # 原代码"
            f"  {target} = list(map({func_src}, {iterable_src}))"
            f"  # 优化后"
            f"  {target} = [{func_src}(x) for x in {iterable_src}]"
        )

@register
class BadListAppend(Pattern):
    """Appending to list inside a loop; prefer list comprehension."""

    name = "bad_list_append"
    description = "list append in loop; use list comprehension"

    def match(self, node):
        return (
            isinstance(node, ast.For)
            and len(node.body) == 1
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Call)
            and isinstance(node.body[0].value.func, ast.Attribute)
            and node.body[0].value.func.attr == "append"
        )

    def suggest(self, node):
        target = node.body[0].value.func.value.id
        value_src = ast.unparse(node.body[0].value.args[0]) if node.body[0].value.args else ""
        iter_src = ast.unparse(node.iter)
        loop_var = ast.unparse(node.target)
        return (
            "使用列表推导式替代 append 循环:\n"
            f"  # 原代码\n  {target} = []\n  for {loop_var} in {iter_src}:\n      {target}.append({value_src})\n\n"
            "  # 优化后\n"
            f"  {target} = [{value_src} for {loop_var} in {iter_src}]"
        )
