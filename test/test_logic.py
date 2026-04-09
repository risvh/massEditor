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


def test_object(b):
    # import massEditor  
    from massEditor import ListOfObjects, search, getObjectsBySprite, getObjectsBySound
    
    r = search('sharp stone')
    assert type(r) == ListOfObjects
    assert len(r) == 2
    r = getObjectsBySprite(515) # clay bowl front sprite
    assert type(r) == ListOfObjects
    r = getObjectsBySound(588) # wooden table use sound
    assert type(r) == ListOfObjects

def test_category(b):
    # import massEditor
    # O = massEditor._store.state.objects
    from massEditor import ListOfObjects
    from massEditor import isCategory, isPattern, isProbSet, getCategoriesOf
    
    assert isCategory(1001) == True # @ Free Lock
    assert isCategory(1601) == False # @ Pile Element
    assert isPattern(1601) == True
    assert isCategory(2095) == False # Perhaps a Fish
    assert isProbSet(2095) == True
    
    r = getCategoriesOf(34) # Sharp Stone
    assert type(r) == ListOfObjects
    assert len(r) == 3
    
def test_transition(b):
    from massEditor import ListOfTransitions
    from massEditor import make, use, getTransitions, getObjectsBySprite
    
    ts = make(6827)
    assert len(ts) == 3
    ts = ts.raw()
    assert len(ts) == 0
    ts = getTransitions(a=-1)
    assert type(ts) == ListOfTransitions