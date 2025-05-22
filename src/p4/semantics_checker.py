from dataclasses import dataclass  # Lightweight record for function metadata
from collections import ChainMap  # Nested, write-through symbol tables
from typing import List, Dict  # Static typing helpers
from lark import Tree, Token  # AST node and token classes from Lark

# error hierarchy
class StaticError(Exception): # Base class for all static-analysis errors
    def __init__(self, message: str, line: int | None = None) -> None:
        if line is not None:
            base_message = f"Line {line}: {message}"
        else:
            base_message = f"{message}"
        self.message = base_message
        self.line = line
        super().__init__(self.message)

class TypeError_(StaticError): pass
class IncompatibleTypeError(TypeError_):
    def __init__(self, actual_value, actual_type: str, variable_name: str, expected_type: str, line: int | None = None):
        if isinstance(actual_value, Tree):
            string_tree = str(actual_value)
            if '/' in string_tree:
                message = (f"Cannot assign a divisional expression of final evaluated type {actual_type} to variable {variable_name} of type {expected_type}.\n "
                                  f"Divisional expressions always evaluates result of type decimal.")
            else:
                message = f"Cannot assign expression of final evaluated type {actual_type} to variable {variable_name} of type {expected_type}."
        else:
            message = f"Cannot assign the value {actual_value} of type {actual_type} to the declared variable {variable_name} of type {expected_type}."
        super().__init__(message, line)
class IncompatibleArraySizeError(TypeError_):
    def __init__(self, array_name: str, expected_size: int, actual_size: int, line: int | None = None):
        message = f"Incompatible array size. Cannot assign array of size {actual_size} to array {array_name} of size {expected_size}."
        super().__init__(message, line)
class ArrayIndexError(TypeError_):
    def __init__(self, actual_index: int, array_name: str, line: int | None = None):
        message = f"Accessing index {actual_index} in array {array_name} is not possible. Array index must be an integer."
        super().__init__(message, line)
class ArrayDimensionOutOfBoundsError(TypeError_):
    def __init__(self, access_dimension: int, array_name: str, array_dimension: int, line: int | None = None):
        message = f"Index is out of bounds. Trying to access dimension {access_dimension} in array {array_name} that only has {array_dimension} dimensions."
        super().__init__(message, line)
class IfConditionTypeError(TypeError_):
    def __init__(self, stmt_type: str, type_value: str, line: int | None = None):
        message = f"The if-condition must be of type boolean but instead got a {stmt_type} of type {type_value}."
        super().__init__(message, line)
class WhileConditionTypeError(TypeError_):
    def __init__(self, stmt_type: str, type_value: str, line: int | None = None):
        message = f"The while-condition must be of type boolean but instead got a {stmt_type} of type {type_value}."
        super().__init__(message, line)
class FunctionReturnError(TypeError_):
    def __init__(self, expected_type: str, actual_type: str, line: int | None = None):
        message = f"Declared return type of function is {expected_type}, but the returned value is of type {actual_type}."
        super().__init__(message, line)
class AdditiveExpressionError(TypeError_):
    def __init__(self, line: int | None = None):
        message = f"The operands of an additive expression must all be either integers, decimals or strings."
        super().__init__(message, line)
class ArithmeticExpressionError(TypeError_):
    def __init__(self, line):
        message = f"The operands of the arithmetic expression must all be either integers, decimals or strings."
        super().__init__(message, line)
class DivisionExpressionError(TypeError_):
    def __init__(self, line):
        message = "operands of / must both be integer or decimal"
        super().__init__(message, line)
class EqualityOperatorsError(TypeError_):
    def __init__(self, operator: str, line: int | None = None):
        message = f"Operands of equality operator {operator} must match and be of either type integer, decimal or string"
        super().__init__(message, line)
class ComparisonOperatorsError(TypeError_):
    def __init__(self, operator: str, line: int | None = None):
        message = f"operands of comparison operator {operator} must match and be of either type integer or decimal"
        super().__init__(message, line)
class LogicalExpressionTypeError(TypeError_):
    def __init__(self, operand_index: int, actual_type: str, line: int | None = None):
        message = f"Operand number {operand_index} is of type {actual_type}. Logical expressions require operands of type boolean."
        super().__init__(message, line)
class EmptyArrayAssignmentError(TypeError_):
    def __init__(self, line):
        message = "Empty arrays cannot be assigned."
        super().__init__(message, line)
class ArrayElementTypeError(TypeError_):
    def __init__(self, line: int | None = None):
        message = "Array elements must share type and be of the same type as the declared array."
        super().__init__(message, line)
