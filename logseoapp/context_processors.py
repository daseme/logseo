from utils.view import client_select
from logseoapp.forms import ClientChoice


def client_form(request):
    form = ClientChoice(initial={'client_list': client_select(request.GET)})
    return {'form': form}
