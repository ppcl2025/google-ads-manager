#!/usr/bin/env python3
"""
Test script to debug API v21 campaign fields
This will help identify the correct field names for your Google Ads API version
"""

import os
import sys
from google.ads.googleads.client import GoogleAdsClient

def test_campaign_fields():
    """Test what fields are available on campaign objects in API v21"""
    
    try:
        # Try to load client from environment or secrets
        if hasattr(os.environ, 'GOOGLE_ADS_CLIENT_ID'):
            # Local environment
            client = GoogleAdsClient.load_from_env()
        else:
            # Streamlit Cloud - we'll need to handle this differently
            print("❌ No Google Ads credentials found in environment")
            print("Please set up your credentials first")
            return
        
        print("🔍 Testing Google Ads API v21 campaign fields...")
        print("=" * 60)
        
        # Get the campaign type to see what fields are available
        campaign_type = client.get_type("Campaign")
        print(f"✅ Campaign type loaded: {type(campaign_type).__name__}")
        
        # Get all available fields (excluding private ones)
        available_fields = [attr for attr in dir(campaign_type) if not attr.startswith('_')]
        print(f"📋 Total available fields: {len(available_fields)}")
        
        # Show first 20 fields
        print("\n🔍 First 20 available fields:")
        for i, field in enumerate(available_fields[:20]):
            print(f"  {i+1:2d}. {field}")
        
        # Look for EU political advertising related fields
        print("\n🔍 EU Political Advertising related fields:")
        eu_fields = [field for field in available_fields if 'eu' in field.lower() or 'political' in field.lower()]
        if eu_fields:
            for field in eu_fields:
                print(f"  ✅ Found: {field}")
        else:
            print("  ❌ No EU political advertising fields found")
        
        # Look for network settings related fields
        print("\n🔍 Network Settings related fields:")
        network_fields = [field for field in available_fields if 'network' in field.lower() or 'target_' in field.lower()]
        if network_fields:
            for field in network_fields:
                print(f"  ✅ Found: {field}")
        else:
            print("  ❌ No network settings fields found")
        
        # Look for geo targeting related fields
        print("\n🔍 Geo Targeting related fields:")
        geo_fields = [field for field in available_fields if 'geo' in field.lower() or 'location' in field.lower()]
        if geo_fields:
            for field in geo_fields:
                print(f"  ✅ Found: {field}")
        else:
            print("  ❌ No geo targeting fields found")
        
        # Show the full list if requested
        if len(sys.argv) > 1 and sys.argv[1] == "--all":
            print(f"\n📋 All {len(available_fields)} available fields:")
            for i, field in enumerate(available_fields):
                print(f"  {i+1:3d}. {field}")
        
        print("\n" + "=" * 60)
        print("💡 Use this information to update the campaign creation code")
        print("💡 Run with --all flag to see all fields: python test_api_v21_fields.py --all")
        
    except Exception as e:
        print(f"❌ Error testing campaign fields: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure you have valid Google Ads credentials")
        print("2. Check that google-ads package is installed")
        print("3. Verify your API access is working")

if __name__ == "__main__":
    test_campaign_fields()
