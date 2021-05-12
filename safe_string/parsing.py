#!/usr/bin/env python3

import ast
import os

def _wrap(node):
    return ast.Call(
        func=ast.Attribute(value=ast.Name(id="safe_string", ctx=ast.Load()),
                           attr="safe_string._new_trusted", ctx=ast.Load()),
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


def replace_safe_str(code):
    tree = ast.parse(code)
    tree.body.insert(0, ast.Import(names=[ast.alias(name='sys')]))
    tree.body.insert(1, ast.Import(names=[ast.alias(name='safe_string', asname='safe_string')]))
    tree.body.insert(2, ast.Import(names=[ast.alias(name='sql')]))
    tree.body.insert(3, ast.Import(names=[ast.alias(name='safe_execute')]))
    tree.body.insert(4, ast.ImportFrom(module='sql', names=[ast.alias(name='has_sqli')], level=0))
    SafeStringVisitor().visit(tree)
    ast.fix_missing_locations(tree)
    tree.body.insert(1, ast.parse("sys.path.insert(1, \'{path}\')".format(path=os.environ.get('SAFE_STRING'))))
    return ast.unparse(tree)
