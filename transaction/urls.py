from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
import transaction.views


urlpatterns = [
    path('contracts', transaction.views.upload_contract, name='upload_contract'),
    path('transaction_detail', transaction.views.select_file, name='select_file'),
    path('transaction_detail/preview', transaction.views.preview_transaction, name='preview_transaction'),
    path('transaction_detail/reload_preview', transaction.views.reload_preview, name='reload_preview'),
    path('transaction_detail/save_transaction', transaction.views.save_transaction, name='save_transaction'),
    path('upload_files/', transaction.views.upload_files, name='upload_files'),
    path('download_errors/', transaction.views.download_errors_view, name='download_errors'),
    path('monitoring', transaction.views.monitoring, name='monitoring'),
    path('dashboard', transaction.views.dashboard, name='dashboard'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
