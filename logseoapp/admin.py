from django.contrib import admin
from logseoapp.models import Engine, Kw, LogSeRank, Page, Client, WatchListKw, WatchListKwNote

admin.site.register(Engine)
admin.site.register(Kw)
admin.site.register(LogSeRank)
admin.site.register(Page)
admin.site.register(Client)
admin.site.register(WatchListKw)
admin.site.register(WatchListKwNote)
