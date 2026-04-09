class MapChance():
    
    def __init__(self, content, callback):
        super().__setattr__('chance', float(content.split('#biomes_')[0]))
        super().__setattr__('biomes', tuple([int(e) for e in content.split('#biomes_')[1].split(',')]))
        super().__setattr__('callback', callback)
    
    def __repr__(self):
        return f"{self.chance:.6f}#biomes_{','.join([str(e) for e in self.biomes])}"
    
    @staticmethod
    def test(string):
        return '#biomes_' in string
    
    def __setattr__(self, tag, value):
        oldValue = MapChance(str(self), self.callback)
        super().__setattr__(tag, value)
        self.callback('mapChance', self, oldValue)

class Sound():
    
    def __init__(self, soundTag, sound, volume, callback, index=None):
        super().__setattr__('soundTag', soundTag)
        super().__setattr__('sound', sound)
        super().__setattr__('volume', volume)
        super().__setattr__('callback', callback)
        super().__setattr__('index', index)

    def __repr__(self):
        if self.volume == 0.0:
            return f"{self.sound}:{self.volume:.1f}"
        else:
            return f"{self.sound}:{self.volume:.6f}"
    
    def __setattr__(self, tag, value):
        if tag == 'sound':
            newSound = Sound(self.soundTag, value, self.volume, self.callback, self.index)
        elif tag == 'volume':
            newSound = Sound(self.soundTag, self.sound, value, self.callback, self.index)
        else:
            return
        self.callback(self.soundTag, newSound, self.index)

class Sounds():
    
    def __init__(self, content, callback):
        
        tags = ['creation', 'using', 'eating', 'decay']
        values = content.split(',')
        objs = []
        for tag, value in zip(tags, values):
            if '#' in value:
                subSounds = []
                subSoundStrings = value.split('#')
                for i, subSoundString in enumerate(subSoundStrings):
                    soundString, volumeString = subSoundString.split(':')
                    obj = Sound(tag, int(soundString), float(volumeString), self.__setattr__, i)
                    subSounds.append(obj)
                objs.append(subSounds)
            else:
                soundString, volumeString = value.split(':')
                obj = Sound(tag, int(soundString), float(volumeString), self.__setattr__)
                objs.append(obj)
        
        super().__setattr__('creation', objs[0])
        super().__setattr__('using', objs[1])
        super().__setattr__('eating', objs[2])
        super().__setattr__('decay', objs[3])
        
        super().__setattr__('callback', callback)
        
        
        
    def __repr__(self):
        str1 = str(self.creation) if type(self.creation) == Sound else '#'.join([str(e) for e in self.creation])
        str2 = str(self.using) if type(self.using) == Sound else '#'.join([str(e) for e in self.using])
        str3 = str(self.eating) if type(self.eating) == Sound else '#'.join([str(e) for e in self.eating])
        str4 = str(self.decay) if type(self.decay) == Sound else '#'.join([str(e) for e in self.decay])
        return ','.join([str1, str2, str3, str4])
    
    @staticmethod
    def test(string):
        return string.count(':') >= 4
    
    def __setattr__(self, tag, value, index=None):
        
        oldValue = Sounds(str(self), self.callback)
        
        if index is not None:
            sounds = self.__getattribute__(tag)
            if type(sounds) == Sound:
                raise TypeError(f'Sounds.{tag} is not a list.')
                return
            sounds[index] = value
        else:
            super().__setattr__(tag, value)
        
        self.callback('sounds', self, oldValue)
        
    @property
    def ids(self):
        firstLevel = [self.creation, self.using, self.eating, self.decay]
        r = set()
        for value in firstLevel:
            if type(value) == Sound:
                r.add(value.sound)
            elif type(value) == list:
                for e in value:
                    r.add(e.sound)
        return r

