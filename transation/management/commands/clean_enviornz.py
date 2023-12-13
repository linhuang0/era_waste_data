import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings
from transation.models import Customer,Supplier,CustomerSite,SupplierOutlet,WasteStream,Service,SubService,MarketServicePrice,Transation,EraStandardTerm

class Command(BaseCommand):
    help = 'Function to read customer data from an Excel file and add to the database.'
def handle(self, *args, **options):
        try:

           # Load wasteStream, service, and subService data from the database
            waste_stream_df = pd.DataFrame(list(WasteStream.objects.values('stream_name')))
            service_df = pd.DataFrame(list(Service.objects.values('service_name', 'container_type', 'size')))
            sub_service_df = pd.DataFrame(list(SubService.objects.values('service_type', 'unit_of_measure')))

            # Read supplier data
            supplier_file_path = os.path.join(settings.MEDIA_ROOT, '03_EnviroNZ_Transactions by Invoice Date.xlsx')
            # Use pandas to read Excel data
            df = pd.read_excel(supplier_file_path)
            # Use pandas to read Excel data from all sheets
            xls = pd.ExcelFile(supplier_file_path)
            all_sheets_data = pd.read_excel(xls, sheet_name=None)
            #Get or create customer and supplier
            customer, created = Customer.objects.get_or_create(
                    customer_name='The Interior Groups',
                    parent_company_name='The Interiors Group Limited',
                    #customer_number=row['Customer Number']
                )
            supplier, created = Supplier.objects.get_or_create(
                    supplier_name='EnviorNZ',
                )
            # Loop through all sheets
            for sheet_name, df in all_sheets_data.items():
                #self.stdout.write(self.style.SUCCESS(f'Sheet name: {sheet_name}'))
                for index, row in df.iterrows():
                    # Clean customer site info. Use "Task Site" as site_name, Use get_or_create to avoid duplicates
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

                
                
                transation, created = Transation.objects.get_or_create(
                    transation_date=row['Transaction Date'],
                    customer_site=customerSite,
                    outlet=outlet,
                    waste_stream=wasteStream,   
                    
                )

            self.stdout.write(self.style.SUCCESS('Data imported successfully'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
