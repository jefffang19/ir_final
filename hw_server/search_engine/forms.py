from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Column

class WordForm(forms.Form):
    keywords = forms.CharField(label='')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Search', css_class='btn btn-outline-primary'))

class UploadFileForm(forms.Form):
    # tag = forms.CharField(label = 'Tag')
    mode = forms.CharField(label = 'Mode')
    file = forms.FileField(label = 'File')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit', css_class='btn btn-primary'))
