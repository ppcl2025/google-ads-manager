#!/usr/bin/env python3
"""
Test script to debug conversion tracking setup for sub-accounts
"""

import os
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

def test_conversion_tracking_setup():
    """Test different approaches to set conversion tracking for sub-accounts"""
    
    try:
        # Load client from environment variables with proper configuration
        client = GoogleAdsClient.load_from_dict({
            "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
            "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
            "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
            "login_customer_id": os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID"),
            "use_proto_plus": True
        })
        
        # Test customer ID (replace with your actual sub-account ID)
        test_customer_id = "2796337825"  # Test 5 account ID
        mcc_customer_id = "5022887746"   # Your MCC ID
        
        print(f"Testing conversion tracking setup for customer: {test_customer_id}")
        print(f"MCC customer ID: {mcc_customer_id}")
        
        # Get available services
        customer_service = client.get_service("CustomerService")
        
        # Method 1: Try to get current customer info using search
        print("\n=== Method 1: Get current customer info using search ===")
        try:
            google_ads_service = client.get_service("GoogleAdsService")
            query = f"""
                SELECT
                  customer.id,
                  customer.descriptive_name,
                  customer.manager,
                  customer.test_account
                FROM customer
                WHERE customer.id = {test_customer_id}
            """
            response = google_ads_service.search(
                customer_id=test_customer_id,
                query=query
            )
            
            for row in response:
                customer = row.customer
                print(f"Customer name: {customer.descriptive_name}")
                print(f"Customer ID: {customer.id}")
                print(f"Manager: {customer.manager}")
                print(f"Test account: {customer.test_account}")
                
                if hasattr(customer, 'conversion_tracking_setting'):
                    print(f"Conversion tracking ID: {customer.conversion_tracking_setting.conversion_tracking_id}")
                    print(f"Cross account conversion tracking ID: {customer.conversion_tracking_setting.cross_account_conversion_tracking_id}")
                else:
                    print("No conversion tracking setting found")
                break
                
        except Exception as e:
            print(f"Error getting customer info: {e}")
        
        # Method 2: Try to update conversion tracking
        print("\n=== Method 2: Try to update conversion tracking ===")
        try:
            # Create customer operation
            customer_operation = client.get_type("CustomerOperation")
            customer_update = customer_operation.update
            customer_update.resource_name = f"customers/{test_customer_id}"
            
            # Set conversion tracking
            customer_update.conversion_tracking_setting = client.get_type("ConversionTrackingSetting")
            customer_update.conversion_tracking_setting.conversion_tracking_id = mcc_customer_id
            customer_update.conversion_tracking_setting.cross_account_conversion_tracking_id = mcc_customer_id
            
            # Try to update
            response = customer_service.mutate_customers(
                customer_id=test_customer_id,
                operations=[customer_operation]
            )
            print("✅ Successfully updated conversion tracking!")
            
        except Exception as e:
            print(f"Error updating conversion tracking: {e}")
        
        # Method 3: Check available customer fields
        print("\n=== Method 3: Check available customer fields ===")
        try:
            customer_type = client.get_type("Customer")
            print("Available customer fields:")
            for field in customer_type.DESCRIPTOR.fields:
                print(f"  - {field.name}: {field.type_name}")
        except Exception as e:
            print(f"Error checking customer fields: {e}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_conversion_tracking_setup() 