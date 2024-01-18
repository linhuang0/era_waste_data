from django.urls import path
import transaction.views

from .views import download_errors_view  

urlpatterns = [
    path('contracts', transaction.views.upload_contract, name='upload_contract'),
    path('invoices', transaction.views.select_file, name='select_file'),
    path('invoices/save', transaction.views.save_transaction, name='save_transaction'),
    path('upload_files/', transaction.views.upload_files, name='upload_files'),
    path('download_errors/', download_errors_view, name='download_errors'),

]

