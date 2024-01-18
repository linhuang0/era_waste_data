from django.contrib import admin

from .models import Customer, CustomerSite, MarketServicePrice, Service, TransactionDetail, ServiceType, Supplier, SupplierOutlet, WasteStream,EraStandardTerm
from django.utils.html import format_html

class CustomerSiteAdmin(admin.ModelAdmin):
    list_display = ('site_id', 'customer', 'site_name', 'site_address', 'suburb_or_town', 'city', 'state', 'site_number')
    
    # 如果您想添加过滤器，可以使用以下代码
    list_filter = ('city', 'state')

    # 如果您想在管理界面添加搜索功能，可以使用以下代码
    search_fields = ('site_name', 'site_number', 'customer__customer_name')

    # 如果您还希望添加按日期的过滤器，可以使用以下代码（前提是您的模型中有日期字段）
    # date_hierarchy = 'date_field_name'

admin.site.register(CustomerSite, CustomerSiteAdmin)

# Customer
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_id', 'customer_name', 'customer_number', 'parent_company_name', 'last_known_cx_id')
admin.site.register(Customer, CustomerAdmin)


# MarketServicePrice
class MarketServicePriceAdmin(admin.ModelAdmin):
    list_display = ('price_id', 'outlet', 'site', 'stream_id', 'service', 'type', 'qty_scheduled', 'frequency', 'unit_price', 'start_date', 'end_date', 'stage', 'route_schedule', 'days')
admin.site.register(MarketServicePrice, MarketServicePriceAdmin)

# Service
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('service_id', 'service_name', 'container_type', 'size')
admin.site.register(Service, ServiceAdmin)

# ServiceType
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ('type_id', 'fee_type', 'unit_of_measure', 'weight')
admin.site.register(ServiceType, ServiceTypeAdmin)

# Supplier
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('supplier_id', 'supplier_name', 'supplier_number', 'parent_company_name', 'last_known_sup_id')
admin.site.register(Supplier, SupplierAdmin)

# SupplierOutlet
class SupplierOutletAdmin(admin.ModelAdmin):
    list_display = ('outlet_id', 'supplier', 'outlet_name', 'outlet_address', 'suburb_or_town', 'city', 'state', 'outlet_number')
admin.site.register(SupplierOutlet, SupplierOutletAdmin)

# WasteStream
class WasteStreamAdmin(admin.ModelAdmin):
    list_display = ('stream_id', 'stream_group', 'stream_name', 'sub_stream_name', 'sub_stream_code')
admin.site.register(WasteStream, WasteStreamAdmin)

# TransactionDetail
class TransactionDetailAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'invoice_number', 'invoice_date', 'transaction_date', 'quantity', 'weight', 'volume', 'unit_amount', 'transaction_ref', 'transaction_number', 'stream', 'service', 'type', 'outlet', 'site')
admin.site.register(TransactionDetail, TransactionDetailAdmin)

# EraStandardTerm
class EraStandardTermAdmin(admin.ModelAdmin):
    list_display = ('era_desc', 'stream_name', 'container', 'sizem3', 'uom', 'activity')
admin.site.register(EraStandardTerm, EraStandardTermAdmin)