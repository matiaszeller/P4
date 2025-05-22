import unittest
from unittest import result

from src.p4.interpreter import Interpreter
from src.p4.environment import Environment

from lark import Tree, Token
from src.p4.semantics_checker import TypeError_

from src.p4.semantics_checker import SemanticsChecker

class DummyNode(Tree):
    def __init__(self, rule_name, children):
        super().__init__(rule_name, children)

class test_arit_expr(unittest.TestCase):
    def setUp(self):
        class TestSemantics(SemanticsChecker):
            def visit(self, node):
                return super().visit(node)
        self.semantics_checker = TestSemantics()

    def test_multiplication_integer(self):
        node = (DummyNode('arit_expr', [
            Token('INT', '1'),
            Token('MUL_OP', '*'),
            Token('INT', '2'),
        ]))
        result = self.semantics_checker.visit_arit_expr(node)
        self.assertEqual(result, "integer")

    def test_multiplication_decimal(self):
        node = (DummyNode('arit_expr', [
            Token('FLOAT', '1.5'),
            Token('MUL_OP', '*'),
            Token('FLOAT', '2.5')
        ]))
        result = self.semantics_checker.visit_arit_expr(node)
        self.assertEqual(result, "decimal")

    def test_multiplication_string(self):
        node = (DummyNode('arit_expr',[
            Token('STRING', '"Hello"'),
            Token('MUL_OP', '*'),
            Token('STRING', '" World"')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_arit_expr(node)

    def test_multiplication_boolean(self):
        node = (DummyNode('arit_expr',[
            Token('BOOLEAN', 'true'),
            Token('MUL_OP', '*'),
            Token('BOOLEAN', 'true')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_arit_expr(node)

    def test_multiplication_int_dec(self):
        node = (DummyNode('arit_expr', [
            Token('INT', '1'),
            Token('MUL_OP', '*'),
            Token('FLOAT', '2.5')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_arit_expr(node)

    def test_multiplication_int_str(self):
        node = (DummyNode('arit_expr', [
            Token('INT', '1'),
            Token('MUL_OP', '*'),
            Token('STRING', '"Hi"')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_arit_expr(node)

    def test_multiplication_int_bool(self):
        node = (DummyNode('arit_expr', [
            Token('INT', '1'),
            Token('MUL_OP', '*'),
            Token('BOOLEAN', 'true')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_arit_expr(node)

    def test_multiplication_dec_str(self):
        node = (DummyNode('arit_expr', [
            Token('FLOAT', '1.5'),
            Token('MUL_OP', '*'),
            Token('STRING', '"Hi"')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_arit_expr(node)

    def test_multiplication_dec_bool(self):
        node = (DummyNode('arit_expr', [
            Token('FLOAT', '1.5'),
            Token('MUL_OP', '*'),
            Token('BOOLEAN', 'true')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_arit_expr(node)

    def test_multiplication_str_bool(self):
        node = (DummyNode('arit_expr', [
            Token('STRING', '"Hi"'),
            Token('MUL_OP', '*'),
            Token('BOOLEAN', 'true')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_arit_expr(node)

    def test_division_integer(self):
        node = (DummyNode('arit_expr', [
            Token('INT', '1'),
            Token('MUL_OP', '/'),
            Token('INT', '2'),
        ]))
        result = self.semantics_checker.visit_arit_expr(node)
        self.assertEqual(result, "decimal")

    def test_division_decimal(self):
        node = (DummyNode('arit_expr', [
            Token('FLOAT', '1.5'),
            Token('MUL_OP', '/'),
            Token('FLOAT', '2.5')
        ]))
        result = self.semantics_checker.visit_arit_expr(node)
        self.assertEqual(result, "decimal")

    def test_division_string(self):
        node = (DummyNode('arit_expr', [
            Token('STRING', '"Hello"'),
            Token('MUL_OP', '/'),
            Token('STRING', '" World"')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_arit_expr(node)

    def test_division_bool(self):
        node = (DummyNode('arit_expr', [
            Token('BOOLEAN', 'true'),
            Token('MUL_OP', '/'),
            Token('BOOLEAN', 'true')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_arit_expr(node)

    def test_division_int_dec(self):
        node = (DummyNode('arit_expr', [
            Token('INT', '1'),
            Token('MUL_OP', '/'),
            Token('FLOAT', '2.5')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_arit_expr(node)

    def test_division_int_str(self):
        node = (DummyNode('arit_expr', [
            Token('INT', '1'),
            Token('MUL_OP', '/'),
            Token('STRING', '"Hi"')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_arit_expr(node)

    def test_division_int_bool(self):
        node = (DummyNode('arit_expr', [
            Token('INT', '1'),
            Token('MUL_OP', '/'),
            Token('BOOLEAN', 'true')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_arit_expr(node)

    def test_division_dec_str(self):
        node = (DummyNode('arit_expr', [
            Token('FLOAT', '1.5'),
            Token('MUL_OP', '/'),
            Token('STRING', '"Hi"')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_arit_expr(node)

    def test_division_dec_bool(self):
        node = (DummyNode('arit_expr', [
            Token('FLOAT', '1.5'),
            Token('MUL_OP', '/'),
            Token('BOOLEAN', 'true')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_arit_expr(node)

    def test_division_str_bool(self):
        node = (DummyNode('arit_expr', [
            Token('STRING', '"Hi"'),
            Token('MUL_OP', '/'),
            Token('BOOLEAN', 'true')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_arit_expr(node)

    def test_modulo_integer(self):
        node = (DummyNode('arit_expr', [
            Token('INT', '1'),
            Token('MUL_OP', '%'),
            Token('INT', '2'),
        ]))
        result = self.semantics_checker.visit_arit_expr(node)
        self.assertEqual(result, "integer")

    def test_modulo_decimal(self):
        node = (DummyNode('arit_expr', [
            Token('FLOAT', '1.5'),
            Token('MUL_OP', '%'),
            Token('FLOAT', '2.5')
        ]))
        result = self.semantics_checker.visit_arit_expr(node)
        self.assertEqual(result, "decimal")

    def test_modulo_string(self):
        node = (DummyNode('arit_expr', [
            Token('STRING', '"Hello"'),
            Token('MUL_OP', '%'),
            Token('STRING', '" World"')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_arit_expr(node)

    def test_modulo_boolean(self):
        node = (DummyNode('arit_expr', [
            Token('BOOLEAN', 'true'),
            Token('MUL_OP', '%'),
            Token('BOOLEAN', 'true')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_arit_expr(node)

    def test_modulo_int_dec(self):
        node = (DummyNode('arit_expr', [
            Token('INT', '1'),
            Token('MUL_OP', '%'),
            Token('FLOAT', '2.5')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_arit_expr(node)

    def test_modulo_int_str(self):
        node = (DummyNode('arit_expr', [
            Token('INT', '1'),
            Token('MUL_OP', '%'),
            Token('STRING', '"Hi"')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_arit_expr(node)

    def test_modulo_int_bool(self):
        node = (DummyNode('arit_expr', [
            Token('INT', '1'),
            Token('MUL_OP', '%'),
            Token('BOOLEAN', 'true')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_arit_expr(node)

    def test_modulo_dec_str(self):
        node = (DummyNode('arit_expr', [
            Token('FLOAT', '1.5'),
            Token('MUL_OP', '%'),
            Token('STRING', '"Hi"')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_arit_expr(node)

    def test_modulo_dec_bool(self):
        node = (DummyNode('arit_expr', [
            Token('FLOAT', '1.5'),
            Token('MUL_OP', '%'),
            Token('BOOLEAN', 'true')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_arit_expr(node)

    def test_modulo_str_bool(self):
        node = (DummyNode('arit_expr', [
            Token('STRING', '"Hi"'),
            Token('MUL_OP', '%'),
            Token('BOOLEAN', 'true')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_arit_expr(node)

    def test_subtraction_integer(self):
        node = (DummyNode('arit_expr', [
            Token('INT', '1'),
            Token('ADD_OP', '-'),
            Token('INT', '2'),
        ]))
        result = self.semantics_checker.visit_arit_expr(node)
        self.assertEqual(result, "integer")


    def test_subtraction_decimal(self):
        node = (DummyNode('arit_expr', [
            Token('FLOAT', '1.5'),
            Token('ADD_OP', '-'),
            Token('FLOAT', '2.5')
        ]))
        result = self.semantics_checker.visit_arit_expr(node)
        self.assertEqual(result, "decimal")


    def test_subtraction_string(self):
        node = (DummyNode('arit_expr', [
            Token('STRING', '"Hello"'),
            Token('ADD_OP', '-'),
            Token('STRING', '" World"')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_arit_expr(node)

    def test_subtraction_boolean(self):
        node = (DummyNode('arit_expr', [
            Token('BOOLEAN', 'true'),
            Token('ADD_OP', '-'),
            Token('BOOLEAN', 'true')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_arit_expr(node)

    def test_subtraction_int_dec(self):
        node = (DummyNode('arit_expr', [
            Token('INT', '1'),
            Token('ADD_OP', '-'),
            Token('FLOAT', '2.5')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_arit_expr(node)


    def test_subtraction_int_str(self):
        node = (DummyNode('arit_expr', [
            Token('INT', '1'),
            Token('ADD_OP', '-'),
            Token('STRING', '"Hi"')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_arit_expr(node)

    def test_subtraction_int_bool(self):
        node = (DummyNode('arit_expr', [
            Token('INT', '1'),
            Token('ADD_OP', '-'),
            Token('BOOLEAN', 'true')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_arit_expr(node)

    def test_subtraction_dec_str(self):
        node = (DummyNode('arit_expr', [
            Token('FLOAT', '1.5'),
            Token('ADD_OP', '-'),
            Token('STRING', '"Hi"')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_arit_expr(node)

    def test_subtraction_dec_bool(self):
        node = (DummyNode('arit_expr', [
            Token('FLOAT', '1.5'),
            Token('ADD_OP', '-'),
            Token('BOOLEAN', 'true')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_arit_expr(node)

    def test_subtraction_str_bool(self):
        node = (DummyNode('arit_expr', [
            Token('STRING', '"Hi"'),
            Token('ADD_OP', '-'),
            Token('BOOLEAN', 'true')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_arit_expr(node)

    def test_addition_integer(self):
        node = (DummyNode('arit_expr', [
            Token('INT', '1'),
            Token('ADD_OP', '+'),
            Token('INT', '2'),
        ]))
        result = self.semantics_checker.visit_arit_expr(node)
        self.assertEqual(result, "integer")

    def test_addition_decimal(self):
        node = (DummyNode('arit_expr', [
            Token('FLOAT', '1.5'),
            Token('ADD_OP', '+'),
            Token('FLOAT', '2.5')
        ]))
        result = self.semantics_checker.visit_arit_expr(node)
        self.assertEqual(result, "decimal")

    def test_addition_string(self):
        node = (DummyNode('arit_expr', [
            Token('STRING', '"Hello"'),
            Token('ADD_OP', '+'),
            Token('STRING', '" World"')
        ]))
        result = self.semantics_checker.visit_arit_expr(node)
        self.assertEqual(result, "string")

    def test_addition_boolean(self):
        node = (DummyNode('arit_expr', [
            Token('BOOLEAN', 'true'),
            Token('ADD_OP', '+'),
            Token('BOOLEAN', 'true')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_arit_expr(node)

    def test_addition_int_dec(self):
        node = (DummyNode('arit_expr', [
            Token('INT', '1'),
            Token('ADD_OP', '+'),
            Token('FLOAT', '2.5')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_arit_expr(node)

    def test_addition_int_str(self):
        node = (DummyNode('arit_expr', [
            Token('INT', '1'),
            Token('ADD_OP', '+'),
            Token('STRING', '"Hi"')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_arit_expr(node)

    def test_addition_int_bool(self):
        node = (DummyNode('arit_expr', [
            Token('INT', '1'),
            Token('ADD_OP', '+'),
            Token('BOOLEAN', 'true')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_arit_expr(node)

    def test_addition_dec_str(self):
        node = (DummyNode('arit_expr', [
            Token('FLOAT', '1.5'),
            Token('ADD_OP', '+'),
            Token('STRING', '"Hi"')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_arit_expr(node)

    def test_addition_dec_bool(self):
        node = (DummyNode('arit_expr', [
            Token('FLOAT', '1.5'),
            Token('ADD_OP', '+'),
            Token('BOOLEAN', 'true')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_arit_expr(node)

    def test_addition_str_bool(self):
        node = (DummyNode('arit_expr', [
            Token('STRING', '"Hi"'),
            Token('ADD_OP', '+'),
            Token('BOOLEAN', 'true')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_arit_expr(node)

class test_compare_expr(unittest.TestCase):
    def setUp(self):
        class TestSemantics(SemanticsChecker):
            def visit(self, node):
                return super().visit(node)
        self.semantics_checker = TestSemantics()

    def test_equal_integer(self):
        node = (DummyNode('compare_expr', [
            Token('INT', '1'),
            Token('EQ_OP', '=='),
            Token('INT', '1')
        ]))
        result = self.semantics_checker.visit_compare_expr(node)
        self.assertEqual(result, 'boolean')

    def test_equal_decimal(self):
        node = (DummyNode('compare_expr', [
            Token('FLOAT', '1.5'),
            Token('EQ_OP', '=='),
            Token('FLOAT', '1.5')
        ]))
        result = self.semantics_checker.visit_compare_expr(node)
        self.assertEqual(result, 'boolean')

    def test_equal_string(self):
        node = (DummyNode('compare_expr', [
            Token('STRING', '"Hi"'),
            Token('EQ_OP', '=='),
            Token('STRING', '"Hi"')
        ]))
        result = self.semantics_checker.visit_compare_expr(node)
        self.assertEqual(result, 'boolean')

    def test_equal_boolean(self):
        node = (DummyNode('compare_expr', [
            Token('STRING', '"Hi"'),
            Token('EQ_OP', '=='),
            Token('BOOLEAN', 'true')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_compare_expr(node)

    def test_equal_int_dec(self):
        node = (DummyNode('arit_expr', [
            Token('INT', '1'),
            Token('EQ_OP', '=='),
            Token('FLOAT', '2.5')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_compare_expr(node)

    def test_equal_int_str(self):
        node = (DummyNode('arit_expr', [
            Token('INT', '1'),
            Token('EQ_OP', '=='),
            Token('STRING', '"Hi"')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_compare_expr(node)

    def test_equal_int_bool(self):
        node = (DummyNode('arit_expr', [
            Token('INT', '1'),
            Token('EQ_OP', '=='),
            Token('BOOLEAN', 'true')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_compare_expr(node)

    def test_equal_dec_str(self):
        node = (DummyNode('arit_expr', [
            Token('FLOAT', '1.5'),
            Token('EQ_OP', '=='),
            Token('STRING', '"Hi"')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_compare_expr(node)

    def test_equal_dec_bool(self):
        node = (DummyNode('arit_expr', [
            Token('FLOAT', '1.5'),
            Token('EQ_OP', '=='),
            Token('BOOLEAN', 'true')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_compare_expr(node)

    def test_equal_str_bool(self):
        node = (DummyNode('arit_expr', [
            Token('STRING', '"Hi"'),
            Token('EQ_OP', '=='),
            Token('BOOLEAN', 'true')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_compare_expr(node)

    def test_not_equal_integer(self):
        node = (DummyNode('compare_expr', [
            Token('INT', '1'),
            Token('EQ_OP', '!='),
            Token('INT', '1')
        ]))
        result = self.semantics_checker.visit_compare_expr(node)
        self.assertEqual(result, 'boolean')

    def test_not_equal_decimal(self):
        node = (DummyNode('compare_expr', [
            Token('FLOAT', '1.5'),
            Token('EQ_OP', '!='),
            Token('FLOAT', '1.5')
        ]))
        result = self.semantics_checker.visit_compare_expr(node)
        self.assertEqual(result, 'boolean')

    def test_not_equal_string(self):
        node = (DummyNode('compare_expr', [
            Token('STRING', '"Hi"'),
            Token('EQ_OP', '!='),
            Token('STRING', '"Hi"')
        ]))
        result = self.semantics_checker.visit_compare_expr(node)
        self.assertEqual(result, 'boolean')

    def test_not_equal_boolean(self):
        node = (DummyNode('compare_expr', [
            Token('STRING', '"Hi"'),
            Token('EQ_OP', '!='),
            Token('BOOLEAN', 'true')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_compare_expr(node)

    def test_not_equal_int_dec(self):
        node = (DummyNode('arit_expr', [
            Token('INT', '1'),
            Token('EQ_OP', '!='),
            Token('FLOAT', '2.5')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_compare_expr(node)

    def test_not_equal_int_str(self):
        node = (DummyNode('arit_expr', [
            Token('INT', '1'),
            Token('EQ_OP', '!='),
            Token('STRING', '"Hi"')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_compare_expr(node)

    def test_not_equal_int_bool(self):
        node = (DummyNode('arit_expr', [
            Token('INT', '1'),
            Token('EQ_OP', '!='),
            Token('BOOLEAN', 'true')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_compare_expr(node)

    def test_not_equal_dec_str(self):
        node = (DummyNode('arit_expr', [
            Token('FLOAT', '1.5'),
            Token('EQ_OP', '!='),
            Token('STRING', '"Hi"')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_compare_expr(node)

    def test_not_equal_dec_bool(self):
        node = (DummyNode('arit_expr', [
            Token('FLOAT', '1.5'),
            Token('EQ_OP', '!='),
            Token('BOOLEAN', 'true')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_compare_expr(node)

    def test_not_equal_str_bool(self):
        node = (DummyNode('arit_expr', [
            Token('STRING', '"Hi"'),
            Token('EQ_OP', '!='),
            Token('BOOLEAN', 'true')
        ]))
        with self.assertRaises(TypeError_):
            self.semantics_checker.visit_compare_expr(node)