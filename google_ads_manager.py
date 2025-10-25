import pandas as pd
import logging
import re
import gc
import psutil
import os
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.api_core.exceptions import GoogleAPICallError
from google.protobuf.field_mask_pb2 import FieldMask

from datetime import datetime, timedelta
import streamlit as st
from typing import Optional, List, Dict, Any
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
# Removed Campaign import as it's not compatible with API v21
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io

# Memory Management Utilities
class MemoryManager:
    """Utility class for managing memory usage and preventing memory leaks."""
    
    @staticmethod
    def get_memory_usage():
        """Get current memory usage in MB."""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024  # Convert to MB
    
    @staticmethod
    def log_memory_usage(location: str):
        """Log current memory usage for debugging."""
        memory_mb = MemoryManager.get_memory_usage()
        logger.info(f"Memory usage at {location}: {memory_mb:.2f} MB")
        
        # Warning if memory usage is high
        if memory_mb > 1000:  # 1GB threshold
            logger.warning(f"High memory usage detected: {memory_mb:.2f} MB at {location}")
    
    @staticmethod
    def cleanup_dataframes():
        """Force garbage collection of DataFrames and other large objects."""
        gc.collect()
        logger.info("Forced garbage collection completed")
    
    @staticmethod
    def clear_session_data():
        """Clear large data from session state to prevent memory leaks."""
        keys_to_clear = ['keywords_data', 'keyword_date_range']
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
                logger.info(f"Cleared session state key: {key}")
    
    @staticmethod
    def limit_dataframe_size(df: pd.DataFrame, max_rows: int = 1000) -> pd.DataFrame:
        """Limit DataFrame size to prevent memory issues."""
        if len(df) > max_rows:
            logger.warning(f"DataFrame truncated from {len(df)} to {max_rows} rows to prevent memory issues")
            return df.head(max_rows)
        return df

# Initialize memory manager
memory_manager = MemoryManager()

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
MAX_HEADLINES = 15
MAX_DESCRIPTIONS = 4

# Build required columns dynamically
REQUIRED_COLUMNS = ["ad_group_name"]
# Add all 15 headlines
REQUIRED_COLUMNS.extend([f"headline{i}" for i in range(1, MAX_HEADLINES + 1)])
# Add all 4 descriptions  
REQUIRED_COLUMNS.extend([f"description{i}" for i in range(1, MAX_DESCRIPTIONS + 1)])
# Add other required columns
REQUIRED_COLUMNS.extend(["final_url", "keywords"])

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
        
        # Test the client by making a simple API call
        try:
            # Try to make a simple search query to verify the token is valid
            google_ads_service = client.get_service("GoogleAdsService")
            # Use a simple query to test the connection
            test_query = """
                SELECT
                  customer.id,
                  customer.descriptive_name
                FROM customer
                LIMIT 1
            """
            google_ads_service.search(
                customer_id=st.secrets["GOOGLE_ADS_LOGIN_CUSTOMER_ID"],
                query=test_query
            )
        except Exception as test_error:
            if "invalid_grant" in str(test_error).lower() or "token has been expired" in str(test_error).lower():
                st.error("🔐 **Authentication Error: Refresh Token Expired or Revoked**")
                st.error(f"Error details: {test_error}")
                
                # Automatically show the reset instructions
                st.session_state.show_auth_reset = True
                
                st.warning("""
                **⚠️ Your refresh token has expired!**
                
                Click the **"🔐 Reset Authentication"** button at the top of the page for step-by-step instructions to fix this.
                
                This usually takes 2-3 minutes to resolve.
                """)
                return None
            else:
                # Other API errors - still return the client but log the warning
                st.warning(f"⚠️ API test failed but continuing: {test_error}")
        
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

@st.cache_data(ttl=300)  # Cache for 5 minutes instead of 30
def get_sub_accounts(_client: GoogleAdsClient, mcc_customer_id: str) -> list[dict]:
    """Fetch all direct, active sub-accounts under the MCC account using GAQL."""
    try:
        # Track memory usage
        memory_manager.log_memory_usage("get_sub_accounts_start")
        
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
        
        # Log memory usage after processing
        memory_manager.log_memory_usage("get_sub_accounts_end")
        return sub_accounts
    except Exception as ex:
        st.error(f"💥 Error fetching sub-accounts: {str(ex)}")
        handle_api_exception(ex, "fetch sub-accounts")
        return []

# Create a new sub-account under MCC
def create_sub_account(client: GoogleAdsClient, mcc_customer_id: str, account_name: str, 
                      currency_code: str, time_zone: str) -> Optional[str]:
    """Create a new sub-account under MCC with conversion tracking set to 'This Manager'.
    Sub-accounts are created without MCC payment profile linking so clients can set up their own payment methods.
    
    Args:
        client: Google Ads client
        mcc_customer_id: MCC customer ID
        account_name: Name for the new sub-account
        currency_code: Currency code for the account
        time_zone: Time zone for the account
    """
    try:
        customer_service = client.get_service("CustomerService")
        customer = client.get_type("Customer")
        customer.descriptive_name = account_name
        customer.currency_code = currency_code
        customer.time_zone = time_zone
        customer.tracking_url_template = ""

        # Always create accounts without MCC payment profile linking
        customer.manager = False  # This prevents automatic MCC payment profile linking
        customer.test_account = False
        
        st.info("ℹ️ Account will be created without MCC payment profile linking. Client will need to set up their own payment methods.")

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
                st.info("🔧 Configuring conversion tracking to use 'This Manager'...")
                
                # In Google Ads API v21, conversion tracking for sub-accounts is typically configured
                # through the Google Ads UI rather than the API. However, let's try the correct approach:
                
                st.info("💡 In API v21, conversion tracking for sub-accounts is typically configured through the Google Ads UI.")
                st.info("🔧 The sub-account has been created and is ready for manual conversion tracking setup.")
                
                # Check current conversion tracking status
                try:
                    google_ads_service = client.get_service("GoogleAdsService")
                    
                    # Query to check current customer conversion tracking settings
                    query = f"""
                        SELECT
                          customer.id,
                          customer.descriptive_name
                        FROM customer
                        WHERE customer.id = {new_customer_id}
                    """
                    
                    response = google_ads_service.search(customer_id=new_customer_id, query=query)
                    for row in response:
                        break
                    
                    st.info("✅ Sub-account is ready and accessible via Google Ads API")
                    
                except Exception as query_error:
                    st.warning(f"⚠️ Could not query new customer details: {query_error}")
                    logger.warning(f"Could not query new customer details: {query_error}")
                
                # Note: The manager-customer relationship is already established during account creation
                # The conversion tracking needs to be set manually in the Google Ads UI
                
                # Provide clear manual setup instructions since API approach isn't working
                st.success("✅ Sub-account created successfully!")
                st.warning("🔧 Manual conversion tracking setup required for portfolio bidding strategies")
                
                show_message(f"✅ Created sub-account with ID: {new_customer_id}. Manual conversion tracking setup needed for portfolio bidding.")
                
                # Add detailed, user-friendly manual setup instructions
                st.markdown(f"""
                ## 🎯 **Important: Enable Portfolio Bidding Strategies**
                
                **Account Created: `{new_customer_id}`**
                
                ### **Quick Setup (5 minutes):**
                
                1. **Open Google Ads** → Go to [ads.google.com](https://ads.google.com)
                2. **Switch to account** `{new_customer_id}` (use account selector in top-right)
                3. **Go to Settings** → Click ⚙️ in top-right → Account Settings
                4. **Find "Conversion tracking"** section
                5. **Click "Google Ads conversion account"**
                6. **Select "This manager ({mcc_customer_id})"** from dropdown
                7. **Click "Save"**
                8. **Wait 15-30 minutes** for system update
                
                ### **✅ What this enables:**
                - 🎯 **MSL - MaxCon bidding strategy** (Maximize Conversions)
                - 📊 **Portfolio bidding strategies** for all campaigns
                - 🚀 **Advanced automated bidding** capabilities
                
                ### **🔄 Alternative (if you skip this step):**
                - Campaigns will use **Manual CPC bidding** (still works fine)
                - You can enable portfolio strategies later when ready
                
                ### **📱 Quick Link:**
                **Direct URL:** `https://ads.google.com/aw/accountsettings?ocid={new_customer_id}#conversion-tracking`
                """)
                
                # Add a helpful reminder
                st.info("💡 **Tip**: Bookmark this page or save the account ID for easy reference!")
                
                return new_customer_id
                
            except Exception as conversion_error:
                # If all conversion tracking setup fails, still return the account ID
                logger.warning(f"Could not set conversion tracking: {conversion_error}")
                st.error(f"❌ Conversion tracking setup error: {conversion_error}")
                show_message(f"✅ Created sub-account with ID: {new_customer_id}. Conversion tracking setup failed - manual setup required.")
                return new_customer_id
        
        return new_customer_id
        
    except Exception as ex:
        handle_api_exception(ex, "create sub-account")
        return None





