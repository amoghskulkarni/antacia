import re

from engine import topology as t
from engine.board import render_topology

# Scale of the drawing; must match render_topology.
COLS, ROWS = 8, 4  # characters per x half-unit, lines per y half-unit

LABEL = re.compile(r"[Hve]\d+")


def _labels() -> dict[str, tuple[int, int]]:
    """Every id label in the drawing -> (line, centre column)."""
    found: dict[str, tuple[int, int]] = {}
    for line_no, line in enumerate(render_topology().splitlines()):
        for m in LABEL.finditer(line):
            label = m.group()
            assert label not in found, f"{label} drawn twice"
            found[label] = (line_no, m.start() + len(label) // 2)
    return found


def test_every_hex_vertex_and_edge_id_is_drawn_exactly_once() -> None:
    expected = (
        {f"H{i}" for i in range(t.NUM_HEXES)}
        | {f"v{i}" for i in range(t.NUM_VERTICES)}
        | {f"e{i}" for i in range(t.NUM_EDGES)}
    )
    assert set(_labels()) == expected


def test_labels_sit_at_their_true_positions() -> None:
    found = _labels()
    # The drawing is trimmed to its contents, so fix the origin from v0.
    line0 = found["v0"][0] - t.VERTEX_POS[0][1] * ROWS
    col0 = found["v0"][1] - t.VERTEX_POS[0][0] * COLS
    for v, (x, y) in enumerate(t.VERTEX_POS):
        assert found[f"v{v}"] == (y * ROWS + line0, x * COLS + col0), v
    for h, (x, y) in enumerate(t.HEX_POS):
        assert found[f"H{h}"] == (y * ROWS - 1 + line0, x * COLS + col0), h
    for e, (x, y) in enumerate(t.EDGE_POS):  # edge positions are twice the midpoint
        assert found[f"e{e}"] == (y * ROWS // 2 + line0, x * COLS // 2 + col0), e


def test_hex_axial_coordinates_are_printed_under_the_hex_id() -> None:
    lines = render_topology().splitlines()
    found = _labels()
    for h, (q, r) in enumerate(t.HEXES):
        line, col = found[f"H{h}"]
        text = f"({q},{r})"
        start = col - len(text) // 2
        assert lines[line + 2][start : start + len(text)] == text, h


def test_stroke_counts_match_edge_kinds() -> None:
    text = render_topology()
    vertical = sum(t.VERTEX_POS[a][0] == t.VERTEX_POS[b][0] for a, b in t.EDGE_VERTICES)
    slanted = t.NUM_EDGES - vertical
    # A vertical edge spans 8 lines (6 strokes around its label), a slanted one 4 (2 strokes).
    assert text.count("|") == 6 * vertical
    assert text.count("/") + text.count("\\") == 2 * slanted


def test_slanted_strokes_lean_the_way_the_edge_goes() -> None:
    lines = render_topology().splitlines()
    found = _labels()
    for e, (a, b) in enumerate(t.EDGE_VERTICES):
        (top_x, _), (bottom_x, _) = sorted((t.VERTEX_POS[a], t.VERTEX_POS[b]), key=lambda p: p[1])
        if top_x == bottom_x:
            continue
        line, col = found[f"e{e}"]
        # Strokes sit one line above and below the label, a quarter of the way along.
        d = (bottom_x - top_x) * COLS // 4
        stroke = "\\" if bottom_x > top_x else "/"
        assert lines[line - 1][col - d] == stroke, e
        assert lines[line + 1][col + d] == stroke, e


def test_drawing_is_trimmed_and_ordered_top_to_bottom() -> None:
    lines = render_topology().splitlines()
    assert all(line == line.rstrip() for line in lines)
    assert lines[0].split() == ["v0", "v1", "v2"]
    assert lines[-1].split() == ["v51", "v52", "v53"]
    assert min(len(line) - len(line.lstrip()) for line in lines) == 0
