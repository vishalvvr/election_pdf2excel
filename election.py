from pdf2image import convert_from_path, convert_from_bytes
from pytesseract import pytesseract
from PIL import Image, ImageEnhance
import yaml
import os, time, argparse

def ocr(img, locale="mar"):
    '''
    This is tesseract ocr function which will extract text from image
    :param image_path:
    :return: list of extracted strings
    '''
    try:
        print("ExtractTextFromImage method initializing")
        text_str = pytesseract.image_to_string(img, lang=locale)
        str_list = text_str.split("\n")
        str_list = list(filter(None, str_list))  # remove empty string
        return str_list
    except Exception as e:
        print(e)


def crop_image(img, axis=(25.63, 195.02, 1014.25, 1916.10)):
    '''
    image obj & crop cordinates (x1,y1,x2,y2)
    '''
    return img.crop(axis)


def pdf_2_img(filename, size=(1050,2050)):
    '''
    pdf filename & image resolution
    '''
    return convert_from_path(filename, size=size)


def main(pdf_name):
    images = pdf_2_img(pdf_name)
    for i,img in enumerate(images[2:len(images)-1]):
        cr = crop_image(img)
        img_w, img_h = cr.size

        cr.save(f"./tmp/{i}.png")
        
        
if __name__ == "__main__":
    if not os.path.isdir("./tmp"):
            os.makedirs("./tmp")
    pdf_name = "ward.pdf"
    main(pdf_name)
