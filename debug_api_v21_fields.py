#!/usr/bin/env python3
"""
Comprehensive API v21 Field Debugging Script
This script will help identify all available fields for various Google Ads objects in your API version
"""

import os
import sys
from google.ads.googleads.client import GoogleAdsClient

def debug_api_v21_fields():
    """Debug what fields are available in API v21 for various Google Ads objects"""
    
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
        
        print("🔍 Comprehensive Google Ads API v21 Field Debugging")
        print("=" * 80)
        
        # Test Campaign object
        print("\n📋 CAMPAIGN OBJECT FIELDS:")
        print("-" * 40)
        campaign_type = client.get_type("Campaign")
        campaign_fields = [attr for attr in dir(campaign_type) if not attr.startswith('_')]
        print(f"Total fields: {len(campaign_fields)}")
        print("First 30 fields:")
        for i, field in enumerate(campaign_fields[:30]):
            print(f"  {i+1:2d}. {field}")
        
        # Test CampaignBudget object
        print("\n💰 CAMPAIGN BUDGET OBJECT FIELDS:")
        print("-" * 40)
        budget_type = client.get_type("CampaignBudget")
        budget_fields = [attr for attr in dir(budget_type) if not attr.startswith('_')]
        print(f"Total fields: {len(budget_fields)}")
        print("First 20 fields:")
        for i, field in enumerate(budget_fields[:20]):
            print(f"  {i+1:2d}. {field}")
        
        # Test ManualCpc object
        print("\n🎯 MANUAL CPC OBJECT FIELDS:")
        print("-" * 40)
        try:
            manual_cpc_type = client.get_type("ManualCpc")
            cpc_fields = [attr for attr in dir(manual_cpc_type) if not attr.startswith('_')]
            print(f"Total fields: {len(cpc_fields)}")
            print("All fields:")
            for i, field in enumerate(cpc_fields):
                print(f"  {i+1:2d}. {field}")
        except Exception as e:
            print(f"❌ Error getting ManualCpc type: {e}")
        
        # Look for specific fields we need
        print("\n🔍 SEARCHING FOR SPECIFIC FIELDS:")
        print("-" * 40)
        
        # Network settings fields
        print("\n🌐 NETWORK SETTINGS FIELDS:")
        network_keywords = ['target_', 'network', 'search', 'content', 'youtube', 'partner']
        network_fields = [field for field in campaign_fields if any(keyword in field.lower() for keyword in network_keywords)]
        if network_fields:
            for field in network_fields:
                print(f"  ✅ Found: {field}")
        else:
            print("  ❌ No network settings fields found")
        
        # Geo targeting fields
        print("\n📍 GEO TARGETING FIELDS:")
        geo_keywords = ['geo', 'location', 'positive', 'negative']
        geo_fields = [field for field in campaign_fields if any(keyword in field.lower() for keyword in geo_keywords)]
        if geo_fields:
            for field in geo_fields:
                print(f"  ✅ Found: {field}")
        else:
            print("  ❌ No geo targeting fields found")
        
        # EU political advertising fields
        print("\n🇪🇺 EU POLITICAL ADVERTISING FIELDS:")
        eu_keywords = ['eu', 'political', 'advertising']
        eu_fields = [field for field in campaign_fields if any(keyword in field.lower() for keyword in eu_keywords)]
        if eu_fields:
            for field in eu_fields:
                print(f"  ✅ Found: {field}")
        else:
            print("  ❌ No EU political advertising fields found")
        
        # Bidding strategy fields
        print("\n🎯 BIDDING STRATEGY FIELDS:")
        bidding_keywords = ['bidding', 'strategy', 'manual', 'cpc']
        bidding_fields = [field for field in campaign_fields if any(keyword in field.lower() for keyword in bidding_keywords)]
        if bidding_fields:
            for field in bidding_fields:
                print(f"  ✅ Found: {field}")
        else:
            print("  ❌ No bidding strategy fields found")
        
        # Show the full list if requested
        if len(sys.argv) > 1 and sys.argv[1] == "--all":
            print(f"\n📋 ALL {len(campaign_fields)} CAMPAIGN FIELDS:")
            for i, field in enumerate(campaign_fields):
                print(f"  {i+1:3d}. {field}")
        
        print("\n" + "=" * 80)
        print("💡 Use this information to update the campaign creation code")
        print("💡 Run with --all flag to see all fields: python debug_api_v21_fields.py --all")
        print("💡 Focus on the fields marked with ✅ for your campaign configuration")
        
    except Exception as e:
        print(f"❌ Error debugging API fields: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure you have valid Google Ads credentials")
        print("2. Check that google-ads package is installed")
        print("3. Verify your API access is working")

if __name__ == "__main__":
    debug_api_v21_fields()
