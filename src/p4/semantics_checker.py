from dataclasses import dataclass, field  # Lightweight record for function metadata
from collections import ChainMap  # Nested, write-through symbol tables
from typing import List, Dict, Any  # Static typing helpers
from lark import Tree, Token  # AST node and token classes from Lark

def location(node):
    # unified access to the first character position of a Tree/Token
    if isinstance(node, Token):
        return node.line, node.column
    if hasattr(node, "meta") and node.meta:  # lark Tree
        return node.meta.line, node.meta.column
    return None, None  # fallback when location unavailable

# error hierarchy
@dataclass
class StaticError(Exception):
    msg: str
    line: int | None = None
    column: int | None = None
    ctx: Dict[str, Any] = field(default_factory=dict)

    def __str__(self):  # compact, grep‑friendly rendering
        head = f"[line {self.line}]" if self.line is not None else ""
        parts = [head, self.msg]
        for k, v in self.ctx.items():
            parts.append(f"{k}={v}")
        return " ".join(p for p in parts if p)

class TypeError_(StaticError): pass
class ScopeError(StaticError): pass
class CaseError(StaticError): pass
class StructureError(StaticError): pass

# helper dataclass
@dataclass
class FunctionSig:
    parameters: List[str]  # Formal parameter types
    return_type: str  # Declared return type
    body: Tree  # AST subtree of the function body

