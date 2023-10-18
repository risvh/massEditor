options = []


#options.append("regenerate_all")
#options.append("regenerate_categories")
#options.append("regenerate_objects")
#options.append("regenerate_transitions")
#options.append("regenerate_depths")


options.append("regenerate_smart")


    

################################################################################
############################################################# Util #############
################################################################################

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

def append_txt(text, path):
    with open(path, "a") as f:
        f.write(text)

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


from collections import OrderedDict

def objectFileLinesParser(content):
    odict = OrderedDict()
    lines = content.splitlines()
    lineNums = OrderedDict()

    for lineNum, line in enumerate(lines):
        if line.count("=") == 0:
            parsed_line = [['name', line]]
        elif line.count("=") > 1 and line.count(",") > 0:
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
            if tag in odict.keys():
                if type(odict[tag]) is not list:
                    odict[tag] = [odict[tag]]
                    lineNums[tag] = [lineNums[tag]]
                odict[tag].append(value)
                lineNums[tag].append(lineNum)
            else:
                odict[tag] = value
                lineNums[tag] = lineNum
    
    return odict, lineNums, lines



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

    @property
    def x( self ):
        return self[0]
    @property
    def y( self ):
        return self[1]


class Object(OrderedDict):
    
    def __getstate__(self): return self.__dict__
    def __setstate__(self, d): self.__dict__.update(d)
    
    def __init__(self, content = ""):
        parsed = objectFileLinesParser(content)
        self.update(parsed[0])
        super(OrderedDict, self).__setattr__('lineNums', parsed[1])
        super(OrderedDict, self).__setattr__('lines', parsed[2])
    
    
    def setExtra(self, key, value):
        super(OrderedDict, self).__setattr__(key, value)
    
    def __getattr__(self, key):
        return self[key]
    
    def __setattr__(self, tag, value, index=None):
        if tag not in self.keys():
            raise KeyError
            return
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
        return Object("\n".join(self.lines))
    
    def getAsList(self, key):
        r = self[key]
        if type(r) is not list: r = [r]
        return r
        
    def copy(self):
        return Object("\n".join(self.lines))
    
    def linesByTag(self, tag):
        index = self.lineNums[tag]
        if type(index) is list:
            return [o.lines[i] for i in index]
        else:
            return o.lines[index]
    
    def save(self):
        
        content = "\n".join(self.lines)
        
        id = self['id']
        path = Path("../output/objects") / f"{id}.txt"
        save_txt(content, path)
#        Path(path/"cache.fcz").unlink(missing_ok=True)
        
        objects[id] = Object("\n".join(self.lines))
        
        append_txt(f"{str(path)}\n", "changed_files.txt")
        
        
    
    def _getSpriteLines(self, index_start, index_end = None):
        if index_end is None: index_end = index_start + 1
        a = self.lineNums['spriteID'][index_start]
        if index_end >= int(self['numSprites']):
            b = self.lineNums['headIndex']
        else:
            b = self.lineNums['spriteID'][index_end]
        
        o_copy = self.copy()
        if type(o_copy['parent']) is list:
            for i, v in enumerate(o_copy['parent']):
                v2 = int(v)
                if v2 < index_start or v2 >= index_end:
                    v2 = -1
                else:
                    v2 = v2 - index_start
                o_copy.__setattr__('parent', str(v2), i)
        return o_copy.lines[a:b]
    
#        return self.lines[a:b]
        
