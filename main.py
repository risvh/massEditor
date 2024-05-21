
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
from draw import drawObject, setBackgroundColor, additiveBlend, iconize


# img = drawObject(30)

# use(30)





    




# ### Find all wall-destructive transitions
# def isWall(id):
#     if id <= 0:
#         return False
#     o = O[id]
#     if 'wallLayer' in o.keys() and o.wallLayer == '1':
#         return True
#     if 'floorHugging' in o.keys() and o.floorHugging == '1':
#         return True
#     return False
#
# for id, o in O.items():
#     if isWall(id):
#         # print(id, o.name)
#         ts = getTransition(b=id)
#         for t in ts:
#             if t.a > 0 and t.c > 0 and t.d not in categories and t.b == id and not isWall(t.d):
#                 t.pprint()
        


# def isFloor(id):
#     if id <= 0:
#         return False
#     if id not in O.keys():
#         return False
#     o = O[id]
#     if 'floor' in o.keys() and o.floor == '1':
#         return True
#     return False






def getNumUses(id):
    if id <= 0: return -1
    if id not in O.keys(): return -1
    o = O[id]
    if 'numUses' not in o.keys(): return -1
    return int(o.numUses.split(',')[0])

def getUseChance(id):
    if id <= 0: return -1
    if id not in O.keys(): return -1
    o = O[id]
    if 'numUses' not in o.keys(): return -1
    if ',' not in o.numUses: return -1
    return float(o.numUses.split(',')[1])

def hasUse(id):
    numUses = getNumUses(id)
    if numUses > 1: return True
    return False

def validUsePair(a, b):
    if hasUse(a) and hasUse(b):
        if getNumUses(a) == getNumUses(b):
            if getUseChance(a) == getUseChance(b):
                return True
    return False

def transUseType(t):
    if not( hasUse(t.a) or hasUse(t.b) or hasUse(t.c) or hasUse(t.d) ): return 0
    if validUsePair(t.a, t.c): return 1 # actor pass-through
    if validUsePair(t.b, t.d): return 2 # target pass-through
    if validUsePair(t.a, t.d): return 3 # cross-pass-through from actor to newTarget
    if validUsePair(t.b, t.c): return 4 # cross-pass-through from target to newActor
    return -1 










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





import numpy as np
from PIL import Image

white = (255,255,255,255)
black = (0,0,0,255)
grey = (128,128,128,255)
whitea = (255,255,255,0)
blacka = (0,0,0,0)
greya = (128,128,128,0)
red = (255,0,0,255)
green = (0,255,0,255)
blue = (0,0,255,255)

backgroundColor = grey
setBackgroundColor(backgroundColor)

id = 3338

o = O[id]

dimension = (1024, 1024)
img = Image.new("RGBA", dimension, backgroundColor)
size_check_img = Image.new("RGBA", dimension, blacka)
sprite_tga = 0

additiveBlend_sprites = []
if 'spritesAdditiveBlend' in o.keys():
    additiveBlend_sprites = [int(e) for e in o.spritesAdditiveBlend.split(',')]

for i, (sprite, pos, rot, hFlip, color) in enumerate(zip(o.getAsList("spriteID"), o.getAsList("pos"), o.getAsList("rot"), o.getAsList("hFlip"), o.getAsList("color"))):
    
    sprite_tga = Image.open(f"../output/sprites/{sprite}.tga")
    sprite_text = read_txt(f"../output/sprites/{sprite}.txt")
    sprite_text_parts = sprite_text.split()
    anchor_pos = (int(sprite_text_parts[-2]), int(sprite_text_parts[-1]))
    pos = Pos(pos)
    
    if color != '1.000000,1.000000,1.000000':
        # arr = np.array(np.asarray(sprite_tga).astype('float'))
        arr = np.array(sprite_tga)
        r, g, b, a = np.rollaxis(arr, axis=-1)
        r1, g1, b1 = [float(e) for e in color.split(",")]
        r = r * r1
        g = g * g1
        b = b * b1
        arr = np.dstack((r, g, b, a))
        sprite_tga = Image.fromarray(arr.astype('uint8'), 'RGBA')
    
    if hFlip == '1': sprite_tga = sprite_tga.transpose(Image.FLIP_LEFT_RIGHT)
    sprite_w, sprite_h = sprite_tga.size
    rotate_center = (sprite_w//2 + anchor_pos[0], sprite_h//2 + anchor_pos[1])
    sprite_tga = sprite_tga.rotate(-float(rot) * 360, center=rotate_center, expand=True)
    sprite_w, sprite_h = sprite_tga.size
    offset = (dimension[0]//2 - sprite_w//2 + int(pos.x) - anchor_pos[0], dimension[1]//2 - sprite_h//2 - int(pos.y) - anchor_pos[1])
    
    
    if i in additiveBlend_sprites:
        temp = Image.new("RGBA", dimension, black)
        temp.paste(sprite_tga, offset, mask=sprite_tga)
        img = additiveBlend(temp, img)
        
        size_check_temp = Image.new("RGBA", dimension, blacka)
        size_check_temp.paste(sprite_tga, offset, mask=sprite_tga)
        size_check_img = additiveBlend(size_check_temp, size_check_img)
    else:
        
        # mask = np.array(sprite_tga)
        # mask[mask/255<0.5] = 0
        # maskRGB = mask[...,:3]
        # maskA = mask[...,3]
        # maskRGB[:] = 0
        # maskA[maskA!=255] = 0
        # mask = np.dstack((maskRGB,maskA)).astype(np.uint8)
        # mask = Image.fromarray(mask.astype('uint8'), 'RGBA')
        
        # mask = sprite_tga.convert('1') 
        
        # temp = Image.new("RGBA", sprite_tga.size, blacka)
        # temp.paste(sprite_tga, (0, 0), mask=mask)
        
        
        
        # temp2 = Image.new("RGBA", sprite_tga.size, blacka)
        # temp2.paste(temp, (0, 0), mask=sprite_tga)
        
        # temp3 = Image.new("RGBA", sprite_tga.size, blacka)
        # temp3.paste(temp2, (0, 0), mask=sprite_tga)
        
        # temp4 = Image.new("RGBA", sprite_tga.size, blacka)
        # temp4.paste(temp3, (0, 0), mask=sprite_tga)
        
        # temp5 = Image.new("RGBA", sprite_tga.size, blacka)
        # temp5.paste(temp4, (0, 0), mask=sprite_tga)
        
        
        blacka_bg = Image.new("RGBA", sprite_tga.size, blacka)
        
        for m in range(3):
            sprite_tga = Image.composite(sprite_tga, blacka_bg, sprite_tga)
        
        # sprite_tga = temp
        
        img.paste(sprite_tga, offset, mask=sprite_tga)
        size_check_img.paste(sprite_tga, offset, mask=sprite_tga)
        
    # if i == 1: 1/0

img = img.crop(size_check_img.getbbox())
img = iconize(img)











