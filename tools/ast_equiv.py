#!/usr/bin/env python3
"""Frozen-logic check: has any source module's *code* changed since a git revision?

Compares every ``.py`` file under a source root at ``<rev>`` with the working tree, at AST
level. Docstrings and comments are ignored, so a documentation or formatting edit is not
reported, while any change to a statement, expression or string literal is.

Typical use, before and after a change that must not alter behaviour::

    python3 tools/ast_equiv.py v1.0.0-nyaysaakshya
    python3 tools/ast_equiv.py v1.0.0-nyaysaakshya --root src/nyaysaakshya/reporting

Exit status is 0 when no module differs, 1 when at least one does, 2 on a usage error.
A module added or removed since ``<rev>`` is reported and also counts as a difference.
"""
from __future__ import annotations

import argparse
import ast
import difflib
import pathlib
import subprocess
import sys

DEFAULT_ROOT = "src/nyaysaakshya"


def _strip_docstrings(tree: ast.AST) -> ast.AST:
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = node.body
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(getattr(body[0], "value", None), ast.Constant)
                    and isinstance(body[0].value.value, str)):
                node.body = body[1:] or [ast.Pass()]
    return tree


def _dump(source: str) -> list:
    return ast.unparse(_strip_docstrings(ast.parse(source))).splitlines()


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], stderr=subprocess.PIPE).decode()


def main(argv: list = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("rev", help="git revision (tag, branch or commit) to compare against")
    parser.add_argument("--root", default=DEFAULT_ROOT,
                        help="source directory to compare (default: %(default)s)")
    args = parser.parse_args(argv)
    root = args.root.rstrip("/")

    try:
        listed = _git("ls-tree", "-r", "--name-only", args.rev, root).split()
    except subprocess.CalledProcessError as exc:
        print("cannot read %s at %s: %s" % (root, args.rev, exc.stderr.decode().strip()),
              file=sys.stderr)
        return 2
    then = {f[len(root):]: f for f in listed if f.endswith(".py")}
    now = {str(p)[len(root):]: str(p) for p in pathlib.Path(root).rglob("*.py")}

    print("modules at %s: %d | working tree: %d" % (args.rev, len(then), len(now)))
    added, removed = sorted(set(now) - set(then)), sorted(set(then) - set(now))
    if added:
        print("ADDED since %s:   %s" % (args.rev, ", ".join(added)))
    if removed:
        print("REMOVED since %s: %s" % (args.rev, ", ".join(removed)))

    differing = 0
    for rel in sorted(set(then) & set(now)):
        before = _dump(_git("show", "%s:%s" % (args.rev, then[rel])))
        after = _dump(pathlib.Path(now[rel]).read_text(encoding="utf-8"))
        if before != after:
            differing += 1
            print("\n### CODE DIFFERS: %s" % rel)
            for line in difflib.unified_diff(before, after, lineterm="", n=0):
                if not line.startswith(("---", "+++", "@@")):
                    print("    " + line[:200])

    changed = differing + len(added) + len(removed)
    print("\nmodules with non-docstring code differences: %d (added %d, removed %d)"
          % (differing, len(added), len(removed)))
    return 1 if changed else 0


if __name__ == "__main__":
    sys.exit(main())
