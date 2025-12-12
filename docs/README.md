# Documentation Index

Welcome to the Google Ads Account Manager - AI Agent documentation.

## 📋 How to Use This Index

All documentation files are **numbered in recommended reading order**:
- **#1-3:** Getting Started (read first)
- **#4-5:** Usage Guides (daily reference)
- **#6-8:** Technical & Advanced Topics (deep dive)
- **#9:** Troubleshooting (when issues occur)

Each document's title includes its number (e.g., "1. User Guide", "6. Claude Prompt System") for easy navigation.

---

## 📚 Documentation Structure (Recommended Reading Order)

### Part 1: Getting Started (Read First)

**1. [01_USER_GUIDE.md](01_USER_GUIDE.md)** ⭐ **START HERE**
   - Comprehensive overview of the web app
   - System architecture and integrations
   - All features and pages explained
   - Best practices and troubleshooting
   - **Read this first** to understand the entire system

**2. [02_SETUP.md](02_SETUP.md)** - Setup & Installation
   - Initial setup instructions
   - Environment configuration
   - Required credentials and API keys
   - Local development setup
   - **Read after USER_GUIDE** to get started

**3. [03_STREAMLIT_DEPLOYMENT.md](03_STREAMLIT_DEPLOYMENT.md)** - Cloud Deployment
   - Deploy to Streamlit Cloud
   - Secrets configuration
   - GitHub integration
   - **Read when ready to deploy**

---

### Part 2: Usage Guides

**4. [01_USER_GUIDE.md](01_USER_GUIDE.md)** - Complete User Guide
   - Detailed instructions for each page
   - Feature walkthroughs
   - Change tracking system
   - **Reference guide** for daily use

**5. [05_USAGE.md](05_USAGE.md)** - CLI Usage (Legacy)
   - Command-line interface guide
   - Legacy CLI functionality
   - **Only if using CLI instead of web app**

---

### Part 3: Technical & Advanced Topics

**6. [06_CLAUDE_PROMPT_SYSTEM.md](06_CLAUDE_PROMPT_SYSTEM.md)** - Prompt Architecture
   - Modular prompt system explained
   - Core prompt and modules
   - Module usage by page/feature
   - Token usage optimization
   - **For understanding how AI prompts work**

**7. [07_MODEL_COMPARISON.md](07_MODEL_COMPARISON.md)** - Claude Model Selection
   - Compare Claude AI models
   - Performance characteristics
   - Cost considerations
   - **When choosing which model to use**

**8. [08_PROMPT_RECOMMENDATIONS.md](08_PROMPT_RECOMMENDATIONS.md)** - Prompt Optimization
   - Tips for optimizing prompts
   - Best practices
   - Advanced techniques
   - **For advanced users and developers**

---

### Part 4: Troubleshooting

**9. [09_AUTHENTICATION_TROUBLESHOOTING.md](09_AUTHENTICATION_TROUBLESHOOTING.md)** - Fix Auth Issues
   - Common authentication errors
   - OAuth 2.0 troubleshooting
   - API access problems
   - **When encountering authentication errors**