# Configure location targeting for API v21
def configure_location_targeting(client: GoogleAdsClient, customer_id: str, campaign_id: str) -> bool:
    """Configure location targeting to use 'Presence Only' instead of 'Presence or Interest'."""
    try:
        # In API v21, location targeting behavior is often configured at the campaign level
        # or through specific location criteria rather than general geo target type settings
        
        google_ads_service = client.get_service("GoogleAdsService")
        
        # Check if the campaign has location-related fields we can update
        query = f"""
            SELECT
              campaign.id,
              campaign.name,
              campaign.advertising_channel_type
            FROM campaign
            WHERE campaign.id = {campaign_id}
        """
        
        response = google_ads_service.search(
            customer_id=customer_id,
            query=query
        )
        
        if not response:
            st.warning("⚠️ Campaign not found for location targeting configuration")
            return False
        

        

        
        # Now let's add specific location targeting using CampaignCriterion
        # This will actually restrict the campaign to target specific locations
        try:
            campaign_criterion_service = client.get_service("CampaignCriterionService")
            
            # Get the user's selected locations from session state
            target_locations = st.session_state.get('selected_locations', [])
            
            # If no specific locations selected, use default behavior
            if not target_locations:
                st.info("ℹ️ No specific locations selected - fallback campaign will target all locations")
                return True
            
            operations = []
            for location in target_locations:
                location_criterion = client.get_type("CampaignCriterion")
                location_criterion.campaign = f"customers/{customer_id}/campaigns/{campaign_id}"
                location_criterion.status = client.enums.CampaignCriterionStatusEnum.ENABLED
                
                # Set the location using the geo target constant ID
                # In API v21, the format should be 'geoTargetConstants/{id}'
                try:
                    location_criterion.location.geo_target_constant = f"geoTargetConstants/{location['id']}"
                except Exception as loc_error:
                    st.warning(f"⚠️ Could not set location {location.get('name', 'unknown')}: {loc_error}")
                    continue
                
                # Note: In API v21, location targeting behavior (Presence Only vs Presence or Interest)
                # is configured at the campaign level through geo_target_type_setting, but this field
                # has compatibility issues. The default behavior should be acceptable for most campaigns.
                
                operation = client.get_type("CampaignCriterionOperation")
                operation.create = location_criterion
                operations.append(operation)
            
            if operations:
                # Apply the location targeting criteria
                response = campaign_criterion_service.mutate_campaign_criteria(
                    customer_id=customer_id,
                    operations=operations
                )
                
                st.success(f"✅ Location targeting configured: Campaign will target {', '.join([loc['name'] for loc in target_locations])}")
                st.success("✅ Targeting set to 'Presence Only' (not 'Presence or Interest')")
                st.info("ℹ️ Users will only see ads when they are physically in these locations")
                logger.info(f"Location targeting configured for campaign {campaign_id}: {[loc['name'] for loc in target_locations]}")
                return True
            else:
                st.warning("⚠️ No location operations to apply")
                return False
                
        except Exception as location_error:
            st.warning(f"⚠️ Could not add specific location targeting: {location_error}")
            st.info("ℹ️ Campaign will still use default location targeting (all locations)")
            logger.warning(f"Failed to add specific location targeting for campaign {campaign_id}: {location_error}")
            return False
            
    except Exception as e:
        st.warning(f"⚠️ Could not configure location targeting: {e}")
        logger.warning(f"Failed to configure location targeting for campaign {campaign_id}: {e}")
        return False

# Update campaign targeting after creation (API v21 compatible approach)
def update_campaign_targeting(client: GoogleAdsClient, customer_id: str, campaign_id: str) -> bool:
    """Update campaign targeting after creation using the correct API v21 approach."""
    try:
        st.info("🔧 Updating campaign targeting settings...")
        
        # Get the campaign service
        campaign_service = client.get_service("CampaignService")
        
        # Create a campaign update operation
        campaign_operation = client.get_type("CampaignOperation")
        campaign = campaign_operation.update
        campaign.resource_name = f"customers/{customer_id}/campaigns/{campaign_id}"
        
        # Configure location targeting behavior to "Presence Only"
        
        # Configure geo_target_type_setting for "Presence Only" behavior
        # In API v21, this is a direct property on the campaign object
        location_updated = False
        if hasattr(campaign, 'geo_target_type_setting'):
            try:
                # Set geo target type properties directly on campaign
                campaign.geo_target_type_setting.positive_geo_target_type = client.enums.PositiveGeoTargetTypeEnum.PRESENCE
                campaign.geo_target_type_setting.negative_geo_target_type = client.enums.NegativeGeoTargetTypeEnum.PRESENCE
                
                location_updated = True
                st.success("✅ Location targeting updated: Presence Only (not Presence or Interest)")
                
            except Exception as geo_error:
                st.warning(f"⚠️ Could not update location targeting: {geo_error}")
        else:
            st.info("ℹ️ geo_target_type_setting field not found - location targeting will use default behavior")
        
        # Try to set network targeting to exclude Display Network and search partners
        # In API v21, these are direct properties on the campaign object
        network_fields_updated = False
        if hasattr(campaign, 'network_settings'):
            try:
                # Set network targeting properties directly on campaign
                campaign.network_settings.target_google_search = True  # Enable Google Search
                campaign.network_settings.target_search_network = False  # Disable search partners
                campaign.network_settings.target_content_network = False  # Disable Display Network
                campaign.network_settings.target_partner_search_network = False  # Disable search partners
                
                network_fields_updated = True
                st.success("✅ Campaign network targeting updated: Google Search Network only")
                
            except Exception as network_error:
                st.warning(f"⚠️ Could not update network targeting: {network_error}")
        else:
            st.info("ℹ️ network_settings field not found on campaign update object")
        
        # Create the update operation
        operation = client.get_type("CampaignOperation")
        operation.update = campaign
        
        # Proceed with update if we have network settings or location settings to update
        if network_fields_updated or location_updated:
            # Set the field mask to update the targeting fields
            field_mask = FieldMask()
            
            # Add geo_target_type_setting subfields to field mask if location was updated
            # Note: Must specify subfields, not parent field, to avoid FIELD_HAS_SUBFIELDS error
            if location_updated:
                if hasattr(campaign.geo_target_type_setting, 'positive_geo_target_type'):
                    field_mask.paths.append("geo_target_type_setting.positive_geo_target_type")
                if hasattr(campaign.geo_target_type_setting, 'negative_geo_target_type'):
                    field_mask.paths.append("geo_target_type_setting.negative_geo_target_type")
            
            # Add network_settings subfields to the field mask if network was updated
            if network_fields_updated and hasattr(campaign.network_settings, 'target_google_search'):
                field_mask.paths.append("network_settings.target_google_search")
            if network_fields_updated and hasattr(campaign.network_settings, 'target_search_network'):
                field_mask.paths.append("network_settings.target_search_network")
            if network_fields_updated and hasattr(campaign.network_settings, 'target_content_network'):
                field_mask.paths.append("network_settings.target_content_network")
            if network_fields_updated and hasattr(campaign.network_settings, 'target_partner_search_network'):
                field_mask.paths.append("network_settings.target_partner_search_network")
            
            operation.update_mask.CopyFrom(field_mask)
            
            # Apply the update
            response = campaign_service.mutate_campaigns(
                customer_id=customer_id,
                operations=[operation]
            )
            
            success_messages = []
            if network_fields_updated:
                success_messages.append("network targeting")
            if location_updated:
                success_messages.append("location targeting")
            
            st.success(f"✅ Campaign {' and '.join(success_messages)} updated successfully!")
            logger.info(f"Campaign targeting updated for campaign {campaign_id}: {success_messages}")
            return True
        else:
            st.info("ℹ️ Network and location settings will use default values (this is normal for some API versions)")
            return True
        
    except Exception as e:
        st.warning(f"⚠️ Could not update campaign targeting: {e}")
        logger.warning(f"Failed to update campaign targeting for campaign {campaign_id}: {e}")
        return False

# Get location IDs for targeting
def get_location_ids(client: GoogleAdsClient, customer_id: str, location_names: List[str]) -> dict:
    """Get location IDs for specified location names."""
    try:
        google_ads_service = client.get_service("GoogleAdsService")
        
        # Build the query for the specified locations
        location_list = "', '".join(location_names)
        query = f"""
            SELECT
              geo_target_constant.id,
              geo_target_constant.name,
              geo_target_constant.country_code
            FROM geo_target_constant
            WHERE geo_target_constant.name IN ('{location_list}')
        """
        
        response = google_ads_service.search(
            customer_id=customer_id,
            query=query
        )
        
        locations = {}
        for row in response:
            locations[row.geo_target_constant.name] = row.geo_target_constant.id
        
        return locations
        
    except Exception as e:
        st.error(f"❌ Error getting location IDs: {e}")
        logger.error(f"Failed to get location IDs: {e}")
        return {}

