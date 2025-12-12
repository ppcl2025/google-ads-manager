"""
Account Manager - List and select MCC accounts and customer accounts
FIXED VERSION - Properly handles MCC account listing
"""

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
import os
from dotenv import load_dotenv

load_dotenv()

def list_customer_accounts(client, login_customer_id=None):
    """
    List all customer accounts accessible via the MCC.
    Uses customer_client resource which is the correct way for MCC accounts.
    """
    if not login_customer_id:
        login_customer_id = os.getenv("GOOGLE_ADS_CUSTOMER_ID")
    
    if not login_customer_id:
        raise ValueError("Customer ID (MCC or account) is required")
    
    try:
        ga_service = client.get_service("GoogleAdsService")
        
        # Use customer_client resource - this is the correct way to list accounts under MCC
        query = """
            SELECT
                customer_client.client_customer,
                customer_client.descriptive_name,
                customer_client.manager,
                customer_client.test_account,
                customer_client.currency_code,
                customer_client.time_zone
            FROM customer_client
            WHERE customer_client.level <= 1
        """
        
        # Convert MCC ID to numeric format (remove dashes)
        login_customer_id_numeric = login_customer_id.replace("-", "")
        
        try:
            # Query customer_client from the MCC
            # The customer_id should be the MCC in numeric format
            response = ga_service.search(customer_id=login_customer_id_numeric, query=query)
            
            customers = []
            for row in response:
                # Extract customer ID from client_customer resource name
                client_customer_resource = row.customer_client.client_customer
                customer_id_numeric = client_customer_resource.split('/')[-1]
                
                # Format customer ID (1234567890 -> 123-456-7890)
                formatted_id = f"{customer_id_numeric[:3]}-{customer_id_numeric[3:6]}-{customer_id_numeric[6:]}"
                
                # Skip if this is the MCC account itself
                if formatted_id == login_customer_id:
                    continue
                
                # Only add if it's NOT a manager account
                if not row.customer_client.manager:
                    customers.append({
                        'customer_id': formatted_id,
                        'descriptive_name': row.customer_client.descriptive_name or formatted_id,
                        'currency_code': row.customer_client.currency_code if hasattr(row.customer_client, 'currency_code') else 'N/A',
                        'time_zone': row.customer_client.time_zone if hasattr(row.customer_client, 'time_zone') else 'N/A',
                        'manager': False,
                        'test_account': row.customer_client.test_account if hasattr(row.customer_client, 'test_account') else False
                    })
            
            return customers
            
        except GoogleAdsException as e:
            error_msg = str(e.error.message()) if hasattr(e, 'error') and hasattr(e.error, 'message') else str(e)
            
            # If we get "Invalid customer ID", it means we can't query the MCC directly
            # This might be a permissions issue or the MCC format is wrong
            if "Invalid customer ID" in error_msg or "INVALID_CUSTOMENT_ID" in error_msg:
                print(f"\n⚠️  Cannot query customer_client from MCC account.")
                print(f"   Error: {error_msg}")
                print(f"\n   Possible issues:")
                print(f"   1. The MCC account ({login_customer_id}) may not have API access enabled")
                print(f"   2. Your OAuth token may not have permission to list linked accounts")
                print(f"   3. The customer accounts may need to be linked differently")
                print(f"\n   SOLUTION: Try using a specific customer account ID directly")
                print(f"   Update GOOGLE_ADS_CUSTOMER_ID in .env to a customer account (not MCC)")
                return []
            
            raise e
        
    except GoogleAdsException as ex:
        error_msg = ex.error.message() if hasattr(ex, 'error') and hasattr(ex.error, 'message') else str(ex)
        raise Exception(f"Error listing customer accounts: {error_msg}")

# Rest of the file remains the same...
def list_campaigns(client, customer_id):
    """
    List all campaigns for a customer account.
    
    Args:
        client: Google Ads API client
        customer_id: Customer account ID (format: 123-456-7890)
    """
    try:
        ga_service = client.get_service("GoogleAdsService")
        
        query = """
            SELECT
                campaign.id,
                campaign.name,
                campaign.status,
                campaign.start_date,
                campaign.end_date
            FROM campaign
            WHERE campaign.status != 'REMOVED'
            ORDER BY campaign.name
        """
        
        # Convert customer_id to numeric format (remove dashes) for API
        customer_id_numeric = customer_id.replace("-", "")
        response = ga_service.search(customer_id=customer_id_numeric, query=query)
        
        campaigns = []
        for row in response:
            campaigns.append({
                'campaign_id': row.campaign.id,
                'campaign_name': row.campaign.name,
                'status': row.campaign.status.name,
                'start_date': row.campaign.start_date if hasattr(row.campaign, 'start_date') else 'N/A',
                'end_date': row.campaign.end_date if hasattr(row.campaign, 'end_date') else 'N/A'
            })
        
        return campaigns
        
    except GoogleAdsException as ex:
        raise Exception(f"Error listing campaigns: {ex.error.message()}")

