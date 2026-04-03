from .config import OUTPUT_PATH

from .util import list_dir
from .models import ListOfObjects, ListOfTransitions, furtherParse
from . import store as _store



def isCategory(id):
    return id in _store.state.categories.keys() and not _store.state.categories[id].type == 'pattern' and not _store.state.categories[id].type == 'probSet'

def isPattern(id):
    return id in _store.state.categories.keys() and _store.state.categories[id].type == 'pattern'

def isProbSet(id):
    return id in _store.state.categories.keys() and _store.state.categories[id].type == 'probSet'

def getCategoriesOf(id):
    r = ListOfObjects()
    for cid, c in _store.state.categories.items():
        if id in c:
            r.append(cid)
    return r


def pickerStyleStringFilter(querystr, s):
    query_list = querystr.split()
    mismatch = False
    for query in query_list:                
        reverse = False
        exact = False
        if query[0] == '-' and query != '-1':
            query = query[1:]
            reverse = True
        if query[-1] == '.':
            query = query[:-1]
            exact = True
        if not exact:
            if (not reverse and query.lower() not in s.lower()) or (reverse and query.lower() in s.lower()):
                mismatch = True
                break
        else:
            if (not reverse and query.lower() not in s.lower().split()) or (reverse and query.lower() in s.lower().split()):
                mismatch = True
                break
    if mismatch: return False
    return True
    
def search(querystr, pool=None):
    if pool is None: pool = ListOfObjects(_store.state.objects.keys())
    return ListOfObjects(filter(lambda x: pickerStyleStringFilter(querystr, _store.state.names[x]), pool))

def parseProbSet(tran):
    probSet_transitions = ListOfTransitions()
    if isProbSet(tran.c):
        for perhaps_newActor in _store.state.categories[tran.c]:
            new_tran = tran.copy()
            new_tran.c = perhaps_newActor
            new_tran.raw = tran.raw + sum([e1 != e2 for e1, e2 in zip(new_tran.toList()[:4], tran.toList()[:4])])
            probSet_transitions.append( new_tran )
    elif isProbSet(tran.d):
        for perhaps_newTarget in _store.state.categories[tran.d]:
            new_tran = tran.copy()
            new_tran.d = perhaps_newTarget
            new_tran.raw = tran.raw + sum([e1 != e2 for e1, e2 in zip(new_tran.toList()[:4], tran.toList()[:4])])
            probSet_transitions.append( new_tran )
    return probSet_transitions

def make(id):
    results = ListOfTransitions()
    
    for tran in _store.state.transitions.values():
        if id == tran.c or id == tran.d:
            results.append( tran )
    
    probs = ListOfObjects([e for e in getCategoriesOf(id) if isProbSet(e)])
    if len(probs) > 0:
        trans = ListOfTransitions()
        for prob in probs:
            probSet_transitions = make(prob)
            for probSet_transition in probSet_transitions:
                ts = parseProbSet(probSet_transition)
                for t in ts:
                    if t not in trans and (t.c == id or t.d == id):
                        trans.append(t)
        results = ListOfTransitions(set(results + trans))
    
    return results

def use(id):
    results = ListOfTransitions()
    
    for tran in _store.state.transitions.values():
        if id == tran.a or id == tran.b:
            results.append( tran )
            
    for tran in results.copy():
        probSet_transitions = parseProbSet(tran)
        for probSet_transition in probSet_transitions:
            if id == probSet_transition.a or id == probSet_transition.b:
                results.append( probSet_transition )
    return results

