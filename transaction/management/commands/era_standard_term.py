import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings
from transation.models import WasteStream, Service, SubService, EraStandardTerm

class Command(BaseCommand):
    help = 'Function to read era standard term data from an Excel file and add to the database.'

    def handle(self, *args, **options):
        try:
            mapping_file_path = os.path.join(settings.MEDIA_ROOT, 'Mapping Table.xlsx')
            mappingdf = pd.read_excel(mapping_file_path)

            for index, row in mappingdf.iterrows():
                row = row.where(pd.notna(row), None)

                era_standard_term, created = EraStandardTerm.objects.get_or_create(
                    era_desc=str(row['Description']),
                    stream_name=str(row['Stream']),
                    container=str(row['Container']),
                    sizem3=str(row['SizeM3']),
                    uom=str(row['UoM']),
                    activity=str(row['Activity']),
                )

                waste_stream, _ = WasteStream.objects.get_or_create(
                    stream_name=str(row['Stream']),
                )

                service, _ = Service.objects.get_or_create(
                    service_name=str(row['Description']),
                    sub_stream=waste_stream,
                    container_type=str(row['Container']),
                    size=str(row['SizeM3']),
                )

                _, _ = SubService.objects.get_or_create(
                    service_type=str(row['Activity']),
                    service=service,
                    unit_of_measure=str(row['UoM']),
                )

            self.stdout.write(self.style.SUCCESS('ERA Term and related data imported successfully'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
