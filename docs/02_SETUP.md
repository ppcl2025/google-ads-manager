# 2. Setup Guide

**Documentation Order:** #2 (Getting Started)  
Complete setup instructions for the Real Estate Google Ads Analyzer.

## Prerequisites

- Python 3.8 or higher
- Google Ads account with API access
- Claude API key from Anthropic
- Terminal/command line access

## Step 1: Install Python Dependencies

### Create Virtual Environment

```bash
# Navigate to project directory
cd "/Users/jer89/Cursor Projects/GAds-Claude"

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### Install Packages

```bash
pip install -r requirements.txt
```

**Note:** On macOS with Homebrew Python, you may need to use `python3` and `pip3`.

## Step 2: Google Ads API Setup

### Get Developer Token

1. Go to [Google Ads API Center](https://ads.google.com/aw/apicenter)
2. Sign in with your Google Ads account
3. Click "Create Application" or select an existing application
4. Copy your **Developer Token** (you'll need this)

### Get OAuth2 Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable "Google Ads API":
   - Go to "APIs & Services" → "Library"
   - Search for "Google Ads API"
   - Click "Enable"
4. Create OAuth2 credentials:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Choose "Desktop app" as application type
   - Click "Create"
5. Download credentials:
   - Click the download icon next to your OAuth client
   - Save the JSON file as `client_secrets.json` in the project root

### Get Customer ID

Your Google Ads Customer ID is in the format `123-456-7890`:
- Found in your Google Ads account settings
- Or in the URL when viewing your account
- For MCC accounts, use the MCC ID

## Step 3: Claude API Setup

1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to "API Keys"
4. Click "Create Key"
5. Copy your API key (starts with `sk-ant-`)

## Step 4: Configure Environment Variables

Create a `.env` file in the project root:

```env
# Google Ads API Credentials
GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token_here
GOOGLE_ADS_CLIENT_ID=your_client_id_from_json
GOOGLE_ADS_CLIENT_SECRET=your_client_secret_from_json
GOOGLE_ADS_REFRESH_TOKEN=will_be_generated_next_step
GOOGLE_ADS_CUSTOMER_ID=123-456-7890

# Claude API
ANTHROPIC_API_KEY=sk-ant-your_key_here

# Optional: Default Claude model
CLAUDE_MODEL=claude-3-5-sonnet-20241022
```

**Where to find values:**
- `GOOGLE_ADS_DEVELOPER_TOKEN`: From Google Ads API Center
- `GOOGLE_ADS_CLIENT_ID`: From downloaded `client_secrets.json` (field: `client_id`)
- `GOOGLE_ADS_CLIENT_SECRET`: From downloaded `client_secrets.json` (field: `client_secret`)
- `GOOGLE_ADS_CUSTOMER_ID`: Your Google Ads account ID (format: `123-456-7890`)
- `ANTHROPIC_API_KEY`: From Anthropic Console
- `GOOGLE_ADS_REFRESH_TOKEN`: Generated in next step

## Step 5: Authenticate Google Ads API

Run the authentication script:

```bash
python authenticate.py
```

This will:
1. Open a browser window
2. Ask you to sign in with your Google account
3. Request permission to access Google Ads
4. Generate a refresh token
5. Display the token in the console

**After authentication:**
1. Copy the refresh token shown in the console
2. Update `GOOGLE_ADS_REFRESH_TOKEN` in your `.env` file

**If authentication fails:**
```bash
# Revoke existing tokens
python authenticate.py --revoke

# Re-authenticate
python authenticate.py
```

## Step 6: Verify Setup

Test your setup:

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate

# Run the analyzer
python real_estate_analyzer.py
```

You should see:
- Account selection prompt
- Campaign listing
- Model selection

If you see errors, check the troubleshooting section below.

## Troubleshooting

### Authentication Issues

**"Failed to authenticate with Google Ads API"**

1. Verify credentials in `.env`:
   ```bash
   # Check .env file has all required fields
   cat .env
   ```

2. Regenerate tokens:
   ```bash
   python authenticate.py --revoke
   python authenticate.py
   ```

3. Check `client_secrets.json` exists:
   ```bash
   ls client_secrets.json
   ```

**"Token expired" or "Invalid refresh token"**

- Regenerate refresh token:
  ```bash
  python authenticate.py --revoke
  python authenticate.py
  ```
- Update `.env` with new token

### API Access Issues

**"No accessible customer accounts found"**

- Verify `GOOGLE_ADS_CUSTOMER_ID` is correct
- Ensure the account has API access enabled
- Check that you're using an MCC account ID if analyzing multiple accounts
- Verify OAuth2 credentials have correct scopes

**"Developer token not approved"**

- Developer tokens can take 24-48 hours to activate
- Check status in Google Ads API Center
- Ensure you've completed the application process

### Claude API Issues

**"ANTHROPIC_API_KEY not found"**

- Verify `.env` file exists and contains `ANTHROPIC_API_KEY`
- Check API key is correct (starts with `sk-ant-`)
- Ensure no extra spaces or quotes around the key

**"Error calling Claude API"**

- Verify API key is valid in Anthropic Console
- Check you have sufficient API credits
- Verify internet connection

### Python/Environment Issues

**"Module not found" errors**

- Ensure virtual environment is activated:
  ```bash
  source venv/bin/activate
  ```
- Reinstall dependencies:
  ```bash
  pip install -r requirements.txt
  ```

**"python: command not found"**

- Use `python3` instead:
  ```bash
  python3 real_estate_analyzer.py
  ```

### File Permission Issues

**"Permission denied" when running scripts**

- Make scripts executable:
  ```bash
  chmod +x run_real_estate.sh
  ```

## Multi-Account Setup (MCC)

If you manage multiple Google Ads accounts:

1. Use your MCC (Manager) account ID as `GOOGLE_ADS_CUSTOMER_ID`
2. The analyzer will list all accessible accounts
3. Select the account you want to analyze when prompted

**To find your MCC ID:**
- Log into Google Ads
- MCC accounts show "Manager" in the account selector
- The ID is in the URL or account settings

## Security Best Practices

1. **Never commit credentials:**
   - `.env` is in `.gitignore`
   - `client_secrets.json` is in `.gitignore`
   - `token.json` is in `.gitignore`

2. **Keep credentials secure:**
   - Don't share `.env` file
   - Rotate API keys periodically
   - Use separate credentials for production/testing

3. **Token management:**
   - Refresh tokens don't expire (unless revoked)
   - Store securely
   - Revoke if compromised

## Next Steps

Once setup is complete:

1. Read the [Usage Guide](05_USAGE.md) for how to use the analyzer
2. Review [Model Comparison](07_MODEL_COMPARISON.md) for Claude model selection
3. Run your first analysis:
   ```bash
   python real_estate_analyzer.py
   ```

## Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Verify all credentials are correct
3. Ensure all dependencies are installed
4. Check Google Ads API and Claude API status pages

For usage questions, see [05_USAGE.md](05_USAGE.md).

