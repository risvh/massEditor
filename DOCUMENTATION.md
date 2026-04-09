# Documentation

### `init(options=[], verbose=False)`

Initializes and loads game asset data or cache.

#### Parameters

- **`options`** (list, optional)  
  List of flags to toggle cache regeneration. Supported values:
  - `"regenerate_all"` – Regenerate all data types
  - `"regenerate_categories"` – Regenerate category cache
  - `"regenerate_objects"` – Regenerate object cache
  - `"regenerate_transitions"` – Regenerate transitions cache
  - `"regenerate_depths"` – Regenerate object depth map
  - `"regenerate_smart"` – Incrementally update only modified files
  
  Default: `[]`

- **`verbose`** (bool, optional)  
  Enable progress output during initialization. Default: `False`

---

### Class `Pos`

Represents a 2D position coordinate as a `list`.

**Constructor:**
- `Pos(x, y)` – Initialize with two floats
- `Pos("x,y")` – Parse from comma-separated string

**Properties:**
- `x` – X coordinate (read-only)
- `y` – Y coordinate (read-only)

**Methods:**
- `__add__(other)` – Vector addition, e.g. `posA + posB`
- `__sub__(other)` – Vector subtraction, e.g. `posA - posB`
- `dist()` – Return squared distance from origin

**String representation:** `"x.000000,y.000000"`

---

### Class `Object`

Represents a game object with its properties. An `OrderedDict` with property name as key, and un-parsed strings as values. (You can parse them with `furtherParse()`)

**Constructor:**
- `Object(content="")` – Parse from raw text file

**Methods:**
- `__getattr__(key)` – Access property by name, e.g. `obj.permanent`. For looking up the property names, see both `Object.key()` and `key()`. Note that the property values are parsed as `int`, `float` or special data types that allows better manipulation, e.g. `obj.sounds` has the type `Sounds`
- `__setattr__(tag, value, index=None)` – Modify property; updates internal line representation, e.g. `obj.permanent = '0'`
- `__getitem__(int|slice)` – Retrieve `Sprites` by index or index range, e.g. `obj[:]` returns the whole list of sprites of the object, `obj[0]` returns a list containing the first sprite (furthest in the back).
- `key(query="")` – List all property keys matching query; empty query lists all keys. Only listing the properties that this object has
- `content()` – Return `Object` to raw text string
- `copy()` – Create deep copy
- `linesByTag(tag)` – Get raw text lines for a property
- `save()` – Write to disk and update store
- `draw()` – Visualize object
- `_getSprites(start, end)` – Extract sprite range as `Sprites` object
- `_insertSprites(index, content)` – Insert sprites at position (Experimental)
- `_removeSprite(index)` – Remove sprite at position (Experimental)

**Attributes:**
- `_raw_dict` - Dict where the keys are the object's properties, and values are the raw string values of the properties, or list of strings in the case where the property can appear multiple times in an object file, e.g. `spriteID`
- `_lineNums` – Dict mapping property names to line numbers
- `_lines` – List of raw text lines

---

### Class `Sprites`

Subclass of `Object` representing sprite layer data.

**Methods:**
- `__len__()` – Number of sprites, e.g. `len(sprites)`
- `__repr__()` – Formatted table of sprite properties, e.g. `str(sprites)` or `print(sprites)`
- `__contains__(other)` – Check if other sprite set is subset (by id, color, position, rotation, flip), e.g. `spritesA in spritesB`
- `delta(i0, i1)` – Compute position difference between two sprite indices
- `index(id)` – Find all indices of sprites with given id

---

### Class `Transition`

Represents a transition in the format of `A + B = C + D (flag)`.

**Constructor:**
- `Transition(a, b, c, d, flag, ...)` – Initialize with object ids and optional parameters

