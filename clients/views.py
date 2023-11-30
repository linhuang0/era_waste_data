import os
import pandas as pd
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.conf.urls.static import static
from .models import CUSTOMERS


def read_excel_and_add_customers():
    """
    Function to read customer data from an Excel file and add to the database.

    Returns:
        str: Message indicating success or failure.
    """
    try:
        # Construct the path to the Excel file in the media folder
        file_path = os.path.join(settings.MEDIA_ROOT, '07_Solo_seagulls october 2022 - december 2022.xlsx')
        
        # Use pandas to read Excel data
        df = pd.read_excel(file_path)
        
        # Iterate through each row
        for index, row in df.iterrows():
            # Use "Task Site" as customer_name
            customer_name = str(row['Task Site'])
            
            # Check if a record with the same customer_name exists in the database
            if not CUSTOMERS.objects.filter(customer_name=customer_name).exists():
                # If not, add a new record to the database
                CUSTOMERS.objects.create(customer_name=customer_name)
        
        return 'Data imported successfully'
    except Exception as e:
        return f'Error: {str(e)}'



# Check if the script is executed directly
if __name__ == "__main__":
    # Call the function to read and add customers
    result_message = read_excel_and_add_customers()

    print(result_message)


def list_all_customers(request):

    # Retrieve all customer records
    customers = CUSTOMERS.objects.all()
    
    # Build a JSON response for the list of customers
    customer_list = [{'customer_name': customer.customer_name, 'customer_number': customer.customer_number}
                     for customer in customers]
    return JsonResponse({'customers': customer_list})
