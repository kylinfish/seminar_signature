from django import forms


class uploadForm(forms.Form):
	upfile = forms.FileField()
