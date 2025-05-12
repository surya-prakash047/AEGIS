import easyocr
from ocr_tamil.ocr import OCR
import matplotlib.pyplot as plt
import cv2
import numpy as np
from PIL import ImageDraw,ImageFont,Image

# add image path
class vision2txt:
    def __init__(self):
    
        self.ocr = OCR(detect=True,details=2)
    
    def extract(self,image):
        text = self.ocr.predict(image)
        #print(text)
        extracted_text = ''
        for t in text[0]:
            ext_txt = t[0]
            extracted_text = extracted_text + ' ' + ext_txt

        return extracted_text.strip()


