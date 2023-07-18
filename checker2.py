from pathlib import Path

def list_dir(folderpath = ".", file = False, folder = False, silent = True):
    import os
    results = []
    for filename in os.listdir(folderpath):
        fullpath = os.path.join(folderpath, filename)
        if not file and os.path.isfile(fullpath): continue
        if not folder and os.path.isdir(fullpath): continue
        # ext = os.path.splitext(filename)[-1].lower()
        results.append(filename)
        if not silent: print(filename)
    return results

def read_txt(path):
    with open(path, 'r', encoding='utf-8-sig') as f:
        text = f.read()
    return text

def save_txt(text, path):
    with open(path, 'w', newline='\n') as f:
        f.write(text)
    return text

def save_json_file(filepath, j):
    with open(filepath, 'w') as f:
        import json
        json.dump(j, f)
        
def save_pickle_file(filepath, j):
    with open(filepath, 'wb') as f:
        import pickle
        pickle.dump(j, f)
    
def load_pickle_file(filepath):
    with open(filepath, 'rb') as f:
        import pickle
        j = pickle.load(f)
    return j
    
    
################################################################################
############################################################# Main #############
################################################################################

def read_category_as_list(id):
    path = Path("./categories")
    filename = f"{id}.txt"
    content = read_txt(path / filename)
    list_str = content[content.find("\n", content.find("numObjects="))+1:]
    return list_str.splitlines()

def read_object_by_id(id):
    path = Path("./objects")
    content = read_txt(path / f"{id}.txt")
    return Object(content)

def read_object_name_by_id(id):
    id = int(id)
    if id <= 0: return str(id)
    return read_object_by_id(id)['name']




from collections import OrderedDict

class Object(OrderedDict):
    def __init__(self, content = ""):
        lines = content.splitlines()
        lineNums = OrderedDict()
        lineByTag = OrderedDict()
        
        for lineNum, line in enumerate(lines):
            if line.count("=") == 0:
                parsed_line = [['name', line]]
            elif line.count("=") > 1 and line.count(",") > 0:
                # parsed_line = [e.split("=", maxsplit=1) for e in line.split(",")]
                parts = line.split(',')
                new_parts = []
                for part in parts:
                    if "=" in part:
                        new_parts.append(part)
                    else:
                        new_parts[-1] += part
                parsed_line = [part.split("=", maxsplit=1) for part in new_parts]
            else:
                parsed_line = [line.split("=", maxsplit=1)]
            
            parsed = [(tag, value, lineNum, line) for tag, value in parsed_line]
                
            for item in parsed:
                tag, value, lineNum, rawLine = item
                if tag in self.keys():
                    if type(self[tag]) is not list:
                        self[tag] = [self[tag]]
                        lineNums[tag] = [lineNums[tag]]
                        lineByTag[tag] = [lineByTag[tag]]
                    self[tag].append(value)
                    lineNums[tag].append(lineNum)
                    lineByTag[tag].append(rawLine)
                else:
                    self[tag] = value
                    lineNums[tag] = lineNum
                    lineByTag[tag] = rawLine
            
            self.lineNums = lineNums
            self.lines = lines
            self.lineByTag = lineByTag
    def change(self, tag, value, index=None):
        lineNum = self.lineNums[tag]
        if self[tag] is list and index is not None:
            oldValue = self[tag][index]
            self[tag][index] = value
        elif self[tag] is not list:
            oldValue = self[tag]
            self[tag] = value
        else:
            raise TypeError
            return
        lhs = f"{tag}="
        if tag == 'name': lhs = ""
        self.lines[lineNum] = self.lines[lineNum].replace(f"{lhs}{oldValue}", f"{lhs}{value}")
        return "\n".join(self.lines)
    def save(self):
        content = "\n".join(self.lines)
        id = self['id']
        path = Path("./objects")
        save_txt(content, path / f"{id}.txt")

