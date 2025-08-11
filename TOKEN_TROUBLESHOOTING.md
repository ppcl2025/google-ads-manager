# Google Ads API Token Troubleshooting Guide

## Why Tokens Expire Frequently

**Having to refresh your token every few days is NOT normal.** Google Ads refresh tokens should last for months or years. Here are the common causes:

### 1. **Token Inactivity (6+ months)**
- Google automatically expires tokens that haven't been used for 6+ months
- **Solution**: Use your app regularly or implement automatic token refresh

### 2. **Too Many Refresh Tokens**
- Google limits the number of refresh tokens per client-user combination
- **Solution**: Revoke old tokens and generate fresh ones

### 3. **OAuth Consent Screen Changes**
- Modifying your OAuth consent screen invalidates existing tokens
- **Solution**: Regenerate tokens after any consent screen changes

### 4. **Token Revocation**
- Manually revoking access or changing app permissions
- **Solution**: Re-authenticate and generate new tokens

## Immediate Fix

### Step 1: Generate New Token
```bash
python refresh_token_simple.py
```

**Requirements:**
- `client_secrets.json` file in your project directory
- `google-auth-oauthlib` package installed

### Step 2: Update Streamlit Cloud Secrets
1. Go to your Streamlit Cloud app settings
2. Update `GOOGLE_ADS_REFRESH_TOKEN` with the new token
3. Redeploy your app

## Long-term Prevention

### 1. **Streamlit Cloud Token Management (Implemented)**
Your app now includes cloud-optimized token management:
- Health checks on every app startup
- Clear error messages when tokens expire
- Session state tracking for token status
- **Note**: Automatic refresh isn't possible on Streamlit Cloud

### 2. **Regular Usage**
- Use your app at least once every few months
- This keeps tokens active and prevents automatic expiration
- Monitor for expiration warnings in the app

### 3. **Token Monitoring**
- Check token health regularly through the app
- Keep backup tokens ready
- Set calendar reminders for token refresh (every 6 months)

## Best Practices

### 1. **Token Storage**
- Store tokens securely (Streamlit Cloud secrets)
- Keep local backups for development
- Never commit tokens to version control

### 2. **Error Handling**
- Implement graceful token refresh
- Provide clear error messages
- Guide users through re-authentication

### 3. **Development vs Production**
- Use different tokens for development and production
- Test token refresh in development environment
- Monitor production token health

## Common Error Messages

### "Token has been expired or revoked"
- **Cause**: Token is no longer valid
- **Solution**: Generate new token using refresh script

### "invalid_grant"
- **Cause**: Token expired or revoked
- **Solution**: Re-authenticate and get new token

### "access_denied"
- **Cause**: Insufficient permissions
- **Solution**: Check OAuth scopes and user permissions

## Getting client_secrets.json

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services** > **Credentials**
3. Find your **OAuth 2.0 Client ID**
4. Click **Download JSON**
5. Save as `client_secrets.json` in your project directory

## Testing Token Health

Your app now includes automatic token health checks:
- Tests API connectivity on startup
- Automatically refreshes expired tokens
- Provides clear feedback on token status

## Streamlit Cloud Limitations

**Important**: Since your app runs on Streamlit Cloud, there are some limitations:

1. **No Persistent Local Storage**: Can't save tokens locally between app restarts
2. **No Automatic Refresh**: Must manually refresh tokens when they expire
3. **Containerized Environment**: Each app restart is a fresh container
4. **Session State Only**: Token info only persists during the current session

**Workarounds**:
- Use the refresh script locally when tokens expire
- Update Streamlit Cloud secrets with new tokens
- Set calendar reminders for token refresh (every 6 months)
- Monitor token health through the app interface

## Support

If you continue experiencing frequent token expiration:
1. Check your Google Cloud Console for any recent changes
2. Verify OAuth consent screen settings
3. Ensure you're not hitting token limits
4. Consider setting up automated token refresh reminders

## Quick Commands

```bash
# Generate new token
python refresh_token_simple.py

# Check existing token
python get_refresh_token.py

# Test API connection
python test_ads_client.py
```

---

**Remember**: Tokens should last months, not days. If you're refreshing frequently, there's likely a configuration issue that needs addressing.
