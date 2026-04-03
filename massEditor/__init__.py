"""
A programmatic editor of XHOL game assets.

Example Usage:
    >>> objects[30] # returns the Object Wild Gooseberry Bush which id is 30.
    >>> search("horse cart -outdated") # return a ListOfObjects with names matching the picker-style query.
    >>> use(30) # return a ListOfTransitions how Wild Gooseberry Bush can be used.
    >>> draw(3338) # draw a Glass Bottle.
    >>> Os.filter(lambda o: o.permanent == '0' and o.blocksWalking == '1') # return a ListOfObjects that are blocking but not permanent.
    >>> getTransitions(a=-1) # return a ListOfTransitions that contains all the decay transitions.
    
    >>> # This is how to loop through all the objects
    >>> results = LO() # shorthand for ListOfObjects
    >>> for id, o in O.items():
    >>>   if o.foodValue != '0':
    >>>     results.append(id)

Data stores and Shorthands:
    O / objects - a dict of all objects, key is object id and value is the Object with that id.
    C / categories - a dict of all categories, key is object id of the category's parent object and value is the ListOfObjects that category holds.
    LO / ListOfObjects - a class that is essentially a python list of ids. Prints with id and object name. Has methods to filter and allow set operations.
    LT / ListOfTransitions - a class that is essentially a python list of Transition.
    Os - a ListOfObjects of all objects.
    names - a dict, key is object id and value is the name of the object with that id.
    depths - a dict, key is object id and value is the depth of the object with that id.
    transitions - a dict of all transitions, key is a tuple of (actor, target, flag), value is the corresponding Transition.
    raw_transitions - same as above, but only contains transitions that exist on disk. Parsed transitions are not included.
"""


from . import loader as _loader
from . import store as _store
from . import models as _models
from . import logic as _logic

init = _loader.init


def __getattr__(name):
    if name in __all__ and name in _store.state.__dict__.keys():
        return _store.state.__getattribute__(name)
    if name in __all__ and name in  _models.__dict__.keys():
        return _models.__getattribute__(name)
    if name in __all__ and name in  _logic.__dict__.keys():
        return _logic.__getattribute__(name)
    
    ## shorthands
    if name == 'O': return _store.state.objects
    if name == 'Os': return _models.ListOfObjects(_store.state.objects.keys())
    if name == 'C': return _store.state.categories
    if name == 'LO': return _models.ListOfObjects
    if name == 'LT': return _models.ListOfTransitions
    
    raise AttributeError(f"module {__name__} has no attribute {name}")


__all__ = \
    ["init"] + \
    list(_store.state.__dict__.keys()) + \
    [
    'furtherParse',
    'getSpriteContent',
    
    'Pos',
    'Object',
    'Sprites',
    'Transition',
    'ListOfTransitions',
    'ListOfObjects',
    'Category',
    
    'isCategory',
    'isPattern',
    'isProbSet',
    'getCategoriesOf',
    
    'key',
    'search',
    'make',
    'use',
    'getTransitions',
    
    'setObjectExtraProperty',
    'draw'
    ] + \
    [
    "getObjectsBySprite",
    "getObjectsBySound",
    
    "getNumUses",
    "getUseChance",
    "getAncestors",
    
    "sortObjectsByDepth",
    "printObjectsWithDepth",
    "completelyDeleteObject",
    "checkForMissingSprites",
    "checkForMissingObjects"
    ] + \
    [
     "O",
     "Os",
     "C",
     "LO",
     "LT",
    ]

def __dir__():
    return __all__

if "loader" in locals(): del loader
if "store" in locals(): del store
if "models" in locals(): del models
if "logic" in locals(): del logic
if "draw" in locals(): del draw