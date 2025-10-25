# Team Authentication Reset Guide

## 🚨 When Authentication Fails

If the Streamlit app shows:
```
Failed to load Google Ads credentials: ('invalid_grant: Bad Request', ...)
```

**Any team member can fix it by following these steps:**

---

## 📋 One-Time Setup (Per Team Member)

### 1. Clone the Repository

```bash
git clone https://github.com/ppcl2025/google-ads-manager.git
cd google-ads-manager
```

### 2. Get `client_secrets.json`

**Important:** This file is NOT in the repo for security reasons.

Ask the team lead for the `client_secrets.json` file and place it in the project root:
```
google-ads-manager/
├── client_secrets.json  ← Place here
├── get_refresh_token.py
├── google_ads_manager.py
└── ...
```

**Security Note:** Never commit this file to git! It's already in `.gitignore`.

### 3. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Mac/Linux
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

---

## 🔧 When You Need to Reset Authentication

### Step 1: Generate New Refresh Token

```bash
cd google-ads-manager
source venv/bin/activate  # Activate venv first
python get_refresh_token.py
```

This will:
1. Open your browser automatically
2. Ask you to sign in with Google Ads account
3. Show the refresh token in the terminal
4. Save a backup to `refresh_token_backup.txt`

**Copy the refresh token from the terminal output.**

### Step 2: Update Streamlit Cloud Secrets

1. Go to [Streamlit Cloud Dashboard](https://share.streamlit.io/)
2. Click on the **google-ads-manager** app
3. Click **Settings** (⚙️) → **Secrets**
4. Find this line:
   ```
   GOOGLE_ADS_REFRESH_TOKEN = "old_token_here"
   ```
5. Replace the old token with your new token
6. Click **Save**

### Step 3: Reboot the App

1. Go to **Main** menu in Streamlit Cloud
2. Click **Reboot app** or **Clear cache**
3. Wait 30-60 seconds for reboot
4. Refresh the app page
5. ✅ Authentication should work!

---

## 🔐 Security Best Practices

### Who Can Reset Authentication?

**Requirements:**
- Access to this GitHub repository
- The `client_secrets.json` file
- Login credentials for the Google Ads account
- Admin access to Streamlit Cloud secrets

### Protecting Secrets

❌ **NEVER:**
- Commit `client_secrets.json` to git
- Share refresh tokens in Slack/email
- Screenshot tokens or post publicly
- Push `refresh_token_backup.txt` to git

✅ **ALWAYS:**
- Use password managers for `client_secrets.json`
- Delete token backups after use
- Use company-approved secure sharing methods
- Check `.gitignore` includes sensitive files

---

## 📞 Troubleshooting

### "client_secrets.json not found"
→ Get the file from team lead and place in project root

### "Invalid client secrets"
→ File may be outdated, get latest from Google Cloud Console

### Browser doesn't open
→ Manually go to the URL shown in terminal

### "Token has no refresh_token"
→ Rerun with: `python get_refresh_token.py` (make sure prompt='consent')

### Still failing after reset
→ Check:
  - OAuth Client is active in Google Cloud Console
  - Correct Google account used for authentication
  - All Streamlit secrets are correctly formatted

---

## 🎯 Quick Reference

**To reset authentication:**
1. `cd google-ads-manager && source venv/bin/activate`
2. `python get_refresh_token.py`
3. Copy token → Update Streamlit secrets
4. Reboot app in Streamlit Cloud

**Estimated time:** 2-3 minutes

---

## 📚 Additional Resources

- **Main Troubleshooting Guide:** `AUTHENTICATION_TROUBLESHOOTING.md`
- **Solution Documentation:** `AUTH_RESET_SOLUTION.md`
- **Streamlit Cloud Dashboard:** https://share.streamlit.io/
- **Google Cloud Console:** https://console.cloud.google.com/

---

## 👥 Team Access Summary

| What | Where | Who Needs Access |
|------|-------|------------------|
| Code Repository | GitHub | All team members |
| `client_secrets.json` | Secure sharing (password manager) | All team members |
| Streamlit Cloud Secrets | Streamlit Dashboard | Admin only |
| Google Ads Account | Google Ads | Person doing reset |
| Google Cloud Console | GCP | Admin (for OAuth issues) |

---

**Last Updated:** October 25, 2025  
**Maintained By:** Team Lead

