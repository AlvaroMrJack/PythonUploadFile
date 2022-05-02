import os
from flask import Flask, jsonify, flash, request, redirect, url_for
from flask_restful import Api, Resource
from werkzeug.utils import secure_filename
import string
import random

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(SITE_ROOT, "uploads")
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

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

    def GenerateResponse(self, responseType, responseData = [], message = None):
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
            return self.GenerateResponse(0, [], 'No file part')
        file = request.files['file']

        if file.filename == '':
            return self.GenerateResponse(0, [], 'No selected file')

        if file and AllowedFile(file.filename):
            # filename = secure_filename(file.filename)
            filename_generated = self.GenerateNewFilename(10, file.filename.rsplit('.', 1)[1].lower())

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename_generated))
            return self.GenerateResponse(1, [], 'File uploaded successfully')
        else:
            return self.GenerateResponse(0, [], 'Extension not supported')

api.add_resource(ImageTextRecognition, "/post_image")

if __name__=="__main__":
    StartValidation()
    app.run(debug=True)