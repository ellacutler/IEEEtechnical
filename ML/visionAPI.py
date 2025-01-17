import argparse
from enum import Enum
import io
import pandas as pd
from pprint import pprint
from google.cloud import vision
from google.oauth2 import service_account
from PIL import Image, ImageDraw


class FeatureType(Enum):
    PAGE = 1
    BLOCK = 2
    PARA = 3
    WORD = 4
    SYMBOL = 5

def detect_text(img):
    client = vision.ImageAnnotatorClient()

    with io.open(img, "rb") as image_file:
        content = image_file.read()
    
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations

    pprint(texts)
    df = pd.DataFrame(columns=["bounding_poly", "description"])
    for text in texts:
        temp = pd.DataFrame([[text.bounding_poly, text.description]], columns=["bounding_poly", "description"])
        df = pd.concat([df, temp],
            ignore_index=True
        )
    return df

def draw_boxes(image, bounds, color):
    """Draw a border around the image using the hints in the vector list."""
    draw = ImageDraw.Draw(image)

    for bound in bounds:
        draw.polygon(
            [
                bound.vertices[0].x,
                bound.vertices[0].y,
                bound.vertices[1].x,
                bound.vertices[1].y,
                bound.vertices[2].x,
                bound.vertices[2].y,
                bound.vertices[3].x,
                bound.vertices[3].y,
            ],
            None,
            color,
        )
    return image


def get_document_bounds(image_file, feature):
    """Returns document bounds given an image."""
    client = vision.ImageAnnotatorClient()

    bounds = []

    with io.open(image_file, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.document_text_detection(image=image)
    # f = open("response.txt", "a")
    # f.write(response)
    # f.close()
    document = response.full_text_annotation
    f = open("document.txt", "a")
    f.write(document)
    f.close()

    # Collect specified feature bounds by enumerating all document features
    for page in document.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    for symbol in word.symbols:
                        if feature == FeatureType.SYMBOL:
                            bounds.append(symbol.bounding_box)

                    if feature == FeatureType.WORD:
                        bounds.append(word.bounding_box)

                if feature == FeatureType.PARA:
                    bounds.append(paragraph.bounding_box)

            if feature == FeatureType.BLOCK:
                bounds.append(block.bounding_box)

    # The list `bounds` contains the coordinates of the bounding boxes.
    return bounds


def render_doc_text(filein, fileout):
    image = Image.open(filein)
    bounds = get_document_bounds(filein, FeatureType.BLOCK)
    draw_boxes(image, bounds, "blue")
    bounds = get_document_bounds(filein, FeatureType.PARA)
    draw_boxes(image, bounds, "red")
    bounds = get_document_bounds(filein, FeatureType.WORD)
    draw_boxes(image, bounds, "yellow")

    if fileout != 0:
        image.save(fileout)
    else:
        image.show()

#Starting with content already being the binary contents of the image file
def detect_text_in_image_binary(content):
    client = vision.ImageAnnotatorClient(credentials=service_account.Credentials.from_service_account_file("citric-trees-377221-f18b8ee77927.json"))
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    detected_text = ""
    for text in texts:
        detected_text += text.description + " "

    return detected_text.strip()
 

def detect_text_in_image(image_path):
    client = vision.ImageAnnotatorClient(credentials=service_account.Credentials.from_service_account_file("citric-trees-377221-f18b8ee77927.json"))

    with io.open(image_path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations

    detected_text = ""
    for text in texts:
        detected_text += text.description + " "

    return detected_text.strip()

if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument("detect_file", help="The image for text detection.")
    # parser.add_argument("-out_file", help="Optional output file", default=0)
    # args = parser.parse_args()

    # # render_doc_text(args.detect_file, args.out_file)
    # print(detect_text(args.detect_file))

    detected_text = detect_text_in_image("test/labelNM1.jpg")
    print(detected_text)
