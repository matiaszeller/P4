import dataclasses

from lark import Tree, Token
from typing import ChainMap, List, Dict
from dataclasses import dataclass

@dataclass #in order to use __init__, __rep__, __eq__ as methods (ex. så skulle init være en setter)

# make an error class, so we can create custom errors!!

#---- defining objects and scopes ----
class FunctionConf:
    #creating the form in which a function should be stored in the stack
    params: List[str]
    ret_type: str
    body: Tree

class StaticSemantics:
    # an initial constructor (__ is a "magic" python constructor => creates an object and initializes that object with these values)
    def __init__(self):
        self._var_map: ChainMap[str, str] = ChainMap() #the single _ means that it is intended for internal use
        self._func_map: Dict[str, FunctionConf] = {} #Dict is used to ensure that we both can make sure that body, returntype, and parameters are compatible and that there are no more that one function of the same name
        self._current_ret_type: str | None = None
        self._in_global: bool = True
        self._func_order: List[str] = [] #in order to later check that the last function indeed is main
        # maybe _saw_syntax: bool = False (but i do not think that, that should be a part "so" late
        # maybe also the case style
        # maybe also the language

#---- methods for handling scope ----
    def enter_scope(self):
        self._var_map = self._var_map.new_child()
        self._in_global = False

    def exit_scope(self):
        self._var_map = self._var_map.parents
        self._in_global = True

    def lookup_variable(self, name: str):#?? does this also work for the function?
        if name in self._var_map:
            return True##need to have something that distinguishes between local and global
        else:
            return False
    def define_variable
    def define_function
    def lookup_variable

    def handle_if_statement
    def handle_while_loop

    def run (self, tree: Tree): #entrypoint from main.py
        self._visit(tree)
        self._post_checks

#---- walking the tree to tokens ----
    def _visit(self, node):
        if isinstance(node, Tree):
            data = node.data
            method_name = f"visit_{data}"
            method = getattr(self, method_name, self._bad_visit)
            return method(node)
        elif isinstance(node, Token):
            return self._visit_token(node)
        return print("structure is not supported")

    def _bad_visit(self, node):
        raise Exception(f"visit_{node.data} is not implemented.")

#---- visiting literals/identifiers ----
    def _visit_token(self, token: Token):
        tokentype = token.type
        if tokentype == "INT":
            return "integer"
        elif tokentype == "FLOAT":
            return "decimal"
        elif tokentype == "BOOLEAN":
            return "boolean"
        elif tokentype == "string":
            return "string"
        elif tokentype == "ID":
            return print("hello")
            #do something that handles i forhold til scopes af en function
        else:
            return print("type does not exist")

#---- visiting the rest?? lol ----
#functions
    def visit_function_definition(self, n: Tree):
        if n.children[0].type == "FUNCTION" and isinstance(n.children[0], Token):
            n.children.pop[0]

#statements
#expressions




# Visit all the different stuff



##Environment (separate from environment in dynamic semantics)

## lookup
#def lookup():
#    e = 7
    ## reversed(TE_stack) looking at the stack reversed to see from the outer most layer
## temporary scope (only at functions!!)
    ## append
#def add_new_scope():
#    TE_stack.append({})

    ## pop
#def exit_scope():
#    TE_stack.pop()


## walk AST





    ## use visitor pattern, traverse all the way down and then work up slowly

## scopes (mapping from identifier to respective decl)
    ## declare_var
        ## add in scope?
    ## lookup_var
        ## look up something in TE or scope? the same(??)
## TE (mapping from identifier to respective type)
    ## declare_var
    ## mainly used for static

## RULES
    ##
    ##



