
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

def minitechSortingAlgorithm(q):
    
    def split(regex_delimiters, s):
        import re
        terms = re.split(regex_delimiters, s)
        terms = list(filter(None, terms))
        return terms
    
    def stripComment(s):
        if s.find("#") != -1:
            s = s[:s.find("#")]
        return s
    
    rs = search(q)
    
    q = q.upper()
    terms = split('\s|\#|\,', q)
    scores_name = {}
    scores_description = {}
    object_depths = {}
    object_ids = {}
    
    for r in rs:
        
        description = names[r].upper()
        name = stripComment(description)
        
        tokens_name = split('\s|\#|\,', name)
        matchCount_name = 0
        
        for term in terms:
            for token in tokens_name:
                if token == term:
                    matchCount_name += 1
                    
        score_name = matchCount_name / len(tokens_name)
        scores_name[r] = score_name
        
        tokens_description = split('\s|\#|\,', description)
        matchCount_description = 0
        
        for term in terms:
            for token in tokens_description:
                if token == term:
                    matchCount_description += 1
                    
        score_description = matchCount_description / len(tokens_description)
        scores_description[r] = score_description
    
        depth = 9999
        if r in depths.keys(): depth = depths[r]
        object_depths[r] = depth
        object_ids[r] = r
    
    rs2 = sorted(rs, key = lambda x: (-scores_name[x], -scores_description[x], object_depths[x], object_ids[x]))
    return ListOfObjects(rs2)



############################################################# print food by depthes and foodValue

# foods = Os.filter(lambda o: o.foodValue != '0')

# def getTotalFoodValue(id):
#     if ',' not in O[id].foodValue: return int(O[id].foodValue)
#     return sum([int(e) for e in O[id].foodValue.split(',')])

# foods.sort(key=lambda x: (depths[x] if x in depths.keys() else 9999, getTotalFoodValue(x)))

# import pandas as pd

# df = pd.DataFrame(columns = ['depth', 'foodValue', 'id', 'name'])

# for id, o in foods.items():
#     i = len(df)
#     df.loc[i, 'depth'] = depths[id] if id in depths.keys() else 9999
#     df.loc[i, 'foodValue'] = o.foodValue
#     df.loc[i, 'id'] = id
#     df.loc[i, 'name'] = names[id]
    
# print(df.to_string())



############################################################# replacing with mortar?

# ts = getTransitions(a=33,c=33).raw().search("-stakes bowl")



############################################################# get unused sounds

# sounds0 = list_dir("../OneLifeData7/sounds", file=True)
# sounds0 = [e.replace(".aiff", "") for e in sounds0 if ".aiff" in e]

# sounds1 = []

# for id, o in O.items():
#     ss = [e.split(":")[0] for e in o.sounds.split(",")]
#     for s in ss:
#         if s not in sounds1:
#             sounds1.append(s)



############################################################# get containees with most sprites

# def overallContainable(id):
#     if O[id].containable == '1': return True
#     cs = getCategoriesOf(id)
#     if len(cs) == 0: return False
#     for c in cs:
#         if '+cont' in names[c]: return True
#     return False

# arr = []

# for id, o in O.items():
#     if int(o.id) not in depths.keys() : continue
#     if not overallContainable(id): continue
#     n = int(o.numSprites)
#     arr.append((n, id, names[id]))
    
# arr.sort(key=lambda x: -x[0])

# from pprint import pprint
# pprint(arr[:50])



############################################################# print natural objects by biome and chance

# def getMapChance(id):
#     if id not in O.keys(): return None
#     o = O[id]
#     s = o.mapChance.split("#")
#     s[0] = float(s[0])
#     if len(s) > 1:
#         s[1] = s[1].replace("biomes_", "")
#         s[1] = s[1].split(",")
#     else:
#         s.append(['0'])
#     return s

# maps = {}
# for i in range(10):
#     maps[str(i)] = LO()


# for id, o in O.items():
#     s = getMapChance(id)
#     if s[0] > 0:
#         for b in s[1]:
#             maps[b].append(id)
            
# for key, os in maps.items():
#     def customSort(x):
#         s = getMapChance(x)
#         return -float(s[0])
#     os.sort(key=customSort)

# for b in maps.items():
#     print()
#     print(" ========================= {}".format(b[0]) )
#     print()
#     for id, o in b[1].items():
#         s = getMapChance(id)
#         print(s[0], id, names[id])