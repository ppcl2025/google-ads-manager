#!/usr/bin/env python3
"""
Research script to find the correct API v20 approach for applying shared negative keywords lists.
"""

from google.ads.googleads.client import GoogleAdsClient

def research_negative_keywords_approach():
    """Research the correct API v20 approach for shared negative keywords."""
    try:
        # Load the client
        client = GoogleAdsClient.load_from_storage(path="/Users/jer89/google-ads-manager/google-ads.yaml")
        
        # MCC Customer ID
        mcc_customer_id = "5022887746"  # Your MCC ID without hyphens
        
        google_ads_service = client.get_service("GoogleAdsService")
        
        print("🔍 Researching API v20 shared negative keywords approaches...")
        print("=" * 60)
        
        # Approach 1: Check if there's a campaign_negative_keyword_shared_set field
        print("\n📋 Approach 1: Checking for campaign_negative_keyword_shared_set field")
        print("-" * 40)
        
        try:
            query1 = """
                SELECT
                  campaign.id,
                  campaign.name,
                  campaign_negative_keyword_shared_set.shared_set
                FROM campaign_negative_keyword_shared_set
                LIMIT 1
            """
            response1 = google_ads_service.search(
                customer_id=mcc_customer_id,
                query=query1
            )
            print("✅ campaign_negative_keyword_shared_set field exists")
            for row in response1:
                print(f"   Found: {row}")
        except Exception as e:
            print(f"❌ campaign_negative_keyword_shared_set not found: {str(e)}")
        
        # Approach 2: Check for shared_set_negative_keyword field
        print("\n📋 Approach 2: Checking for shared_set_negative_keyword field")
        print("-" * 40)
        
        try:
            query2 = """
                SELECT
                  shared_set_negative_keyword.shared_set,
                  shared_set_negative_keyword.keyword.text,
                  shared_set_negative_keyword.keyword.match_type
                FROM shared_set_negative_keyword
                LIMIT 5
            """
            response2 = google_ads_service.search(
                customer_id=mcc_customer_id,
                query=query2
            )
            print("✅ shared_set_negative_keyword field exists")
            for row in response2:
                print(f"   Found: {row}")
        except Exception as e:
            print(f"❌ shared_set_negative_keyword not found: {str(e)}")
        
        # Approach 3: Check for campaign_shared_set field
        print("\n📋 Approach 3: Checking for campaign_shared_set field")
        print("-" * 40)
        
        try:
            query3 = """
                SELECT
                  campaign.id,
                  campaign.name,
                  campaign_shared_set.shared_set
                FROM campaign_shared_set
                LIMIT 5
            """
            response3 = google_ads_service.search(
                customer_id=mcc_customer_id,
                query=query3
            )
            print("✅ campaign_shared_set field exists")
            for row in response3:
                print(f"   Campaign ID: {row.campaign.id}")
                print(f"   Campaign Name: {row.campaign.name}")
                print(f"   Shared Set: {row.campaign_shared_set.shared_set}")
                print("   ---")
        except Exception as e:
            print(f"❌ campaign_shared_set not found: {str(e)}")
        
        # Approach 3b: Check for campaign_shared_set with specific shared set
        print("\n📋 Approach 3b: Checking for campaign_shared_set with PPCL List")
        print("-" * 40)
        
        try:
            query3b = """
                SELECT
                  campaign.id,
                  campaign.name,
                  campaign_shared_set.shared_set
                FROM campaign_shared_set
                WHERE campaign_shared_set.shared_set = 'customers/5022887746/sharedSets/11404993599'
                LIMIT 5
            """
            response3b = google_ads_service.search(
                customer_id=mcc_customer_id,
                query=query3b
            )
            print("✅ Found campaigns using PPCL List")
            for row in response3b:
                print(f"   Campaign ID: {row.campaign.id}")
                print(f"   Campaign Name: {row.campaign.name}")
                print(f"   Shared Set: {row.campaign_shared_set.shared_set}")
                print("   ---")
        except Exception as e:
            print(f"❌ No campaigns found using PPCL List: {str(e)}")
        
        # Approach 4: Check for ad_group_negative_keyword_shared_set field
        print("\n📋 Approach 4: Checking for ad_group_negative_keyword_shared_set field")
        print("-" * 40)
        
        try:
            query4 = """
                SELECT
                  ad_group.id,
                  ad_group.name,
                  ad_group_negative_keyword_shared_set.shared_set
                FROM ad_group_negative_keyword_shared_set
                LIMIT 1
            """
            response4 = google_ads_service.search(
                customer_id=mcc_customer_id,
                query=query4
            )
            print("✅ ad_group_negative_keyword_shared_set field exists")
            for row in response4:
                print(f"   Found: {row}")
        except Exception as e:
            print(f"❌ ad_group_negative_keyword_shared_set not found: {str(e)}")
        
        # Approach 5: Check what fields are available on Campaign
        print("\n📋 Approach 5: Checking Campaign fields that might contain shared sets")
        print("-" * 40)
        
        try:
            query5 = """
                SELECT
                  campaign.id,
                  campaign.name,
                  campaign.status,
                  campaign.advertising_channel_type
                FROM campaign
                LIMIT 1
            """
            response5 = google_ads_service.search(
                customer_id=mcc_customer_id,
                query=query5
            )
            print("✅ Campaign query works, checking for shared set related fields...")
            
            # Try to get campaign details to see available fields
            campaign_service = client.get_service("CampaignService")
            campaign_type = client.get_type("Campaign")
            
            # Look for fields that might be related to shared sets
            shared_set_related_fields = []
            for field in dir(campaign_type):
                if 'shared' in field.lower() or 'set' in field.lower():
                    shared_set_related_fields.append(field)
            
            print(f"   Shared set related fields: {shared_set_related_fields}")
            
        except Exception as e:
            print(f"❌ Campaign query failed: {str(e)}")
        
        # Approach 6: Check if there's a direct shared_set field on Campaign
        print("\n📋 Approach 6: Checking for direct shared_set field on Campaign")
        print("-" * 40)
        
        try:
            query6 = """
                SELECT
                  campaign.id,
                  campaign.name,
                  campaign.shared_set
                FROM campaign
                LIMIT 1
            """
            response6 = google_ads_service.search(
                customer_id=mcc_customer_id,
                query=query6
            )
            print("✅ Campaign.shared_set field exists")
            for row in response6:
                print(f"   Campaign ID: {row.campaign.id}")
                print(f"   Campaign Name: {row.campaign.name}")
                print(f"   Shared Set: {row.campaign.shared_set}")
        except Exception as e:
            print(f"❌ Campaign.shared_set field not found: {str(e)}")
        
        print("\n" + "=" * 60)
        print("🎯 RESEARCH SUMMARY:")
        print("Based on the results above, we'll determine the correct approach")
        print("for applying shared negative keywords lists in API v20.")
        
    except Exception as e:
        print(f"💥 Error: {str(e)}")

if __name__ == "__main__":
    research_negative_keywords_approach() 