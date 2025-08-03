# Google Ads Manager AI Agent

A comprehensive Streamlit application for managing Google Ads campaigns, ad groups, ads, and keywords under an MCC (Manager) account. Features include sub-account creation, campaign management, bulk uploads, and performance analysis.

## Features

- **Sub-Account Management**: Create and manage sub-accounts under your MCC
- **Campaign Creation**: Set up campaigns with MSL-MaxCon bidding strategy
- **Bulk Upload**: Upload CSV/Excel files to create ad groups, ads, and keywords
- **Performance Analysis**: Analyze keywords and search terms performance across accounts
- **Memory Management**: Optimized for handling large datasets
- **PDF Reports**: Generate comprehensive performance reports

## Authentication Issues & Troubleshooting

### Common Authentication Errors

#### "invalid_grant: Token has been expired or revoked"

This error occurs when your Google Ads refresh token has expired or been revoked. This can happen when:

- The token hasn't been used for 6+ months
- You've revoked access to the app
- The OAuth consent screen was modified
- Too many refresh tokens were issued for the same client/user combination

#### How to Fix Authentication Issues

1. **Generate a New Refresh Token**:
   ```bash
   # Make sure you have the required package
   pip install google-auth-oauthlib
   
   # Run the refresh token generator
   python get_refresh_token.py
   ```

2. **Download OAuth Credentials**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Navigate to APIs & Services > Credentials
   - Find your OAuth 2.0 Client ID
   - Download the JSON file and save it as `client_secrets.json`

3. **Update Streamlit Cloud Secrets**:
   - Go to your Streamlit Cloud app settings
   - Update the `GOOGLE_ADS_REFRESH_TOKEN` secret with the new token
   - Redeploy your app

#### Required Streamlit Cloud Secrets

Ensure these secrets are configured in your Streamlit Cloud app:

```toml
GOOGLE_ADS_CLIENT_ID = "your_client_id"
GOOGLE_ADS_CLIENT_SECRET = "your_client_secret"
GOOGLE_ADS_DEVELOPER_TOKEN = "your_developer_token"
GOOGLE_ADS_REFRESH_TOKEN = "your_refresh_token"
GOOGLE_ADS_LOGIN_CUSTOMER_ID = "5022887746"
```

#### Local Development Setup

For local development, you can use environment variables instead of Streamlit secrets:

```bash
export GOOGLE_ADS_CLIENT_ID="your_client_id"
export GOOGLE_ADS_CLIENT_SECRET="your_client_secret"
export GOOGLE_ADS_DEVELOPER_TOKEN="your_developer_token"
export GOOGLE_ADS_REFRESH_TOKEN="your_refresh_token"
export GOOGLE_ADS_LOGIN_CUSTOMER_ID="5022887746"
```

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd google-ads-manager
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up authentication** (see Authentication section above)

4. **Run the application**:
   ```bash
   streamlit run google_ads_manager.py
   ```

## Usage

### Creating Sub-Accounts
- Navigate to the "Create Sub-Account" tab
- Enter account name, currency, and timezone
- Sub-accounts are created without MCC payment profile linking
- Conversion tracking is automatically set to "This Manager"

### Creating Campaigns
- Use the "Create Campaign" tab
- Campaigns use MSL-MaxCon bidding strategy
- PPCL List negative keywords are automatically applied
- Network settings: Core Google Search only
- Location targeting: Presence Only

### Bulk Upload
- Prepare CSV/Excel file with required columns
- Upload file in the "Bulk Upload" tab
- All content is added to a single campaign
- Keywords only need to be specified in the first row of each ad group

### Performance Analysis
- Select sub-accounts to analyze
- Choose date range for analysis
- View top keywords and search terms by spend
- Download comprehensive PDF reports

## File Structure

```
google-ads-manager/
├── google_ads_manager.py      # Main application
├── get_refresh_token.py       # Token generation script
├── requirements.txt           # Python dependencies
├── README.md                 # This file
└── client_secrets.json       # OAuth credentials (not in repo)
```

## Memory Management

The application includes comprehensive memory management features:
- Automatic garbage collection
- DataFrame size limiting
- Session state cleanup
- Memory usage monitoring

## API Usage Tracking

The app tracks Google Ads API usage to stay within monthly limits:
- Default limit: 15,000 operations per month
- Automatic monthly reset
- Usage statistics display

## Support

For issues related to:
- **Authentication**: See the Authentication section above
- **API Limits**: Check your Google Ads API usage in the app
- **Memory Issues**: Use the memory management features in the app
- **General Issues**: Check the error messages and logs in the application

## License

This project is licensed under the MIT License. 