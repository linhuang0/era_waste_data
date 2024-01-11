# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    customer_name = models.CharField(max_length=255)
    customer_number = models.CharField(max_length=255, blank=True, null=True)
    parent_company_name = models.CharField(max_length=255, blank=True, null=True)
    last_known_cx_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'customer'


class CustomerSite(models.Model):
    site_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, models.DO_NOTHING)
    site_name = models.CharField(max_length=255)
    site_address = models.CharField(max_length=255, blank=True, null=True)
    suburb_or_town = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    site_number = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'customer_site'


class EraStandardTerm(models.Model):
    era_desc = models.CharField(max_length=255)
    stream_name = models.CharField(max_length=255, blank=True, null=True)
    container = models.CharField(max_length=255, blank=True, null=True)
    sizem3 = models.CharField(max_length=255, blank=True, null=True)
    uom = models.CharField(max_length=255, blank=True, null=True)
    activity = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'era_standard_term'
        unique_together = (('era_desc', 'stream_name', 'container', 'uom'),)


class MarketServicePrice(models.Model):
    price_id = models.AutoField(primary_key=True)
    outlet = models.ForeignKey('SupplierOutlet', models.DO_NOTHING)
    site = models.ForeignKey(CustomerSite, models.DO_NOTHING, blank=True, null=True)
    stream_id = models.IntegerField(blank=True, null=True)
    service = models.ForeignKey('Service', models.DO_NOTHING)
    type = models.ForeignKey('ServiceType', models.DO_NOTHING, blank=True, null=True)
    qty_scheduled = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    frequency = models.CharField(max_length=255, blank=True, null=True)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    stage = models.CharField(max_length=255, blank=True, null=True)
    route_schedule = models.CharField(max_length=255, blank=True, null=True)
    days = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'market_service_price'


class Service(models.Model):
    service_id = models.AutoField(primary_key=True)
    service_name = models.CharField(max_length=255)
    container_type = models.CharField(max_length=255, blank=True, null=True)
    size = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'service'


class ServiceType(models.Model):
    type_id = models.AutoField(primary_key=True)
    fee_type = models.CharField(max_length=255, blank=True, null=True)
    unit_of_measure = models.CharField(max_length=255, blank=True, null=True)
    weight = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'service_type'


class Supplier(models.Model):
    supplier_id = models.AutoField(primary_key=True)
    supplier_name = models.CharField(max_length=255)
    supplier_number = models.CharField(max_length=255, blank=True, null=True)
    parent_company_name = models.CharField(max_length=255, blank=True, null=True)
    last_known_sup_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'supplier'


class SupplierOutlet(models.Model):
    outlet_id = models.AutoField(primary_key=True)
    supplier = models.ForeignKey(Supplier, models.DO_NOTHING)
    outlet_name = models.CharField(max_length=255)
    outlet_address = models.CharField(max_length=255, blank=True, null=True)
    suburb_or_town = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    outlet_number = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'supplier_outlet'


class TransactionDetail(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    invoice_number = models.CharField(max_length=255, blank=True, null=True)
    invoice_date = models.DateField(blank=True, null=True)
    transaction_date = models.DateField()
    quantity = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    weight = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    volume = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    unit_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    transaction_ref = models.CharField(max_length=255, blank=True, null=True)
    transaction_number = models.CharField(max_length=255, blank=True, null=True)
    stream = models.ForeignKey('WasteStream', models.DO_NOTHING)
    service = models.ForeignKey(Service, models.DO_NOTHING)
    type = models.ForeignKey(ServiceType, models.DO_NOTHING, blank=True, null=True)
    outlet = models.ForeignKey(SupplierOutlet, models.DO_NOTHING)
    site = models.ForeignKey(CustomerSite, models.DO_NOTHING)

    class Meta:
        managed = True
        db_table = 'transaction_detail'


class WasteStream(models.Model):
    stream_id = models.AutoField(primary_key=True)
    stream_group = models.CharField(max_length=255, blank=True, null=True)
    stream_name = models.CharField(max_length=255)
    sub_stream_name = models.CharField(max_length=255, blank=True, null=True)
    sub_stream_code = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'waste_stream'
