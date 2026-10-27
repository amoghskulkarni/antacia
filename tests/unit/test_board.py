from collections import Counter

from engine import topology as t
from engine.board import (
    HARBOR_TILES,
    TERRAIN_TILES,
    TOKEN_SEQUENCE,
    Board,
    Layout,
    generate_board,
    red_numbers_adjacent,
    render_board,
    spiral,
)
from engine.rng import seed_rng
from engine.types import Harbor, Terrain


def test_component_counts() -> None:
    # rules-spec section 1.
    assert Counter(TERRAIN_TILES) == {
        Terrain.FOREST: 4,
        Terrain.PASTURE: 4,
        Terrain.FIELDS: 4,
        Terrain.HILLS: 3,
        Terrain.MOUNTAINS: 3,
        Terrain.DESERT: 1,
    }
    assert TOKEN_SEQUENCE == (5, 2, 6, 3, 8, 10, 9, 12, 11, 4, 8, 10, 9, 4, 5, 6, 3, 11)
    assert Counter(HARBOR_TILES) == {
        Harbor.GENERIC: 4,
        Harbor.BRICK: 1,
        Harbor.LUMBER: 1,
        Harbor.ORE: 1,
        Harbor.GRAIN: 1,
        Harbor.WOOL: 1,
    }


def test_spiral_visits_every_hex_once_through_neighbours() -> None:
    for corner in range(6):
        path = spiral(corner)
        assert sorted(path) == list(range(t.NUM_HEXES))
        assert len(t.HEX_NEIGHBORS[path[0]]) == 3  # starts on an outer corner
        assert path[-1] == t.HEX_ID[(0, 0)]  # ends in the centre
        for a, b in zip(path, path[1:], strict=False):
            assert b in t.HEX_NEIGHBORS[a]


def test_spiral_runs_counterclockwise() -> None:
    # Corner 0 is the east corner; counterclockwise on screen means moving up first.
    path = spiral(0)
    assert t.HEXES[path[0]] == (2, 0)
    assert t.HEX_POS[path[1]][1] < t.HEX_POS[path[0]][1]


def test_spiral_from_north_east_corner_matches_rulebook() -> None:
    # ADR 0009, verified against the rulebook: counterclockwise from any corner, here NE (h2).
    path = spiral(1)
    assert path == (2, 1, 0, 3, 7, 12, 16, 17, 18, 15, 11, 6, 5, 4, 8, 13, 14, 10, 9)


def test_spiral_skips_the_desert_without_losing_a_token() -> None:
    # ADR 0009: the desert gets no token; the next hex on the spiral takes the next letter.
    # NE corner spiral: h2 h1 h0 h3 h7 h12 h16 h17 h18 h15 h11 h6 h5 h4 h8 h13 h14 h10 h9.
    from engine.board import _place_tokens

    def tokens_with_desert_at(desert: int) -> tuple[int | None, ...]:
        terrains = tuple(
            Terrain.DESERT if h == desert else Terrain.FIELDS for h in range(t.NUM_HEXES)
        )
        return _place_tokens(terrains, 1)

    mid = tokens_with_desert_at(4)  # 14th on the spiral
    assert (mid[5], mid[4], mid[8]) == (9, None, 4)  # M, desert, N
    assert mid[9] == 11  # R still reaches the centre

    start = tokens_with_desert_at(2)  # desert on the start hex
    assert (start[2], start[1]) == (None, 5)  # A moves to the second hex

    centre = tokens_with_desert_at(9)  # desert in the centre
    assert (centre[10], centre[9]) == (11, None)  # R lands just before the centre

    for tokens in (mid, start, centre):
        assert sorted(x for x in tokens if x is not None) == sorted(TOKEN_SEQUENCE)


def test_spiral_starts_differ_per_corner() -> None:
    assert len({spiral(c)[0] for c in range(6)}) == 6


def test_beginner_board_is_fixed_and_draws_no_randomness() -> None:
    rng = seed_rng(123)
    board, after = generate_board(Layout.BEGINNER, rng)
    assert after == rng
    assert board == generate_board(Layout.BEGINNER, seed_rng(999))[0]
    assert Counter(board.terrains) == Counter(TERRAIN_TILES)
    assert sorted(x for x in board.tokens if x is not None) == sorted(TOKEN_SEQUENCE)
    assert board.terrains[board.desert()] is Terrain.DESERT
    assert not red_numbers_adjacent(board)


def test_random_board_consumes_randomness_in_documented_order() -> None:
    from engine.rng import randbelow, shuffle

    rng = seed_rng(5)
    terrains, rng = shuffle(rng, TERRAIN_TILES)
    corner, rng = randbelow(rng, 6)
    harbors, rng = shuffle(rng, HARBOR_TILES)

    board, after = generate_board(Layout.RANDOM, seed_rng(5))
    assert board.terrains == terrains
    assert board.harbors == harbors
    assert after == rng
    tokens = iter(TOKEN_SEQUENCE)
    for h in spiral(corner):
        expected = None if terrains[h] is Terrain.DESERT else next(tokens)
        assert board.tokens[h] == expected


def test_red_numbers_adjacent_detects_neighbouring_six_and_eight() -> None:
    board, _ = generate_board(Layout.BEGINNER, seed_rng(0))
    a = 0
    b = t.HEX_NEIGHBORS[a][0]
    tokens = list(board.tokens)
    tokens[a], tokens[b] = 6, 8
    assert red_numbers_adjacent(Board(board.terrains, tuple(tokens), board.harbors, frame=0))


def test_render_board_shows_rows_tokens_and_harbors() -> None:
    board, _ = generate_board(Layout.BEGINNER, seed_rng(0))
    text = render_board(board)
    lines = text.splitlines()
    hex_rows = [line for line in lines if "[" in line]
    assert [row.count("[") for row in hex_rows] == [3, 4, 5, 4, 3]
    assert "[DE  ]" in text
    assert "harbor frame 0" in lines
    assert sum(line.startswith("harbor ") and ":" in line for line in lines) == 9


def test_spiral_never_puts_red_numbers_side_by_side_for_any_desert_and_corner() -> None:
    # Token placement only depends on the desert's hex and the start corner, so
    # these 19 x 6 cases cover every random board.
    from engine.board import _place_tokens

    for desert in range(t.NUM_HEXES):
        terrains = tuple(
            Terrain.DESERT if h == desert else Terrain.FIELDS for h in range(t.NUM_HEXES)
        )
        for corner in range(6):
            board = Board(terrains, _place_tokens(terrains, corner), HARBOR_TILES, frame=0)
            assert not red_numbers_adjacent(board), (desert, corner)


def test_beginner_harbors_match_the_rulebook() -> None:
    board, _ = generate_board(Layout.BEGINNER, seed_rng(0))
    by_edge = dict(zip(t.HARBOR_FRAMES[0], board.harbors, strict=True))
    assert by_edge == {
        0: Harbor.GENERIC,
        3: Harbor.GRAIN,
        17: Harbor.ORE,
        18: Harbor.LUMBER,
        38: Harbor.GENERIC,
        49: Harbor.BRICK,
        61: Harbor.WOOL,
        66: Harbor.GENERIC,
        69: Harbor.GENERIC,
    }
