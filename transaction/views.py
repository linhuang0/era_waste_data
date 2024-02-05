import pandas as pd
import os
import re
from fuzzywuzzy import process,fuzz
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.conf import settings
from django.template import loader
from django.core.exceptions import ObjectDoesNotExist
from .contracts import process_contract
from .strandard_transaction_data import process_transaction
from .models import MarketServicePrice
from transaction.models import Supplier,Customer,Supplier,CustomerSite,SupplierOutlet,WasteStream,Service,ServiceType,MarketServicePrice,TransactionDetail,EraStandardTerm


def upload_files(request):
    sheet_names = []
    success_message = None
    error_message = None
    #confirmation_required = False
    file_name = None  # Initialize file_name to None

    if request.method == 'POST' and request.FILES.get('excel_file'):
        uploaded_file = request.FILES['excel_file']

        # Save the uploaded file to the server
        fs = FileSystemStorage()
        file_name = uploaded_file.name.replace(" ", "_")

        # Check if the file with the same name already exists
        #if fs.exists(file_name):
        #    confirmation_required = True

        #   if request.POST.get('confirmation') == 'confirm':
                # If the user confirms, delete the existing file
        #        fs.delete(file_name)
        #        success_message = "Existing file deleted. Uploading new file."
        #        confirmation_required = False
        #    else:
        #        # Generate a new filename
        #       file_name = fs.get_available_name(file_name)

        # TODO FIXBUG Save the new file if confirmation is not required or user confirmed
        fs.save(file_name, uploaded_file)
        print("File saved successfully!")
        supplier_file_path = os.path.join(settings.MEDIA_ROOT, file_name)
        
        print("File exists:", os.path.exists(supplier_file_path))
        success_message = "File uploaded successfully."
        print(supplier_file_path)
  
    # Load the template manually to include the confirmation prompt
    template = loader.get_template('upload_files.html')

    return HttpResponse(template.render(
        {'sheet_names': sheet_names, 'success_message': success_message, 'error_message': error_message,},
        request
    ))


def select_file(request):
    file_names = []
    # Save the uploaded file to the server
    fs = FileSystemStorage()
    
    #file_names = fs.listdir(settings.MEDIA_ROOT)
    # Get all files in MEDIA_ROOT
    all_files = [f for f in os.listdir(settings.MEDIA_ROOT) if os.path.isfile(os.path.join(settings.MEDIA_ROOT, f))]
    
    # Sort files by creation time in reverse order
    file_names = sorted(all_files, key=lambda f: os.path.getctime(os.path.join(settings.MEDIA_ROOT, f)), reverse=True)
    #print(file_names)    

    selected_file = None
    sheet_names = []
    all_supplier_names= []
    if request.method == 'POST' and request.POST.get('selected_file'):
        selected_file = request.POST['selected_file']
        #print(selected_file)

        supplier_file_path = os.path.join(settings.MEDIA_ROOT, selected_file)
        # Use pandas to read Excel data
        df = pd.read_excel(supplier_file_path)
        # Use pandas to read Excel data from all sheets
        xls = pd.ExcelFile(supplier_file_path)

        sheet_names = xls.sheet_names
        #print(sheet_names)
        
        all_supplier= Supplier.objects.all()
        all_supplier_names = all_supplier.values_list('supplier_name', flat=True)
        #print(all_supplier_names)
        
    # Load the template manually to include the confirmation prompt
    template = loader.get_template('transaction_detail.html')

    return HttpResponse(template.render(
        {'file_names': file_names,'selected_file': selected_file, 'sheet_names': sheet_names, 'all_supplier_names': all_supplier_names},
        request
    ))

