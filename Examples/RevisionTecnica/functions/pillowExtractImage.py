import pytesseract
import cv2
import base64
import re

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\USER\AppData\Local\Tesseract-OCR\tesseract.exe'


def load_captcha(page_soup):
    containers = page_soup.findAll("div", {"class": "col-sm-4 col-md-3 col-lg-3"})
    container = containers[0]
    img_data_url = container.div.img["src"]
    base64_image = img_data_url.split(',')[1].replace(' ', '+')

    imgdata = base64.b64decode(base64_image)
    filename = 'ejemplo_descargado.jpg'
    with open(filename, 'wb') as f:
        f.write(imgdata)

    # Grayscale, Gaussian blur, Otsu's threshold
    image = cv2.imread('D:\python-projects\RevisionTecnica\scrap example 2\ejemplo_descargado.jpg')
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    # Morph open to remove noise and invert image
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    invert = 255 - opening

    text = pytesseract.image_to_string(invert, lang='eng', config='--psm 7')
    return text


def is_reg_placa(placa):
    x = re.match(r"^[0-9]*$", placa)
    return x
