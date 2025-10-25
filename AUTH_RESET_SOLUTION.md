# Authentication Reset Solution

## Problem
The app periodically fails with the error:
```
Failed to load Google Ads credentials: ('invalid_grant: Bad Request', {'error': 'invalid_grant', 'error_description': 'Bad Request'})
```

## Root Cause
Google OAuth refresh tokens can expire or be revoked for several reasons:

1. **Inactivity**: Tokens automatically expire after 6 months of non-use
2. **Token Limit**: Google limits the number of refresh tokens per user/client (typically 50)
3. **Security Revocation**: User manually revoked access or security policies changed
4. **OAuth Changes**: Modifications to the OAuth consent screen in Google Cloud Console

## Solution Implemented

### 1. Added "Reset Authentication" Button
A prominent **🔐 Reset Authentication** button has been added to the top of the app UI that:
- Is visible at all times for quick access
- Shows detailed step-by-step instructions when clicked
- Includes helper text explaining when to use it

### 2. Automatic Error Detection
When an `invalid_grant` error occurs, the app now:
- Automatically sets the flag to show reset instructions
- Displays a clear warning message
- Directs users to click the Reset Authentication button

### 3. Clear Instructions
The reset instructions include:
- Why the error happens
- Step-by-step guide to generate a new token
- How to update Streamlit Cloud secrets
- Troubleshooting tips

## How to Use

### When the Error Occurs:
1. Click the **🔐 Reset Authentication** button at the top of the page
2. Follow the step-by-step instructions displayed
3. Run `python get_refresh_token.py` on your local machine
4. Update the Streamlit Cloud secrets with the new token
5. Reboot the app

### Quick Fix (2-3 minutes):
```bash
# On your local machine
cd google-ads-manager
source venv/bin/activate
python get_refresh_token.py
# Copy the token from terminal output
```

Then update `GOOGLE_ADS_REFRESH_TOKEN` in Streamlit Cloud secrets and reboot.

## Prevention Tips

1. **Use the app regularly**: Tokens expire after 6 months of inactivity
2. **Keep backup tokens**: Save generated tokens in a secure location
3. **Monitor token limits**: Avoid generating too many tokens
4. **Document the process**: Keep instructions accessible for quick fixes

## Technical Details

### Files Modified:
- `google_ads_manager.py`: Added reset button and improved error handling

### Key Changes:
1. Added `show_auth_reset` session state variable
2. Created authentication reset button in main UI
3. Added comprehensive instructions panel
4. Improved error detection in `get_google_ads_client()`
5. Automatic display of instructions on `invalid_grant` error

### Code Locations:
- Reset button: Line ~1340 in `main()` function
- Error detection: Line ~204 in `get_google_ads_client()` function
- Instructions panel: Line ~1355 in `main()` function

## Related Files
- `get_refresh_token.py`: Script to generate new refresh tokens
- `AUTHENTICATION_TROUBLESHOOTING.md`: Detailed troubleshooting guide
- `client_secrets.json`: OAuth client credentials (not committed to repo)

## Maintenance
This solution should reduce the friction of dealing with expired tokens. The process is now:
- **Before**: App fails → User confused → Searches documentation → Manual fix
- **After**: App fails → Click button → Follow clear steps → Fixed in 2-3 minutes

## Future Improvements
Potential enhancements:
1. Add token expiry monitoring/warnings
2. Create automated token refresh (requires OAuth flow changes)
3. Add email notifications when token is about to expire
4. Implement token health dashboard

