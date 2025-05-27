from lark import Tree, Token
from src.p4.environment import Environment
from src.p4.error import TreeError, OperatorError, ArrayIndexError, ArrayDimensionError
import ast

class Interpreter:
    def __init__(self):
        self.env = Environment()

    # Recursive logic for visits
    def visit(self, node):
        if isinstance(node, Tree):
            data = node.data
            method_name = f"visit_{data}"
            method = getattr(self, method_name, self.bad_visit)
            return method(node)
        elif isinstance(node, Token):
            return self.visit_token(node)
        return None

    ## Error handling
    def bad_visit(self, node):
        raise TreeError(node)

    ## Start and Block
    def visit_start(self, node):
        for child in node.children:
            self.visit(child)

    def visit_block(self, node):
        for child in node.children:
            result = self.visit(child)
            if result == "FLAG_XXXXXXXXXXXXXXXX":
                break
            elif result is not None:
                return result
        return None

    def visit_token(self, node):
        if node.type == "INT":
            return int(node)
        elif node.type == "ID":
            return self.env.get_variable(node.value, line=node.line)
        elif node.type == "FLOAT":
            return float(node)
        elif node.type == "STRING":
            return ast.literal_eval(node.value)
        elif node.type == "BOOLEAN":
            return node.value == "true"
        else:
            raise TreeError(node)

    # Unary expressions
    def visit_uminus(self, node):
        value = self.visit(node.children[1])
        return -value

    def visit_negate(self, node):
        boolean = self.visit(node.children[0])
        return not bool(boolean)

    ## Binary Expressions
    def visit_arit_expr(self, node):
        result = self.visit(node.children[0])
        for i in range(1, len(node.children), 2):
            operator = node.children[i].value
            operand = self.visit(node.children[i + 1])
            if operator == "*":
                result *= operand
            elif operator == "/":
                result /= operand
            elif operator == "%":
                result %= operand
            elif operator == "-":
                result -= operand
            elif operator == "+":
                result += operand
            else:
                raise OperatorError(operator, node.line, "arithmetic")
        return result

    def visit_compare_expr(self, node):
        value1 = self.visit(node.children[0])
        value2 = self.visit(node.children[2])
        operator = node.children[1].value
        if operator == "==":
            return value1 == value2
        elif operator == "!=":
            return value1 != value2
        elif operator == "<":
            return value1 < value2
        elif operator == ">":
            return value1 > value2
        elif operator == "<=":
            return value1 <= value2
        elif operator == ">=":
            return value1 >= value2
        else:
            raise OperatorError(operator, node.line, "comparison")

    def visit_logical_expr(self, node):
        result = self.visit(node.children[0])
        for i in range(1, len(node.children), 2):
            op = node.children[i].value
            rhs = self.visit(node.children[i + 1])
            if op == "and":
                result = result and rhs
            elif op == "or":
                result = result or rhs
            else:
                raise OperatorError(op, node.line, "logical")
        return result

    ## Statements
    def visit_expr_stmt(self, node):
        return self.visit(node.children[0])

    def visit_declaration_stmt(self, node):
        type_tok = node.children[0]
        name_tok = node.children[1]
        sizes, idx = self.collect_sizes(node.children, 2)
        has_value = idx < len(node.children)
        self.env.declare_variable(name_tok.value, type_tok.value, sizes, line=node.children[1].line)
        if has_value:
            value = self.visit(node.children[idx])
            if sizes and not isinstance(value, list):
                raise ArrayDimensionError(node.children[0].line)
            self.env.set_variable(name_tok.value, value, line=node.children[0].line)

    def visit_assignment_stmt(self, node):
        name_tok = node.children[0].children[0]
        value = self.visit(node.children[1])
        index_depth = len(node.children[0].children) - 1
        if index_depth == 0:
            self.env.set_variable(name_tok.value, value, line=name_tok.line)
        else:
            index_list = [
                self.visit(node.children[0].children[i + 1])
                for i in range(index_depth)
            ]
            self.env.set_variable(name_tok.value, value, index_list, line=name_tok.line)

    def visit_if_stmt(self, node):
        condition = node.children[0]
        then_block = node.children[1]
        if self.visit(condition):
            self.visit(then_block)
        elif len(node.children) == 3:
            else_block = node.children[2]
            self.visit(else_block)

    def visit_while_stmt(self, node):
        condition = node.children[0]
        block = node.children[1]
        while self.visit(condition):
            self.visit(block)

    def visit_return_stmt(self, node):
        if len(node.children) == 0:
            return "FLAG_XXXXXXXXXXXXXXXX"
        return self.visit(node.children[0])

    ## User Interactions
    def visit_output_stmt(self, node):
        print(self.visit(node.children[0]))

    def visit_input_expr(self, node):
        return input().strip()

    ## Functions & Arrays
    def visit_function_definition(self, node):
        name_tok = node.children[1]
        type_tok = node.children[0]
        block = node.children[-1]
        has_params = len(node.children) == 4
        if name_tok.value == "main":
            self.visit(block)
        elif has_params:
            parameters = node.children[2]
            self.env.declare_function(
                name_tok.value, type_tok.value, block, parameters
            )
        else:
            self.env.declare_function(name_tok.value, type_tok.value, block)

    def visit_postfix_expr(self, node):
        name_tok = node.children[0]
        suffix = node.children[-1]
        if suffix.data == "call_suffix":
            function_interpreter = Interpreter()
            function_interpreter.env.functions = self.env.functions.copy()
            if len(suffix.children) == 1:
                parameters = suffix.children[0].children
                param_iter = (
                    p
                    for p in parameters
                    if not (isinstance(p, Token) and p.value == ",")
                )
                meta = self.env.get_function(name_tok.value)
                for i, arg_node in enumerate(param_iter):
                    param = meta["parameters"].children[i]
                    param_name = param.children[1].value
                    param_type = param.children[0].value
                    param_sizes, _ = self.collect_sizes(param.children, 2)
                    function_interpreter.env.declare_variable(
                        param_name, param_type, param_sizes
                    )
                    function_interpreter.env.set_variable(
                        param_name, self.visit(arg_node)
                    )
            return function_interpreter.visit(
                self.env.get_function(name_tok.value)["block"]
            )
        elif suffix.data == "array_access_suffix":
            indices = [self.visit(child) for child in node.children[1:]]
            return self.env.get_variable(name_tok.value, indices, line=name_tok.line)
        return None

    def visit_array_suffix(self, node):
        return int(node.children[0])

    def visit_array_access_suffix(self, node):
        index = self.visit(node.children[0])
        return index

    def visit_array_literal(self, node):
        list_values = [
            self.visit(child)
            for child in node.children[0].children
            if not (isinstance(child, Token) and child.value == ",")
        ]
        return list_values

    ## Syntax
    def visit_syntax(self, node):
        return

    ## Helper Functions
    def has_value(self, node):
        return not (isinstance(node, Tree) and node.data == "array_suffix")

    def is_array(self, node):
        try:
            if node.children[2].data == "array_suffix":
                return True
            else:
                return False
        except (IndexError, AttributeError):
            return False

    def get_type_with_suffixes(self, children, idx0):
        base = children[idx0].value
        sizes, next_idx = self.collect_sizes(children, idx0 + 1)
        return base + "[]" * len(sizes), sizes, next_idx

    def collect_sizes(self, children, start):
        sizes = []
        i = start
        while (
            i < len(children)
            and isinstance(children[i], Tree)
            and children[i].data == "array_suffix"
        ):
            expr_node = children[i].children[0]       # INT, ID, or expr
            size_val = self.visit(expr_node)          # run-time evaluation
            if not isinstance(size_val, int):
                raise ArrayIndexError(expr_node.line, expr_node.column)
            sizes.append(size_val)
            i += 1
        return sizes, i