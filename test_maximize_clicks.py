#!/usr/bin/env python3
"""
Test script to figure out how to set Maximize Clicks bidding strategy
in the Google Ads API.
"""

import os
from google.ads.googleads.client import GoogleAdsClient

def test_maximize_clicks_approaches():
    """Test different approaches to set Maximize Clicks bidding strategy."""
    
    print("🔍 Testing Maximize Clicks Bidding Strategy Approaches")
    print("=" * 60)
    
    try:
        # Create a minimal client just to inspect types
        # We don't need valid credentials, just need to access the type system
        config = {
            "client_id": "test",
            "client_secret": "test",
            "developer_token": "test",
            "refresh_token": "test",
            "use_proto_plus": True
        }
        client = GoogleAdsClient.load_from_dict(config)
        print("✅ Client created for type inspection")
        print()
        
        # Get a campaign type to inspect
        campaign_operation = client.get_type("CampaignOperation")
        campaign = campaign_operation.create
        
        print("📋 Inspecting Campaign object for bidding strategy fields:")
        print("-" * 60)
        
        # List all attributes that contain 'click', 'bid', or 'maximize'
        relevant_attrs = []
        for attr in dir(campaign):
            if not attr.startswith('_'):
                attr_lower = attr.lower()
                if any(keyword in attr_lower for keyword in ['click', 'bid', 'maximize', 'strategy']):
                    relevant_attrs.append(attr)
        
        print(f"\n🔎 Found {len(relevant_attrs)} relevant attributes:")
        for attr in sorted(relevant_attrs):
            print(f"  - {attr}")
        
        print("\n" + "=" * 60)
        print("🧪 Testing Approach 1: Direct field access")
        print("-" * 60)
        try:
            # Test if maximize_clicks field exists
            if hasattr(campaign, 'maximize_clicks'):
                print("✅ 'maximize_clicks' field EXISTS on Campaign")
                
                # Try to access it
                mc_field = campaign.maximize_clicks
                print(f"✅ Field accessed successfully: {type(mc_field)}")
                print(f"   Field type: {mc_field.__class__.__name__}")
                
                # Check if it has any subfields
                mc_attrs = [a for a in dir(mc_field) if not a.startswith('_')]
                print(f"   Available methods/fields: {mc_attrs[:10]}...")
                
            else:
                print("❌ 'maximize_clicks' field DOES NOT EXIST on Campaign")
        except Exception as e:
            print(f"❌ Error accessing maximize_clicks: {e}")
        
        print("\n" + "=" * 60)
        print("🧪 Testing Approach 2: Check for bidding strategy types")
        print("-" * 60)
        
        # Try to get different bidding strategy types
        strategies_to_test = [
            "MaximizeClicks",
            "common.MaximizeClicks", 
            "resources.MaximizeClicks",
            "ManualCpc",
            "TargetCpa",
            "MaximizeConversions"
        ]
        
        for strategy_name in strategies_to_test:
            try:
                strategy_type = client.get_type(strategy_name)
                print(f"✅ Type '{strategy_name}' EXISTS: {strategy_type}")
            except Exception as e:
                print(f"❌ Type '{strategy_name}' does not exist: {str(e)[:80]}")
        
        print("\n" + "=" * 60)
        print("🧪 Testing Approach 3: Inspect campaign bidding fields")
        print("-" * 60)
        
        # Check what bidding-related fields are available
        if hasattr(campaign, 'bidding_strategy'):
            print(f"✅ campaign.bidding_strategy exists: {type(campaign.bidding_strategy)}")
        else:
            print("❌ campaign.bidding_strategy does not exist")
        
        if hasattr(campaign, 'bidding_strategy_type'):
            print(f"✅ campaign.bidding_strategy_type exists")
        else:
            print("❌ campaign.bidding_strategy_type does not exist")
            
        if hasattr(campaign, 'manual_cpc'):
            print(f"✅ campaign.manual_cpc exists: {type(campaign.manual_cpc)}")
        else:
            print("❌ campaign.manual_cpc does not exist")
        
        print("\n" + "=" * 60)
        print("✅ Diagnostic Complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_maximize_clicks_approaches()

