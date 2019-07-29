#the ast module is fucking useless, because it doesnt include comments
#same with inspect, because it only gives the source, not a tree

with open("main.py") as f:
    text = f.read()

from horast import parse, unparse
print("import")
tree = parse(text)
#print(unparse(tree))
#print(tree)

class Visitor(RecursiveAstVisitor[typed_ast.ast3]):
    def visit_node(self, node):
        if not only_localizable or hasattr(node, 'lineno') and hasattr(node, 'col_offset'):
            print(node)
visitor = Visitor()
visitor.visit(tree)
