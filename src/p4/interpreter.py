from lark import Tree, Token

from environment import Environment

class Interpreter:
    def __init__(self):
        self.env = Environment()

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

    ## Variables

    def visit_declaration_stmt(self, node):
        if len(node.children) == 2:
            self.env.declare(node.children[1])
        else:
            self.env.define(node.children[1], node.children[2])

    ## Block

    def visit_block(self, node):
        for child in node.children:
            self.visit(child)

    ## Interactions

    def visit_output_stmt(self, node):
        print(self.visit(node.children[0]))

    def visit_input_stmt(self, node):
        return input()