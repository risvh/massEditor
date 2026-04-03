import time
from pathlib import Path

from .config import OUTPUT_PATH

from .util import read_txt, list_dir, load_pickle_file, save_pickle_file, save_txt
from .models import Object, Category, Transition, lookForListTags
from .logic import isCategory, isPattern, use

from . import store as _store


def parseCategories(trans):
    raw_tran = trans.copy()
    other_parts = trans.toList()[5:]
    trans = trans.toList()[:5]
    a, b, c, d, flag = trans
    category_bool = [isCategory(e) for e in trans[:-1]]
    pattern_bool = [isPattern(e) for e in trans[:-1]]
    if sum(category_bool) + sum(pattern_bool) == 0: return [Transition(*(trans + other_parts))]

    results = [trans]

    pattern_items = [[], [], [], []]
    zip_category_items = [[], [], [], []]
    category_items = [[], [], [], []]

    pattern_numObj = 0
    if isPattern(a):
        pattern_numObj = len(_store.state.categories[a])
    elif isPattern(b):
        pattern_numObj = len(_store.state.categories[b])

    zipCat_numObj = 0
    parse_other_category = False

    for i, e in enumerate((a, b, c, d)):
        if not isCategory(e) and not isPattern(e): continue
        e_category_list = _store.state.categories[e].copy()
        if isPattern(e) and len(e_category_list) == pattern_numObj:
            pattern_items[i] += e_category_list
        elif isPattern(e) and len(e_category_list) != pattern_numObj:
            pass
        elif isCategory(e) and (a, b, c, d).count(e) > 1:
            zip_category_items[i] = e_category_list
            zipCat_numObj = len(e_category_list)
        elif isCategory(e):
            category_items[i] = e_category_list
            parse_other_category = True


    if pattern_numObj > 0:
        for i, items in enumerate(pattern_items):
            if len(items) == 0:
                pattern_items[i] = [ [a, b, c, d][i] ] * pattern_numObj

        for a2, b2, c2, d2 in zip(*pattern_items):
            results.append( [a2, b2, c2, d2, flag] )


    if zipCat_numObj > 0:
        results_copy = results.copy()
        for result in results_copy:
            a2, b2, c2, d2, flag2 = result[:5]

            zip_category_items_copy = zip_category_items.copy()
            for i, items in enumerate(zip_category_items_copy):
                if len(items) == 0:
                    zip_category_items_copy[i] = [ [a2, b2, c2, d2][i] ] * zipCat_numObj

            for a3, b3, c3, d3 in zip(*zip_category_items_copy):
                results.append( [a3, b3, c3, d3, flag] )

    if parse_other_category:
        results_copy = results.copy()
        for result in results_copy:
            a2, b2, c2, d2, flag2 = result[:5]

            category_items_copy = [ e.copy() for e in category_items ]
            for l, id in zip(category_items_copy, (a2, b2, c2, d2)):
                l.append(id)

            for a3 in category_items_copy[0]:
                for b3 in category_items_copy[1]:
                    for c3 in category_items_copy[2]:
                        for d3 in category_items_copy[3]:
                            if [a3, b3, c3, d3, flag] not in results:
                                results.append( [a3, b3, c3, d3, flag] )
    
    for i, result in enumerate(results):
        results[i] = Transition( *(result + other_parts) )
        results[i].raw = sum([e1 != e2 for e1, e2 in zip(raw_tran.toList()[:4], results[i].toList()[:4])])
    return results

import shutil
total_width = shutil.get_terminal_size().columns
last_update = 0
update_interval = 0.1
def updateProgress(s, force):
    global last_update
    now = time.time()
    if force or now - last_update > update_interval:
        print( f"\r{s:<{total_width}}", end="", flush=True )
        last_update = now

