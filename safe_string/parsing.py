#!/usr/bin/env python3

import ast


def _wrap(node):
    return ast.Call(
        func=ast.Attribute(value=ast.Name(id="safe_string", ctx=ast.Load()),
                           attr="trusted_string", ctx=ast.Load()),
        args=[
            node
        ],
        keywords=[],
    )

class SafeStringVisitor(ast.NodeTransformer):
    def visit_Constant(self, node):
        if isinstance(node.value, str):
            return _wrap(node)
        else:
            return node

    def visit_JoinedStr(self, node):
        """
        Cases to take care of:

        f'{x}'
        f'{x!r:4d}'
        f'{1 + 2}'
        f'{1 + 2:4d}'
        f'{1 + 2!r:4}'
        f'{foo()!r:4}'
        """
        args = []
        fmt_string = ""
        for child in node.values:
            if not isinstance(child, ast.FormattedValue):
                args.append(child.value)

                conv = ""
                for conv_value in ('r', 's', 'a'):
                    if child.conversion == ord(conv_value):
                        conv = "!" + conv_value
                        break

                fmt_string += (
                    "{"
                    + conv
                    + "}"
                )


# code = r"""
# x = 5
# y = 'foo'
# z = "foo\"bar"
# z = input()
# print(x + z)
# d = {}
# d["foo"] = "bar"
# d[u"foo"] = r"bar"
# d[u"foo"] = r"b\ar"
# """

with open("/tmp/sample.py", "r") as fp:
    code = fp.read()


tree = ast.parse(code)
print(ast.dump(tree, indent=4))

# tree.body.insert(0, ast.Import(names=[ast.alias(name='safe_string')]))
# SafeStringVisitor().visit(tree)
# ast.fix_missing_locations(tree)

# print('----------------------------')
# print(ast.dump(tree, indent=4))
# print('----------------------------')
# print(ast.unparse(tree))