class Transition():
    def __init__(self, filename, content):
        line = content.splitlines()[0]
        items = line.split()
        filename_items = filename.replace(".txt", "").split("_")
        actor, target = filename_items[:2]
        flag = ""
        if len(filename_items) > 2: flag = filename_items[2]
        defaults = [None, None, None, "0.000000", "0.000000", '0', '0', '0', '1', '0', '0']
        for i in range(len(items), 11):
            items.append( defaults[i] )
        self.flag = flag
        [
            self.newActor,
            self.newTarget,
            self.autoDecaySeconds,
            self.actorMinUseFraction,
            self.targetMinUseFraction,
            self.reverseUseActorFlag,
            self.reverseUseTargetFlag,
            self.move,
            self.desiredMoveDist,
            self.noUseActorFlag,
            self.noUseTargetFlag
         ] = items
        actor, target, self.newActor, self.newTarget = [int(e) for e in (actor, target, self.newActor, self.newTarget)]
        self.a, self.b, self.c, self.d = [int(e) for e in (actor, target, self.newActor, self.newTarget)]
    def __repr__(self):
        return str((self.a, self.b, self.c, self.d))
    def pprint(self):
        a_name, b_name, c_name, d_name = [ read_object_name_by_id(e) for e in ( self.a, self.b, self.c, self.d ) ]
        print( f"{a_name} + {b_name} = {c_name} + {d_name}")







def get_transition_producing(id):
    return list(set(get_transition(None, None, id) + get_transition(None, None, None, id)))

def get_transition_using(id):
    return list(set(get_transition(id) + get_transition(None, id)))

def is_category(id):
    return id in categories.keys() and not categories[id][1] == 'pattern' and not categories[id][1] == 'probSet'

def is_pattern(id):
    return id in categories.keys() and categories[id][1] == 'pattern'

def is_probSet(id):
    return id in categories.keys() and categories[id][1] == 'probSet'

def get_category_by_id(id):
    return categories[id][0]


def parse_categories(trans):
    a, b, c, d, flag = trans
    category_bool = [is_category(e) for e in trans[:-1]]
    pattern_bool = [is_pattern(e) for e in trans[:-1]]
    if sum(category_bool) + sum(pattern_bool) == 0: return [trans]
    
    results = [trans]
    
    pattern_items = [[], [], [], []]
    zip_category_items = [[], [], [], []]
    category_items = [[], [], [], []]
    
    pattern_numObj = 0
    if is_pattern(a):
        pattern_numObj = len(get_category_by_id(a))
    elif is_pattern(b):
        pattern_numObj = len(get_category_by_id(b))
        
    zipCat_numObj = 0
    parse_other_category = False
    
    for i, e in enumerate((a, b, c, d)):
        if not is_category(e) and not is_pattern(e): continue
        e_category_list = get_category_by_id(e).copy()
        if is_pattern(e) and len(e_category_list) == pattern_numObj:
            pattern_items[i] += e_category_list
        elif is_pattern(e) and len(e_category_list) != pattern_numObj:
            pass
        elif is_category(e) and (a, b, c, d).count(e) > 1:
            zip_category_items[i] = e_category_list
            zipCat_numObj = len(e_category_list)
        elif is_category(e):
            category_items[i] = e_category_list
            parse_other_category = True
    
    
    if pattern_numObj > 0:
        for i, items in enumerate(pattern_items):
            if len(items) == 0:
                pattern_items[i] = [ (a, b, c, d)[i] ] * pattern_numObj
        
        for a2, b2, c2, d2 in zip(*pattern_items):
            results.append( (a2, b2, c2, d2, flag) )
    
    
    if zipCat_numObj > 0:
        results_copy = results.copy()
        for result in results_copy:
            a2, b2, c2, d2, flag2 = result
            
            zip_category_items_copy = zip_category_items.copy()
            for i, items in enumerate(zip_category_items_copy):
                if len(items) == 0:
                    zip_category_items_copy[i] = [ (a2, b2, c2, d2)[i] ] * zipCat_numObj
            
            for a3, b3, c3, d3 in zip(*zip_category_items_copy):
                results.append( (a3, b3, c3, d3, flag) )

    if parse_other_category:
        results_copy = results.copy()
        for result in results_copy:
            a2, b2, c2, d2, flag2 = result
            
            category_items_copy = [ e.copy() for e in category_items ]
            for l, id in zip(category_items_copy, (a2, b2, c2, d2)):
                l.append(id)
            
            for a3 in category_items_copy[0]:
                for b3 in category_items_copy[1]:
                    for c3 in category_items_copy[2]:
                        for d3 in category_items_copy[3]:
                            if (a3, b3, c3, d3, flag) not in results:
                                results.append( (a3, b3, c3, d3, flag) )
    return results


