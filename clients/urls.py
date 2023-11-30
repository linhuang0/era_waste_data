from django.conf.urls import url, include
from .views import *

urlpatterns = [
    url(r'read_excel_and_add_customers$', read_excel_and_add_customers, ),
    url(r'list_all_customers$', list_all_customers, ),
]