#    def getSprites0(self, index_start, index_end = None):
#        lines = self._getSpriteLines( index_start, index_end )
#        temp_obj = Sprite( '\n'.join(lines) )
#        indexes = temp_obj.lineNums['spriteID']
#        indexes.append( len(temp_obj.lines) )
#        r = []
#        for i, v in enumerate(indexes[:-1]):
#            s = Sprite( '\n'.join( lines[indexes[i]:indexes[i+1]] ) )
#            r.append( s )
#        return r
    
    def getSprites(self, index_start, index_end = None):
        lines = self._getSpriteLines( index_start, index_end )
        return Object( '\n'.join(lines) )
    
    def _insertSprites(self, index, new_content):
        # first to last
        # back to front
        # 0 to N
        if type(new_content) is str: new_content = new_content.split("\n")
        partial_object = Object( "\n".join(new_content) )
        
        extra_numSprites = len(partial_object.getAsList('spriteID'))
        old_numSprites = int(self.numSprites)
        self.numSprites = str( old_numSprites + extra_numSprites )
        
        parents = self.getAsList('parent')
        if len(parents) > 1:
            for i, v in enumerate( [int(e) for e in parents] ):
                if v >= index:
                    self.__setattr__("parent", str(v + extra_numSprites), i)
        parents = partial_object.getAsList('parent')
        if len(parents) > 1:
            for i, v in enumerate( [int(e) for e in parents] ):
                if v == -1: continue
                partial_object.__setattr__("parent", str(v + extra_numSprites), i)
        
        if index >= int(old_numSprites):
            insertAt_lineNum = self.lineNums['headIndex']
        else:
            insertAt_lineNum = self.lineNums['spriteID'][index]
        lines = self.lines
        lines[insertAt_lineNum:insertAt_lineNum] = new_content
        
        content = "\n".join(lines)
        new_object = Object(content)
        self.update(new_object)
        self.lineNums.update(new_object.lineNums)
        self.lines[:] = new_object.lines
        
    def _removeSprite(self, index):
        
        removeFrom_lineNum = self.lineNums['spriteID'][index]
        if index + 1 >= int(self.numSprites):
            removeTo_lineNum = self.lineNums['headIndex']
        else:
            removeTo_lineNum = self.lineNums['spriteID'][index+1]
            
        lines = self.lines
        lines[removeFrom_lineNum:removeTo_lineNum] = []
        
        content = "\n".join(lines)
        new_object = Object(content)
        self.update(new_object)
        self.lineNums.update(new_object.lineNums)
        self.lines[:] = new_object.lines
        
        self.numSprites = str(int(self.numSprites) - 1)
        
        parents = self.getAsList('parent')
        for i, v in enumerate( [int(e) for e in parents] ):
            if v == index:
                self.__setattr__("parent", "-1", i)




class Sprite(OrderedDict):
    def __init__(self, content = ""):
        odict, self.lineNums, self.lines = objectFileLinesParser(content)
        self.update(odict)


class Transition():
    
    _fields = [
            "a", "b", "c", "d",
            "flag",
            "autoDecaySeconds",
            "actorMinUseFraction",
            "targetMinUseFraction",
            "reverseUseActorFlag",
            "reverseUseTargetFlag",
            "move",
            "desiredMoveDist",
            "noUseActorFlag",
            "noUseTargetFlag"
            ]
    
    _defaults = [None, None, None, None, "", "0", "0.000000", "0.000000", '0', '0', '0', '1', '0', '0']
    
    def __init__(self, *args):
        if type(args[0]) is list: args = args[0]
        args = list(args)
        
        for i, (field, default) in enumerate(zip(self._fields, self._defaults)):
            value = default
            if i < len(args): value = args[i]
            setattr(self, field, value)
            
        self.raw = True
        
    def __repr__(self):
        a_name, b_name, c_name, d_name = [ names[e] if e in names.keys() else str(e) for e in ( self.a, self.b, self.c, self.d ) ]
        return f"{str((self.a, self.b, self.c, self.d, self.flag)):<32}{a_name:<32} + {b_name:<32} = {c_name:<32} + {d_name:<32}"
    
    def pprint(self):
        print( self.__repr__() )
    
    def copy(self):
        return Transition(*self.toList())
    
    def toList(self):
        return [ getattr(self, field) for field in self._fields ]
    
    def replace(self, old, new):
        if self.a == old: self.a = new
        if self.b == old: self.b = new
        if self.c == old: self.c = new
        if self.d == old: self.d = new
        
    def save(self):
        if self.a is None or self.b is None or self.c is None or self.d is None: return
        
        content_list = self.toList()[2:4] + self.toList()[5:]
        content_list = [str(e) for e in content_list]
        content = " ".join(content_list)
        
        filename_flag = ""
        if self.flag != "": filename_flag = f"_{self.flag}"
        filename = f"{self.a}_{self.b}{filename_flag}.txt"
        path = Path("../output/transitions/") / filename
        save_txt(content, path)
