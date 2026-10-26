"""Static guard: symmetry tables may only be indexed after check_symmetry (ADR 0015).

The tables (HEX_SYMMETRIES, ...) are plain tuples, so `table[-1]` silently means
symmetry 11. They are kept as tuples on purpose, so this test enforces the
convention instead: in every function of non-test code, each use of a table must
be a direct `TABLE[...]` subscript, and a call to `check_symmetry` must come
before that subscript is evaluated (earlier in the function, or inside the
subscript itself). Module-level code (table construction) is exempt.

Limits: it checks that a call exists, not that the checked value is the one used.
A line that is safe for another reason can say why with `# symmetry-ok: <reason>`.
"""

import ast
from pathlib import Path

ROOT = Path(__file__).parents[2]
TABLES = {"HEX_SYMMETRIES", "VERTEX_SYMMETRIES", "EDGE_SYMMETRIES", "INVERSE_SYMMETRY"}
GUARD = "check_symmetry"
MARKER = "symmetry-ok"
SKIPPED_DIRS = {".venv", ".git", "tests", "node_modules", "__pycache__", "build", "dist"}
FUNCTIONS = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)


def _name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def violations(source: str, filename: str = "<source>") -> list[str]:
    tree = ast.parse(source)
    lines = source.splitlines()
    parents = {child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
    found: list[str] = []
    for node in ast.walk(tree):
        if _name(node) not in TABLES:
            continue
        func: ast.AST | None = parents.get(node)
        while func is not None and not isinstance(func, FUNCTIONS):
            func = parents.get(func)
        if func is None or MARKER in lines[node.lineno - 1]:  # type: ignore[attr-defined]
            continue  # module-level construction, or explicitly marked
        where = f"{filename}:{node.lineno}"  # type: ignore[attr-defined]
        parent = parents[node]
        if not (isinstance(parent, ast.Subscript) and parent.value is node):
            found.append(f"{where}: {_name(node)} must be indexed directly, not aliased or passed")
            continue
        end = (parent.end_lineno or 0, parent.end_col_offset or 0)
        guarded = any(
            isinstance(call, ast.Call)
            and _name(call.func) == GUARD
            and (call.lineno, call.col_offset) < end
            for call in ast.walk(func)
        )
        if not guarded:
            found.append(f"{where}: {_name(node)}[...] used before {GUARD}(s) in this function")
    return found


def _source_files() -> list[Path]:
    return [
        path for path in ROOT.rglob("*.py") if not SKIPPED_DIRS & set(path.relative_to(ROOT).parts)
    ]


# --- The real code ----------------------------------------------------------


def test_no_unchecked_direct_indexing_of_symmetry_tables() -> None:
    found = [v for path in _source_files() for v in violations(path.read_text(), str(path))]
    assert found == [], "\n".join(found)


def test_the_scan_covers_the_engine_and_is_not_vacuous() -> None:
    files = {p.relative_to(ROOT).as_posix() for p in _source_files()}
    assert {"engine/symmetry.py", "engine/topology.py"} <= files
    # Removing the guard from the real code must be caught.
    source = (ROOT / "engine/symmetry.py").read_text().replace(GUARD, "int")
    assert len(violations(source)) >= 3


# --- The checker itself -----------------------------------------------------


def test_unchecked_index_is_a_violation() -> None:
    assert len(violations("def f(s):\n    return t.HEX_SYMMETRIES[s]\n")) == 1
    assert len(violations("def f(s):\n    return HEX_SYMMETRIES[s][0]\n")) == 1  # bare name too


def test_check_before_use_is_fine() -> None:
    assert violations("def f(s):\n    t.check_symmetry(s)\n    return t.EDGE_SYMMETRIES[s]\n") == []
    assert violations("def f(s):\n    return t.HEX_SYMMETRIES[t.check_symmetry(s)]\n") == []
    assert violations("def f(s):\n    check_symmetry(s)\n    return INVERSE_SYMMETRY[s]\n") == []


def test_check_after_use_is_a_violation() -> None:
    source = "def f(s):\n    x = t.HEX_SYMMETRIES[s]\n    t.check_symmetry(s)\n    return x\n"
    assert len(violations(source)) == 1


def test_check_in_another_function_does_not_count() -> None:
    source = "def a(s):\n    t.check_symmetry(s)\n\ndef b(s):\n    return t.VERTEX_SYMMETRIES[s]\n"
    assert len(violations(source)) == 1


def test_aliasing_or_passing_a_table_is_a_violation() -> None:
    assert len(violations("def f(s):\n    table = t.HEX_SYMMETRIES\n    return table[s]\n")) == 1
    assert len(violations("def f():\n    return list(t.HEX_SYMMETRIES)\n")) == 1
    assert (
        len(violations("def f():\n    for x in (HEX_SYMMETRIES, EDGE_SYMMETRIES):\n        pass\n"))
        == 2
    )


def test_methods_lambdas_and_async_functions_are_checked_too() -> None:
    assert (
        len(violations("class C:\n    def m(self, s):\n        return t.HEX_SYMMETRIES[s]\n")) == 1
    )
    assert len(violations("f = lambda s: t.HEX_SYMMETRIES[s]\n")) == 1
    assert len(violations("async def f(s):\n    return t.HEX_SYMMETRIES[s]\n")) == 1


def test_module_level_construction_and_marked_lines_are_exempt() -> None:
    assert violations("X = tuple(HEX_SYMMETRIES[b][0] for b in range(12))\n") == []
    source = "def f(s):\n    return t.HEX_SYMMETRIES[s]  # symmetry-ok: s comes from range(12)\n"
    assert violations(source) == []
