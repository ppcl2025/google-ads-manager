# Google Ads Manager

A Streamlit-based web application for managing Google Ads campaigns, ad groups, ads, and keywords under an MCC (My Client Center) account.

## Features

- **Create Sub-Accounts**: Automatically create new sub-accounts with conversion tracking
- **Create Campaigns**: Set up campaigns with shared bidding strategies and negative keyword lists
- **Bulk Upload**: Upload ad groups, ads, and keywords via CSV/Excel files
- **Performance Analysis**: Analyze campaign and keyword performance across sub-accounts
- **🤖 Bid Optimization Engine**: AI-powered bid recommendations based on auction insights and performance metrics
- **🏢 Competitive Landscape Report**: Comprehensive competitive intelligence and market positioning analysis
- **📊 Keywords Analysis**: Detailed keyword performance analysis with sorting and filtering
- **MCC Management**: Manage multiple sub-accounts from a single interface

## Deployment to Streamlit Cloud

### Prerequisites

1. **Google Ads API Access**:
   - Google Ads Developer Token
   - OAuth2 Client ID and Secret
   - Refresh Token
   - MCC Customer ID

2. **GitHub Account**: For code hosting and Streamlit Cloud integration

### Step-by-Step Deployment Instructions

#### Step 1: Prepare Your Google Ads Credentials

1. **Get your Google Ads API credentials**:
   - Developer Token: From Google Ads API Center
   - Client ID & Secret: From Google Cloud Console
   - Refresh Token: Generated through OAuth2 flow
   - MCC Customer ID: Your manager account ID (format: XXX-XXX-XXXX)

#### Step 2: Set Up GitHub Repository

1. **Create a new GitHub repository**:
   - Go to [GitHub](https://github.com)
   - Click "New repository"
   - Name it `google-ads-manager`
   - Make it public (required for Streamlit Cloud free tier)
   - Don't initialize with README (we'll push our code)

2. **Push your code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/google-ads-manager.git
   git push -u origin main
   ```

#### Step 3: Deploy to Streamlit Cloud

1. **Go to Streamlit Cloud**:
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account

2. **Create a new app**:
   - Click "New app"
   - Select your `google-ads-manager` repository
   - Set the main file path to: `google_ads_manager.py`
   - Click "Deploy!"

3. **Configure Environment Variables**:
   - In your app settings, go to "Secrets"
   - Add the following secrets:
   ```toml
   GOOGLE_ADS_CLIENT_ID = "your_client_id"
   GOOGLE_ADS_CLIENT_SECRET = "your_client_secret"
   GOOGLE_ADS_DEVELOPER_TOKEN = "your_developer_token"
   GOOGLE_ADS_REFRESH_TOKEN = "your_refresh_token"
   GOOGLE_ADS_LOGIN_CUSTOMER_ID = "your_mcc_customer_id"
   ```

4. **Redeploy the app**:
   - Click "Redeploy" to apply the secrets

#### Step 4: Test Your Deployment

1. **Access your app**:
   - Your app will be available at: `https://your-app-name.streamlit.app`
   - Share this URL with your team

2. **Verify functionality**:
   - Test creating a sub-account
   - Test creating a campaign
   - Test bulk upload functionality
   - Test performance analysis
   - Test bid optimization engine
   - Test competitive landscape analysis
   - Test keywords analysis

### Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `GOOGLE_ADS_CLIENT_ID` | OAuth2 Client ID | `123456789-abc123.apps.googleusercontent.com` |
| `GOOGLE_ADS_CLIENT_SECRET` | OAuth2 Client Secret | `GOCSPX-abc123def456` |
| `GOOGLE_ADS_DEVELOPER_TOKEN` | API Developer Token | `ABC123DEF456` |
| `GOOGLE_ADS_REFRESH_TOKEN` | OAuth2 Refresh Token | `1//04abc123def456` |
| `GOOGLE_ADS_LOGIN_CUSTOMER_ID` | MCC Customer ID | `502-288-7746` |

## Advanced Features

### 🤖 Bid Optimization Engine

The Bid Optimization Engine analyzes auction insights data to provide intelligent bid recommendations:

- **Increase Bids**: Keywords with high ROAS but low impression share
- **Decrease Bids**: Keywords with low ROAS but high impression share  
- **Pause Keywords**: Poor performing keywords with high competition
- **Maintain Bids**: Keywords with balanced performance

**Requirements**: Active campaigns with sufficient auction insights data

### 🏢 Competitive Landscape Report

Get comprehensive competitive intelligence including:

- **Market Share Analysis**: Your position vs. competitors
- **Top Competitors**: Overlap rates and positioning strategies
- **Market Opportunities**: High-ROAS keywords with low competition
- **Competitive Threats**: Keywords with high competitive pressure
- **Strategic Recommendations**: Actionable insights for improvement

**Requirements**: Active campaigns with auction insights data

### 📊 Keywords Analysis

Detailed keyword performance analysis with:

- **Multi-Account Analysis**: Compare performance across sub-accounts
- **Flexible Date Ranges**: Current month, last month, custom ranges
- **Sorting Options**: Cost, impressions, CTR, conversions, conversion rate
- **Export Capabilities**: Download performance reports as PDF
- **Performance Insights**: Automated recommendations and insights

**Requirements**: Active campaigns with performance data

### Security Best Practices

1. **Never commit credentials**:
   - Keep `google-ads.yaml` in `.gitignore`
   - Use environment variables in production

2. **Access Control**:
   - Consider adding authentication to your app
   - Monitor usage and API calls

3. **Regular Updates**:
   - Keep dependencies updated
   - Monitor for security patches

### Troubleshooting

#### Common Issues

1. **"Failed to load Google Ads credentials"**:
   - Verify all environment variables are set correctly
   - Check that your refresh token is valid

2. **"Invalid customer ID"**:
   - Ensure your MCC customer ID is in the correct format (XXX-XXX-XXXX)
   - Verify you have access to the account

3. **"Developer token not approved"**:
   - Contact Google Ads support to approve your developer token
   - Ensure your token has the necessary permissions

#### Getting Help

- Check the [Google Ads API documentation](https://developers.google.com/google-ads/api/docs)
- Review [Streamlit Cloud documentation](https://docs.streamlit.io/streamlit-community-cloud)
- Check the app logs in Streamlit Cloud dashboard

### Local Development

To run the app locally:

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up credentials**:
   - Create a `google-ads.yaml` file with your credentials
   - Or set environment variables

3. **Run the app**:
   ```bash
   streamlit run google_ads_manager.py
   ```

### Support

For issues or questions:
- Check the troubleshooting section above
- Review the Google Ads API documentation
- Contact your Google Ads representative for API access issues 