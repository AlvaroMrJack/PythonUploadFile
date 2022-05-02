import os
from flask import Flask, jsonify, flash, request, redirect, url_for
from flask_restful import Api, Resource
from werkzeug.utils import secure_filename
import string
import random
import cv2
import tesserocr
from PIL import Image
from pathlib import Path

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(SITE_ROOT, "uploads")
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
IMAGE_ZOOM_SIZE = 1.5
PATH_TESSERACTOCR_TESSDATA = 'C:\\Program Files\\Tesseract-OCR\\tessdata'

app = Flask(__name__)
api = Api(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def AllowedFile(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def StartValidation():
    if os.path.isdir(app.config['UPLOAD_FOLDER']) == False:
        os.mkdir(UPLOAD_FOLDER)

class ImageTextRecognition(Resource):
    def GenerateNewFilename(self, length, extension):
        letters = string.ascii_lowercase
        randomText = ''.join(random.choice(letters) for i in range(length)) + '.' + extension
        return randomText

    def GetTextFromImage(self, filepath):
        imgUpscale = cv2.imread(filepath, 1)
        imgScaleUp = cv2.resize(imgUpscale, (0, 0), fx=IMAGE_ZOOM_SIZE, fy=IMAGE_ZOOM_SIZE)

        with tesserocr.PyTessBaseAPI(path=PATH_TESSERACTOCR_TESSDATA) as api:
            imgPil = Image.fromarray(imgScaleUp)
            api.SetImage(imgPil)
            finalText = api.GetUTF8Text()
            
        return finalText
                        
    def GenerateResponse(self, responseType, responseData = {}, message = None):
        response = {}
        data = responseData

        if responseType == 0:
            response = {
                "statusCode": 400,
                "status": "error",
                "data": data,
                "message": message if message != None else "Bad Request"
            }
        elif responseType == 1:
            response = {
                "statusCode": 200,
                "status": "success",
                "data": data,
                "message": message if message != None else "OK"
            }

        return jsonify(response)

    def post(self):
        if 'file' not in request.files:
            return self.GenerateResponse(0, {}, 'No file part')
        file = request.files['file']

        if file.filename == '':
            return self.GenerateResponse(0, {}, 'No selected file')

        if file and AllowedFile(file.filename):
            # filename = secure_filename(file.filename)
            filenameGenerated = self.GenerateNewFilename(10, file.filename.rsplit('.', 1)[1].lower())
            filepathToCreate = os.path.join(app.config['UPLOAD_FOLDER'], filenameGenerated)

            file.save(filepathToCreate)
            text = self.GetTextFromImage(filepathToCreate)

            return self.GenerateResponse(1, {'texto': text}, 'File uploaded successfully')
        else:
            return self.GenerateResponse(0, {}, 'Extension not supported')

api.add_resource(ImageTextRecognition, "/post_image")

if __name__=="__main__":
    StartValidation()
    app.run(debug=True)