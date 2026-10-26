from django.views.generic import ListView
from .models import Download


class DownloadListView(ListView):
    model = Download
    template_name = 'downloads/download_list.html'
    context_object_name = 'downloads'
    paginate_by = 20
