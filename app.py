from flask import Flask, request, redirect, url_for, render_template, send_from_directory
import pytesseract
from PIL import Image
import os
import cv2

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def ocr_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return "Error: Unable to load image"

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    filename = "{}.png".format("temp")
    cv2.imwrite(filename, thresh)
    pil_image = Image.open(filename)
    text = pytesseract.image_to_string(pil_image)
    os.remove(filename)
    return text

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            text = ocr_image(filepath)
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], filename.rsplit('.', 1)[0] + '.txt')
            with open(output_path, 'w') as f:
                f.write(text)
            return send_from_directory(app.config['UPLOAD_FOLDER'], filename.rsplit('.', 1)[0] + '.txt')
    return render_template('index.html')

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)