class NumSlots():
    
    def __init__(self, content, callback):
        super().__setattr__('num', int(content.split('#timeStretch=')[0]))
        super().__setattr__('timeStretch', float(content.split('#timeStretch=')[1]))
        super().__setattr__('callback', callback)
    
    def __repr__(self):
        return f"{self.num}#timeStretch={self.timeStretch:.6f}"
    
    @staticmethod
    def test(string):
        return '#timeStretch=' in string
    
    def __setattr__(self, tag, value):
        oldValue = NumSlots(str(self), self.callback)
        super().__setattr__(tag, value)
        self.callback('numSlots', self, oldValue)
        
class TapoutTrigger():
    
    def __init__(self, content, callback):
        toggle, values = content.split('#')
        super().__setattr__('toggle', int(toggle))
        values = [int(e) for e in values.split(',')]
        super().__setattr__('parameters', tuple(values))
        super().__setattr__('callback', callback)
    
    def __repr__(self):
        return f"{self.toggle}#{','.join([str(e) for e in self.parameters])}"
    
    def pprint(self):
        print( f"line: {str(self)}")
        print( f"toggle: {self.toggle}")
        modes = ['Area tapout. x radius, y radius, limit(optional).', 'Coordinates. x, y.', 'Directional tapout. N radius, E radius, S radius, W radius, limit(optional).']
        mode = self.parameters[0]
        print( f"mode: {mode} - {modes[mode]}")
        if mode == 0:
            print(f"radiusN / radiusS: {self.parameters[2]}")
            print(f"radiusE / radiusW: {self.parameters[1]}")
            if len(self.parameters) > 3:
                print(f"limit: {self.parameters[3]}")
        elif mode == 1:
            print(f"specificX: {self.parameters[1]}")
            print(f"specificY: {self.parameters[2]}")
        elif mode == 2:
            print(f"radiusN: {self.parameters[1]}")
            print(f"radiusE: {self.parameters[2]}")
            print(f"radiusS: {self.parameters[3]}")
            print(f"radiusW: {self.parameters[4]}")
            if len(self.parameters) > 5:
                print(f"limit: {self.parameters[5]}")
    
    def __setattr__(self, tag, value):
        oldValue = TapoutTrigger(str(self), self.callback)
        if tag == 'parameters':
            if type(value) is str:
                value = [int(e) for e in value.split(',')]
            if type(value) is list:
                value = tuple(value)
            super().__setattr__('parameters', value)
        elif tag == 'toggle':
            raise KeyError('To disable tapoutTrigger, remove the tag instead.')
            return
            
        self.callback('tapoutTrigger', self, oldValue)

class FoodValue():
    def __init__(self, content, callback):
        values = [int(e) for e in content.split(',')]
        base = values[0]
        bonus = 0
        if len(values) > 1: bonus = values[1]
        super().__setattr__('base', base)
        super().__setattr__('bonus', bonus)
        super().__setattr__('callback', callback)
    
    def __repr__(self):
        if self.bonus == 0:
            return f"{self.base}"
        else:
            return f"{self.base},{self.bonus}"
    
    @property
    def total(self):
        return self.base + self.bonus
    
    def __setattr__(self, tag, value):
        oldValue = FoodValue(str(self), self.callback)
        super().__setattr__(tag, value)
        self.callback('foodValue', self, oldValue)

class NumUses():
    def __init__(self, content, callback):
        values = content.split(',')
        num = int(values[0])
        chance = 1.0
        if len(values) > 1: chance = float(values[1])
        super().__setattr__('num', num)
        super().__setattr__('chance', chance)
        super().__setattr__('callback', callback)

    def __repr__(self):
        return f"{self.num},{self.chance:.6f}"
    
    def __setattr__(self, tag, value):
        oldValue = NumUses(str(self), self.callback)
        super().__setattr__(tag, value)
        self.callback('numUses', self, oldValue)

special_types = {
    'mapChance': MapChance,
    'sounds': Sounds,
    'numSlots': NumSlots,
    'tapoutTrigger': TapoutTrigger,
    'foodValue': FoodValue,
    'numUses': NumUses,
    }