def select_account_interactive(client):
    """Interactive account selector."""
    print("\n" + "="*60)
    print("Select Customer Account")
    print("="*60 + "\n")
    
    try:
        accounts = list_customer_accounts(client)
        
        if not accounts:
            print("No accessible customer accounts found.")
            print("\n💡 TIP: If you have customer accounts linked to your MCC,")
            print("   you may need to:")
            print("   1. Use a specific customer account ID directly")
            print("   2. Ensure API access is enabled for those accounts")
            print("   3. Check OAuth permissions")
            print("\n   Would you like to enter a customer account ID manually?")
            manual = input("   Enter customer account ID (format: 123-456-7890) or press Enter to skip: ").strip()
            if manual:
                return {
                    'customer_id': manual,
                    'account_name': manual  # Use ID as name if manually entered
                }
            return None
        
        print("Available Customer Accounts:\n")
        for idx, account in enumerate(accounts, 1):
            account_type = "MCC/Manager" if account['manager'] else "Account"
            test_label = " (TEST)" if account['test_account'] else ""
            print(f"{idx}. {account['descriptive_name']} ({account['customer_id']}) [{account_type}]{test_label}")
        
        print(f"\n{len(accounts) + 1}. Use default from .env file")
        
        while True:
            try:
                choice = input(f"\nSelect account (1-{len(accounts) + 1}): ").strip()
                choice_num = int(choice)
                
                if choice_num == len(accounts) + 1:
                    default_id = os.getenv("GOOGLE_ADS_CUSTOMER_ID")
                    if default_id:
                        print(f"Using default account: {default_id}")
                        return {
                            'customer_id': default_id,
                            'account_name': default_id  # Use ID as name if no name available
                        }
                    else:
                        print("No default account found in .env file.")
                        continue
                
                if 1 <= choice_num <= len(accounts):
                    selected = accounts[choice_num - 1]
                    print(f"Selected: {selected['descriptive_name']} ({selected['customer_id']})")
                    return {
                        'customer_id': selected['customer_id'],
                        'account_name': selected['descriptive_name']
                    }
                else:
                    print(f"Please enter a number between 1 and {len(accounts) + 1}")
            except ValueError:
                print("Please enter a valid number")
            except KeyboardInterrupt:
                print("\n\nCancelled.")
                return None
                
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def select_campaign_interactive(client, customer_id):
    """Interactive campaign selector."""
    print("\n" + "="*60)
    print("Select Campaign")
    print("="*60 + "\n")
    
    try:
        campaigns = list_campaigns(client, customer_id)
        
        if not campaigns:
            print("No campaigns found for this account.")
            return {
                'campaign_id': None,
                'campaign_name': 'No Campaigns Found'
            }
        
        print("Available Campaigns:\n")
        for idx, campaign in enumerate(campaigns, 1):
            status_icon = "✓" if campaign['status'] == 'ENABLED' else "⏸" if campaign['status'] == 'PAUSED' else "✗"
            print(f"{idx}. {status_icon} {campaign['campaign_name']} (ID: {campaign['campaign_id']}) [{campaign['status']}]")
        
        print(f"\n{len(campaigns) + 1}. Analyze all campaigns")
        
        while True:
            try:
                choice = input(f"\nSelect campaign (1-{len(campaigns) + 1}): ").strip()
                choice_num = int(choice)
                
                if choice_num == len(campaigns) + 1:
                    print("Selected: All campaigns")
                    return {
                        'campaign_id': None,
                        'campaign_name': 'All Campaigns'
                    }
                
                if 1 <= choice_num <= len(campaigns):
                    selected = campaigns[choice_num - 1]
                    print(f"Selected: {selected['campaign_name']} (ID: {selected['campaign_id']})")
                    return {
                        'campaign_id': selected['campaign_id'],
                        'campaign_name': selected['campaign_name']
                    }
                else:
                    print(f"Please enter a number between 1 and {len(campaigns) + 1}")
            except ValueError:
                print("Please enter a valid number")
            except KeyboardInterrupt:
                print("\n\nCancelled.")
                return {
                    'campaign_id': None,
                    'campaign_name': 'Cancelled'
                }
                
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'campaign_id': None,
            'campaign_name': 'Error Loading Campaigns'
        }

