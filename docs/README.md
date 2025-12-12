# Documentation Index

## Getting Started

- **[Setup Guide](SETUP.md)** - Complete setup instructions for local development
- **[Usage Guide](USAGE.md)** - How to use the CLI analyzer
- **[Streamlit Deployment](STREAMLIT_DEPLOYMENT.md)** - Deploy to Streamlit Cloud

## Troubleshooting

- **[Authentication Troubleshooting](AUTHENTICATION_TROUBLESHOOTING.md)** - Fix authentication issues
- **[Model Comparison](MODEL_COMPARISON.md)** - Compare Claude models

## Project Structure

```
GAds-Claude/
├── app.py                          # Streamlit web application
├── real_estate_analyzer.py         # Core analyzer with Claude integration
├── authenticate.py                 # Google Ads API authentication
├── account_manager.py              # Account selection utilities
├── account_campaign_manager.py     # Account/campaign creation
├── comprehensive_data_fetcher.py   # Google Ads API data fetching
├── google_ads_manager.py          # Streamlit entry point wrapper
├── requirements.txt                # Python dependencies
├── README.md                       # Main project README
└── docs/                           # All documentation
```

## Quick Links

- **Local Development**: See [SETUP.md](SETUP.md)
- **Web App**: See [STREAMLIT_DEPLOYMENT.md](STREAMLIT_DEPLOYMENT.md)
- **Troubleshooting**: See [AUTHENTICATION_TROUBLESHOOTING.md](AUTHENTICATION_TROUBLESHOOTING.md)
