import os
import datetime
from flask_wtf.file import FileStorage


def upload_item_picture(path, file_data, user_id, name):
    if not (isinstance(file_data, FileStorage) and file_data):
        return None
    else:
        if not os.path.exists(path):
            print(path, "folder created")
            os.makedirs(path)
        f = file_data
        filename = "{}-{}-{}.{}".format(user_id, name, datetime.datetime.now(),
                                        f.filename.rsplit('.', 1)[1])
        f.save(os.path.join(path, filename))
        file_path = os.path.join('upload_file/image/item_main_picture', filename)
        return file_path
