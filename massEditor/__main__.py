import sys
import argparse
import textwrap
import massEditor

if __name__ == "__main__":
    
    description = textwrap.dedent("""
        MassEditor - a programmatic editor of XHOL game assets
        
        Example Usage:
            >>> objects[30] # returns the Object Wild Gooseberry Bush which id is 30.
            >>> search("horse cart -outdated") # return a ListOfObjects with names matching the picker-style query.
            >>> use(30) # return a ListOfTransitions how Wild Gooseberry Bush can be used.
            >>> draw(3338) # draw a Glass Bottle.
            >>> Os.filter(lambda o: o.permanent == '0' and o.blocksWalking == '1') # return a ListOfObjects that are blocking but not permanent.
            >>> getTransitions(a=-1) # return a ListOfTransitions that contains all the decay transitions.
            
            >>> # This is how to loop through all the objects
            >>> results = LO() # shorthand for ListOfObjects
            >>> for id, o in O.items():
            >>>   if o.foodValue != '0':
            >>>     results.append(id)
        
        Data stores and Shorthands:
            O / objects - a dict of all objects, key is object id and value is the Object with that id.
            C / categories - a dict of all categories, key is object id of the category's parent object and value is the ListOfObjects that category holds.
            LO / ListOfObjects - a class that is essentially a python list of ids. Prints with id and object name. Has methods to filter and allow set operations.
            LT / ListOfTransitions - a class that is essentially a python list of Transition.
            Os - a ListOfObjects of all objects.
            names - a dict, key is object id and value is the name of the object with that id.
            depths - a dict, key is object id and value is the depth of the object with that id.
            transitions - a dict of all transitions, key is a tuple of (actor, target, flag), value is the corresponding Transition.
            raw_transitions - same as above, but only contains transitions that exist on disk. Parsed transitions are not included.
        """)
    
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawDescriptionHelpFormatter, exit_on_error=False)
    parser.add_argument("-a", "--all", action="store_true", help="regenerate all cache")
    parser.add_argument("-c", "--category", action="store_true", help="regenerate category cache")
    parser.add_argument("-o", "--object", action="store_true", help="regenerate object cache")
    parser.add_argument("-t", "--transition", action="store_true", help="regenerate transition cache")
    parser.add_argument("-d", "--depth", action="store_true", help="regenerate depth map")
    
    try:
        args = parser.parse_args()
    except SystemExit:
        import os
        os._exit(0)
    
    options = []
    if args.all: options.append("regenerate_all")
    if args.category: options.append("regenerate_categories")
    if args.object: options.append("regenerate_objects")
    if args.transition: options.append("regenerate_transitions")
    if args.depth: options.append("regenerate_depths")
    options.append("regenerate_smart")
        
    massEditor.init(options=options, verbose=True)
    
    from massEditor import *