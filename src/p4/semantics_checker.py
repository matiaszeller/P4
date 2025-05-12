from __future__ import annotations
from dataclasses import dataclass
from collections import ChainMap
from typing import List, Dict
from lark import Tree, Token

# error hierarchy
class StaticError(Exception): pass
class TypeError_(StaticError): pass
class ScopeError(StaticError): pass
class CaseError(StaticError): pass
class StructureError(StaticError): pass

# helper dataclass
@dataclass
class FunctionSig:
    params: List[str]
    ret: str
    body: Tree

# static semantics checker
class SemanticsChecker:
    # primitive sets
    PRIMITIVES = {"boolean", "integer", "decimal", "string", "noType"}
    _NUM = {"integer", "decimal"}
    _ARITH = _NUM | {"string"}

    def __init__(self) -> None:
        self._vars: ChainMap[str, str] = ChainMap()
        self._funcs: Dict[str, FunctionSig] = {}
        self._current_ret: str | None = None
        self._in_global: bool = True
        self._case_style: str = "camelCase"
        self._func_order: list[str] = []
        self._saw_syntax: bool = False
        self._in_expr_stmt: bool = False

    # main entry
    def run(self, tree: Tree) -> None:
        self._walk(tree)
        self._post_checks()

    # walker
    def _walk(self, node: Tree | Token):
        if isinstance(node, Token):
            return self._visit_token(node)
        return getattr(self, f"visit_{node.data}", self._default)(node)

    def _default(self, n: Tree):
        for ch in n.children:
            self._walk(ch)

    # token handling
    def _visit_token(self, tk: Token):
        if tk.type == "INT":     return "integer"
        if tk.type == "FLOAT":   return "decimal"
        if tk.type == "BOOLEAN": return "boolean"
        if tk.type == "STRING":  return "string"
        if tk.type == "ID":
            if tk.value not in self._vars:
                raise ScopeError(f"Undeclared identifier '{tk.value}'")
            return self._vars[tk.value]
        return None

    # syntax header
    def visit_syntax(self, n: Tree):
        if self._saw_syntax:
            raise StructureError("Duplicate syntax header")
        lang, case = n.children[0].value, n.children[1].value
        if lang not in {"EN", "DK"}: raise StructureError("Unsupported language")
        if case not in {"camelCase", "snake_case"}: raise StructureError("Unsupported case style")
        self._case_style, self._saw_syntax = case, True

    # start
    def visit_start(self, n: Tree):
        for ch in n.children:
            self._walk(ch)
            if isinstance(ch, Tree) and ch.data not in {"syntax", "function_definition"}:
                raise StructureError("Only function definitions allowed at top level")

    # functions
    def visit_function_definition(self, n: Tree):
        if not self._in_global: raise StructureError("Nested functions not allowed")
        ret_t, fname = n.children[0].value, n.children[1].value
        params_node = next((c for c in n.children if isinstance(c, Tree) and c.data == "params"), None)
        body = n.children[-1]
        if fname in self._funcs: raise ScopeError(f"Function '{fname}' already defined")
        self._func_order.append(fname)

        p_names, p_types = [], []
        if params_node:
            for p in params_node.children:
                ptype, pid = p.children[0].value, p.children[1].value
                self._check_case(pid)
                self._shadow_check(pid)
                p_names.append(pid)
                p_types.append(ptype)

        self._funcs[fname] = FunctionSig(p_types, ret_t, body)

        outer_vars, outer_ret, outer_flag = self._vars, self._current_ret, self._in_global
        self._vars = ChainMap(dict(zip(p_names, p_types)))
        self._current_ret, self._in_global = ret_t, False
        self._walk(body)

        if ret_t != "noType" and not self._body_guarantees_return(body):
            raise StructureError(f"Function '{fname}' may exit without returning a value")

        self._vars, self._current_ret, self._in_global = outer_vars, outer_ret, outer_flag
        self._check_single_return(body)

    # blocks
    def visit_block(self, n: Tree):
        for st in n.children:
            self._walk(st)

    # declarations
    def visit_declaration_stmt(self, n: Tree):
        base, name = n.children[0].value, n.children[1].value
        self._check_case(name)
        self._shadow_check(name)
        idx, dims = 2, 0
        while idx < len(n.children) and isinstance(n.children[idx], Tree) and n.children[idx].data == "array_suffix":
            dims += 1
            idx += 1
        declared_t = base + "[]" * dims
        rhs_node = None
        if idx < len(n.children):
            child = n.children[idx]
            rhs_node = n.children[idx + 1] if isinstance(child, Token) and child.value == "=" else child
            if isinstance(rhs_node, list): rhs_node = rhs_node[0] if rhs_node else None
        if rhs_node is not None:
            rhs_t = self._walk(rhs_node)
            if rhs_t == "noType" and not self._is_input_expr(rhs_node):
                raise TypeError_("Cannot initialise with value of noType")
            if rhs_t != declared_t and rhs_t != "noType":
                raise TypeError_(f"Initialiser type mismatch for '{name}'")
        self._vars[name] = declared_t

    # assignments
    def visit_assignment_stmt(self, n: Tree):
        lval, rhs_node = n.children[0], n.children[-1]
        name = lval.children[0].value
        if name not in self._vars: raise ScopeError(f"Variable '{name}' not declared")
        var_t = self._vars[name]
        indices = [c for c in lval.children[1:] if c.data == "array_access_suffix"]
        for suf in indices:
            if self._walk(suf.children[0]) != "integer":
                raise TypeError_("Array index must be integer")
        rhs_t = self._walk(rhs_node)
        if rhs_t == "noType" and not self._is_input_expr(rhs_node):
            raise TypeError_("Cannot assign value of noType")
        if indices:
            if var_t.count("[]") < len(indices):
                raise TypeError_("Too many indices for array")
            elem_t = var_t[:-2 * len(indices)]
            if rhs_t != elem_t and rhs_t != "noType":
                raise TypeError_("Assignment type mismatch")
        else:
            if rhs_t != var_t and rhs_t != "noType":
                raise TypeError_("Assignment type mismatch")

    # control flow
    def visit_if_stmt(self, n: Tree):
        if self._walk(n.children[0]) != "boolean":
            raise TypeError_("If-condition must be boolean")
        self._walk(n.children[1])
        if len(n.children) == 3: self._walk(n.children[2])

    def visit_while_stmt(self, n: Tree):
        if self._walk(n.children[0]) != "boolean":
            raise TypeError_("While-condition must be boolean")
        self._walk(n.children[1])

    def visit_return_stmt(self, n: Tree):
        if self._current_ret is None:
            raise StructureError("return outside function")
        expr_t = self._walk(n.children[0])
        if expr_t not in {self._current_ret, "noType"}:
            raise TypeError_("Return type mismatch")

    # expression statement
    def visit_expr_stmt(self, n: Tree):
        prev = self._in_expr_stmt
        self._in_expr_stmt = True
        self._walk(n.children[0])
        self._in_expr_stmt = prev

    # arithmetic expression
    def visit_arit_expr(self, n: Tree):
        left_t = self._walk(n.children[0])
        op_tok: Token = n.children[1] if len(n.children) == 3 else None
        if op_tok is None:
            return left_t
        right_t = self._walk(n.children[2])
        op = op_tok.value
        if op == "+":
            if left_t != right_t or left_t not in self._ARITH:
                raise TypeError_("operands of + must match and be numeric or string")
            return left_t
        if op in {"-", "*", "%"}:
            if left_t != right_t or left_t not in self._NUM:
                raise TypeError_(f"operands of {op} must both be integer or decimal")
            return left_t
        if op == "/":
            if left_t != right_t or left_t not in self._NUM:
                raise TypeError_("operands of / must both be integer or decimal")
            return "decimal"
        raise StructureError(f"unknown operator {op}")

    # comparison
    def visit_compare_expr(self, n: Tree):
        l_t = self._walk(n.children[0])
        op = n.children[1].value
        r_t = self._walk(n.children[2])
        if op in {"==", "!="}:
            if l_t != r_t: raise TypeError_("operands of ==/!= must match")
        else:
            if l_t != r_t or l_t not in self._NUM:
                raise TypeError_(f"operands of {op} must both be integer or decimal")
        return "boolean"

    # logical and/or
    def visit_logical_expr(self, n: Tree):
        for i in range(0, len(n.children), 2):
            if self._walk(n.children[i]) != "boolean":
                raise TypeError_("logical operands must be boolean")
        return "boolean"

    # array literal
    def visit_array_literal(self, n: Tree):
        if not n.children:
            raise TypeError_("empty array literal")
        elems = [self._walk(c) for c in n.children[0].children if not (isinstance(c, Token) and c.value == ",")]
        if any(t != elems[0] for t in elems):
            raise TypeError_("array elements must share type")
        return elems[0] + "[]"

    # postfix (calls / indexing)
    def visit_postfix_expr(self, n: Tree):
        primary = n.children[0]
        id_tok: Token | None = primary if isinstance(primary, Token) and primary.type == "ID" else None
        cur_t: str | None = None
        for suf in n.children[1:]:
            if suf.data == "call_suffix":
                if id_tok is None:
                    raise StructureError("function call must target identifier")
                sig = self._funcs.get(id_tok.value)
                if sig is None:
                    raise ScopeError(f"call to undefined function '{id_tok.value}'")
                raw_args = suf.children[0].children if suf.children else []
                arg_nodes = [c for c in raw_args if not (isinstance(c, Token) and c.value == ",")]
                arg_types = [self._walk(a) for a in arg_nodes]
                if len(arg_types) != len(sig.params):
                    raise StructureError(f"wrong number of arguments in call to '{id_tok.value}'")
                for a, expected in zip(arg_types, sig.params):
                    if a not in {expected, "noType"}:
                        raise TypeError_("argument type mismatch")
                cur_t, id_tok = sig.ret, None
            elif suf.data == "array_access_suffix":
                cur_t = self._walk(primary) if cur_t is None else cur_t
                if not cur_t.endswith("[]"):
                    raise TypeError_("indexing non-array value")
                if self._walk(suf.children[0]) != "integer":
                    raise TypeError_("array index must be integer")
                cur_t = cur_t[:-2]
            else:
                raise StructureError("unexpected postfix suffix")
        if cur_t is None:
            cur_t = self._walk(primary)
        if cur_t == "noType" and not self._in_expr_stmt:
            raise TypeError_("void value used in expression")
        return cur_t

    # input lit
    def visit_input_expr(self, _): return "noType"

    # helpers
    def _check_case(self, name: str):
        if self._case_style == "camelCase":
            if "_" in name or not name[0].islower(): raise CaseError(f"'{name}' not camelCase")
        else:
            if any(c.isupper() for c in name): raise CaseError(f"'{name}' not snake_case")

    def _shadow_check(self, name: str):
        if name in self._vars: raise ScopeError(f"shadowing '{name}'")

    def _is_input_expr(self, node: Tree | Token | None) -> bool:
        return isinstance(node, Tree) and node.data == "input_expr"

    # global checks
    def _post_checks(self):
        if not self._saw_syntax: raise StructureError("missing syntax header")
        if not self._func_order or self._func_order[-1] != "main" or self._func_order.count("main") != 1:
            raise StructureError("'main' must be last function")

    # single-return-per-branch
    def _check_single_return(self, block: Tree):
        if block.data != "block": return
        if sum(1 for c in block.children if isinstance(c, Tree) and c.data == "return_stmt") > 1:
            raise StructureError("Multiple returns in same branch")
        for c in block.children:
            if not isinstance(c, Tree): continue
            if c.data == "if_stmt":
                self._check_single_return(c.children[1])
                if len(c.children) == 3: self._check_single_return(c.children[2])
            elif c.data == "while_stmt":
                self._check_single_return(c.children[1])
            elif c.data == "block":
                self._check_single_return(c)

    # full-path return check
    def _body_guarantees_return(self, node: Tree) -> bool:
        if node.data == "return_stmt": return True
        if node.data == "block":
            for st in node.children:
                if isinstance(st, Tree) and self._body_guarantees_return(st): return True
            return False
        if node.data == "if_stmt":
            then_ok = self._body_guarantees_return(node.children[1])
            else_ok = False
            if len(node.children) == 3: else_ok = self._body_guarantees_return(node.children[2])
            return then_ok and else_ok
        return False