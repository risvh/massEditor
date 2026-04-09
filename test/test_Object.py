import pytest
import massEditor

@pytest.fixture
def b():
    import massEditor
    massEditor._store.state = massEditor._store.State()
    massEditor.init(options=[
        # "regenerate_all",
        # "regenerate_categories",
        # "regenerate_objects",
        # "regenerate_transitions",
        # "regenerate_depths",
        "regenerate_smart",
        ], verbose=False)
    return massEditor._store.state.objects


def test_properties(b):
    import massEditor
    O = massEditor._store.state.objects
    o = O[30]
    assert type(o.id) == int
    assert o.id == 30
    assert type(o.name) == str
    assert o.name == 'Wild Gooseberry Bush'
    assert type(o.spriteID) == massEditor.TrackedList
    assert type(o.spriteID[0]) == int
    a = O[34]
    assert type(a.spriteID) == massEditor.TrackedList
    assert type(a.spriteID[0]) == int


def test_property_change(b):
    import massEditor
    O = massEditor._store.state.objects
    o = O[30]
    assert o.spriteID[0] == 143
    o.spriteID[0] = 999
    assert o.spriteID[0] == 999
    assert str(o.spriteID) == '[999, 153, 154, 155, 156, 157, 158]'
    lineNum = o._lineNums['spriteID'][0]
    line = o._lines[lineNum]
    assert line == 'spriteID=999'
    assert str(o[:]) == ' 0 -1   7.000000,-24.000000    999 BearBlood 0 0 0\n 1  2  17.000000, 18.000000    153 Gooseberry 0 0 0\n 2  0   6.000000, 23.000000    154 Gooseberry 0 0 0\n 3  0  17.000000,  2.000000    155 Gooseberry 0 0 0\n 4  0   7.000000,  7.000000    156 Gooseberry 0 0 0\n 5  0  -4.000000, -5.000000    157 Gooseberry 0 0 0\n 6  0  -6.000000,  8.000000    158 Gooseberry 0 0 0\n'
    
    assert str(o.useVanishIndex) == '1,2,3,4,5,6'
    r = o.useVanishIndex.pop(3)
    assert r == 4
    assert str(o.useVanishIndex) == '1,2,3,5,6'
    assert o.linesByTag('useVanishIndex') == 'useVanishIndex=1,2,3,5,6'
    
def test_spriteManipulation(b):
    import massEditor
    O = massEditor._store.state.objects
    o = O[30]
    a = O[434]
    assert str(a[:]) == ' 0 -1  -1.000000, -6.000000    791 Box 0 0 0\n 1 -1  -2.000000,-20.000000    790 Box 0 0 0\n'
    assert str(a[:1]) == ' 0 -1  -1.000000, -6.000000    791 Box 0 0 0\n'
    assert str(a[1]) == ' 0 -1  -2.000000,-20.000000    790 Box 0 0 0\n'
    o = o._insertSprites(2, a[:])
    assert str(o[:]) == ' 0 -1   7.000000,-24.000000    143 BerryBush 0 3 19\n 1  4  17.000000, 18.000000    153 Gooseberry 0 0 0\n 2 -1  -1.000000, -6.000000    791 Box 0 0 0\n 3 -1  -2.000000,-20.000000    790 Box 0 0 0\n 4  0   6.000000, 23.000000    154 Gooseberry 0 0 0\n 5  0  17.000000,  2.000000    155 Gooseberry 0 0 0\n 6  0   7.000000,  7.000000    156 Gooseberry 0 0 0\n 7  0  -4.000000, -5.000000    157 Gooseberry 0 0 0\n 8  0  -6.000000,  8.000000    158 Gooseberry 0 0 0\n'
    
def test_mapChance(b):
    import massEditor
    O = massEditor._store.state.objects
    o = O[33]
    
    assert str(o.mapChance) == '1.000000#biomes_0,3,4,5'
    assert type(o.mapChance) == massEditor.MapChance
    assert o._lines[o._lineNums['mapChance']] == 'mapChance=1.000000#biomes_0,3,4,5'
    
    o.mapChance.chance = 2.0
    
    assert str(o.mapChance) == '2.000000#biomes_0,3,4,5'
    assert o._lines[o._lineNums['mapChance']] == 'mapChance=2.000000#biomes_0,3,4,5'
    
    assert type(o.mapChance.biomes) == tuple
    assert str(o.mapChance.biomes) == '(0, 3, 4, 5)'
    
    oldList = list(o.mapChance.biomes)
    oldList.append(7)
    o.mapChance.biomes = tuple(oldList)
    
    assert type(o.mapChance.biomes) == tuple
    assert str(o.mapChance) == '2.000000#biomes_0,3,4,5,7'
    assert o._lines[o._lineNums['mapChance']] == 'mapChance=2.000000#biomes_0,3,4,5,7'

