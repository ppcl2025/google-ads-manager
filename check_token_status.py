#!/usr/bin/env python3
"""
Google Ads Token Status Checker

This script checks if your current Google Ads API token is working.
Useful for testing tokens before updating Streamlit Cloud secrets.

Usage:
python check_token_status.py
"""

import os
import sys
from google.ads.googleads.client import GoogleAdsClient

def check_token_status():
    """Check if the current Google Ads token is working."""
    print("🔍 Checking Google Ads Token Status")
    print("=" * 40)
    
    # Check if we have the required environment variables
    required_vars = [
        "GOOGLE_ADS_CLIENT_ID",
        "GOOGLE_ADS_CLIENT_SECRET", 
        "GOOGLE_ADS_DEVELOPER_TOKEN",
        "GOOGLE_ADS_REFRESH_TOKEN",
        "GOOGLE_ADS_LOGIN_CUSTOMER_ID"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n📋 To fix this:")
        print("1. Create a .env file in this directory")
        print("2. Add your Google Ads credentials:")
        print("   GOOGLE_ADS_CLIENT_ID=your_client_id")
        print("   GOOGLE_ADS_CLIENT_SECRET=your_client_secret")
        print("   GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token")
        print("   GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token")
        print("   GOOGLE_ADS_LOGIN_CUSTOMER_ID=your_customer_id")
        print("3. Run: source .env && python check_token_status.py")
        return False
    
    try:
        # Create client
        print("🔧 Creating Google Ads client...")
        client = GoogleAdsClient.load_from_env()
        
        # Test the client
        print("🧪 Testing API connection...")
        google_ads_service = client.get_service("GoogleAdsService")
        
        # Simple query to test authentication
        query = "SELECT customer.id FROM customer LIMIT 1"
        customer_id = os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID")
        
        response = google_ads_service.search(customer_id=customer_id, query=query)
        
        print("✅ Token is working!")
        print(f"📊 Customer ID: {customer_id}")
        print(f"🔗 API Response: {len(list(response))} results")
        
        return True
        
    except Exception as e:
        error_msg = str(e).lower()
        
        if "invalid_grant" in error_msg or "token has been expired" in error_msg:
            print("❌ Token expired or revoked")
            print("\n📋 To fix this:")
            print("1. Run: python refresh_token_simple.py")
            print("2. Update your environment variables")
            print("3. Test again with this script")
        elif "access_denied" in error_msg:
            print("❌ Access denied - check permissions")
            print("\n📋 To fix this:")
            print("1. Verify your OAuth consent screen settings")
            print("2. Check that the app has the right scopes")
            print("3. Ensure you're using the correct Google account")
        else:
            print(f"❌ API Error: {e}")
            print("\n📋 This might be a temporary issue. Try again later.")
        
        return False

def main():
    """Main function."""
    success = check_token_status()
    
    if success:
        print("\n🎉 Your Google Ads token is working correctly!")
        print("You can use this token in your Streamlit Cloud app.")
    else:
        print("\n💡 Need help? Check the troubleshooting guide:")
        print("   TOKEN_TROUBLESHOOTING.md")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