def init(options=[], verbose=False):
    
    print("--- START LOADING ---")
    
    changed_files = []
    
    if "regenerate_all" in options:
        options += ["regenerate_categories", 
                    "regenerate_objects", 
                    "regenerate_transitions", 
                    "regenerate_depths"]
    
    if Path("changed_files.txt").exists():
        changed_files = read_txt('changed_files.txt').strip().splitlines()
    
    
    
    ############################################################# Categories
    
    if "regenerate_categories" not in options and Path("categories.pickle").exists():
        _store.state.categories = load_pickle_file('categories.pickle')
        
        if "regenerate_smart" in options:
            for file in changed_files:
                if "categories" not in file: continue
                path = Path(file)
                id = int(path.stem)
                
                if not path.exists():
                    _store.state.categories.pop(id, None)
                else:
                    t = read_txt(file)
                    c = Category.load(t)
                    id = int(c.parentID)
                    _store.state.categories[id] = c
    else:
        path = Path(OUTPUT_PATH / "categories")
        files = list_dir(path, file=1)
    
        for i, file in enumerate(files):
            if ".txt" not in file: continue
            t = read_txt(path / file)
            lines = t.splitlines()
            if len(lines) < 2: continue
    
            id = int(file.replace(".txt", ""))
            _store.state.categories[id] = Category.load(t)
            
            if verbose:
                s = f"Categories: {i} / {len(files)}"
                updateProgress(s, i == 0)
        print("\r" + s)
            
        save_pickle_file('categories.pickle', _store.state.categories)
        
        for file in changed_files:
            if "categories" in file:
                changed_files.remove(file)
        save_txt('\n'.join(changed_files) + '\n', 'changed_files.txt')
    
    ############################################################# Objects
    
    if "regenerate_objects" not in options and Path("objects.pickle").exists():
        _store.state.objects = load_pickle_file('objects.pickle')
        
        if "regenerate_smart" in options:
            for file in changed_files:
                if "objects" not in file: continue
                path = Path(file)
                id = int(path.stem)
                
                if not path.exists():
                    _store.state.objects.pop(id, None)
                    _store.state.names.pop(id, None)
                else:
                    t = read_txt(file)
                    o = Object(t)
                    id = int(o.id)
                    _store.state.objects[id] = o
    else:
        path = Path(OUTPUT_PATH / "objects")
        files = list_dir(path, file=1)
    
        for i, file in enumerate(files):
            if ".txt" not in file: continue
            t = read_txt(path / file)
            if len(t.splitlines()) < 2: continue
    
            o = Object(t)
            id = int(o.id)
            _store.state.objects[id] = o
    
            if verbose:
                s = f"Objects: {i} / {len(files)}"
                updateProgress(s, i == 0)
        print("\r" + s)
        
        save_pickle_file('objects.pickle', _store.state.objects)
        
        for file in changed_files:
            if "objects" in file:
                changed_files.remove(file)
        save_txt('\n'.join(changed_files) + '\n', 'changed_files.txt')
    
    for id, o in _store.state.objects.items():
        _store.state.names[id] = o.name
    lookForListTags()
    
    ############################################################# Transitions
    
    if "regenerate_transitions" not in options and Path("transitions.pickle").exists():
        _store.state.transitions = load_pickle_file('transitions.pickle')
        
        raw_transitions = {}
        for key, tran in _store.state.transitions.items():
            if tran.raw == 0:
                raw_transitions[key] = tran
        
        if "regenerate_smart" in options:
            for file in changed_files:
                if "transitions" not in file: continue
                path = Path(file)
                filename = path.name
                
                filename_items = filename.replace(".txt", "").split("_")
                actor, target = filename_items[:2]
                flag = ""
                if len(filename_items) > 2: flag = filename_items[2]
                key = (int(actor), int(target), flag)
                
                if not path.exists():
                    raw_transitions.pop(key, None)
                else:
                    t = read_txt(file)
                    
                    raw_tran = Transition.load(filename, t)
                    raw_transitions[raw_tran.a, raw_tran.b, raw_tran.flag] = raw_tran
            
            _store.state.transitions = raw_transitions
            
            for raw_tran in _store.state.transitions.copy().values():
        
                trans = parseCategories(raw_tran)
                if len(trans) == 1: continue
        
                for tran in trans:
                    a, b, c, d, flag = tran.toList()[:5]
                    if (a, b, flag) not in _store.state.transitions.keys():
                        _store.state.transitions[a, b, flag] = tran
                    else:
                        if tran.raw < _store.state.transitions[(a, b, flag)].raw:
                            _store.state.transitions[a, b, flag] = tran
    else:
        path = Path(OUTPUT_PATH / "transitions")
        files = list_dir(path, file=1)
    
        for i, file in enumerate(files):
            if ".txt" not in file: continue
            t = read_txt(path / file)
            items = t.split()
            if len(items) < 2: continue
    
            raw_tran = Transition.load(file, t)
            _store.state.transitions[raw_tran.a, raw_tran.b, raw_tran.flag] = raw_tran
    
            if verbose:
                s = f"Transitions: {i} / {len(files)}"
                updateProgress(s, i == 0)
        print("\r" + s)
    
        for raw_tran in _store.state.transitions.copy().values():
    
            trans = parseCategories(raw_tran)
            if len(trans) == 1: continue
    
            for tran in trans:
                a, b, c, d, flag = tran.toList()[:5]
                if (a, b, flag) not in _store.state.transitions.keys():
                    _store.state.transitions[a, b, flag] = tran
                else:
                    if tran.raw < _store.state.transitions[(a, b, flag)].raw:
                        _store.state.transitions[a, b, flag] = tran
                    
        save_pickle_file('transitions.pickle', _store.state.transitions)
        
        for file in changed_files:
            if "transitions" in file:
                changed_files.remove(file)
        save_txt('\n'.join(changed_files) + '\n', 'changed_files.txt')
                    
    
    ############################################################# Generating Object Depth Map
    
    natural_objects = [key for key, value in _store.state.objects.items() if _store.state.objects[key]['mapChance'].split('#')[0] != '0.000000']
    
    if "regenerate_depths" not in options and Path("depths.pickle").exists():
        _store.state.depths = load_pickle_file('depths.pickle')
    else:
        horizon = list(natural_objects)
    
        for id in natural_objects:
            _store.state.depths[id] = 0
        _store.state.depths[0] = 0
        _store.state.depths[-1] = 0
        _store.state.depths[-2] = 0
    
        i = 0
        while len(horizon) > 0:
    
            id = horizon.pop(0)
            
            if verbose:
                s = f"{len(_store.state.depths.keys())} / {len(_store.state.objects.keys())}, horizon: {len(horizon)}, id: {id}"
                updateProgress(s, i == 0)
            i += 1
    
            trans = use(id)
            
            for tran in trans:
                if tran.a in _store.state.depths.keys() and tran.b in _store.state.depths.keys():
                    next_depth = max( _store.state.depths[tran.a], _store.state.depths[tran.b] ) + 1
                    if tran.c > 0 and tran.c not in _store.state.depths.keys(): horizon.append(tran.c)
                    if tran.d > 0 and tran.d not in _store.state.depths.keys(): horizon.append(tran.d)
                    _store.state.depths[tran.c] = next_depth if tran.c not in _store.state.depths.keys() else min(_store.state.depths[tran.c], next_depth)
                    _store.state.depths[tran.d] = next_depth if tran.d not in _store.state.depths.keys() else min(_store.state.depths[tran.d], next_depth)
        print("\r" + s)
        
        save_pickle_file('depths.pickle', _store.state.depths)
        
    

    print("--- DONE LOADING ---")