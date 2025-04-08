from lark import Lark, Transformer
from lark.tree import pydot__tree_to_png

# Load grammar
with open("grammar/grammar.lark", "r") as grammar_file:
    grammar = grammar_file.read()

# Lark parser
parser = Lark(grammar, parser='earley', start='start')

# Optional transformer to process the parse tree.
class MyTransformer(Transformer):
    def start(self, items):
        return items

# parse and transformed tree showing tokens
def main():
    try:
        # open test source
        with open("sample.txt", "r") as src_file:
            sample_input = src_file.read()
    except FileNotFoundError:
        print("Error reading file")
        return

    try:
        tree = parser.parse(sample_input)
        transformed_tree = MyTransformer().transform(tree)
        print("Parse Tree:")
        print(tree.pretty())
        print("Transformed Tree:")
        print(transformed_tree)
        pydot__tree_to_png(tree, "tree.png")
    except Exception as e:
        print("Parsing error:", e)

if __name__ == "__main__":
    main()