
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

def transparent_color(color):
    new_color = (color[0], color[1], color[2], 0)
    return new_color

def remove_transparent_background(img):
    arr = np.array(img)
#    r, g, b, a = np.rollaxis(arr, axis=-1)
    a = arr[...,3]
    rgb = arr[...,:3]
    rgb[a==0] = 0
    arr = np.dstack((rgb, a))
    return Image.fromarray(arr.astype('uint8'), 'RGBA')

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

def blend(mode, front, back):
    nsrc = np.asarray(front)
    ndst = np.asarray(back)
    
    # Extract the RGB channels
    srcRGB = nsrc[...,:3]
    dstRGB = ndst[...,:3]
    
    # Extract the alpha channels
    srcA = nsrc[...,3]
    dstA = ndst[...,3]
    
    
    srcScale = nsrc[...,3]/255.0 # GL_SRC_ALPHA
    if mode == 'additive':
        dstScale = np.ones(ndst[...,3].shape) # GL_ONE
    elif mode == 'normal':
        dstScale = 1 - nsrc[...,3]/255.0 # GL_ONE_MINUS_SRC_ALPHA
    
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
    img = Image.new("RGBA", dimension, transparent_color(backgroundColor))
    
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
            
            temp = Image.new("RGBA", dimension, blacka)
            temp.paste(sprite_tga, offset, mask=sprite_tga)
            img = blend('additive', temp, img)
            
        else:
            
#            blacka_bg = Image.new("RGBA", sprite_tga.size, blacka)
#            
#            for m in range(3):
#                sprite_tga = Image.composite(sprite_tga, blacka_bg, sprite_tga)
#                
#            img.paste(sprite_tga, offset, mask=sprite_tga)
            
            temp = Image.new("RGBA", dimension, blacka)
            temp.paste(sprite_tga, offset, mask=sprite_tga)
            img = blend('normal', temp, img)
            

    background = Image.new("RGBA", dimension, backgroundColor)
    background.paste(img, (0, 0), mask=img)
    
    img = remove_transparent_background(img)
    
    img = background.crop(img.getbbox())
    
    img = iconize(img)
    
    return img

