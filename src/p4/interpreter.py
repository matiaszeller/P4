from lark import Tree, Token

from environment import Environment

class Interpreter:
    def __init__(self, old_environment=None):
        if old_environment is None:
            self.env = Environment()
        else:
            self.env = old_environment



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

    def isBoolean(self, bool):
        if bool in (True, False, "true", "false"):
            return True
        else:
            raise Exception(f'{bool} is neither true nor false.')

    ## Start

    def visit_start(self, node):
        for child in node.children:
            self.visit(child)

    ## Unary Expressions

    def visit_token(self, node):
        if node.type == "INT":
            return int(node)
        elif node.type == "ID":
            return self.env.get(node)
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
        string = node.children[0]
        return string

    def visit_uminus(self, node):
        value = self.visit(node.children[1])
        return -(value)

    def visit_negate(self, node):
        boolean = self.visit(node.children[0])
        if self.isBoolean(boolean):
            return not bool(boolean)
        else:
            raise Exception(f'{boolean} is not a valid boolean value.')

    def visit_expr_stmt(self, node):
        return self.visit(node.children[0])

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
                raise Exception(f'Unsupported operator: {operator}')
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
                raise Exception(f'Unsupported operator: {operator}')
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
            raise Exception(f'Unsupported operator: {operator}')

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
            raise Exception(f'Unsupported operator: {operator}')

    def visit_and_expr(self, node):
        result = self.visit(node.children[0])
        self.isBoolean(result)
        for i in range(1, len(node.children)):
            boolean = self.visit(node.children[i])
            self.isBoolean(boolean)
            result = result and boolean
        return result

    def visit_or_expr(self, node):
        result = self.visit(node.children[0])
        self.isBoolean(result)
        for i in range(1, len(node.children)):
            boolean = self.visit(node.children[i])
            self.isBoolean(boolean)
            result = result or boolean
        return result

    ## Statements

    def visit_declaration_stmt(self, node):
        name = node.children[1]
        children_amount = len(node.children)
        if children_amount == 2:
            self.env.declare(name)
        elif self.isArray(node):
            array_depth = len(node.children) - 2
            self.env.declare(node.children[1], array_depth)
        else:
            self.env.define(node.children[1], self.visit(node.children[2]))

    def visit_assignment_stmt(self, node):
        name = node.children[0].children[0]
        value = self.visit(node.children[1])
        array_depth = len(node.children[0].children)-1
        if array_depth == 0:
            self.env.set(name, value)
        else:
            index_list = [None]*array_depth
            for i in range(array_depth):
                index_list[i] = self.visit(node.children[0].children[i+1])
            self.env.set(name, value, index_list)


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

    ## Block

    def visit_block(self, node):
        for child in node.children:
            self.visit(child)

    ## User Interactions

    def visit_output_stmt(self, node):
        print(self.visit(node.children[0]))

    def visit_input_expr(self, node):
        return input()

    ## Functions & Arrays

    def visit_function_definition(self, node):
        name = node.children[1]
        block = node.children[-1]
        if name == "main":
            self.visit(block)
        else:
            self.env.define(name, block)
        if len(node.children) == 4:
            parameters = node.children[2]
            self.env.define(f'{name}_parameters', parameters)

    def visit_postfix_expr(self, node):
        name = node.children[0]
        suffix = node.children[-1]
        if suffix.data == "call_suffix":
            parameters = suffix.children[0]
            parameter_count = len(parameters.children)
            function_interpreter = Interpreter(self.env)
            if parameter_count > 0:
                for i in range(parameter_count):
                    parameter_name = self.env.get(name+"_parameters").children[i].children[1].value
                    parameter_value = self.visit(parameters.children[i])
                    function_interpreter.env.define(parameter_name, parameter_value)
            return self.visit(function_interpreter.visit(name))
        elif suffix.data == "array_access_suffix":
            indices = len(node.children)-1
            array_index = [None]*indices
            for i in range(indices):
                array_index[i] = self.visit(node.children[i+1])
            return self.env.get(name,array_index)
        return None

    def visit_array_suffix(self, node):
        return True

    def visit_array_access_suffix(self, node):
        index = self.visit(node.children[0])
        return index

    def isArray(self, node):
        try:
            if node.children[2].data == "array_suffix":
                return True
            else:
                return False
        except:
            return False

    ## Syntax

    def visit_syntax(self, node):
        print(f'Youre programming in {node.children[0]} using {node.children[2]}\n')