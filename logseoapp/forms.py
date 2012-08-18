from django import forms
from logseoapp.models import Client
from widgets import SelectWidgetBootstrap

class ClientChoice(forms.Form):
    client_list = forms.ModelChoiceField(label=(''),queryset=Client.objects.all(),
            required=False,initial=Client.objects.get(pk="1").pk, widget=SelectWidgetBootstrap())

    class Meta:
        model = Client