#        Path(path/"cache.fcz").unlink(missing_ok=True)
        
        transitions[(self.a, self.b, self.flag)] = Transition(*self.toList())
        
        append_txt(f"{str(path)}\n", "changed_files.txt")
    
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
        filename = f"{self.a}_{self.b}.txt"
        if self.flag != "": filename = f"{self.a}_{self.b}_{self.flag}.txt"
        path = Path("../output/transitions/") / filename

        if not Path(path).exists(): print(f"TRANSITION DELETE NOT EXIST: {filename}")
        Path(path).unlink() # missing_ok=True)
        
        transitions.pop((self.a, self.b, self.flag), None)
        
        append_txt(f"{str(path)}\n", "changed_files.txt")

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
                reverse = False
                exact = False
                if query[0] == '-' and query != '-1':
                    query = query[1:]
                    reverse = True
                if query[-1] == '.':
                    query = query[:-1]
                    exact = True
                if not exact:
                    if (not reverse and query.lower() not in transition_str.lower()) or (reverse and query.lower() in transition_str.lower()):
                        mismatch = True
                        break
                else:
                    if (not reverse and query.lower() not in transition_str.lower().split()) or (reverse and query.lower() in transition_str.lower().split()):
                        mismatch = True
                        break
            if mismatch: continue
            results.append(transition)
        return results
        
    def delete(self):
        for transition in self:
            transition.delete()
            
    def raw(self):
        return ListOfTransitions([t for t in self if t.raw])
        
    
class ListOfObjects(list):
    def __repr__(self):
        r = []
        for e in self:
            if e in names.keys():
                r.append( f"{str(e):<8}{names[e]}" )
            else:
                r.append( f"{str(e):<8}" )
        return "\n".join(r)
    def __sub__(self, other):
        return ListOfObjects(set(self) - set(other))
    def search(self, querystr):
        return search(querystr, self)
    def items(self):
        return [ (i, objects[i]) for i in self ]

class Category(ListOfObjects):
    @classmethod
    def load(self, content):
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
        
    def save(self):
        lines = []
        lines.append(f"parentID={self.parentID}")
        if self.type != "":
            lines.append(self.type)
        lines.append(f"numObjects={len(self)}")
        lines.extend([str(e) for e in self])
        content = '\n'.join(lines)
        
        path = Path("../output/categories") / f"{self.parentID}.txt"
        save_txt(content, path)
#        Path(path/"cache.fcz").unlink(missing_ok=True)
        
        categories[self.parentID] = Category.load(content)
        
        append_txt(f"{str(path)}\n", "changed_files.txt")
    
    @property
    def name(self):
        return names[self.parentID]


def isCategory(id):
    return id in categories.keys() and not categories[id].type == 'pattern' and not categories[id].type == 'probSet'

def isPattern(id):
    return id in categories.keys() and categories[id].type == 'pattern'

def isProbSet(id):
    return id in categories.keys() and categories[id].type == 'probSet'

def parseCategories(trans):
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
        pattern_numObj = len(categories[a])
    elif isPattern(b):
        pattern_numObj = len(categories[b])

    zipCat_numObj = 0
    parse_other_category = False

    for i, e in enumerate((a, b, c, d)):
        if not isCategory(e) and not isPattern(e): continue
        e_category_list = categories[e].copy()
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
        results[i].raw = False
    return results




