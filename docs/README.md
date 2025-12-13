# Documentation Index

Welcome to the Google Ads Account Manager - AI Agent documentation.

## 📚 Documentation Structure (Chronological Order)

Documents are numbered sequentially for easy navigation:

1. **[01_USER_GUIDE.md](01_USER_GUIDE.md)** ⭐ **START HERE** - Comprehensive guide to the web app, integrations, and all features
2. **[02_SETUP.md](02_SETUP.md)** - Initial setup and installation instructions
3. **[03_STREAMLIT_DEPLOYMENT.md](03_STREAMLIT_DEPLOYMENT.md)** - Deploy the web app to Streamlit Cloud
4. **[04_USAGE.md](04_USAGE.md)** - CLI usage guide (legacy - for command-line interface)
5. **[05_CLAUDE_PROMPT_SYSTEM.md](05_CLAUDE_PROMPT_SYSTEM.md)** - Complete Claude prompt system documentation
6. **[06_MODEL_COMPARISON.md](06_MODEL_COMPARISON.md)** - Compare Claude AI models for optimal selection
7. **[07_PROMPT_RECOMMENDATIONS.md](07_PROMPT_RECOMMENDATIONS.md)** - Tips for optimizing Claude prompts
8. **[08_AUTHENTICATION_TROUBLESHOOTING.md](08_AUTHENTICATION_TROUBLESHOOTING.md)** - Fix authentication and API access issues

---

## Quick Navigation

### By Topic

**Web App Usage:**
- [01_USER_GUIDE.md](01_USER_GUIDE.md) - Complete guide to all pages and features

**Setup & Deployment:**
- [02_SETUP.md](02_SETUP.md) - Local setup
- [03_STREAMLIT_DEPLOYMENT.md](03_STREAMLIT_DEPLOYMENT.md) - Cloud deployment

**AI & Models:**
- [05_CLAUDE_PROMPT_SYSTEM.md](05_CLAUDE_PROMPT_SYSTEM.md) - Complete prompt system
- [06_MODEL_COMPARISON.md](06_MODEL_COMPARISON.md) - Claude model comparison
- [07_PROMPT_RECOMMENDATIONS.md](07_PROMPT_RECOMMENDATIONS.md) - Prompt optimization

**Troubleshooting:**
- [08_AUTHENTICATION_TROUBLESHOOTING.md](08_AUTHENTICATION_TROUBLESHOOTING.md) - Auth issues
- [01_USER_GUIDE.md](01_USER_GUIDE.md#troubleshooting) - General issues

**Legacy:**
- [04_USAGE.md](04_USAGE.md) - CLI usage (for command-line interface)

### By User Type

**New Users:**
1. Read [01_USER_GUIDE.md](01_USER_GUIDE.md) - Overview and all features
2. Follow [02_SETUP.md](02_SETUP.md) - Initial setup
3. Deploy with [03_STREAMLIT_DEPLOYMENT.md](03_STREAMLIT_DEPLOYMENT.md)

**Existing Users:**
- [01_USER_GUIDE.md](01_USER_GUIDE.md) - Reference for all features
- [06_MODEL_COMPARISON.md](06_MODEL_COMPARISON.md) - Choose best model
- [08_AUTHENTICATION_TROUBLESHOOTING.md](08_AUTHENTICATION_TROUBLESHOOTING.md) - Fix issues

**Developers:**
- [01_USER_GUIDE.md](01_USER_GUIDE.md#system-architecture--integrations) - System architecture
- [05_CLAUDE_PROMPT_SYSTEM.md](05_CLAUDE_PROMPT_SYSTEM.md) - Complete prompt system
- [07_PROMPT_RECOMMENDATIONS.md](07_PROMPT_RECOMMENDATIONS.md) - Prompt engineering

---

## Documentation Files

| # | File | Purpose | When to Read |
|---|------|---------|--------------|
| 01 | **01_USER_GUIDE.md** | Complete web app user guide | First (comprehensive overview) |
| 02 | **02_SETUP.md** | Setup instructions | After USER_GUIDE, before first use |
| 03 | **03_STREAMLIT_DEPLOYMENT.md** | Cloud deployment | When deploying to Streamlit Cloud |
| 04 | **04_USAGE.md** | CLI usage (legacy) | If using command-line interface |
| 05 | **05_CLAUDE_PROMPT_SYSTEM.md** | Complete prompt system | Understanding Claude prompts |
| 06 | **06_MODEL_COMPARISON.md** | Compare AI models | When choosing which Claude model to use |
| 07 | **07_PROMPT_RECOMMENDATIONS.md** | Prompt optimization | Advanced: optimizing prompts |
| 08 | **08_AUTHENTICATION_TROUBLESHOOTING.md** | Fix auth issues | When encountering authentication errors |

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
    ├── 01_USER_GUIDE.md            # ⭐ Comprehensive user guide
    ├── 02_SETUP.md                 # Setup instructions
    ├── 03_STREAMLIT_DEPLOYMENT.md # Streamlit Cloud deployment
    ├── 04_USAGE.md                 # CLI usage (legacy)
    ├── 05_CLAUDE_PROMPT_SYSTEM.md # Complete prompt system
    ├── 06_MODEL_COMPARISON.md     # Claude model comparison
    ├── 07_PROMPT_RECOMMENDATIONS.md # Prompt optimization tips
    └── 08_AUTHENTICATION_TROUBLESHOOTING.md # Auth troubleshooting
```

---

## Getting Help

1. **Start with [01_USER_GUIDE.md](01_USER_GUIDE.md)** - Most questions are answered here
2. **Check [08_AUTHENTICATION_TROUBLESHOOTING.md](08_AUTHENTICATION_TROUBLESHOOTING.md)** - For auth/API issues
3. **Review specific feature sections** in 01_USER_GUIDE.md
4. **Check Streamlit Cloud logs** - For deployment issues

---

**Last Updated:** December 2024
