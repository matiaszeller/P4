# a file for all errors

# customized parsing errors




# static errors
class StaticError(Exception):
    """ the form/base of all errors"""

    def __init__(self, message: str, line: int | None = None):
        if line is not None:
            message = f"At line {line}: {message}"
        super().__init__(message)
        self.line = line

        """
        --- in case we want to capture more that one line ---

        if end_line is not None:
            message = f"At line {start_line}-{end_line}: {message}"
        else:
            message = f"At line {start_line}: {message}"
    super().__init__(message)
    self.start_line = start_line
    self.end_line = end_line """


# ---- meaning ----
class TypeError_(StaticError):
    """ if types does not match """
    pass


class ScopeErrorCategory(StaticError):
    """if variables is not defined/or defined more than once"""

class FunctionAlreadyInScopeError(ScopeErrorCategory):
    def __init__(self, name: str, line: int | None = None):
        # how can i access the other function.line?
        message = (f"Function {name} is already defined in line {duplicate_line}")
        super().__init__(message, line)


# ---- structure ----
class CaseErrorCategory(StaticError):
    """if ID does not align with casing specification"""
    pass


class StructureErrorCategory(StaticError):
    """if well-formedness is not obtained"""


class DuplicateSyntaxError(StructureErrorCategory):
    def __init__(self, line: int | None = None):
        message = f"Syntax choices has been defined more than once."
        super().__init__(message, line)


class LanguageSpecificationError(StructureErrorCategory):
    def __init__(self, lang: str, line: int | None = None):
        languages_list = ','.join(str(n) for n in BasicValues.LANGUAGES)
        message = (f"The specified language {lang} is not supported. "
                   f"Please provide one of the following languages instead: {languages_list}"
                   )
        super().__init__(message, line)

class CaseSpecificationError(StructureErrorCategory):
    def __init__(self, case: str, line: int | None = None):
        cases_list = ','.join(str(n) for n in BasicValues.CASESTYLES)
        message = (f"The specified case {case} is not supported. "
                   f"Please provide one of the following case styles instead: {cases_list}"
                   )
        super().__init__(message, line)


class TopLevelDefError(StructureErrorCategory):
    def __init__(self, node, line: int | None = None):
        # evt. switch or if else for hver mulig ting(??)
        """ declaration_stmt, assignment_stmt, if_stmt, output_stmt, expr_stmt, input_stmt, content"""
        type_ = node.data

        if type_ == "declaration_stmt":
            name = node.children[1].value
            error_name = f"declaration of {name}"
        elif type_ == "assignment_stmt":
            name = node.children[0].children[0].value
            error_name = f"assignment of {name}"
        elif type_ == "if_stmt":
            error_name = "if statement"
        elif type_ == "output_stmt":
            error_name = "output statement"
        elif type_ == "expr_stmt":
            error_name = "expression"
        elif type_ == "input_stmt":
            error_name = "input statement"
        else:
            error_name = "content"

        message = (f"Only syntax specifications and function definitions are allowed at top level. "
                   f"The {error_name} at {line} must be defined within the scope of a function."
                   )
        super().__init__(message, line)


class NestedFunctionsError(StructureErrorCategory):
    def __init__(self, node, line: int | None = None):
        message = (f"Function {inner_function} is declared within function {outer_function} on line {outer_function_line}."
                   f"Defining functions within other functions is not allowed."
                   f"Alternatively define {inner_function} outside the scope of {outer_function}."
                   f"To use {inner_function} in any other function try using a function call: {inner_function}()"
                   )
        super.__init__(message, line)

class NoReturnTypeError(StructureErrorCategory):
    def __init__(self, name, line: int | None = None):
        message = f"Function {name} has no return type specified."
        super().__init__(message, line)

# dynamic errors