def search(querystr, pool=None):
    query_list = querystr.split()
    results = ListOfObjects()
    if pool is None: pool = names.keys()
    for id in pool:
        name = names[id]
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
                if (not reverse and query.lower() not in name.lower()) or (reverse and query.lower() in name.lower()):
                    mismatch = True
                    break
            else:
                if (not reverse and query.lower() not in name.lower().split()) or (reverse and query.lower() in name.lower().split()):
                    mismatch = True
                    break
        if mismatch: continue
        results.append(id)
    return results

def getTransition(a=None, b=None, c=None, d=None):
    results = ListOfTransitions()
    
    if a is not None and b is not None:
        key = (a, b, "")
        if key in transitions.keys():
            tran = transitions[key]
            if c is not None and tran.c == c and d is not None and tran.d == d:
                results.append(transitions[key])
                return results
    
    for tran in transitions.values():
        if (a is None or a == tran.a) and (b is None or b == tran.b) and (c is None or c == tran.c) and (d is None or d == tran.d):
            results.append( tran )
    
    for tran in results.copy():
        probSet_transitions = parseProbSet(tran)
        for probSet_transition in probSet_transitions:
            if (a is None or a == probSet_transition.a) and (b is None or b == probSet_transition.b) and (c is None or c == probSet_transition.c) and (d is None or d == probSet_transition.d):
                results.append( probSet_transition )
    return results

def parseProbSet(tran):
    probSet_transitions = ListOfTransitions()
    if isProbSet(tran.c):
        for perhaps_newActor in categories[tran.c]:
            new_tran = tran.copy()
            new_tran.b = perhaps_newActor
            probSet_transitions.append( new_tran )
    elif isProbSet(tran.d):
        for perhaps_newTarget in categories[tran.d]:
            new_tran = tran.copy()
            new_tran.d = perhaps_newTarget
            probSet_transitions.append( new_tran )
    return probSet_transitions

def make(id):
    return ListOfTransitions(set(getTransition(c=id) + getTransition(d=id)))

def use(id):
    results = ListOfTransitions()
    
    for tran in transitions.values():
        if id == tran.a or id == tran.b:
            results.append( tran )
            
    for tran in results.copy():
        probSet_transitions = parseProbSet(tran)
        for probSet_transition in probSet_transitions:
            if id == probSet_transition.a or id == probSet_transition.b:
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
        
def getCategoriesOf(id):
    r = ListOfObjects()
    for cid, c in categories.items():
        if id in c:
            r.append(cid)
    return r

def child(id):
    r = ListOfObjects()
    for t in use(id):
        if t.c > 0 and t.a != t.c: r.append(t.c)
        if t.d > 0 and t.b != t.d: r.append(t.d)
    return r


def parent(id):
    r = ListOfObjects()
    for t in make(id):
        if t.a > 0 and t.a != t.c: r.append(t.a)
        if t.b > 0 and t.b != t.d: r.append(t.b)
    return r

################################################################################
############################################################# Loading ##########
################################################################################

categories = {}
objects = {}
names = {}
transitions = {}
raw_transitions = {}
depths = {}

changed_files = []

if "regenerate_all" in options:
    options += ["regenerate_categories", 
                "regenerate_objects", 
                "regenerate_transitions", 
                "regenerate_depths"]

if Path("changed_files.txt").exists():
    changed_files = read_txt('changed_files.txt').strip().splitlines()



############################################################# Categories

if "regenerate_categories" in options:
    
    path = Path("../output/categories")
    files = list_dir(path, file=1)

    for i, file in enumerate(files):
        if ".txt" not in file: continue
        t = read_txt(path / file)
        lines = t.splitlines()
        if len(lines) < 2: continue

        id = int(file.replace(".txt", ""))
        categories[id] = Category.load(t)

        if i % 500 == 0: print( "Categories:", i, len(files) )
        
    save_pickle_file('categories.pickle', categories)
    
    for file in changed_files:
        if "categories" in file:
            changed_files.remove(file)
    save_txt('\n'.join(changed_files) + '\n', 'changed_files.txt')
    
