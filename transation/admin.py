from django.contrib import admin

from transation.models import Customer, CustomerSite, MarketServicePrice, Service, Transation, SubService, Supplier, SupplierOutlet, WasteStream

admin.site.register(Customer)
admin.site.register(CustomerSite)
admin.site.register(MarketServicePrice)
admin.site.register(Service)
admin.site.register(SubService)
admin.site.register(Supplier)
admin.site.register(SupplierOutlet)
admin.site.register(WasteStream)
admin.site.register(Transation)


