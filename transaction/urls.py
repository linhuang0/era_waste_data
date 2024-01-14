from django.urls import path
import transaction.views


urlpatterns = [
    path('contracts', transaction.views.upload_contract, name='upload_contract')
]

