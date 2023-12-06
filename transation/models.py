from django.db import models


class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    customer_name = models.CharField(max_length=255)
    customer_number = models.IntegerField(null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'customer'


class CustomerSite(models.Model):
    site_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, models.DO_NOTHING)
    site_name = models.CharField(max_length=255)
    site_address = models.CharField(max_length=255)
    suburb_or_town = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    site_number = models.IntegerField(null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'customer_site'

class Supplier(models.Model):
    supplier_id = models.AutoField(primary_key=True)
    supplier_name = models.CharField(max_length=1000)
    supplier_number = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'supplier'


class SupplierOutlet(models.Model):
    outlet_id = models.AutoField(primary_key=True)
    supplier = models.ForeignKey(Supplier, models.DO_NOTHING)
    outlet_name = models.CharField(max_length=255)
    outlet_address = models.CharField(max_length=255)
    suburb_or_town = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    outlet_number = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'supplier_outlet'

class WasteStream(models.Model):
    stream_id = models.AutoField(primary_key=True)
    stream_group = models.CharField(max_length=255)
    stream_name = models.CharField(max_length=255)
    sub_stream_name = models.CharField(max_length=255)
    sub_stream_code = models.CharField(max_length=255)

    class Meta:
        managed = True
        db_table = 'waste_stream'



class QuoteService(models.Model):
    quote_id = models.AutoField(primary_key=True)
    outlet = models.ForeignKey('SupplierOutlet', models.DO_NOTHING)
    service = models.ForeignKey('Service', models.DO_NOTHING)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        managed = True
        db_table = 'quote_service'


class Service(models.Model):
    service_id = models.AutoField(primary_key=True)
    sub_steam = models.ForeignKey('WasteStream', models.DO_NOTHING)
    service_name = models.CharField(max_length=255)
    container_type = models.CharField(max_length=255)
    uom = models.CharField(max_length=255)
    weight = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        managed = True
        db_table = 'service'


class SubService(models.Model):
    sub_service_id = models.AutoField(primary_key=True)
    service = models.ForeignKey('Service', models.DO_NOTHING)
    fee_type = models.CharField(max_length=255)
    charged_by = models.CharField(max_length=255)

    class Meta:
        managed = True
        db_table = 'sub_service'


class Task(models.Model):
    task_id = models.AutoField(primary_key=True)
    site = models.ForeignKey(CustomerSite, models.DO_NOTHING)
    service = models.ForeignKey(Service, models.DO_NOTHING)
    qty_scheduled = models.IntegerField()
    frequency = models.CharField(max_length=255)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    outlet = models.ForeignKey(SupplierOutlet, models.DO_NOTHING)

    class Meta:
        managed = True
        db_table = 'task'

class Invoice(models.Model):
    invoice_id = models.AutoField(primary_key=True)
    invoice_number = models.IntegerField()
    site = models.ForeignKey(CustomerSite, models.DO_NOTHING)
    outlet = models.ForeignKey(SupplierOutlet, models.DO_NOTHING)
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)
    invoice_date = models.DateField()

    class Meta:
        managed = True
        db_table = 'invoice'


class Transation(models.Model):
    transation_id = models.AutoField(primary_key=True)
    task = models.ForeignKey(Task, models.DO_NOTHING)
    invoice = models.ForeignKey(Invoice, models.DO_NOTHING)
    transation_date = models.DateField()
    quantity = models.DecimalField(max_digits=8, decimal_places=2)
    weight = models.DecimalField(max_digits=8, decimal_places=2)
    volume = models.DecimalField(max_digits=8, decimal_places=2)
    amout = models.DecimalField(max_digits=8, decimal_places=2)
    transation_ref = models.CharField(max_length=255)
    transation_number = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'transation'



