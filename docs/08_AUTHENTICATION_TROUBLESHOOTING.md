# 9. Authentication Troubleshooting Guide

**Documentation Order:** #9 (Troubleshooting)  
Common authentication issues and how to fix them.

## Error: "DEVELOPER_TOKEN_INVALID"

### Cause
The developer token is incorrect or not approved.

### Solution
1. Go to [Google Ads API Center](https://ads.google.com/aw/apicenter)
2. Verify your developer token matches what's in your secrets
3. Check status is **"Approved"**
4. Check access level:
   - **Basic**: Can only access test accounts
   - **Standard**: Can access real accounts
5. Update `GOOGLE_ADS_DEVELOPER_TOKEN` in Streamlit Cloud secrets

## Error: "Request is missing required authentication credential"

### Cause
OAuth access token is not being included in requests. Usually caused by:
- Invalid or expired refresh token
- TOKEN_JSON not properly formatted
- Project mismatch between developer token and OAuth credentials

### Solution

#### 1. Verify TOKEN_JSON Format
In Streamlit Cloud secrets, TOKEN_JSON must use triple quotes:
```toml
TOKEN_JSON = """
{
  "token": "...",
  "refresh_token": "...",
  ...
}
"""
```

#### 2. Regenerate Token
If token is expired:
```bash
source venv/bin/activate
python3 authenticate.py
```
Then update TOKEN_JSON secret with new token.

#### 3. Check Project Match
Developer token and OAuth credentials must be from the **same Google Cloud project**:
- Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
- Find your OAuth Client ID
- Note the project name
- Verify developer token is associated with the same project

## Error: "Refresh Token Expired or Revoked"

### Cause
- OAuth consent screen in "Testing" mode (tokens expire after 7 days)
- Token not used for 6+ months
- Token was revoked

### Solution
1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials/consent)
2. Ensure OAuth consent screen is in **"Production"** mode
3. Regenerate token:
   ```bash
   python3 authenticate.py
   ```
4. Update TOKEN_JSON secret in Streamlit Cloud

## Error: "DEVELOPER_TOKEN_PROHIBITED"

### Cause
Developer token is associated with a different Google Cloud project than your OAuth credentials.

### Solution
1. Create new OAuth credentials in the project that has the developer token, OR
2. Use a developer token from the project that has your OAuth credentials
3. Regenerate token with matching credentials

## Basic vs Standard Access

- **Basic Access**: Can only access test accounts
- **Standard Access**: Can access real accounts

If you have Basic access and try to access a real account, you'll get authentication errors.

## Quick Checklist

- [ ] Developer token is correct: `goGGiR9m2FWr-3g82AonmQ`
- [ ] Developer token is approved
- [ ] All 6 secrets are present in Streamlit Cloud
- [ ] TOKEN_JSON uses triple quotes `"""`
- [ ] OAuth consent screen is in "Production" mode
- [ ] Developer token and OAuth credentials are from same project
- [ ] Token was regenerated recently (if expired)

## Getting Help

- [Google Ads API Forum](https://groups.google.com/g/adwords-api)
- [Streamlit Community](https://discuss.streamlit.io/)
- Check Streamlit Cloud logs for specific error messages

