import unittest

from src.p4.interpreter import Interpreter

from src.p4.environment import Environment


class DummyNode:
    def __init__(self, children):
        self.children = children


class test_add_sub(unittest.TestCase):
    def setUp(self):
        class Visitor:
            def visit(self, node):
                return node

            new_intepreter = Interpreter()

            def visit_add_expr(self, node):
                result = self.visit(node.children[0])

                for i in range(1, len(node.children), 2):
                    op = node.children[i]
                    value = self.visit(node.children[i + 1])

                    if op == "+":
                        result += value
                    elif op == "-":
                        result -= value
                    else:
                        raise Exception(f'Unsupported operator: {op}')
                return result

        self.visitor = Visitor()

    def test_addition(self):
        node = DummyNode([1, "+", 2, "+", 3])
        result = self.visitor.visit_add_expr(node)
        self.assertEqual(result, 6)

    def test_addition_2(self):
        node = DummyNode([-3, "+", 2, "+", 1])
        result = self.visitor.visit_add_expr(node)
        self.assertEqual(result, 0)

    def test_subtraction(self):
        node = DummyNode([3, "-", 2, "-", 1])
        result = self.visitor.visit_add_expr(node)
        self.assertEqual(result, 0)

    def test_subtraction_2(self):
        node = DummyNode([-1, "-", 2, "-", 3])
        result = self.visitor.visit_add_expr(node)
        self.assertEqual(result, -6)

    def test_addition_and_subtraction(self):
        node = DummyNode([10, "-", 3, "+", 2])
        result = self.visitor.visit_add_expr(node)
        self.assertEqual(result, 9)