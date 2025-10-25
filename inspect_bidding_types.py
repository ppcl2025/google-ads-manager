#!/usr/bin/env python3
"""
Simple script to inspect what bidding strategy types and fields are available
in the installed Google Ads API version.
"""

def inspect_bidding_strategies():
    print("🔍 Inspecting Google Ads API Bidding Strategy Types")
    print("=" * 70)
    
    try:
        # Try to import the types module directly
        from google.ads.googleads import client as googleads_client
        
        # Get version
        try:
            import google.ads.googleads
            version = google.ads.googleads.__version__
            print(f"📦 google-ads-python version: {version}")
        except:
            print("📦 google-ads-python version: Unable to determine")
        
        print()
        
        # Try to inspect campaign proto
        print("🔎 Attempting to inspect Campaign message type...")
        print("-" * 70)
        
        try:
            # Import the protobuf messages
            from google.ads.googleads.v18 import types
            print("✅ Successfully imported v18 types")
            
            # Check Campaign type
            campaign = types.Campaign()
            print(f"✅ Campaign type loaded: {type(campaign)}")
            
            # List all fields that might be related to bidding
            print("\n📋 Bidding-related fields on Campaign:")
            bidding_fields = []
            for field_name in dir(campaign):
                if not field_name.startswith('_'):
                    lower_name = field_name.lower()
                    if any(kw in lower_name for kw in ['click', 'bid', 'maximize', 'cpc', 'strategy']):
                        bidding_fields.append(field_name)
            
            for field in sorted(bidding_fields):
                print(f"  ✓ {field}")
            
            # Test if maximize_clicks exists
            print("\n🧪 Testing 'maximize_clicks' field:")
            if hasattr(campaign, 'maximize_clicks'):
                print("  ✅ 'maximize_clicks' field EXISTS")
                mc = campaign.maximize_clicks
                print(f"     Type: {type(mc)}")
                print(f"     Class: {mc.__class__.__name__}")
            else:
                print("  ❌ 'maximize_clicks' field DOES NOT EXIST")
            
            # Test manual_cpc for comparison
            print("\n🧪 Testing 'manual_cpc' field (for comparison):")
            if hasattr(campaign, 'manual_cpc'):
                print("  ✅ 'manual_cpc' field EXISTS")
                manual = campaign.manual_cpc
                print(f"     Type: {type(manual)}")
                print(f"     Class: {manual.__class__.__name__}")
            else:
                print("  ❌ 'manual_cpc' field DOES NOT EXIST")
                
        except ImportError as ie:
            print(f"❌ Could not import v18 types: {ie}")
            print("\n Trying other versions...")
            
            # Try v17, v16, etc.
            for version_num in ['v17', 'v16', 'v15', 'v14']:
                try:
                    exec(f"from google.ads.googleads.{version_num} import types")
                    print(f"✅ Successfully imported {version_num} types")
                    break
                except ImportError:
                    print(f"❌ {version_num} not available")
        
        print("\n" + "=" * 70)
        print("✅ Inspection Complete!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error during inspection: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_bidding_strategies()

