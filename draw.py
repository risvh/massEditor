
import numpy as np
from PIL import Image

import massEditor
from massEditor import Pos, read_txt


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

def setBackgroundColor(color):
    global backgroundColor
    backgroundColor = color

def bestFit(oldsize, picsize):
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
        bestSize = bestFit(originalSize, objectSize)
        img = img.resize(bestSize)
    img2 = Image.new("RGBA", iconSize, backgroundColor)
    offset = ((iconSize[0] - bestSize[0])//2, (iconSize[1] - bestSize[1])//2)
    img2.paste(img, offset, mask=img)
    return img2

def oldAttemptAtAdditiveBlend(front,back):
    front = np.asarray(front)
    back = np.asarray(back)
    
    result=back*256.0/(256.0-front) 
    result[result>255]=255
    result[back==255]=255
    
    return Image.fromarray(result.astype('uint8'), 'RGBA')

def additiveBlend(front, back):
    nsrc = np.asarray(front)
    ndst = np.asarray(back)
    
    # Extract the RGB channels
    srcRGB = nsrc[...,:3]
    dstRGB = ndst[...,:3]
    
    # Extract the alpha channels
    srcA = nsrc[...,3]
    dstA = ndst[...,3]
    
    
    srcScale = nsrc[...,3]/255.0 # GL_SRC_ALPHA
    dstScale = np.ones(ndst[...,3].shape) # GL_ONE
    
    # Work out resultant alpha channel
    outA = srcA * srcScale + dstA * dstScale
    outA[outA>255.0] = 255.0
    
    # Work out resultant RGB
    outRGB = ( srcRGB*srcScale[...,np.newaxis] + dstRGB*dstScale[...,np.newaxis] )
    outRGB[outRGB>255.0] = 255.0
    
    # Merge RGB and alpha back into single image
    outRGBA = np.dstack((outRGB,outA)).astype(np.uint8)

    
    return Image.fromarray(outRGBA.astype('uint8'), 'RGBA')

def drawObject(id):
    
    o = massEditor.objects[id]
    
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
            
            temp = Image.new("RGBA", sprite_tga.size, blacka)
            temp.paste(sprite_tga, (0, 0), mask=sprite_tga)
            sprite_tga = temp
            
            img.paste(sprite_tga, offset, mask=sprite_tga)
            size_check_img.paste(sprite_tga, offset, mask=sprite_tga)
    
    img = img.crop(size_check_img.getbbox())
    img = iconize(img)
    
    return img