# Real Estate Google Ads Analyzer

A specialized AI-powered tool for analyzing Google Ads campaigns targeting motivated and distressed home sellers. Uses Claude AI to provide comprehensive optimization recommendations.

## Features

- 🏠 **Specialized Real Estate Analysis** - Custom Claude prompt optimized for real estate investor campaigns
- 📊 **Comprehensive Data Analysis** - Campaigns, ad groups, ads, keywords, and auction insights
- 🎯 **MCC Account Support** - Select from multiple customer accounts in your MCC
- 🤖 **AI-Powered Recommendations** - Actionable, prioritized optimization suggestions
- 💾 **Export Results** - Save recommendations to files for reference

## Quick Start

### 1. Install Dependencies

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### 2. Set Up Credentials

Create a `.env` file in the project root:

```env
# Google Ads API
GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token
GOOGLE_ADS_CLIENT_ID=your_client_id
GOOGLE_ADS_CLIENT_SECRET=your_client_secret
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token
GOOGLE_ADS_CUSTOMER_ID=your_customer_id

# Claude API
ANTHROPIC_API_KEY=sk-ant-...
```

See [docs/SETUP.md](docs/SETUP.md) for detailed setup instructions.

### 3. Authenticate

```bash
python authenticate.py
```

This will open a browser for OAuth2 authentication and generate your refresh token.

### 4. Run Analysis

```bash
python real_estate_analyzer.py
```

Or use the quick script:
```bash
./run_real_estate.sh
```

## Usage

1. **Select Customer Account** - Choose from accessible accounts in your MCC
2. **Select Campaign** - Pick a specific campaign or analyze all
3. **Set Date Range** - Choose analysis period (default: 30 days)
4. **Set Optimization Goals** - Use defaults or enter custom goals
5. **Get Recommendations** - Claude analyzes and provides structured recommendations

## Project Structure

```
.
├── real_estate_analyzer.py    # Main CLI application
├── account_manager.py          # MCC/campaign selection
├── comprehensive_data_fetcher.py  # Data fetching from Google Ads API
├── authenticate.py             # OAuth2 authentication
├── requirements.txt            # Python dependencies
├── run_real_estate.sh          # Quick start script
├── README.md                   # This file
└── docs/                       # Documentation
    ├── SETUP.md                # Detailed setup guide
    ├── USAGE.md                # Usage guide and examples
    └── MODEL_COMPARISON.md     # Claude model comparison
```

## Documentation

- **[Setup Guide](docs/SETUP.md)** - Complete setup instructions
- **[Usage Guide](docs/USAGE.md)** - How to use the analyzer
- **[Model Comparison](docs/MODEL_COMPARISON.md)** - Claude model selection guide

## Requirements

- Python 3.8+
- Google Ads API access (free)
- Claude API key from [Anthropic Console](https://console.anthropic.com/)
- Google Ads account with API access enabled

## Cost

- **Google Ads API**: Free
- **Claude API**: ~$0.03-0.05 per analysis (using Claude 3.5 Sonnet)

## Troubleshooting

### Authentication Issues

```bash
# Revoke and regenerate tokens
python authenticate.py --revoke
python authenticate.py
```

### No Accounts Found

- Verify your MCC account ID in `.env`
- Ensure API access is enabled
- Check that accounts are linked to your MCC

See [docs/SETUP.md](docs/SETUP.md) for more troubleshooting tips.

## Security

- All credentials stored locally in `.env` (not committed to git)
- OAuth2 authentication for Google Ads
- Secure API communication
- No data stored or logged

## License

This project is for internal use. Ensure compliance with Google Ads API and Anthropic API terms of service.
