from django import forms

TITLE_CHOICES = (
    ('unit', 'unit'),
    ('student', 'student'),
)



class uploadForm(forms.Form):
	model_type = forms.CharField(max_length=10,widget=forms.Select(choices=TITLE_CHOICES))
	upfile = forms.FileField()
