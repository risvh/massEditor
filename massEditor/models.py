import math
from pathlib import Path
from collections import OrderedDict

from .config import OUTPUT_PATH

from .util import save_txt, append_txt, read_txt
from . import store as _store

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

list_tags = []
def lookForListTags():
    global list_tags
    if len(list_tags) > 0: return
    for id, o in _store.state.objects.items():
        for key in o.keys():
            if type(o[key]) is list and key not in list_tags:
                list_tags.append(key)

def furtherParse(value):
    def isFloat(value):
        if value.count('.') == 1:
            values = value.split('.')
            if values[0].replace('-', '', 1).isdigit() and values[1].isdigit() and len(values[1]) == 6:
                return True
        return False
    if type(value) == list:
        return [furtherParse(e) for e in value]
    if type(value) != str: return value
    if value.count('#') > 1: return value
    if '#' in value:
        values = value.split('#')
        return [furtherParse(values[0]), values[1]]
    if value.count(',') > 1:
        values = value.split(',')
        return [furtherParse(e) for e in values]
    if value.count(',') == 1:
        values = value.split(',')
        if isFloat(values[0]) and isFloat(values[1]):
            return Pos(value)
        return [furtherParse(values[0]), furtherParse(values[1])]
    if ':' in value:
        values = value.split(':')
        return [furtherParse(values[0]), furtherParse(values[1])]
    if isFloat(value):
        return float(value)
    if value.replace('-', '', 1).isdigit():
        return int(value)
    return value

sprite_contents = {}
def getSpriteContent(spriteID):
    global sprite_contents
    if spriteID not in sprite_contents.keys():
        path = OUTPUT_PATH / "sprites/{}.txt".format(spriteID)
        t = read_txt(path)
        sprite_contents[spriteID] = t
    return sprite_contents[spriteID]


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
    def dist(self):
        return self.x * self.x + self.y * self.y

    @property
    def x( self ):
        return self[0]
    @property
    def y( self ):
        return self[1]

class Object(OrderedDict):
    
    def __getstate__(self): return self.__dict__
    def __setstate__(self, d): self.__dict__.update(d)
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
    
    def __init__(self, content = ""):
        parsed = objectFileLinesParser(content)
        self.update(parsed[0])
        super(OrderedDict, self).__setattr__('lineNums', parsed[1])
        super(OrderedDict, self).__setattr__('lines', parsed[2])
    
    def __getattr__(self, key):
        r = self[key]
        if key in list_tags and type(r) is not list: r = [r]
        return r
    
    def __setattr__(self, tag, value, index=None):
        if tag not in self.keys():
            raise KeyError('Tag {} not found in O[{}]. ({})'.format(tag, self.id, self.name))
            return
        lineNum = self.lineNums[tag]
        if type(self[tag]) is list and index is not None:
            oldValue = self[tag][index]
            self[tag][index] = value
            lineNum = lineNum[index]
        elif type(self[tag]) is not list and index is None:
            oldValue = self[tag]
            self[tag] = value
        else:
            raise TypeError('O[{}].{} is not a list. ({})'.format(self.id, tag, self.name))
            return
        lhs = f"{tag}="
        if tag == 'name': lhs = ""
        self.lines[lineNum] = self.lines[lineNum].replace(f"{lhs}{oldValue}", f"{lhs}{value}")
    
    def change(self, tag, index, value):
        return self.__setattr__(tag, value, index)
    
    def __getitem__(self, arg):
        if not isinstance(arg, int) and not isinstance(arg, slice):
            return super(OrderedDict, self).__getitem__(arg)
        if isinstance(arg, int):
            arg = [arg]
        if isinstance(arg, slice):
            length = len(self.pos)
            arg = list(range(length)[arg])
        
        if len(arg) == 0: return None
        a, b = arg[0], arg[-1] + 1
        return self._getSprites(a, b)
    
    def key(self, query=""):
        ks = list(self.keys())
        ks.sort()
        ks = [e for e in ks if query.lower() in e.lower() or query == ""]
        return ks
        
    def content(self):
        return "\n".join(self.lines)
    
    def copy(self):
        return Object(self.content())
    
    def linesByTag(self, tag):
        index = self.lineNums[tag]
        if type(index) is list:
            return [self.lines[i] for i in index]
        else:
            return self.lines[index]
    
    def save(self):
        id = self['id']
        path = OUTPUT_PATH / "objects" / f"{id}.txt"
        save_txt(self.content(), path)
