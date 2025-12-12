# ✅ Correct TOML Format for Streamlit Cloud Secrets

## The Issue

Streamlit Cloud secrets must be in **TOML format**. When you have multi-line JSON, you need to use triple quotes.

## ✅ Correct Format

In Streamlit Cloud → Settings → Secrets, use this **exact format**:

```toml
TOKEN_JSON = """
{
  "token": "your_access_token_here",
  "refresh_token": "your_refresh_token_here",
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

GOOGLE_ADS_DEVELOPER_TOKEN = "your_developer_token"
GOOGLE_ADS_CLIENT_ID = "your_client_id.apps.googleusercontent.com"
GOOGLE_ADS_CLIENT_SECRET = "your_client_secret"
GOOGLE_ADS_CUSTOMER_ID = "your_customer_id"
ANTHROPIC_API_KEY = "your_anthropic_key"
```

## Important Notes

1. **Triple quotes are REQUIRED** for multi-line strings in TOML
2. **The `TOKEN_JSON = """` part is part of the TOML syntax** - don't remove it
3. **The closing `"""` is also required**
4. **All other secrets** use regular quotes (single or double)

## Basic Access vs Standard Access

You mentioned your token is approved for **"Basic"** access. This is important:

- **Basic Access**: Can only access **test accounts** (accounts marked as test)
- **Standard Access**: Can access **real accounts**

If google-ads-manager was working with Basic access, you must be using test accounts. Make sure:
- Your accounts are marked as test accounts in Google Ads
- Or you're only trying to access test accounts

## If You Need Standard Access

If you need to access real accounts:
1. Go to https://ads.google.com/aw/apicenter
2. Apply for "Standard" access
3. Wait for approval (can take several days)

## After Saving

1. Click "Save" in Streamlit Cloud
2. Wait 1-2 minutes for redeploy
3. The app should now work!