@csrf_exempt
def preview_transaction(request):
    success_message = None
    error_message = None
    
    file_name = request.POST['file_name']
    #print(file_name)
    supplier_file_path = os.path.join(settings.MEDIA_ROOT, file_name)
    # Handle sheet selection based on the form submission
    if request.method == 'POST' and 'selected_sheet' in request.POST:
        selected_sheet = request.POST['selected_sheet']
        
        selected_supplier = request.POST['selected_supplier']

        skip_rows = 1

        if 'skip_rows' in request.POST:
            skip_rows = int(request.POST['skip_rows'])

        # Read a preview of the data
        df_preview = pd.read_excel(supplier_file_path, sheet_name=selected_sheet, nrows=5, skiprows=skip_rows)
        # Convert NaN values to None for proper rendering in HTML
        df_preview = df_preview.where(pd.notna(df_preview), None)

        # Get column names with index
        column_names_with_index = list(enumerate(df_preview.columns, 1))
        column_names = [column_name for index, column_name in column_names_with_index]

        # Fetch distinct parent_company_names from the Customer model
        parent_company_names = Customer.objects.values_list('parent_company_name', flat=True).distinct()

        process_result= None
        if process_result:
            success_message = "All data has been successfully saved to the database."
        else:
            error_message = process_result

    # Load the template manually to include the confirmation prompt
    template = loader.get_template('transaction_detail.html')

    return HttpResponse(template.render(
        {'success_message': success_message, 'error_message': error_message,
         'file_name': file_name, 'selected_sheet': selected_sheet, 'selected_supplier': selected_supplier,
         'skip_rows': skip_rows, 'df_preview': df_preview.to_html(classes='table table-striped'),'column_names': column_names,'parent_company_names': parent_company_names}
    ))

@csrf_exempt
def reload_preview(request):
    success_message = None
    error_message = None
    
    if request.method == 'POST' and 'skip_rows' in request.POST:
        file_name = request.POST['file_name']
        supplier_file_path = os.path.join(settings.MEDIA_ROOT, file_name)

        selected_sheet = request.POST['selected_sheet']
        selected_supplier = request.POST['selected_supplier']
        
        skip_rows = int(request.POST['skip_rows'])
        
        df_preview = pd.read_excel(supplier_file_path, sheet_name=selected_sheet, nrows=5, skiprows=skip_rows)
        df_preview = df_preview.where(pd.notna(df_preview), None)

        # Get column names with index
        column_names_with_index = list(enumerate(df_preview.columns, 1))
        column_names = [column_name for index, column_name in column_names_with_index]

        
        # Retrieve ERA standard mapping
        era_standard_mapping = [
            'customer_name', 'customer_number', 'parent_company_name', 'customer_site_name', 'customer_site_address',
            'customer_site_suburb', 'customer_site_city', 'customer_site_state', 'customer_site_number', 'service_name',
            'container_type', 'size', 'fee_type', 'uom', 'service_weight', 'supplier_outlet_name', 'supplier_outlet_address',
            'supplier_outlet_suburb', 'supplier_outlet_city', 'supplier_outlet_state', 'supplier_outlet_number',
            'waste_stream_name', 'stream_group', 'sub_stream_name', 'sub_stream_code', 'invoice_number', 'invoice_date','transaction_date',
            'quantity', 'transaction_weight', 'transaction_volume', 'unit_amount', 'transaction_ref', 'transaction_number'
        ]

        # Fetch distinct parent_company_names from the Customer model
        parent_company_names = Customer.objects.values_list('parent_company_name', flat=True).distinct()

    template = loader.get_template('transaction_detail.html')

    return HttpResponse(template.render(
        {'success_message': success_message, 'error_message': error_message,
         'file_name': file_name, 'selected_sheet': selected_sheet, 'selected_supplier': selected_supplier,
         'skip_rows': skip_rows, 'df_preview': df_preview.to_html(classes='table table-striped'),
         'column_names': column_names, 'era_standard_mapping': era_standard_mapping,'parent_company_names': parent_company_names}
    ))

