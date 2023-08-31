options = []


# options.append("regenerate_all")
# options.append("regenerate_categories")
# options.append("regenerate_objects")
# options.append("regenerate_transitions")
# options.append("regenerate_depths")





    

import os
from pathlib import Path

def list_dir(folderpath = ".", file = False, folder = False, silent = True):
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

class Pos(list):
    def __add__(self, other):
        return Pos(self[0] + other[0], self[1] + other[1])
    def __sub__(self, other):
        return Pos(self[0] - other[0], self[1] - other[1])
    def __init__(self, *args):
        if len(args) == 1 and type(args[0]) is str:
            self[:] = [float(e) for e in args[0].split(',')]
        else:
            self[:] = args            
    def __repr__(self):
        return f"{self[0]:.6f},{self[1]:.6f}"

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
                        new_parts[-1] += (',' + part)
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
        if type(self[tag]) is list and index is not None:
            oldValue = self[tag][index]
            self[tag][index] = value
            lineNum = lineNum[index]
        elif type(self[tag]) is not list:
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
    
        # first to last
        # back to front
        # 0 to N
    
    def getSpriteLines(self, index_start, index_end = None):
        if index_end is None: index_end = index_start + 1
        a = self.lineNums['spriteID'][index_start]
        if index_end >= int(self['numSprites']):
            b = self.lineNums['headIndex']
        else:
            b = self.lineNums['spriteID'][index_end]
        return self.lines[a:b]
    
    def insertSprites(self, index, new_content):
        if type(new_content) is str: new_content = new_content.split("\n")
        old_numSprites = self['numSprites']
        partiral_object = Object( "\n".join(new_content) )
        if type(partiral_object['spriteID']) is str:
            extra_numSprites = 1
        else:
            extra_numSprites = len(partiral_object['spriteID'])
        new_numSprites = str( int(old_numSprites) + extra_numSprites )
        self.change("numSprites", new_numSprites)
        
        parents = self['parent']
        if type(parents) is list:
            for i, v in enumerate(parents):
                v = int(v)
                if v >= index:
                    self.change("parent", str(v + extra_numSprites), i)
        
        insertAt_lineNum = self.lineNums['spriteID'][index]
        lines = self.lines
        lines[insertAt_lineNum:insertAt_lineNum] = new_content
        
        content = "\n".join(lines)
        new_object = Object(content)        
        numSlots = int(new_object['numSlots'].split("#")[0])
        
        for i in range(numSlots + index, numSlots + index + extra_numSprites):
            if int(new_object['parent'][i]) == -1: continue
            if int(new_object['parent'][i]) >= extra_numSprites:
                new_index = -1
            else:
                new_index = int(new_object['parent'][i]) + index
            new_object.change("parent", str(new_index), i)
        
        self.update(new_object)
        self.lineNums.update(new_object.lineNums)
        self.lines[:] = new_object.lines
        self.lineByTag.update(new_object.lineByTag)