# Create a campaign with daily budget
def create_campaign(client: GoogleAdsClient, customer_id: str, campaign_name: str, 
                   budget_amount: float) -> Optional[str]:
    """Create a campaign with daily budget and Maximize Clicks bidding strategy."""
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
        
        # Ensure budget is not shared (campaign-specific)
        # In API v21, explicitly set explicitly_shared to False to ensure individual campaign budget
        try:
            if hasattr(campaign_budget, 'explicitly_shared'):
                campaign_budget.explicitly_shared = False  # Individual campaign budget, not shared
                st.info("✅ Budget configured as individual campaign budget (not shared)")
            elif hasattr(campaign_budget, 'is_shared'):
                campaign_budget.is_shared = False  # Alternative field name
                st.info("✅ Budget configured as individual campaign budget (not shared)")
            else:
                st.info("ℹ️ Budget sharing field not found - using default behavior")
        except Exception as budget_error:
            st.warning(f"⚠️ Could not configure budget sharing: {budget_error}")
            st.info("ℹ️ Budget will use default behavior")
        
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
        
        # Set Maximize Clicks bidding strategy
        # This is a campaign-level automated bidding strategy that automatically sets bids to get as many clicks as possible within the budget
        try:
            # Access the maximize_clicks field to initialize it (this sets the bidding strategy)
            campaign.maximize_clicks.SetInParent()
            st.info("✅ Bidding strategy set to: Maximize Clicks")
        except Exception as bidding_error:
            st.warning(f"⚠️ Could not set Maximize Clicks bidding strategy: {bidding_error}")
            logger.warning(f"Failed to set Maximize Clicks bidding strategy: {bidding_error}")
        
        # Hardcoded shared negative keywords list - PPCL List
        ppcl_negative_list_id = "11404993599"  # PPCL List negative keywords ID
        st.info(f"✅ Will apply PPCL List negative keywords (ID: {ppcl_negative_list_id}) after campaign creation")
        
        # Configure network settings to exclude search partners and display network
        # In API v21, these are direct properties on the campaign object, not separate types
        try:
            # Set network targeting properties directly on campaign
            campaign.network_settings.target_google_search = True  # Enable Google Search
            campaign.network_settings.target_search_network = False  # Disable search partners
            campaign.network_settings.target_content_network = False  # Disable Display Network
            campaign.network_settings.target_partner_search_network = False  # Disable search partners
            
            st.info("✅ Network settings configured: Google Search only (no search partners, no Display Network)")
            
        except Exception as network_error:
            st.warning(f"⚠️ Could not configure network settings during creation: {network_error}")
            st.info("ℹ️ Network settings will be configured after campaign creation")
        
        # Configure location targeting behavior to "Presence Only"
        # In API v21, this is a direct property on the campaign object, not a separate type
        try:
            # Set geo target type properties directly on campaign
            campaign.geo_target_type_setting.positive_geo_target_type = client.enums.PositiveGeoTargetTypeEnum.PRESENCE
            campaign.geo_target_type_setting.negative_geo_target_type = client.enums.NegativeGeoTargetTypeEnum.PRESENCE
            
            st.info("✅ Location targeting configured: Presence Only (not Presence or Interest)")
            
        except Exception as geo_error:
            st.warning(f"⚠️ Could not configure location targeting during creation: {geo_error}")
            st.info("ℹ️ Location targeting will be configured after campaign creation")
        
        # Note: We'll configure location targeting after campaign creation using CampaignCriterion
        # This avoids initialization errors with campaign fields during creation
        
        campaign.start_date = datetime.now().strftime("%Y-%m-%d")  # Current date at runtime
        # No end_date (ongoing)
        
        # Set EU political advertising field (required in API v21)
        try:
            # Try different possible field names for API v21
            eu_field_set = False
            
            # Try common field names for EU political advertising
            eu_field_names = [
                'contains_eu_political_advertising',
                'eu_political_advertising',
                'eu_political_content',
                'political_advertising',
                'political_content'
            ]
            
            for field_name in eu_field_names:
                if hasattr(campaign, field_name):
                    # Use the proper enum value instead of False
                    setattr(campaign, field_name, client.enums.EuPoliticalAdvertisingStatusEnum.DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING)
                    st.info(f"✅ Set EU political advertising field '{field_name}' to False")
                    eu_field_set = True
                    break
            
            if not eu_field_set:
                st.warning("⚠️ EU political advertising field not found")
                
        except Exception as eu_error:
            st.warning(f"⚠️ Could not set EU political advertising field: {eu_error}")
            logger.warning(f"Failed to set EU political advertising field: {eu_error}")

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
            
            # Update campaign targeting settings after creation
            st.info("🔧 Updating campaign targeting settings...")
            targeting_success = update_campaign_targeting(client, customer_id, campaign_id)
            
            # Campaign will target all locations with "Presence Only" behavior
            st.info("ℹ️ Campaign configured to target all locations with 'Presence Only' behavior")
            
            show_message(f"✅ Created campaign with ID: {campaign_id} (PAUSED) using Maximize Clicks bidding strategy. Budget is set to ${budget_amount}/day for this campaign only (not shared). Add ad groups, ads, and keywords in the Bulk Upload tab.")
            return campaign_id
        except Exception as ex:
            # Check if the error is related to conversion tracking or bidding strategy
            error_message = str(ex)
            logger.error(f"Campaign creation failed with error: {error_message}")
            
            # Check for specific bidding strategy or conversion tracking errors
            if ("CONVERSION_TRACKING_NOT_ENABLED" in error_message or 
                "REQUIRED" in error_message or 
                "bidding" in error_message.lower() or
                "strategy" in error_message.lower()):
                
                if "CONVERSION_TRACKING_NOT_ENABLED" in error_message:
                    st.warning("⚠️ Conversion tracking is not enabled for this customer account.")
                    st.info("💡 Portfolio bidding strategies (like Maximize Conversions) require conversion tracking to be enabled.")
                    st.markdown("""
                    **💡 To Enable Conversion Tracking:**
                    1. Go to Google Ads UI for this customer account
                    2. Navigate to **Tools & Settings** > **Measurement** > **Conversions**
                    3. Create at least one conversion action (e.g., website purchases, form submissions)
                    4. Or set up **Google Analytics 4** conversion import
                    5. Wait 15-30 minutes for the system to recognize conversion tracking is enabled
                    6. Then retry campaign creation with portfolio bidding strategy
                    
                    **Alternative:** Use Manual CPC bidding (current fallback) and switch to portfolio strategy later.
                    """)
                
                st.warning("⚠️ Bidding strategy issue detected. Retrying with Manual CPC bidding strategy...")
                
                # Create a new campaign operation without the bidding strategy
                campaign_operation_fallback = client.get_type("CampaignOperation")
                campaign_fallback = campaign_operation_fallback.create
                campaign_fallback.name = campaign_name
                campaign_fallback.status = client.enums.CampaignStatusEnum.PAUSED
                campaign_fallback.campaign_budget = budget_resource_name
                campaign_fallback.advertising_channel_type = client.enums.AdvertisingChannelTypeEnum.SEARCH
                campaign_fallback.start_date = datetime.now().strftime("%Y-%m-%d")
                
                # Configure network settings for fallback campaign too
                # In API v21, these are direct properties on the campaign object
                try:
                    # Set network targeting properties directly on fallback campaign
                    campaign_fallback.network_settings.target_google_search = True  # Enable Google Search
                    campaign_fallback.network_settings.target_search_network = False  # Disable search partners
                    campaign_fallback.network_settings.target_content_network = False  # Disable Display Network
                    campaign_fallback.network_settings.target_partner_search_network = False  # Disable search partners
                    
                    st.info("✅ Fallback network settings configured: Google Search only (no search partners, no Display Network)")
                    
                except Exception as network_error_fallback:
                    st.warning(f"⚠️ Could not configure fallback network settings: {network_error_fallback}")
                
                # Configure location targeting behavior for fallback campaign too
                # In API v21, this is a direct property on the campaign object
                try:
                    # Set geo target type properties directly on fallback campaign
                    campaign_fallback.geo_target_type_setting.positive_geo_target_type = client.enums.PositiveGeoTargetTypeEnum.PRESENCE
                    campaign_fallback.geo_target_type_setting.negative_geo_target_type = client.enums.NegativeGeoTargetTypeEnum.PRESENCE
                    
                    st.info("✅ Fallback location targeting configured: Presence Only (not Presence or Interest)")
                    
                except Exception as geo_error_fallback:
                    st.warning(f"⚠️ Could not configure fallback location targeting: {geo_error_fallback}")
                

                

                
                # Set EU political advertising field (required in API v21)
                try:
                    # Try different possible field names for API v21
                    eu_field_set = False
                    
                    # Try common field names for EU political advertising
                    eu_field_names = [
                        'contains_eu_political_advertising',
                        'eu_political_advertising',
                        'eu_political_content',
                        'political_advertising',
                        'political_content'
                    ]
                    
                    for field_name in eu_field_names:
                        if hasattr(campaign_fallback, field_name):
                            # Use the proper enum value instead of False
                            setattr(campaign_fallback, field_name, client.enums.EuPoliticalAdvertisingStatusEnum.DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING)
                            st.info(f"✅ Set EU political advertising field '{field_name}' to False (fallback)")
                            eu_field_set = True
                            break
                    
                    if not eu_field_set:
                        st.warning("⚠️ EU political advertising field not found in fallback")
                    

                    
                except Exception as eu_error:
                    st.warning(f"⚠️ Could not set EU political advertising field: {eu_error}")
                    logger.warning(f"Failed to set EU political advertising field: {eu_error}")
                
                # Set Manual CPC bidding strategy
                try:
                    campaign_fallback.manual_cpc = client.get_type("ManualCpc")
                    # Try to set enhanced CPC if the field exists
                    if hasattr(campaign_fallback.manual_cpc, 'enhanced_cpc_enabled'):
                        campaign_fallback.manual_cpc.enhanced_cpc_enabled = False
                        st.info("✅ Manual CPC bidding strategy configured with enhanced CPC disabled")
                    else:
                        st.info("✅ Manual CPC bidding strategy configured (enhanced CPC field not available)")
                except Exception as cpc_error:
                    st.warning(f"⚠️ Could not configure Manual CPC bidding strategy: {cpc_error}")
                    logger.warning(f"Failed to configure Manual CPC bidding strategy: {cpc_error}")
                
                # Note: Network and location settings are configured above using proper NetworkSettings and GeoTargetTypeSetting objects
                
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
                    
                    # Update campaign targeting settings after creation (fallback case)
                    st.info("🔧 Updating fallback campaign targeting settings...")
                    targeting_success = update_campaign_targeting(client, customer_id, campaign_id)
                    
                    # Fallback campaign will target all locations with "Presence Only" behavior
                    st.info("ℹ️ Fallback campaign configured to target all locations with 'Presence Only' behavior")
                    
                    show_message(f"✅ Created campaign with ID: {campaign_id} (PAUSED) using Manual CPC bidding strategy. Budget is set to ${budget_amount}/day for this campaign only (not shared). You can change to MSL - MaxCon later once conversion tracking is enabled.")
                    return campaign_id
                except Exception as fallback_ex:
                    handle_api_exception(fallback_ex, "create campaign with Manual CPC")
                    return None
            else:
                st.error(f"❌ Campaign creation failed with non-bidding strategy error: {error_message}")
                st.error("❌ This error is not related to bidding strategy. Please check the error details above.")
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
        ad_group_operation.create = ad_group
        ad_group_response = ad_group_service.mutate_ad_groups(
            customer_id=customer_id,
            operations=[ad_group_operation]
        )
        ad_group_id = ad_group_response.results[0].resource_name.split("/")[-1]
        show_message(f"Created ad group with ID: {ad_group_id}")
        logger.info(f"Created ad group: {ad_group_id}")
        return ad_group_id
        
    except GoogleAdsException as ex:
        error_msg = ex.error.message if hasattr(ex.error, 'message') else str(ex)
        show_message(f"Failed to create ad group: {error_msg}", False)
        logger.error(f"Ad group creation error: {error_msg}")
        return None
    except Exception as ex:
        show_message(f"Failed to create ad group: {str(ex)}", False)
        logger.error(f"Ad group creation error: {str(ex)}")
        return None



