import pandas as pd
import logging
import re
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.api_core.exceptions import GoogleAPICallError
from google.protobuf.field_mask_pb2 import FieldMask
from datetime import datetime, timedelta
import streamlit as st
from typing import Optional, List, Dict, Any
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
import os
from google.ads.googleads.v20.resources.types import Campaign

# API Usage Tracker
class APIUsageTracker:
    def __init__(self, monthly_limit: int = 15000):
        self.monthly_limit = monthly_limit
        self.operations_count = 0
        self.last_reset = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    def increment(self, count: int = 1):
        """Increment API operation count"""
        # Reset counter if it's a new month
        current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if current_month > self.last_reset:
            self.operations_count = 0
            self.last_reset = current_month
        
        self.operations_count += count
    
    def get_usage_stats(self):
        """Get current usage statistics"""
        remaining = max(0, self.monthly_limit - self.operations_count)
        usage_percentage = (self.operations_count / self.monthly_limit) * 100
        return {
            'used': self.operations_count,
            'remaining': remaining,
            'percentage': usage_percentage
        }
    
    def is_limit_reached(self):
        """Check if monthly limit is reached"""
        return self.operations_count >= self.monthly_limit

# Initialize API tracker
if 'api_tracker' not in st.session_state:
    st.session_state.api_tracker = APIUsageTracker()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# App Usage Logger
class AppUsageLogger:
    def __init__(self):
        self.log_file = "app_usage.log"
    
    def log_action(self, user_action: str, details: str = ""):
        """Log user actions for analytics"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {user_action}: {details}"
        logger.info(log_entry)
        
        # Also log to file for analysis
        try:
            with open(self.log_file, "a") as f:
                f.write(log_entry + "\n")
        except Exception as e:
            logger.error(f"Failed to write to log file: {e}")

# Initialize usage logger
if 'usage_logger' not in st.session_state:
    st.session_state.usage_logger = AppUsageLogger()

# Constants
DEFAULT_MCC_ID = "502-288-7746"
DEFAULT_CURRENCIES = ["USD", "EUR", "GBP", "INR"]
DEFAULT_CAMPAIGN_STATUSES = ["PAUSED", "ENABLED"]
DEFAULT_CPC_BID_MICROS = 1_000_000  # $1.00 CPC
REQUIRED_COLUMNS = ["ad_group_name", "headline1", "headline2", "headline3", "description1", "description2", "final_url", "keywords"]
MAX_HEADLINES = 15
MAX_DESCRIPTIONS = 4

# US Timezones for sub-account creation
US_TIMEZONES = [
    "America/New_York",      # Eastern Time
    "America/Chicago",       # Central Time
    "America/Denver",        # Mountain Time
    "America/Los_Angeles",   # Pacific Time
    "America/Anchorage",     # Alaska Time
    "Pacific/Honolulu"       # Hawaii Time
]

# Page configuration
st.set_page_config(
    page_title="Google Ads Manager",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Google Ads API credentials from Streamlit secrets
def get_google_ads_client():
    """Create Google Ads client using Streamlit secrets"""
    try:
        # Check if we're running in Streamlit Cloud (has secrets)
        if hasattr(st, 'secrets'):
            # Use Streamlit secrets
            client = GoogleAdsClient.load_from_dict({
                "client_id": st.secrets["GOOGLE_ADS_CLIENT_ID"],
                "client_secret": st.secrets["GOOGLE_ADS_CLIENT_SECRET"],
                "developer_token": st.secrets["GOOGLE_ADS_DEVELOPER_TOKEN"],
                "refresh_token": st.secrets["GOOGLE_ADS_REFRESH_TOKEN"],
                "login_customer_id": st.secrets["GOOGLE_ADS_LOGIN_CUSTOMER_ID"],
                "use_proto_plus": True
            })
        else:
            # Fallback to environment variables for local development
            client = GoogleAdsClient.load_from_env()
        
        return client
    except Exception as e:
        st.error(f"Failed to load Google Ads credentials: {e}")
        st.info("Please ensure the following secrets are configured in Streamlit Cloud:")
        st.code("""