#        Path(path/"cache.fcz").unlink(missing_ok=True)
        
        _store.state.objects[id] = self.copy()
        
        append_txt(f"{str(path)}\n", "changed_files.txt")
        
    def draw(self):
        return draw(self)
    
    
    def _getSprites(self, index_start, index_end = None):
        if index_end is None: index_end = index_start + 1
        spriteID = self.lineNums['spriteID']
        if type(spriteID) is int: spriteID = [spriteID]
        a = spriteID[index_start]
        if index_end >= len(self.spriteID):
            if 'headIndex' not in self.keys():
                raise IndexError('GetSprites index out of range ({}, {}).'.format(index_start, index_end))
            b = self.lineNums['headIndex']
        else:
            b = spriteID[index_end]
        
        o_copy = Sprites( '\n'.join(self.lines[a:b]) )
        if type(o_copy['parent']) is list:
            for i, v in enumerate(o_copy['parent']):
                v2 = int(v)
                if v2 < index_start or v2 >= index_end:
                    v2 = -1
                else:
                    v2 = v2 - index_start
                o_copy.__setattr__('parent', str(v2), i)
        return o_copy
    
    def _insertSprites(self, index, new_content):
        # first to last
        # back to front
        # 0 to N
        if type(new_content) is list: new_content = "\n".join(new_content)
        if type(new_content) is Sprites: new_content = new_content.content()
        partial_object = Sprites( new_content )
        
        extra_numSprites = len(partial_object.spriteID)
        old_numSprites = int(self.numSprites)
        self.numSprites = str( old_numSprites + extra_numSprites )
        
        parents = self.parent
        if len(parents) > 1:
            for i, v in enumerate( [int(e) for e in parents] ):
                if v >= index:
                    self.__setattr__("parent", str(v + extra_numSprites), i)
        parents = partial_object.parent
        if len(parents) > 1:
            for i, v in enumerate( [int(e) for e in parents] ):
                if v == -1: continue
                partial_object.__setattr__("parent", str(v + extra_numSprites), i)
        
        if index >= int(old_numSprites):
            insertAt_lineNum = self.lineNums['headIndex']
        else:
            insertAt_lineNum = self.lineNums['spriteID'][index]
        lines = self.lines
        lines[insertAt_lineNum:insertAt_lineNum] = partial_object.lines
        
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
        
        parents = self.parent
        for i, v in enumerate( [int(e) for e in parents] ):
            if v == index:
                self.__setattr__("parent", "-1", i)
            elif v > index:
                self.__setattr__("parent", str(v-1), i)