def get_transition(a=None, b=None, c=None, d=None):
    results = []
    for key, item in transitions_map.items():
        actor, target, flag = key
        newActor, newTarget = item
        if (a is None or a == actor) and (b is None or b == target) and (c is None or c == newActor) and (d is None or d == newTarget):
            results.append( (actor, target, newActor, newTarget, flag) )
        
        probSet_transitions = []
        if is_probSet(newActor):
            for perhaps_newActor in get_category_by_id(newActor):
                probSet_transitions.append( (actor, target, perhaps_newActor, newTarget, flag) )
        elif is_probSet(newTarget):
            for perhaps_newTarget in get_category_by_id(newTarget):
                probSet_transitions.append( (actor, target, newActor, perhaps_newTarget, flag) )
        for probSet_transition in probSet_transitions:
            if (a is None or a == probSet_transition[0]) and (b is None or b == probSet_transition[1]) and (c is None or c == probSet_transition[2]) and (d is None or d == probSet_transition[3]):
                results.append( probSet_transition )
    return results

















def print_simple_trans(trans):
    a_name, b_name, c_name, d_name = [ read_object_name_by_id(e) for e in trans[:-1] ]
    print( f"{a_name} + {b_name} = {c_name} + {d_name}")








################################################################################
############################################################# Loading ##########
################################################################################
        





        
categories = {}
objects = {}
names = {}
depths = {}
transitions_map = {}





if 0:
    
    ############################################################# Categories
    
    path = Path("./categories")
    files = list_dir(path, file=1)
    
    for i, file in enumerate(files):
        if ".txt" not in file: continue
        t = read_txt(path / file)
        lines = t.splitlines()
        if len(lines) < 2: continue
    
        id = int(file.replace(".txt", ""))
        list_str = t[t.find("\n", t.find("numObjects="))+1:].splitlines()
        list_int = [int(e.split()[0]) for e in list_str]
        category_type = ""
        if lines[1] in ["pattern", "probSet"]: category_type = lines[1]
        categories[id] = list_int, category_type
        
        if i % 500 == 0: print( "Categories:", i, len(files) )
    
    ############################################################# Objects
    
    path = Path("./objects")
    files = list_dir(path, file=1)
    
    for i, file in enumerate(files):
        if ".txt" not in file: continue
        t = read_txt(path / file)
        if len(t.splitlines()) < 2: continue
    
        o = Object(t)
        id = int( o['id'] )
        name = o['name']
        names[id] = name
        objects[id] = o

        if i % 500 == 0: print( "Objects:", i, len(files) )
    
    ############################################################# Transitions
    
    path = Path("./transitions/")
    files = list_dir(path, file=1)
    
    test_dict = {}
    
    for i, file in enumerate(files):
        if ".txt" not in file: continue
        t = read_txt(path / file)
        items = t.split()
        if len(items) < 2: continue
    
        raw_tran = Transition(file, t)
        transitions_map[raw_tran.a, raw_tran.b, raw_tran.flag] = raw_tran.c, raw_tran.d
        
        if i % 500 == 0: print( "Transitions:", i, len(files) )
    
    ############################################################# Auto-generating Transitions
    
    transitions_map_copy = transitions_map.copy()
    
    for key, item in transitions_map_copy.items():
        
        actor, target, flag = key
        newActor, newTarget = item
        simple_raw_tran = (actor, target, newActor, newTarget, flag)
    
        trans = parse_categories(simple_raw_tran)
        if len(trans) == 1: continue
    
        for tran in trans:
            a, b, c, d, flag = tran
            if (a, b, flag) not in transitions_map.keys():
                transitions_map[a, b, flag] = c, d
    
    ############################################################# Generating Object Depth Map

    natural_objects = {key:value for key, value in objects.items() if objects[key]['mapChance'].split('#')[0] != '0.000000'}
    horizon = list(natural_objects.keys())
    
    for id in natural_objects.keys():
        depths[id] = 0
    depths[0] = 0
    depths[-1] = 0
    depths[-2] = 0
    
    i = 0
    while len(horizon) > 0:
        
        id = horizon.pop(0)
        if i % 500 == 0: print( f"{len(depths.keys())} / {len(objects.keys())}, horizon: {len(horizon)}, id: {id}" )
        i += 1
        
        trans = get_transition_using(id)
        for tran in trans:
            a, b, c, d, flag = tran
            if a in depths.keys() and b in depths.keys():
                next_depth = max( depths[a], depths[b] ) + 1
                if c not in depths.keys(): 
                    depths[c] = next_depth
                    if c > 0: horizon.append(c)
                if d not in depths.keys(): 
                    depths[d] = next_depth
                    if d > 0: horizon.append(d)


    save_pickle_file('categories.pickle', categories)    
    save_pickle_file('objects.pickle', objects)
    save_pickle_file('depths.pickle', depths)
    save_pickle_file('names.pickle', names)
    save_pickle_file('transitions_map.pickle', transitions_map)

    print( "\nDONE LOADING\n" )

