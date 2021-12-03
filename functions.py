from PyPDF2 import PdfFileMerger, PdfFileReader
import csv
from cv2 import imdecode, cvtColor, COLOR_BGR2RGB
from urllib.request import urlopen, Request
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def loadImage(url):
    # takes in an image url, returns a PIL image object
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36'}
    req = urlopen(Request(url=url, headers=headers))
    arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
    img_arr = imdecode(arr, 1)
    img_PIL = Image.fromarray(cvtColor(img_arr, COLOR_BGR2RGB))
    return img_PIL


def reformat(img):
    # img takes in a PIL image object, not a url or any other image format, so you need loadImage() first for urls
    blank_img = Image.new(
        "RGB",
        (960, 720), # (w,h)
        (255, 255, 255)
        ) 
        

    def rescale(img):
        # rescales PIL image object
        width, height = img.size
        if height >= width:  # i.e. portrait or square
            scale = 720/height
            return img.resize((round(width*scale), 720))

        else:  # i.e. landscape
            scale = 960/width
            return img.resize((960, round(height*scale)))

    def overlay(img):
        # overlay and background are both PIL image object
        ov_w, ov_h = rescale(img).size
        bg_w, bg_h = blank_img.size
        offset = ((bg_w - ov_w) // 2, (bg_h - ov_h) // 2)
        blank_img.paste(rescale(img), offset)
        final_img = blank_img
        return final_img

    return overlay(img)


def add_page_num(num, img):  # img is PIL image type, num is page number
    fnt = ImageFont.truetype('arial.ttf', 24)
    x_pos = 940 - (10 * len(str(num)))
    ImageDraw.Draw(img).text(
        (x_pos, 680),
        str(num),
        font=fnt,
        fill='black',
        stroke_width=2,
        stroke_fill='white'
    )


def image_to_pdf(url, page_num=None):
    # converts PIL image to a single pdf page, also returns the location.
    img = loadImage(url)  # PIL image type
    img = reformat(img)
    add_page_num(page_num, img)
    current_page = './output/current_page.pdf'
    img.save(current_page, 'PDF', resolution=100.0, save_all=True)
    return current_page

def csv_to_list(filename):
    file = open(filename, newline='')
    with file as f:
        reader = csv.reader(f)
        url_list = [x[0] for x in list(reader)]

    return url_list

def merge_to_pdf(url_csv):
    url_list = csv_to_list(url_csv)
    filename = url_list.pop(0)
    merger = PdfFileMerger(strict=False)
    for i, page in enumerate(url_list):
        current_page = image_to_pdf(page, page_num = i+1)
        merger.append(PdfFileReader(current_page, 'rb'))
        print(f'Page {i+1}/{len(url_list)} added.')

    output = f'./output/{filename}.pdf'
    merger.write(output)
    merger.close()
