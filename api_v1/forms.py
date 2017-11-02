from django import forms

class UploadFileForm(forms.Form):
    upload_ref_ID = forms.CharField(max_length=50)
    file = forms.FileField()