**Fields:**
- `a`, `b`, `c`, `d` – Actor, target, newActor and newTarget object ids
- `flag` – [Transition flag](https://twohoursonelife.fandom.com/wiki/Transitions_(Mechanics)#Transition_Flags)
- `autoDecaySeconds`, `actorMinUseFraction`, `targetMinUseFraction`, `reverseUseActorFlag`, `reverseUseTargetFlag`, `noUseActorFlag`, `noUseTargetFlag`, `move`, `desiredMoveDist` – [Transition fields](https://twohoursonelife.fandom.com/wiki/Transitions_(Mechanics)#Other_Transition_Properties)
- `raw` – 1 means that this transition exists on disk, 0 means that this transition is generated/parsed during loading

**Methods:**
- `__repr__()` – Pretty-print with object names, e.g. `str(trans)` or `print(trans)`
- `copy()` – Create deep copy
- `toList()` – Convert to list representation
- `replace(old, new)` – Replace object id across all fields
- `save()` – Write to disk and update store
- `delete()` – Remove from disk and store
- `load(filename, content)` – Class method to parse from file (static)

---

### Class `ListOfTransitions`

List of `Transition` that pretty-prints and allows filtering.

**Methods:**
- `__add__(other)` – Combine two lists, e.g. `listA + listB`
- `__repr__()` – Print all transitions with numeric object ids and names, e.g. `str(transList)` or `print(transList)`
- `search(querystr)` – Filter the Transition's string representations by picker-style string query, i.e. can filter by object name or id
- `delete()` – Delete all transitions in the list from disk and from store
- `raw()` – Return only raw transitions that exist on disk, excluding the transitions that are generated/parsed during loading

---

### Class `ListOfObjects`

Collection of object ids that pretty-prints and allows filtering and set operations.

**Methods:**
- `__repr__()` – Print ids with names, e.g. `str(objList)` or `print(objList)`
- `__add__(other)` – set union between two `ListOfObjects`, e.g. `listA + listB`
- `__sub__(other)` – set difference between two `ListOfObjects`, e.g. `listA - listB`
- `intersection(other)` – set intersection between two `ListOfObjects`
- `search(querystr)` – Filter by object name with a picker-style string query
- `items()` – Get list of (id, Object) tuples
- `__getitem__()` – Slice and return as `ListOfObjects`, e.g. `objList[:3]`
- `filter(func)` – Filter by function applied to `Object`
- `sort(key, reverse=False)` – Sort by function applied to the `Object` members

---

### Class `Category`

Subclass of `ListOfObjects` representing a category of objects.

**Properties:**
- `parentID` – id of parent object
- `type` – Category type: `""` (normal category), `"pattern"`, `"probSet"` or `"contSet"`
- `name` – Name of parent object (read-only property)

**Methods:**
- `load(content)` – Class method to parse from raw category text file
- `save()` – Write category to disk and store
---
### `key(query="")`

Print all possible property keys from all objects, optionally filtered by query string.

**Parameters:**
- `query` (str, optional) – Case-insensitive substring to match against property keys. Default: `""` (returns all keys)

**Returns:** None (prints to stdout)

---

### Class `TrackedList`

A list that represents an `Object`'s sprite-related properties, e.g. `spriteID`. These sprite properties can appear multiple times in an object file, hence one `TrackedList` can represent several lines in a file. When this list is changed, the `Object` it is attached to changes accordingly, via `tag` and `callback`. `TrackedList` does not support `append()` or `pop()`.

**Constructor:**
- `TrackedList(items, tag, callback)` – `items` is the iterable. `tag` is the `Object` property this list is representing. `callback` is the `Object`'s `__setattr__()`

**Methods:**
- `__setitem__(index, value)` – Change element, e.g. `obj.spriteID[0] = 100`

---

### Class `TrackedIndexList`

A list that represents a property of an `Object` which is supposed to be a list of sprite indexes, e.g. `useAppearIndex`. When this list is changed, the `Object` it is attached to changes accordingly, via `tag` and `callback`.

**Constructor:**
- `TrackedIndexList(content, tag, callback)` – `content` is the raw object file line. `tag` is the `Object` property this list is representing. `callback` is the `Object`'s `__setattr__()`

**Methods:**
- `__repr__()` - Return the comma-joined list
- `__setitem__(index, value)` – Change element, e.g. `obj.useAppearIndex[0] = 2`
- `append(value)` - Add to the end of the list, e.g. `obj.useAppearIndex.append(2)`
- `pop(index=-1)` - Remove an element by index, e.g. `removed_element = obj.useAppearIndex.pop(0)`

---

### `setObjectExtraProperty(obj, newKey, newValue)`

(Experimental) Add a new property to an object. The function will try to add this property following the same ordering of properties in other objects.

**Parameters:**
- `obj` (Object) – Target object to modify
- `newKey` (str) – Property name
- `newValue` (str) – Property value

**Returns:** Object – New `Object` instance with the added property

---

### `draw(arg)`

(Requires PIL package) Visualize a game object or sprite(s).

**Parameters:**
- `arg` (int | Object | Sprites) – Object id, `Object` instance, or `Sprites` instance to visualize

**Returns:** Rendered visualization of the object or sprite(s)

---

### `furtherParse(value)`

(Experimental) Parse string values into native Python types and custom types.

**Parameters:**
- `value` (str | list | any) – Value to parse. If list, recursively parses each element.

**Returns:** 
- Parsed value (float, int, list, `Pos`, or original string)

```python
furtherParse("1.234567")  # → 1.234567 (float)
furtherParse("42")  # → 42 (int)
furtherParse("1.500000,2.300000")  # → Pos(1.5, 2.3)
furtherParse("1.000000#biomes_0")  # → [1.0, 'biomes_0']
furtherParse("1,2,3")  # → [1, 2, 3]
furtherParse("unknown")  # → "unknown" (unchanged string)
```

---

### `isCategory(id)`
Checks if an id represents a standard category (not a pattern or probability set).
- **Parameters**: `id` - Object id 
- **Returns**: `bool` - True if object is a category and not pattern or probability set

---

### `isPattern(id)`
Checks if an id represents a pattern category.
- **Parameters**: `id` - Object id
- **Returns**: `bool` - True if pattern category

---

### `isProbSet(id)`
Checks if an id represents a probability set category type.
- **Parameters**: `id` - Object id
- **Returns**: `bool` - True if probability set

---

### `getCategoriesOf(id)`
Retrieves all categories containing a given object id.
- **Parameters**: `id` - Object id
- **Returns**: `ListOfObjects` - object ids of categories that contain the object

---

### `search(querystr, pool=None)`
Searches objects by name similar to a [picker](https://twohoursonelife.fandom.com/wiki/Picker#Search_Field).
- **Parameters**:
  - `querystr` - Query string. Modifiers `-` (negation) and `.` (exact match) are accepted
  - `pool` - Optional `ListOfObjects` to search (default: all objects)
- **Returns**: `ListOfObjects` - Matching object ids

---

### `make(id)`
Retrieves transitions where object is newActor or newTarget.
- **Parameters**: `id` - Object id
- **Returns**: `ListOfTransitions` - both raw and generated/parsed transitions

---

### `use(id)`
Retrieves transitions where object is actor or target.
- **Parameters**: `id` - Object id
- **Returns**: `ListOfTransitions` - both raw and generated/parsed transitions

---

### `getTransitions(a=None, b=None, c=None, d=None)`
Queries transitions by Actor, Target, newActor or newTarget.
- **Parameters**:
  - `a` - Actor (optional)
  - `b` - Target (optional)
  - `c` - newActor (optional)
  - `d` - newTarget (optional)
- **Returns**: `ListOfTransitions` - both raw and generated/parsed transitions matching the query

---

### `getObjectsBySprite(sprite_id)`
Finds all objects using a specific sprite.
- **Parameters**: `sprite_id` - Sprite id
- **Returns**: `ListOfObjects` - Object ids with given sprite

---

### `getObjectsBySound(sound_id)`
Finds all objects using a specific sound.
- **Parameters**: `sound_id` - Sound id
- **Returns**: `ListOfObjects` - Object ids with given sound

---

### `getAncestors(id)`
Retrieves immediate ancestor objects of an object, i.e. objects with one depth level above
- **Parameters**: `id` - Object id
- **Returns**: `ListOfObjects`

---

### `sortObjectsByDepth(lo)`
Sorts objects by depth (highest first, 9999 for unknown).
- **Parameters**: `lo` - `ListOfObjects`
- **Returns**: `ListOfObjects` - Sorted list

---

### `printObjectsWithDepth(lo)`
Debug utility printing objects with depth values.
- **Parameters**: `lo` - `ListOfObjects`
- **Returns**: None (prints to stdout)
- **Format**: `{depth} {id} {name}`

---

### `completelyDeleteObject(id)`
Delete the object, and the transitions and categories that involve it.
- **Parameters**: `id` - Object id to delete
- **Returns**: None

---

### `checkForMissingSprites()`
Identifies sprite ids referenced but not found in sprites directory.
- **Parameters**: None
- **Returns**: `list` - Missing sprite ids

---

### `checkForMissingObjects()`
Identifies object ids referenced in `transitions` but not found in `objects`.
- **Parameters**: None
- **Returns**: `list` - Missing object ids

---

### Class `MapChance`

Represents the `mapChance` property of an `Object`.

**Constructor:**
- `MapChance(content, callback)` – `content` is the raw string of the property value. `callback` is the `__setattr__` of the `Object` which this property is attached to

**Methods:**
- `__repr__()` – Return the formatted string of this property
- `__setattr__(tag, value)` – Change the `chance` or `biomes`, e.g. `obj.mapChance.chance = 0.5`

**Attributes:**
- `chance` - `float`, the map chance value
- `biomes` – `tuple` of `int` that represent the biomes

**String representation:** `"1.000000#biomes_0,3,4,5"`

---

### Class `Sounds`

Represents a `sounds` property of an `Object`.

**Constructor:**
- `Sounds(content, callback)` - `content` is the raw string of the property value. `callback` is the `__setattr__` of the `Object` which this property is attached to

**Methods:**
- `__repr__()` – Return the formatted string of this property
- `__setattr__(tag, value)` – Access the `Sound` of this property, e.g. `obj.sounds.creation.volume = 0.5`
- `ids()` - Return a `set` containing the sound IDs used in this property

**Attributes:**
- `creation`, `using`, `eating` or `decay` - Sound types, see [this wiki page](https://twohoursonelife.fandom.com/wiki/Object_Page#Sound_Related)

**String representation:** `"369:0.500000,74:0.250000#496:0.250000,-1:1.000000,-1:1.000000"`

---

### Class `Sound`

Represents a sound under the class `Sounds`.

**Constructor:**
- `Sound(soundTag, sound, volume, callback, index=None)` - See Attributes below

**Methods:**
- `__repr__()` – Return the formatted string of this property
- `__setattr__(tag, value)` – Change the `sound` or `volume` of this property, e.g. `obj.sounds.creation.volume = 0.5`. The other attributes cannot be changed

**Attributes:**
- `soundTag` - The sound type, either `creation`, `using`, `eating` or `decay`
- `sound` - The sound ID
- `volume` - A `float` representing the volume
- `callback` - To change the parent `Sounds`
- `index=None` - The index of this sound in case this is a subsound 

**String representation:** `"369:0.500000"`

---

### Class `NumSlots`

Represents a `numSlots` property of an `Object`.

**Constructor:**
- `NumSlots(content, callback)` - `content` is the raw string of the property value. `callback` is the `__setattr__` of the `Object` which this property is attached to

**Methods:**
- `__repr__()` – Return the formatted string of this property
- `__setattr__(tag, value)` – Change the `num` or `timeStretch` of this property, e.g. `obj.numSlots.num = 3`. The other attributes cannot be changed

**Attributes:**
- `num` - An `int` of the number of slots
- `timeStretch` - A `float`, usually just `1.000000` as this mechanics is not used in the game

**String representation:** `"3#timeStretch=1.000000"`

---

### Class `TapoutTrigger`

Represents a `tapoutTrigger` property of an `Object`.

**Constructor:**
- `TapoutTrigger(content, callback)` - `content` is the raw string of the property value. `callback` is the `__setattr__` of the `Object` which this property is attached to

**Methods:**
- `__repr__()` – Return the formatted string of this property
- `__setattr__(tag, value)` – Change the `parameters` of this property, e.g. `obj.tapoutTrigger.parameters = (0,3,3,1)`
- `pprint()` - Print out the values of this property, with details of what the `tapoutTrigger` parameters represent

**Attributes:**
- `toggle` - Should always be 1. To toggle off, this property should be removed from the object file
- `parameters` - `tuple`, the first value is the tapout mode, see the `+tapoutTrigger` tag in [this wiki page](https://twohoursonelife.fandom.com/wiki/Objects_(Mechanics)#Tags) for more information

**String representation:** `"1#0,3,3,1"`

---

### Class `FoodValue`

Represents a `foodValue` property of an `Object`.

**Constructor:**
- `FoodValue(content, callback)` - `content` is the raw string of the property value. `callback` is the `__setattr__` of the `Object` which this property is attached to

**Methods:**
- `__repr__()` – Return the formatted string of this property
- `__setattr__(tag, value)` – Change the `base` or `bonus` of this property, e.g. `obj.foodValue.bonus = 4`
- `total()` - Return the sum of `base` and `bonus` values

**Attributes:**
- `base` - `int`, base food value
- `bonus` - `int`, bonus food value

**String representation:** `"1,16"`

---

### Class `NumUses`

Represents a `numUses` property of an `Object`.

**Constructor:**
- `NumUses(content, callback)` - `content` is the raw string of the property value. `callback` is the `__setattr__` of the `Object` which this property is attached to

**Methods:**
- `__repr__()` – Return the formatted string of this property
- `__setattr__(tag, value)` – Change the `num` or `chance` of this property, e.g. `obj.numUses.chance = 0.5`

**Attributes:**
- `num` - `int`, number of uses
- `chance` - `float`, use chance

**String representation:** `"6,1.000000"`
