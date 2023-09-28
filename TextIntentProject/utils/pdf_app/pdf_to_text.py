import fitz
import easyocr
import os
import time
import cv2
from skimage.filters import threshold_local
import cv2
import numpy as np
import re

""" You need to install following libraries:- 
    1) pip install easyocr
    2) pip install PyMuPDF
    """

reader = easyocr.Reader(['en'], gpu=True, quantize=True)


def preprocess_image(image):
   
    smoothed_image = cv2.GaussianBlur(image, (3,3), 0)

    gray = cv2.cvtColor(smoothed_image, cv2.COLOR_BGR2GRAY)
    ret, th = cv2.threshold(gray,
        170,  # threshold value (ignored when using cv2.THRESH_OTSU)
        255,  # maximum value assigned to pixel values exceeding the threshold
        cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = np.ones((1,1), np.uint8)

    # Now we erode
    erosion = cv2.erode(th, kernel, iterations = 1)
    # img_scaled4 = cv2.resize(erosion, (500, 300), interpolation = cv2.INTER_AREA)
    
    return erosion
    
def returnPDFData(file_path:str, num_pages_to_read:int=1,time=time, reader= reader):
    """

    Args:
        file_path : Provide a pdf file path_

    Raises:
        Exception1: If file not found then raises exception.
        Exception2: If the number of pages provided as arguments is more than total pages
                   in pdf it will raise exception

    Returns:
        List : Returns the list with text in particular page.
    """
    # start = time.time()
    try:
        doc = fitz.open(file_path)
        zoom = 3
        mat = fitz.Matrix(zoom, zoom)
    except fitz.fitz.FileNotFoundError as e:
        raise Exception("File Not Found.")
 
    # count = 0
    count = len(doc)
    print("count", count)
    
    
    if count == 0:
        raise Exception(f"PDF has no data in it.")
    
    # Converting pdf to image
    images = []
    left_side_img = []
    right_side_img = []
    text = []
    images_dict = {}
    left_side_img_dict = {}
    right_side_img_dict = {}
    
    for i in range(count):
        val = f"image_{i+1}.png"
        page = doc.load_page(i)
        
        # Determine the width and height of the page
        page_width, page_height = page.rect.width, page.rect.height
        print(f"width {page_width} height {page_height}")
        
        if page_height >= 700:
            
        # Define a rectangle that covers the upper half of the page
            upper_half_rect = fitz.Rect(0, 0, page_width, page_height/2)
            left_half_rect = fitz.Rect(50, 100, page_width / 2, page_height / 3)
            right_half_rect = fitz.Rect(page_width / 2, 0, page_width, page_height / 4)
        else:
            upper_half_rect = fitz.Rect(0, 0, page_width, page_height/2)
            left_half_rect = fitz.Rect(50, 100, page_width / 2, page_height / 2)
            right_half_rect = fitz.Rect(page_width / 2, 0, page_width, page_height / 2)

        ## Get the pixmap of the pdf page
        pix = page.get_pixmap(matrix=mat, clip=upper_half_rect)
        left_half_pixmap = page.get_pixmap(matrix=mat, clip=left_half_rect)
        right_half_pixmap = page.get_pixmap(matrix=mat, clip=right_half_rect)
        
        
        
        image_data = np.frombuffer(pix.samples, dtype=np.uint8)
        height, width, channels = pix.h, pix.w, 3  
        image_data = image_data.reshape(height, width, channels)
        images_dict[f"{val}"] = image_data
        
        image_data = np.frombuffer(left_half_pixmap.samples, dtype=np.uint8)
        height, width, channels = left_half_pixmap.h, left_half_pixmap.w, 3  
        image_data = image_data.reshape(height, width, channels)
        left_side_img_dict[f"left_{val}"] = image_data
        
        image_data = np.frombuffer(right_half_pixmap.samples, dtype=np.uint8)
        height, width, channels = right_half_pixmap.h, right_half_pixmap.w, 3  
        image_data = image_data.reshape(height, width, channels) 
        right_side_img_dict[f"right_{val}"] = image_data
        
        
        
        
        ## SAVING image name in the dict which can be used further for reading an image.
        images.append(f"images/{val}")
        left_side_img.append(f"images/left_{val}")
        right_side_img.append(f"images/right_{val}")

        ## SAVING images in the images folder
        # left_half_pixmap.save(f"images/left_{val}")
        # right_half_pixmap.save(f"images/right_{val}")
        # pix.save(f"images/{val}")
    doc.close()
    
        # print("IF HEIGHT", page_height)
        ## READING FROM THE DICT  
    for image_name in images_dict:
        
        ## Condition to check if the pdf is of full page then preprocessing doesn't required
        if page_height >= 700:
            right_side_image = right_side_img_dict[f"right_{image_name}"]
            left_side_image = left_side_img_dict[f"left_{image_name}"]
        else:
            # right_side_image = preprocess_image(right_side_img_dict[f"right_{image_name}"])
            right_side_image = right_side_img_dict[f"right_{image_name}"]
            left_side_image = preprocess_image(left_side_img_dict[f"left_{image_name}"])
        
        right_result = reader.readtext(right_side_image, batch_size=32, decoder="greedy", beamWidth=10, paragraph=False, width_ths=3, add_margin=0)
        result_r = []
        for bbox, text_line, prob in right_result:
                result_r.append(text_line.strip())
        print("RESULT of IMAGE:- ", result_r)
        
        date_pattern = r'\d{2}-\d{2}-\d{4}'
        
        # if any("Date of this notice" in item for item in result_r):
        if re.search(date_pattern, result_r[0]):

            left_result = reader.readtext(left_side_image, batch_size=32, decoder="greedy", beamWidth=10, paragraph=False, width_ths=3,add_margin=0)
            result_ = []
            for bbox, text_line, prob in left_result:
                result_.append(" ".join(text_line.strip().split()))
            print("LEFT RESULT", result_)
            text.append(result_)
                

            text.append(result_r)
            
            break
    
        
    # end = time.time()
    
    # time = f"{(end-start) * 10**3} ms"
    return text

def is_street_address(text):
# Regular expression pattern to check if the text starts with a number
    starts_with_number_pattern = r'^\d'

    return bool(re.match(starts_with_number_pattern, text))

def extract_information(text):
    # Initialize variables to store extracted information
    date_of_notice = ''
    emp_identification_num = ''
    number_of_notice = ''
    company_title = text[0][0]
    company_subtitle = ''
    full_address = ''
    
    city = ''
    state = ''
    zip_code = ''
    
    # Extracting information from the text
    date_match = re.search(r'(\d{2}-\d{2}-\d{4})', text[1][0])
    if date_match:
        date_of_notice = date_match.group(1)
    
    ein_match = re.search(r'(\d{2}-\d{7})', text[1][2])
    if ein_match:
        # print("ein_match")
        emp_identification_num = ein_match.group(1)
    
    number_of_notice = text[1][4].split(":")[1].strip()

    if is_street_address(text[0][1]):
        # company_subtitle = ""
        street_address = text[0][1]
        address_part = text[0][2]
    else:
        company_subtitle = text[0][1]
        street_address = text[0][2]
        address_part = text[0][3]
    
    add_split = address_part.split(",")
    if len(add_split) >= 2:
        city = add_split[0].strip()
        state = add_split[1][:3].strip()
        zip_code = add_split[1][-5:]
    
    full_address = f"{street_address}, {city}, {state} {zip_code}"

    # Construct and return the result dictionary
    result = {
        'date_of_notice': date_of_notice,
        'emp_identification_number': emp_identification_num,
        'number_of_notice': number_of_notice,
        'company_title': company_title,
        'company_subtitle': company_subtitle,
        'full_address': full_address,
        'street_address': street_address,
        'city': city,
        'state': state,
        'zip': zip_code,
    }

    return result

def returnPdfOCRData(filepath):
    text = returnPDFData(filepath)
    # print(text)
    text_ = extract_information(text)
    if text_:
        return text_
    else:
        return None


