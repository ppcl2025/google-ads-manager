# 🔧 Fix: Developer Token Project Mismatch

## The Problem

You're getting "DEVELOPER_TOKEN_INVALID" even though the token is correct. This is usually caused by:

**The developer token and OAuth credentials must be from the SAME Google Cloud project.**

## Why This Happens

Google Ads API requires that:
- Your **developer token** is associated with a specific Google Cloud project
- Your **OAuth credentials** (client_id, client_secret) are from the same project
- If they're from different projects, authentication will fail

## How to Check

### Step 1: Find Your OAuth Credentials Project

1. Go to: **https://console.cloud.google.com/apis/credentials**
2. Find your OAuth 2.0 Client ID: `905635304992-j1usvu7fs29br04urlik91n3ohvhe2o2`
3. Click on it to see details
4. Note the **Project** name at the top

### Step 2: Check Developer Token Association

1. Go to: **https://ads.google.com/aw/apicenter**
2. Find your developer token: `goGGiR9m2FWr-3g82AonQ`
3. Check if it shows which project it's associated with
4. **Note:** The first API request with a developer token permanently associates it with that project

### Step 3: Verify They Match

- ✅ **Same project** = Should work
- ❌ **Different projects** = Will fail with DEVELOPER_TOKEN_INVALID

## How to Fix

### Option 1: Use Same Project (Recommended)

**If your developer token is already associated with a project:**

1. **Create new OAuth credentials in that project:**
   - Go to Google Cloud Console
   - Select the project that has your developer token
   - Go to APIs & Services → Credentials
   - Create new OAuth 2.0 Client ID
   - Download as `client_secrets.json`

2. **Regenerate token with new credentials:**
   ```bash
   python3 authenticate.py
   ```

3. **Update Streamlit secrets:**
   - Update `GOOGLE_ADS_CLIENT_ID` with new client ID
   - Update `GOOGLE_ADS_CLIENT_SECRET` with new client secret
   - Update `TOKEN_JSON` with new token

### Option 2: Create New Project (If Token Not Locked)

**If your developer token hasn't been used yet (not locked to a project):**

1. **Create new Google Cloud project:**
   - Go to Google Cloud Console
   - Create new project
   - Note the project ID

2. **Create OAuth credentials in new project:**
   - Go to APIs & Services → Credentials
   - Create OAuth 2.0 Client ID
   - Download as `client_secrets.json`

3. **Use developer token with new project:**
   - The first API call will associate the token with this project
   - Make sure to use the new OAuth credentials

4. **Regenerate token:**
   ```bash
   python3 authenticate.py
   ```

5. **Update Streamlit secrets** with new values

### Option 3: Use Existing Working Setup

**If the original google-ads-manager project was working:**

1. **Check what project it was using:**
   - Look at the original project's OAuth credentials
   - Note the project name

2. **Use the same project:**
   - Make sure your current OAuth credentials are from that project
   - Or recreate credentials in that project

## Verification Steps

After fixing, verify:

1. ✅ OAuth credentials are from Project A
2. ✅ Developer token is associated with Project A (or not yet associated)
3. ✅ All secrets updated in Streamlit Cloud
4. ✅ Token regenerated with matching credentials
5. ✅ App redeployed

## Common Issues

### "Token already associated with different project"
**Solution:** You need to use OAuth credentials from the project the token is associated with, or create a new developer token.

### "Can't find which project token is associated with"
**Solution:** Make your first API call - it will associate the token with the project of your OAuth credentials.

### "Original project was working, but this one isn't"
**Solution:** Check if the original project used different OAuth credentials or a different developer token setup.

## Still Not Working?

1. **Check Streamlit Cloud logs** for specific error messages
2. **Verify all credentials** are from the same project
3. **Try creating a completely new setup:**
   - New Google Cloud project
   - New OAuth credentials
   - New developer token (if possible)
   - Regenerate everything

## Need Help?

- **Google Ads API Forum:** https://groups.google.com/g/adwords-api
- **Google Cloud Console:** https://console.cloud.google.com/
- **Google Ads API Center:** https://ads.google.com/aw/apicenter

