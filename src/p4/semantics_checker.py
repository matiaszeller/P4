from dataclasses import dataclass  # Lightweight record for function metadata
from collections import ChainMap  # Nested, write-through symbol tables
from typing import List, Dict  # Static typing helpers
from lark import Tree, Token  # AST node and token classes from Lark

# error hierarchy
class StaticError(Exception): pass  # Base class for all static-analysis errors
class TypeError_(StaticError): pass  # Type mismatch or misuse
class ScopeError(StaticError): pass  # Undeclared identifier or variable shadowing
class CaseError(StaticError): pass  # Wrong identifier case style
class StructureError(StaticError): pass  # Violations of language structure rules

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
        self.current_return_type: str | None = None  # Expected return type in the current function
        self.case_style: str = "camelCase"  # Active identifier style, set by syntax header
        self.function_order: list[str] = []  # Definition order, used to enforce 'main' last
        self.in_expr_stmt: bool = False  # Suppresses "void value" error in expression statements
        self.seen_returns: list[str] = []

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

    def default(self, n: Tree):
        for child in n.children:  # Depth-first traversal for productions without a custom visitor
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
                raise ScopeError(f"Undeclared identifier '{token.value}'")
            return self.variable_map[token.value]
        return None  # Commas, brackets, etc. are ignored here

    # syntax header
    def visit_syntax(self, n: Tree):
        case = n.children[1].value
        self.case_style = case

    # start symbol
    def visit_start(self, n: Tree):
        for child in n.children:
            self.visit(child)

    # functions
    def visit_function_definition(self, n: Tree):

        return_type = self.get_base_type(n.children, 0)
        function_name = n.children[1].value
        parameters_node = None  # look for a child node representing parameter declarations
        for child in n.children:
            if isinstance(child, Tree) and child.data == "params":
                parameters_node = child  # found the params subtree
                break  # stop once we've located it
        body = n.children[-1]

        if function_name in self.function_map:
            raise ScopeError(f"Function '{function_name}' already defined")
        self.function_order.append(function_name)

        # Collect parameter names and types with case- and shadow-checking
        parameter_names, parameter_types = [], []
        if parameters_node:
            for parameters in parameters_node.children:
                parameter_type = parameters.children[0].value
                parameter_id = parameters.children[1].value
                self.check_case(parameter_id)
                self.shadow_check(parameter_id)
                parameter_names.append(parameter_id)
                parameter_types.append(parameter_type)

        self.function_map[function_name] = FunctionSig(parameter_types, return_type, body)

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
                raise StructureError(f"Function '{function_name}' may exit without returning a value")

        # Restore outer context
        self.variable_map = outer_vars
        self.current_return_type = outer_return_type

        self.check_single_return(body)  # Enforce at most one return per branch

    # blocks
    def visit_block(self, n: Tree):
        # Sequential walk; nothing special aside from nesting handled by scopes elsewhere
        for st in n.children:
            self.visit(st)

    # variable declarations
    def visit_declaration_stmt(self, n: Tree):
        base = n.children[0].value
        name = n.children[1].value
        sizes, idx = self.collect_sizes(n.children, 2)

        self.check_case(name)
        self.shadow_check(name)

        declared_type = base + "[]" * len(sizes)

        right_hand_side_node = None
        if idx < len(n.children):
            child = n.children[idx]
            right_hand_side_node = n.children[idx + 1] if isinstance(child, Token) and child.value == "=" else child
            if isinstance(right_hand_side_node, list):
                right_hand_side_node = right_hand_side_node[0] if right_hand_side_node else None

        if right_hand_side_node is not None:
            right_hand_side_type = self.visit(right_hand_side_node)
            if right_hand_side_type == "noType" and not self.is_input_expr(right_hand_side_node):
                raise TypeError_("Cannot initialize with value of noType")
            if right_hand_side_type != declared_type and right_hand_side_type != "noType":
                raise TypeError_(f"Initializer type mismatch for '{name}'")
            if sizes and isinstance(right_hand_side_node, Tree) and right_hand_side_node.data == "array_literal":
                literal_elems = [
                    elem for elem in right_hand_side_node.children[0].children
                    if not (isinstance(elem, Token) and elem.value == ",")
                ]
                if len(literal_elems) != sizes[0]:
                    raise TypeError_(f"Initializer size mismatch for '{name}'")

        self.variable_map[name] = declared_type

    # assignments
    def visit_assignment_stmt(self, n: Tree):
        left_value = n.children[0]
        right_hand_side_node = n.children[-1]

        # identifier being assigned to
        name = left_value.children[0].value
        if name not in self.variable_map:
            raise ScopeError(f"Variable '{name}' not declared")

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
                raise TypeError_("Array index must be integer")

            # constant-bound check
            if sizes and sizes[dim] is not None \
                    and isinstance(idx_node, Token) and idx_node.type == "INT" \
                    and int(idx_node) >= sizes[dim]:
                raise TypeError_("Index out of bounds at compile time")

        # too many indices?
        if len(indices) > declared_dims:
            raise TypeError_("Too many indices for array")

        right_hand_side_type = self.visit(right_hand_side_node)
        if right_hand_side_type == "noType" and not self.is_input_expr(right_hand_side_node):
            raise TypeError_("Cannot assign value of noType")

        # determine the expected type after applying the indices
        remaining_dims = declared_dims - len(indices)
        expected_type = (
            element_base if remaining_dims == 0
            else element_base + "[]" * remaining_dims
        )

        if right_hand_side_type not in {expected_type, "noType"}:
            raise TypeError_("Assignment type mismatch")

    # control flow
    def visit_if_stmt(self, n: Tree):
        if self.visit(n.children[0]) != "boolean":
            raise TypeError_("If-condition must be boolean")
        self.visit(n.children[1])  # then branch
        if len(n.children) == 3:
            self.visit(n.children[2])  # else branch

    def visit_while_stmt(self, n: Tree):
        if self.visit(n.children[0]) != "boolean":
            raise TypeError_("While-condition must be boolean")
        self.visit(n.children[1])

    def visit_return_stmt(self, n: Tree):
        if self.current_return_type is None:
            raise StructureError("return outside function")

        actual = self.visit(n.children[0])
        if not self.compatible(actual, self.current_return_type):
            raise TypeError_("Return type mismatch")

        self.seen_returns.append(actual)

    # expression statement
    def visit_expr_stmt(self, n: Tree):
        previous = self.in_expr_stmt
        self.in_expr_stmt = True  # Suppress "void value" error for RHS 'noType'
        self.visit(n.children[0])
        self.in_expr_stmt = previous

    # arithmetic expression
    def visit_arit_expr(self, n: Tree):
        left_type = self.visit(n.children[0])
        operator_token: Token = n.children[1] if len(n.children) == 3 else None
        if operator_token is None:  # Single operand (propagates type)
            return left_type
        right_type = self.visit(n.children[2])
        operator = operator_token.value

        # '+' supports string concatenation; others require numeric
        if operator == "+":
            if left_type != right_type or left_type not in self._ARITH:
                raise TypeError_("operands of + must match and be numeric or string")
            return left_type
        if operator in {"-", "*", "%"}:
            if left_type != right_type or left_type not in self._NUM:
                raise TypeError_(f"operands of {operator} must both be integer or decimal")
            return left_type
        if operator == "/":
            if left_type != right_type or left_type not in self._NUM:
                raise TypeError_("operands of / must both be integer or decimal")
            return "decimal"  # Division always yields decimal
        raise StructureError(f"unknown operator {operator}")

    # comparison
    def visit_compare_expr(self, n: Tree):
        left_type = self.visit(n.children[0])
        operator = n.children[1].value
        right_type = self.visit(n.children[2])
        if operator in {"==", "!="}:  # Equality works for any matching types
            if left_type != right_type:
                raise TypeError_("operands of ==/!= must match")
        else:  # <, <=, >, >= restricted to numbers
            if left_type != right_type or left_type not in self._NUM:
                raise TypeError_(f"operands of {operator} must both be integer or decimal")
        return "boolean"

    # logical and/or
    def visit_logical_expr(self, n: Tree):
        # Children alternate operand, operator, operand, ...
        for i in range(0, len(n.children), 2):
            if self.visit(n.children[i]) != "boolean":
                raise TypeError_("logical operands must be boolean")
        return "boolean"

    # array literal
    def visit_array_literal(self, n: Tree):
        if not n.children:
            raise TypeError_("empty array literal")
        # Flatten comma-separated list into element nodes only
        elements = []  # collect element types from the first child’s subtree
        for node in n.children[0].children:
            if isinstance(node, Token) and node.value == ",":
                continue  # skip comma separators
            element_type = self.visit(node)  # compute the type of the element
            elements.append(element_type)
        if any(t != elements[0] for t in elements):
            raise TypeError_("array elements must share type")
        return elements[0] + "[]"  # Resulting type is elementType[]

    # postfix (function call, array indexing)
    def visit_postfix_expr(self, n: Tree):
        primary = n.children[0]
        id_token: Token | None = primary if isinstance(primary, Token) and primary.type == "ID" else None
        current_type: str | None = None  # Tracks the running type as suffixes are processed

        for suf in n.children[1:]:
            if suf.data == "call_suffix":
                # First suffix can only be applied to an identifier
                if id_token is None:
                    raise StructureError("function call must target identifier")
                signature = self.function_map.get(id_token.value)
                if signature is None:
                    raise ScopeError(f"call to undefined function '{id_token.value}'")

                # Parse argument list, skipping comma tokens
                raw_arguments = suf.children[0].children if suf.children else []
                argument_nodes = []  # collect actual argument nodes, skipping commas
                for node in raw_arguments:
                    if isinstance(node, Token) and node.value == ",":
                        continue  # ignore comma separators
                    argument_nodes.append(node)
                argument_types = [self.visit(a) for a in argument_nodes]

                if len(argument_types) != len(signature.parameters):
                    raise StructureError(f"wrong number of arguments in call to '{id_token.value}'")
                for arg_t, expected in zip(argument_types, signature.parameters):
                    if arg_t not in {expected, "noType"}:
                        raise TypeError_("argument type mismatch")

                current_type, id_token = signature.return_type, None  # Type post-call; clear id_token
            elif suf.data == "array_access_suffix":
                # Resolve base type for the first indexing occurrence
                current_type = self.visit(primary) if current_type is None else current_type
                if not current_type.endswith("[]"):
                    raise TypeError_("indexing non-array value")
                if self.visit(suf.children[0]) != "integer":
                    raise TypeError_("array index must be integer")
                current_type = current_type[:-2]  # Drop one dimension
            else:
                raise StructureError("unexpected postfix suffix")

        if current_type is None:  # No suffixes: just primary expression
            current_type = self.visit(primary)

        # Using a void/noType value inside an expression (except expr_stmt) is illegal
        if current_type == "noType" and not self.in_expr_stmt:
            raise TypeError_("void value used in expression")
        return current_type

    # input literal
    def visit_input_expr(self, _):
        return "noType"  # Represents read-from-stdin; has no concrete type

    # helpers below
    # identifier case enforcement
    def check_case(self, name: str):
        if self.case_style == "camelCase":
            if "_" in name or not name[0].islower():
                raise CaseError(f"'{name}' not camelCase")
        else:  # snake_case
            if any(c.isupper() for c in name):
                raise CaseError(f"'{name}' not snake_case")

    def shadow_check(self, name: str):
        if name in self.variable_map:
            raise ScopeError(f"shadowing '{name}'")

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
            raise StructureError("Multiple returns in same branch")
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
            else_ok = True
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