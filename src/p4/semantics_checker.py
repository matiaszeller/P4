from __future__ import annotations

"""Semantic analysis for the ROLEX language.
This tree-walk checker verifies
• structural rules (syntax header, program layout, single-main, single-return …)
• static / lexical scoping with no shadowing
• strict static typing incl. arrays, function calls and control-flow guards
The module raises subclasses of ``StaticError`` on any violation so the driver can
stop before interpretation.
"""

# ── error hierarchy ────────────────────────────────────────────────────────────
class StaticError(Exception):
    """Base-class for all static (compile-time) errors."""


class TypeError_(StaticError):
    pass


class ScopeError(StaticError):
    pass
0

class CaseError(StaticError):
    pass


class StructureError(StaticError):
    pass


# ── helpers / data-structures ─────────────────────────────────────────────────
from dataclasses import dataclass
from collections import ChainMap
from typing import List, Dict, Any

from lark import Tree, Token


@dataclass
class FunctionSig:
    """Signature of a function gathered from its definition."""

    params: List[str]  # parameter types, order preserved
    ret: str          # return type
    body: Tree        # body "block" tree (needed for single-return check)


# ── main checker class ────────────────────────────────────────────────────────
class SemanticsChecker:
    """Walks a Lark parse-tree and validates ROLEX static semantics."""

    # primitive scalar types; arrays are noted as e.g. "integer[]", "decimal[][]" …
    PRIMITIVES = {"boolean", "integer", "decimal", "string", "noType"}
    _NUM = {"integer", "decimal"}
    _ARITH = _NUM | {"string"}

    # --------------------------------------------------------------------- init
    def __init__(self) -> None:
        # ChainMap behaves like a stack of "variable → type" tables.
        self._vars: ChainMap[str, str] = ChainMap()
        # Function name → signature (collect once and reuse for call-checking).
        self._funcs: Dict[str, FunctionSig] = {}
        # Return-type expected for the *current* function (None when in global).
        self._current_ret: str | None = None
        # Naming-case selected in the syntax header.
        self._case_style: str = "camelCase"
        # Whether we are currently traversing the global (top-level) scope.
        self._in_global: bool = True
        # Keeps definition order so we can later assert that "main" is last.
        self._func_order: List[str] = []
        # Flags that we encountered exactly one valid syntax header.
        self._saw_syntax: bool = False
        self._language: str | None = None  # "EN" or "DK" – not used yet

    # ---------------------------------------------------------------- public
    def run(self, tree: Tree) -> None:
        """Entry-point – walk whole parse-tree then run final global checks."""
        self._walk(tree)
        self._post_checks()

    # ---------------------------------------------------------------- walkers
    def _walk(self, node: Tree | Token):
        """Dispatch helper calling the appropriate visit_* method."""
        if isinstance(node, Token):
            return self._visit_token(node)
        getattr(self, f"visit_{node.data}", self._default)(node)

    def _default(self, node: Tree):
        for ch in node.children:
            self._walk(ch)

    # .............................. literals / identifier lookup ..........
    def _visit_token(self, tk: Token):
        ttype = tk.type
        if ttype == "INT":
            return "integer"
        if ttype == "decimal":
            return "decimal"
        if ttype == "BOOLEAN":
            return "boolean"
        if ttype == "string":
            return "string"
        if ttype == "ID":
            name = tk.value
            if name not in self._vars:
                raise ScopeError(
                    f"Undeclared identifier '{name}' at {tk.line}:{tk.column}")
            return self._vars[name]
        return None  # NEWLINE, punctuation … – ignored for type purposes

    # .............................. syntax header ..........................
    def visit_syntax(self, n: Tree):
        if self._saw_syntax:
            raise StructureError("Duplicate syntax header")
        lang_tok: Token = n.children[0]
        case_tok: Token = n.children[2]
        lang = lang_tok.value
        case_style = case_tok.value
        if lang not in {"EN", "DK"}:
            raise StructureError(f"Unsupported language '{lang}' – expected EN or DK")
        if case_style not in {"camelCase", "snake_case"}:
            raise StructureError(
                f"Unsupported case style '{case_style}' – expected camelCase or snake_case")
        self._language, self._case_style, self._saw_syntax = lang, case_style, True

    # .............................. program root ..........................
    def visit_start(self, n: Tree):
        for ch in n.children:
            self._walk(ch)
            if isinstance(ch, Tree) and ch.data not in {"syntax", "function_definition"}:
                raise StructureError("Only function definitions allowed at top level")

    # .............................. function definition ....................
    # ──────────────────────────────────────────────────────────────────────
    #   function_definition  (handles header token, params, body, etc.)
    # ──────────────────────────────────────────────────────────────────────
    def visit_function_definition(self, n: Tree):
        # NEW: generic grammar puts a leading FUNCTION token at index 0
        if isinstance(n.children[0], Token) and n.children[0].type == "FUNCTION":
            n.children.pop(0)  # discard the keyword token

        if not self._in_global:
            raise StructureError("Nested functions not allowed")

        # After pop: children[0]=TYPE, children[1]=ID, …, children[-1]=block
        ret_t = n.children[0].value  # declared return TYPE
        fname = n.children[1].value  # function name (ID token)

        # Optional params node
        params_node = (
            n.children[2]
            if len(n.children) > 2
               and isinstance(n.children[2], Tree)
               and n.children[2].data == "params"
            else None
        )
        body: Tree = n.children[-1]

        if fname in self._funcs:
            raise ScopeError(f"Function '{fname}' already defined")
        self._func_order.append(fname)

        # ── collect parameter names / types ───────────────────────────────
        pids: list[str] = []
        ptypes: list[str] = []
        if params_node:
            for p in params_node.children:  # each param node
                ptype = p.children[0].value
                pid = p.children[1].value
                self._check_case(pid)
                self._shadow_check(pid)
                pids.append(pid)
                ptypes.append(ptype)

        # ── register signature (allows recursion) ─────────────────────────
        self._funcs[fname] = FunctionSig(ptypes, ret_t, body)

        # ── new lexical scope with only parameters ────────────────────────
        prev_vars, prev_ret, prev_flag = self._vars, self._current_ret, self._in_global
        self._vars = ChainMap({pid: ptype for pid, ptype in zip(pids, ptypes)})
        self._current_ret, self._in_global = ret_t, False

        # ── walk body ─────────────────────────────────────────────────────
        self._walk(body)

        # ── restore outer scope ───────────────────────────────────────────
        self._vars, self._current_ret, self._in_global = prev_vars, prev_ret, prev_flag

        # ── enforce single-return-per-branch rule ─────────────────────────
        self._check_single_return(body)

    # .............................. block / lexical scope .................
    def visit_block(self, n: Tree):
        prev = self._vars
        self._vars = self._vars.new_child()
        for stmt in n.children:
            self._walk(stmt)
        self._vars = prev

    # .............................. declarations / assignments ...........
    def visit_declaration_stmt(self, n: Tree):
        # Structure: TYPE ID array_suffix* [ '=' expr ]
        base_type = n.children[0].value
        name = n.children[1].value
        self._check_case(name)
        self._shadow_check(name)

        # Count array suffixes -------------------------------------------
        idx = 2
        dims = 0
        while idx < len(n.children) and isinstance(n.children[idx], Tree) and n.children[idx].data == "array_suffix":
            dims += 1
            idx += 1
        declared_type = base_type + "[]" * dims

        # Optional initializer -------------------------------------------
        expr_t: str | None = None
        if idx < len(n.children) and isinstance(n.children[idx], Token) and n.children[idx].value == "=":
            expr_t = self._walk(n.children[idx + 1])

        if expr_t is not None and expr_t != declared_type and expr_t != "noType":
            raise TypeError_(f"Type mismatch in declaration of '{name}' – expected {declared_type}, got {expr_t}")

        self._vars[name] = declared_type

    # ----------------------------------------------------------------- assignment
    def visit_assignment_stmt(self, n: Tree):
        # Structure: lvalue '=' expr
        lval: Tree = n.children[0]
        rhs_expr: Tree = n.children[2] if isinstance(n.children[1], Token) else n.children[1]

        name = lval.children[0].value  # base identifier token
        if name not in self._vars:
            raise ScopeError(f"Variable '{name}' not declared")

        var_type = self._vars[name]
        # Determine if we have array indices (array_access_suffix children)
        suffixes = [c for c in lval.children[1:] if isinstance(c, Tree) and c.data == "array_access_suffix"]
        idx_count = len(suffixes)

        # Validate indices -------------------------------------------------
        for suf in suffixes:
            idx_type = self._walk(suf.children[0])
            if idx_type != "integer":
                raise TypeError_("Array index must be integer")

        if idx_count == 0:
            # Plain variable assignment
            rhs_type = self._walk(rhs_expr)
            if rhs_type != var_type and rhs_type != "noType":
                raise TypeError_("Assignment type mismatch")
            return

        # Array-element assignment ---------------------------------------
        if var_type.count("[]") < idx_count:
            raise TypeError_("Too many indices for array")
        elem_type = var_type[:-2 * idx_count]
        rhs_type = self._walk(rhs_expr)
        if rhs_type != elem_type and rhs_type != "noType":
            raise TypeError_(
                f"Assignment type mismatch – assigning {rhs_type} to {elem_type} array element")

    # .............................. control-flow .........................
    def visit_if_stmt(self, n: Tree):
        if self._walk(n.children[0]) != "boolean":
            raise TypeError_("If condition must be boolean")
        self._walk(n.children[1])
        if len(n.children) == 3:
            self._walk(n.children[2])

    def visit_while_stmt(self, n: Tree):
        if self._walk(n.children[0]) != "boolean":
            raise TypeError_("While condition must be boolean")
        self._walk(n.children[1])

    def visit_return_stmt(self, n: Tree):
        if self._current_ret is None:
            raise StructureError("Return outside function")
        if self._walk(n.children[0]) != self._current_ret and self._walk(n.children[0]) != "noType":
            raise TypeError_("Return type mismatch")

    # .............................. expressions ..........................
    def visit_add_expr(self, n: Tree):
        t = self._walk(n.children[0])
        for i in range(2, len(n.children), 2):
            if self._walk(n.children[i]) != t or t not in self._ARITH:
                raise TypeError_("Add/Sub require same arithmetic type")
        return t

    def visit_mul_expr(self, n: Tree):
        t = self._walk(n.children[0])
        for i in range(2, len(n.children), 2):
            if self._walk(n.children[i]) != t or t not in self._NUM:
                raise TypeError_("Mul/Div/Mod require same numeric type")
        return t

    def visit_equality_expr(self, n: Tree):
        if self._walk(n.children[0]) != self._walk(n.children[2]):
            raise TypeError_("Equality operands must match")
        return "boolean"

    def visit_relational_expr(self, n: Tree):
        t1, t2 = self._walk(n.children[0]), self._walk(n.children[2])
        if t1 != t2 or t1 not in self._NUM:
            raise TypeError_("Relational operands must be same numeric type")
        return "boolean"

    def visit_and_expr(self, n: Tree):
        for ch in n.children:
            if self._walk(ch) != "boolean":
                raise TypeError_("'and' expects booleans")
        return "boolean"

    def visit_or_expr(self, n: Tree):
        for ch in n.children:
            if self._walk(ch) != "boolean":
                raise TypeError_("'or' expects booleans")
        return "boolean"

    # ----------------------------- array literal -------------------------
    def visit_array_literal(self, n: Tree):
        if not n.children:
            raise TypeError_("Cannot infer type of empty array literal")
        elements_node = n.children[0]
        el_types: List[str] = [self._walk(elements_node.children[i]) for i in range(0, len(elements_node.children), 2)]
        first_type = el_types[0]
        if any(t != first_type for t in el_types[1:]):
            raise TypeError_("Array literal elements must have the same type")
        return first_type + "[]"

    # ----------------------------- postfix chain (calls / indexing) ------
    def visit_postfix_expr(self, n: Tree):
        # First child is always the primary expression
        primary = n.children[0]
        current_type = self._walk(primary)
        primary_id_token: Token | None = primary if isinstance(primary, Token) and primary.type == "ID" else None

        for suf in n.children[1:]:
            if suf.data == "call_suffix":
                if primary_id_token is None:
                    raise StructureError("Function call must target identifier")
                fname = primary_id_token.value
                sig = self._funcs.get(fname)
                if sig is None:
                    raise ScopeError(f"Call to undefined function '{fname}'")
                args_node = suf.children[0] if suf.children else None
                arg_types = [self._walk(e) for e in (args_node.children if args_node else [])]
                if len(arg_types) != len(sig.params):
                    raise StructureError(f"Wrong number of arguments in call to '{fname}'")
                for actual_t, expected_t in zip(arg_types, sig.params):
                    if actual_t != expected_t and actual_t != "noType":
                        raise TypeError_(
                            f"Argument type mismatch in call to '{fname}': expected {expected_t}, got {actual_t}")
                current_type = sig.ret
                # after a call the chain continues on the returned type, but we
                # prevent *another* call on the result (functions are not first-class)
                primary_id_token = None
            elif suf.data == "array_access_suffix":
                if not current_type.endswith("[]"):
                    raise TypeError_("Indexing into non-array value")
                if self._walk(suf.children[0]) != "integer":
                    raise TypeError_("Array index must be integer")
                current_type = current_type[:-2]  # trim one []
            else:
                raise StructureError(f"Unexpected postfix suffix '{suf.data}'")
        return current_type

    # ----------------------------- input expression ----------------------
    def visit_input_expr(self, _n: Tree):
        # Dynamic – accepted at compile-time as noType
        return "noType"

    # .............................. helper checks ........................
    def _check_case(self, name: str):
        if self._case_style == "camelCase":
            if "_" in name or not name[0].islower():
                raise CaseError(f"'{name}' not camelCase")
        else:  # snake_case
            if any(c.isupper() for c in name):
                raise CaseError(f"'{name}' not snake_case")

    def _shadow_check(self, name: str):
        # No variable may redeclare an existing identifier in *any* visible scope
        if name in self._vars:
            raise ScopeError(f"Shadowing/redeclaration of '{name}'")

    # .............................. post (global) checks .................
    def _post_checks(self):
        if not self._saw_syntax:
            raise StructureError("Missing syntax header (Language … / Case …)")
        if (
            not self._func_order
            or self._func_order[-1] != "main"
            or self._func_order.count("main") != 1
        ):
            raise StructureError("'main' must be the single last function")

    # .............................. single-return checker ................
    def _check_single_return(self, block: Tree):
        if block.data != "block":
            return
        # Count top-level returns directly inside this block
        top_returns = sum(
            1 for c in block.children if isinstance(c, Tree) and c.data == "return_stmt"
        )
        if top_returns > 1:
            raise StructureError("Multiple top-level returns in branch")
        # Recurse into nested structures (branches/loops/inner blocks)
        for c in block.children:
            if not isinstance(c, Tree):
                continue
            if c.data == "if_stmt":
                # then-block always at index 1
                self._check_single_return(c.children[1])
                if len(c.children) == 3:  # has else
                    self._check_single_return(c.children[2])
            elif c.data == "while_stmt":
                self._check_single_return(c.children[1])
            elif c.data == "block":
                self._check_single_return(c)