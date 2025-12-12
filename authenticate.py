"""
Google Ads API Authentication Module

Handles OAuth2 authentication and token management.
Supports token generation, refresh, and revocation.
"""

import os
import json
import tempfile
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.ads.googleads.client import GoogleAdsClient
from dotenv import load_dotenv

load_dotenv()

# Try to import streamlit for Cloud deployment
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

# OAuth2 scopes required for Google Ads API and Google Drive
SCOPES = [
    'https://www.googleapis.com/auth/adwords',
    'https://www.googleapis.com/auth/drive.file',  # For saving files to Google Drive
    'https://www.googleapis.com/auth/drive'  # For creating folders and managing Drive files
]

def authenticate():
    """Authenticate and get credentials for Google Ads API."""
    creds = None
    token_file = 'token.json'
    
    # For Streamlit Cloud: Check if token.json is in secrets
    if STREAMLIT_AVAILABLE and hasattr(st, 'secrets'):
        try:
            if 'TOKEN_JSON' in st.secrets:
                # Create temporary token file from secrets
                token_content = st.secrets['TOKEN_JSON']
                if isinstance(token_content, str):
                    # If it's a string, parse it as JSON
                    token_data = json.loads(token_content)
                else:
                    # If it's already a dict
                    token_data = token_content
                
                # Create temporary file
                temp_token = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
                json.dump(token_data, temp_token)
                temp_token.close()
                token_file = temp_token.name
        except Exception as e:
            # Fall back to local file if secrets fail
            pass
    
    # Load existing token if available
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    
    # If no valid credentials, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                if STREAMLIT_AVAILABLE:
                    st.info("🔄 Refreshing expired token...")
                else:
                    print("Refreshing expired token...")
                creds.refresh(Request())
            except Exception as e:
                if STREAMLIT_AVAILABLE:
                    st.error(f"❌ Failed to refresh token: {str(e)}")
                    st.info("💡 You may need to regenerate your refresh token. See authentication docs.")
                else:
                    print(f"ERROR: Failed to refresh token: {e}")
                return None
        else:
            # In Streamlit Cloud, we can't run OAuth flow interactively
            if STREAMLIT_AVAILABLE:
                st.error("❌ No valid token found. Please add TOKEN_JSON secret in Streamlit Cloud settings.")
                st.info("💡 Copy the contents of your local token.json file and add it as TOKEN_JSON secret.")
                return None
            else:
                print("Starting OAuth2 flow...")
                client_secrets_file = 'client_secrets.json'
                
                if not os.path.exists(client_secrets_file):
                    print("ERROR: client_secrets.json not found!")
                    print("Please download OAuth2 credentials from Google Ads API Center")
                    print("and save as 'client_secrets.json' in the project root.")
                    return None
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    client_secrets_file, SCOPES)
                # Use fixed port 8080 for consistent redirect URI
                creds = flow.run_local_server(port=8080)
        
        # Save credentials for future use (only if not using temp file from secrets)
        if not (STREAMLIT_AVAILABLE and hasattr(st, 'secrets') and 'TOKEN_JSON' in st.secrets):
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
            if not STREAMLIT_AVAILABLE:
                print("Token saved successfully!")
    
    return creds

def revoke_token():
    """Revoke the current access token."""
    token_file = 'token.json'
    
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        if creds and creds.refresh_token:
            try:
                creds.revoke(Request())
                print("Token revoked successfully!")
            except Exception as e:
                print(f"Error revoking token: {e}")
        
        # Remove token file
        os.remove(token_file)
        print("Token file removed.")
    else:
        print("No token file found.")

