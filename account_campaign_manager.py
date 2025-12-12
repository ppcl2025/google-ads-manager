"""
Account and Campaign Creation Manager
Extracted from google-ads-manager for integration with GAds-Claude
"""

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from typing import Optional
from datetime import datetime
import streamlit as st
import logging

logger = logging.getLogger(__name__)

# US Timezones for sub-account creation
US_TIMEZONES = {
    "America/New_York": "Eastern Time (ET)",
    "America/Chicago": "Central Time (CT)",
    "America/Denver": "Mountain Time (MT)",
    "America/Los_Angeles": "Pacific Time (PT)",
    "America/Phoenix": "Arizona Time (MST)",
    "America/Anchorage": "Alaska Time (AKST)",
    "Pacific/Honolulu": "Hawaii Time (HST)"
}

def get_sub_accounts(client: GoogleAdsClient, mcc_customer_id: str) -> list[dict]:
    """Fetch all direct, active sub-accounts under the MCC account using GAQL."""
    try:
        ga_service = client.get_service("GoogleAdsService")
        
        # Convert MCC ID to numeric format (remove dashes)
        mcc_customer_id_numeric = mcc_customer_id.replace("-", "")
        
        query = """
            SELECT
                customer_client.id,
                customer_client.descriptive_name,
                customer_client.manager,
                customer_client.test_account,
                customer_client.currency_code,
                customer_client.time_zone
            FROM customer_client
            WHERE customer_client.level <= 1
            AND customer_client.status = 'ENABLED'
        """
        
        response = ga_service.search(customer_id=mcc_customer_id_numeric, query=query)
        
        sub_accounts = []
        for row in response:
            customer_id = str(row.customer_client.id)
            # Format customer ID with dashes
            formatted_id = f"{customer_id[:3]}-{customer_id[3:6]}-{customer_id[6:]}"
            
            sub_accounts.append({
                'id': formatted_id,
                'name': row.customer_client.descriptive_name,
                'display': f"{row.customer_client.descriptive_name} ({formatted_id})",
                'currency': row.customer_client.currency_code,
                'timezone': row.customer_client.time_zone
            })
        
        sub_accounts.sort(key=lambda x: x['name'])
        return sub_accounts
        
    except GoogleAdsException as ex:
        error_msg = ex.error.message() if hasattr(ex.error, 'message') else str(ex)
        raise Exception(f"Error fetching sub-accounts: {error_msg}")

def create_sub_account(client: GoogleAdsClient, mcc_customer_id: str, account_name: str, 
                      currency_code: str, time_zone: str) -> Optional[str]:
    """Create a new sub-account under MCC.
    Sub-accounts are created without MCC payment profile linking so clients can set up their own payment methods.
    """
    try:
        customer_service = client.get_service("CustomerService")
        customer = client.get_type("Customer")
        customer.descriptive_name = account_name
        customer.currency_code = currency_code
        customer.time_zone = time_zone
        customer.tracking_url_template = ""
        customer.manager = False  # Prevents automatic MCC payment profile linking
        customer.test_account = False
        
        # Create the customer client
        response = customer_service.create_customer_client(
            customer_id=mcc_customer_id.replace("-", ""),
            customer_client=customer
        )
        
        # Extract the new customer ID from the response
        new_customer_id = None
        try:
            if hasattr(response, 'customer_client') and hasattr(response.customer_client, 'id'):
                new_customer_id = response.customer_client.id
            elif hasattr(response, 'resource_name'):
                new_customer_id = response.resource_name.split('/')[-1]
            elif hasattr(response, 'results') and len(response.results) > 0:
                new_customer_id = response.results[0].resource_name.split('/')[-1]
            else:
                new_customer_id = str(response).split('customers/')[-1].split('/')[0]
        except Exception as parse_error:
            logger.warning(f"Could not parse response structure: {parse_error}")
            return "UNKNOWN"
        
        if new_customer_id and new_customer_id != "UNKNOWN":
            # Format customer ID with dashes
            formatted_id = f"{new_customer_id[:3]}-{new_customer_id[3:6]}-{new_customer_id[6:]}"
            return formatted_id
        
        return new_customer_id
        
    except Exception as ex:
        error_msg = ex.error.message() if hasattr(ex.error, 'message') else str(ex)
        raise Exception(f"Error creating sub-account: {error_msg}")

