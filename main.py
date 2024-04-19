
from massEditor import init

init(options=[
    # "regenerate_all",
    # "regenerate_categories",
    # "regenerate_objects",
    # "regenerate_transitions",
    # "regenerate_depths",
    "regenerate_smart",
    ], verbose=True)

from massEditor import *
from draw import drawObject


# img = drawObject(30)

# use(30)





    




# ### Find all wall-destructive transitions
# def isWall(id):
#     if id <= 0:
#         return False
#     o = O[id]
#     if 'wallLayer' in o.keys() and o.wallLayer == '1':
#         return True
#     if 'floorHugging' in o.keys() and o.floorHugging == '1':
#         return True
#     return False
#
# for id, o in O.items():
#     if isWall(id):
#         # print(id, o.name)
#         ts = getTransition(b=id)
#         for t in ts:
#             if t.a > 0 and t.c > 0 and t.d not in categories and t.b == id and not isWall(t.d):
#                 t.pprint()
        


# def isFloor(id):
#     if id <= 0:
#         return False
#     if id not in O.keys():
#         return False
#     o = O[id]
#     if 'floor' in o.keys() and o.floor == '1':
#         return True
#     return False






def getNumUses(id):
    if id <= 0: return -1
    if id not in O.keys(): return -1
    o = O[id]
    if 'numUses' not in o.keys(): return -1
    return int(o.numUses.split(',')[0])

def getUseChance(id):
    if id <= 0: return -1
    if id not in O.keys(): return -1
    o = O[id]
    if 'numUses' not in o.keys(): return -1
    if ',' not in o.numUses: return -1
    return float(o.numUses.split(',')[1])

def hasUse(id):
    numUses = getNumUses(id)
    if numUses > 1: return True
    return False

def validUsePair(a, b):
    if hasUse(a) and hasUse(b):
        if getNumUses(a) == getNumUses(b):
            if getUseChance(a) == getUseChance(b):
                return True
    return False

def transUseType(t):
    if not( hasUse(t.a) or hasUse(t.b) or hasUse(t.c) or hasUse(t.d) ): return 0
    if validUsePair(t.a, t.c): return 1 # actor pass-through
    if validUsePair(t.b, t.d): return 2 # target pass-through
    if validUsePair(t.a, t.d): return 3 # cross-pass-through from actor to newTarget
    if validUsePair(t.b, t.c): return 4 # cross-pass-through from target to newActor
    return -1 











# r = ListOfObjects()
# for id, o in O.items():
#     ss = [int(e) for e in o.spriteID]
#     if 2637 in ss or 2638 in ss:
#         r.append(id)
    
# r2 = r.search("sack")

# for id, o in r2.items():
#     sid = '2637'
#     ss = o.getAsList('spriteID')
#     if sid not in ss: sid = '2638'
#     index = o.getAsList('spriteID').index(sid)
#     o._removeSprite(index)
#     o.save()


    
# r = search("sack #2")
# for id, o in r.items():
#     if id == 12080: continue
#     t = "\n".join(o.lines)
#     t = t.replace("speedMult=1.000000", "speedMult=1.000000\ncontainOffset=0,2")
#     o2 = Object(t)
#     o2.save()
    
    
    
    
    
# r = ListOfObjects()
# for id, o in O.items():
#     if 'numSlots' in o.keys() and 'slotStyle' in o.keys() and int(o.numSlots[0]) > 0 and o.slotStyle == '1':
#         r.append(id)
    
# r = r.search("-grave -tarr")

# for id, o in r.items():
#     slotPos = o.getAsList('slotPos')
#     slotPos2 = []
#     for i, s in enumerate(slotPos):
#         s = Pos(s)
#         s = s + Pos(0, 6)
#         o.__setattr__("slotPos", str(s), i)
#     o.save()
#     print(len(slotPos), o.name)
    
    
# r = ListOfObjects()
# for id, o in O.items():
#     add = False
#     if 'containable' in o.keys() and o.containable == '0': continue
#     if 'rot' in o.keys():
#         rots = [float(e) for e in o.getAsList('rot')]
#         for rot in rots:
#             rot = rot - math.floor(rot)
#             if rot != 0.25 and rot != 0.75 and rot != 0:
#                 add = True
#     if add:
#         r.append(id)











# sprites = list_dir("../output/sprites/", file=1)
# sprites = [e.replace(".tga","") for e in sprites if '.tga' in e]


# os = LO([4935,4940,4943,4944,4945,4946,4947,4948,4949])
# r = LO()
# missing = []

# for id, o in os.items():
#     ss = o.getAsList('spriteID')
#     for s in ss:
#         if s not in sprites:
#             r.append(id)
#             missing.append(s)
#             # break




























