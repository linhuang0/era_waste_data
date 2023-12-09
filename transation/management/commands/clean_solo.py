import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings
from transation.models import Customer,Supplier,CustomerSite,WasteStream,Service,SubService,MarketServicePrice,Invoice,Transation

class Command(BaseCommand):
    help = 'Function to read customer data from an Excel file and add to the database.'

    def handle(self, *args, **options):
        try:
            #Add ERA Term data
            mapping_file_path = os.path.join(settings.MEDIA_ROOT, 'Mapping Table.xlsx')
            mappingdf=pd.read_excel(mapping_file_path)  
            for index, row in mappingdf.iterrows():
                wasteStream, created = WasteStream.objects.get_or_create(
                        stream_name=str(row['Stream']),
                    )
                service, created = Service.objects.get_or_create(
                        service_name=str(row['Description']),
                        sub_stream=wasteStream,
                        container_type=str(row['Container']),
                        size=str(row['SizeM3']),
                    )
                subService, created = SubService.objects.get_or_create(
                        service_type=str(row['Activity']),
                        service=service,
                        unit_of_measure=str(row['UoM']),
                    )
        
            # Construct the path to the Excel file in the media folder
            clean_file_path = os.path.join(settings.MEDIA_ROOT, '07_Solo_seagulls october 2022 - december 2022.xlsx')
            # Use pandas to read Excel data
            df = pd.read_excel(clean_file_path)
            # Use pandas to read Excel data from all sheets
            xls = pd.ExcelFile(clean_file_path)
            all_sheets_data = pd.read_excel(xls, sheet_name=None)
        
            #Get or create customer and supplier
            customer, created = Customer.objects.get_or_create(
                    customer_name='SEAGULLS',
                    #customer_number=row['Customer Number']
                )
            supplier, created = Supplier.objects.get_or_create(
                    supplier_name='SOLO',
                )

            # Loop through all sheets
            for sheet_name, df in all_sheets_data.items():
                #self.stdout.write(self.style.SUCCESS(f'Sheet name: {sheet_name}'))

                # Iterate through each row
                for index, row in df.iterrows():
                    # clean cx site info. Use "Task Site" as site_name,Use get_or_create to avoid duplicates
                    #self.stdout.write(row['Task Site'])
                    customerSite, created = CustomerSite.objects.get_or_create(
                        site_name=str(row['Task Site']),
                        customer=customer,
                    )

                    # clean waste info. Use "Stream" as waste_stream.stream_name
                    #self.stdout.write(row['Stream'])
                    wasteStream, created = WasteStream.objects.get_or_create(
                        stream_name=str(row['Stream']),
                    )

                    # clean service and subservice data. Use mapping table to match service and subservice 
                    #self.stdout.write(row['Desc'])

            self.stdout.write(self.style.SUCCESS('Data imported successfully'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