else:
    categories = load_pickle_file('categories.pickle')
    
    if "regenerate_smart" in options:
        for file in changed_files:
            if "categories" not in file: continue
            path = Path(file)
            id = int(path.stem)
            
            if not path.exists():
                categories.pop(id, None)
            else:
                t = read_txt(file)
                c = Category.load(t)
                id = int(c.parentID)
                categories[id] = c

############################################################# Objects

if "regenerate_objects" in options:
    
    path = Path("../output/objects")
    files = list_dir(path, file=1)

    for i, file in enumerate(files):
        if ".txt" not in file: continue
        t = read_txt(path / file)
        if len(t.splitlines()) < 2: continue

        o = Object(t)
        id = int(o.id)
        names[id] = o.name
        objects[id] = o

        if i % 500 == 0: print( "Objects:", i, len(files) )
    
    save_pickle_file('objects.pickle', objects)
    
    for file in changed_files:
        if "objects" in file:
            changed_files.remove(file)
    save_txt('\n'.join(changed_files) + '\n', 'changed_files.txt')
    
else:
    objects = load_pickle_file('objects.pickle')
    
    if "regenerate_smart" in options:
        for file in changed_files:
            if "objects" not in file: continue
            path = Path(file)
            id = int(path.stem)
            
            if not path.exists():
                objects.pop(id, None)
                names.pop(id, None)
            else:
                t = read_txt(file)
                o = Object(t)
                id = int(o.id)
                names[id] = o.name
                objects[id] = o

for id, o in objects.items():
    names[id] = o.name
    
O = objects

############################################################# Transitions

autogen_transitions = False

if "regenerate_transitions" in options:
    
    path = Path("../output/transitions/")
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

    for raw_tran in transitions.copy().values():

        trans = parseCategories(raw_tran)
        if len(trans) == 1: continue

        for tran in trans:
            a, b, c, d, flag = tran.toList()[:5]
            if (a, b, flag) not in transitions.keys():
                transitions[a, b, flag] = tran
                
    save_pickle_file('transitions.pickle', transitions)
    
    for file in changed_files:
        if "transitions" in file:
            changed_files.remove(file)
    save_txt('\n'.join(changed_files) + '\n', 'changed_files.txt')
    
else:
    transitions = load_pickle_file('transitions.pickle')
    
    raw_transitions = {}
    for key, tran in transitions.items():
        if tran.raw:
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
        
        transitions = raw_transitions
        
        for raw_tran in transitions.copy().values():
    
            trans = parseCategories(raw_tran)
            if len(trans) == 1: continue
    
            for tran in trans:
                a, b, c, d, flag = tran.toList()[:5]
                if (a, b, flag) not in transitions.keys():
                    transitions[a, b, flag] = tran
                

############################################################# Generating Object Depth Map

natural_objects = [key for key, value in objects.items() if objects[key]['mapChance'].split('#')[0] != '0.000000']

if "regenerate_depths" in options:

    horizon = list(natural_objects)

    for id in natural_objects:
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
            if tran.a in depths.keys() and tran.b in depths.keys():
                next_depth = max( depths[tran.a], depths[tran.b] ) + 1
                if tran.c > 0 and tran.c not in depths.keys(): horizon.append(tran.c)
                if tran.d > 0 and tran.d not in depths.keys(): horizon.append(tran.d)
                depths[tran.c] = next_depth if tran.c not in depths.keys() else min(depths[tran.c], next_depth)
                depths[tran.d] = next_depth if tran.d not in depths.keys() else min(depths[tran.d], next_depth)
                    
    
    save_pickle_file('depths.pickle', depths)

else:
    depths = load_pickle_file('depths.pickle')
    

uncraftables = ListOfObjects(objects.keys() - depths.keys())

for oid, o in objects.items():    
    o.setExtra('uncraftable', oid in uncraftables)

print( "\nDONE LOADING\n" )





