from lark import Tree, Token

from environment import Environment

class Interpreter:
    def __init__(self, old_environment):
        if old_environment == 0:
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

    ## Error handling

    def bad_visit(self, node):
        raise Exception(f'visit_{node.data} is not implemented.')

    def isBoolean(self, bool):
        if bool == True or bool == False:
            return True
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
        return node.children[0]

    def visit_uminus(self, node):
        return -float(self.visit(node.children[0]))

    def visit_negate(self, node):
        return not bool(self.visit(node.children[0]))

    def visit_expr_stmt(self, node):
        return self.visit(node.children[0])

    ## Binary Expressions

    def visit_add_expr(self, node):
        result = self.visit(node.children[0])

        for i in range(1, len(node.children), 2):
            op = node.children[i]
            value = self.visit(node.children[i +1])

            if op == "+":
                result += value
            elif op == "-":
                result -= value
            else:
                raise Exception(f'Unsupported operator: {op}')
        return result

    def visit_mul_expr(self, node):
        result = self.visit(node.children[0])

        for i in range(1, len(node.children), 2):
            op = node.children[i]
            value = self.visit(node.children[i+1])

            if op == "*":
                result *= value
            elif op == "/":
                result /= value
            elif op == "%":
                result %= value
            else:
                raise Exception(f'Unsupported operator: {op}')
        return result

    def visit_comparison_expr(self, node):
        value1 = self.visit(node.children[0])
        value2 = self.visit(node.children[2])
        op = node.children[1]

        if op == "==":
            return value1 == value2
        elif op == "<":
            return value1 < value2
        elif op == ">":
            return value1 > value2
        elif op == "<=":
            return value1 <= value2
        elif op == ">=":
            return value1 >= value2
        else:
            raise Exception(f'Unsupported operator: {op}')

    def visit_and_expr(self, node):
        result = self.visit(node.children[0])
        self.isBoolean(result)
        for i in range(1, len(node.children)):
            result = result and self.visit(node.children[i])
        return result

    def visit_or_expr(self, node):
        result = self.visit(node.children[0])
        self.isBoolean(result)
        for i in range(1, len(node.children)):
            result = result or self.visit(node.children[i])
        return result

    ## Statements

    def visit_declaration_stmt(self, node):
        childrenAmount = len(node.children)
        if childrenAmount == 2:
            self.env.declare(node.children[1])
        elif childrenAmount == 3:
            if self.visit(node.children[2]):
                self.env.declare(node.children[1], True)
            else:
                self.env.define(node.children[1], self.visit(node.children[2]))

    def visit_assignment_stmt(self, node):
        name = node.children[0].children[0]
        value = node.children[1]
        if len(node.children[0].children) == 1:
            self.env.set(name, value)
        else:
            arrayIndex = self.visit(node.children[0].children[1])
            self.env.set(name, value, [arrayIndex])


    def visit_if_stmt(self, node):
        if self.visit(node.children[0]):
            self.visit(node.children[1])
        elif len(node.children) == 3:
            self.visit(node.children[2])

    def visit_while_stmt(self, node):
        while self.visit(node.children[0]):
            self.visit(node.children[1])

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
        if node.children[1] == "main":
            self.visit(node.children[2])
        elif len(node.children) == 3:
            self.env.define(node.children[1], node.children[2])
        else:
            self.env.define(node.children[1], node.children[3])
            self.env.define(f'{node.children[1]}_parameters', node.children[2])

    def visit_postfix_expr(self, node):
        if node.children[-1].data == "call_suffix":
            function_interpreter = Interpreter(self.env)
            if len(node.children[1].children) > 0:
                for i in range(0,len(node.children[1].children[0].children)):
                    parameter_name = self.env.get(node.children[0]+"_parameters").children[i].children[1].value
                    parameter_value = self.visit(node.children[1].children[0].children[i])
                    function_interpreter.env.define(parameter_name, parameter_value)
            return self.visit(function_interpreter.visit(node.children[0]))
        elif node.children[-1].data == "array_access_suffix":
            name = node.children[0]
            arrayIndex = self.visit(node.children[1])
            return self.env.get(name,[arrayIndex])

    def visit_array_suffix(self, node):
        return True

    def visit_array_access_suffix(self, node):
        index = self.visit(node.children[0])
        return index


    ## Syntax

    def visit_syntax(self, node):
        print(f'Youre programming in {node.children[0]} using {node.children[2]}\n')