@csrf_exempt
def save_transaction(request):
    success_message = None
    error_data = None
    download_errors_url = None

    era_standard_mapping = [
        'customer_name', 'customer_number', 'parent_company_name', 'customer_site_name', 'customer_site_address',
        'customer_site_suburb', 'customer_site_city', 'customer_site_state', 'customer_site_number', 'service_name',
        'container_type', 'size', 'fee_type', 'uom', 'service_weight', 'supplier_outlet_name', 'supplier_outlet_address',
        'supplier_outlet_suburb', 'supplier_outlet_city', 'supplier_outlet_state', 'supplier_outlet_number',
        'waste_stream_name', 'stream_group', 'sub_stream_name', 'sub_stream_code', 'invoice_number', 'invoice_date','transaction_date',
        'quantity', 'transaction_weight', 'transaction_volume', 'unit_amount', 'transaction_ref', 'transaction_number'
    ]

    if request.method == 'POST' and request.POST.get('file_name') and request.POST.get('selected_sheet'):
        file_name = request.POST['file_name']
        supplier_file_path = os.path.join(settings.MEDIA_ROOT, file_name)
        selected_sheet = request.POST['selected_sheet']
        skip_rows = int(request.POST['skip_rows'])
        selected_supplier = request.POST['selected_supplier']
        #print("Supplier Name:", selected_supplier)
        
        # Read the entire sheet
        df = pd.read_excel(supplier_file_path, sheet_name=selected_sheet, skiprows=skip_rows)

        # Extract selected column names from the POST data
        selected_columns = []
        for i in range(len(era_standard_mapping)):
            column_key = f'selected_columns_{i}'
            selected_columns.append(request.POST.get(column_key, '')) 

        # Initialize lists to store successful and error data
        success_data = []
        error_data = []

        selected_parent_company_name = selected_columns[2] 
        selected_columns[2] = 'None'

        # Process and save to the database
        for index, row in df.iterrows():
            try:
                #print(selected_columns)

                # Replace problematic characters in column names
                modified_columns = [re.sub(r'[^a-zA-Z0-9]', '', col.replace('\r\n', '').replace(' ', '_')) for col in selected_columns]
                #print("Modified Columns:", modified_columns)
                #print("Actual DataFrame Columns:", df.columns)

                # Find closest matches using fuzzy matching
                matched_columns_mapping = {}

                for modified_column in modified_columns:
                    matches = process.extractOne(modified_column, df.columns)
                    
                    if matches[1] >= 80:  # You can adjust the threshold as needed
                        matched_columns_mapping[modified_column] = matches[0]

                #print("Matched Columns Mapping:", matched_columns_mapping)

                processed_row = {era_standard_mapping[i]: row.get(matched_columns_mapping.get(modified_columns[i], 'None'), 'Default') for i in range(len(era_standard_mapping))}
                processed_row['parent_company_name'] = selected_parent_company_name

                #print("Processed Row:", processed_row)

                # Validate required fields before creating database objects
                required_fields = ['customer_name', 'customer_site_name', 'service_name', 'waste_stream_name']
                if any(processed_row[field] is None or processed_row[field] == '' for field in required_fields):
                    raise ValueError("Required fields are missing.")


                # Replace 'Default' values with None
                processed_row = {key: None if value == 'Default' else value for key, value in processed_row.items()}

                #process_result = process_transaction(processed_row, supplier_name)
                
                # Create Customer object
                if processed_row['customer_name']:
                    # Check if customer_name is not empty, create or get based on customer_name
                    customer, created = Customer.objects.get_or_create(
                        customer_name=processed_row['customer_name'],
                        customer_number=processed_row['customer_number'],
                        parent_company_name=processed_row['parent_company_name'],
                    )
                else:
                    # Check if customer_name is empty, get based on customer_number
                    try:
                        customer = Customer.objects.get(customer_number=processed_row['customer_number'])
                    except Customer.DoesNotExist:
                        # If no existing record is found, create a new one
                        customer = Customer.objects.create(
                            customer_number=processed_row['customer_number'],
                            parent_company_name=processed_row['parent_company_name'],
                        )
                # Extract customer_id
                customer_id = customer.customer_id if customer else None

                # Create CustomerSite object
                customer_site, created = CustomerSite.objects.get_or_create(
                    customer_id=customer_id,
                    site_name=processed_row['customer_site_name'],
                    site_address=processed_row['customer_site_address'],
                    suburb_or_town=processed_row['customer_site_suburb'],
                    city=processed_row['customer_site_city'],
                    state=processed_row['customer_site_state'],
                    site_number=processed_row['customer_site_number'],
                )

                # Check if the WasteStream with the given waste_stream_name already exists
                waste_stream = WasteStream.objects.filter(stream_name=processed_row['waste_stream_name']).first()

                if not waste_stream:
                    # Create WasteStream object only if it doesn't exist
                    waste_stream = WasteStream.objects.create(
                        stream_group=processed_row['stream_group'],
                        stream_name=processed_row['waste_stream_name'],
                        sub_stream_name=processed_row['sub_stream_name'],
                        sub_stream_code=processed_row['sub_stream_code'],
                    )

                # Concatenate values for original_desc
                original_desc_value = f"{processed_row['service_name']} {processed_row['container_type']} {processed_row['size']} {processed_row['fee_type']} {processed_row['uom']}"
                original_desc_value = original_desc_value.strip()

                if processed_row['service_name'] is None:
                    processed_row['service_name'] = original_desc_value
                # Check if container_type,size,fee_type, uom, and service_weight are empty
                if not processed_row['container_type'] or not processed_row['size'] or not processed_row['fee_type'] or not processed_row['uom']:
                    era_standard_term_entry = EraStandardTerm.objects.filter(era_desc=processed_row['service_name']).first()

                    if era_standard_term_entry:
                        processed_row['container_type'] = era_standard_term_entry.container
                        processed_row['size'] = era_standard_term_entry.sizem3
                        processed_row['fee_type'] = era_standard_term_entry.activity
                        processed_row['uom'] = era_standard_term_entry.uom
                    else:
                        # Create EraStandardTerm entry
                        era_standard_term_entry, created = EraStandardTerm.objects.get_or_create(
                            era_desc=original_desc_value,
                            stream_name=processed_row['waste_stream_name'],
                            container=processed_row['container_type'],
                            sizem3=processed_row['size'],
                            uom=processed_row['uom'],
                            activity=processed_row['fee_type'],
                        )
                

                        
                # Check if the Service with the given service_name already exists
                try:
                    service = Service.objects.filter(service_name=processed_row['service_name']).first()


                    #if service.exists():
                    #    service = service.first()
                    # If an existing record is found, get the ServiceType object
                    # Create ServiceType object
                    service_type, created = ServiceType.objects.get_or_create(
                        fee_type=processed_row['fee_type'],
                        unit_of_measure=processed_row['uom'],
                        weight=processed_row['service_weight'],
                    )
                    
                except ObjectDoesNotExist:
                    # If no existing record is found, Calculate similarity
                    similarity = calculate_similarity(original_desc_value, processed_row['service_name'])

                    print("Original Desc:", original_desc_value)
                    print("Service Name:", processed_row['service_name'])
                    print("Similarity:", similarity)

                    # If similarity is greater than 80, use the existing service
                    if similarity > 80:
                        service_type, created = ServiceType.objects.get_or_create(
                            fee_type=processed_row['fee_type'],
                            unit_of_measure=processed_row['uom'],
                            weight=processed_row['service_weight'],
                        )
                    else:
                        # Create EraStandardTerm entry
                        era_standard_term_entry, created = EraStandardTerm.objects.get_or_create(
                            era_desc=original_desc_value,
                            stream_name=processed_row['waste_stream_name'],
                            container=processed_row['container_type'],
                            sizem3=processed_row['size'],
                            uom=processed_row['uom'],
                            activity=processed_row['fee_type'],
                        )
                        # Create Service object only if it doesn't exist
                        service = Service.objects.create(
                            service_name=processed_row['service_name'],
                            container_type=processed_row['container_type'],
                            size=processed_row['size'],
                        )
                        
                        # Calculate similarity after creating the Service object
                        similarity = calculate_similarity(original_desc_value, service.service_name)
                        print("Similarity:", similarity)

                        # Create ServiceType object
                        service_type, created = ServiceType.objects.get_or_create(
                            fee_type=processed_row['fee_type'],
                            unit_of_measure=processed_row['uom'],
                            weight=processed_row['service_weight'],
                        )                    
                    # Update des_service_similarity in the TransactionDetail object
                    transaction_detail.des_service_similarity = similarity
                    transaction_detail.save()

                #print("Supplier Name:", selected_supplier)
                supplier, created = Supplier.objects.get_or_create(
                    supplier_name=selected_supplier,
                )
                
                if processed_row['supplier_outlet_name'] is None:
                    processed_row['supplier_outlet_name'] = selected_supplier

                # Create SupplierOutlet object
                supplier_outlet, created = SupplierOutlet.objects.get_or_create(
                    supplier=supplier,
                    outlet_name=processed_row['supplier_outlet_name'],
                    outlet_address=processed_row['supplier_outlet_address'],
                    suburb_or_town=processed_row['supplier_outlet_suburb'],
                    city=processed_row['supplier_outlet_city'],
                    state=processed_row['supplier_outlet_state'],
                    outlet_number=processed_row['supplier_outlet_number'],
                )

                # Check if a similar TransactionDetail already exists
                existing_transaction_detail = TransactionDetail.objects.filter(
                    invoice_number=processed_row['invoice_number'],
                    transaction_date=processed_row['transaction_date'],
                    stream=waste_stream,
                    service=service,
                    type=service_type,
                    outlet=supplier_outlet,
                    site=customer_site,
                ).first()

                if existing_transaction_detail:
                    # Use the existing TransactionDetail if it exists
                    transaction_detail = existing_transaction_detail
                else:
                    # Create a new TransactionDetail object
                    transaction_detail = TransactionDetail.objects.create(
                        invoice_number=processed_row['invoice_number'],
                        invoice_date=processed_row['invoice_date'],
                        transaction_date=processed_row['transaction_date'],
                        quantity=processed_row['quantity'],
                        weight=processed_row['transaction_weight'],
                        volume=processed_row['transaction_volume'],
                        unit_amount=processed_row['unit_amount'],
                        transaction_ref=processed_row['transaction_ref'],
                        transaction_number=processed_row['transaction_number'],
                        stream=waste_stream,
                        service=service,
                        type=service_type,
                        outlet=supplier_outlet,
                        site=customer_site,
                        original_desc=original_desc_value,
                        des_service_similarity=similarity,
                    )

                # Append to the successful data list
                success_data.append(row)

            except Exception as e:
                print(f"Error processing row: {row}, Error: {e}")
                error_data.append(row)

        # Prepare data for download
        if error_data:
            error_data = error_data
            download_errors_url = "/download_errors/"  # Replace with your actual download_errors URL
        else:
            success_message = "All data has been successfully saved to the database."

    return render(request, 'transaction_detail.html', {'success_message': success_message, 'error_data': error_data, 'download_errors_url': download_errors_url,'selected_supplier': selected_supplier, 'selected_parent_company_name': selected_parent_company_name})

