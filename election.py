from pdf2image import convert_from_path, convert_from_bytes
from pytesseract import pytesseract
from PIL import Image, ImageEnhance
import yaml
import os, time, argparse


conf = {
        "pdf_name" : "ward.pdf",
        "pdf_page_start" : 4,
        "pdf_page_end" :  76,
        "pdf_img_size":(1050,2050),
        "crop_img_axis": (25.63, 195.02, 1014.25, 1916.10),
        "split_row_unit":3,
        "split_col_unit":10
    }

csv_data_list = list()


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


def pdf_2_img():
    '''
    pdf filename & image resolution
    '''
    return convert_from_path(conf["pdf_name"], size=conf["pdf_img_size"], first_page=conf["pdf_page_start"], last_page=conf["pdf_page_end"])

def crop_into_row_subimg(img, page_no, split_unit=3):
    img_w, img_h = img.size
    print(img_w,img_h)
    x1,y1 = 0,0
    for row_no in range(split_unit):
        x2, y2 = (img_w/split_unit)*(row_no+1),img_h
        cr_img = crop_image(img=img, axis=(x1,y1,x2,y2))
        # data = ocr(img=cr_img, locale="mar")
        # data2 = ocr(img=cr_img, locale="eng")

        # print(data)
        # print(data2)
        # cr_img.save(f"./tmp/{page_no}_{row_no}.png")
        
        crop_into_col_subimg(cr_img, page_no, row_no, split_unit=10)
        x1,y1 = x2, 0 #shift crop slot
        del(cr_img)

def crop_into_col_subimg(img, page_no, row_no, split_unit=10):
    img_w, img_h = img.size
    # print(img_w,img_h)
    x1,y1 = 0,0
    for col_no in range(split_unit):
        x2, y2 = img_w, (img_h/split_unit)*(col_no+1)
        cr_img = crop_image(img=img, axis=(x1,y1,x2,y2))
        clrs = cr_img.getcolors()
        # if isinstance(clrs,list) and 
        data = ocr(img=cr_img, locale="mar")
        data2 = ocr(img=cr_img, locale="eng")

        # check if image ocr data is not blank
        if len(data) > 1 and data[0] != '\x0c':
            tmp = list()
            
            # filter name
            if "मतदाराचे पूर्ण." in data[1]:
                tmp.append(data[1].replace("मतदाराचे पूर्ण.",""))
            elif "मतदाराचे पूर्ण-" in data[1]:
                tmp.append(data[1].replace("मतदाराचे पूर्ण-",""))
            else:
                tmp.append(data[1].replace("मतदाराचे पूर्ण",""))

            # get number data
            t = data2[0].split(" ")
            if len(t) == 2:
                t.insert(1," ")
            tmp.extend(t)
            csv_data_list.append(tmp)
            del(t)
            del(tmp)
        cr_img.save(f"./tmp/{page_no}_{row_no}_{col_no}.png")
        x1,y1 = 0, y2 #shift crop slot

def data_into_csv():
    import csv
    with open('./tmp/election_yadi.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(csv_data_list)

def main():
    #convert pdf pages into images
    images = pdf_2_img()
    
    # iterate over image list and process
    for page_no, img in enumerate(images):
        cr_img = crop_image(img, axis=conf["crop_img_axis"])
        crop_into_row_subimg(cr_img, page_no)
        # cr.save(f"./tmp/{i}.png")
        del(cr_img)
    data_into_csv()

if __name__ == "__main__":
    if not os.path.isdir("./tmp"):
            os.makedirs("./tmp")
    main()
