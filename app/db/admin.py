from sqladmin import ModelView

from .models import URLVisit, URL


class URLAdmin(ModelView, model=URL):
    column_list = [URL.id, URL.original_url, URL.short_code]
    form_columns = [URL.original_url, URL.short_code]


class URLVisitAdmin(ModelView, model=URLVisit):
    column_list = [URLVisit.id, URLVisit.url, URLVisit.timestamp]