else:
    categories = load_pickle_file('categories.pickle')
    objects = load_pickle_file('objects.pickle')
    depths = load_pickle_file('depths.pickle')
    names = load_pickle_file('names.pickle')
    transitions_map = load_pickle_file('transitions_map.pickle')
    
    print( "\nDONE LOADING PICKLES\n" )




def search_objects_by_name(querystr):
    query_list = querystr.split()
    results = {}
    for id, name in names.items():
        mismatch = False
        for query in query_list:
            if query[0] == '-':
                query = query[1:]
                if query.lower() in name.lower(): 
                    mismatch = True
                    break
            elif query.lower() not in name.lower(): 
                mismatch = True
                break
        if mismatch: continue
        results[id] = name
    return results






################################################################################
############################################################# Categories #######
################################################################################
        
if 0:

    path = Path("./categories")
    files = list_dir(path, file=1)
    
    results = []
    
    for file in files:
        if ".txt" not in file: continue
        t = read_txt(path / file)
        lines = t.splitlines()
        if len(lines) < 2: continue
        
        id = file.replace(".txt", "")
        # name = lines[1]
        
        parentID = 0
        
        for num, line in enumerate(lines):
            if "parentID=" in line:
                parentID = line.replace("parentID=", "")
                break
        
        if lines[1] == 'pattern':
            mode = "pattern"
        elif lines[1] == 'probSet':
            mode = "probSet"
        else:
            mode = "category"
        
        # parentName = objects[id][None]
        
        # @ = None
        # None = pattern
        # Perhaps = probSet
        
        # if "#" in parentName:
        #     print(id, mode, parentName)


################################################################################
############################################################# Transitions ######
################################################################################




if 0:
    
    path = Path("./transitions/")
    files = list_dir(path, file=1)
    
    i = 0
    for file in files:
        if ".txt" not in file: continue
        t = read_txt(path / file)
        items = t.split()
        if len(items) < 2: continue
        
        actor = int(file.replace(".txt", "").split("_")[0])
        target = int(file.replace(".txt", "").split("_")[1])
        new_actor = int(items[0])
        new_target = int(items[1])
        
        # decay_time = items[2]
        # move = '0'
        # if len(items) > 7: move = items[7]


################################################################################
############################################################# Objects ##########
################################################################################


if 1:

    rawStr = """
8419
8420
8423
8424
8474
8475
8416
8417
8425
8426
8476
8477
8400
8401
8421
8422
8472
8473
    """.strip()
    # files = [f"{e}.txt" for e in rawStr.splitlines()]
    
    
    uncraftables = list(objects.keys() - depths.keys())
    files = [f"{e}.txt" for e in uncraftables]
    
    path = Path("./objects")
    # files = list_dir(path, file=1)
    
    for file in files:
        if ".txt" not in file: continue
        t = read_txt(path / file)
        if len(t.splitlines()) < 2: continue
        
        o = Object(t)
        id = o['id']
        name = o['name']
        
        permanent = o['permanent'] == '1'
        blocking = o['blocksWalking'] == '1'
        
        infos = [
            id,
            name
            ]
        
        if "Pipe" in name:
        
            print("\t".join([str(e) for e in infos]))
            
                
            # save_txt(t, path / f"{id}.txt")

        
        
