import ast


class SafeStringTransformer(ast.NodeTransformer):
    def visit_Constant(self, node):
        if isinstance(node.value, str):
            return ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id="safe_string", ctx=ast.Load()),
                    attr="trusted_string",
                    ctx=ast.Load()),
                args=[node],
                keywords=[],
            )
        else:
            return node


def wrap_safe(code_str):
    tree = ast.parse(code_str)
    tree.body.insert(0, ast.Import(names=[ast.alias(name='safe_string')]))
    SafeStringTransformer().visit(tree)
    ast.fix_missing_locations(tree)
    return ast.unparse(tree)
