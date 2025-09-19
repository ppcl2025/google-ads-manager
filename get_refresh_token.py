#!/usr/bin/env python3
"""
Google Ads Refresh Token Generator

This script helps you generate a new refresh token for Google Ads API access.
Follow these steps:

1. Download your OAuth client credentials from Google Cloud Console
2. Save the JSON file as 'client_secrets.json' in this directory
3. Run this script: python get_refresh_token.py
4. Follow the browser authentication flow
5. Copy the refresh token and update your Streamlit Cloud secrets

Requirements:
- client_secrets.json file in the same directory
- google-auth-oauthlib package installed
"""

import os
import sys
from google_auth_oauthlib.flow import InstalledAppFlow

def main():
    # Check if client_secrets.json exists
    if not os.path.exists('client_secrets.json'):
        print("❌ Error: client_secrets.json not found!")
        print("\n📋 To fix this:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Navigate to APIs & Services > Credentials")
        print("3. Find your OAuth 2.0 Client ID")
        print("4. Download the JSON file")
        print("5. Save it as 'client_secrets.json' in this directory")
        print("6. Run this script again")
        sys.exit(1)
    
    print("🔐 Google Ads Refresh Token Generator")
    print("=" * 50)
    print("This will open your browser for authentication...")
    print()
    
    try:
        # Define the scopes needed for Google Ads API
        scopes = [
            "https://www.googleapis.com/auth/adwords",
            "https://www.googleapis.com/auth/userinfo.email",
            "openid"
        ]
        
        # Create the OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secrets.json',
            scopes=scopes
        )
        
        # Run the local server for authentication
        print("🌐 Opening browser for authentication...")
        credentials = flow.run_local_server(
            port=56230, 
            prompt='consent',
            access_type='offline'
        )
        
        print("\n✅ Authentication successful!")
        print("=" * 50)
        print("🔑 Your new refresh token:")
        print("=" * 50)
        print(credentials.refresh_token)
        print("=" * 50)
        
        print("\n📋 Next steps:")
        print("1. Copy the refresh token above")
        print("2. Go to your Streamlit Cloud app settings")
        print("3. Update the GOOGLE_ADS_REFRESH_TOKEN secret")
        print("4. Redeploy your app")
        
        # Save token to file for backup
        with open('refresh_token_backup.txt', 'w') as f:
            f.write(f"Refresh Token: {credentials.refresh_token}\n")
            f.write(f"Generated: {credentials.expiry}\n")
        
        print("\n💾 Token also saved to 'refresh_token_backup.txt' for backup")
        
    except Exception as e:
        print(f"❌ Error during authentication: {e}")
        print("\n🔧 Troubleshooting:")
        print("- Make sure client_secrets.json is valid")
        print("- Check your internet connection")
        print("- Try running the script again")
        sys.exit(1)

if __name__ == "__main__":
    main()