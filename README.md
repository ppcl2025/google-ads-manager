# 🏠 Real Estate Google Ads Analyzer

AI-Powered Campaign Analysis & Management for Real Estate Investors

A specialized tool for analyzing Google Ads campaigns targeting motivated and distressed home sellers. Uses Claude AI to provide comprehensive optimization recommendations.

## Features

- 🏠 **Specialized Real Estate Analysis** - Custom Claude prompt optimized for real estate investor campaigns
- 📊 **Comprehensive Data Analysis** - Campaigns, ad groups, ads, keywords, and auction insights
- 🎯 **MCC Account Support** - Select from multiple customer accounts in your MCC
- 🤖 **AI-Powered Recommendations** - Actionable, prioritized optimization suggestions
- 💾 **Export Results** - Save recommendations to files and Google Drive
- 🌐 **Web Interface** - Modern Streamlit web app for easy access
- 📝 **Ad Copy Optimization** - Specialized A/B testing recommendations
- 📄 **Biweekly Reports** - Professional client reports
- 💬 **AI Q&A** - Ask Claude questions about Google Ads management
- ➕ **Account Management** - Create sub-accounts and campaigns

## Quick Start

### Option 1: Web App (Recommended)

Deploy to Streamlit Cloud for easy access. See [docs/STREAMLIT_DEPLOYMENT.md](docs/STREAMLIT_DEPLOYMENT.md) for setup.

### Option 2: Local CLI

```bash
# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Authenticate
python3 authenticate.py

# Run analyzer
python3 real_estate_analyzer.py
```

See [docs/SETUP.md](docs/SETUP.md) for detailed setup instructions.

## Project Structure

```
GAds-Claude/
├── app.py                          # Streamlit web application
├── real_estate_analyzer.py         # Core analyzer with Claude integration
├── authenticate.py                 # Google Ads API authentication
├── account_manager.py              # Account selection utilities
├── account_campaign_manager.py    # Account/campaign creation
├── comprehensive_data_fetcher.py  # Google Ads API data fetching
├── google_ads_manager.py         # Streamlit entry point wrapper
├── requirements.txt               # Python dependencies
└── docs/                          # Documentation
    ├── SETUP.md                   # Setup instructions
    ├── USAGE.md                   # Usage guide
    ├── STREAMLIT_DEPLOYMENT.md   # Streamlit Cloud deployment
    └── AUTHENTICATION_TROUBLESHOOTING.md
```

## Documentation

All documentation is in the `docs/` folder. **Start with the [User Guide](docs/USER_GUIDE.md)** for a comprehensive overview.

- **[User Guide](docs/USER_GUIDE.md)** ⭐ **START HERE** - Complete guide to the web app, integrations, and all features
- **[Setup Guide](docs/SETUP.md)** - Initial setup and installation
- **[Streamlit Deployment](docs/STREAMLIT_DEPLOYMENT.md)** - Deploy to Streamlit Cloud
- **[Authentication Troubleshooting](docs/AUTHENTICATION_TROUBLESHOOTING.md)** - Fix auth issues
- **[Model Comparison](docs/MODEL_COMPARISON.md)** - Compare Claude models
- **[Documentation Index](docs/README.md)** - Full documentation index

## Requirements

- Python 3.8+
- Google Ads API access
- Claude API key from Anthropic
- Google Ads account with MCC or customer account

## Features Overview

### Campaign Analysis
- Comprehensive performance analysis
- Keyword optimization recommendations
- Budget allocation suggestions
- Ad copy improvements

### Ad Copy Optimization
- A/B testing recommendations
- Character limit compliance
- High-converting keyword integration

### Biweekly Reports
- Professional 2-page PDF reports
- Client-friendly format
- Performance overview and trends

### Q&A Chat
- Ask Claude questions about Google Ads
- Context-aware responses
- Chat history export

### Account Management
- Create new sub-accounts
- Create new campaigns
- Manage MCC accounts

## License

Private project - All rights reserved