**10. [01_USER_GUIDE.md](01_USER_GUIDE.md#troubleshooting)** - General Troubleshooting
   - General issues and solutions
   - Common problems
   - **For other non-auth issues**

---

## Quick Navigation

### By Topic

**Web App Usage:**
- [01_USER_GUIDE.md](01_USER_GUIDE.md) - Complete guide to all pages and features

**Setup & Deployment:**
- [02_SETUP.md](02_SETUP.md) - Local setup
- [03_STREAMLIT_DEPLOYMENT.md](03_STREAMLIT_DEPLOYMENT.md) - Cloud deployment

**AI & Models:**
- [06_CLAUDE_PROMPT_SYSTEM.md](06_CLAUDE_PROMPT_SYSTEM.md) - Modular prompt architecture guide
- [07_MODEL_COMPARISON.md](07_MODEL_COMPARISON.md) - Claude model comparison
- [08_PROMPT_RECOMMENDATIONS.md](08_PROMPT_RECOMMENDATIONS.md) - Prompt optimization

**Troubleshooting:**
- [09_AUTHENTICATION_TROUBLESHOOTING.md](09_AUTHENTICATION_TROUBLESHOOTING.md) - Auth issues
- [01_USER_GUIDE.md](01_USER_GUIDE.md#troubleshooting) - General issues

### By User Type

**New Users (First Time Setup):**
1. **[01_USER_GUIDE.md](01_USER_GUIDE.md)** (#1) - Read overview and all features
2. **[02_SETUP.md](02_SETUP.md)** (#2) - Complete initial setup
3. **[03_STREAMLIT_DEPLOYMENT.md](03_STREAMLIT_DEPLOYMENT.md)** (#3) - Deploy to Streamlit Cloud
4. **[01_USER_GUIDE.md](01_USER_GUIDE.md)** (#4) - Reference for daily use

**Existing Users (Daily Use):**
- **[01_USER_GUIDE.md](01_USER_GUIDE.md)** (#4) - Reference for all features
- **[07_MODEL_COMPARISON.md](07_MODEL_COMPARISON.md)** (#7) - Choose best model if needed
- **[09_AUTHENTICATION_TROUBLESHOOTING.md](09_AUTHENTICATION_TROUBLESHOOTING.md)** (#9) - Fix issues when they occur

**Developers (Technical Deep Dive):**
- **[01_USER_GUIDE.md](01_USER_GUIDE.md#system-architecture--integrations)** (#1) - System architecture
- **[06_CLAUDE_PROMPT_SYSTEM.md](06_CLAUDE_PROMPT_SYSTEM.md)** (#6) - Modular prompt system architecture
- **[08_PROMPT_RECOMMENDATIONS.md](08_PROMPT_RECOMMENDATIONS.md)** (#8) - Prompt engineering

---

## Documentation Files (Quick Reference)

| # | File | Purpose | When to Read |
|---|------|---------|--------------|
| 1 | **01_USER_GUIDE.md** | Complete web app user guide | First (comprehensive overview) |
| 2 | **02_SETUP.md** | Setup instructions | After USER_GUIDE, before first use |
| 3 | **03_STREAMLIT_DEPLOYMENT.md** | Cloud deployment | When deploying to Streamlit Cloud |
| 4 | **01_USER_GUIDE.md** | Usage reference | Daily reference for features |
| 5 | **05_USAGE.md** | CLI usage (legacy) | If using command-line interface |
| 6 | **06_CLAUDE_PROMPT_SYSTEM.md** | Modular prompt architecture | Understanding prompt system and modules |
| 7 | **07_MODEL_COMPARISON.md** | Compare AI models | When choosing which Claude model to use |
| 8 | **08_PROMPT_RECOMMENDATIONS.md** | Prompt optimization | Advanced: optimizing prompts |
| 9 | **09_AUTHENTICATION_TROUBLESHOOTING.md** | Fix auth issues | When encountering authentication errors |
| 10 | **01_USER_GUIDE.md#troubleshooting** | General troubleshooting | For non-auth issues |

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
    ├── 01_USER_GUIDE.md               # #1 ⭐ Comprehensive user guide
    ├── 02_SETUP.md                    # #2 Setup instructions
    ├── 03_STREAMLIT_DEPLOYMENT.md    # #3 Streamlit Cloud deployment
    ├── 05_USAGE.md                    # #5 CLI usage (legacy)
    ├── 06_CLAUDE_PROMPT_SYSTEM.md    # #6 Modular prompt architecture guide
    ├── 07_MODEL_COMPARISON.md         # #7 Claude model comparison
    ├── 08_PROMPT_RECOMMENDATIONS.md  # #8 Prompt optimization tips
    └── 09_AUTHENTICATION_TROUBLESHOOTING.md  # #9 Fix auth issues
```

---

## Getting Help

**Quick Help Path:**
1. **Start with [01_USER_GUIDE.md](01_USER_GUIDE.md)** (#1) - Most questions are answered here
2. **Check [09_AUTHENTICATION_TROUBLESHOOTING.md](09_AUTHENTICATION_TROUBLESHOOTING.md)** (#9) - For auth/API issues
3. **Review specific feature sections** in 01_USER_GUIDE.md (#1)
4. **Check Streamlit Cloud logs** - For deployment issues (see #3)

**By Issue Type:**
- **Setup/Installation:** See #2 (02_SETUP.md)
- **Deployment:** See #3 (03_STREAMLIT_DEPLOYMENT.md)
- **Feature Usage:** See #1 (01_USER_GUIDE.md)
- **Authentication Errors:** See #9 (09_AUTHENTICATION_TROUBLESHOOTING.md)
- **Model Selection:** See #7 (07_MODEL_COMPARISON.md)
- **Prompt System:** See #6 (06_CLAUDE_PROMPT_SYSTEM.md)

---

**Last Updated:** December 2024
