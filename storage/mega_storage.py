# storage/mega_storage.py
from mega import Mega
from config import MEGA_EMAIL, MEGA_PASSWORD

class MegaStorage:
    def __init__(self):
        self.mega = Mega()
        self.mega.login(email=MEGA_EMAIL, password=MEGA_PASSWORD)

    def upload_file(self, file_path):
        file = self.mega.upload(file_path)
        return self.mega.get_upload_link(file)

    def upload_media(self, media_path):
        return self.upload_file(media_path)
