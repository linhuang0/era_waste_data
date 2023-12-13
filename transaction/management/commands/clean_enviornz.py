import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings
from transaction.models import Customer,Supplier,CustomerSite,WasteStream,SupplierOutlet,Transaction

class Command(BaseCommand):
    help = 'Function to read customer data from an Excel file and add to the database.'

    def handle(self, *args, **options):
        try:
            
            file_path = os.path.join(settings.MEDIA_ROOT, '03_EnviroNZ_Transactions by Invoice Date.xlsx')
            
            df = pd.read_excel(file_path)
            
            customer, created = Customer.objects.get_or_create(
                customer_name='The Interior Groups',
                parent_company_name='The Interiors Group Limited',
                # customer_number=row['Customer Number']
            )
            supplier, created = Supplier.objects.get_or_create(
                supplier_name='EnviorNZ',
            )

            
            for index, row in df.iterrows():
                # self.stdout.write(self.style.SUCCESS(f'Sheet name: {sheet_name}'))
                
                    
                customerSite, created = CustomerSite.objects.get_or_create(
                    site_name=str(row['Known As']),
                    customer=customer,
                )

                outlet, created = SupplierOutlet.objects.get_or_create(
                    outlet_name='EnviorNZ',
                    supplier=supplier,
                )
                    
                wasteStream, created = WasteStream.objects.get_or_create(
                    stream_name=str(row['Waste Description']),
                )
                    
                    
                transaction, created = Transaction.objects.get_or_create(
                    transaction_date=row['Transaction Date'],
                    customer_site=customerSite,
                    outlet=outlet,
                    waste_stream=wasteStream,   
                )

            self.stdout.write(self.style.SUCCESS('Data imported successfully'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
