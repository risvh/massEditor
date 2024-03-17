
import numpy as np
from PIL import Image

import massEditor
from massEditor import Pos, read_txt


def best_fit(oldsize, picsize):
    new_width, new_height = picsize
    old_width, old_height = oldsize
    if new_width * old_height < new_height * old_width:
        new_height = max(1, old_height * new_width // old_width)
    else:
        new_width = max(1, old_width * new_height // old_height)
    return (new_width, new_height)

def iconize(img):
    originalSize = img.size
    objectSize = (64, 64)
    iconSize = (96, 96)
    # objectSize = (128, 128)
    # iconSize = (192, 192)
    bestSize = originalSize
    if not (originalSize[0] < objectSize[0] and originalSize[1] < objectSize[1]):
        bestSize = best_fit(originalSize, objectSize)
        img = img.resize(bestSize)
    img2 = Image.new("RGBA", iconSize, (255, 255, 255, 128))
    offset = ((iconSize[0] - bestSize[0])//2, (iconSize[1] - bestSize[1])//2)
    img2.paste(img, offset, mask=img)
    return img2

def dodge(front,back):
    front = np.asarray(front)
    back = np.asarray(back)
    
    result=back*256.0/(256.0-front) 
    result[result>255]=255
    result[back==255]=255
    
    return Image.fromarray(result.astype('uint8'), 'RGBA')

def drawObject(id):
    
    o = massEditor.objects[id]
    
    dimension = (1024, 1024)
    img = Image.new("RGBA", dimension, (0, 0, 0, 0))
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
            arr = np.array(np.asarray(sprite_tga).astype('float'))
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
        
        if i in additiveBlend_sprites and not i == 0:
            temp = Image.new("RGBA", dimension, (0, 0, 0, 0))
            temp.paste(sprite_tga, offset, mask=sprite_tga)
            img = dodge(temp, img)
        else:
            img.paste(sprite_tga, offset, mask=sprite_tga)
    
    img = img.crop(img.getbbox())
    img = iconize(img)
    
    # img.show()
    
    return img