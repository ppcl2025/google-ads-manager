#!/usr/bin/env python3
"""
Simple Google Ads Token Refresh Script

This script helps you refresh your Google Ads API token when it expires.
Run this whenever you get the "Token has been expired or revoked" error.

Usage:
1. Make sure you have client_secrets.json in this directory
2. Run: python refresh_token_simple.py
3. Follow the browser authentication
4. Copy the new refresh token to your Streamlit Cloud secrets
"""

import os
import sys
from google_auth_oauthlib.flow import InstalledAppFlow

def main():
    print("🔄 Google Ads Token Refresh")
    print("=" * 40)
    
    # Check for client_secrets.json
    if not os.path.exists('client_secrets.json'):
        print("❌ client_secrets.json not found!")
        print("\n📋 To get this file:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Navigate to APIs & Services > Credentials")
        print("3. Find your OAuth 2.0 Client ID")
        print("4. Download the JSON file")
        print("5. Save it as 'client_secrets.json' in this directory")
        print("6. Run this script again")
        sys.exit(1)
    
    try:
        # Define scopes for Google Ads API
        scopes = ["https://www.googleapis.com/auth/adwords"]
        
        # Create OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secrets.json',
            scopes=scopes
        )
        
        print("🌐 Opening browser for authentication...")
        print("Please complete the Google OAuth flow in your browser.")
        print()
        
        # Run local server for authentication
        credentials = flow.run_local_server(
            port=56230,
            prompt='consent',
            access_type='offline'
        )
        
        print("✅ Authentication successful!")
        print("=" * 40)
        print("🔑 Your new refresh token:")
        print("=" * 40)
        print(credentials.refresh_token)
        print("=" * 40)
        
        print("\n📋 Next steps:")
        print("1. Copy the refresh token above")
        print("2. Go to your Streamlit Cloud app settings")
        print("3. Update the GOOGLE_ADS_REFRESH_TOKEN secret")
        print("4. Redeploy your app")
        
        # Save to backup file
        with open('new_refresh_token.txt', 'w') as f:
            f.write(f"Refresh Token: {credentials.refresh_token}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        print("\n💾 Token also saved to 'new_refresh_token.txt'")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Common solutions:")
        print("- Make sure client_secrets.json is valid")
        print("- Check your internet connection")
        print("- Try running the script again")
        print("- Make sure you're using the correct Google account")
        sys.exit(1)

if __name__ == "__main__":
    from datetime import datetime
    main()
