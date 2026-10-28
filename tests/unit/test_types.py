from engine.types import Resource, Terrain, terrain_resource


def test_each_terrain_produces_its_resource_and_the_desert_nothing() -> None:
    # rules-spec 1: hills brick, forest lumber, mountains ore, fields grain, pasture wool.
    assert terrain_resource(Terrain.HILLS) is Resource.BRICK
    assert terrain_resource(Terrain.FOREST) is Resource.LUMBER
    assert terrain_resource(Terrain.MOUNTAINS) is Resource.ORE
    assert terrain_resource(Terrain.FIELDS) is Resource.GRAIN
    assert terrain_resource(Terrain.PASTURE) is Resource.WOOL
    assert terrain_resource(Terrain.DESERT) is None
