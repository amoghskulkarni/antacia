from collections import Counter

from engine import topology as t

# Corner offsets from a hex centre in half-units (x: sqrt(3)/2 size, y: size/2),
# clockwise from the top: N, NE, SE, S, SW, NW. Independent of the naming formulas.
CORNER_OFFSETS = [(0, -2), (1, -1), (1, 1), (0, 2), (-1, 1), (-1, -1)]


def test_counts() -> None:
    assert len(t.HEXES) == t.NUM_HEXES == 19
    assert len(t.VERTICES) == t.NUM_VERTICES == 54
    assert len(t.EDGES) == t.NUM_EDGES == 72


def test_hexes_are_row_major_top_to_bottom_left_to_right() -> None:
    rows = [3, 4, 5, 4, 3]
    ys = [t.HEX_POS[h][1] for h in range(t.NUM_HEXES)]
    assert [n for n in Counter(ys).values()] == rows
    assert t.HEXES[0] == (0, -2)
    assert t.HEXES[9] == (0, 0)  # centre
    assert t.HEXES[18] == (0, 2)


def test_ids_follow_position_order() -> None:
    def key(p: tuple[int, int]) -> tuple[int, int]:
        return (p[1], p[0])

    for positions in (t.HEX_POS, t.VERTEX_POS, t.EDGE_POS):
        keys = [key(p) for p in positions]
        assert keys == sorted(keys)
        assert len(set(keys)) == len(keys)  # no ties


def test_vertex_names_match_geometry() -> None:
    for h in range(t.NUM_HEXES):
        cx, cy = t.HEX_POS[h]
        expected = [(cx + dx, cy + dy) for dx, dy in CORNER_OFFSETS]
        assert [t.VERTEX_POS[v] for v in t.HEX_VERTICES[h]] == expected


def test_edge_endpoints_are_adjacent_corners() -> None:
    for e in range(t.NUM_EDGES):
        a, b = t.EDGE_VERTICES[e]
        (ax, ay), (bx, by) = t.VERTEX_POS[a], t.VERTEX_POS[b]
        # Vertical side (W) or one of the four slanted sides.
        assert (abs(ax - bx), abs(ay - by)) in {(0, 2), (1, 1)}
        assert t.EDGE_POS[e] == (ax + bx, ay + by)


def test_hex_neighbors() -> None:
    assert len(t.HEX_NEIGHBORS[9]) == 6  # centre
    assert sorted(Counter(len(n) for n in t.HEX_NEIGHBORS).items()) == [(3, 6), (4, 6), (6, 7)]
    for h, ns in enumerate(t.HEX_NEIGHBORS):
        for n in ns:
            assert h in t.HEX_NEIGHBORS[n]
            shared = set(t.HEX_VERTICES[h]) & set(t.HEX_VERTICES[n])
            assert len(shared) == 2


def test_vertex_hex_incidence() -> None:
    sizes = Counter(len(hs) for hs in t.VERTEX_HEXES)
    assert sizes == {3: 24, 2: 12, 1: 18}
    for v, hs in enumerate(t.VERTEX_HEXES):
        for h in hs:
            assert v in t.HEX_VERTICES[h]


def test_vertex_adjacency_is_symmetric_and_consistent_with_edges() -> None:
    for v, ns in enumerate(t.VERTEX_VERTICES):
        assert len(ns) == (2 if len(t.VERTEX_HEXES[v]) == 1 else 3)
        for n in ns:
            assert v in t.VERTEX_VERTICES[n]
        via_edges = {next(x for x in t.EDGE_VERTICES[e] if x != v) for e in t.VERTEX_EDGES[v]}
        assert via_edges == set(ns)


def test_edge_edges_share_exactly_one_vertex() -> None:
    for e, others in enumerate(t.EDGE_EDGES):
        assert e not in others
        assert 2 <= len(others) <= 4
        for o in others:
            assert len(set(t.EDGE_VERTICES[e]) & set(t.EDGE_VERTICES[o])) == 1


def test_coast_is_a_clockwise_cycle_of_30_edges() -> None:
    assert len(t.COAST) == len(set(t.COAST)) == 30
    for i, e in enumerate(t.COAST):
        nxt = t.COAST[(i + 1) % 30]
        assert len(set(t.EDGE_VERTICES[e]) & set(t.EDGE_VERTICES[nxt])) == 1
    # Starts at the top-left and moves right along the top (clockwise on screen).
    first, second = t.EDGE_POS[t.COAST[0]], t.EDGE_POS[t.COAST[1]]
    assert second[0] > first[0]


def test_harbor_slots_are_coastal_and_never_share_a_vertex() -> None:
    assert len(t.HARBOR_SLOTS) == 9
    coast = set(t.COAST)
    used: set[int] = set()
    for e in t.HARBOR_SLOTS:
        assert e in coast
        a, b = t.EDGE_VERTICES[e]
        assert not {a, b} & used
        used |= {a, b}


def test_harbor_slots_are_the_rulebook_edges_in_clockwise_order() -> None:
    # Verified against the rulebook frame using render_topology().
    assert set(t.HARBOR_SLOTS) == {0, 3, 17, 18, 38, 49, 61, 66, 69}
    harbor_vertices = sorted(v for e in t.HARBOR_SLOTS for v in t.EDGE_VERTICES[e])
    assert harbor_vertices == [0, 1, 3, 5, 10, 11, 15, 16, 26, 32, 33, 38, 42, 46, 47, 49, 51, 52]
    # Slot ids run clockwise from the top left, so a 120-degree rotation shifts slots by 3.
    assert list(t.HARBOR_SLOTS) == sorted(t.HARBOR_SLOTS, key=t.COAST.index)
    assert t.HARBOR_SLOTS[0] == t.COAST[0]


def test_coordinate_lookups_round_trip() -> None:
    for i, h in enumerate(t.HEXES):
        assert t.HEX_ID[h] == i
    for i, v in enumerate(t.VERTICES):
        assert t.VERTEX_ID[v] == i
    for i, e in enumerate(t.EDGES):
        assert t.EDGE_ID[e] == i