class FunctionCallWithNumericIdentifierError(TypeError_):
    def __init__(self, identifier: str, line: int | None = None):
        message = f"Function call cannot target numeric identifier '{identifier}'. Only previously declared functions with a valid identifier can be called."
        super().__init__(message, line)
class UnexpectedArgumentTypeError(TypeError_):
    def __init__(self, actual_type, function_identifier, expected_type, line: int | None = None):
        message = f"Argument of type {actual_type} given in function call for function {function_identifier} does not match the expected argument of type {expected_type}."
        super().__init__(message, line)
class ArrayAccessInAssignError(TypeError_):
    def __init__(self, actual_parameter, line):
        message = f"Accessing array index with {actual_parameter} is not possible. Array access index must be of type Integer."
        super().__init__(message, line)
class ArrayDimensionAccessError(TypeError_):
    def __init__(self, array_identifier, declared_dimensions, line):
        message = f"Cannot access a dimension in array {array_identifier} greater than the declared amount of {declared_dimensions} dimensions."
        super().__init__(message, line)
class AssignNoReturnError(TypeError_):
    def __init__(self, variable_identifier, function_identifier, declared_function_type, line: int | None = None):
        message = f"Cannot initialize variable {variable_identifier} with function {function_identifier} that has return type {declared_function_type} and therefore returns no value."
        super().__init__(message, line)

class ScopeError(StaticError): pass# Type mismatch or misuse
class DuplicateIdentifierError(ScopeError):
    def __init__(self, name: str, line: int | None = None):
        message = f"Function {name} is already defined"
        super().__init__(message, line)
class UndefinedIdentifierError(ScopeError):
    def __init__(self, name: str, line: int | None = None):
        message = f"The variable '{name}' is not declared in scope before use."
        super().__init__(message, line)
class FunctionCallWithUndefinedFunctionError(ScopeError):
    def __init__(self, identifier: str, line: int | None = None):
        message = f"Function call targets undefined function '{identifier}'."
        super().__init__(message, line)
class ShadowingIdentifierError(ScopeError):
    def __init__(self, name, form, line: int | None = None):
        if form == "variable":
            message = f"The identifier '{name}' has already been declared as a {form} in the same scope."
        if form == "function":
            message = f"The identifier '{name}' has already been declared as a {form} in the same scope."
        super().__init__(message, line)

# Undeclared identifier or variable shadowing
class CaseError(StaticError): pass# Wrong identifier case style
class CaseStyleError(CaseError):
    def __init__(self, identifier, case_style, line: int | None = None):
        if case_style == "camelCase":
            message = f"Identifier '{identifier}' is not following the specified case style '{case_style}'. The style must begin with a lowercase letter and _ is not allowed"
        if case_style == "snake_case":
            message = f"Identifier '{identifier}' is not following the specified case style '{case_style}'. No uppercase letters is allowed."
        super().__init__(message, line)

class StructureError(StaticError):  pass # Violations of language structure rules
class ReturnStatementOfnoTypeFunctionError(StructureError):
    def __init__(self, value, line):
        message = (f"Cannot exit scope of function by returning value {value}. A function with return type noType cannot return any value. \n"
                                     f"Fix: Delete value {value} from return statement or redefine return type of function to match type of returned value.")
        super().__init__(message, line)
class NoReturnError(StructureError):
    def __init__(self, name: str, line: int | None = None):
        message = f"Function {name} has no return value defined"
        super().__init__(message, line)
class UnmatchedNumberOfArgumentsError(StructureError):
    def __init__(self, function_identifier, expected_argument_amount, actual_argument_amount, line):
        message = f"Function call for '{function_identifier}' expects {expected_argument_amount} arguments. Only {actual_argument_amount} is given."
        super().__init__(message, line)
class MainFunctionError(StructureError):
    def __init__(self, error_type, line: int | None = None):
        if error_type == "no main":
            message = "The main function must be specified."
        if error_type == "not last":
            message = "The main function must be declared as the last function in the source code."
        super().__init__(message, line)
