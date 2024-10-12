
from massEditor import *

def getNumUses(id):
    if id not in O.keys(): return -1
    o = O[id]
    return int(o.numUses.split(',')[0])

def getUseChance(id):
    if id not in O.keys(): return -1
    o = O[id]
    if ',' not in o.numUses: return -1
    return float(o.numUses.split(',')[1])

def hasUse(id):
    numUses = getNumUses(id)
    if numUses > 1: return True
    return False

def transUseType(t):
    if not( hasUse(t.a) or hasUse(t.b) or hasUse(t.c) or hasUse(t.d) ): return 0
    
    def validUsePair(a, b):
        if hasUse(a) and hasUse(b):
            if getNumUses(a) == getNumUses(b):
                if getUseChance(a) == getUseChance(b):
                    return True
        return False
    
    if validUsePair(t.a, t.c): return 1 # actor pass-through
    if validUsePair(t.b, t.d): return 2 # target pass-through
    if validUsePair(t.a, t.d): return 3 # cross-pass-through from actor to newTarget
    if validUsePair(t.b, t.c): return 4 # cross-pass-through from target to newActor
    return -1 


def isFloor(id):
     if id not in O.keys(): return False
     o = O[id]
     if o.floor == '1': return True
     return False