def get_client():
    """Get authenticated Google Ads client."""
    creds = authenticate()
    
    if not creds:
        return None
    
    # Get credentials from environment or Streamlit secrets
    developer_token = None
    client_id = None
    client_secret = None
    login_customer_id = None
    
    # Try Streamlit secrets first (for Cloud deployment)
    if STREAMLIT_AVAILABLE and hasattr(st, 'secrets'):
        try:
            # Access secrets directly (Streamlit Cloud format)
            if 'GOOGLE_ADS_DEVELOPER_TOKEN' in st.secrets:
                developer_token = st.secrets['GOOGLE_ADS_DEVELOPER_TOKEN']
            if 'GOOGLE_ADS_CLIENT_ID' in st.secrets:
                client_id = st.secrets['GOOGLE_ADS_CLIENT_ID']
            if 'GOOGLE_ADS_CLIENT_SECRET' in st.secrets:
                client_secret = st.secrets['GOOGLE_ADS_CLIENT_SECRET']
            if 'GOOGLE_ADS_CUSTOMER_ID' in st.secrets:
                login_customer_id = st.secrets['GOOGLE_ADS_CUSTOMER_ID']
        except Exception as e:
            # Fall back to environment variables
            if STREAMLIT_AVAILABLE:
                st.warning(f"⚠️ Error reading secrets: {str(e)}")
            pass
    
    # Fall back to environment variables if not in secrets
    if not developer_token:
        developer_token = os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN")
    if not client_id:
        client_id = os.getenv("GOOGLE_ADS_CLIENT_ID")
    if not client_secret:
        client_secret = os.getenv("GOOGLE_ADS_CLIENT_SECRET")
    if not login_customer_id:
        login_customer_id = os.getenv("GOOGLE_ADS_CUSTOMER_ID")
    
    # Validate required credentials
    if not developer_token:
        if STREAMLIT_AVAILABLE:
            st.error("❌ Missing GOOGLE_ADS_DEVELOPER_TOKEN in Streamlit secrets. Please add it in Settings → Secrets.")
            st.info("💡 Current value: " + str(developer_token))
        else:
            print("ERROR: Missing GOOGLE_ADS_DEVELOPER_TOKEN in environment variables")
        return None
    
    if not client_id:
        if STREAMLIT_AVAILABLE:
            st.error("❌ Missing GOOGLE_ADS_CLIENT_ID in Streamlit secrets.")
        else:
            print("ERROR: Missing GOOGLE_ADS_CLIENT_ID in environment variables")
        return None
    
    if not client_secret:
        if STREAMLIT_AVAILABLE:
            st.error("❌ Missing GOOGLE_ADS_CLIENT_SECRET in Streamlit secrets.")
        else:
            print("ERROR: Missing GOOGLE_ADS_CLIENT_SECRET in environment variables")
        return None
    
    # Validate developer token format (should not be empty or None)
    if not developer_token or developer_token.strip() == "":
        if STREAMLIT_AVAILABLE:
            st.error("❌ GOOGLE_ADS_DEVELOPER_TOKEN is empty. Please check your Streamlit secrets.")
        return None
    
    # Create Google Ads client configuration
    config = {
        "developer_token": developer_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": creds.refresh_token,
        "use_proto_plus": True
    }
    
    # Add login_customer_id if it's an MCC account (for listing sub-accounts)
    if login_customer_id:
        # Remove dashes for login_customer_id (needs format: 1234567890)
        login_customer_id_numeric = login_customer_id.replace("-", "")
        config["login_customer_id"] = login_customer_id_numeric
    
    try:
        client = GoogleAdsClient.load_from_dict(config)
        return client
    except Exception as e:
        error_msg = str(e)
        if STREAMLIT_AVAILABLE:
            st.error(f"❌ Error creating Google Ads client: {error_msg}")
            # Provide helpful debugging info
            if "DEVELOPER_TOKEN" in error_msg.upper() or "developer token" in error_msg.lower():
                st.info("💡 The developer token may be invalid or not properly set in Streamlit secrets.")
                st.info("💡 Verify GOOGLE_ADS_DEVELOPER_TOKEN is correct in Settings → Secrets.")
        else:
            print(f"Error creating Google Ads client: {e}")
        return None

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--revoke":
        revoke_token()
    else:
        print("Authenticating with Google Ads API...")
        creds = authenticate()
        if creds:
            print("Authentication successful!")
            print(f"Refresh token: {creds.refresh_token[:20]}...")
            print("\nUpdate your .env file with:")
            print(f"GOOGLE_ADS_REFRESH_TOKEN={creds.refresh_token}")