class Transition():
#    def __new__(cls, *args):
#        if len(args) > 1: return super().__new__(cls, args)
#        return super().__new__(cls, *args)
    
    def __init__(self, *args):
        if type(args[0]) is list: args = args[0]
        args = list(args)
        defaults = [None, None, None, None, "", None, "0.000000", "0.000000", '0', '0', '0', '1', '0', '0']
        for i in range(len(args), 14):
            args.append( defaults[i] )
        [
            self.a, self.b, self.c, self.d,
            self.flag,
            self.autoDecaySeconds,
            self.actorMinUseFraction,
            self.targetMinUseFraction,
            self.reverseUseActorFlag,
            self.reverseUseTargetFlag,
            self.move,
            self.desiredMoveDist,
            self.noUseActorFlag,
            self.noUseTargetFlag
         ] = args
    def __repr__(self):
        a_name, b_name, c_name, d_name = [ names[e] if e in names.keys() else str(e) for e in ( self.a, self.b, self.c, self.d ) ]
        return f"{str((self.a, self.b, self.c, self.d, self.flag)):<32}{a_name:<32} + {b_name:<32} = {c_name:<32} + {d_name:<32}"
    def pprint(self):
        print( self.__repr() )
    def copy(self):
        return Transition(*self.toList())
    def toList(self):
        return [
            self.a, self.b, self.c, self.d,
            self.flag,
            self.autoDecaySeconds,
            self.actorMinUseFraction,
            self.targetMinUseFraction,
            self.reverseUseActorFlag,
            self.reverseUseTargetFlag,
            self.move,
            self.desiredMoveDist,
            self.noUseActorFlag,
            self.noUseTargetFlag
         ]
    
    
    def replace(self, old, new):
        if self.a == old: self.a = new
        if self.b == old: self.b = new
        if self.c == old: self.c = new
        if self.d == old: self.d = new
    def save(self):
        if self.a is None or self.b is None or self.c is None or self.d is None: return
        filename_flag = ""
        if self.flag != "": filename_flag = f"_{self.flag}"
        filename = f"{self.a}_{self.b}{filename_flag}.txt"
        content_list = self.toList()[2:4] + self.toList()[5:]
        content_list = [str(e) for e in content_list]
        content = " ".join(content_list)
        path = Path("./transitions/")
        save_txt(content, path/filename)
    
    @classmethod
    def load(cls, filename, content):
        line = content.splitlines()[0]
        items = line.split()
        filename_items = filename.replace(".txt", "").split("_")
        actor, target = filename_items[:2]
        newActor, newTarget = items[:2]
        actor, target, newActor, newTarget = [int(e) for e in (actor, target, newActor, newTarget)]
        flag = ""
        if len(filename_items) > 2: flag = filename_items[2]
        return cls(actor, target, newActor, newTarget, flag, *items[2:])
    
    def delete(self):
        path = Path("./transitions/")
        f = f"{self.a}_{self.b}.txt"
        Path(path/f).unlink(missing_ok=True)

class ListOfTransitions(list):
    
    def __add__(self, other):
        return ListOfTransitions(list(self) + list(other))
    
    def pprint(self):
        for t in self: t.pprint()
        
    def search(self, querystr):
        query_list = querystr.split()
        results = ListOfTransitions()
        for transition in self:
            transition_str = str(transition)
            mismatch = False
            for query in query_list:
                if query[0] == '-' and query != '-1':
                    query = query[1:]
                    if query.lower() in transition_str.lower(): 
                        mismatch = True
                        break
                elif query.lower() not in transition_str.lower(): 
                    mismatch = True
                    break
            if mismatch: continue
            results.append(transition)
        return results
        
    def delete(self):
        for transition in self:
            transition.delete()
            
    def raw(self):
        return ListOfTransitions([t for t in self if (t.a, t.b, t.flag) in raw_transitions and raw_transitions[(t.a, t.b, t.flag)].toList()[2:4] == [t.c, t.d]])
        
        
    
class ListOfObjects(list):
    def __repr__(self):
        r = []
        for e in self:
            if e in names.keys():
                r.append( f"{str(e):<8}{names[e]}" )
            else:
                r.append( f"{str(e):<8}" )
        return "\n".join(r)
    def search(self, querystr):
        return search(querystr, self)

class Category(ListOfObjects):
    @classmethod
    def load(self, filename, content):
        lines = content.splitlines()
        list_str = content[content.find("\n", content.find("numObjects="))+1:].splitlines()
        list_int = [int(e.split()[0]) for e in list_str]
        category_type = ""
        if lines[1] in ["pattern", "probSet"]: category_type = lines[1]
        result = Category(list_int)
        id_str = lines[0].replace("parentID=", "")
        result.parentID = int(id_str)
        result.type = category_type
        return result
        
        


def make(id):
    return ListOfTransitions(set(get_transition(c=id) + get_transition(d=id)))

def use(id):
    return ListOfTransitions(set(get_transition(a=id) + get_transition(b=id)))

def is_category(id):
    return id in categories.keys() and not categories[id].type == 'pattern' and not categories[id].type == 'probSet'

def is_pattern(id):
    return id in categories.keys() and categories[id].type == 'pattern'

def is_probSet(id):
    return id in categories.keys() and categories[id].type == 'probSet'

def get_category_by_id(id):
    return categories[id]


def parse_categories(trans):
    other_parts = trans.toList()[5:]
    trans = trans.toList()[:5]
    a, b, c, d, flag = trans
    category_bool = [is_category(e) for e in trans[:-1]]
    pattern_bool = [is_pattern(e) for e in trans[:-1]]
    if sum(category_bool) + sum(pattern_bool) == 0: return [Transition(*(trans + other_parts))]

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
    return results




