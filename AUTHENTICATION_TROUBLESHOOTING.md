# Authentication Troubleshooting Guide

## Quick Fix for "invalid_grant" Error

If you're seeing this error in your Streamlit Cloud app:
```
Failed to load Google Ads credentials: ('invalid_grant: Token has been expired or revoked.', {'error': 'invalid_grant', 'error_description': 'Token has been expired or revoked.'})
```

Follow these steps to fix it:

### Step 1: Download Your OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services** > **Credentials**
3. Find your **OAuth 2.0 Client ID**
4. Click the download button (⬇️) to download the JSON file
5. Save it as `client_secrets.json` in your project directory

### Step 2: Generate a New Refresh Token

1. Make sure you have the required package:
   ```bash
   pip install google-auth-oauthlib
   ```

2. Run the refresh token script:
   ```bash
   python get_refresh_token.py
   ```

3. Follow the browser authentication flow:
   - A browser window will open
   - Sign in with your Google account
   - Grant permissions to the app
   - Copy the refresh token that appears

### Step 3: Update Streamlit Cloud Secrets

1. Go to your Streamlit Cloud app dashboard
2. Click on your app name
3. Go to **Settings** > **Secrets**
4. Update the `GOOGLE_ADS_REFRESH_TOKEN` value with your new token
5. Click **Save**
6. Go back to **Main** and click **Redeploy**

### Step 4: Test Your App

1. Wait for the redeployment to complete
2. Visit your app URL
3. The authentication error should be resolved

## Why This Happens

Google OAuth refresh tokens can expire or be revoked for several reasons:

- **Inactivity**: Tokens expire after 6 months of non-use
- **Security**: You may have revoked access
- **OAuth Changes**: Modifications to your OAuth consent screen
- **Token Limits**: Too many refresh tokens issued for the same client/user

## Prevention Tips

1. **Regular Usage**: Use your app regularly to keep tokens active
2. **Monitor Expiry**: Check token status periodically
3. **Backup Tokens**: Keep backup copies of working tokens
4. **Test Regularly**: Test authentication before important operations

## Alternative Solutions

If the above doesn't work:

1. **Check OAuth Consent Screen**:
   - Ensure your app is properly configured
   - Verify the scopes are correct
   - Check if the app is in testing or production

2. **Verify Client Credentials**:
   - Make sure your client ID and secret are correct
   - Check that the OAuth client is properly configured

3. **Contact Google Support**:
   - If issues persist, contact Google Ads API support
   - Provide your developer token and error details

## Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `invalid_grant` | Token expired/revoked | Generate new refresh token |
| `invalid_client` | Wrong client credentials | Check client ID/secret |
| `unauthorized_client` | OAuth not configured | Verify OAuth setup |
| `access_denied` | User denied permission | Re-authenticate user |

## Need Help?

If you're still having issues:

1. Check the app logs in Streamlit Cloud
2. Verify all secrets are correctly set
3. Test with a fresh OAuth client
4. Contact support with specific error details

Remember: Never share your refresh tokens or client secrets publicly! 