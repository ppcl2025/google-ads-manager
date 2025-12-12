# Streamlit Cloud Deployment Guide

## Migrating from google-ads-manager to GAds-Claude

This guide will help you migrate your Streamlit Cloud deployment from the `google-ads-manager` project to this `GAds-Claude` project.

## Step 1: Update Your Streamlit Cloud App

1. **Go to Streamlit Cloud Dashboard**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account

2. **Find Your Existing App**
   - Locate the app that's currently using `google-ads-manager`
   - Click on it to open settings

3. **Update Repository Settings**
   - Click "Settings" or "⚙️" icon
   - Update the repository to point to your `GAds-Claude` repository
   - Update the **Main file path** to: `app.py`
   - Update the **Branch** if needed (usually `main` or `master`)

## Step 2: Update Secrets/Environment Variables

In Streamlit Cloud, go to **Settings → Secrets** and ensure you have all these secrets configured:

```toml
[secrets]
GOOGLE_ADS_DEVELOPER_TOKEN = "your_developer_token"
GOOGLE_ADS_CLIENT_ID = "your_client_id"
GOOGLE_ADS_CLIENT_SECRET = "your_client_secret"
GOOGLE_ADS_CUSTOMER_ID = "your_mcc_customer_id"
ANTHROPIC_API_KEY = "your_anthropic_api_key"
```

**Important Notes:**
- These secrets are the same as your `.env` file locally
- Streamlit Cloud uses `st.secrets` which the app automatically reads
- Never commit secrets to your repository

## Step 3: Handle OAuth Token (token.json)

For Streamlit Cloud, you have two options:

### Option A: Upload token.json (Recommended for initial setup)

1. **Get your token.json file** from your local machine
2. **In Streamlit Cloud**, go to Settings → Secrets
3. **Add a new secret** called `TOKEN_JSON` with the contents of your token.json file
4. **Update authenticate.py** to read from secrets if token.json doesn't exist locally

### Option B: Re-authenticate in Streamlit Cloud (More secure)

The app will need to handle OAuth flow in Streamlit Cloud. This requires:
- Setting up OAuth redirect URIs for Streamlit Cloud
- Implementing OAuth flow in the Streamlit app

**For now, Option A is recommended** - upload your existing token.json as a secret.

## Step 4: Update Requirements

Streamlit Cloud will automatically install packages from `requirements.txt`. Make sure it includes:
- `streamlit>=1.28.0`
- All other dependencies

## Step 5: Deploy

1. **Save all settings** in Streamlit Cloud
2. **Click "Reboot app"** or wait for automatic redeployment
3. **Check the logs** if there are any errors
4. **Test the app** at your Streamlit Cloud URL

## Step 6: Verify Deployment

Test these features:
- ✅ App loads without errors
- ✅ Authentication works (Google Ads API)
- ✅ Account listing works
- ✅ Campaign analysis works
- ✅ Account creation works
- ✅ Campaign creation works
- ✅ Q&A chat works

## Troubleshooting

### App won't start
- Check Streamlit Cloud logs
- Verify all secrets are set correctly
- Ensure `app.py` is in the root directory
- Check that `requirements.txt` has all dependencies

### Authentication errors
- Verify `token.json` is uploaded as a secret (Option A)
- Or check OAuth redirect URIs are configured correctly
- Ensure Google Ads API credentials are correct

### Import errors
- Check that all Python files are in the repository
- Verify `requirements.txt` includes all packages
- Check Streamlit Cloud logs for missing modules

### API errors
- Verify all API keys are correct in secrets
- Check that MCC customer ID is correct
- Ensure API access is enabled in Google Ads

## File Structure for Streamlit Cloud

Your repository should have this structure:
```
GAds-Claude/
├── app.py                          # Main Streamlit app (required)
├── .streamlit/
│   └── config.toml                 # Streamlit config (optional)
├── requirements.txt                # Python dependencies (required)
├── packages.txt                    # System packages (optional)
├── account_campaign_manager.py     # Account/campaign creation
├── account_manager.py              # Account management
├── authenticate.py                 # OAuth authentication
├── comprehensive_data_fetcher.py   # Data fetching
├── real_estate_analyzer.py         # Core analysis engine
└── ... (other files)
```

## After Migration

Once the new app is working:
1. **Test thoroughly** to ensure all features work
2. **Update any bookmarks** to the new app URL
3. **Archive or delete** the old `google-ads-manager` Streamlit app (optional)
4. **Update documentation** if you have any

## Support

If you encounter issues:
1. Check Streamlit Cloud logs first
2. Verify all secrets are set correctly
3. Test locally with `streamlit run app.py` to isolate issues
4. Check that all dependencies are in `requirements.txt`

