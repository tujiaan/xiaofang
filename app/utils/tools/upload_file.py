import datetime
import os
from urllib.parse import quote

from flask import current_app
from werkzeug.utils import secure_filename

allow_ext = ['png', 'jpg', 'jpeg', 'gif']


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allow_ext


def upload_file(file):
    try:
        if file.filename == 'blob': file.filename = 'blob.png'
        if not allowed_file(file.filename):
            return None, 415
        now = datetime.datetime.now()
        date = now.strftime('%Y%m%d')
        filename = now.strftime('%H%M%S') + secure_filename(quote(file.filename))
        path = current_app.config.get('UPLOAD_FOLDER', None) + date
        url = current_app.config.get('UPLOADED_URL', None) + date + '/' + filename
        if not os.path.exists(path):
            os.makedirs(path)
        file.save(path + '/' + filename)
        print(filename)
        return url
    except:
        return None