class MultipleReturnsInSameScopeError(StructureError):
    def __init__(self, occurrences, line: int | None = None):
        occurences_amount = len(occurrences)
        if occurences_amount == 2:
            occurrences_placement = ' and '.join(str(element) for element in occurrences)
        else:
            occurrences_placement = ', '.join(str(element) for element in occurrences)
        message = f"Multiple return statements is in the same function scope on lines {occurrences_placement}. Only one return statement is allowed per declared function."
        super().__init__(message, line)

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
                raise UndefinedIdentifierError(token.value)
            return self.variable_map[token.value]
        return None  # Commas, brackets, etc. are ignored here

    # syntax header
    def visit_syntax(self, node: Tree):
        case = node.children[1].value
        self.case_style = case

    # start symbol
    def visit_start(self, node: Tree):
        for child in node.children:
            self.visit(child)

    # functions
    def visit_function_definition(self, node: Tree):
        return_type = self.get_base_type(node.children, 0)
        function_name = node.children[1].value
        parameters_node = None  # look for a child node representing parameter declarations
        for child in node.children:
            if isinstance(child, Tree) and child.data == "params":
                parameters_node = child  # found the params subtree
                break  # stop once we've located it
        body = node.children[-1]

        if function_name in self.function_map:
            line = self.get_line_from_tree(node)
            raise DuplicateIdentifierError(function_name, line)
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
            if all(type_ == inferred for type_ in self.seen_returns):
                # replace the published type with the more specific one
                self.function_map[function_name].return_type = inferred

        # Non-void functions must guarantee a return on every path
        if return_type != "noType" and not self.body_guarantees_return(body):
            line = self.get_line_from_tree(node)
            raise NoReturnError(function_name, line)

        # Restore outer context
        self.variable_map = outer_vars
        self.current_return_type = outer_return_type

        self.check_single_return(body)  # Enforce at most one return per branch

    # blocks
    def visit_block(self, node: Tree):
        # Sequential walk; nothing special aside from nesting handled by scopes elsewhere
        for statement in node.children:
            self.visit(statement)

    # variable declarations
    def visit_declaration_stmt(self, node: Tree):
        base = node.children[0].value
        name = node.children[1].value
        sizes, idx = self.collect_sizes(node.children, 2)

        self.check_case(name)
        self.shadow_check(name)

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
                line = self.get_line_from_tree(node)
                raise AssignNoReturnError(name, right_hand_side_node.children[0].value, right_hand_side_type, line)
            if right_hand_side_type != declared_type and right_hand_side_type != "noType":
                line = self.get_line_from_tree(node)
                raise IncompatibleTypeError(right_hand_side_node, right_hand_side_type, name, declared_type, line)
            if sizes and isinstance(right_hand_side_node, Tree) and right_hand_side_node.data == "array_literal":
                literal_elements = [
                    elem for elem in right_hand_side_node.children[0].children
                    if not (isinstance(elem, Token) and elem.value == ",")
                ]
                if len(literal_elements) != sizes[0]:
                    length = len(literal_elements)
                    raise IncompatibleArraySizeError(name, sizes[0], length)

        self.variable_map[name] = declared_type

    # assignments
    def visit_assignment_stmt(self, node: Tree):
        left_value = node.children[0]
        right_hand_side_node = node.children[-1]
        # identifier being assigned to
        name = left_value.children[0].value
        if name not in self.variable_map:
            line = self.get_line_from_tree(node)
            raise UndefinedIdentifierError(name, line)

        full_type = self.variable_map[name]
        declared_dimensions = full_type.count("[]")
        element_base = full_type.rstrip("[]")
        sizes = None

        # collect every indexing suffix
        indices = [suffix for suffix in left_value.children[1:] if
                   isinstance(suffix, Tree) and suffix.data == "array_access_suffix"]

        # basic type-check on each index expression and optional const-bound check
        for dimension, suffix in enumerate(indices):
            index_node = suffix.children[0]
            if self.visit(index_node) != "integer":
                actual_index = self.visit(index_node) #actual index is not used
                line = self.get_line_from_tree(node)
                raise ArrayIndexError(index_node.value, name, line)

        # too many indices?
        if len(indices) > declared_dimensions:
            actual_length = len(indices)
            line = self.get_line_from_tree(node)
            raise ArrayDimensionOutOfBoundsError(actual_length, name, declared_dimensions, line)

        right_hand_side_type = self.visit(right_hand_side_node)

        # determine the expected type after applying the indices
        remaining_dimensions = declared_dimensions - len(indices)
        expected_type = (
            element_base if remaining_dimensions == 0
            else element_base + "[]" * remaining_dimensions
        )

        if right_hand_side_type not in {expected_type, "noType"}:
            line = self.get_line_from_tree(node)
            raise IncompatibleTypeError(right_hand_side_node, right_hand_side_type, name, expected_type, line)

    # control flow
    def visit_if_stmt(self, node: Tree):
        if self.visit(node.children[0]) != "boolean":
            conditional_stmt = node.children[0].data #if else in error handler
            type_ = self.visit(node.children[0])
            line = self.get_line_from_tree(node)
            raise IfConditionTypeError(conditional_stmt, type_, line)
        self.visit(node.children[1])  # then branch
        if len(node.children) == 3:
            self.visit(node.children[2])  # else branch

    def visit_while_stmt(self, node: Tree):
        if self.visit(node.children[0]) != "boolean":
            conditional_stmt = node.children[0].data
            type_ = self.visit(node.children[0])
            line = self.get_line_from_tree(node)
            raise WhileConditionTypeError(conditional_stmt, type_, line)
        self.visit(node.children[1])

    def visit_return_stmt(self, node):
        if self.current_return_type == "noType":
            if len(node.children) != 0:
                value = node.children[0].value
                line = self.get_line_from_tree(node)
                raise ReturnStatementOfnoTypeFunctionError(value, line)
            else:
                return
        else:
            actual = self.visit(node.children[0])
            if not self.compatible(actual, self.current_return_type):
                declared_return_type = self.current_return_type
                line = self.get_line_from_tree(node)
                raise FunctionReturnError(declared_return_type, actual, line)

        self.seen_returns.append(actual)

    # expression statement
    def visit_expr_stmt(self, node: Tree):
        previous = self.in_expr_stmt
        self.in_expr_stmt = True  # Suppress "void value" error for RHS 'noType'
        self.visit(node.children[0])
        self.in_expr_stmt = previous

    # arithmetic expression
    def visit_arit_expr(self, node: Tree):
        left_type = self.visit(node.children[0])
        operator_token: Token = node.children[1] if len(node.children) == 3 else None
        if operator_token is None:  # Single operand (propagates type)
            return left_type
        right_type = self.visit(node.children[2])
        operator = operator_token.value

        # '+' supports string concatenation; others require numeric
        if operator == "+":
            if left_type != right_type or left_type not in self._ARITH:
                line = self.get_line_from_tree(node)
                raise AdditiveExpressionError(line)
            return left_type
        if operator in {"-", "*", "%"}:
            if left_type != right_type or left_type not in self._NUM:
                line = self.get_line_from_tree(node)
                raise ArithmeticExpressionError(line)
            return left_type
        if operator == "/":
            if left_type != right_type or left_type not in self._NUM:
                line = self.get_line_from_tree(node)
                raise DivisionExpressionError(line)
            return "decimal"  # Division always yields decimal
        raise StructureError("default")

    # comparison
    def visit_compare_expr(self, node: Tree):
        left_type = self.visit(node.children[0])
        operator = node.children[1].value
        right_type = self.visit(node.children[2])
        if operator in {"==", "!="}:  # Equality works for any matching types
            if left_type != right_type:
                line = self.get_line_from_tree(node)
                raise EqualityOperatorsError(operator, line)
        else:  # <, <=, >, >= restricted to numbers
            if left_type != right_type or left_type not in self._NUM:
                line = self.get_line_from_tree(node)
                raise ComparisonOperatorsError(operator, line)
        return "boolean"

    # logical and/or
    def visit_logical_expr(self, node: Tree):
        # Children alternate operand, operator, operand, ...
        for i in range(0, len(node.children), 2):
            if self.visit(node.children[i]) != "boolean":
                actual_type = self.visit(node.children[i])
                operand_index = i + 1
                line = self.get_line_from_tree(node)
                raise LogicalExpressionTypeError(operand_index, actual_type, line)
        return "boolean"

    # array literal
    def visit_array_literal(self, node: Tree):
        if not node.children:
            line = self.get_line_from_tree(node)
            raise EmptyArrayAssignmentError(line)
        # Flatten comma-separated list into element nodes only
        elements = []  # collect element types from the first child’s subtree
        for node in node.children[0].children:
            if isinstance(node, Token) and node.value == ",":
                continue  # skip comma separators
            element_type = self.visit(node)  # compute the type of the element
            elements.append(element_type)
        if any(t != elements[0] for t in elements):
            raise ArrayElementTypeError(node.line)
        return elements[0] + "[]"  # Resulting type is elementType[]

    # postfix (function call, array indexing)
    def visit_postfix_expr(self, node: Tree):
        primary = node.children[0]
        id_token: Token | None = primary if isinstance(primary, Token) and primary.type == "ID" else None
        current_type: str | None = None  # Tracks the running type as suffixes are processed
        declared_dimensions = -1
        
        for suffix in node.children[1:]:
            if suffix.data == "call_suffix":
                # First suffix can only be applied to an identifier
                if id_token is None:
                    line = self.get_line_from_tree(node)
                    raise FunctionCallWithNumericIdentifierError(node.children[0], line)
                signature = self.function_map.get(id_token.value)
                if signature is None:
                    line = self.get_line_from_tree(node)
                    raise FunctionCallWithUndefinedFunctionError(id_token.value, line)

                # Parse argument list, skipping comma tokens
                raw_arguments = suffix.children[0].children if suffix.children else []
                argument_nodes = []  # collect actual argument nodes, skipping commas
                for node in raw_arguments:
                    if isinstance(node, Token) and node.value == ",":
                        continue  # ignore comma separators
                    argument_nodes.append(node)
                argument_types = [self.visit(a) for a in argument_nodes]

                if len(argument_types) != len(signature.parameters):
                    expected_argument_amount = len(signature.parameters)
                    actual_argument_amount = len(argument_types)
                    line = node.line
                    raise UnmatchedNumberOfArgumentsError(id_token.value, expected_argument_amount, actual_argument_amount, line)
                for argument_type, expected in zip(argument_types, signature.parameters):
                    if argument_type not in {expected, "noType"}:
                        line = node.line
                        raise UnexpectedArgumentTypeError(argument_type, id_token.value, expected, line)

                current_type, id_token = signature.return_type, None  # Type post-call; clear id_token
            elif suffix.data == "array_access_suffix":
                # Resolve base type for the first indexing occurrence
                declared_dimensions += 1
                current_type = self.visit(primary) if current_type is None else current_type
                if not current_type.endswith("[]"):
                    line = self.get_line_from_tree(node)
                    raise ArrayDimensionAccessError(primary, declared_dimensions, line)
                if self.visit(suffix.children[0]) != "integer":
                    line = self.get_line_from_tree(node)
                    actual_parameter = suffix.children[0]
                    raise ArrayAccessInAssignError(actual_parameter, line)
                current_type = current_type[:-2]  # Drop one dimension
            else:
                raise StructureError("unexpected postfix suffix") #what do we use this for?

        if current_type is None:  # No suffixes: just primary expression
            current_type = self.visit(primary)

        # Using a void/noType value inside an expression (except expr_stmt) is illegal
        if current_type == "noType" and not self.in_expr_stmt: #what is this used for?
            raise TypeError_("void value used in expression")
        return current_type

    # input literal
    def visit_input_expr(self, _): #hvorfor er der _??
        return "noType"  # Represents read-from-stdin; has no concrete type

    # helpers below
    # identifier case enforcement
    def check_case(self, name: str):
        if self.case_style == "camelCase":
            if "_" in name or not name[0].islower():
                raise CaseStyleError(name, self.case_style)
        else:  # snake_case
            if any(character.isupper() for character in name):
                raise CaseStyleError(name, self.case_style)

    def shadow_check(self, name: str):
        if name in self.variable_map:
            identified_form = "variable"
            raise ShadowingIdentifierError(name, identified_form)
        if name in self.function_map:
            identified_form = "function"
            raise ShadowingIdentifierError(name, identified_form)

    def is_input_expr(self, node: Tree | Token | None) -> bool:
        return isinstance(node, Tree) and node.data == "input_expr"

    # global checks
    def post_checks(self):
        # Exactly one main, and it must be last
        has_main = self.function_order.count("main") == 1  # check there is exactly one 'main'
        is_last = bool(self.function_order) and self.function_order[-1] == "main"  # check 'main' is the last element
        if not has_main:
            error_type = "no main"
            raise MainFunctionError(error_type)
            #raise StructureError("main function must be specified")
        if not is_last:
            error_type = "not last"
            raise MainFunctionError(error_type)
            #raise StructureError("'main' must be last function")

    # single-return-per-branch
    def check_single_return(self, block: Tree):
        # Enforce at most one return per linear execution branch (no early exits after return)
        if block.data != "block":
            return
        return_count = 0 # count return statements in this block
        return_statement_line = []
        for child in block.children:
            if isinstance(child, Tree) and child.data == "return_stmt":
                return_count += 1  # increment for each return statement found
                line = self.get_line_from_tree(child)
                return_statement_line.append(line)
        if return_count > 1:
            line = return_statement_line[0]
            all_lines = return_statement_line
            raise MultipleReturnsInSameScopeError(all_lines, line)
        for child in block.children:
            if not isinstance(child, Tree):
                continue
            if child.data == "if_stmt":
                # Check both branches recursively
                self.check_single_return(child.children[1])
                if len(child.children) == 3:
                    self.check_single_return(child.children[2])
            elif child.data == "while_stmt":
                self.check_single_return(child.children[1])
            elif child.data == "block":
                self.check_single_return(child)

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

    def get_line_from_tree(self, node: Tree):
        for child in node.children:
            if isinstance(child, Token):
                return child.line
            elif isinstance(child, Tree):
                line = self.get_line_from_tree(child)
                if line:
                    return line
        return None

    def get_base_type(self, children, idx0):
        return children[idx0].value