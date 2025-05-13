from lark import Tree, Token
from environment import Environment
import ast

class Interpreter:
    def __init__(self):
        self.env = Environment()

    # Recursive logic for visits
    def visit(self, node):
        if isinstance(node, Tree):
            data = node.data
            method_name = f'visit_{data}'
            method = getattr(self, method_name, self.bad_visit)
            return method(node)
        elif isinstance(node, Token):
            return self.visit_token(node)
        return None

    ## Error handling
    def bad_visit(self, node):
        raise Exception(f'visit_{node.data} is not implemented.')

    ## Start and Block
    def visit_start(self, node):
        for child in node.children:
            self.visit(child)

    def visit_block(self, node):
        for child in node.children:
            result = self.visit(child)
            if result is not None:
                return result
        return None

    def visit_token(self, node):
        if node.type == "INT":
            return int(node)
        elif node.type == "ID":
            return self.env.get_variable(node)
        elif node.type == "FLOAT":
            return float(node)
        elif node.type == "STRING":
            return ast.literal_eval(node.value)
        elif node.type == "BOOLEAN":
            return node.value == "true"
        else:
            raise Exception(f'Unknown type: {node.type}')

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
                raise Exception(f'Unsupported operator: {operator}, expected *, /, %, + or -')
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
            raise Exception(f'Unsupported operator: {operator}, expected ==, !=, <, >, <=, or >=.')

    def visit_logical_expr(self, node):
        result = self.visit(node.children[0])
        # children: [expr, Token(LOGIC_OP), expr, Token, expr…]
        for i in range(1, len(node.children), 2):
            op = node.children[i].value
            rhs = self.visit(node.children[i+1])
            if op == "and":
                result = result and rhs
            elif op == "or":
                result = result or rhs
            else:
                raise Exception(f"Unknown logical op '{op}'")
        return result

    ## Statements
    def visit_expr_stmt(self, node):
        return self.visit(node.children[0])

    def visit_declaration_stmt(self, node):
        name = node.children[1]
        type = node.children[0]

        # determine array depth and position of possible value
        array_depth = 0
        idx = 2
        while idx < len(node.children) and isinstance(node.children[idx], Tree) and node.children[idx].data == "array_suffix":
            array_depth += 1
            idx += 1

        has_value = idx < len(node.children)

        # declare variable
        self.env.declare_variable(name, type, array_depth)

        # set initial value if present
        if has_value:
            value = self.visit(node.children[idx])
            if array_depth > 0 and not isinstance(value, list):
                raise Exception(f'Cannot assign {value} to array variable {name}. Make sure it is a list of values separated by commas, and wrapped in brackets.')
            self.env.set_variable(name, value)

    def visit_assignment_stmt(self, node):
        name = node.children[0].children[0]
        value = self.visit(node.children[1])
        index_depth = len(node.children[0].children)-1

        if index_depth == 0:
            self.env.set_variable(name, value)
        else:
            index_list = [None]*index_depth
            for i in range(index_depth):
                index_list[i] = self.visit(node.children[0].children[i+1])
            self.env.set_variable(name, value, index_list)

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
        return self.visit(node.children[0])

    ## User Interactions
    def visit_output_stmt(self, node):
        print(self.visit(node.children[0]))

    def visit_input_stmt(self, node):
        return input()

    ## Functions & Arrays
    def visit_function_definition(self, node):
        name = node.children[1]
        type = node.children[0]
        block = node.children[-1]
        hasParams = True if len(node.children) == 4 else False
        if name == "main":
            self.visit(block)
        elif hasParams:
            parameters = node.children[2]
            self.env.declare_function(name, type, block, parameters)
        else:
            self.env.declare_function(name, type, block)

    def visit_postfix_expr(self, node):
        name = node.children[0]
        suffix = node.children[-1]
        if suffix.data == "call_suffix":
            function_interpreter = Interpreter()
            function_interpreter.env.functions = self.env.functions.copy()
            if len(suffix.children) == 1:
                parameters = suffix.children[0]
                parameter_count = len(parameters.children)
                for i in range(parameter_count):
                    parameter_name = self.env.get_function(name)['parameters'].children[i].children[1].value
                    parameter_value = self.visit(parameters.children[i])
                    parameter_type = self.env.get_function(name)['parameters'].children[i].children[0].value
                    function_interpreter.env.declare_variable(parameter_name, parameter_type)
                    function_interpreter.env.set_variable(parameter_name, parameter_value)
            return self.visit(function_interpreter.visit(self.env.get_function(name)['block']))
        elif suffix.data == "array_access_suffix":
            indices = len(node.children)-1
            array_index = [None]*indices
            for i in range(indices):
                array_index[i] = self.visit(node.children[i+1])
            return self.env.get_variable(name,array_index)
        return None

    def visit_array_suffix(self, node):
        return True

    def visit_array_access_suffix(self, node):
        index = self.visit(node.children[0])
        return index

    def visit_array_literal(self, node):
        list_values = []
        for child in node.children[0].children:
            list_values.append(self.visit(child))
        return list_values

    ## Syntax
    def visit_syntax(self, node):
        print(f'You are programming in {node.children[0]} using {node.children[1]}\n')

    ## Helper Functions
    def hasValue(self, node):
        return not (isinstance(node, Tree) and node.data == "array_suffix")

    def isArray(self, node):
        try:
            if node.children[2].data == "array_suffix":
                return True
            else:
                return False
        except (IndexError, AttributeError):
            return False