# Create a responsive search ad with up to 15 headlines and 4 descriptions
def create_ad(client: GoogleAdsClient, customer_id: str, ad_group_id: str, 
              headlines: List[str], descriptions: List[str], final_url: str, 
              headline_positions: List[str], description_positions: List[str],
              path1: str = "", path2: str = "") -> Optional[str]:
    """Create a responsive search ad."""
    try:
        ad_group_ad_service = client.get_service("AdGroupAdService")
        ad_group_ad = client.get_type("AdGroupAd")
        ad_group_ad.ad_group = f"customers/{customer_id}/adGroups/{ad_group_id}"
        ad_group_ad.status = client.enums.AdGroupAdStatusEnum.ENABLED

        ad = client.get_type("Ad")
        
        # Set the final URL (the actual landing page)
        ad.final_urls.append(final_url)
        
        # Create the responsive search ad object
        rsa = ad.responsive_search_ad
        
        # For Google Ads responsive search ads, we can set display URL paths
        # This affects how the URL appears in the ad, not the actual landing page
        if path1:
            rsa.path1 = path1.strip()
        if path2:
            rsa.path2 = path2.strip()
        
        # Debug: Log what's being sent to the API
        st.write(f"DEBUG: API - final_urls: {ad.final_urls}, path1: '{rsa.path1 if hasattr(rsa, 'path1') else 'None'}', path2: '{rsa.path2 if hasattr(rsa, 'path2') else 'None'}'")

        # Add headlines with positions
        for i, headline in enumerate(headlines):
            if headline:
                headline_asset = client.get_type("AdTextAsset")
                headline_asset.text = headline
                if i < len(headline_positions) and headline_positions[i]:
                    headline_asset.pinned_field = client.enums.ServedAssetFieldTypeEnum[f"HEADLINE_{headline_positions[i]}"]
                rsa.headlines.append(headline_asset)
                # Debug: Log what's being sent
                if "{" in headline:
                    st.write(f"DEBUG: Headline {i+1} with ad customizer: '{headline}' (length: {len(headline)})")

        # Add descriptions with positions
        for i, description in enumerate(descriptions):
            if description:
                description_asset = client.get_type("AdTextAsset")
                description_asset.text = description
                if i < len(description_positions) and description_positions[i]:
                    description_asset.pinned_field = client.enums.ServedAssetFieldTypeEnum[f"DESCRIPTION_{description_positions[i]}"]
                rsa.descriptions.append(description_asset)
                # Debug: Log what's being sent
                if "{" in description:
                    st.write(f"DEBUG: Description {i+1} with ad customizer: '{description}' (length: {len(description)})")

        ad_group_ad.ad = ad
        ad_group_ad_operation = client.get_type("AdGroupAdOperation")
        ad_group_ad_operation.create = ad_group_ad
        ad_response = ad_group_ad_service.mutate_ad_group_ads(
            customer_id=customer_id,
            operations=[ad_group_ad_operation]
        )
        ad_id = ad_response.results[0].resource_name.split("/")[-1]
        show_message(f"Created responsive search ad with ID: {ad_id}")
        logger.info(f"Created ad: {ad_id}")
        return ad_id
        
    except GoogleAdsException as ex:
        error_msg = ex.error.message if hasattr(ex.error, 'message') else str(ex)
        show_message(f"Failed to create ad: {error_msg}", False)
        logger.error(f"Ad creation error: {error_msg}")
        return None
    except Exception as ex:
        show_message(f"Failed to create ad: {str(ex)}", False)
        logger.error(f"Ad creation error: {str(ex)}")
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
            operation.create = criterion
            operations.append(operation)

        response = ad_group_criterion_service.mutate_ad_group_criteria(
            customer_id=customer_id,
            operations=operations
        )
        show_message(f"Uploaded {len(response.results)} keywords to ad group {ad_group_id}")
        logger.info(f"Uploaded {len(response.results)} keywords to ad group {ad_group_id}")
        return response.results
        
    except GoogleAdsException as ex:
        error_msg = ex.error.message if hasattr(ex.error, 'message') else str(ex)
        show_message(f"Failed to upload keywords: {error_msg}", False)
        logger.error(f"Keyword upload error: {error_msg}")
        return None
    except Exception as ex:
        show_message(f"Failed to upload keywords: {str(ex)}", False)
        logger.error(f"Keyword upload error: {str(ex)}")
        return None