def search(querystr, pool=None):
    query_list = querystr.split()
    results = ListOfObjects()
    if pool is None: pool = names.keys()
    for id in pool:
        name = names[id]
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
        results.append(id)
    return results

def get_transition(a=None, b=None, c=None, d=None):
    results = ListOfTransitions()
    
    if a is not None and b is not None:
        key = (a, b, "")
        if key in transitions.keys():
            results.append(transitions[key])
        return results
    
    for tran in transitions.values():
        actor, target, newActor, newTarget, flag = tran.toList()[:5]
        if (a is None or a == actor) and (b is None or b == target) and (c is None or c == newActor) and (d is None or d == newTarget):
            results.append( tran )
        
        probSet_transitions = []
        if is_probSet(newActor):
            for perhaps_newActor in get_category_by_id(newActor):
                new_tran = tran.copy()
                new_tran.b = perhaps_newActor
                probSet_transitions.append( new_tran )
        elif is_probSet(newTarget):
            for perhaps_newTarget in get_category_by_id(newTarget):
                new_tran = tran.copy()
                new_tran.d = perhaps_newTarget
                probSet_transitions.append( new_tran )
        for probSet_transition in probSet_transitions:
            if (a is None or a == probSet_transition.a) and (b is None or b == probSet_transition.b) and (c is None or c == probSet_transition.c) and (d is None or d == probSet_transition.d):
                results.append( probSet_transition )
    return results

def guide(id):
    a = make(id)
    b = use(id)
    if len(a) > 0:
        print("\n")
        print("MAKE")
        print("\n")
        for t in a: print(t)
    if len(b) > 0:
        print("\n")
        print("USE")
        print("\n")
        for t in b: print(t)

################################################################################
############################################################# Loading ##########
################################################################################


categories = {}
objects = {}
names = {}
transitions = {}
raw_transitions = {}
depths = {}


if "regenerate_all" in options:
    options += ["regenerate_categories", 
                "regenerate_objects", 
                "regenerate_transitions", 
                "regenerate_depths"]
    


############################################################# Categories

if "regenerate_categories" in options:
    
    path = Path("./categories")
    files = list_dir(path, file=1)

    for i, file in enumerate(files):
        if ".txt" not in file: continue
        t = read_txt(path / file)
        lines = t.splitlines()
        if len(lines) < 2: continue

        id = int(file.replace(".txt", ""))
        categories[id] = Category.load(file, t)

        if i % 500 == 0: print( "Categories:", i, len(files) )
        
    save_pickle_file('categories.pickle', categories)
    
else:
    categories = load_pickle_file('categories.pickle')

############################################################# Objects

if "regenerate_objects" in options:
    
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
    
    save_pickle_file('objects.pickle', objects)
    save_pickle_file('names.pickle', names)
    
else:
    objects = load_pickle_file('objects.pickle')
    names = load_pickle_file('names.pickle')

############################################################# Transitions

if "regenerate_transitions" in options:
    
    path = Path("./transitions/")
    files = list_dir(path, file=1)

    for i, file in enumerate(files):
        if ".txt" not in file: continue
        t = read_txt(path / file)
        items = t.split()
        if len(items) < 2: continue

        raw_tran = Transition.load(file, t)
        transitions[raw_tran.a, raw_tran.b, raw_tran.flag] = raw_tran

        if i % 500 == 0: print( "Transitions:", i, len(files) )

############################################################# Auto-generating Transitions

    transitions_copy = transitions.copy()
    raw_transitions = transitions.copy()

    for raw_tran in transitions_copy.values():

        trans = parse_categories(raw_tran)
        if len(trans) == 1: continue

        for tran in trans:
            a, b, c, d, flag = tran.toList()[:5]
            if (a, b, flag) not in transitions.keys():
                transitions[a, b, flag] = tran
                
    save_pickle_file('transitions.pickle', transitions)
    save_pickle_file('raw_transitions.pickle', raw_transitions)
    
else:
    transitions = load_pickle_file('transitions.pickle')
    raw_transitions = load_pickle_file('raw_transitions.pickle')

############################################################# Generating Object Depth Map

natural_objects = {key:value for key, value in objects.items() if objects[key]['mapChance'].split('#')[0] != '0.000000'}

