# Team Authentication Reset Guide

## 🚨 When Authentication Fails

If the Streamlit app shows:
```
Failed to load Google Ads credentials: ('invalid_grant: Bad Request', ...)
```

**Any team member can fix it by following these steps:**

---

## 📁 Project Location

**Shared Google Drive Folder:**
https://drive.google.com/drive/folders/1-8Xq1iD_SGsJG-JCJDcFCxpcM6HqLDMf?usp=drive_link

**All team members have access to the latest code and credentials through this shared folder.**

---

## 📋 One-Time Setup (Per Team Member)

### 1. Access the Shared Google Drive Folder

1. Open the shared folder link above (or find it in your Google Drive)
2. **Important:** Right-click the `google-ads-manager` folder → **"Available offline"**
   - This ensures git operations work smoothly
   - Prevents sync delays during token generation
3. Note the local path where Google Drive mounts (usually `~/Google Drive/Shared drives/...`)

### 2. Verify Files Are Present

The folder should contain:
```
google-ads-manager/
├── client_secrets.json  ← Already included (no need to request)
├── get_refresh_token.py
├── google_ads_manager.py
├── venv/                ← Virtual environment
└── ...
```

**Everything you need is already there!** No separate downloads required.

### 3. Locate Your Google Drive Path

Find where Google Drive mounts on your computer:

**Mac:**
```bash
# Usually one of these:
cd ~/Library/CloudStorage/GoogleDrive-*/Shared\ drives/[folder]/google-ads-manager
# or
cd ~/Google\ Drive/Shared\ drives/[folder]/google-ads-manager
```

**Windows:**
```bash
cd "G:\Shared drives\[folder]\google-ads-manager"
# or wherever your Google Drive is mounted
```

**Tip:** Just navigate to it in Finder/Explorer, then drag the folder into Terminal to get the full path.

---

## 🔧 When You Need to Reset Authentication

### Step 1: Navigate to Shared Folder

```bash
# Navigate to the shared Google Drive folder
# Example paths (your actual path may vary):
cd ~/Library/CloudStorage/GoogleDrive-*/Shared\ drives/.../google-ads-manager
# or
cd ~/Google\ Drive/Shared\ drives/.../google-ads-manager
```

**Tip:** Open the folder in Finder/Explorer and drag it into Terminal to get the exact path.

### Step 2: Generate New Refresh Token

```bash
# Activate virtual environment (already set up in shared folder)
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

### Step 3: Update Streamlit Cloud Secrets

1. Go to [Streamlit Cloud Dashboard](https://share.streamlit.io/)
2. Click on the **google-ads-manager** app
3. Click **Settings** (⚙️) → **Secrets**
4. Find this line:
   ```
   GOOGLE_ADS_REFRESH_TOKEN = "old_token_here"
   ```
5. Replace the old token with your new token
6. Click **Save**

### Step 4: Reboot the App

1. Go to **Main** menu in Streamlit Cloud
2. Click **Reboot app** or **Clear cache**
3. Wait 30-60 seconds for reboot
4. Refresh the app page
5. ✅ Authentication should work!

---

## 🔐 Security Best Practices

### Who Can Reset Authentication?

**Requirements:**
- Access to the shared Google Drive folder
- Login credentials for the Google Ads account
- Admin access to Streamlit Cloud secrets (for updating tokens)

**Note:** `client_secrets.json` is already in the shared folder - no additional access needed!

### Protecting Secrets

❌ **NEVER:**
- Share the Google Drive folder with non-team members
- Share refresh tokens in Slack/email/chat
- Screenshot tokens or post publicly
- Remove files from the shared Drive folder
- Commit `client_secrets.json` to git (if you're also using git)

✅ **ALWAYS:**
- Keep the shared Drive folder access limited to team only
- Use Google Drive's sharing controls properly
- Delete local `refresh_token_backup.txt` files after use
- Coordinate with team before making changes

---

## 📞 Troubleshooting

### "Can't find the Google Drive folder"
→ Make sure you've opened the shared link and it appears in your Google Drive
→ Make the folder "Available offline" for easier access

### "client_secrets.json not found"
→ Make sure you're in the correct folder path
→ Check that the shared Drive folder has synced completely

### "Invalid client secrets"
→ File may be outdated - notify team lead to update in shared folder

### "venv not found or broken"
→ You may need to recreate it: `python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`

### Browser doesn't open during token generation
→ Manually go to the URL shown in terminal

### "Token has no refresh_token"
→ This shouldn't happen with the current script, but if it does, check the script includes `prompt='consent'`

### Still failing after reset
→ Check:
  - OAuth Client is active in Google Cloud Console
  - Correct Google account used for authentication
  - All Streamlit secrets are correctly formatted
  - Google Drive folder has latest files

---

## 🎯 Quick Reference

**To reset authentication:**
1. Open shared Google Drive folder in Terminal
2. `source venv/bin/activate`
3. `python get_refresh_token.py`
4. Copy token → Update Streamlit secrets
5. Reboot app in Streamlit Cloud

**Estimated time:** 2-3 minutes

**Shared Folder Link:** https://drive.google.com/drive/folders/1-8Xq1iD_SGsJG-JCJDcFCxpcM6HqLDMf?usp=drive_link

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
| Project Files & Code | Shared Google Drive | All team members ✅ |
| `client_secrets.json` | In shared Drive folder | All team members (automatic) ✅ |
| Streamlit Cloud Secrets | Streamlit Dashboard | Admin only (to update tokens) |
| Google Ads Account | Google Ads | Person running token reset |
| Google Cloud Console | GCP | Admin only (for OAuth issues) |

**Benefits of Shared Drive Approach:**
- ✅ Everyone has latest code automatically
- ✅ Everyone has `client_secrets.json` - no separate sharing needed
- ✅ One folder, multiple team members
- ✅ Easy to keep virtual environment set up
- ✅ Any team member can fix authentication issues independently

---

## ⚠️ Important Reminders

1. **Make folder "Available offline"** for smooth git operations
2. **Coordinate before committing** to avoid conflicts (if using git from shared folder)
3. **One person at a time** should be running token generation
4. **Google Drive must sync** completely before operations

---

**Last Updated:** October 25, 2025  
**Maintained By:** Team Lead  
**Shared Folder:** https://drive.google.com/drive/folders/1-8Xq1iD_SGsJG-JCJDcFCxpcM6HqLDMf?usp=drive_link

