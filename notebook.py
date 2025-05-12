import marimo

__generated_with = "0.12.8"
app = marimo.App(width="medium")


@app.cell
def _(mo):
    mo.md(
        r"""
        #Text Extraction from extracted images from live feed
        ## Using Easy OCR
        """
    )
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    #import required libraries
    import easyocr
    from ocr_tamil.ocr import OCR
    import matplotlib.pyplot as plt
    import cv2
    import numpy as np
    from PIL import ImageDraw,ImageFont,Image
    return Image, ImageDraw, ImageFont, OCR, cv2, easyocr, np, plt


@app.cell
def _():
    image_path = 'C:/Users/PureVodka/Documents/Projects/npl/classifier_model/vison_part/imgs/frame_00003.jpg'
    return (image_path,)


@app.cell
def _(OCR, image_path):
    ocr = OCR(detect=True,details=2)
    text = ocr.predict(image_path)
    print(text)
    #print(" ".join(text[0][0]))
    return ocr, text


@app.cell
def _(Image, ImageDraw, ImageFont, cv2, image_path, np, text):
    def add_text(text,img,bounding_box):

        fontpath = "./vison_part/fonts/latha.ttf"    
        font = ImageFont.truetype(fontpath, 20)
        img_pil = Image.fromarray(img)
        draw = ImageDraw.Draw(img_pil)
        draw.text((int(bounding_box[0][0]), int(bounding_box[0][1] - 30)),  text, font = font, fill = (100, 255, 0, 0))
        img_pil = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGBA2RGB) 
        return img_pil

    def add_bounding_box(bounding_box,extracted_text):
        bounding_box = bounding_box.astype(np.int32) # wtf is this 
        cv2.polylines(image_rgb,[bounding_box],isClosed=True,color=(0,255,0),thickness=2)

    # showing the extracted text in bounding box
    image = cv2.imread(image_path)

    #convert image to RGB
    image_rgb = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)

    extracted_text = ''
    for t in text[0]:
        ext_txt = t[0]
        extracted_text = extracted_text + ' ' + ext_txt
        points = t[2][0]
        add_bounding_box(bounding_box=points,extracted_text=ext_txt)
        image_rgb = add_text(text=ext_txt,img=image_rgb,bounding_box=points)
    return (
        add_bounding_box,
        add_text,
        ext_txt,
        extracted_text,
        image,
        image_rgb,
        points,
        t,
    )


@app.cell
def _(plt):
    def display_img(img):
        plt.figure(figsize=(16,8))
        plt.axis('off')
        plt.imshow(img)
        plt.title('Extracted text')
        plt.show()
    return (display_img,)


@app.cell
def _(display_img, image_rgb):
    display_img(image_rgb)
    return


@app.cell
def _(extracted_text):
    # show the extracted text
    extracted_text
    return


@app.cell
def _(mo):
    mo.md(
        r"""
        #Analysing extracted text by using gemma3 locally
        ##Using ollama and langchain
        """
    )
    return


@app.cell
def _():
    from llm_part.gemma3 import LLMProcessor
    return (LLMProcessor,)


@app.cell
def _(LLMProcessor):
    model = LLMProcessor()
    return (model,)


@app.cell
def _(extracted_text, model):
    # run the model to extract data
    response = model.generate_response(input=extracted_text)
    return (response,)


@app.cell
def _(response):
    print(response)
    return


if __name__ == "__main__":
    app.run()
