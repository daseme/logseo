from django import forms
from django.forms import ModelForm
from logseoapp.models import Client, WatchListKw, WatchListKwNote
#from django.contrib.auth.models import User
from widgets import SelectWidgetBootstrap
from django.forms.models import inlineformset_factory


class ClientChoice(forms.Form):
    client_list = forms.ModelChoiceField(label=(''), queryset=Client.objects.all(),
                                                     required=False, widget=SelectWidgetBootstrap())

    class Meta:
        model = Client


class WatchListKwForm(ModelForm):

    class Meta:
        model = WatchListKw


class WatchListKwNoteForm(ModelForm):

    class Meta:
        model = WatchListKwNote


KwNoteFormSet = inlineformset_factory(WatchListKw,
                                      WatchListKwNote,
                                      can_delete=False,
                                      extra=1)
