import math
from PIL import Image

# TODO: take in image and color (default to white) as parameters ?
# or just put this into the notebook?

def lcm(x, y):
    x2 = math.ceil(x/64)*64
    y2 = math.ceil(y/64)*64
    return x2, y2

im = Image.open('samples/Fritzi_Ritz.jpg')

def add_margin(pil_img, color):
    width, height = pil_img.size
    new_width, new_height = lcm(width, height)
    result = Image.new(pil_img.mode, (new_width, new_height), color)
    result.paste(pil_img, (0, 0))

    print('original size: ', width, height)
    print('new size: ', new_width, new_height)

    return result

im_new = add_margin(im, (256, 256, 256))
im_new.save('samples/padded.jpg', quality=95)