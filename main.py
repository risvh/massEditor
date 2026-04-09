import massEditor

if __name__ == '__main__':
    
    massEditor.init(options=[
        # "regenerate_all",
        # "regenerate_categories",
        # "regenerate_objects",
        # "regenerate_transitions",
        # "regenerate_depths",
        "regenerate_smart",
        ], verbose=True)
    
    
    # Do stuff here.
    
    # See README for full description. 
    # For example, this is how you loop through all the objects.
    
    # from massEditor import *
    # results = LO() # LO is shorthand for ListOfObjects
    # for id, o in O.items(): # O is shorthand for objects
    #     if o.permanent == 0 and o.blocksWalking == 1:
    #         results.append(id)
    # print(results)