from lark import Tree, Token

class Interpreter:
    def visit(self, node):
        if isinstance(node, Tree):
            data = node.data
            method_name = f'visit_{data}'
            method = getattr(self, method_name, self.bad_visit)
            return method(node)
        elif isinstance(node, Token):
            return self.visit_token(node)

    def bad_visit(self, node):
        raise Exception(f'visit_{node.data} is not implemented.')

    #########################

    def visit_token(self, node):
        print(node.type)
        if node.type == "INT":
            return int(node.value)
        elif node.type == "DOUBLE":
            return float(node.value)
        return node.value

    def visit_expr_plus(self, node):
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