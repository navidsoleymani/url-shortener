from sqladmin import ModelView

from .models import URLVisit, URL


# Admin view for the URL model
class URLAdmin(ModelView, model=URL):
    # Columns to display in the admin list view
    column_list = [URL.id, URL.original_url, URL.short_code]

    # Fields to include in the admin form
    form_columns = [URL.original_url, URL.short_code]


# Admin view for the URLVisit model
class URLVisitAdmin(ModelView, model=URLVisit):
    # Columns to display in the admin list view
    column_list = [URLVisit.id, URLVisit.url, URLVisit.timestamp]