if "regenerate_depths" in options:

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

        trans = use(id)
        for tran in trans:
            a, b, c, d, flag = tran.toList()[:5]
            if a in depths.keys() and b in depths.keys():
                next_depth = max( depths[a], depths[b] ) + 1
                if c > 0 and c not in depths.keys(): horizon.append(c)
                if d > 0 and d not in depths.keys(): horizon.append(d)
                depths[c] = next_depth if c not in depths.keys() else min(depths[c], next_depth)
                depths[d] = next_depth if d not in depths.keys() else min(depths[d], next_depth)
                    
    
    save_pickle_file('depths.pickle', depths)

else:
    depths = load_pickle_file('depths.pickle')
    

uncraftables = list(objects.keys() - depths.keys())

for oid, o in objects.items():
    o.name = o['name']
    o.id = int(o['id'])
    if oid in uncraftables:
        o.uncraftable = True
    else:
        o.uncraftable = False

print( "\nDONE LOADING\n" )

## 1. Should remove arrows before skinning animals 
#l = use(561).search("arrow -no")




#for o in objects.values():
#    id = o.id
#    a = get_transition(560, id) #Knife
#    b = get_transition(11671, id) #Bronze Knife
#    c = get_transition(8709, id) #Flint Knife
#    d = get_transition(34, id) #Sharp Stone
#    
#    A = get_transition(964, id) #Fine cutter
#    B = get_transition(723, id) #Rough cutter
#    
#    C = get_transition(561, id) #Skinning Tool
#    
#    y = get_transition(9046, id) #@ Tier 1 Knives   Cheese and water snares  
#    z = get_transition(9047, id) #@ Tier 2 Knives   Not used
#    


#    ## 2. have trans for all 3 knives, but not using any categories
#    if len(a) > 0 and len(b) > 0 and len(c) > 0 and (len(A) == 0 and len(C) == 0 and len(B) == 0):
#        print(o.id, o.name)


# 1332 Dead Boar# no arrow
# 1352 Dead Domestic Pig
# 2962 Primitive Fence Gate
# 2982 Shaky Primitive Fence#horizontal
# 2983 Shaky Primitive Fence Gate#+blocksMoving
# 2984 Shaky Primitive Fence Gate
# 2985 Shaky Primitive Fence#corner
# 2986 Shaky Primitive Fence#vert
# 562 Skinned Mouflon
# 596 Skinned Sheep
# 6926 Skinned Cow
# 6927 Skinned Bison







## 3. Exotic flower stages should be using Dry and Wet plant categories
watering_can = ListOfObjects([t.b for t in use(7013).raw().search("emptied -@ -bucket")])
full_watering_can = ListOfObjects([t.b for t in use(7029).raw().search("-emptied -@ -bucket")])
# set(full_watering_can) == set(watering_can)

## 4. Full watering can should be used on Banana and domestic mango tree
full_can_trees = ListOfObjects([t.b for t in use(7029).raw().search("emptied -@ -bucket")])
full_bucket_trees = ListOfObjects([t.b for t in use(660).search("tree")])
not_in = ListOfObjects(set(full_bucket_trees) - set(full_can_trees))







# water sources

full_source_c = categories[394] # @ Full Portable Water Source 
# 7013    Watering Can
# 7029    Full Watering Can
any_sprinkler_c = categories[12626] # @Any Sprinkler tapout


## target

dry_plant_c = categories[7031] # @Dry Plant
## which contains "Dry Maple Sapling Cutting" and "Dry Maple Sapling" patterns
trees_cutting = categories[1790]
trees_sapling = categories[1802]
# exotic flowers
# staked bush






## 5. These trees are not using the categories
sapling_not_in_cat = ListOfObjects(set(search("dry sapling -cutting")) - set(trees_sapling))






## 6. check why some are in others4 and others in bowl_water_targets

full_source_targets = ListOfObjects([t.b for t in use(394).raw()])

b = ListOfObjects( set(dry_plant_c) - set(full_source_targets) )
# b == trees_cutting + trees_sapling, checks out


## non-plant target for pouch and bowl
others = ListOfObjects( set(full_source_targets) - set(dry_plant_c) )
others2 = others.search("-@")
others3 = ListOfObjects(set(others2) - set(full_watering_can))
others4 = others3.search("-wall -rubble -pond -well -bucket -pouch")

## raw transitions of Bowl of Water
bowl_water_trans = get_transition(a=382, c=235).raw()
bowl_water_targets = ListOfObjects([t.b for t in bowl_water_trans])

bowl_water_trans = get_transition(a=382, c=235).raw()
water_pouch_trans = get_transition(a=210, c=209).raw()
