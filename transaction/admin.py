from django.contrib import admin

from transaction.models import Customer, CustomerSite, MarketServicePrice, Service, Transaction, SubService, Supplier, SupplierOutlet, WasteStream,EraStandardTerm

admin.site.register(Customer)
admin.site.register(CustomerSite)
admin.site.register(MarketServicePrice)
admin.site.register(Service)
admin.site.register(SubService)
admin.site.register(Supplier)
admin.site.register(SupplierOutlet)
admin.site.register(WasteStream)
admin.site.register(Transaction)
admin.site.register(EraStandardTerm)


