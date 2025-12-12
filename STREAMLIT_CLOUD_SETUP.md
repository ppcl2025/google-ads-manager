# Streamlit Cloud Setup - Quick Guide

## Quick Migration Steps

### 1. Push This Repository to GitHub

```bash
cd "/Users/jer89/Cursor Projects/GAds-Claude"
git init  # if not already a git repo
git add .
git commit -m "Initial commit - Streamlit web app"
git remote add origin <your-github-repo-url>
git push -u origin main
```

### 2. Update Streamlit Cloud App

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Find your existing app (the one using google-ads-manager)
3. Click **Settings** (⚙️ icon)
4. Update:
   - **Repository**: Change to your `GAds-Claude` repository
   - **Main file path**: `app.py`
   - **Branch**: `main` (or `master`)

### 3. Configure Secrets

In Streamlit Cloud → Settings → Secrets, add:

```toml
[secrets]
GOOGLE_ADS_DEVELOPER_TOKEN = "your_token_here"
GOOGLE_ADS_CLIENT_ID = "your_client_id_here"
GOOGLE_ADS_CLIENT_SECRET = "your_client_secret_here"
GOOGLE_ADS_CUSTOMER_ID = "your_mcc_id_here"
ANTHROPIC_API_KEY = "your_claude_key_here"
TOKEN_JSON = """
{
  "token": "your_refresh_token_here",
  "refresh_token": "your_refresh_token_here",
  "token_uri": "https://oauth2.googleapis.com/token",
  "client_id": "your_client_id_here",
  "client_secret": "your_client_secret_here",
  "scopes": [
    "https://www.googleapis.com/auth/adwords",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
  ]
}
"""
```

**To get TOKEN_JSON:**
1. Copy the contents of your local `token.json` file
2. Paste it into the `TOKEN_JSON` secret in Streamlit Cloud
3. Make sure to keep the triple quotes `"""` around the JSON

### 4. Deploy

1. Click **Save** in Streamlit Cloud settings
2. The app will automatically redeploy
3. Check the logs if there are errors
4. Your app URL will remain the same (or you'll get a new one)

## File Checklist

Make sure these files are in your repository:

- ✅ `app.py` (main Streamlit app)
- ✅ `requirements.txt` (with streamlit)
- ✅ `.streamlit/config.toml` (optional, for theming)
- ✅ All Python modules (authenticate.py, account_manager.py, etc.)
- ✅ `.gitignore` (to exclude sensitive files)

## Testing Locally First (Recommended)

Before deploying, test locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

If it works locally, it should work on Streamlit Cloud!

## Troubleshooting

**App won't start:**
- Check that `app.py` is in the root directory
- Verify all secrets are set correctly
- Check Streamlit Cloud logs

**Authentication errors:**
- Verify `TOKEN_JSON` secret is correctly formatted
- Ensure all OAuth scopes are included
- Check that token hasn't expired

**Import errors:**
- Verify all Python files are committed to the repo
- Check `requirements.txt` has all dependencies
- Look at Streamlit Cloud logs for missing modules

## After Deployment

Once deployed:
1. Test all features (analysis, account creation, etc.)
2. Update any bookmarks to use the new app
3. You can archive the old google-ads-manager Streamlit app

