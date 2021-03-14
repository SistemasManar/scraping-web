import pytesseract
from collections import Counter
from PIL import Image, ImageFilter, ImageOps, ImageEnhance


paths = [
    'captcha1.png',
    'captcha2.png',
    'captcha3.png',
    'captcha4.png',
    'captcha5.png',
    'captcha6.png',
]
for path in paths:
    image = Image.open(path).convert('RGB')
    width, height = image.size
    image = image.resize((int(width*1.5), int(height*1.5)), Image.ANTIALIAS)

    # Remove some colors
    pixels = image.load()
    colors = []
    ending_purples = [131, 132, 133, 134, 135]
    for i in range(image.size[0]):
        for j in range(image.size[1]):
            pxs = pixels[i, j]
            # if pxs[2] not in ending_purples:
            #     pixels[i, j] =  (255, 255, 255)

            if pxs[0] not in [69, 70, 71, 72, 73, 74, 76, 77, 78, 79, 80, 81]:
                pixels[i, j] =  (255, 255, 255)

    # Apply some filters
    image = (image
        .filter(ImageFilter.SMOOTH)
        .filter(ImageFilter.SMOOTH)
        .filter(ImageFilter.SMOOTH)
        .filter(ImageFilter.MedianFilter)
    )
    image = ImageOps.invert(image)
    sharpness = ImageEnhance.Sharpness(image)
    image = sharpness.enhance(0.3)
    brightness = ImageEnhance.Brightness(image)
    image = brightness.enhance(1.0)
    image.show()

    counter = Counter(colors)
    print(counter.most_common())

    text = pytesseract.image_to_string(image, config='-c tessedit_char_whitelist=0123456789abcdef -psm 8')
    text = text.replace(' ', '')
    print(text)
