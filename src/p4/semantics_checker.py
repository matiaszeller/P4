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

# main checker
class SemanticsChecker:
    PRIMITIVES = {"boolean", "integer", "decimal", "string", "noType"}
    _NUM = {"integer", "decimal"}
    _ARITH = _NUM | {"string"}

    def __init__(self) -> None:
        self._vars: ChainMap[str, str] = ChainMap()
        self._funcs: Dict[str, FunctionSig] = {}
        self._current_ret: str | None = None
        self._in_global = True
        self._case_style = "camelCase"
        self._func_order: list[str] = []
        self._saw_syntax = False

    # walker helpers
    def run(self, tree: Tree) -> None:
        self._walk(tree)
        self._post_checks()

    def _walk(self, node: Tree | Token):
        if isinstance(node, Token):
            return self._visit_token(node)
        method = getattr(self, f"visit_{node.data}", self._default)
        return method(node)

    def _default(self, n: Tree):
        for ch in n.children:
            self._walk(ch)

    # tokens
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

    # syntax
    def visit_syntax(self, n: Tree):
        if self._saw_syntax:
            raise StructureError("Duplicate syntax header")
        lang, case = n.children[0].value, n.children[1].value
        if lang not in {"EN", "DK"}: raise StructureError("Unsupported language") # Never called as incorrect results in parse error, could be useful if we change this
        if case not in {"camelCase", "snake_case"}: raise StructureError("Unsupported case style") # Never called as incorrect results in parse error, could be useful if we change this
        self._case_style, self._saw_syntax = case, True

    # program root
    def visit_start(self, n: Tree):
        for ch in n.children:
            self._walk(ch)
            if isinstance(ch, Tree) and ch.data not in {"syntax", "function_definition"}:
                raise StructureError("Only function definitions allowed at top level")

    # function definition
    def visit_function_definition(self, n: Tree):
        if not self._in_global:
            raise StructureError("Nested functions not allowed")
        ret_t, fname = n.children[0].value, n.children[1].value
        params_node = next((c for c in n.children if isinstance(c, Tree) and c.data == "params"), None)
        body = n.children[-1]
        if fname in self._funcs:
            raise ScopeError(f"Function '{fname}' already defined")
        self._func_order.append(fname)

        p_names, p_types = [], []
        if params_node:
            for p in params_node.children:
                ptype, pid = p.children[0].value, p.children[1].value
                self._check_case(pid)
                self._shadow_check(pid)
                p_names.append(pid); p_types.append(ptype)

        self._funcs[fname] = FunctionSig(p_types, ret_t, body)

        outer_vars, outer_ret, outer_flag = self._vars, self._current_ret, self._in_global
        self._vars = ChainMap(dict(zip(p_names, p_types)))
        self._current_ret, self._in_global = ret_t, False
        self._walk(body)
        if ret_t != "noType" and not self._body_guarantees_return(body):
            raise StructureError(f"Function '{fname}' may exit without returning a value")
        self._vars, self._current_ret, self._in_global = outer_vars, outer_ret, outer_flag
        self._check_single_return(body)

    # block (no new scope)
    def visit_block(self, n: Tree):
        for stmt in n.children:
            self._walk(stmt)

    # declarations
    def visit_declaration_stmt(self, n: Tree):
        base, name = n.children[0].value, n.children[1].value
        self._check_case(name)
        self._shadow_check(name)

        # array suffix handling
        idx, dims = 2, 0
        while idx < len(n.children) \
                and isinstance(n.children[idx], Tree) \
                and n.children[idx].data == "array_suffix":
            dims += 1
            idx += 1
        declared = base + "[]" * dims

        # look for an initialiser
        rhs_node = None
        if idx < len(n.children):  # something follows the ID
            child = n.children[idx]
            if isinstance(child, Token) and child.value == "=":
                # classic parse: "=" then the expression
                rhs_node = n.children[idx + 1] if idx + 1 < len(n.children) else None
            else:
                # transformed parse: expression directly; unwrap list if necessary
                rhs_node = child[0] if isinstance(child, list) and child else child

        if rhs_node is not None:
            rhs_t = self._walk(rhs_node)
            if rhs_t not in {declared, "noType"}:
                raise TypeError_(f"Initialiser type mismatch for '{name}'")

        # finally bind the variable in the current scope
        self._vars[name] = declared

    # assignment
    def visit_assignment_stmt(self, n: Tree):
        lval, rhs_node = n.children[0], n.children[-1]
        name = lval.children[0].value
        if name not in self._vars:
            raise ScopeError(f"Variable '{name}' not declared")
        var_t = self._vars[name]
        indices = [c for c in lval.children[1:] if c.data == "array_access_suffix"]
        for suf in indices:
            if self._walk(suf.children[0]) != "integer":
                raise TypeError_("Array index must be integer")
        rhs_t = self._walk(rhs_node)
        if indices:
            if var_t.count("[]") < len(indices):
                raise TypeError_("Too many indices for array")
            elem_t = var_t[:-2 * len(indices)]
            if rhs_t not in {elem_t, "noType"}:
                raise TypeError_("Assignment type mismatch")
        else:
            if rhs_t not in {var_t, "noType"}:
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

    # expressions
    def visit_arit_expr(self, n: Tree):
        t0 = self._walk(n.children[0])
        if t0 not in self._ARITH:
            raise TypeError_("Arithmetic requires number/string")
        for i in range(2, len(n.children), 2):
            if self._walk(n.children[i]) != t0:
                raise TypeError_("Mixed-type arithmetic not allowed")
        return t0

    def visit_compare_expr(self, n: Tree):
        left_t, op_tok, right_t = self._walk(n.children[0]), n.children[1], self._walk(n.children[2])
        op = op_tok.value
        if op in {"==", "!="}:
            if left_t != right_t:
                raise TypeError_("Operands of == or != must match")
        else:
            if left_t != right_t or left_t not in self._NUM:
                raise TypeError_("Operands of relational operator must both be integer or decimal")
        return "boolean"

    def visit_logical_expr(self, n: Tree):
        # every operand (even indices) must be boolean
        for i in range(0, len(n.children), 2):
            if self._walk(n.children[i]) != "boolean":
                raise TypeError_("and/or operands must be boolean")
        return "boolean"

    # array literal
    def visit_array_literal(self, n: Tree):
        if not n.children: raise TypeError_("Empty array literal")
        elems = [self._walk(c) for c in n.children[0].children if not (isinstance(c, Token) and c.value == ",")]
        if any(t != elems[0] for t in elems):
            raise TypeError_("Array elements must share type")
        return elems[0] + "[]"

    # postfix (function call / index)
    def visit_postfix_expr(self, n: Tree):
        primary = n.children[0]
        # Determine if this is a function call on an identifier
        id_tok = primary if isinstance(primary, Token) and primary.type == "ID" else None
        cur_t = None
        # Walk through suffixes
        for suf in n.children[1:]:
            if suf.data == "call_suffix":
                # Function call
                if id_tok is None:
                    raise StructureError("Function call must target identifier")
                sig = self._funcs.get(id_tok.value)
                if sig is None:
                    raise ScopeError(f"Call to undefined function '{id_tok.value}'")
                # Gather argument nodes
                raw_args = suf.children[0].children if suf.children else []
                arg_nodes = [c for c in raw_args if not (isinstance(c, Token) and c.value == ",")]
                arg_types = [self._walk(a) for a in arg_nodes]
                # Check argument count
                if len(arg_types) != len(sig.params):
                    raise StructureError(f"Wrong number of arguments in call to '{id_tok.value}'")
                # Check argument types
                for a, e in zip(arg_types, sig.params):
                    if a not in {e, "noType"}:
                        raise TypeError_("Argument type mismatch")
                cur_t = sig.ret
                # After a call, no further calls allowed on same identifier
                id_tok = None
            elif suf.data == "array_access_suffix":
                # Array indexing
                if cur_t is None:
                    # First suffix, primary should be var or array literal
                    cur_t = self._walk(primary)
                if not cur_t.endswith("[]"):
                    raise TypeError_("Indexing non-array")
                if self._walk(suf.children[0]) != "integer":
                    raise TypeError_("Array index must be integer")
                # Strip one array dimension
                cur_t = cur_t[:-2]
            else:
                raise StructureError("Unexpected postfix suffix")
        # If no suffix processed, just primary
        if cur_t is None:
            return self._walk(primary)
        return cur_t

    # input
    def visit_input_expr(self, _): return "noType"

    # helpers
    def _check_case(self, name: str):
        if self._case_style == "camelCase":
            if "_" in name or not name[0].islower():
                raise CaseError(f"'{name}' not camelCase")
        else:
            if any(c.isupper() for c in name):
                raise CaseError(f"'{name}' not snake_case")

    def _shadow_check(self, name: str):
        if name in self._vars:
            raise ScopeError(f"Shadowing '{name}'")

    # global post checks
    def _post_checks(self):
        if not self._saw_syntax:
            raise StructureError("Missing syntax header")
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
                if isinstance(st, Tree) and self._body_guarantees_return(st):
                    return True
            return False
        if node.data == "if_stmt":
            then_ok = self._body_guarantees_return(node.children[1])
            else_ok = False
            if len(node.children) == 3: else_ok = self._body_guarantees_return(node.children[2])
            return then_ok and else_ok
        return False