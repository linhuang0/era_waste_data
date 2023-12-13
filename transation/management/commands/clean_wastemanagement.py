import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings
from fuzzywuzzy import fuzz, process
from django.db import transaction



from transation.models import Customer, CustomerSite, Supplier, SupplierOutlet, WasteStream, Service, SubService, Transation

class Command(BaseCommand):
    help = 'Load WasteManagement data from an Excel file into the MySQL database.'

    def handle(self, *args, **options):
        # Path to the Excel file within the media root
        excel_file_path = os.path.join(settings.MEDIA_ROOT, '04_WasteManagement_230804_Customer Sales Transactions by Service Date 2023.xlsx')
        df = pd.read_excel(excel_file_path)

        # Start a new transaction
        with transaction.atomic():
            # Assuming 'WasteManagement' is the name of your WasteManagement supplier in the db
            supplier, _ = Supplier.objects.get_or_create(supplier_name='WasteManagement')

            # Iterate over each row of the DataFrame
            for index, row in df.iterrows():
                # Get or create the Customer and CustomerSite instances
                customer, _ = Customer.objects.get_or_create(
                    customer_number=row['Customer Number'],
                    defaults={'customer_name': row['Customer Name']}
                )

                customer_site, _ = CustomerSite.objects.get_or_create(
                    customer=customer,
                    site_name=row['Site Name'],
                    defaults={
                        'site_address': row['Site Address'],
                        'suburb_or_town': row['Site Suburb'],
                    }
                )

                # Get or create the SupplierOutlet instance
                outlet, _ = SupplierOutlet.objects.get_or_create(
                    supplier=supplier,
                    outlet_name=row['Service Company Outlet']
                )

                # Get or create WasteStream and Service instances
                waste_stream, _ = WasteStream.objects.get_or_create(
                    stream_name=row['Material Profile'],
                    defaults={'stream_group': row['Landfill Waste/ Recycled Waste']}
                )

                service, _ = Service.objects.get_or_create(
                    service_name=row['Bin Type'],
                    defaults={'sub_stream': waste_stream}
                )

                # Get or create the SubService instance
                sub_service, _ = SubService.objects.get_or_create(
                    service_type=row['Action'],
                    defaults={'service': service}
                )

                # Create or update the Transation instance
                transation, _ = Transation.objects.update_or_create(
                    invoice_number=row['Invoice Number'],
                    defaults={
                        'invoice_date': pd.to_datetime(row['Invoice Date']),
                        'transation_date': pd.to_datetime(row['Service Date']),
                        'site': customer_site,
                        'outlet': outlet,
                        'volume': row['Volume (m³)'],
                        'weight': row['Reported Weight (t)'],
                        'sub_service': sub_service,
                        'transation_number': row['Ticket Number'],
                        # Include additional fields as necessary
                    }
                )

            self.stdout.write(self.style.SUCCESS('Successfully imported WasteManagement data.'))




















