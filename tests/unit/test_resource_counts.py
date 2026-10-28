from engine.types import Resource, ResourceCounts


def test_get_reads_the_count_for_a_resource() -> None:
    counts = ResourceCounts(brick=1, lumber=2, ore=3, grain=4, wool=5)
    assert [counts.get(r) for r in Resource] == [1, 2, 3, 4, 5]


def test_add_returns_a_new_count_and_leaves_the_original_unchanged() -> None:
    empty = ResourceCounts()
    one_ore = empty.add(Resource.ORE)
    assert one_ore == ResourceCounts(ore=1)
    assert one_ore.add(Resource.ORE, 2) == ResourceCounts(ore=3)
    assert empty == ResourceCounts()


def test_counts_add_and_subtract_per_resource() -> None:
    a = ResourceCounts(brick=2, wool=1)
    b = ResourceCounts(brick=1, grain=3)
    assert a + b == ResourceCounts(brick=3, grain=3, wool=1)
    assert a - b == ResourceCounts(brick=1, grain=-3, wool=1)


def test_total_counts_every_card() -> None:
    assert ResourceCounts(brick=2, ore=1, wool=4).total() == 7
    assert ResourceCounts().total() == 0


def test_uniform_puts_the_same_count_on_every_resource() -> None:
    assert ResourceCounts.uniform(19) == ResourceCounts(19, 19, 19, 19, 19)
