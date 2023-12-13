import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings
from fuzzywuzzy import process

from transaction.models import Customer,Supplier,CustomerSite,SupplierOutlet,WasteStream,Service,SubService,MarketServicePrice,Transaction,EraStandardTerm

class Command(BaseCommand):
    help = 'Function to read customer data from an Excel file and add to the database.'

    def handle(self, *args, **options):
        try:

            # Load wasteStream, service, and subService data from the database
            waste_stream_df = pd.DataFrame(list(WasteStream.objects.values('stream_name')))
            service_df = pd.DataFrame(list(Service.objects.values('service_name', 'container_type', 'size')))
            sub_service_df = pd.DataFrame(list(SubService.objects.values('service_type', 'unit_of_measure')))

            # Read supplier data
            #supplier_file_path = os.path.join(settings.MEDIA_ROOT, '01_Cleanaway_Charles Sturt University Waste Report August 2023.xlsb')
            supplier_file_path = os.path.join(settings.MEDIA_ROOT, '02_Cleanaway_FY 23 Rockhampton Grammer school Report Jan 2023.xlsm')
            
            # Use pandas to read Excel data
            df = pd.read_excel(supplier_file_path)
            # Use pandas to read Excel data from all sheets
            xls = pd.ExcelFile(supplier_file_path)
            sheets_data = pd.read_excel(xls, sheet_name='Transaction Data', skiprows=[0, 1], engine='openpyxl')
        
            #Get or create customer and supplier
            customer, created = Customer.objects.get_or_create(
                    customer_name='Rockhampton Grammer School',
                    #customer_number=row['Customer Number']
                )
            supplier, created = Supplier.objects.get_or_create(
                    supplier_name='Cleanaway',
                )

            
            for index, row in sheets_data.iterrows():
                #print(f'{sheets_data}')
                # Clean customer site info. Use "Task Site" as site_name, Use get_or_create to avoid duplicates
                customerSite, created = CustomerSite.objects.get_or_create(
                    site_name=str(row['Site Name']),
                    site_number=str(row['Account Number']),
                    customer=customer,
                    city=str(row['Site City']),
                )

                outlet, created = SupplierOutlet.objects.get_or_create(
                    outlet_name='Cleanaway',
                    supplier=supplier,
                )

                # Clean waste, service, and subService data.
                #print(f"Desc: {row['Description']}")
                #print(f"Desc: {waste_stream_df}")
                best_match_row = self.find_best_match(row['Description'],row['Waste Category'],row['Volume (m3)'], waste_stream_df, service_df, sub_service_df)
                #print(f"Desc: {best_match_row}")

                if best_match_row is not None:
                    wasteStream, created = WasteStream.objects.get_or_create(
                        stream_name=str(best_match_row['stream_name']),
                    )
                    service, created = Service.objects.get_or_create(
                        service_name=str(best_match_row['service_name']),
                        sub_stream=wasteStream,
                        container_type=str(best_match_row['container_type']),
                        size=str(best_match_row['size']),
                    )
                    # Check if there are multiple SubService matches and handle accordingly
                    sub_services = SubService.objects.filter(
                        service=service,
                        service_type=str(best_match_row['service_type']),
                        unit_of_measure=str(best_match_row['unit_of_measure'])
                    )
                    
                    if sub_services.exists():
                        subService = sub_services.first()  # Choose the first match or implement other logic
                    else:
                        subService = SubService.objects.create(
                            service=service,
                            service_type=str(best_match_row['service_type']),
                            unit_of_measure=str(best_match_row['unit_of_measure'])
                        )

                    transaction, created = Transaction.objects.get_or_create(
                        transation_date=row['Transaction Date'],
                        quantity=float(row['No. Units Serviced']),
                        unit_amount=float(row['Unit Amount']),
                        sub_service=subService,
                        site=customerSite,
                        outlet=outlet,
                        volume=float(row['Volume (m3)']),
                        weight=float(row['Weight\n(kg)']),
                    )
                else:
                    print(f"{row['Description']} / {row['Waste Stream']} not found in ERA strandard term")
                    handle_unmatched_data(row['Description'],row['Waste Stream'])

            self.stdout.write(self.style.SUCCESS('Data imported successfully'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))


    def find_best_match(self, description, waste_category, volume, waste_stream_df, service_df, sub_service_df):
        waste_category_lower = waste_category.lower()
        all_streams = list(waste_stream_df['stream_name'].apply(lambda x: x.lower()))
        match_stream, score_stream = process.extractOne(waste_category_lower, all_streams)

        if score_stream > 80:
            matched_row_stream = waste_stream_df[waste_stream_df['stream_name'].apply(lambda x: x.lower()) == match_stream].iloc[0]
        else:
            return None  # No suitable waste stream match found

        # Find best match for service based on description and volume
        desc_lower = description.lower()
        volume_str = str(volume).lower()
        all_services = list(service_df.apply(lambda x: f"{x['service_name'].lower()} {str(x['size'])}", axis=1))
        match_service, score_service = process.extractOne(f"{desc_lower} {volume_str}", all_services)

        if score_service > 80:
            service_name, service_size = match_service.rsplit(' ', 1)
            matched_row_service = service_df[(service_df['service_name'].apply(lambda x: x.lower()) == service_name) & (service_df['size'].apply(lambda x: str(x).lower()) == service_size)].iloc[0]
        else:
            return None  # No suitable service match found

        # Match for sub-service
        match_service_type, score_service_type = process.extractOne(desc_lower, list(sub_service_df['service_type'].apply(lambda x: x.lower())))
        if score_service_type > 30:
            matched_row_sub_service = sub_service_df[sub_service_df['service_type'].apply(lambda x: x.lower()) == match_service_type].iloc[0]
        else:
            return None  # No suitable sub-service match found

        #print(f"waste_category: {waste_category}, Match Stream: {match_stream}, Score Stream: {score_stream}")
        #print(f"Description: {description}, Match Service: {match_service}, Score Service: {score_service}")
        #print(f"Description: {description}, Match Service Type: {match_service_type}, Score Service Type: {score_service_type}")
        #print(f"Best match: {matched_row_stream['stream_name']}, {matched_row_service['service_name']}, {matched_row_service['container_type']}, {matched_row_service['size']}, {matched_row_sub_service['service_type']}, {matched_row_sub_service['unit_of_measure']}")


        return {
            'stream_name': matched_row_stream['stream_name'],
            'service_name': matched_row_service['service_name'],
            'container_type': matched_row_service['container_type'],
            'size': matched_row_service['size'],
            'service_type': matched_row_sub_service['service_type'],
            'unit_of_measure': matched_row_sub_service['unit_of_measure']
        }





def handle_unmatched_data(desc,waste_stream):
    # Append a new row to mappingdf
    try:
        # Create a new EraStandardTerm record for the unmatched data
        era_standard_term = EraStandardTerm.objects.get_or_create(
            era_desc=str(desc),
            stream_name=str(waste_stream),  # Set appropriate default values for other fields
            container='',
            sizem3=0.0,
            uom='',
            activity='',
        )

        print(f"Unmatched data for description '{desc}' saved to EraStandardTerm table.")

    except Exception as e:
        print(f"Error saving unmatched data to EraStandardTerm table: {str(e)}")

