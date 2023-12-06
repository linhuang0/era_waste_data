import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings
from transation.models import Customer,Supplier,CustomerSite,WasteStream

class Command(BaseCommand):
    help = 'Function to read customer data from an Excel file and add to the database.'

    def handle(self, *args, **options):
        try:
            # Construct the path to the Excel file in the media folder
            file_path = os.path.join(settings.MEDIA_ROOT, '07_Solo_seagulls october 2022 - december 2022.xlsx')

            # Use pandas to read Excel data
            df = pd.read_excel(file_path)
            #get or create customer and supplier
            customer, created = Customer.objects.get_or_create(
                    customer_name='SEAGULLS',
                    #customer_number=row['Customer Number']
                )
            supplier, created = Supplier.objects.get_or_create(
                    supplier_name='SOLO',
                )

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


            self.stdout.write(self.style.SUCCESS('Data imported successfully'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
