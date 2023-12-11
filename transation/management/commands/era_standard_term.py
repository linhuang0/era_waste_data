# ear_standard_term.py

import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings
from transation.models import WasteStream, Service, SubService, EraStandardTerm

class Command(BaseCommand):
    help = 'Function to read era standard term data from an Excel file and add to the database.'

    def handle(self, *args, **options):
        try:
            # Add ERA Term data
            mapping_file_path = os.path.join(settings.MEDIA_ROOT, 'Mapping Table.xlsx')
            mappingdf = pd.read_excel(mapping_file_path)

            for index, row in mappingdf.iterrows():
                # Use get_or_create to ensure uniqueness based on specified fields
                era_standard_term, created = EraStandardTerm.objects.get_or_create(
                    era_desc=str(row['Description']),
                    stream_name=str(row['Stream']),
                    container=str(row['Container']),
                    sizem3=float(row['SizeM3']),
                    uom=str(row['UoM']),
                    activity=str(row['Activity']),
                )

            self.stdout.write(self.style.SUCCESS('ERA Term data imported successfully'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