class Sprites(Object):
    
    def __init__(self, content):
        parsed = objectFileLinesParser(content)
        self.update(parsed[0])
        super(OrderedDict, self).__setattr__('lineNums', parsed[1])
        super(OrderedDict, self).__setattr__('lines', parsed[2])
        
    def __len__(self):
        return len(self.spriteID)
    
    def __repr__(self):
        pos = self.pos
        spriteID = self.spriteID
        parent = self.parent
        ss = ""
        for i in range(len(self)):
            p = Pos(pos[i])
            ss += f"{i:2} {parent[i]:2} {p.x:>10.6f},{p.y:>10.6f} {spriteID[i]:6} {getSpriteContent(spriteID[i])}\n"
        return ss
    
    def __contains__(self, other, verbose=False):
        if not isinstance(other, Sprites):
            raise TypeError('Sub-sprites condition involves {}.'.format(type(other).__name__))
        
        if len(other) > len(self): return False
        
        if len(other) == 1:
            if other["spriteID"] in self.spriteID:
                indexes = self.index(other["spriteID"])
                for index in indexes:
                    if other["color"] == self.color[index]:
                        return True
                    else:
                        if verbose: print( "Single sprite {} color mismatch {} vs {}.".format(other["spriteID"], other["color"], self.color[index]) )
            return False
        
        zeroSprite = other.spriteID[0]
        indexes = self.index(zeroSprite)
        if len(indexes) == 0:
            return False
        elif len(indexes) == 1:
            index1 = indexes[0]
        else:
            pos0 = other.pos[0]
            minDist = 9999999
            for i1, pos1 in enumerate(self.pos):
                d = (Pos(pos0) - Pos(pos1)).dist()
                if d < minDist:
                    minDist = d
                    index1 = i1
        
        for i0, sprite0 in enumerate(other.gspriteID):
            if sprite0 not in self.spriteID: return False
            
            found = False
            
            for i1, sprite1 in enumerate(self.spriteID):
                
                if verbose:
                    if sprite0 == sprite1:
                        a, b = other.delta(i0, 0), self.delta(i1, index1)
                        if a != b: print( "Sprite {} at index {}, delta mismatch {} vs {}.".format(sprite0, i1, a, b) )
                        a, b = other.rot[i0], self.rot[i1]
                        if a != b: print( "Sprite {} at index {}, rot mismatch {} vs {}.".format(sprite0, i1, a, b) )
                        a, b = other.hFlip[i0], self.hFlip[i1]
                        if a != b: print( "Sprite {} at index {}, hFlip mismatch {} vs {}.".format(sprite0, i1, a, b) )
                
                if sprite0 == sprite1 and \
                   other.delta(i0, 0) == self.delta(i1, index1) and \
                   other.rot[i0] == self.rot[i1] and \
                   other.hFlip[i0] == self.hFlip[i1]:
                    found = True
                if found: break
            if not found: return False
        return True
    
    def delta(self, i0, i1):
        p0 = Pos(self.pos[i0])
        p1 = Pos(self.pos[i1])
        return p1 - p0
    
    def index(self, id):
        return [i for i, v in enumerate(self.spriteID) if v == str(id)]

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
            
        self.raw = 0 # the smaller the value the more raw it is
        
    def __repr__(self):
        a_name, b_name, c_name, d_name = [ _store.state.names[e] if e in _store.state.names.keys() else str(e) for e in ( self.a, self.b, self.c, self.d ) ]
        
        import shutil
        total_width = shutil.get_terminal_size().columns
        if total_width == 80: total_width = 240
        id_length = 5
        flag_length = 5
        commas_length = 1 * 4
        numeric_trans_length = id_length * 4 + flag_length + commas_length
        seperator_length = 5 * 3
        name_length = math.floor((total_width - numeric_trans_length - seperator_length) / 4)
        
        max_lines = math.ceil(max([len(e) for e in (a_name, b_name, c_name, d_name)]) / name_length)
        
        ss = []
        for i in range(max_lines):
            
            s = ""
            s += f"{self.a:<{id_length}} {self.b:<{id_length}} {self.c:<{id_length}} {self.d:<{id_length}} {self.flag:<{flag_length}}" if i == 0 else " " * numeric_trans_length
            s += f"{a_name[i*name_length:(i+1)*name_length]:<{name_length}}"
            s += "  +  " if i == 0 else "     "
            s += f"{b_name[i*name_length:(i+1)*name_length]:<{name_length}}"
            s += "  =  " if i == 0 else "     "
            s += f"{c_name[i*name_length:(i+1)*name_length]:<{name_length}}"
            s += "  +  " if i == 0 else "     "
            s += f"{d_name[i*name_length:(i+1)*name_length]:<{name_length}}"
            
            ss.append(s)
        
        
        return '\n'.join(ss)
    
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
        path = OUTPUT_PATH / "transitions" / filename
        save_txt(content, path)
#        Path(path/"cache.fcz").unlink(missing_ok=True)
        
        _store.state.transitions[(self.a, self.b, self.flag)] = Transition(*self.toList())
        
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
        if len(filename_items) > 2: flag = '_'.join(filename_items[2:])
        return cls(actor, target, newActor, newTarget, flag, *items[2:])
    
    def delete(self):
        filename = f"{self.a}_{self.b}.txt"
        if self.flag != "": filename = f"{self.a}_{self.b}_{self.flag}.txt"
        path = OUTPUT_PATH / "transitions" / filename

        if not Path(path).exists(): print(f"TRANSITION DELETE NOT EXIST: {filename}")
        Path(path).unlink() # missing_ok=True)
        
        _store.state.transitions.pop((self.a, self.b, self.flag), None)
        
        append_txt(f"{str(path)}\n", "changed_files.txt")

