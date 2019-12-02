from django import forms
from django.core.files.storage import default_storage

class ImageUploadForm(forms.Form):
    file = forms.ImageField(label='画像ファイル')

    def upload(self):
        file_name = default_storage.save(self.files['file'].name, self.files['file'])
        return default_storage.url(file_name)