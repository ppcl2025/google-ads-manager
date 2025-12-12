# Documentation Index

Welcome to the Google Ads Account Manager - AI Agent documentation.

## 📚 Documentation Structure (Chronological Order)

### 1. Getting Started

Start here if you're new to the project:

- **[USER_GUIDE.md](USER_GUIDE.md)** ⭐ **START HERE** - Comprehensive guide to the web app, integrations, and all features
- **[SETUP.md](SETUP.md)** - Initial setup and installation instructions
- **[STREAMLIT_DEPLOYMENT.md](STREAMLIT_DEPLOYMENT.md)** - Deploy the web app to Streamlit Cloud

### 2. Usage & Reference

After setup, learn how to use the system:

- **[USER_GUIDE.md](USER_GUIDE.md)** - Complete web app user guide (includes usage instructions)
- **[MODEL_COMPARISON.md](MODEL_COMPARISON.md)** - Compare Claude AI models for optimal selection
- **[PROMPT_RECOMMENDATIONS.md](PROMPT_RECOMMENDATIONS.md)** - Tips for optimizing Claude prompts

### 3. Troubleshooting

If you encounter issues:

- **[AUTHENTICATION_TROUBLESHOOTING.md](AUTHENTICATION_TROUBLESHOOTING.md)** - Fix authentication and API access issues
- **[USER_GUIDE.md](USER_GUIDE.md#troubleshooting)** - General troubleshooting section

---

## Quick Navigation

### By Topic

**Web App Usage:**
- [USER_GUIDE.md](USER_GUIDE.md) - Complete guide to all pages and features

**Setup & Deployment:**
- [SETUP.md](SETUP.md) - Local setup
- [STREAMLIT_DEPLOYMENT.md](STREAMLIT_DEPLOYMENT.md) - Cloud deployment

**AI & Models:**
- [MODEL_COMPARISON.md](MODEL_COMPARISON.md) - Claude model comparison
- [PROMPT_RECOMMENDATIONS.md](PROMPT_RECOMMENDATIONS.md) - Prompt optimization

**Troubleshooting:**
- [AUTHENTICATION_TROUBLESHOOTING.md](AUTHENTICATION_TROUBLESHOOTING.md) - Auth issues
- [USER_GUIDE.md](USER_GUIDE.md#troubleshooting) - General issues

### By User Type

**New Users:**
1. Read [USER_GUIDE.md](USER_GUIDE.md) - Overview and all features
2. Follow [SETUP.md](SETUP.md) - Initial setup
3. Deploy with [STREAMLIT_DEPLOYMENT.md](STREAMLIT_DEPLOYMENT.md)

**Existing Users:**
- [USER_GUIDE.md](USER_GUIDE.md) - Reference for all features
- [MODEL_COMPARISON.md](MODEL_COMPARISON.md) - Choose best model
- [AUTHENTICATION_TROUBLESHOOTING.md](AUTHENTICATION_TROUBLESHOOTING.md) - Fix issues

**Developers:**
- [USER_GUIDE.md](USER_GUIDE.md#system-architecture--integrations) - System architecture
- [PROMPT_RECOMMENDATIONS.md](PROMPT_RECOMMENDATIONS.md) - Prompt engineering

---

## Documentation Files

| File | Purpose | When to Read |
|------|---------|--------------|
| **USER_GUIDE.md** | Complete user guide | First (comprehensive overview) |
| **SETUP.md** | Setup instructions | After USER_GUIDE, before first use |
| **STREAMLIT_DEPLOYMENT.md** | Cloud deployment | When deploying to Streamlit Cloud |
| **AUTHENTICATION_TROUBLESHOOTING.md** | Fix auth issues | When encountering authentication errors |
| **MODEL_COMPARISON.md** | Compare AI models | When choosing which Claude model to use |
| **PROMPT_RECOMMENDATIONS.md** | Prompt optimization | Advanced: optimizing prompts |

---

## Project Structure

```
GAds-Claude/
├── app.py                          # Streamlit web application
├── real_estate_analyzer.py         # Core analyzer with Claude integration
├── authenticate.py                 # Google Ads API authentication
├── account_manager.py              # Account selection utilities
├── account_campaign_manager.py     # Account/campaign creation
├── comprehensive_data_fetcher.py  # Google Ads API data fetching
├── changelog_manager.py            # Change tracking system
├── snapshot_manager.py             # Snapshot system for change detection
├── google_ads_manager.py          # Streamlit entry point wrapper
├── requirements.txt                # Python dependencies
├── README.md                       # Main project README
└── docs/                           # All documentation
    ├── README.md                   # This file (documentation index)
    ├── USER_GUIDE.md               # ⭐ Comprehensive user guide
    ├── SETUP.md                    # Setup instructions
    ├── STREAMLIT_DEPLOYMENT.md    # Streamlit Cloud deployment
    ├── AUTHENTICATION_TROUBLESHOOTING.md
    ├── MODEL_COMPARISON.md         # Claude model comparison
    └── PROMPT_RECOMMENDATIONS.md  # Prompt optimization tips
```

---

## Getting Help

1. **Start with [USER_GUIDE.md](USER_GUIDE.md)** - Most questions are answered here
2. **Check [AUTHENTICATION_TROUBLESHOOTING.md](AUTHENTICATION_TROUBLESHOOTING.md)** - For auth/API issues
3. **Review specific feature sections** in USER_GUIDE.md
4. **Check Streamlit Cloud logs** - For deployment issues

---

**Last Updated:** December 2024
