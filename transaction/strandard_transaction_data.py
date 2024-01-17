
from transaction.models import Customer,Supplier,CustomerSite,SupplierOutlet,WasteStream,Service,ServiceType,MarketServicePrice,TransactionDetail,EraStandardTerm

def process_transaction(sheets_data,supplier_name):
    try:
        error_data = []
        supplier, created = Supplier.objects.get_or_create(
            supplier_name=supplier_name,
        )
                    
        for index, row in sheets_data.iterrows():
            customer, created = Customer.objects.get_or_create(
                customer_name=str(row['Customer Entity']),
                #parent_company_name='Charles Sturt University'
                #customer_number=row['Customer Number']
            )
            # Clean customer site info. Use "Task Site" as site_name, Use get_or_create to avoid duplicates
            customerSite, created = CustomerSite.objects.get_or_create(
                site_name=str(row['Ship to Name']),
                site_number=str(row['Account Number']),
                customer=customer,
                city=str(row['Ship to City']),
                state=str(row['Ship to State']),
            )

            outlet, created = SupplierOutlet.objects.get_or_create(
                outlet_name=supplier_name,
                supplier=supplier,
            )

            wasteStream, created = WasteStream.objects.get_or_create(
                stream_name=str(row['Waste Stream']),
            )

            # Use filter to get a queryset
            service_queryset = Service.objects.filter(service_name=str(row['Description']))

            if service_queryset.exists():
                # If the queryset is not empty, retrieve the first object
                service = service_queryset.first()
            else:
                # If the queryset is empty, create a new Service object
                service, created = Service.objects.get_or_create(
                    service_name=str(row['Description']),
                    #container_type=str(best_match_row['container_type']),
                    #size=str(best_match_row['size']),
                )

            # TODO Process service type and unit of measure
                        
            transaction, created = TransactionDetail.objects.get_or_create(
                transaction_date=row['Transaction Date'],
                quantity=float(row['No. Units Serviced']),
                unit_amount=float(row['Unit Amount']),
                site=customerSite,
                outlet=outlet,
                service=service,
                stream=wasteStream,
                volume=float(row['Volume (m3)']),
                weight=float(row['Weight\n(kg)']),
                transaction_ref=row['Reference'],
                invoice_number=row['Invoice Number'],
            )
        
        print(f"Successfully processed {len(sheets_data)} transactions")
        return True

    except Exception as e:
        print(f"Error processing transaction: {e}")
        error_data.append(row)
        print(f"Error data: {error_data}")
        return error_data