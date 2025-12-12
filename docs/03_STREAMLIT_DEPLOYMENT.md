# 3. Streamlit Cloud Deployment Guide

**Documentation Order:** #3 (Getting Started)  
Complete guide for deploying the Google Ads Analyzer to Streamlit Cloud.

## Prerequisites

- GitHub account
- Streamlit Cloud account (free)
- Google Ads API credentials
- Claude API key

## Step 1: Push to GitHub

The code is already in your GitHub repository: `ppcl2025/google-ads-manager`

## Step 2: Configure Streamlit Cloud

1. Go to [Streamlit Cloud](https://share.streamlit.io)
2. Click "New app"
3. Connect your GitHub repository: `ppcl2025/google-ads-manager`
4. Main file path: `google_ads_manager.py` (or `app.py` if you've updated it)
5. Branch: `main`

## Step 3: Configure Secrets

Go to **Settings → Secrets** and add all required secrets:

### Required Secrets

```toml
GOOGLE_ADS_DEVELOPER_TOKEN = "your_developer_token"
GOOGLE_ADS_CLIENT_ID = "your_client_id.apps.googleusercontent.com"
GOOGLE_ADS_CLIENT_SECRET = "your_client_secret"
GOOGLE_ADS_CUSTOMER_ID = "your_customer_id"
ANTHROPIC_API_KEY = "your_claude_api_key"
TOKEN_JSON = """
{
  "token": "your_access_token",
  "refresh_token": "your_refresh_token",
  "token_uri": "https://oauth2.googleapis.com/token",
  "client_id": "your_client_id.apps.googleusercontent.com",
  "client_secret": "your_client_secret",
  "scopes": [
    "https://www.googleapis.com/auth/adwords",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
  ],
  "universe_domain": "googleapis.com",
  "account": "",
  "expiry": "2025-12-12T16:53:25.862942Z"
}
"""
```

### Important Notes

- **TOKEN_JSON format**: Must use triple quotes `"""` for multi-line strings in TOML
- **All secrets are required**: Missing any will cause authentication errors
- **TOKEN_JSON**: Copy from your local `token.json` file (see [Authentication Setup](02_SETUP.md))

## Step 4: Deploy

1. Click "Save" in Streamlit Cloud
2. Wait 1-2 minutes for deployment
3. Your app will be live at: `https://your-app-name.streamlit.app`

## Troubleshooting

### Authentication Errors

See [Authentication Troubleshooting](09_AUTHENTICATION_TROUBLESHOOTING.md)

### Common Issues

1. **"Module not found"**: Check `requirements.txt` has all dependencies
2. **"Invalid TOML"**: Verify TOKEN_JSON uses triple quotes
3. **"DEVELOPER_TOKEN_INVALID"**: Verify token is correct and approved

## Updating the App

1. Push changes to GitHub
2. Streamlit Cloud auto-deploys
3. Or manually click "Reboot app" in Streamlit Cloud

## Main File Path

The app uses `google_ads_manager.py` as a wrapper that imports from `app.py`. This allows Streamlit Cloud to use the existing configuration without changing settings.

