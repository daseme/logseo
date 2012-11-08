from django import forms
from django.forms import ModelForm
from logseoapp.models import Client, WatchListKw, WatchListKwNote
#from django.contrib.auth.models import User
from widgets import SelectWidgetBootstrap
from django.forms.models import inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class ClientChoice(forms.Form):
    client_list = forms.ModelChoiceField(label=(''), queryset=Client.objects.all(),
                                                     required=False, widget=SelectWidgetBootstrap())

    class Meta:
        model = Client


class WatchListKwForm(ModelForm):

    #owner = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    #phrase = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.form_show_errors = True
        self.form_error_title = 'Errors'

        self.helper.form_tag = False
        super(WatchListKwForm, self).__init__(*args, **kwargs)

    def clean(self):
        """ This is the form's clean method, not a particular field's clean method """
        cleaned_data = super(WatchListKwForm, self).clean()

        owner = cleaned_data.get("owner")
        phrase = cleaned_data.get("phrase")

        if WatchListKw.objects.filter(owner=owner, phrase=phrase).count() > 0:
            del cleaned_data["owner"]
            del cleaned_data["phrase"]
            raise forms.ValidationError("Owner and phrase combination already exists.")

        # Always return the full collection of cleaned data.
        return cleaned_data

    class Meta:
        model = WatchListKw


class WatchListKwNoteForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.form_show_errors = True
        self.form_error_title = 'Errors'
        self.helper.form_tag = False
        super(WatchListKwNoteForm, self).__init__(*args, **kwargs)

    class Meta:
        model = WatchListKwNote


KwNoteFormSet = inlineformset_factory(WatchListKw,
                                      WatchListKwNote,
                                      form=WatchListKwForm,
                                      can_delete=False,
                                      extra=1)