def getTransitions(a=None, b=None, c=None, d=None):
    results = ListOfTransitions()
    
    working = ListOfTransitions()
    if c in _store.state.objects.keys():
        working = make(c)
    elif d in _store.state.objects.keys():
        working = make(d)
    elif a in _store.state.objects.keys():
        working = use(a)
    elif b in _store.state.objects.keys():
        working = use(b)
        
    for t in working:
        if (a is None or a == t.a) and (b is None or b == t.b) and (c is None or c == t.c) and (d is None or d == t.d):
            results.append(t)
            
    if len(working) == 0:
        for t in _store.state.transitions.values():
            if (a is None or a == t.a) and (b is None or b == t.b) and (c is None or c == t.c) and (d is None or d == t.d):
                working.append(t)
        for t0 in working:
            results.append(t0)
            ts = parseProbSet(t0)
            for t in ts:
                if (a is None or a == t.a) and (b is None or b == t.b) and (c is None or c == t.c) and (d is None or d == t.d):
                    results.append(t)
        results = ListOfTransitions(set(results))
    
    return results




def getObjectsBySprite(sprite_id):
    r = ListOfObjects()
    for id, o in _store.state.objects.items():
        sprites = o.spriteID
        if str(sprite_id) in sprites: r.append(id)
    return r

def getObjectsBySound(sound_id):
    r = ListOfObjects()
    for id, o in _store.state.objects.items():
        sounds = furtherParse(o.sounds)
        for s in sounds:
            if sound_id == s[0]: r.append(id)
    return r



def getNumUses(o):
    return int(o.numUses.split(',')[0])

def getUseChance(o):
    if ',' not in o.numUses: return 1.0
    return float(o.numUses.split(',')[1])

def getAncestors(id):
    r = ListOfObjects()
    if id not in _store.state.depths.keys(): return r
    do = _store.state.depths[id]
    ts = make(id)
    for t in ts:
        da, db = 9999, 9999
        if t.a in _store.state.depths.keys(): da = _store.state.depths[t.a]
        if t.b in _store.state.depths.keys(): db = _store.state.depths[t.b]
        if da < do and db < do:
            if do - da == 1 and t.a not in r: r.append(t.a)
            if do - db == 1 and t.b not in r: r.append(t.b)
    return r


def sortObjectsByDepth(lo):
    lo.sort(key=lambda x: 9999 if int(x) not in _store.state.depths.keys() else -_store.state.depths[int(x)])
    return lo

def printObjectsWithDepth(lo):
    for id, o in lo.items():
        d = 9999 if id not in _store.state.depths.keys() else _store.state.depths[id]
        print(d, id, o.name)

def completelyDeleteObject(id):
    import os
    
    cs = getCategoriesOf(id)
    for cid in cs:
        c = _store.state.categories[cid]
        c.remove(id)
        c.save()
    
    ts = use(id).raw()
    for t in ts:
        t.delete()
        
    ts = make(id).raw()
    for t in ts:
        t.delete()
        
    os.remove(OUTPUT_PATH / "objects" /  "{}.txt".format(id)) 
    

    def find(pattern, path):
        import fnmatch
        result = []
        for root, dirs, files in os.walk(path):
            for name in files:
                if fnmatch.fnmatch(name, pattern):
                    result.append(os.path.join(root, name))
        return result
    
    files = find( '{}_*.txt'.format(id), OUTPUT_PATH / 'animations')
    for file in files:
        os.remove(file)

def checkForMissingSprites():
    sprites = list_dir(OUTPUT_PATH / "sprites", file=True)
    sprites = [e.replace(".tga", "") for e in sprites if ".tga" in e]
    
    missing_sprites = []
    
    for id, o in _store.state.objects.items():
        for s in o.spriteID:
            if s not in sprites:
                missing_sprites.append(s)
                
    return missing_sprites

def checkForMissingObjects():
    os = ListOfObjects(_store.state.objects.keys())
    os.append(0)
    os.append(-1)
    os.append(-2)
    
    missing_objects = []
    
    for key, t in _store.state.transitions.items():
        if t.a not in os: missing_objects.append(t.a)
        if t.b not in os: missing_objects.append(t.b)
        if t.c not in os: missing_objects.append(t.c)
        if t.d not in os: missing_objects.append(t.d)
    
    for id, c in _store.state.categories.items():
        if id not in os: missing_objects.append(id)
        for oid, o, in c.items():
            if oid not in os: missing_objects.append(oid)
    
    return missing_objects