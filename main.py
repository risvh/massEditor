
from massEditor import init

init(options=[
    # "regenerate_all",
    # "regenerate_categories",
    # "regenerate_objects",
    # "regenerate_transitions",
    # "regenerate_depths",
    "regenerate_smart",
    ], verbose=True)

from massEditor import *
from draw import drawObject, setBackgroundColor, blend, iconize





# sprites = list_dir("../output/sprites/", file=1)
# sprites = [e.replace(".tga","") for e in sprites if '.tga' in e]


# os = LO([4935,4940,4943,4944,4945,4946,4947,4948,4949])
# r = LO()
# missing = []

# for id, o in os.items():
#     ss = o.getAsList('spriteID')
#     for s in ss:
#         if s not in sprites:
#             r.append(id)
#             missing.append(s)
#             # break

