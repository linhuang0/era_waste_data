import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings
from transation.models import CUSTOMERS

class Command(BaseCommand):
    help = 'Function to read customer data from an Excel file and add to the database.'

    def handle(self, *args, **options):
        try:
            # Construct the path to the Excel file in the media folder
            file_path = os.path.join(settings.MEDIA_ROOT, '07_Solo_seagulls october 2022 - december 2022.xlsx')

            # Use pandas to read Excel data
            df = pd.read_excel(file_path)

            # Iterate through each row
            for index, row in df.iterrows():
                # Use "Task Site" as customer_name
                customer_name = str(row['Task Site'])
                self.stdout.write(customer_name)
                # Check if a record with the same customer_name exists in the database
                if not CUSTOMERS.objects.filter(customer_name=customer_name).exists():
                    # If not, add a new record to the database
                    CUSTOMERS.objects.create(customer_name=customer_name)

            self.stdout.write(self.style.SUCCESS('Data imported successfully'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
