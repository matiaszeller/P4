from lark import Tree, Token


#Runtime Errors
class DynamicError(Exception):
    """Base class for all dynamic errors"""
    pass

class TreeError(DynamicError): # if node.data yields unimplemented visit_ function
    def __init__(self, node):
        message = 'Youve encountered an error in the interpretation of the AST.'
        if isinstance(node, Tree):
            message += f' No visit function for "{node.data}" nodes.'
        if isinstance(node, Token):
            message += f' Token of type "{node.type}" is not recognized in line {node.line}'
        super().__init__(message)

class OperatorError(DynamicError):
    def __init__(self, operator, line, type):
        message = f'Unknown operator "{operator}" in line {line}.'
        if type == "arithmetic":
            message += f'expected *, /, %, + or -'
        elif type == "comparison":
            message += f'expected ==, !=, <, >, <=, or >=.'
        elif type == "logical":
            message += f'expected "and" or "or"'
        super().__init__(message)

class ArrayIndexError(DynamicError):
    def __init__(self, line, column):
        message = f'Array index in line {line}, column {column} does not evaluate to an integer.'
        super().__init__(message)

class ArrayDimensionError(DynamicError):
    def __init__(self, line):
        message = f'Cannot assign non-list value to array in line {line}'
        super().__init__(message)

class BooleanError(DynamicError):
    def __init__(self, value, line=None, column=None):
        message = f'Boolean of value "{value}"'
        if line is not None:
            message += f' in line {line}'
            if column is not None:
                message += f', column {column}'
        message += ' is neither true nor false.'
        super().__init__(message)

class UnknownTypeError(DynamicError):
    def __init__(self, type, line=None, column=None):
        message = f'Unknown type "{type}"'
        if line is not None:
            message += f' in line {line}'
            if column is not None:
                message += f', column {column}'
        super().__init__(message)

class DuplicateNameError(DynamicError):
    def __init__(self, name, line=None):
        message = f'Duplicate name "{name}"'
        if line is not None:
            message += f' in line {line}'
        super().__init__(message)

class UndeclaredNameError(DynamicError):
    def __init__(self, name, line=None):
        message = f'Undeclared name "{name}"'
        if line is not None:
            message += f' in line {line}'
        super().__init__(message)

class OverIndexedError(DynamicError):
    def __init__(self, index_size, array_size, line=None):
        message = f'Dimensions of index ({len(index_size)}) exceeds dimensions of array ({array_size}) in line {line}'
        super().__init__(message)

class IndexRangeError(DynamicError):
    def __init__(self, index, limit, line=None):
        message = f'Index value ({index}) exceeds the upper limit of {limit-1} in line {line}'
        super().__init__(message)