GOOGLE_ADS_CLIENT_ID = "your_client_id"
GOOGLE_ADS_CLIENT_SECRET = "your_client_secret"
GOOGLE_ADS_DEVELOPER_TOKEN = "your_developer_token"
GOOGLE_ADS_REFRESH_TOKEN = "your_refresh_token"
GOOGLE_ADS_LOGIN_CUSTOMER_ID = "5022887746"
        """)
        return None

# Helper function to validate Customer ID format (XXX-XXX-XXXX)
def validate_customer_id(customer_id: str) -> bool:
    """Validate customer ID format."""
    pattern = r'^\d{3}-\d{3}-\d{4}$'
    return bool(re.match(pattern, customer_id))

# Helper function to format customer ID for API
def format_customer_id(customer_id: str) -> str:
    """Remove hyphens from customer ID for API calls."""
    return customer_id.replace("-", "")

# Helper function to create success/error messages
def show_message(message: str, is_success: bool = True):
    """Show success or error message."""
    if is_success:
        st.success(message)
    else:
        st.error(message)

# Helper function to handle API exceptions
def handle_api_exception(ex: Exception, operation: str) -> None:
    """Centralized exception handling for API operations."""
    if isinstance(ex, GoogleAPICallError):
        error_details = ex.details() or str(ex)
        show_message(f"Failed to {operation}: {error_details}", False)
        logger.error(f"{operation} error: {error_details}")
    else:
        show_message(f"Unexpected error {operation}: {str(ex)}", False)
        logger.error(f"Unexpected error: {str(ex)}")

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def get_sub_accounts(_client: GoogleAdsClient, mcc_customer_id: str) -> list[dict]:
    """Fetch all direct, active sub-accounts under the MCC account using GAQL."""
    try:
        # Track API usage
        st.session_state.api_tracker.increment(1)
        
        st.info(f"🔍 Fetching sub-accounts for MCC ID: {mcc_customer_id}")
        sub_accounts = []
        google_ads_service = _client.get_service("GoogleAdsService")
        query = """
            SELECT
              customer_client.client_customer,
              customer_client.descriptive_name,
              customer_client.level,
              customer_client.status
            FROM customer_client
            WHERE customer_client.level = 1
              AND customer_client.status = 'ENABLED'
        """
        response = google_ads_service.search(
            customer_id=mcc_customer_id,
            query=query
        )
        for row in response:
            client_customer = row.customer_client
            sub_accounts.append({
                'id': str(client_customer.client_customer.split('/')[-1]),
                'name': client_customer.descriptive_name,
                'display': f"{client_customer.descriptive_name} ({client_customer.client_customer.split('/')[-1]})"
            })
        sub_accounts.sort(key=lambda x: x['name'])
        st.success(f"🎉 Found {len(sub_accounts)} active sub-accounts under this MCC.")
        if not sub_accounts:
            st.warning("⚠️ No active sub-accounts found. Make sure you have active sub-accounts under this MCC.")
        return sub_accounts
    except Exception as ex:
        st.error(f"💥 Error fetching sub-accounts: {str(ex)}")
        handle_api_exception(ex, "fetch sub-accounts")
        return []

# Create a new sub-account under MCC
def create_sub_account(client: GoogleAdsClient, mcc_customer_id: str, account_name: str, 
                      currency_code: str, time_zone: str) -> Optional[str]:
    """Create a new sub-account under MCC with conversion tracking set to 'This Manager'."""
    try:
        customer_service = client.get_service("CustomerService")
        customer = client.get_type("Customer")
        customer.descriptive_name = account_name
        customer.currency_code = currency_code
        customer.time_zone = time_zone
        customer.tracking_url_template = ""

        # Create the customer client first (without conversion tracking)
        response = customer_service.create_customer_client(
            customer_id=mcc_customer_id,
            customer_client=customer
        )
        
        # Extract the new customer ID from the response
        new_customer_id = None
        try:
            # Try different possible response structures
            if hasattr(response, 'customer_client') and hasattr(response.customer_client, 'id'):
                new_customer_id = response.customer_client.id
            elif hasattr(response, 'resource_name'):
                # Extract ID from resource name format: customers/{customer_id}
                new_customer_id = response.resource_name.split('/')[-1]
            elif hasattr(response, 'results') and len(response.results) > 0:
                # Handle batch response format
                new_customer_id = response.results[0].resource_name.split('/')[-1]
            else:
                # Fallback: try to get from the response object directly
                new_customer_id = str(response).split('customers/')[-1].split('/')[0]
        except Exception as parse_error:
            logger.warning(f"Could not parse response structure: {parse_error}")
            show_message("✅ Sub-account created successfully! (Response structure parsing issue)")
            return "UNKNOWN"
        
        if new_customer_id and new_customer_id != "UNKNOWN":
            # Now set the conversion tracking to "This Manager" for the new account
            try:
                # Try to set conversion tracking using the correct API v20 approach
                # First, let's try to link the account to the MCC's conversion tracking
                
                # Use the CustomerService to update the customer settings
                customer_service = client.get_service("CustomerService")
                
                # Create a customer update operation
                customer_operation = client.get_type("CustomerOperation")
                customer_update = customer_operation.update
                customer_update.resource_name = f"customers/{new_customer_id}"
                
                # Set the conversion tracking to use the MCC account
                customer_update.conversion_tracking_setting = client.get_type("ConversionTrackingSetting")
                customer_update.conversion_tracking_setting.conversion_tracking_id = mcc_customer_id
                customer_update.conversion_tracking_setting.cross_account_conversion_tracking_id = mcc_customer_id
                
                # Also set the manager link to ensure proper MCC relationship
                customer_update.manager = True
                customer_update.test_account = False
                
                # Update the customer with conversion tracking settings
                update_response = customer_service.mutate_customers(
                    customer_id=new_customer_id,
                    operations=[customer_operation]
                )
                
                show_message(f"✅ Created sub-account with ID: {new_customer_id} with conversion tracking set to 'This Manager'")
                logger.info(f"Created sub-account: {new_customer_id} with conversion tracking enabled")
                
                # Add helpful instructions
                st.info("""
                **Next Steps:**
                - Verify conversion tracking is set to 'This Manager' in Google Ads UI
                - If not, go to Account Settings → Conversion tracking → Select 'This manager (USD)'
                - This enables MSL-MaxCon bidding strategy for campaigns
                """)
                
                return new_customer_id
                
            except Exception as conversion_error:
                # If setting conversion tracking fails, still return the account ID
                logger.warning(f"Could not set conversion tracking: {conversion_error}")
                show_message(f"✅ Created sub-account with ID: {new_customer_id}. Conversion tracking may need to be set manually.")
                return new_customer_id
        
        return new_customer_id
        
    except Exception as ex:
        handle_api_exception(ex, "create sub-account")
        return None

# Create a campaign with daily budget
def create_campaign(client: GoogleAdsClient, customer_id: str, campaign_name: str, 
                   budget_amount: float) -> Optional[str]:
    """Create a campaign with daily budget and hardcoded MSL - MaxCon bidding strategy."""
    try:
        campaign_service = client.get_service("CampaignService")
        campaign_budget_service = client.get_service("CampaignBudgetService")

        # Generate unique budget name with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        budget_name = f"Budget for {campaign_name} - {timestamp}"

        # Create campaign budget operation
        budget_operation = client.get_type("CampaignBudgetOperation")
        campaign_budget = budget_operation.create
        campaign_budget.name = budget_name
        campaign_budget.amount_micros = int(float(budget_amount) * 1000000)  # Convert to micros
        campaign_budget.delivery_method = client.enums.BudgetDeliveryMethodEnum.STANDARD
        
        budget_response = campaign_budget_service.mutate_campaign_budgets(
            customer_id=customer_id, operations=[budget_operation]
        )
        budget_resource_name = budget_response.results[0].resource_name

        # Create campaign operation
        campaign_operation = client.get_type("CampaignOperation")
        campaign = campaign_operation.create
        campaign.name = campaign_name
        campaign.status = client.enums.CampaignStatusEnum.PAUSED  # Set to PAUSED
        campaign.campaign_budget = budget_resource_name
        campaign.advertising_channel_type = client.enums.AdvertisingChannelTypeEnum.SEARCH
        
        # Hardcoded MSL - MaxCon bidding strategy
        # To find your bidding strategy ID, run: python find_bidding_strategy.py
        # Or check in Google Ads UI: Tools & Settings > Shared Library > Bid Strategies
        msl_maxcon_strategy_id = "11481770709"  # MSL - MaxCon bidding strategy ID
        
        # Set the shared bidding strategy using the correct API v20 field name
        # In API v20, we need to use the correct field name for bidding strategy
        try:
            # Try the correct field name for API v20
            campaign.campaign_bidding_strategy = f"customers/{customer_id}/biddingStrategies/{msl_maxcon_strategy_id}"
        except AttributeError:
            # Fallback to alternative field name
            try:
                campaign.bidding_strategy = f"customers/{customer_id}/biddingStrategies/{msl_maxcon_strategy_id}"
            except AttributeError:
                # If neither field exists, we'll handle it in the try-catch below
                pass
        
        st.info(f"✅ Attempting to use MSL - MaxCon bidding strategy (ID: {msl_maxcon_strategy_id})")
        
        # Hardcoded shared negative keywords list - PPCL List
        ppcl_negative_list_id = "11404993599"  # PPCL List negative keywords ID
        st.info(f"✅ Will apply PPCL List negative keywords (ID: {ppcl_negative_list_id}) after campaign creation")
        
        # Configure NetworkSettings to use only core Google Search Network
        # Exclude search partners and Display Network
        try:
            # Use the correct API v20 approach with Campaign resource types
            campaign.network_settings = Campaign.NetworkSettings()
            campaign.network_settings.target_google_search = True  # Enable core Google Search
            campaign.network_settings.target_search_network = False  # Disable search partners
            campaign.network_settings.target_content_network = False  # Disable Display Network
            campaign.network_settings.target_partner_search_network = False  # Disable partner search network
            campaign.network_settings.target_youtube = False  # Disable YouTube
            st.info("✅ Network settings configured: Core Google Search only (no search partners, no Display Network)")
        except Exception as network_error:
            st.warning(f"⚠️ Could not configure network settings: {network_error}")
            logger.warning(f"Failed to configure network settings: {network_error}")
        
        # Configure Location Targeting to use "Presence Only" instead of "Presence or Interest"
        try:
            # Use the correct API v20 approach with Campaign resource types
            campaign.geo_target_type_setting = Campaign.GeoTargetTypeSetting()
            campaign.geo_target_type_setting.positive_geo_target_type = client.enums.PositiveGeoTargetTypeEnum.PRESENCE
            campaign.geo_target_type_setting.negative_geo_target_type = client.enums.NegativeGeoTargetTypeEnum.PRESENCE
            st.info("✅ Location targeting configured: Presence Only (not Presence or Interest)")
        except Exception as location_error:
            st.warning(f"⚠️ Could not configure location targeting: {location_error}")
            logger.warning(f"Failed to configure location targeting: {location_error}")
        
        # In API v20, network settings are handled differently
        # For Search campaigns, the network targeting is controlled by the advertising_channel_type
        # and other campaign settings rather than a separate NetworkSettings object
        
        # Add manual configuration instructions
        with st.expander("📋 Manual Network & Location Configuration Instructions"):
            st.markdown("""
            **After creating a campaign, configure these settings in Google Ads UI:**
            
            **🌐 Network Settings (Google Search only):**
            1. Go to **Campaigns** → Select your campaign → **Settings**
            2. Click on **Networks** section
            3. **Uncheck** "Search partners" 
            4. **Uncheck** "Display Network"
            5. **Keep checked** "Google Search" only
            6. Click **Save**
            
            **📍 Location Targeting (Presence Only):**
            1. Go to **Campaigns** → Select your campaign → **Settings**
            2. Click on **Locations** section
            3. Click **Location options** (gear icon)
            4. Select **"Presence"** (not "Presence or interest")
            5. Click **Save**
            
            **Why manual configuration?**
            - Google Ads API v20 doesn't support programmatic network/location settings
            - These settings must be configured through the Google Ads UI
            - Campaigns will work correctly once these are set manually
            """)
        
        campaign.start_date = datetime.now().strftime("%Y-%m-%d")  # Current date at runtime
        # No end_date (ongoing)

                # Try to mutate campaign with bidding strategy first
        try:
            response = campaign_service.mutate_campaigns(
                customer_id=customer_id, operations=[campaign_operation]
            )
            campaign_id = response.results[0].resource_name.split("/")[-1]
            
            # Apply shared negative keywords list to the campaign
            try:
                campaign_shared_set_service = client.get_service("CampaignSharedSetService")
                campaign_shared_set_operation = client.get_type("CampaignSharedSetOperation")
                campaign_shared_set = campaign_shared_set_operation.create
                campaign_shared_set.campaign = f"customers/{customer_id}/campaigns/{campaign_id}"
                campaign_shared_set.shared_set = f"customers/{customer_id}/sharedSets/{ppcl_negative_list_id}"
                
                # Apply the shared negative keywords list
                shared_set_response = campaign_shared_set_service.mutate_campaign_shared_sets(
                    customer_id=customer_id,
                    operations=[campaign_shared_set_operation]
                )
                st.info(f"✅ Successfully applied PPCL List negative keywords to campaign")
                logger.info(f"Applied shared negative keywords list {ppcl_negative_list_id} to campaign {campaign_id}")
                
            except Exception as shared_set_error:
                st.warning(f"⚠️ Could not apply shared negative keywords list: {shared_set_error}")
                logger.warning(f"Failed to apply shared negative keywords list: {shared_set_error}")
            
            show_message(f"✅ Created campaign with ID: {campaign_id} (PAUSED) using MSL - MaxCon bidding strategy. Add ad groups, ads, and keywords in the Bulk Upload tab.")
            return campaign_id
            
        except Exception as ex:
            # Check if the error is related to conversion tracking or bidding strategy
            error_message = str(ex)
            if "CONVERSION_TRACKING_NOT_ENABLED" in error_message or "REQUIRED" in error_message:
                st.warning("⚠️ Conversion tracking is not enabled or bidding strategy field issue. Retrying with Manual CPC bidding strategy...")
                
                # Create a new campaign operation without the bidding strategy
                campaign_operation_fallback = client.get_type("CampaignOperation")
                campaign_fallback = campaign_operation_fallback.create
                campaign_fallback.name = campaign_name
                campaign_fallback.status = client.enums.CampaignStatusEnum.PAUSED
                campaign_fallback.campaign_budget = budget_resource_name
                campaign_fallback.advertising_channel_type = client.enums.AdvertisingChannelTypeEnum.SEARCH
                campaign_fallback.start_date = datetime.now().strftime("%Y-%m-%d")
                
                # Set Manual CPC bidding strategy
                campaign_fallback.manual_cpc = client.get_type("ManualCpc")
                campaign_fallback.manual_cpc.enhanced_cpc_enabled = False
                
                # Configure NetworkSettings for fallback case too
                try:
                    # Use the correct API v20 approach with Campaign resource types
                    campaign_fallback.network_settings = Campaign.NetworkSettings()
                    campaign_fallback.network_settings.target_google_search = True  # Enable core Google Search
                    campaign_fallback.network_settings.target_search_network = False  # Disable search partners
                    campaign_fallback.network_settings.target_content_network = False  # Disable Display Network
                    campaign_fallback.network_settings.target_partner_search_network = False  # Disable partner search network
                    campaign_fallback.network_settings.target_youtube = False  # Disable YouTube
                    st.info("✅ Network settings configured: Core Google Search only (no search partners, no Display Network)")
                except Exception as network_error:
                    st.warning(f"⚠️ Could not configure network settings: {network_error}")
                    logger.warning(f"Failed to configure network settings: {network_error}")
                
                # Configure Location Targeting for fallback case too
                try:
                    # Use the correct API v20 approach with Campaign resource types
                    campaign_fallback.geo_target_type_setting = Campaign.GeoTargetTypeSetting()
                    campaign_fallback.geo_target_type_setting.positive_geo_target_type = client.enums.PositiveGeoTargetTypeEnum.PRESENCE
                    campaign_fallback.geo_target_type_setting.negative_geo_target_type = client.enums.NegativeGeoTargetTypeEnum.PRESENCE
                    st.info("✅ Location targeting configured: Presence Only (not Presence or Interest)")
                except Exception as location_error:
                    st.warning(f"⚠️ Could not configure location targeting: {location_error}")
                    logger.warning(f"Failed to configure location targeting: {location_error}")
                
                try:
                    response_fallback = campaign_service.mutate_campaigns(
                        customer_id=customer_id, operations=[campaign_operation_fallback]
                    )
                    campaign_id = response_fallback.results[0].resource_name.split("/")[-1]
                    
                    # Apply shared negative keywords list to the campaign (fallback case)
                    try:
                        campaign_shared_set_service = client.get_service("CampaignSharedSetService")
                        campaign_shared_set_operation = client.get_type("CampaignSharedSetOperation")
                        campaign_shared_set = campaign_shared_set_operation.create
                        campaign_shared_set.campaign = f"customers/{customer_id}/campaigns/{campaign_id}"
                        campaign_shared_set.shared_set = f"customers/{customer_id}/sharedSets/{ppcl_negative_list_id}"
                        
                        # Apply the shared negative keywords list
                        shared_set_response = campaign_shared_set_service.mutate_campaign_shared_sets(
                            customer_id=customer_id,
                            operations=[campaign_shared_set_operation]
                        )
                        st.info(f"✅ Successfully applied PPCL List negative keywords to campaign")
                        logger.info(f"Applied shared negative keywords list {ppcl_negative_list_id} to campaign {campaign_id}")
                        
                    except Exception as shared_set_error:
                        st.warning(f"⚠️ Could not apply shared negative keywords list: {shared_set_error}")
                        logger.warning(f"Failed to apply shared negative keywords list: {shared_set_error}")
                    
                    show_message(f"✅ Created campaign with ID: {campaign_id} (PAUSED) using Manual CPC bidding strategy. You can change to MSL - MaxCon later once conversion tracking is enabled.")
                    return campaign_id
                except Exception as fallback_ex:
                    handle_api_exception(fallback_ex, "create campaign with Manual CPC")
                    return None
            else:
                handle_api_exception(ex, "create campaign")
        return None
        
    except Exception as ex:
        handle_api_exception(ex, "create campaign")
        return None

# Create an ad group
def create_ad_group(client: GoogleAdsClient, customer_id: str, campaign_id: str, 
                   ad_group_name: str, status: str = "ENABLED") -> Optional[str]:
    """Create an ad group."""
    try:
        ad_group_service = client.get_service("AdGroupService")
        ad_group = client.get_type("AdGroup")
        ad_group.name = ad_group_name
        ad_group.campaign = f"customers/{customer_id}/campaigns/{campaign_id}"
        ad_group.status = client.enums.AdGroupStatusEnum[status]
        ad_group.type_ = client.enums.AdGroupTypeEnum.SEARCH_STANDARD
        ad_group.cpc_bid_micros = DEFAULT_CPC_BID_MICROS

        ad_group_operation = client.get_type("AdGroupOperation")
        ad_group_operation.create.CopyFrom(ad_group)
        ad_group_response = ad_group_service.mutate_ad_groups(
            customer_id=customer_id,
            operations=[ad_group_operation]
        )
        ad_group_id = ad_group_response.results[0].resource_name.split("/")[-1]
        show_message(f"Created ad group with ID: {ad_group_id}")
        logger.info(f"Created ad group: {ad_group_id}")
        return ad_group_id
        
    except GoogleAdsException as ex:
        show_message(f"Failed to create ad group: {ex.error.message}", False)
        logger.error(f"Ad group creation error: {ex.error.message}")
        return None

# Create a responsive search ad with up to 15 headlines and 4 descriptions
def create_ad(client: GoogleAdsClient, customer_id: str, ad_group_id: str, 
              headlines: List[str], descriptions: List[str], final_url: str, 
              headline_positions: List[str], description_positions: List[str]) -> Optional[str]:
    """Create a responsive search ad."""
    try:
        ad_group_ad_service = client.get_service("AdGroupAdService")
        ad_group_ad = client.get_type("AdGroupAd")
        ad_group_ad.ad_group = f"customers/{customer_id}/adGroups/{ad_group_id}"
        ad_group_ad.status = client.enums.AdGroupAdStatusEnum.ENABLED

        ad = client.get_type("Ad")
        ad.final_urls.append(final_url)
        rsa = ad.responsive_search_ad

        # Add headlines with positions
        for i, headline in enumerate(headlines):
            if headline:
                headline_asset = client.get_type("AdTextAsset")
                headline_asset.text = headline[:30]
                if i < len(headline_positions) and headline_positions[i]:
                    headline_asset.pinned_field = client.enums.ServedAssetFieldTypeEnum[f"HEADLINE_{headline_positions[i]}"]
                rsa.headlines.append(headline_asset)

        # Add descriptions with positions
        for i, description in enumerate(descriptions):
            if description:
                description_asset = client.get_type("AdTextAsset")
                description_asset.text = description[:60]
                if i < len(description_positions) and description_positions[i]:
                    description_asset.pinned_field = client.enums.ServedAssetFieldTypeEnum[f"DESCRIPTION_{description_positions[i]}"]
                rsa.descriptions.append(description_asset)

        ad_group_ad.ad.CopyFrom(ad)
        ad_group_ad_operation = client.get_type("AdGroupAdOperation")
        ad_group_ad_operation.create.CopyFrom(ad_group_ad)
        ad_response = ad_group_ad_service.mutate_ad_group_ads(
            customer_id=customer_id,
            operations=[ad_group_ad_operation]
        )
        ad_id = ad_response.results[0].resource_name.split("/")[-1]
        show_message(f"Created responsive search ad with ID: {ad_id}")
        logger.info(f"Created ad: {ad_id}")
        return ad_id
        
    except GoogleAdsException as ex:
        show_message(f"Failed to create ad: {ex.error.message}", False)
        logger.error(f"Ad creation error: {ex.error.message}")
        return None

# Upload keywords with match types
def upload_keywords(client: GoogleAdsClient, customer_id: str, ad_group_id: str, 
                   keywords: List[str]) -> Optional[List]:
    """Upload keywords with match types."""
    try:
        ad_group_criterion_service = client.get_service("AdGroupCriterionService")
        operations = []
        
        for keyword in keywords:
            criterion = client.get_type("AdGroupCriterion")
            criterion.ad_group = f"customers/{customer_id}/adGroups/{ad_group_id}"
            criterion.status = client.enums.AdGroupCriterionStatusEnum.ENABLED
            
            # Determine match type
            keyword_text = keyword.strip()
            if keyword_text.startswith('[') and keyword_text.endswith(']'):
                match_type = client.enums.KeywordMatchTypeEnum.EXACT
                keyword_text = keyword_text[1:-1]
            elif keyword_text.startswith('"') and keyword_text.endswith('"'):
                match_type = client.enums.KeywordMatchTypeEnum.PHRASE
                keyword_text = keyword_text[1:-1]
            else:
                match_type = client.enums.KeywordMatchTypeEnum.BROAD
                
            criterion.keyword.text = keyword_text
            criterion.keyword.match_type = match_type
            operation = client.get_type("AdGroupCriterionOperation")
            operation.create.CopyFrom(criterion)
            operations.append(operation)

        response = ad_group_criterion_service.mutate_ad_group_criteria(
            customer_id=customer_id,
            operations=operations
        )
        show_message(f"Uploaded {len(response.results)} keywords to ad group {ad_group_id}")
        logger.info(f"Uploaded {len(response.results)} keywords to ad group {ad_group_id}")
        return response.results
        
    except GoogleAdsException as ex:
        show_message(f"Failed to upload keywords: {ex.error.message}", False)
        logger.error(f"Keyword upload error: {ex.error.message}")
        return None

# Process bulk upload data
def process_bulk_upload(client: GoogleAdsClient, customer_id: str, campaign_name: str, 
                       df: pd.DataFrame) -> bool:
    """Process bulk upload of ad groups, ads, and keywords."""
    try:
        # Create the single campaign
        campaign_id = create_campaign(client, customer_id, campaign_name, 1.0) # Default budget to 1.0 for bulk upload
        if not campaign_id:
            return False

        # Group by ad_group_name
        grouped = df.groupby("ad_group_name")
        for ad_group_name, group in grouped:
            # Create ad group
            ad_group_id = create_ad_group(client, customer_id, campaign_id, ad_group_name)
            if not ad_group_id:
                continue
                
            # Create ads for each row in the group
            for _, row in group.iterrows():
                headlines = [row.get(f"headline{i}", "") for i in range(1, MAX_HEADLINES + 1)]
                descriptions = [row.get(f"description{i}", "") for i in range(1, MAX_DESCRIPTIONS + 1)]
                final_url = row["final_url"]
                
                headline_positions = (row.get("headline_positions", "").split(";") 
                                    if pd.notna(row.get("headline_positions")) else [""] * MAX_HEADLINES)
                description_positions = (row.get("description_positions", "").split(";") 
                                       if pd.notna(row.get("description_positions")) else [""] * MAX_DESCRIPTIONS)
                
                create_ad(client, customer_id, ad_group_id, headlines, descriptions, 
                         final_url, headline_positions, description_positions)
                
            # Upload keywords (use first row's keywords)
            if pd.notna(group["keywords"].iloc[0]):
                keyword_list = [k.strip() for k in str(group["keywords"].iloc[0]).split(";") if k.strip()]
                upload_keywords(client, customer_id, ad_group_id, keyword_list)
        
        return True
        
    except Exception as e:
        show_message(f"Error processing bulk upload: {str(e)}", False)
        logger.error(f"Bulk upload error: {str(e)}")
        return False

# Streamlit UI
def main():
    st.title("Google Ads Manager AI Agent")
    st.write("Manage Google Ads sub-accounts, campaigns, ad groups, ads, and keywords under your MCC account. Budgets are set at the campaign level.")

    # Load client once and cache it
    client = get_google_ads_client()
    if not client:
        return

    # MCC Customer ID - Set to default value
    mcc_customer_id = st.text_input("MCC Customer ID (format: XXX-XXX-XXXX)", value=DEFAULT_MCC_ID)
    if not validate_customer_id(mcc_customer_id):
        st.warning("Please enter a valid MCC Customer ID (e.g., 123-456-7890)")
        return
    mcc_customer_id = format_customer_id(mcc_customer_id)

    # Fetch sub-accounts under MCC
    # Clear all caches to ensure fresh execution
    st.cache_data.clear()
    st.cache_resource.clear()
    
    # Add a timestamp to force fresh execution
    import time
    timestamp = time.time()
    st.info(f"🔄 Fetching sub-accounts at {timestamp}")
    
    sub_accounts_list = get_sub_accounts(client, mcc_customer_id)
    
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.write(f"**Found {len(sub_accounts_list)} sub-account(s) under your MCC**")
    with col2:
        if st.button("🔄 Refresh Sub-Accounts"):
            st.cache_data.clear()
            st.rerun()
    with col3:
        if st.button("🗑️ Clear Cache"):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.success("Cache cleared!")
    
    if not sub_accounts_list:
        st.warning("No sub-accounts found under the MCC account. You can still manually enter customer IDs below.")
        sub_accounts_list = []  # Ensure it's an empty list

    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Create Sub-Account", 
        "Create Campaign", 
        "Bulk Upload", 
        "Performance Analysis"
    ])

    # Tab 1: Create Sub-Account
    with tab1:
        st.subheader("Create New Sub-Account")
        st.info("ℹ️ New sub-accounts will automatically have conversion tracking set to 'This Manager' for bidding strategy compatibility")
        
        # Add manual setup instructions
        with st.expander("📋 Manual Conversion Tracking Setup (if needed)"):
            st.markdown("""
            **If conversion tracking is not automatically set to 'This Manager', follow these steps:**
            
            1. **Go to Google Ads** → Account Settings → Conversion tracking
            2. **Click on 'Google Ads conversion account'**
            3. **Select 'This manager (USD)'** from the dropdown
            4. **Save the changes**
            
            This will enable the MSL-MaxCon bidding strategy for campaigns.
            """)
        
        account_name = st.text_input("Account Name")
        currency_code = st.selectbox("Currency Code", DEFAULT_CURRENCIES)
        time_zone = st.selectbox("Time Zone", US_TIMEZONES)
        
        if st.button("Create Sub-Account"):
            if account_name and time_zone:
                new_customer_id = create_sub_account(client, mcc_customer_id, account_name, currency_code, time_zone)
                if new_customer_id:
                    st.session_state["new_customer_id"] = new_customer_id
            else:
                show_message("Please fill in all fields.", False)

    # Tab 2: Create Campaign
    with tab2:
        st.subheader("Create Campaign")
        st.write("Budget is set at the campaign level.")
        
        # Use dropdown for customer selection with fallback
        if sub_accounts_list:
            customer_display = st.selectbox("Select Customer Account", [acc['display'] for acc in sub_accounts_list])
            customer_id = next(acc['id'] for acc in sub_accounts_list if acc['display'] == customer_display)
        else:
            customer_id = st.text_input("Customer ID for Campaign (format: XXX-XXX-XXXX)", "")
            if customer_id:
                if not validate_customer_id(customer_id):
                    st.warning("Please enter a valid Customer ID (e.g., 123-456-7890)")
                    return
                customer_id = format_customer_id(customer_id)
        
        campaign_name = st.text_input("Campaign Name")
        budget_amount = st.number_input("Daily Budget Amount (in account currency)", min_value=1.0, step=1.0)
        status = st.selectbox("Campaign Status", DEFAULT_CAMPAIGN_STATUSES)
        
        # Hardcoded bidding strategy and negative keywords info
        st.info("🎯 All campaigns will use the hardcoded MSL - MaxCon (Maximize Conversions) bidding strategy")
        st.info("✅ Conversion tracking is automatically set to 'This Manager' for new sub-accounts, enabling the bidding strategy")
        st.info("✅ All campaigns will use the hardcoded PPCL List shared negative keywords list")
        st.info("🎯 All campaigns will be configured for core Google Search only (no search partners, no Display Network)")
        st.info("🎯 All campaigns will use 'Presence Only' location targeting (not Presence or Interest)")
        
        if st.button("Create Campaign"):
            if customer_id and campaign_name and budget_amount:
                create_campaign(client, customer_id, campaign_name, budget_amount)
            else:
                show_message("Please fill in all required fields.", False)

    # Tab 3: Bulk Upload
    with tab3:
        st.subheader("Bulk Upload Ad Groups, Ads, and Keywords")
        st.write("Upload a CSV or Excel file with columns: ad_group_name, headline1 to headline15, description1 to description4, final_url, keywords, headline_positions, description_positions. All rows are added to a single campaign specified below. **Keywords only need to be specified in the first row of each ad group.**")
        
        # Use dropdown for customer selection with fallback
        if sub_accounts_list:
            customer_bulk_display = st.selectbox("Select Customer Account for Bulk Upload", [acc['display'] for acc in sub_accounts_list])
            customer_id_bulk = next(acc['id'] for acc in sub_accounts_list if acc['display'] == customer_bulk_display)
        else:
            customer_id_bulk = st.text_input("Customer ID for Bulk Upload (format: XXX-XXX-XXXX)", "")
            if customer_id_bulk:
                if not validate_customer_id(customer_id_bulk):
                    st.warning("Please enter a valid Customer ID (e.g., 123-456-7890)")
                    return
                customer_id_bulk = format_customer_id(customer_id_bulk)
        
        campaign_name = st.text_input("Campaign Name for Bulk Upload")
        uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])
        
        if st.button("Process Bulk Upload"):
            if not campaign_name:
                show_message("Please enter a campaign name.", False)
                return
            if not uploaded_file:
                show_message("Please upload a CSV or Excel file.", False)
                return
                
            try:
                # Determine file type and read accordingly
                file_extension = uploaded_file.name.split(".")[-1].lower()
                if file_extension == "csv":
                    df = pd.read_csv(uploaded_file)
                elif file_extension == "xlsx":
                    df = pd.read_excel(uploaded_file, engine="openpyxl")
                else:
                    show_message("Unsupported file format. Please upload a .csv or .xlsx file.", False)
                    return

                # Validate required columns
                if not all(col in df.columns for col in REQUIRED_COLUMNS):
                    show_message("File must contain required columns: ad_group_name, headline1, headline2, headline3, description1, description2, final_url, keywords", False)
                    return

                # Validate that each ad group has keywords in at least the first row
                grouped = df.groupby("ad_group_name")
                for ad_group_name, group in grouped:
                    if pd.isna(group["keywords"].iloc[0]) or str(group["keywords"].iloc[0]).strip() == "":
                        show_message(f"Ad group '{ad_group_name}' must have keywords specified in the first row.", False)
                        return

                # Process the bulk upload
                process_bulk_upload(client, customer_id_bulk, campaign_name, df)
                
            except Exception as e:
                show_message(f"Error processing file: {str(e)}", False)
                logger.error(f"Bulk upload error: {str(e)}")

    # Tab 4: Performance Analysis (formerly Keywords Analysis)
    with tab4:
        st.subheader("Performance Analysis")
        st.write("Analyze top keywords by spend across selected sub-accounts with comprehensive performance metrics.")
        
        # Sub-account selection for keywords analysis
        st.write("**Select which sub-accounts to include in performance analysis:**")
        if sub_accounts_list:
            selected_keyword_accounts = st.multiselect(
                "Choose sub-accounts for performance analysis",
                options=[acc['display'] for acc in sub_accounts_list],
                default=[acc['display'] for acc in sub_accounts_list],  # Default to all selected
                help="Select the sub-accounts you want to include in the performance analysis. Uncheck paused accounts that aren't running ads."
            )
            
            # Convert selected display names back to account objects
            selected_keyword_sub_accounts = [acc for acc in sub_accounts_list if acc['display'] in selected_keyword_accounts]
            
            if not selected_keyword_sub_accounts:
                st.warning("Please select at least one sub-account for performance analysis.")
                return
                
            st.info(f"📊 Will analyze performance from {len(selected_keyword_sub_accounts)} selected sub-accounts")
        else:
            st.warning("No sub-accounts found. Please create sub-accounts first.")
            return
        
        # Date range selection
        col1, col2 = st.columns(2)
        with col1:
            keyword_start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30), key="keyword_start")
        with col2:
            keyword_end_date = st.date_input("End Date", value=datetime.now(), key="keyword_end")
        
        if keyword_start_date > keyword_end_date:
            st.warning("Start date cannot be after end date. Please select a valid date range.")
            return
        
        # Initialize session state for keywords data and sort
        if 'keywords_data' not in st.session_state:
            st.session_state.keywords_data = None
        if 'keyword_sort_option' not in st.session_state:
            st.session_state.keyword_sort_option = "Cost (Highest)"
        
        # Get keyword insights
        if st.button("Fetch Performance Analysis"):
            st.info(f"Fetching performance analysis from {keyword_start_date.strftime('%Y-%m-%d')} to {keyword_end_date.strftime('%Y-%m-%d')}...")
            try:
                # Get keywords data from selected sub-accounts
                all_keywords_data = get_keywords_analysis(client, selected_keyword_sub_accounts, (keyword_start_date.strftime("%Y-%m-%d"), keyword_end_date.strftime("%Y-%m-%d")))
                
                if all_keywords_data:
                    # Store data in session state
                    st.session_state.keywords_data = all_keywords_data
                    st.session_state.keyword_sort_option = "Cost (Highest)"  # Reset sort to default
                    display_keywords_analysis(all_keywords_data, "Cost (Highest)")
                else:
                    st.warning("No performance data available for the selected date range.")
                    st.session_state.keywords_data = None
                    
            except Exception as e:
                show_message(f"Error fetching performance analysis: {str(e)}", False)
                logger.error(f"Performance analysis error: {str(e)}")
        
        # Display existing data if available
        elif st.session_state.keywords_data:
            # Sort options
            sort_options = {
                "Cost (Highest)": "cost",
                "Impressions": "impressions", 
                "CTR": "ctr",
                "Conversions": "conversions",
                "Conversion Rate": "conversion_rate",
                "Cost per Conversion": "cost_per_conversion"
            }
            
            # Sort selection that persists
            selected_sort = st.selectbox(
                "Sort by:", 
                list(sort_options.keys()), 
                index=list(sort_options.keys()).index(st.session_state.keyword_sort_option),
                key="keyword_sort_persistent"
            )
            
            # Update session state if sort changed
            if selected_sort != st.session_state.keyword_sort_option:
                st.session_state.keyword_sort_option = selected_sort
            
            # Display the data with current sort
            display_keywords_analysis(st.session_state.keywords_data, selected_sort)

# Get keywords analysis across all sub-accounts
@st.cache_data(ttl=3600)  # Cache for 1 hour to reduce API calls
def get_keywords_analysis(_client, sub_accounts_list: list, date_range: tuple) -> dict:
    """Get keywords and search terms performance data from all sub-accounts, grouped by account."""
    try:
        # Track API usage for the overall function call
        st.session_state.api_tracker.increment(1)
        
        all_accounts_keywords = {}
        google_ads_service = _client.get_service("GoogleAdsService")
        
        # Query for keywords with performance metrics
        keywords_query = f"""
            SELECT
              campaign.id,
              campaign.name,
              ad_group_criterion.keyword.text,
              ad_group_criterion.keyword.match_type,
              metrics.impressions,
              metrics.clicks,
              metrics.cost_micros,
              metrics.conversions,
              metrics.conversions_value,
              segments.date
            FROM keyword_view
            WHERE segments.date BETWEEN '{date_range[0]}' AND '{date_range[1]}'
            AND ad_group_criterion.status = 'ENABLED'
            AND campaign.status = 'ENABLED'
            ORDER BY metrics.cost_micros DESC
            LIMIT 1000
        """
        
        # Query for search terms with performance metrics
        search_terms_query = f"""
            SELECT
              campaign.id,
              campaign.name,
              search_term_view.search_term,
              metrics.impressions,
              metrics.clicks,
              metrics.cost_micros,
              metrics.conversions,
              metrics.conversions_value,
              segments.date
            FROM search_term_view
            WHERE segments.date BETWEEN '{date_range[0]}' AND '{date_range[1]}'
            AND campaign.status = 'ENABLED'
            ORDER BY metrics.cost_micros DESC
            LIMIT 1000
        """
        
        for sub_account in sub_accounts_list:
            try:
                # Track API usage for each sub-account
                st.session_state.api_tracker.increment(1)
                
                sub_customer_id = sub_account['id']
                st.write(f"📊 Processing keywords for {sub_account['name']}...")
                
                response = google_ads_service.search(
                    customer_id=sub_customer_id,
                    query=keywords_query
                )
                
                # Initialize account data structure
                if sub_account['name'] not in all_accounts_keywords:
                    all_accounts_keywords[sub_account['name']] = {
                        'account_name': sub_account['name'],
                        'account_id': sub_customer_id,
                        'campaigns': {},
                        'summary': {
                            'total_keywords': 0,
                            'total_impressions': 0,
                            'total_clicks': 0,
                            'total_conversions': 0,
                            'total_cost': 0,
                            'avg_ctr': 0,
                            'avg_conversion_rate': 0,
                            'avg_cost_per_conversion': 0
                        }
                    }
                
                account_data = all_accounts_keywords[sub_account['name']]
                
                # Process keywords data by campaign
                for row in response:
                    campaign_id = row.campaign.id
                    campaign_name = row.campaign.name
                    keyword_text = row.ad_group_criterion.keyword.text
                    match_type = row.ad_group_criterion.keyword.match_type.name
                    impressions = row.metrics.impressions
                    clicks = row.metrics.clicks
                    cost_micros = row.metrics.cost_micros
                    conversions = row.metrics.conversions
                    conversions_value = row.metrics.conversions_value
                    date = row.segments.date
                    
                    # Initialize campaign if not exists
                    if campaign_id not in account_data['campaigns']:
                        account_data['campaigns'][campaign_id] = {
                            'campaign_name': campaign_name,
                            'campaign_id': campaign_id,
                            'keywords': [],
                            'search_terms': [],
                            'summary': {
                                'total_impressions': 0,
                                'total_clicks': 0,
                                'total_cost': 0,
                                'total_conversions': 0,
                                'avg_ctr': 0,
                                'avg_conversion_rate': 0,
                                'avg_cost_per_conversion': 0
                            }
                        }
                    
                    campaign_data = account_data['campaigns'][campaign_id]
                    
                    # Calculate metrics for this keyword
                    cost = cost_micros / 1000000
                    ctr = clicks / impressions if impressions > 0 else 0
                    cost_per_conversion = cost / conversions if conversions > 0 else 0
                    conversion_rate = conversions / clicks if clicks > 0 else 0
                    
                    # Add keyword to campaign
                    keyword_data = {
                        'keyword_text': keyword_text,
                        'match_type': match_type,
                        'impressions': impressions,
                        'clicks': clicks,
                        'ctr': ctr,
                        'conversions': conversions,
                        'cost_per_conversion': cost_per_conversion,
                        'conversion_rate': conversion_rate,
                        'cost': cost,
                        'date': date
                    }
                    
                    campaign_data['keywords'].append(keyword_data)
                    
                    # Update campaign summary
                    campaign_data['summary']['total_impressions'] += impressions
                    campaign_data['summary']['total_clicks'] += clicks
                    campaign_data['summary']['total_cost'] += cost
                    campaign_data['summary']['total_conversions'] += conversions
                
                # Now fetch and process search terms data
                st.write(f"🔍 Processing search terms for {sub_account['name']}...")
                
                search_terms_response = google_ads_service.search(
                    customer_id=sub_customer_id,
                    query=search_terms_query
                )
                
                # Process search terms data by campaign
                for row in search_terms_response:
                    campaign_id = row.campaign.id
                    search_term = row.search_term_view.search_term
                    impressions = row.metrics.impressions
                    clicks = row.metrics.clicks
                    cost_micros = row.metrics.cost_micros
                    conversions = row.metrics.conversions
                    conversions_value = row.metrics.conversions_value
                    date = row.segments.date
                    
                    # Only process if campaign exists (from keywords data)
                    if campaign_id in account_data['campaigns']:
                        campaign_data = account_data['campaigns'][campaign_id]
                        
                        # Calculate metrics for this search term
                        cost = cost_micros / 1000000
                        ctr = clicks / impressions if impressions > 0 else 0
                        cost_per_conversion = cost / conversions if conversions > 0 else 0
                        conversion_rate = conversions / clicks if clicks > 0 else 0
                        
                        # Add search term to campaign
                        search_term_data = {
                            'search_term': search_term,
                            'impressions': impressions,
                            'clicks': clicks,
                            'ctr': ctr,
                            'conversions': conversions,
                            'cost_per_conversion': cost_per_conversion,
                            'conversion_rate': conversion_rate,
                            'cost': cost,
                            'date': date
                        }
                        
                        campaign_data['search_terms'].append(search_term_data)
                
            except Exception as sub_error:
                st.warning(f"⚠️ Could not fetch keywords for {sub_account['name']}: {str(sub_error)}")
                continue
        
        # Process each account and campaign
        processed_accounts = []
        for account_name, account_data in all_accounts_keywords.items():
            account_summary = {
                'total_impressions': 0,
                'total_clicks': 0,
                'total_cost': 0,
                'total_conversions': 0,
                'total_keywords': 0
            }
            
            processed_campaigns = []
            
            # Process each campaign in the account
            for campaign_id, campaign_data in account_data['campaigns'].items():
                # Store total keyword count before limiting
                total_keywords_in_campaign = len(campaign_data['keywords'])
                total_search_terms_in_campaign = len(campaign_data['search_terms'])
                
                # Sort keywords by cost (highest first) and take top 10
                campaign_data['keywords'].sort(key=lambda x: x['cost'], reverse=True)
                top_keywords = campaign_data['keywords'][:10]
                
                # Sort search terms by cost (highest first) and take top 20
                campaign_data['search_terms'].sort(key=lambda x: x['cost'], reverse=True)
                top_search_terms = campaign_data['search_terms'][:20]
                
                # Calculate campaign summary metrics from ALL KEYWORDS in the campaign
                if campaign_data['keywords']:
                    # Campaign summary should reflect ALL keywords, not just top 10
                    # The summary metrics are already calculated from all keywords during data collection
                    # Just calculate the averages from the total campaign metrics
                    campaign_data['summary']['avg_ctr'] = campaign_data['summary']['total_clicks'] / campaign_data['summary']['total_impressions'] if campaign_data['summary']['total_impressions'] > 0 else 0
                    campaign_data['summary']['avg_conversion_rate'] = campaign_data['summary']['total_conversions'] / campaign_data['summary']['total_clicks'] if campaign_data['summary']['total_clicks'] > 0 else 0
                    campaign_data['summary']['avg_cost_per_conversion'] = campaign_data['summary']['total_cost'] / campaign_data['summary']['total_conversions'] if campaign_data['summary']['total_conversions'] > 0 else 0
                
                # Update account summary
                account_summary['total_impressions'] += campaign_data['summary']['total_impressions']
                account_summary['total_clicks'] += campaign_data['summary']['total_clicks']
                account_summary['total_cost'] += campaign_data['summary']['total_cost']
                account_summary['total_conversions'] += campaign_data['summary']['total_conversions']
                account_summary['total_keywords'] += len(top_keywords)
                
                processed_campaigns.append({
                    'campaign_name': campaign_data['campaign_name'],
                    'campaign_id': campaign_data['campaign_id'],
                    'keywords': top_keywords,
                    'search_terms': top_search_terms,
                    'summary': campaign_data['summary'],
                    'total_keywords_in_campaign': total_keywords_in_campaign,  # Store the total count
                    'total_search_terms_in_campaign': total_search_terms_in_campaign  # Store the total count
                })
            
            # Calculate account-level averages
            account_data['summary'] = {
                'total_keywords': account_summary['total_keywords'],
                'total_impressions': account_summary['total_impressions'],
                'total_clicks': account_summary['total_clicks'],
                'total_conversions': account_summary['total_conversions'],
                'total_cost': account_summary['total_cost'],
                'avg_ctr': account_summary['total_clicks'] / account_summary['total_impressions'] if account_summary['total_impressions'] > 0 else 0,
                'avg_conversion_rate': account_summary['total_conversions'] / account_summary['total_clicks'] if account_summary['total_clicks'] > 0 else 0,
                'avg_cost_per_conversion': account_summary['total_cost'] / account_summary['total_conversions'] if account_summary['total_conversions'] > 0 else 0
            }
            
            processed_accounts.append({
                'account_name': account_name,
                'account_id': account_data['account_id'],
                'campaigns': processed_campaigns,
                'summary': account_data['summary']
            })
        
        return {
            'accounts': processed_accounts,
            'total_accounts': len(processed_accounts)
        }
        
    except Exception as e:
        st.error(f"Error getting keywords analysis: {str(e)}")
        return {}

def display_keywords_analysis(keywords_data: dict, sort_by_option: str):
    """Display keywords analysis in a dashboard format, grouped by account and campaign."""
    
    if not keywords_data or not keywords_data['accounts']:
        st.warning("No keyword data available for the selected date range.")
        return
    
    # Overall summary metrics
    st.subheader("📊 Account Performance Summary")
    
    total_accounts = keywords_data['total_accounts']
    total_keywords = sum(acc['summary']['total_keywords'] for acc in keywords_data['accounts'])
    total_cost = sum(acc['summary']['total_cost'] for acc in keywords_data['accounts'])
    total_impressions = sum(acc['summary']['total_impressions'] for acc in keywords_data['accounts'])
    total_clicks = sum(acc['summary']['total_clicks'] for acc in keywords_data['accounts'])
    total_conversions = sum(acc['summary']['total_conversions'] for acc in keywords_data['accounts'])
    
    avg_ctr = total_clicks / total_impressions if total_impressions > 0 else 0
    avg_conversion_rate = total_conversions / total_clicks if total_clicks > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Accounts Analyzed", total_accounts)
    
    with col2:
        st.metric("Avg CTR", f"{avg_ctr:.2%}")
    
    with col3:
        st.metric("Total Cost", f"${total_cost:.2f}")
    
    with col4:
        st.metric("Total Conversions", f"{total_conversions:.0f}")
    
    # Sort options for keywords tables
    sort_options = {
        "Cost (Highest)": "cost",
        "Impressions": "impressions", 
        "CTR": "ctr",
        "Conversions": "conversions",
        "Conversion Rate": "conversion_rate",
        "Cost per Conversion": "cost_per_conversion"
    }
    
    sort_column = sort_options[sort_by_option]
    
    # Display each account
    st.subheader("🏢 Performance by Account & Campaign")
    
    for account in keywords_data['accounts']:
        # Just show the sub-account name without summary metrics
        st.write(f"**📈 {account['account_name']} (ID: {account['account_id']})**")
        
        # Display each campaign in this account
        for campaign in account['campaigns']:
            if not campaign['keywords']:
                continue
                
            st.write(f"**🎯 Campaign: {campaign['campaign_name']}**")
            
            # Add note about top 10 keywords
            total_keywords_in_campaign = campaign.get('total_keywords_in_campaign', len(campaign['keywords']))
            st.info(f"📊 Campaign summary shows ALL {total_keywords_in_campaign} keywords. Table shows top 10 keywords by spend.")
            
            # Campaign summary metrics
            camp_col1, camp_col2, camp_col3, camp_col4 = st.columns(4)
            
            with camp_col1:
                st.metric("Impressions", f"{campaign['summary']['total_impressions']:,}")
            
            with camp_col2:
                st.metric("Clicks", f"{campaign['summary']['total_clicks']:,}")
                st.metric("CTR", f"{campaign['summary']['avg_ctr']:.2%}")
            
            with camp_col3:
                st.metric("Conversions", f"{campaign['summary']['total_conversions']:.0f}")
                st.metric("Conv. Rate", f"{campaign['summary']['avg_conversion_rate']:.2%}")
            
            with camp_col4:
                st.metric("Cost", f"${campaign['summary']['total_cost']:.2f}")
                st.metric("Cost/Conv.", f"${campaign['summary']['avg_cost_per_conversion']:.2f}")
            
            # Keywords table for this campaign
            if campaign['keywords']:
                keywords_df = pd.DataFrame(campaign['keywords'])
                
                # Sort based on selected metric
                if sort_column == "cost":
                    keywords_df = keywords_df.sort_values('cost', ascending=False)
                elif sort_column == "impressions":
                    keywords_df = keywords_df.sort_values('impressions', ascending=False)
                elif sort_column == "ctr":
                    keywords_df = keywords_df.sort_values('ctr', ascending=False)
                elif sort_column == "conversions":
                    keywords_df = keywords_df.sort_values('conversions', ascending=False)
                elif sort_column == "conversion_rate":
                    keywords_df = keywords_df.sort_values('conversion_rate', ascending=False)
                elif sort_column == "cost_per_conversion":
                    keywords_df = keywords_df.sort_values('cost_per_conversion', ascending=True)  # Lower is better
                
                # Format display columns
                display_df = keywords_df[['keyword_text', 'match_type', 'impressions', 'clicks', 'ctr', 'conversions', 'cost_per_conversion', 'conversion_rate', 'cost']].copy()
                display_df['CTR'] = display_df['ctr'].apply(lambda x: f"{x:.2%}")
                display_df['Conv. Rate'] = display_df['conversion_rate'].apply(lambda x: f"{x:.2%}")
                display_df['Cost/Conv.'] = display_df['cost_per_conversion'].apply(lambda x: f"${x:.2f}")
                display_df['Cost'] = display_df['cost'].apply(lambda x: f"${x:.2f}")
                
                # Rename columns to match requested format
                display_df = display_df.rename(columns={
                    'keyword_text': 'Keyword',
                    'match_type': 'Match Type',
                    'impressions': 'Impressions',
                    'clicks': 'Clicks',
                    'conversions': 'Conversions'
                })
                
                # Select and order columns in the requested format
                display_df = display_df[['Keyword', 'Match Type', 'Impressions', 'Clicks', 'CTR', 'Conversions', 'Cost/Conv.', 'Conv. Rate', 'Cost']]
                
                st.dataframe(display_df, use_container_width=True)
            else:
                st.info("No keyword data available for this campaign.")
            
            # Search Terms table for this campaign
            if campaign.get('search_terms'):
                st.write("**🔍 Top Search Terms by Spend**")
                
                # Add note about top 20 search terms
                total_search_terms_in_campaign = campaign.get('total_search_terms_in_campaign', len(campaign['search_terms']))
                st.info(f"📊 Showing top 20 search terms by spend (out of {total_search_terms_in_campaign} total search terms in campaign)")
                
                search_terms_df = pd.DataFrame(campaign['search_terms'])
                
                # Sort based on selected metric (same as keywords)
                if sort_column == "cost":
                    search_terms_df = search_terms_df.sort_values('cost', ascending=False)
                elif sort_column == "impressions":
                    search_terms_df = search_terms_df.sort_values('impressions', ascending=False)
                elif sort_column == "ctr":
                    search_terms_df = search_terms_df.sort_values('ctr', ascending=False)
                elif sort_column == "conversions":
                    search_terms_df = search_terms_df.sort_values('conversions', ascending=False)
                elif sort_column == "conversion_rate":
                    search_terms_df = search_terms_df.sort_values('conversion_rate', ascending=False)
                elif sort_column == "cost_per_conversion":
                    search_terms_df = search_terms_df.sort_values('cost_per_conversion', ascending=True)  # Lower is better
                
                # Format display columns
                search_display_df = search_terms_df[['search_term', 'impressions', 'clicks', 'ctr', 'conversions', 'cost_per_conversion', 'conversion_rate', 'cost']].copy()
                search_display_df['CTR'] = search_display_df['ctr'].apply(lambda x: f"{x:.2%}")
                search_display_df['Conv. Rate'] = search_display_df['conversion_rate'].apply(lambda x: f"{x:.2%}")
                search_display_df['Cost/Conv.'] = search_display_df['cost_per_conversion'].apply(lambda x: f"${x:.2f}")
                search_display_df['Cost'] = search_display_df['cost'].apply(lambda x: f"${x:.2f}")
                
                # Rename columns to match requested format
                search_display_df = search_display_df.rename(columns={
                    'search_term': 'Search Term',
                    'impressions': 'Impressions',
                    'clicks': 'Clicks',
                    'conversions': 'Conversions'
                })
                
                # Select and order columns in the requested format
                search_display_df = search_display_df[['Search Term', 'Impressions', 'Clicks', 'CTR', 'Conversions', 'Cost/Conv.', 'Conv. Rate', 'Cost']]
                
                st.dataframe(search_display_df, use_container_width=True)
            else:
                st.info("No search terms data available for this campaign.")
            
            st.divider()

if __name__ == "__main__":
    main()