import sys
from lark.tree import pydot__tree_to_png
from semantics_checker import SemanticsChecker
from src.p4.interpreter import Interpreter
from src.p4.parse_tree_processor import extract_header, make_parser, ParseTreeProcessor

def main():
    source_file = sys.argv[1] if len(sys.argv) > 1 else "sample.txt"

    try:
        with open(source_file, "r") as src_file:
            sample_input = src_file.read()
    except FileNotFoundError:
        print(f"Error reading file: {source_file}")
        return

    try:
        lang, _ = extract_header(sample_input)
        parser = make_parser(lang)
        tree = parser.parse(sample_input)
        processor = ParseTreeProcessor()
        processed_tree = processor.transform(tree)
        print("Parse Tree:")
        print(tree.pretty())
        print(tree)
        print(processed_tree)
        # Uncomment to update tree.png (need to install requirements.txt and graphviz from https://gitlab.com/api/v4/projects/4207231/packages/generic/graphviz-releases/12.2.1/windows_10_cmake_Release_graphviz-install-12.2.1-win64.exe)
        # pydot__tree_to_png(processed_tree, "tree.png")
    except Exception as e:
        print("Parsing error:", e)
        return

    SemanticsChecker().run(processed_tree)



    interpreter = Interpreter()
    interpreter.visit(processed_tree)

if __name__ == "__main__":
    main()