# static semantics checker
class SemanticsChecker:
    _NUM = {"integer", "decimal"}  # Numeric types allowed in arithmetic
    _ARITH = _NUM | {"string"}  # Types that support '+'

    def __init__(self) -> None:
        self.variable_map: ChainMap[str, str] = ChainMap()  # Stack of lexical scopes
        self.function_map: Dict[str, FunctionSig] = {}  # Registry of all functions
        self.function_defs: Dict[str, Token] = {}  # first definition token per function
        self.current_return_type: str | None = None  # Expected return type in the current function
        self.case_style: str = "camelCase"  # Active identifier style, set by syntax header
        self.function_order: list[str] = []  # Definition order, used to enforce 'main' last
        self.in_expr_stmt: bool = False  # Suppresses "void value" error in expression statements
        self.seen_returns: list[str] = []

    def error(self, exc_type, msg, node, **ctx):
        line, col = location(node)
        raise exc_type(msg, line=line, column=col, ctx=ctx)

    # main entry
    def run(self, tree: Tree) -> None:
        self.visit(tree)
        self.post_checks()  # Global invariants checked after full walk

    # generic walker
    def visit(self, node):
        if isinstance(node, Tree):
            data = node.data
            method_name = f'visit_{data}'
            method = getattr(self, method_name, self.default)
            return method(node)  # Dispatch to dedicated visitor or default
        elif isinstance(node, Token):
            return self.visit_token(node)
        return None  # Ignore anything else (should not happen)

    def default(self, node):
        for child in node.children:  # Depth-first traversal for productions without a custom visitor
            self.visit(child)

    # token handling
    def visit_token(self, token: Token):
        # Constant literals map directly to primitive types
        if token.type == "INT":     return "integer"
        if token.type == "FLOAT":   return "decimal"
        if token.type == "BOOLEAN": return "boolean"
        if token.type == "STRING":  return "string"
        if token.type == "ID":  # Identifier lookup must respect scope
            if token.value not in self.variable_map:
                self.error(ScopeError, "Undeclared identifier", token, identifier=token.value)
                return self.variable_map[token.value]
        return None  # Commas, brackets, etc. are ignored here

    # syntax header
    def visit_syntax(self, node):
        case = node.children[1].value
        self.case_style = case

    # start symbol
    def visit_start(self, node):
        for child in node.children:
            self.visit(child)

    # functions
    def visit_function_definition(self, node):

        return_type = self.get_base_type(node.children, 0)
        name_token: Token = node.children[1]
        function_name = name_token.value
        parameters_node = None  # look for a child node representing parameter declarations
        for child in node.children:
            if isinstance(child, Tree) and child.data == "params":
                parameters_node = child  # found the params subtree
                break  # stop once we've located it
        body = node.children[-1]

        if function_name in self.function_map:
            if function_name in self.function_map:
                prev_line, _ = location(self.function_defs[function_name])
                self.error(ScopeError, "Function already defined", name_token, identifier=function_name, first_definition=prev_line)
        self.function_order.append(function_name)

        # Collect parameter names and types with case- and shadow-checking
        parameter_names, parameter_types = [], []
        if parameters_node:
            for parameters in parameters_node.children:
                parameter_type = parameters.children[0].value
                parameter_id_token: Token = parameters.children[1]
                parameter_id = parameters.children[1].value
                self.check_case(parameter_id_token)
                self.shadow_check(parameter_id_token)
                parameter_names.append(parameter_id)
                parameter_types.append(parameter_type)

        self.function_map[function_name] = FunctionSig(parameter_types, return_type, body)
        self.function_defs[function_name] = name_token  # remember where it was first defined

        # Save outer context, then push new scope for parameters
        outer_vars = self.variable_map
        outer_return_type = self.current_return_type

        self.variable_map = ChainMap(dict(zip(parameter_names, parameter_types)))
        self.current_return_type = return_type
        self.seen_returns = []
        self.visit(body)

        if self.seen_returns:  # no returns for noType functions
            inferred = self.seen_returns[0]
            if all(t == inferred for t in self.seen_returns):
                # replace the published type with the more specific one
                self.function_map[function_name].return_type = inferred

        # Non-void functions must guarantee a return on every path
        if return_type != "noType" and not self.body_guarantees_return(body):
            self.error(StructureError, "Function may exit without returning a value", name_token, function=function_name, expected_type=return_type)

        # Restore outer context
        self.variable_map = outer_vars
        self.current_return_type = outer_return_type

        self.check_single_return(body)  # Enforce at most one return per branch

    # blocks
    def visit_block(self, node: Tree):
        # Sequential walk; nothing special aside from nesting handled by scopes elsewhere
        for st in node.children:
            self.visit(st)

    # variable declarations
    def visit_declaration_stmt(self, node):
        base = node.children[0].value
        name_token: Token = node.children[1]
        name = name_token.value
        sizes, idx = self.collect_sizes(node.children, 2)

        self.check_case(name_token)
        self.shadow_check(name_token)

        declared_type = base + "[]" * len(sizes)

        right_hand_side_node = None
        if idx < len(node.children):
            child = node.children[idx]
            right_hand_side_node = node.children[idx + 1] if isinstance(child, Token) and child.value == "=" else child
            if isinstance(right_hand_side_node, list):
                right_hand_side_node = right_hand_side_node[0] if right_hand_side_node else None

        if right_hand_side_node is not None:
            right_hand_side_type = self.visit(right_hand_side_node)
            if right_hand_side_type == "noType" and not self.is_input_expr(right_hand_side_node):
                self.error(TypeError_, "Cannot initialise with value of noType", right_hand_side_node, variable=name)
            if right_hand_side_type != declared_type and right_hand_side_type != "noType":
                self.error(TypeError_, "Initializer type mismatch", right_hand_side_node, variable=name, expected=declared_type, actual=right_hand_side_type)
            if sizes and isinstance(right_hand_side_node, Tree) and right_hand_side_node.data == "array_literal":
                literal_elems = [
                    elem for elem in right_hand_side_node.children[0].children
                    if not (isinstance(elem, Token) and elem.value == ",")
                ]
                if len(literal_elems) != sizes[0]:
                    self.error(TypeError_, "Initializer size mismatch", right_hand_side_node, ariable=name, expected_size=sizes[0], actual_size=len(literal_elems))

        self.variable_map[name] = declared_type

    # assignments
    def visit_assignment_stmt(self, node):
        left_value = node.children[0]
        right_hand_side_node = node.children[-1]

        # identifier being assigned to
        name_token: Token = left_value.children[0]
        name = name_token.value
        if name not in self.variable_map:
            self.error(ScopeError, "Variable not declared", name_token, identifier=name)


        full_type = self.variable_map[name]
        declared_dims = full_type.count("[]")
        element_base = full_type.rstrip("[]")
        sizes = None

        # collect every indexing suffix
        indices = [suf for suf in left_value.children[1:] if
                   isinstance(suf, Tree) and suf.data == "array_access_suffix"]

        # basic type-check on each index expression and optional const-bound check
        for dim, suf in enumerate(indices):
            idx_node = suf.children[0]
            if self.visit(idx_node) != "integer":
                self.error(TypeError_, "Array index must be integer", idx_node, index_value=idx_node.value)

            # constant-bound check
            if sizes and sizes[dim] is not None \
                    and isinstance(idx_node, Token) and idx_node.type == "INT" \
                    and int(idx_node) >= sizes[dim]:
                self.error(TypeError_, "Index out of bounds at compile time", idx_node, index_value=idx_node.value)

        # too many indices?
        if len(indices) > declared_dims:
            self.error(TypeError_, "Too many indices for array", name_token, identifier=name)

        right_hand_side_type = self.visit(right_hand_side_node)
        if right_hand_side_type == "noType" and not self.is_input_expr(right_hand_side_node):
            self.error(TypeError_, "Cannot assign value of noType", right_hand_side_type, variable=name)

        # determine the expected type after applying the indices
        remaining_dims = declared_dims - len(indices)
        expected_type = (
            element_base if remaining_dims == 0
            else element_base + "[]" * remaining_dims
        )

        if right_hand_side_type not in {expected_type, "noType"}:
            self.error(TypeError_, "Assignment type mismatch", right_hand_side_node, variable=name, expected=expected_type, actual=right_hand_side_type)

    # control flow
    def visit_if_stmt(self, node):
        condition_node = node.children[0]
        if self.visit(condition_node) != "boolean":
            self.error(TypeError_, "If‑condition must be boolean", condition_node)
        self.visit(node.children[1])  # then branch
        if len(node.children) == 3:
            self.visit(node.children[2])  # else branch

    def visit_while_stmt(self, node):
        condition_node = node.children[0]
        if self.visit(condition_node) != "boolean":
            self.error(TypeError_, "While‑condition must be boolean", condition_node)
        self.visit(node.children[1])

    def visit_return_stmt(self, node):
        if self.current_return_type is None:
            self.error(StructureError, "return outside function", node)

        actual = self.visit(node.children[0])
        if not self.compatible(actual, self.current_return_type):
            self.error(TypeError_, "Return type mismatch", node.children[0], expected=self.current_return_type, actual=actual)
        self.seen_returns.append(actual)

    # expression statement
    def visit_expr_stmt(self, node):
        previous = self.in_expr_stmt
        self.in_expr_stmt = True  # Suppress "void value" error for RHS 'noType'
        self.visit(node.children[0])
        self.in_expr_stmt = previous

    # arithmetic expression
    def visit_arit_expr(self, node):
        left_type = self.visit(node.children[0])
        operator_token: Token = node.children[1] if len(node.children) == 3 else None
        if operator_token is None:  # Single operand (propagates type)
            return left_type
        right_type = self.visit(node.children[2])
        operator = operator_token.value

        # '+' supports string concatenation; others require numeric
        if operator == "+":
            if left_type != right_type or left_type not in self._ARITH:
                self.error(TypeError_, "operands of + must match and be numeric or string", operator_token, left=left_type, right=right_type)
            return left_type
        if operator in {"-", "*", "%"}:
            if left_type != right_type or left_type not in self._NUM:
                self.error(TypeError_, f"operands of {operator} must both be integer or decimal", operator_token, left=left_type, right=right_type)
                return left_type
        if operator == "/":
            if left_type != right_type or left_type not in self._NUM:
                self.error(TypeError_, "operands of / must both be integer or decimal", operator_token, left=left_type, right=right_type)
            return "decimal"  # Division always yields decimal
        self.error(StructureError, "unknown operator", operator_token, operator=operator)

    # comparison
    def visit_compare_expr(self, node):
        left_type = self.visit(node.children[0])
        operator_token: Token = node.children[1]
        operator = operator_token.value
        right_type = self.visit(node.children[2])
        if operator in {"==", "!="}:  # Equality works for any matching types
            if left_type != right_type:
                self.error(TypeError_, "operands of ==/!= must match", operator_token, left=left_type, right=right_type)
        else:  # <, <=, >, >= restricted to numbers
            if left_type != right_type or left_type not in self._NUM:
                self.error(TypeError_, f"operands of {operator} must both be integer or decimal", operator_token, left=left_type, right=right_type)
        return "boolean"

    # logical and/or
    def visit_logical_expr(self, node):
        # Children alternate operand, operator, operand, ...
        for i in range(0, len(node.children), 2):
            type = self.visit(node.children[i])
            if self.visit(node.children[i]) != "boolean":
                self.error(TypeError_, "logical operands must be boolean", node.children[i], actual=type)
        return "boolean"

    # array literal
    def visit_array_literal(self, node):
        if not node.children:
            self.error(TypeError_, "Array literal cannot be empty", node)
        element_types = []
        for element_node in node.children[0].children:
            if isinstance(element_node, Token) and element_node.value == ",":
                continue
            element_type = self.visit(element_node)
            element_types.append(element_type)
        if any(current_type != element_types[0] for current_type in element_types):
            mismatch_index = next(i for i, t in enumerate(element_types) if t != element_types[0])
            self.error(TypeError_, "All array elements must have the same type", node.children[0].children[mismatch_index], array_type=element_types[0], wrong_type=element_types[mismatch_index], index=mismatch_index)
        return element_types[0] + "[]"

    # postfix (function call, array indexing)
    def visit_postfix_expr(self, node):
        primary = node.children[0]
        id_token: Token | None = primary if isinstance(primary, Token) and primary.type == "ID" else None
        current_type: str | None = None  # Tracks the running type as suffixes are processed

        for suf in node.children[1:]:
            if suf.data == "call_suffix":
                # First suffix can only be applied to an identifier
                if id_token is None:
                    self.error(StructureError, "function call must target identifier", suf)
                signature = self.function_map.get(id_token.value)
                if signature is None:
                    self.error(ScopeError, "call to undefined function", id_token, identifier=id_token.value)

                # Parse argument list, skipping comma tokens
                raw_arguments = suf.children[0].children if suf.children else []
                argument_nodes = []  # collect actual argument nodes, skipping commas
                for node in raw_arguments:
                    if isinstance(node, Token) and node.value == ",":
                        continue  # ignore comma separators
                    argument_nodes.append(node)
                argument_types = [self.visit(a) for a in argument_nodes]

                if len(argument_types) != len(signature.parameters):
                    self.error(StructureError, "wrong number of arguments", suf, identifier=id_token.value, expected=len(signature.parameters), actual=len(argument_types))
                for argument_type, expected in zip(argument_types, signature.parameters):
                    if argument_type not in {expected, "noType"}:
                        self.error(TypeError_, "argument type mismatch", argument_nodes[argument_types.index(argument_type)], expected=expected, actual=argument_type)

                current_type = signature.return_type
                id_token = None  # Type post-call; clear id_token
            elif suf.data == "array_access_suffix":
                # Resolve base type for the first indexing occurrence
                current_type = self.visit(primary) if current_type is None else current_type
                index_node = suf.children[0]
                if not current_type.endswith("[]"):
                    self.error(TypeError_, "indexing non‑array value", index_node)
                if self.visit(suf.children[0]) != "integer":
                    self.error(TypeError_, "array index must be integer", index_node, index_value=index_node.value)
                current_type = current_type[:-2]  # Drop one dimension

        if current_type is None:  # No suffixes: just primary expression
            current_type = self.visit(primary)

        return current_type

    # input literal
    def visit_input_expr(self, _):
        return "noType"  # Represents read-from-stdin; has no concrete type

    # helpers below
    # identifier case enforcement
    def check_case(self, token: Token):
        name = token.value
        if self.case_style == "camelCase":
            if "_" in name or not name[0].islower():
                self.error(CaseError, "not camelCase", token, identifier=name)
        else:  # snake_case
            if any(c.isupper() for c in name):
                self.error(CaseError, "not snake_case", token, identifier=name)

    def shadow_check(self, token: Token):
        name = token.value
        if name in self.variable_map:
            self.error(ScopeError, "shadowing", token, identifier=name)

    def is_input_expr(self, node: Tree | Token | None) -> bool:
        return isinstance(node, Tree) and node.data == "input_expr"

    # global checks
    def post_checks(self):
        # Exactly one main, and it must be last
        has_main = self.function_order.count("main") == 1  # check there is exactly one 'main'
        is_last = bool(self.function_order) and self.function_order[-1] == "main"  # check 'main' is the last element
        if not has_main or not is_last:
            raise StructureError("'main' must be last function")

    # single-return-per-branch
    def check_single_return(self, block: Tree):
        # Enforce at most one return per linear execution branch (no early exits after return)
        if block.data != "block":
            return
        return_count = 0  # count return statements in this block
        for child in block.children:
            if isinstance(child, Tree) and child.data == "return_stmt":
                return_count += 1  # increment for each return statement found
        if return_count > 1:
            self.error(StructureError, "Multiple returns in same branch", return_count[1])
        for c in block.children:
            if not isinstance(c, Tree):
                continue
            if c.data == "if_stmt":
                # Check both branches recursively
                self.check_single_return(c.children[1])
                if len(c.children) == 3:
                    self.check_single_return(c.children[2])
            elif c.data == "while_stmt":
                self.check_single_return(c.children[1])
            elif c.data == "block":
                self.check_single_return(c)

    # full-path return check
    def body_guarantees_return(self, node: Tree) -> bool:
        # True if every possible execution path ends in a return_stmt
        if node.data == "return_stmt":
            return True
        if node.data == "block":
            for statement in node.children:
                if isinstance(statement, Tree) and self.body_guarantees_return(statement):
                    return True  # First guaranteed-return statement exits the block
            return False
        if node.data == "if_stmt":
            then_ok = self.body_guarantees_return(node.children[1])
            else_ok = False
            if len(node.children) == 3:
                else_ok = self.body_guarantees_return(node.children[2])
            # Both branches must guarantee return
            return then_ok and else_ok
        return False  # while, expressions, etc. do not guarantee return

    def collect_sizes(self, children, start):
        sizes = []
        i = start
        while i < len(children) \
                and isinstance(children[i], Tree) \
                and children[i].data == "array_suffix":

            token = children[i].children[0]
            if token.type == "INT":
                sizes.append(int(token))
            else:
                sizes.append(None)
            i += 1
        return sizes, i

    def get_base_type(self, children, idx0):
        return children[idx0].value

    def compatible(self, actual: str, expected: str) -> bool:
        if expected == "noType":
            return True
        if actual == expected:
            return True
        while actual.endswith("[]"):
            actual = actual[:-2]
            if actual == expected:
                return True
        return False