def create_campaign(client: GoogleAdsClient, customer_id: str, campaign_name: str, 
                   budget_amount: float) -> Optional[str]:
    """Create a campaign with daily budget and Maximize Clicks bidding strategy."""
    try:
        campaign_service = client.get_service("CampaignService")
        campaign_budget_service = client.get_service("CampaignBudgetService")
        
        customer_id_numeric = customer_id.replace("-", "")
        
        # Generate unique budget name with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        budget_name = f"Budget for {campaign_name} - {timestamp}"
        
        # Create campaign budget operation
        budget_operation = client.get_type("CampaignBudgetOperation")
        campaign_budget = budget_operation.create
        campaign_budget.name = budget_name
        campaign_budget.amount_micros = int(float(budget_amount) * 1000000)  # Convert to micros
        campaign_budget.delivery_method = client.enums.BudgetDeliveryMethodEnum.STANDARD
        
        # Ensure budget is not shared (campaign-specific)
        if hasattr(campaign_budget, 'explicitly_shared'):
            campaign_budget.explicitly_shared = False
        elif hasattr(campaign_budget, 'is_shared'):
            campaign_budget.is_shared = False
        
        budget_response = campaign_budget_service.mutate_campaign_budgets(
            customer_id=customer_id_numeric, operations=[budget_operation]
        )
        budget_resource_name = budget_response.results[0].resource_name
        
        # Create campaign operation
        campaign_operation = client.get_type("CampaignOperation")
        campaign = campaign_operation.create
        campaign.name = campaign_name
        campaign.status = client.enums.CampaignStatusEnum.PAUSED  # Set to PAUSED
        campaign.campaign_budget = budget_resource_name
        campaign.advertising_channel_type = client.enums.AdvertisingChannelTypeEnum.SEARCH
        
        # Set Maximize Clicks bidding strategy using target_spend
        try:
            campaign.target_spend = client.get_type("TargetSpend")
        except Exception as bidding_error:
            logger.warning(f"Failed to set Maximize Clicks bidding strategy: {bidding_error}")
            raise
        
        # Hardcoded shared negative keywords list - PPCL List
        ppcl_negative_list_id = "11404993599"
        
        # Configure network settings
        try:
            campaign.network_settings.target_google_search = True
            campaign.network_settings.target_search_network = False
            campaign.network_settings.target_content_network = False
            campaign.network_settings.target_partner_search_network = False
        except Exception as network_error:
            logger.warning(f"Could not configure network settings: {network_error}")
        
        # Configure location targeting behavior to "Presence Only"
        try:
            campaign.geo_target_type_setting.positive_geo_target_type = client.enums.PositiveGeoTargetTypeEnum.PRESENCE
            campaign.geo_target_type_setting.negative_geo_target_type = client.enums.NegativeGeoTargetTypeEnum.PRESENCE
        except Exception as geo_error:
            logger.warning(f"Could not configure location targeting: {geo_error}")
        
        campaign.start_date = datetime.now().strftime("%Y-%m-%d")
        
        # Set EU political advertising field (required in API v21)
        try:
            eu_field_names = [
                'contains_eu_political_advertising',
                'eu_political_advertising',
                'eu_political_content',
                'political_advertising',
                'political_content'
            ]
            
            for field_name in eu_field_names:
                if hasattr(campaign, field_name):
                    setattr(campaign, field_name, client.enums.EuPoliticalAdvertisingStatusEnum.DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING)
                    break
        except Exception as eu_error:
            logger.warning(f"Failed to set EU political advertising field: {eu_error}")
        
        # Create the campaign
        response = campaign_service.mutate_campaigns(
            customer_id=customer_id_numeric, operations=[campaign_operation]
        )
        campaign_id = response.results[0].resource_name.split("/")[-1]
        
        # Apply shared negative keywords list to the campaign
        try:
            campaign_shared_set_service = client.get_service("CampaignSharedSetService")
            campaign_shared_set_operation = client.get_type("CampaignSharedSetOperation")
            campaign_shared_set = campaign_shared_set_operation.create
            campaign_shared_set.campaign = f"customers/{customer_id_numeric}/campaigns/{campaign_id}"
            campaign_shared_set.shared_set = f"customers/{customer_id_numeric}/sharedSets/{ppcl_negative_list_id}"
            
            shared_set_response = campaign_shared_set_service.mutate_campaign_shared_sets(
                customer_id=customer_id_numeric,
                operations=[campaign_shared_set_operation]
            )
        except Exception as negative_error:
            logger.warning(f"Could not apply negative keywords list: {negative_error}")
        
        return campaign_id
        
    except Exception as ex:
        error_msg = ex.error.message() if hasattr(ex.error, 'message') else str(ex)
        raise Exception(f"Error creating campaign: {error_msg}")