class ListOfTransitions(list):
    
    def __add__(self, other):
        return ListOfTransitions(list(self) + list(other))
    
    def __repr__(self):
        return "\n".join([str(e) for e in self])
        
    def search(self, querystr):
        from .logic import pickerStyleStringFilter
        return ListOfTransitions(filter(lambda x: pickerStyleStringFilter(querystr, str(x)), self))
        
    def delete(self):
        for transition in self:
            transition.delete()
            
    def raw(self):
        return ListOfTransitions([t for t in self if t.raw == 0])
    
class ListOfObjects(list):
    def __repr__(self):
        r = []
        for e in self:
            if e in _store.state.names.keys():
                r.append( f"{str(e):<8}{_store.state.names[e]}" )
            else:
                r.append( f"{str(e):<8}" )
        return "\n".join(r)
    def __add__(self, other):
        return ListOfObjects(set(list(self) + list(other)))
    def __sub__(self, other):
        return ListOfObjects(set(self) - set(other))
    def intersection(self, other):
        return  self - (self - other)
    def search(self, querystr):
        from .logic import search
        return search(querystr, self)
    def items(self):
        return [ (i, _store.state.objects[i]) for i in self ]
    
    def __getitem__(self, *args):
        r = list(self).__getitem__(*args)
        if type(r) is int: r = [r]
        return ListOfObjects(r)
    
    def filter(self, func):
        return ListOfObjects([e for e in self if func(_store.state.objects[e])])
    def sort(self, key, reverse=False):
        return ListOfObjects(sorted(
            self, 
            key=lambda e: key(_store.state.objects[e]), 
            reverse=reverse
        ))

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
        
        path = OUTPUT_PATH / "categories" / f"{self.parentID}.txt"
        save_txt(content, path)
#        Path(path/"cache.fcz").unlink(missing_ok=True)
        
        _store.state.categories[self.parentID] = Category.load(content)
        
        append_txt(f"{str(path)}\n", "changed_files.txt")
    
    @property
    def name(self):
        return _store.state.objects[self.parentID].name




allKeys = []
def key(query=""):
    global allKeys
    if len(allKeys) == 0:
        for id, o in _store.state.objects.items():
            for key in o.keys():
                if key not in allKeys:
                    allKeys.append(key)
    
    print([e for e in allKeys if query.lower() in e.lower() or query == ""])


key_following = {}
def setObjectExtraProperty(o, newKey, newValue):
    global key_following
    if len(key_following) == 0:
        for id, o in _store.state.objects.items():
            
            linesFirstTag_dict = {}
            linesFirstTag = []
            for i, (key, lineNum) in enumerate(o.lineNums.items()):
                if type(lineNum) is not list:
                    lineNum = [lineNum]
                
                for n in lineNum:
                    if n not in linesFirstTag_dict.keys():
                        linesFirstTag_dict[n] = key
                
            for i2 in range(len(linesFirstTag_dict)):
                linesFirstTag.append( linesFirstTag_dict[i2] )
            
            for i, (key, lineNum) in enumerate(o.lineNums.items()):
                
                if i == 0:
                    key_following[key] = None
                    continue
                
                if type(lineNum) is list:
                    lineNum = lineNum[0]
                
                key_following[key] = linesFirstTag[lineNum - 1]
    
    key0 = key_following[newKey]
    lineNum0 = o.lineNums[key0]
    lines = o.lines
    lines[lineNum0+1:lineNum0+1] = ["{}={}".format(newKey, newValue)]
    
    return Object("\n".join(lines))

def draw(arg):
    from .draw import draw as d
    if type(arg) == int:
        arg = _store.state.objects[arg]    
    if type(arg) == Object or type(arg) == Sprites:
        arg = arg
    else:
        return
    return d(arg)