def test_sounds(b):
    import massEditor
    O = massEditor._store.state.objects
    
    o = O[34]
    
    assert str(o.sounds) == '45:0.250000,-1:0.250000,-1:0.250000,-1:1.000000'
    assert type(o.sounds) == massEditor.Sounds
    assert str(o.sounds.creation) == '45:0.250000'
    assert type(o.sounds.creation) == massEditor.Sound
    assert o.sounds.creation.sound == 45
    assert o.sounds.creation.volume == 0.25
    
    o.sounds.creation.volume = 1.0
    
    assert str(o.sounds) == '45:1.000000,-1:0.250000,-1:0.250000,-1:1.000000'
    assert type(o.sounds) == massEditor.Sounds
    assert str(o.sounds.creation) == '45:1.000000'
    assert type(o.sounds.creation) == massEditor.Sound
    assert o.sounds.creation.sound == 45
    assert o.sounds.creation.volume == 1.0
    
    
    o = O[6701]
    
    assert str(o.sounds) == '198:0.250000,588:0.080000#591:0.080000#594:0.080000#595:0.080000,-1:0.0,-1:0.0'
    assert type(o.sounds) == massEditor.Sounds
    assert str(o.sounds.using) == '[588:0.080000, 591:0.080000, 594:0.080000, 595:0.080000]'
    assert type(o.sounds.using) == list
    assert str(o.sounds.using[1]) == '591:0.080000'
    assert type(o.sounds.using[1]) == massEditor.Sound
    assert o.sounds.using[1].sound == 591
    assert o.sounds.using[1].volume == 0.08
    
    o.sounds.using[1].volume = 1.0
    
    assert str(o.sounds) == '198:0.250000,588:0.080000#591:1.000000#594:0.080000#595:0.080000,-1:0.0,-1:0.0'
    assert type(o.sounds) == massEditor.Sounds
    assert str(o.sounds.using) == '[588:0.080000, 591:1.000000, 594:0.080000, 595:0.080000]'
    assert type(o.sounds.using) == list
    assert str(o.sounds.using[1]) == '591:1.000000'
    assert type(o.sounds.using[1]) == massEditor.Sound
    assert o.sounds.using[1].sound == 591
    assert o.sounds.using[1].volume == 1.0
    
def test_spritesDrawnBehind(b):
    import massEditor
    from massEditor import TrackedIndexList
    O = massEditor._store.state.objects
    o = O[17619]
    assert type(o.spritesDrawnBehind) == TrackedIndexList
    assert str(o.spritesDrawnBehind) == '0,1,2'
    o.spritesDrawnBehind.append(3)
    assert str(o.spritesDrawnBehind) == '0,1,2,3'
    assert o.linesByTag('spritesDrawnBehind') == 'spritesDrawnBehind=0,1,2,3'
    o.spritesDrawnBehind[0] = 4
    assert str(o.spritesDrawnBehind) == '4,1,2,3'
    assert o.linesByTag('spritesDrawnBehind') == 'spritesDrawnBehind=4,1,2,3'
    
def test_tapoutTrigger(b):
    import massEditor
    from massEditor import TapoutTrigger
    O = massEditor._store.state.objects
    o = O[12703]
    assert type(o.tapoutTrigger) == TapoutTrigger
    assert str(o.tapoutTrigger) == '1#0,3,3,1'
    
    o.tapoutTrigger.parameters = '1,2,3'
    
    assert type(o.tapoutTrigger) == TapoutTrigger
    assert str(o.tapoutTrigger) == '1#1,2,3'
    
    o.tapoutTrigger.parameters = [1, 2, 3, 4]
    assert str(o.tapoutTrigger) == '1#1,2,3,4'
    
    assert o.linesByTag('tapoutTrigger') == 'tapoutTrigger=1#1,2,3,4'

def test_draw(b):
    import massEditor
    O = massEditor._store.state.objects
    o = O[3338]
    assert o.draw().height == 96
    
def test_foodValue(b):
    import massEditor
    from massEditor import FoodValue
    O = massEditor._store.state.objects
    o = O[31]
    assert type(o.foodValue) == FoodValue
    assert str(o.foodValue) == '1'
    
    o = O[6948]
    assert str(o.foodValue) == '2,13'
    o.foodValue.base = 3
    assert str(o.foodValue) == '3,13'
    assert o.foodValue.total == 16
    assert o.linesByTag('foodValue') == 'foodValue=3,13'
    
def test_numUses(b):
    import massEditor
    from massEditor import NumUses
    O = massEditor._store.state.objects
    o = O[663]
    assert type(o.numUses) == NumUses
    assert str(o.numUses) == '5,0.125000'
    
    o.numUses.num = 6
    assert str(o.numUses) == '6,0.125000'
    o.numUses.chance = 0.5
    assert str(o.numUses) == '6,0.500000'
    assert o.linesByTag('numUses') == 'numUses=6,0.500000'