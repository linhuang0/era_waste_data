import pandas as pd
import os
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.conf import settings
from django.template import loader
from .contracts import process_contract
from .strandard_transaction_data import process_transaction
from .models import MarketServicePrice
from transaction.models import Supplier


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
    file_names = fs.listdir(settings.MEDIA_ROOT)
    selected_file = None
    sheet_names = []
    all_supplier_names= []
    if request.method == 'POST' and request.POST.get('selected_file'):
        selected_file = request.POST['selected_file']
        print(selected_file)

        supplier_file_path = os.path.join(settings.MEDIA_ROOT, selected_file)
        # Use pandas to read Excel data
        df = pd.read_excel(supplier_file_path)
        # Use pandas to read Excel data from all sheets
        xls = pd.ExcelFile(supplier_file_path)

        sheet_names = xls.sheet_names
        print(sheet_names)
        
        all_supplier= Supplier.objects.all()
        all_supplier_names = all_supplier.values_list('supplier_name', flat=True)
        print(all_supplier_names)
        
    # Load the template manually to include the confirmation prompt
    template = loader.get_template('invoices.html')

    return HttpResponse(template.render(
        {'file_names': file_names,'selected_file': selected_file, 'sheet_names': sheet_names, 'all_supplier_names': all_supplier_names},
        request
    ))

def save_transaction(request):
    success_message = None
    error_message = None
    
    file_name = request.POST['file_name']
    print(file_name)
    supplier_file_path = os.path.join(settings.MEDIA_ROOT, file_name)
    # Handle sheet selection based on the form submission
    if 'selected_sheet' in request.POST:
        selected_sheet = request.POST['selected_sheet']
        df = pd.read_excel(supplier_file_path, sheet_name=selected_sheet,skiprows=2)
        #column_names = list(df.columns)
        supplier_name = request.POST['selected_supplier']
        process_result= process_transaction(df,supplier_name)
        if process_result:
            success_message = "All data has been successfully saved to the database."
        else:
            error_message = process_result

    # Load the template manually to include the confirmation prompt
    template = loader.get_template('invoices.html')

    return HttpResponse(template.render(
        {'success_message': success_message, 'error_message': error_message,
         'file_name': file_name, 'selected_sheet': selected_sheet, 'supplier_name': supplier_name},
        request
    ))


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