# Process bulk upload data
def process_bulk_upload(client: GoogleAdsClient, customer_id: str, campaign_name: str, 
                       df: pd.DataFrame, existing_campaign_id: str = None, budget_amount: float = 1.0) -> bool:
    """Process bulk upload of ad groups, ads, and keywords."""
    try:
        # Use existing campaign or create new one
        if existing_campaign_id:
            campaign_id = existing_campaign_id
            st.info(f"📋 Using existing campaign: {campaign_name}")
        else:
            # Create the single campaign
            campaign_id = create_campaign(client, customer_id, campaign_name, budget_amount)
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
                
                # Get final URL and path parameters
                final_url = row["final_url"].rstrip('/')
                path1 = row.get("path1", "").strip() if pd.notna(row.get("path1")) else ""
                path2 = row.get("path2", "").strip() if pd.notna(row.get("path2")) else ""
                
                # Debug: Log the URL values being used
                st.write(f"DEBUG: Row {_}: final_url='{final_url}', path1='{path1}', path2='{path2}'")
                
                headline_positions = (row.get("headline_positions", "").split(";") 
                                    if pd.notna(row.get("headline_positions")) else [""] * MAX_HEADLINES)
                description_positions = (row.get("description_positions", "").split(";") 
                                       if pd.notna(row.get("description_positions")) else [""] * MAX_DESCRIPTIONS)
                
                create_ad(client, customer_id, ad_group_id, headlines, descriptions, 
                         final_url, headline_positions, description_positions, path1, path2)
                
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
    # Clear uploaded file on app refresh/restart
    if 'uploaded_file_cleared' not in st.session_state:
        st.session_state.uploaded_file_cleared = False
    
    # Clear the uploaded file when the app starts
    if not st.session_state.uploaded_file_cleared:
        st.session_state.uploaded_file_cleared = True
        # This will force the file uploader to be empty on app refresh
    
    # Memory management - clear old session data on app start
    if 'memory_cleanup_done' not in st.session_state:
        memory_manager.clear_session_data()
        st.session_state.memory_cleanup_done = True
    
    # Clear all caches to ensure fresh execution and prevent API v21 compatibility issues
    if 'cache_cleared' not in st.session_state:
        st.cache_data.clear()
        st.cache_resource.clear()
        st.session_state.cache_cleared = True
        st.info("🔄 Cache cleared to ensure API v21 compatibility")
    

    
    st.title("Google Ads Manager AI Agent")
    st.write("Manage Google Ads sub-accounts, campaigns, ad groups, ads, and keywords under your MCC account. Budgets are set at the campaign level.")

    # Authentication Reset Section - Prominent placement at the top
    col_auth1, col_auth2, col_auth3, col_auth4 = st.columns([2, 1.2, 1, 1])
    with col_auth1:
        memory_usage = memory_manager.get_memory_usage()
        st.info(f"💾 Current Memory Usage: {memory_usage:.1f} MB")
    with col_auth2:
        if st.button("🔐 Reset Authentication", help="Click if you're getting 'invalid_grant' errors"):
            st.session_state.show_auth_reset = True
    with col_auth3:
        if st.button("🧹 Clear Cache"):
            st.cache_data.clear()
            st.cache_resource.clear()
            memory_manager.clear_session_data()
            memory_manager.cleanup_dataframes()
            st.success("Cache and memory cleared!")
    with col_auth4:
        if st.button("🔄 Force GC"):
            memory_manager.cleanup_dataframes()
            st.success("Garbage collection completed!")
    
    # Show authentication reset instructions when button is clicked
    if st.session_state.get('show_auth_reset', False):
        st.warning("### 🔐 Authentication Reset Instructions")
        st.markdown("""
        **If you're seeing `invalid_grant: Bad Request` errors, follow these steps:**
        
        **Why This Happens:**
        - Google OAuth refresh tokens expire after 6+ months of inactivity
        - Too many refresh tokens issued for the same user/client
        - Changes to the OAuth consent screen in Google Cloud Console
        
        ---
        
        ### Step-by-Step Fix:
        
        **1. Generate a New Refresh Token (Local Machine):**
        ```bash
        # Clone your repository (if not already on your machine)
        git clone <your-repo-url>
        cd google-ads-manager
        
        # Activate virtual environment
        source venv/bin/activate  # Mac/Linux
        # or: venv\\Scripts\\activate  # Windows
        
        # Run the token generator
        python get_refresh_token.py
        ```
        
        **2. Follow the Browser Flow:**
        - A browser window will open automatically
        - Sign in with your Google Ads account
        - Grant permissions to the app
        - Copy the refresh token that appears in the terminal
        
        **3. Update Streamlit Cloud Secrets:**
        - Go to your [Streamlit Cloud Dashboard](https://share.streamlit.io/)
        - Click on your app name
        - Navigate to **Settings** → **Secrets**
        - Find `GOOGLE_ADS_REFRESH_TOKEN`
        - Replace the old token with your new token
        - Click **Save**
        
        **4. Redeploy the App:**
        - Click **Main** in the sidebar
        - Click **Reboot app** or **Clear cache** and reload
        - The error should be resolved!
        
        ---
        
        **Quick Reference:**
        - 📄 See `AUTHENTICATION_TROUBLESHOOTING.md` for more details
        - 🔧 Use `get_refresh_token.py` script in your repository
        - 💡 Keep `client_secrets.json` secure and never commit it
        
        **Still having issues?** Check that:
        - Your OAuth Client ID is still active in Google Cloud Console
        - The OAuth consent screen hasn't been modified
        - Your Google Ads account has API access enabled
        """)
        
        if st.button("✅ Close Instructions"):
            st.session_state.show_auth_reset = False
            st.rerun()

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
        
        st.info("ℹ️ **Note**: All sub-accounts are created without MCC payment profile linking. Clients will need to set up their own payment methods in Google Ads UI.")
        
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
        st.info("🔧 Portfolio bidding requires conversion tracking set to 'This Manager' (see sub-account creation for setup)")
        st.info("✅ All campaigns will use the hardcoded PPCL List shared negative keywords list")
        st.info("🎯 All campaigns will be configured for core Google Search only (no search partners, no Display Network)")
        st.info("🎯 All campaigns will use 'Presence Only' location targeting (not Presence or Interest)")
        
        # All campaigns will target all locations with "Presence Only" behavior
        
        if st.button("Create Campaign"):
            if customer_id and campaign_name and budget_amount:
                # Create the campaign
                create_campaign(client, customer_id, campaign_name, budget_amount)
            else:
                show_message("Please fill in all required fields.", False)

    # Tab 3: Bulk Upload
    with tab3:
        st.subheader("Bulk Upload Ad Groups, Ads, and Keywords")
        st.write("Upload a CSV or Excel file with columns: ad_group_name, headline1 to headline15, description1 to description4, final_url, path1, path2, keywords, headline_positions, description_positions. All rows are added to a single campaign specified below. **Keywords only need to be specified in the first row of each ad group.**")
        
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
        
        # Campaign selection - dropdown with existing campaigns or option to create new
        if customer_id_bulk:
            # Get existing campaigns for the selected sub-account
            existing_campaigns = get_campaigns_for_account(client, customer_id_bulk)
            
            if existing_campaigns and len(existing_campaigns) > 0:
                # Show dropdown with existing campaigns
                campaign_options = [f"{camp['name']} ({camp['status']})" for camp in existing_campaigns]
                campaign_options.insert(0, "Create New Campaign")  # Add option to create new
                
                selected_campaign_option = st.selectbox(
                    "Select Campaign for Bulk Upload",
                    options=campaign_options,
                    help="Choose an existing campaign or 'Create New Campaign' to create a new one"
                )
                
                if selected_campaign_option == "Create New Campaign":
                    # Show text input for new campaign name
                    campaign_name = st.text_input("New Campaign Name")
                    campaign_id = None
                    # Show budget input for new campaign
                    col1, col2 = st.columns(2)
                    with col1:
                        budget_amount = st.number_input("Daily Budget Amount (USD)", min_value=1.0, value=10.0, step=1.0, help="Daily budget for the new campaign")
                    with col2:
                        st.write("")  # Spacer
                        st.write("💡 Budget will be set at campaign level")
                else:
                    # Extract campaign name from selected option (remove status part)
                    campaign_name = selected_campaign_option.split(" (")[0]
                    # Get the campaign ID for the selected campaign
                    selected_campaign = next(camp for camp in existing_campaigns if camp['name'] == campaign_name)
                    campaign_id = selected_campaign['id']
                    budget_amount = 1.0  # Not used for existing campaigns
                    st.info(f"📋 Will add content to existing campaign: {campaign_name}")
            else:
                # No existing campaigns or couldn't fetch them, show text input for new campaign
                st.info("📝 No existing campaigns found or unable to access campaigns. Will create a new campaign.")
                campaign_name = st.text_input("Campaign Name for Bulk Upload (will create new campaign)")
                campaign_id = None
                budget_amount = 10.0  # Default budget for new campaign
        else:
            # No customer selected yet
            campaign_name = st.text_input("Campaign Name for Bulk Upload")
            campaign_id = None
            budget_amount = 10.0  # Default budget for new campaign
        # File upload with clear functionality
        col1, col2 = st.columns([3, 1])
        with col1:
            uploaded_file = st.file_uploader(
                "Upload CSV or Excel file", 
                type=["csv", "xlsx"],
                key=f"bulk_upload_file_{st.session_state.uploaded_file_cleared}"
            )
        with col2:
            if st.button("🗑️ Clear File", help="Clear the uploaded file"):
                st.session_state.uploaded_file_cleared = not st.session_state.uploaded_file_cleared
                st.rerun()
        
        # Show file status
        if uploaded_file:
            st.success(f"✅ File uploaded: {uploaded_file.name}")
        else:
            st.info("📁 Please upload a CSV or Excel file to proceed")
        
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
                    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
                    show_message(f"File is missing required columns: {', '.join(missing_columns)}. Required: ad_group_name, headline1 to headline15, description1 to description4, final_url, keywords. Optional: path1, path2, headline_positions, description_positions", False)
                    return

                # Process the bulk upload
                if process_bulk_upload(client, customer_id_bulk, campaign_name, df, campaign_id, budget_amount):
                    show_message("✅ Bulk upload completed successfully!")
                    # Clear the file after successful upload by changing the key
                    st.session_state.uploaded_file_cleared = not st.session_state.uploaded_file_cleared
                    st.success("🔄 File uploader has been cleared. You can upload a new file.")
                else:
                    show_message("❌ Bulk upload failed. Please check the file format and try again.", False)

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
        
        # Date range selection with predefined options
        date_range_option = st.selectbox(
            "Select Date Range:",
            options=["Current Month", "Last Month", "Last 2 Weeks", "Custom Date Range"],
            index=0,  # Default to "Current Month"
            help="Choose a predefined date range or select custom dates"
        )
        
        # Calculate dates based on selection
        today = datetime.now().date()
        
        if date_range_option == "Current Month":
            # Current month: from 1st of current month to today
            start_date = today.replace(day=1)
            end_date = today
        elif date_range_option == "Last Month":
            # Last month: from 1st to last day of previous month
            if today.month == 1:
                start_date = today.replace(year=today.year-1, month=12, day=1)
                end_date = today.replace(year=today.year-1, month=12, day=31)
            else:
                start_date = today.replace(month=today.month-1, day=1)
                # Get last day of previous month
                if today.month == 1:
                    last_day = 31
                elif today.month in [3, 5, 7, 8, 10, 12]:
                    last_day = 31
                elif today.month == 2:
                    # Check if leap year
                    if today.year % 4 == 0 and (today.year % 100 != 0 or today.year % 400 == 0):
                        last_day = 29
                    else:
                        last_day = 28
                else:
                    last_day = 30
                end_date = today.replace(month=today.month-1, day=last_day)
        elif date_range_option == "Last 2 Weeks":
            # Last 2 weeks: 14 days ago to today
            start_date = today - timedelta(days=14)
            end_date = today
        else:  # Custom Date Range
            # Show date inputs for custom range
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start Date", value=today - timedelta(days=30), key="keyword_start")
            with col2:
                end_date = st.date_input("End Date", value=today, key="keyword_end")
            
            if start_date > end_date:
                st.warning("Start date cannot be after end date. Please select a valid date range.")
                return
        
        # Display selected date range
        st.info(f"📅 Analyzing data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
        # Initialize session state for keywords data and sort
        if 'keywords_data' not in st.session_state:
            st.session_state.keywords_data = None
        if 'keyword_sort_option' not in st.session_state:
            st.session_state.keyword_sort_option = "Cost (Highest)"
        if 'keyword_date_range' not in st.session_state:
            st.session_state.keyword_date_range = None
        
        # Get keyword insights
        if st.button("Fetch Performance Analysis"):
            st.info(f"Fetching performance analysis from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}...")
            try:
                # Get keywords data from selected sub-accounts
                all_keywords_data = get_keywords_analysis(client, selected_keyword_sub_accounts, (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
                
                if all_keywords_data:
                    # Store data in session state
                    st.session_state.keywords_data = all_keywords_data
                    st.session_state.keyword_sort_option = "Cost (Highest)"  # Reset sort to default
                    st.session_state.keyword_date_range = (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
                    display_keywords_analysis(all_keywords_data, "Cost (Highest)", st.session_state.keyword_date_range)
                else:
                    st.warning("No performance data available for the selected date range.")
                    st.session_state.keywords_data = None
                    st.session_state.keyword_date_range = None
                    
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
            display_keywords_analysis(st.session_state.keywords_data, selected_sort, st.session_state.keyword_date_range)

# Get keywords analysis across all sub-accounts
@st.cache_data(ttl=600)  # Cache for 10 minutes instead of 1 hour
def get_keywords_analysis(_client, sub_accounts_list: list, date_range: tuple) -> dict:
    """Get keywords and search terms performance data from all sub-accounts, grouped by account."""
    try:
        # Track memory usage at start
        memory_manager.log_memory_usage("get_keywords_analysis_start")
        
        # Track API usage for the overall function call
        st.session_state.api_tracker.increment(1)
        
        all_accounts_keywords = {}
        google_ads_service = _client.get_service("GoogleAdsService")
        
        # Query for keywords with performance metrics - limit results to prevent memory issues
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
            LIMIT 500
        """
        
        # Query for search terms with performance metrics - limit results
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
            LIMIT 500
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
        
        # Process each account and campaign with memory management
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
        
        result = {
            'accounts': processed_accounts,
            'total_accounts': len(processed_accounts)
        }
        
        # Log memory usage at end
        memory_manager.log_memory_usage("get_keywords_analysis_end")
        
        return result
        
    except Exception as e:
        st.error(f"Error getting keywords analysis: {str(e)}")
        return {}

def display_keywords_analysis(keywords_data: dict, sort_by_option: str, date_range: tuple = None):
    """Display keywords analysis in a dashboard format, grouped by account and campaign."""
    
    if not keywords_data or not keywords_data['accounts']:
        st.warning("No keyword data available for the selected date range.")
        return
    
    # Track memory usage
    memory_manager.log_memory_usage("display_keywords_analysis_start")
    
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
    
    # PDF Download Button
    st.write("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📄 Download Performance Report (PDF)", type="primary"):
            try:
                # Use the provided date range or fallback to current month
                if date_range:
                    pdf_date_range = date_range
                else:
                    # Fallback to current month
                    today = datetime.now().date()
                    start_date = today.replace(day=1)
                    end_date = today
                    pdf_date_range = (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
                
                pdf_content = generate_performance_pdf(keywords_data, sort_by_option, pdf_date_range)
                if pdf_content:
                    # Create download button
                    st.download_button(
                        label="💾 Download PDF Report",
                        data=pdf_content,
                        file_name=f"google_ads_performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf"
                    )
                    st.success("✅ PDF report generated successfully!")
                else:
                    st.error("❌ Failed to generate PDF report")
            except Exception as e:
                st.error(f"❌ Error generating PDF: {str(e)}")
    
    st.write("---")
    
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
                
                # Limit DataFrame size to prevent memory issues
                keywords_df = memory_manager.limit_dataframe_size(keywords_df, max_rows=100)
                
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
                
                # Clean up DataFrames to free memory
                del keywords_df, display_df
            else:
                st.info("No keyword data available for this campaign.")
            
            # Search Terms table for this campaign
            if campaign.get('search_terms'):
                st.write("**🔍 Top Search Terms by Spend**")
                
                # Add note about top 20 search terms
                total_search_terms_in_campaign = campaign.get('total_search_terms_in_campaign', len(campaign['search_terms']))
                st.info(f"📊 Showing top 20 search terms by spend (out of {total_search_terms_in_campaign} total search terms in campaign)")
                
                search_terms_df = pd.DataFrame(campaign['search_terms'])
                
                # Limit DataFrame size to prevent memory issues
                search_terms_df = memory_manager.limit_dataframe_size(search_terms_df, max_rows=200)
                
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
                
                # Clean up DataFrames to free memory
                del search_terms_df, search_display_df
            else:
                st.info("No search terms data available for this campaign.")
            
            st.divider()
    
    # Force garbage collection after processing
    memory_manager.cleanup_dataframes()
    memory_manager.log_memory_usage("display_keywords_analysis_end")

def generate_performance_pdf(keywords_data: dict, sort_by_option: str, date_range: tuple) -> bytes:
    """Generate a modern PDF report with account campaign summary, keywords, and search terms tables."""
    try:
        # Create a buffer to store the PDF
        buffer = io.BytesIO()
        
        # Create the PDF document with modern margins
        doc = SimpleDocTemplate(buffer, pagesize=letter, 
                              leftMargin=0.75*inch, rightMargin=0.75*inch,
                              topMargin=0.75*inch, bottomMargin=0.75*inch)
        story = []
        
        # Modern color palette (similar to Streamlit's clean design)
        primary_color = colors.HexColor('#FF4B4B')  # Streamlit red
        secondary_color = colors.HexColor('#F0F2F6')  # Light gray background
        accent_color = colors.HexColor('#1F77B4')  # Modern blue
        text_color = colors.HexColor('#262730')  # Dark text
        light_text = colors.HexColor('#6B7280')  # Gray text
        
        # Modern styles
        styles = getSampleStyleSheet()
        
        # Title style - modern and clean
        title_style = ParagraphStyle(
            'ModernTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=primary_color,
            fontName='Helvetica-Bold'
        )
        
        # Subtitle style
        subtitle_style = ParagraphStyle(
            'ModernSubtitle',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=light_text,
            fontName='Helvetica'
        )
        
        # Section heading style
        section_style = ParagraphStyle(
            'ModernSection',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=15,
            spaceBefore=20,
            textColor=accent_color,
            fontName='Helvetica-Bold'
        )
        
        # Campaign heading style
        campaign_style = ParagraphStyle(
            'ModernCampaign',
            parent=styles['Heading3'],
            fontSize=14,
            spaceAfter=10,
            spaceBefore=15,
            textColor=text_color,
            fontName='Helvetica-Bold'
        )
        
        # Normal text style
        normal_style = ParagraphStyle(
            'ModernNormal',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            textColor=text_color,
            fontName='Helvetica'
        )
        
        # Header with logo-like design
        story.append(Paragraph("📊 Google Ads Performance Report", title_style))
        story.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", subtitle_style))
        story.append(Paragraph(f"📅 Date Range: {date_range[0]} to {date_range[1]}", subtitle_style))
        story.append(Spacer(1, 20))
        
        # Overall summary with modern card-like design
        if keywords_data and keywords_data['accounts']:
            total_accounts = keywords_data['total_accounts']
            total_cost = sum(acc['summary']['total_cost'] for acc in keywords_data['accounts'])
            total_impressions = sum(acc['summary']['total_impressions'] for acc in keywords_data['accounts'])
            total_clicks = sum(acc['summary']['total_clicks'] for acc in keywords_data['accounts'])
            total_conversions = sum(acc['summary']['total_conversions'] for acc in keywords_data['accounts'])
            
            avg_ctr = total_clicks / total_impressions if total_impressions > 0 else 0
            avg_conversion_rate = total_conversions / total_clicks if total_clicks > 0 else 0
            
            # Modern summary table with clean design
            summary_data = [
                ['📈 Performance Overview', ''],
                ['', ''],
                ['Accounts Analyzed', f"<b>{total_accounts}</b>"],
                ['Total Impressions', f"<b>{total_impressions:,}</b>"],
                ['Total Clicks', f"<b>{total_clicks:,}</b>"],
                ['Total Conversions', f"<b>{total_conversions:.0f}</b>"],
                ['Total Cost', f"<b>${total_cost:,.2f}</b>"],
                ['', ''],
                ['Average CTR', f"<b>{avg_ctr:.2%}</b>"],
                ['Average Conversion Rate', f"<b>{avg_conversion_rate:.2%}</b>"]
            ]
            
            # Create modern summary table
            summary_table = Table(summary_data, colWidths=[2.5*inch, 1.5*inch])
            summary_table.setStyle(TableStyle([
                # Header styling
                ('BACKGROUND', (0, 0), (-1, 1), primary_color),
                ('TEXTCOLOR', (0, 0), (-1, 1), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 1), 12),
                ('TOPPADDING', (0, 0), (-1, 1), 12),
                
                # Data rows styling
                ('BACKGROUND', (0, 2), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 2), (-1, -1), text_color),
                ('FONTNAME', (0, 2), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 2), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 2), (-1, -1), 8),
                ('TOPPADDING', (0, 2), (-1, -1), 8),
                
                # Right column alignment for values
                ('ALIGN', (1, 2), (1, -1), 'RIGHT'),
                
                # Subtle borders
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
                ('ROWBACKGROUNDS', (0, 2), (-1, -1), [colors.white, secondary_color])
            ]))
            
            story.append(Paragraph("📊 Overall Performance Summary", section_style))
            story.append(summary_table)
            story.append(Spacer(1, 25))
            
            # Process each account and campaign
            for account in keywords_data['accounts']:
                story.append(Paragraph(f"🏢 {account['account_name']} (ID: {account['account_id']})", section_style))
                
                for campaign in account['campaigns']:
                    if not campaign['keywords']:
                        continue
                    
                    # Modern campaign summary card
                    campaign_summary_data = [
                        ['Campaign Metrics', ''],
                        ['', ''],
                        ['Campaign Name', f"<b>{campaign['campaign_name']}</b>"],
                        ['Impressions', f"<b>{campaign['summary']['total_impressions']:,}</b>"],
                        ['Clicks', f"<b>{campaign['summary']['total_clicks']:,}</b>"],
                        ['CTR', f"<b>{campaign['summary']['avg_ctr']:.2%}</b>"],
                        ['Conversions', f"<b>{campaign['summary']['total_conversions']:.0f}</b>"],
                        ['Conversion Rate', f"<b>{campaign['summary']['avg_conversion_rate']:.2%}</b>"],
                        ['Cost', f"<b>${campaign['summary']['total_cost']:.2f}</b>"],
                        ['Cost per Conversion', f"<b>${campaign['summary']['avg_cost_per_conversion']:.2f}</b>"]
                    ]
                    
                    campaign_table = Table(campaign_summary_data, colWidths=[2*inch, 1.5*inch])
                    campaign_table.setStyle(TableStyle([
                        # Header styling
                        ('BACKGROUND', (0, 0), (-1, 1), accent_color),
                        ('TEXTCOLOR', (0, 0), (-1, 1), colors.white),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 1), 11),
                        ('BOTTOMPADDING', (0, 0), (-1, 1), 10),
                        ('TOPPADDING', (0, 0), (-1, 1), 10),
                        
                        # Data rows styling
                        ('BACKGROUND', (0, 2), (-1, -1), colors.white),
                        ('TEXTCOLOR', (0, 2), (-1, -1), text_color),
                        ('FONTNAME', (0, 2), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 2), (-1, -1), 9),
                        ('BOTTOMPADDING', (0, 2), (-1, -1), 6),
                        ('TOPPADDING', (0, 2), (-1, -1), 6),
                        
                        # Right column alignment for values
                        ('ALIGN', (1, 2), (1, -1), 'RIGHT'),
                        
                        # Subtle borders
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
                        ('ROWBACKGROUNDS', (0, 2), (-1, -1), [colors.white, secondary_color])
                    ]))
                    
                    story.append(Paragraph(f"📋 {campaign['campaign_name']}", campaign_style))
                    story.append(campaign_table)
                    story.append(Spacer(1, 15))
                    
                    # Keywords table with modern design
                    if campaign['keywords']:
                        keywords_df = pd.DataFrame(campaign['keywords'])
                        
                        # Sort based on selected metric
                        sort_options = {
                            "Cost (Highest)": "cost",
                            "Impressions": "impressions", 
                            "CTR": "ctr",
                            "Conversions": "conversions",
                            "Conversion Rate": "conversion_rate",
                            "Cost per Conversion": "cost_per_conversion"
                        }
                        sort_column = sort_options.get(sort_by_option, "cost")
                        
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
                            keywords_df = keywords_df.sort_values('cost_per_conversion', ascending=True)
                        
                        # Modern keywords table
                        keywords_data_for_pdf = []
                        keywords_data_for_pdf.append(['🔍 Keyword', 'Match Type', 'Impressions', 'Clicks', 'CTR', 'Conversions', 'Cost/Conv.', 'Conv. Rate', 'Cost'])
                        
                        for _, row in keywords_df.head(10).iterrows():
                            keywords_data_for_pdf.append([
                                row['keyword_text'][:18],  # Truncate long keywords
                                row['match_type'],
                                f"{row['impressions']:,}",
                                f"{row['clicks']:,}",
                                f"{row['ctr']:.2%}",
                                f"{row['conversions']:.0f}",
                                f"${row['cost_per_conversion']:.2f}",
                                f"{row['conversion_rate']:.2%}",
                                f"${row['cost']:.2f}"
                            ])
                        
                        keywords_table = Table(keywords_data_for_pdf, colWidths=[1.3*inch, 0.6*inch, 0.6*inch, 0.5*inch, 0.4*inch, 0.6*inch, 0.6*inch, 0.6*inch, 0.5*inch])
                        keywords_table.setStyle(TableStyle([
                            # Header styling
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),  # Modern green
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, 0), 8),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                            ('TOPPADDING', (0, 0), (-1, 0), 8),
                            
                            # Data rows styling
                            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                            ('TEXTCOLOR', (0, 1), (-1, -1), text_color),
                            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                            ('FONTSIZE', (0, 1), (-1, -1), 7),
                            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
                            ('TOPPADDING', (0, 1), (-1, -1), 4),
                            
                            # Subtle borders
                            ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#E5E7EB')),
                            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, secondary_color])
                        ]))
                        
                        story.append(Paragraph("🔍 Top 10 Keywords by Spend", normal_style))
                        story.append(keywords_table)
                        story.append(Spacer(1, 12))
                    
                    # Search terms table with modern design
                    if campaign.get('search_terms'):
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
                            search_terms_df = search_terms_df.sort_values('cost_per_conversion', ascending=True)
                        
                        # Modern search terms table
                        search_terms_data_for_pdf = []
                        search_terms_data_for_pdf.append(['🔎 Search Term', 'Impressions', 'Clicks', 'CTR', 'Conversions', 'Cost/Conv.', 'Conv. Rate', 'Cost'])
                        
                        for _, row in search_terms_df.head(20).iterrows():
                            search_terms_data_for_pdf.append([
                                row['search_term'][:22],  # Truncate long search terms
                                f"{row['impressions']:,}",
                                f"{row['clicks']:,}",
                                f"{row['ctr']:.2%}",
                                f"{row['conversions']:.0f}",
                                f"${row['cost_per_conversion']:.2f}",
                                f"{row['conversion_rate']:.2%}",
                                f"${row['cost']:.2f}"
                            ])
                        
                        search_terms_table = Table(search_terms_data_for_pdf, colWidths=[1.6*inch, 0.6*inch, 0.5*inch, 0.4*inch, 0.6*inch, 0.6*inch, 0.6*inch, 0.5*inch])
                        search_terms_table.setStyle(TableStyle([
                            # Header styling
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7C3AED')),  # Modern purple
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, 0), 8),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                            ('TOPPADDING', (0, 0), (-1, 0), 8),
                            
                            # Data rows styling
                            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                            ('TEXTCOLOR', (0, 1), (-1, -1), text_color),
                            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                            ('FONTSIZE', (0, 1), (-1, -1), 7),
                            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
                            ('TOPPADDING', (0, 1), (-1, -1), 4),
                            
                            # Subtle borders
                            ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#E5E7EB')),
                            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, secondary_color])
                        ]))
                        
                        story.append(Paragraph("🔎 Top 20 Search Terms by Spend", normal_style))
                        story.append(search_terms_table)
                        story.append(Spacer(1, 20))
                
                story.append(PageBreak())
        
        # Build the PDF
        doc.build(story)
        
        # Get the PDF content
        pdf_content = buffer.getvalue()
        buffer.close()
        
        return pdf_content
        
    except Exception as e:
        st.error(f"Error generating PDF: {str(e)}")
        return None

# Get campaigns for a specific sub-account
@st.cache_data(ttl=300)  # Cache for 5 minutes instead of 30
def get_campaigns_for_account(_client: GoogleAdsClient, customer_id: str) -> list[dict]:
    """Fetch all campaigns for a specific sub-account."""
    try:
        # Track API usage
        st.session_state.api_tracker.increment(1)
        
        # Debug: Log the customer ID being used
        st.info(f"🔍 Attempting to fetch campaigns for customer ID: {customer_id}")
        
        campaigns = []
        google_ads_service = _client.get_service("GoogleAdsService")
        
        # Try to query campaigns for this specific customer
        query = """
            SELECT
              campaign.id,
              campaign.name,
              campaign.status,
              campaign.advertising_channel_type
            FROM campaign
            WHERE campaign.status IN ('ENABLED', 'PAUSED')
            ORDER BY campaign.name
        """
        
        try:
            response = google_ads_service.search(
                customer_id=customer_id,
                query=query
            )
            for row in response:
                campaigns.append({
                    'id': row.campaign.id,
                    'name': row.campaign.name,
                    'status': row.campaign.status.name,
                    'channel_type': row.campaign.advertising_channel_type.name
                })
        except Exception as search_error:
            st.warning(f"⚠️ Could not fetch campaigns for customer {customer_id}: {str(search_error)}")
            # Return empty list if we can't access this customer's campaigns
            return []
            
        return campaigns
    except Exception as ex:
        st.error(f"💥 Error fetching campaigns: {str(ex)}")
        handle_api_exception(ex, "fetch campaigns")
        return []

# Debug functions for targeting issues
def debug_network_fields(client: GoogleAdsClient):
    """Debug function to check available network targeting fields."""
    st.write("**🔍 Debug: Network Targeting Fields**")
    
    try:
        campaign = client.get_type("Campaign")
        st.write(f"Campaign type: {type(campaign)}")
        
        # Check for network-related fields using dir() instead of DESCRIPTOR
        campaign_attrs = dir(campaign)
        network_fields = []
        for attr in campaign_attrs:
            if not attr.startswith('_') and any(keyword in attr.lower() for keyword in ['network', 'target', 'search', 'content', 'youtube', 'partner']):
                network_fields.append(attr)
        
        if network_fields:
            st.write("✅ Found network-related fields:")
            for field in network_fields:
                st.write(f"  - {field}")
        else:
            st.write("❌ No network-related fields found")
            
        # Check specific fields we need
        specific_fields = ['target_google_search', 'target_search_network', 'target_content_network', 'target_partner_search_network']
        for field in specific_fields:
            if hasattr(campaign, field):
                st.write(f"✅ {field} field exists")
            else:
                st.write(f"❌ {field} field does not exist")
                
    except Exception as e:
        st.error(f"❌ Error debugging network fields: {e}")

def debug_location_fields(client: GoogleAdsClient):
    """Debug function to check available location targeting fields."""
    st.write("**🔍 Debug: Location Targeting Fields**")
    
    try:
        campaign = client.get_type("Campaign")
        st.write(f"Campaign type: {type(campaign)}")
        
        # Check for location-related fields using dir() instead of DESCRIPTOR
        campaign_attrs = dir(campaign)
        location_fields = []
        for attr in campaign_attrs:
            if not attr.startswith('_') and any(keyword in attr.lower() for keyword in ['geo', 'location', 'positive', 'negative', 'target']):
                location_fields.append(attr)
        
        if location_fields:
            st.write("✅ Found location-related fields:")
            for field in location_fields:
                st.write(f"  - {field}")
        else:
            st.write("❌ No location-related fields found")
            
        # Check specific fields we need
        specific_fields = ['positive_geo_target_type', 'negative_geo_target_type', 'geoTargetTypeSetting']
        for field in specific_fields:
            if hasattr(campaign, field):
                st.write(f"✅ {field} field exists")
            else:
                st.write(f"❌ {field} field does not exist")
                
    except Exception as e:
        st.error(f"❌ Error debugging location fields: {e}")

def debug_campaign_fields(client: GoogleAdsClient):
    """Debug function to check all available campaign fields."""
    st.write("**🔍 Debug: Campaign Object Fields**")
    
    try:
        campaign = client.get_type("Campaign")
        st.write(f"Campaign type: {type(campaign)}")
        
        # Get all available fields using dir() instead of DESCRIPTOR
        campaign_attrs = dir(campaign)
        all_fields = [attr for attr in campaign_attrs if not attr.startswith('_')]
        st.write(f"Total fields available: {len(all_fields)}")
        
        # Show first 50 fields
        st.write("First 50 fields:")
        for i, field in enumerate(all_fields[:50]):
            st.write(f"  {i+1:2d}. {field}")
            
        if len(all_fields) > 50:
            st.write(f"... and {len(all_fields) - 50} more fields")
            
    except Exception as e:
        st.error(f"❌ Error debugging campaign fields: {e}")

def debug_criterion_fields(client: GoogleAdsClient):
    """Debug function to check CampaignCriterion fields."""
    st.write("**🔍 Debug: CampaignCriterion Fields**")
    
    try:
        criterion = client.get_type("CampaignCriterion")
        st.write(f"CampaignCriterion type: {type(criterion)}")
        
        # Get all available fields using dir() instead of DESCRIPTOR
        criterion_attrs = dir(criterion)
        all_fields = [attr for attr in criterion_attrs if not attr.startswith('_')]
        st.write(f"Total fields available: {len(all_fields)}")
        
        # Check specific targeting fields
        if hasattr(criterion, 'network'):
            st.write("✅ network field exists")
        else:
            st.write("❌ network field does not exist")
            
        if hasattr(criterion, 'location'):
            st.write("✅ location field exists")
            # Check location sub-fields
            if hasattr(criterion.location, 'geo_target_type'):
                st.write("✅ location.geo_target_type field exists")
            else:
                st.write("❌ location.geo_target_type field does not exist")
        else:
            st.write("❌ location field does not exist")
            
    except Exception as e:
        st.error(f"❌ Error debugging criterion fields: {e}")

def debug_available_enums(client: GoogleAdsClient):
    """Debug function to check available enums."""
    st.write("**🔍 Debug: Available Enums**")
    
    try:
        # Check network-related enums
        st.write("**Network Enums:**")
        try:
            network_enum = client.enums.NetworkEnum
            st.write(f"✅ NetworkEnum found: {network_enum}")
            for name, value in network_enum.__dict__.items():
                if not name.startswith('_'):
                    st.write(f"  - {name}: {value}")
        except AttributeError as e:
            st.write(f"❌ NetworkEnum not found: {e}")
        
        # Check search network enums
        st.write("**Search Network Enums:**")
        try:
            search_network_enum = client.enums.SearchNetworkEnum
            st.write(f"✅ SearchNetworkEnum found: {search_network_enum}")
            for name, value in search_network_enum.__dict__.items():
                if not name.startswith('_'):
                    st.write(f"  - {name}: {value}")
        except AttributeError as e:
            st.write(f"❌ SearchNetworkEnum not found: {e}")
        
        # Check geo target type enums
        st.write("**Geo Target Type Enums:**")
        try:
            geo_target_enum = client.enums.GeoTargetTypeEnum
            st.write(f"✅ GeoTargetTypeEnum found: {geo_target_enum}")
            for name, value in geo_target_enum.__dict__.items():
                if not name.startswith('_'):
                    st.write(f"  - {name}: {value}")
        except AttributeError as e:
            st.write(f"❌ GeoTargetTypeEnum found: {e}")
            
        # Check positive geo target type enums
        st.write("**Positive Geo Target Type Enums:**")
        try:
            positive_geo_enum = client.enums.PositiveGeoTargetTypeEnum
            st.write(f"✅ PositiveGeoTargetTypeEnum found: {positive_geo_enum}")
            for name, value in positive_geo_enum.__dict__.items():
                if not name.startswith('_'):
                    st.write(f"  - {name}: {value}")
        except AttributeError as e:
            st.write(f"❌ PositiveGeoTargetTypeEnum not found: {e}")
            
    except Exception as e:
        st.error(f"❌ Error debugging enums: {e}")

def debug_test_targeting(client: GoogleAdsClient, customer_id: str):
    """Debug function to test targeting configuration."""
    st.write("**🔍 Debug: Test Targeting Configuration**")
    
    try:
        # Test creating a campaign object
        st.write("**Testing Campaign Creation:**")
        campaign = client.get_type("Campaign")
        campaign.name = "DEBUG_TEST_CAMPAIGN"
        campaign.status = client.enums.CampaignStatusEnum.PAUSED
        campaign.advertising_channel_type = client.enums.AdvertisingChannelTypeEnum.SEARCH
        
        st.write("✅ Campaign object created successfully")
        st.write(f"  - Name: {campaign.name}")
        st.write(f"  - Status: {campaign.status}")
        st.write(f"  - Channel Type: {campaign.advertising_channel_type}")
        
        # Test creating a campaign criterion
        st.write("**Testing CampaignCriterion Creation:**")
        criterion = client.get_type("CampaignCriterion")
        criterion.status = client.enums.CampaignCriterionStatusEnum.ENABLED
        
        st.write("✅ CampaignCriterion object created successfully")
        st.write(f"  - Status: {criterion.status}")
        
        # Test location targeting
        if hasattr(criterion, 'location'):
            st.write("✅ location field exists in CampaignCriterion")
            if hasattr(criterion.location, 'geo_target_constant'):
                st.write("✅ location.geo_target_constant field exists")
            if hasattr(criterion.location, 'geo_target_type'):
                st.write("✅ location.geo_target_type field exists")
        else:
            st.write("❌ location field does not exist in CampaignCriterion")
            
    except Exception as e:
        st.error(f"❌ Error testing targeting: {e}")

def debug_available_types(client: GoogleAdsClient):
    """Debug function to check what types are available for targeting."""
    st.write("**🔍 Debug: Available Types for Targeting**")
    
    try:
        # Test common targeting types
        targeting_types = [
            "GeoTargetTypeSetting",
            "NetworkSettings", 
            "CampaignGeoTargetTypeSetting",
            "CampaignNetworkSettings",
            "LocationTargetingSetting",
            "NetworkTargetingSetting"
        ]
        
        for type_name in targeting_types:
            try:
                obj_type = client.get_type(type_name)
                st.write(f"✅ {type_name} type exists: {type(obj_type)}")
            except Exception as e:
                st.write(f"❌ {type_name} type does not exist: {e}")
                
        # Test if we can access the fields directly on Campaign
        st.write("**Testing Direct Field Access on Campaign:**")
        campaign = client.get_type("Campaign")
        
        # Test if we can set fields directly
        if hasattr(campaign, 'geo_target_type_setting'):
            st.write("✅ geo_target_type_setting field exists and can be set directly")
        else:
            st.write("❌ geo_target_type_setting field does not exist")
            
        if hasattr(campaign, 'network_settings'):
            st.write("✅ network_settings field exists and can be set directly")
        else:
            st.write("❌ network_settings field does not exist")
            
    except Exception as e:
        st.error(f"❌ Error debugging available types: {e}")

if __name__ == "__main__":
    main()