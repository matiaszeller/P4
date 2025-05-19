from lark import Tree, Token
from environment import Environment
import ast

class Interpreter:
    def __init__(self):
        self.env = Environment()

    #Recursive logic for visits
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

    ## Terminals
    def visit_token(self, node):
        if node.type == "INT":
            return int(node)
        elif node.type == "ID":
            return self.env.get_variable(node)
        elif node.type == "NEWLINE":
            return
        elif node.type == "BOOLEAN":
            if node == "true":
                return True
            elif node == "false":
                return False
            raise Exception(f'{node} is not a valid boolean value.')
        else:
            raise Exception(f'Unknown type: {node.type}')

    def visit_decimal(self, node):
        number = node.children[0]
        fraction = node.children[1]
        return float(f"{number}.{fraction}")

    def visit_string(self, node):
        string = ast.literal_eval(node.children[0])
        return string

    #Unary expressions
    def visit_uminus(self, node):
        value = self.visit(node.children[1])
        return -value

    def visit_negate(self, node):
        boolean = self.visit(node.children[0])
        return not bool(boolean)

    ## Binary Expressions
    def visit_add_expr(self, node):
        result = self.visit(node.children[0])

        for i in range(1, len(node.children), 2):
            operator = node.children[i]
            operand = self.visit(node.children[i +1])

            if operator == "+":
                result += operand
            elif operator == "-":
                result -= operand
            else:
                raise Exception(f'Unsupported operator: {operator}. Expected + or -.')
        return result

    def visit_mul_expr(self, node):
        result = self.visit(node.children[0])

        for i in range(1, len(node.children), 2):
            operator = node.children[i]
            operand = self.visit(node.children[i+1])

            if operator == "*":
                result *= operand
            elif operator == "/":
                result /= operand
            elif operator == "%":
                result %= operand
            else:
                raise Exception(f'Unsupported operator: {operator}, expected *, /, or %.')
        return result

    def visit_equality_expr(self, node):
        value1 = self.visit(node.children[0])
        value2 = self.visit(node.children[2])
        operator = node.children[1]

        if operator == "==":
            return value1 == value2
        elif operator == "!=":
            return value1 != value2
        else:
            raise Exception(f'Unsupported operator: {operator}, expected == or !=.')

    def visit_relational_expr(self, node):
        value1 = self.visit(node.children[0])
        value2 = self.visit(node.children[2])
        operator = node.children[1]

        if operator == "<":
            return value1 < value2
        elif operator == ">":
            return value1 > value2
        elif operator == "<=":
            return value1 <= value2
        elif operator == ">=":
            return value1 >= value2
        else:
            raise Exception(f'Unsupported operator: {operator}, expected <, >, <=, or >=.')

    def visit_and_expr(self, node):
        result = self.visit(node.children[0])
        for i in range(1, len(node.children)):
            boolean = self.visit(node.children[i])
            result = result and boolean
        return result

    def visit_or_expr(self, node):
        result = self.visit(node.children[0])
        for i in range(1, len(node.children)):
            boolean = self.visit(node.children[i])
            result = result or boolean
        return result

    ## Statements
    def visit_expr_stmt(self, node):
        return self.visit(node.children[0])

    def visit_declaration_stmt(self, node):
        name = node.children[1]
        type = node.children[0]
        children_amount = len(node.children)
        if children_amount == 2: #Contains only name and type
            self.env.declare_variable(name,type)
        elif self.isArray(node):
            if self.hasValue(node.children[-2]): #Contains initial value for array
                array_depth = len(node.children) - 3 #name, type and value children are discounted
                array_values = self.visit(node.children[-1])
                if not isinstance(array_values, list):
                    raise Exception(f'Cannot assign {array_values} to array variable {name}. Make sure it is a list of values separated by commas, and wrapped in brackets.')
                self.env.declare_variable(name, type, array_depth)
                self.env.set_variable(name, array_values)
            else:
                array_depth = len(node.children) - 2
                self.env.declare_variable(name, type, array_depth)
        else:
            self.env.declare_variable(name, type)
            self.env.set_variable(name, self.visit(node.children[-1]))

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
        print(f'You are programming in {node.children[0]} using {node.children[2]}\n')

    ## Helper Functions
    def hasValue(self, node):
        print(node.data)
        if node.data == "array_suffix":
            return True
        else:
            return False

    def isArray(self, node):
        try:
            if node.children[2].data == "array_suffix":
                return True
            else:
                return False
        except IndexError and AttributeError:
            return False