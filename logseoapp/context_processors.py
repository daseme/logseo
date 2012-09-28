from utils.view import client_select
from logseoapp.models import Client
from logseoapp.forms import ClientChoice


def client_form(request):
    form = ClientChoice(initial={'client_list': client_select(request.GET)})
    return {'form': form}


def client_name(request):
    client = Client.objects.values('name').filter(pk=client_select(request.GET))
    return {'client': client}
