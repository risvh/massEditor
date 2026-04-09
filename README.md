# Mass Editor

A Python programmatic interface for [Two Hours One Life](https://github.com/twohoursonelife/OneLifeData7) and [One Hour One Life](https://github.com/jasonrohrer/OneLifeData7/) game content. It allows filtering and sorting of [objects](https://twohoursonelife.fandom.com/wiki/Objects_(Mechanics)), [transitions](https://twohoursonelife.fandom.com/wiki/Transitions_(Mechanics)), [categories](https://twohoursonelife.fandom.com/wiki/Categories_(Mechanics)) to make rule-based changes to them in batch and thoroughly.

# Setup

### Cloning the repo

The scripts expect folder structure as below, you may want to clone this repo into the same parent folder as other repos. (See [this page](https://twohoursonelife.fandom.com/wiki/Modding_Notes#Repositories) to learn more about the repos of the XHOL eco-system):
```
Root/
├── massEditor/
	├── massEditor/
	├── main.py	
	...
├── miniOneLifeCompile/
├── OneLife/
├── OneLifeData7/
├── minorGems/
└── output/
	├── animations/
	├── categories/
	├── objects/
	├── transitions/
	├── OneLife.exe
	...
```
Alternatively, if you're not modding and you only have the game folder, you can clone this repo into a `massEditor` folder that sits at the same level as your game folder, like this:
```
├── massEditor/
	├── massEditor/
	├── main.py	
	...
└── 2HOL/
	├── animations/
	├── categories/
	├── objects/
	├── transitions/
	├── OneLife.exe
	...
```

### Running the scripts

You can either use the scripts in a terminal: (Make sure you're in the outer `massEditor` folder. Add `-h` flag at the end to see help.)
``` bash
python -im massEditor
```
Or use it in an IDE that comes with IPython shell, e.g. Spyder. In that case, start scripting in [`main.py`](https://github.com/risvh/massEditor/blob/main/main.py).

# Quick Demo

```python
from massEditor import *

# Os is shorthand for a ListOfObjects containing all the objects
# Here we filter all objects for foods
foods = Os.filter(lambda o: o.foodValue.total != 0)

# We can also loop through a ListOfObjects in the way below,
# in case the filter is too complex for a lambda function

results = LO() # LO is shorthand for ListOfObjects

for id, o in foods.items():
    
    # An eating transition is denoted by
    # a food in slot A (Actor) and a value of -1 in slot B (Target)
    # In slot C we have 235, the id of a Clay Bowl
    eating_transitions = getTransitions(a=id, b=-1, c=235)
    
    # This way we filter for the foods that can be eaten and return a Clay Bowl
    if len(eating_transitions) > 0:
        results.append(id)

# Sort the results by crafting depths
# depths is a dict, key being object ids, and value being the crafting depth
results = results.sort(key=lambda o: depths[o.id])

# ListOfObjects prints nicely to read both object ids and names
print(results)

```
Output:
```
253     Bowl of Gooseberries
1355    Bowl of Carnitas
1175    Bowl of Green Beans
8764    Bowl of Cooked Rice
1121    Popcorn
1251    Bowl of Stew
10101   Bowl of Fish Stew
9067    Bowl of Tomato Soup
8540    Bowl of Chilli Con Carne# +emotEat_26_10
2198    Bowl of Turkey Broth
4647    Bowl of Honey
9068    Bowl of Mushroom Soup # +noFeeding +drug +emotEat_10_10
9069    Bowl of French Onion Soup
8584    Bowl of Maple Syrup
1242    Bowl of Sauerkraut
```

# Usage

This section provides some entry points you can start your script from.

## Start from objects
### Get object by id
```python
>>> obj = O[30]
>>> obj.name
'Wild Gooseberry Bush'
``` 
### Filter objects by property
```python
>>> permanent_objects = Os.filter(lambda o: o.permanent == 1)
```

[`key()`](https://github.com/risvh/massEditor/blob/main/DOCUMENTATION.md#keyquery) returns all keys an object can potentially have. You can do [`key(queryStr)`](https://github.com/risvh/massEditor/blob/main/DOCUMENTATION.md#keyquery) to look for a certain key.

### Get objects by name
```python
>>> search("cooked pie berry -carrot")
272     Cooked Berry Pie
276     Cooked Berry Rabbit Pie
```
### Get objects contained in a category
```python
>>> C[11625] # @ Any Mining Pick
8710    Bronze Mining Pick
684     Steel Mining Pick
```
### Get categories containing an object
```python
>>> getCategoriesOf(34) # Sharp Stone
1601    @ Pile Element
722     @ Shallow Digger
723     @ Rough Cutter
```
### Get objects by sprite id
```python
>>> getObjectsBySprite(145) # 145 is sprite ID of a sharp stone
34      Sharp Stone
6827    Pile of Sharp Stones
722     @ Shallow Digger
723     @ Rough Cutter
850     Stone Hoe
```
### Loop through all objects
```python
>>> blocking_nonpermanent_objects = LO() # LO is shorthand for ListOfObjects
>>> for id, o in O.items(): # O is shorthand for objects
>>>     if id not in depths.keys(): continue # Skip uncraftable objects
>>>     if o.permanent == 0 and o.blocksWalking == 1:
>>>         blocking_nonpermanent_objects.append(id)
```
## Start from transitions
### Get transitions that use an object
```python
>>> use(692) # Crown Blank
1051 692 0   7766 Red Rose        + Crown Blank = 0               + Crown Blank with Rose
402  692 0   698  Carrot          + Crown Blank = 0               + Crown Blank with Carrot
425  692 0   699  Wolf Skin       + Crown Blank = 0               + Crown Blank with Wolf Skin
62   692 0   697  Leaf            + Crown Blank = 0               + Crown Blank with Leaf
692  692 0   5260 Crown Blank     + Crown Blank = 0               + Hoops
441  692 441 2130 Smithing Hammer + Crown Blank = Smithing Hammer + Gold Ingot# just hammered
```
### Get transitions that make an object
```python
>>> make(74) # Fire Bow Drill
0  1423 134 74  0              + Bow Drill with Removed Tip = Flint Arrowhead + Fire Bow Drill
69 73   0   74  Short Shaft    + Bow Drill Bow              = 0               + Fire Bow Drill
74 67   74  75  Fire Bow Drill + Long Straight Shaft        = Fire Bow Drill  + Ember Shaft
```
### Get transitions by specifying slots
```python
>>> all_decay_transitions = getTransitions(a=-1, c=0)
```
## Data Stores and Shorthands

Data stores are the variables that contain the game content which you can manipulate with. There are also a few shorthands for class names.

`O` / `objects`  
A dict of all objects, with object id as key and the Object as value.

`C` / `categories`  
A dict of all categories, with object id of the category as key and the ListOfObjects that the category holds as value.

`Os`  
A ListOfObjects of all objects.

`names`  
A dict, with object id as key and object name as value.

`depths`  
A dict, with object id as key and crafting depth of the object as value.

`transitions`  
A dict of all transitions, with tuple of (actor, target, flag) as key, the corresponding Transition as value.

`raw_transitions`  
Same as above, but only contains transitions that exist on disk. Parsed transitions are not included.

`LO` / `ListOfObjects`  
A class that is essentially a Python list of ids. Prints with id and object name. Has methods to filter and allow set operations.

`LT` / `ListOfTransitions`  
A class that is essentially a Python list of Transition, prints nicely and allows filtering and set operations.


## Documentation

See [Documentation](https://github.com/risvh/massEditor/blob/main/DOCUMENTATION.md)