#TODO HASN'T FINISHED
def upload_contract(request):
    success_message = None
    error_message = None
    download_errors_url = None  

    if request.method == 'POST' and request.FILES['excel_file']:
        uploaded_file = request.FILES['excel_file']

        # Save the uploaded file to the server
        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)

        # Get the saved file path
        file_path = fs.url(filename)

        try:
            # Call the processing logic in contracts.py
            contract_content = process_contract(file_path)

            # Initialize lists to store successful and error data
            success_data = []
            error_data = []

            # Process and save to the database
            for row in contract_content:
                try:
                    outlet, site, stream_id, service, type, qty_scheduled, frequency, unit_price, start_date, end_date, stage, route_schedule, days = row

                    # Create a new MarketServicePrice object
                    MarketServicePrice.objects.create(
                        outlet=outlet,
                        site=site,
                        stream_id=stream_id,
                        service=service,
                        type=type,
                        qty_scheduled=qty_scheduled,
                        frequency=frequency,
                        unit_price=unit_price,
                        start_date=start_date,
                        end_date=end_date,
                        stage=stage,
                        route_schedule=route_schedule,
                        days=days
                    )

                    # Append to the successful data list
                    success_data.append(row)

                except Exception as e:
                    # If an error occurs, append the row to the error data list
                    error_data.append(row)

            # Prepare data for download
            if error_data:
                error_message = "Data could not be processed successfully. You can download the error data below."
                download_errors_url = "/download_errors/"  # Replace with your actual download_errors URL
            else:
                success_message = "All data has been successfully saved to the database."

        except Exception as e:
            error_message = "An error occurred during data processing."

    return render(request, 'contracts.html', {'success_message': success_message, 'error_message': error_message, 'download_errors_url': download_errors_url})

def download_errors_view(request):

    return HttpResponse("Download errors view")

def monitoring(request):

    # Load the template manually to include the confirmation prompt
    template = loader.get_template('monitoring.html')

    return HttpResponse(template.render(
        {},
        request
    ))


def dashboard(request):
    pdf_file = 'docs.pdf'
    pdf_path = os.path.join(settings.MEDIA_ROOT, pdf_file)

    if os.path.exists(pdf_path):
        #print(f"PDF file exists: {pdf_path}")
        template = loader.get_template('dashboard.html')
        return HttpResponse(template.render({'pdf_url': pdf_path}, request))
    else:
        #print(f"PDF file not found: {pdf_path}")
        return HttpResponse("PDF file not found.")
    
# Function to calculate text similarity using fuzzywuzzy
def calculate_similarity(a, b):
    return fuzz.token_sort_ratio(a, b)