from PIL import Image
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent / 'users/avatars/'

def watermark_photo(input_image_path, output_image_path, watermark_image_path, position):
    base_image = Image.open(input_image_path)
    watermark = Image.open(watermark_image_path)
    base_image.paste(watermark, position)
    base_image.show()
    base_image.save(output_image_path)



if __name__ == '__main__':
    # path = PROJECT_ROOT / 'users/avatars/default_avatar.png'
    # show_avatar_image(path)

    img = 'default_avatar.png'
    img_2 =  'lighthouse_watermarked2.png'
    watermark =  'watermark.png'
    watermark_photo(img, img_2, watermark, position=(0,0))