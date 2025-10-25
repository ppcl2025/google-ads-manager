# Team Authentication Reset Guide

## 🚨 When Authentication Fails

If the Streamlit app shows:
```
Failed to load Google Ads credentials: ('invalid_grant: Bad Request', ...)
```

**Any team member can fix it by following these steps:**

---

## 📁 Project Location

**GitHub Repository:**
https://github.com/ppcl2025/google-ads-manager

**All team members clone from GitHub to get the latest code.**

---

## 📋 One-Time Setup (Per Team Member)

### 1. Clone the Repository

```bash
# Clone the repository to your local machine
git clone https://github.com/ppcl2025/google-ads-manager.git
cd google-ads-manager
```

### 2. Get `client_secrets.json`

**Important:** This file contains OAuth credentials and is NOT in the repository for security reasons.

**How to get it:**
- Ask the team lead for the `client_secrets.json` file
- Share via secure method (password manager, encrypted storage, etc.)
- Place it in the project root:

```
google-ads-manager/
├── client_secrets.json  ← Place here (get from team lead)
├── get_refresh_token.py
├── google_ads_manager.py
└── ...
```

**Security Note:** This file is in `.gitignore` and will never be committed.

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

**You only need to do this once!**

---

## 🔧 When You Need to Reset Authentication

### Step 1: Navigate to Project Folder

```bash
# Navigate to your cloned repository
cd google-ads-manager

# Or if you placed it elsewhere:
cd ~/path/to/google-ads-manager
```

### Step 2: Pull Latest Changes (Optional but Recommended)

```bash
# Make sure you have the latest code
git pull
```

### Step 3: Generate New Refresh Token

```bash
# Activate virtual environment
source venv/bin/activate  # Mac/Linux
# or: venv\Scripts\activate  # Windows

# Run token generator
python get_refresh_token.py
```

This will:
1. Open your browser automatically
2. Ask you to sign in with Google Ads account
3. Show the refresh token in the terminal
4. Save a backup to `refresh_token_backup.txt`

**Copy the refresh token from the terminal output.**

### Step 4: Update Streamlit Cloud Secrets

1. Go to [Streamlit Cloud Dashboard](https://share.streamlit.io/)
2. Click on the **google-ads-manager** app
3. Click **Settings** (⚙️) → **Secrets**
4. Find this line:
   ```
   GOOGLE_ADS_REFRESH_TOKEN = "old_token_here"
   ```
5. Replace the old token with your new token
6. Click **Save**

### Step 5: Reboot the App

1. Go to **Main** menu in Streamlit Cloud
2. Click **Reboot app** or **Clear cache**
3. Wait 30-60 seconds for reboot
4. Refresh the app page
5. ✅ Authentication should work!

---

## 🔐 Security Best Practices

### Who Can Reset Authentication?

**Requirements:**
- Access to the GitHub repository
- The `client_secrets.json` file (get from team lead)
- Login credentials for the Google Ads account
- Admin access to Streamlit Cloud secrets (for updating tokens)

### Protecting Secrets

❌ **NEVER:**
- Commit `client_secrets.json` to git
- Share refresh tokens in Slack/email/chat
- Screenshot tokens or post publicly
- Push `refresh_token_backup.txt` to git
- Share `client_secrets.json` insecurely

✅ **ALWAYS:**
- Use password managers or encrypted storage for `client_secrets.json`
- Delete local `refresh_token_backup.txt` files after use
- Keep GitHub repository access limited to team members only
- Verify `.gitignore` includes sensitive files before committing

---

## 📞 Troubleshooting

### "Repository not found" or "Permission denied"
→ Make sure you have access to the GitHub repository
→ Check you're using correct GitHub credentials

### "client_secrets.json not found"
→ Get the file from team lead
→ Make sure it's placed in the project root directory
→ Verify the filename is exactly `client_secrets.json`

### "Invalid client secrets"
→ File may be outdated - get latest from team lead or Google Cloud Console

### "venv not found or broken"
→ Recreate it: `python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`

### Browser doesn't open during token generation
→ Manually go to the URL shown in terminal

### "Token has no refresh_token"
→ This shouldn't happen with the current script
→ Verify the script includes `prompt='consent'` and `access_type='offline'`

### Still failing after reset
→ Check:
  - OAuth Client is active in Google Cloud Console
  - Correct Google account used for authentication
  - All Streamlit secrets are correctly formatted
  - Latest code pulled from GitHub: `git pull`

---

## 🎯 Quick Reference

**To reset authentication:**
1. `cd google-ads-manager`
2. `git pull` (get latest code)
3. `source venv/bin/activate`
4. `python get_refresh_token.py`
5. Copy token → Update Streamlit secrets
6. Reboot app in Streamlit Cloud

**Estimated time:** 2-3 minutes

**GitHub Repository:** https://github.com/ppcl2025/google-ads-manager

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
| Project Code | GitHub | All team members ✅ |
| `client_secrets.json` | Team lead (secure sharing) | All team members |
| Streamlit Cloud Secrets | Streamlit Dashboard | Admin only (to update tokens) |
| Google Ads Account | Google Ads | Person running token reset |
| Google Cloud Console | GCP | Admin only (for OAuth issues) |

**Benefits of GitHub Approach:**
- ✅ Everyone gets latest code with `git pull`
- ✅ Version control for all changes
- ✅ Works perfectly with IDEs (Cursor, VSCode, etc.)
- ✅ No sync conflicts or IDE issues
- ✅ Any team member can fix authentication independently

---

## ⚠️ Important Reminders

1. **Get `client_secrets.json`** from team lead (one-time setup)
2. **Pull latest code** before generating tokens: `git pull`
3. **Delete token backups** after use for security
4. **Keep repository private** - contains sensitive configurations

---

**Last Updated:** October 25, 2025  
**Maintained By:** Team Lead  
**GitHub Repository:** https://github.com/ppcl2025/google-ads-manager

