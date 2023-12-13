import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings
from fuzzywuzzy import process

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
            supplier_file_path = os.path.join(settings.MEDIA_ROOT, '06_URM_Oct - Jan 2022 Service summary.xlsm')
            # Use pandas to read Excel data
            df = pd.read_excel(supplier_file_path)
            # Use pandas to read Excel data from all sheets
            xls = pd.ExcelFile(supplier_file_path)
            all_sheets_data = pd.read_excel(xls, sheet_name=None)
        
            # Set the supplier 
            supplier, created = Supplier.objects.get_or_create(
                    supplier_name = 'URM',
                )

            
            for index, row in df.iterrows():
                #Get or create customer and
                customer, created = Customer.objects.get_or_create(
                    customer_name = str(row['Customer Name'])
                )

                # Clean customer site info. Use "Address 1" as outlet_address, "City" as city
                customerSite, created = CustomerSite.objects.get_or_create(
                    outlet_address = str(row['Address 1']),
                    city = str(row['City']),
                    customer = customer,
                )

                # Clean waste, service, and subService data.
                #print(f"Desc: {row['Desc']}")
                best_match_row = self.find_best_match(row['Desc'], waste_stream_df, service_df, sub_service_df)
                #print(f"Desc: {best_match_row}")

                if best_match_row is not None:
                    wasteStream, created = WasteStream.objects.get_or_create(
                        stream_name=str(best_match_row['Waste Type']),
                    )
                    service, created = Service.objects.get_or_create(
                        service_name=str(best_match_row['service_name']),
                        sub_stream=wasteStream,
                        container_type=str(best_match_row['Container Type']),
                        size=str(best_match_row['size']),
                    )
                    subService, created = SubService.objects.get_or_create(
                        service_type=str(best_match_row['service_type']),
                        service=service,
                        unit_of_measure=str(best_match_row['unit_of_measure']),
                        charged_by=str(row['UOM']),
                    )
                    transation, created = Transation.objects.get_or_create(
                        transation_date=row['Task Date'],
                        quantity=float(row['Qty']),
                        unit_amount=float(row['Unit Price']),
                        sub_service=subService,
                        site=customerSite,
                        outlet=outlet,
                    )
                else:
                    print(f"Desc: {row['Desc']} not found in ERA strandard term")
                    handle_unmatched_data(row['Desc'])

            self.stdout.write(self.style.SUCCESS('Data imported successfully'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))


    def find_best_match(self, desc, waste_stream_df, service_df, sub_service_df):
        desc_lower = desc.lower()  # Convert the description field to lowercase

        # Get all stream_name data
        all_streams = list(waste_stream_df['stream_name'].apply(lambda x: x.lower()))

        # Use FuzzyWuzzy for fuzzy matching
        match_stream, score_stream = process.extractOne(desc_lower, all_streams)

        # Get all service_name data
        all_services = list(service_df['service_name'].apply(lambda x: x.lower()))

        # Use FuzzyWuzzy for fuzzy matching
        match_service, score_service = process.extractOne(desc_lower, all_services)

        # Get all service_type data
        all_service_types = list(sub_service_df['service_type'].apply(lambda x: x.lower()))

        # Use FuzzyWuzzy for fuzzy matching
        match_service_type, score_service_type = process.extractOne(desc_lower, all_service_types)

        # Set a threshold based on matching scores
        if score_stream > 80 and score_service > 80 and score_service_type > 30:
            # Find the matched row in waste_stream_df
            matched_row_stream = waste_stream_df[waste_stream_df['stream_name'].apply(lambda x: x.lower()) == match_stream].iloc[0]

            # Find the matched row in service_df
            matched_row_service = service_df[service_df['service_name'].apply(lambda x: x.lower()) == match_service].iloc[0]

            # Find the matched row in sub_service_df
            matched_row_sub_service = sub_service_df[sub_service_df['service_type'].apply(lambda x: x.lower()) == match_service_type].iloc[0]

            #Print Debug Information
            #print(f"Desc: {desc}, Match Stream: {match_stream}, Score Stream: {score_stream}")
            #print(f"Desc: {desc}, Match Service: {match_service}, Score Service: {score_service}")
            #print(f"Desc: {desc}, Match Service Type: {match_service_type}, Score Service Type: {score_service_type}")

            # Return information about the matched row
            return {
                'stream_name': str(matched_row_stream['stream_name']),
                'service_name': str(matched_row_service['service_name']),
                'container_type': str(matched_row_service['container_type']),
                'size': str(matched_row_service['size']),
                'service_type': str(matched_row_sub_service['service_type']),
                'unit_of_measure': str(matched_row_sub_service['unit_of_measure'])
            }

        # If the matching scores don't meet the threshold, return None
        return None

def handle_unmatched_data(desc):
    # Append a new row to mappingdf
    try:
        # Create a new EraStandardTerm record for the unmatched data
        era_standard_term = EraStandardTerm.objects.get_or_create(
            era_desc=str(desc),
            stream_name='',  # Set appropriate default values for other fields
            container='',
            sizem3=0.0,
            uom='',
            activity='',
        )

        print(f"Unmatched data for description '{desc}' saved to EraStandardTerm table.")

    except Exception as e:
        print(f"Error saving unmatched data to EraStandardTerm table: {str(e)}")