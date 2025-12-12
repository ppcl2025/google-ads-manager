# 1. Google Ads Account Manager - AI Agent
## Comprehensive User Guide

**Version:** 1.0  
**Last Updated:** December 2024  
**Documentation Order:** #1 (Getting Started - Read First)

---

## Table of Contents

1. [Overview](#overview)
2. [System Architecture & Integrations](#system-architecture--integrations)
3. [Getting Started](#getting-started)
4. [Web App Pages Guide](#web-app-pages-guide)
5. [Change Tracking System](#change-tracking-system)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Overview

**Google Ads Account Manager - AI Agent** is a comprehensive web application that combines Google Ads API integration with Claude AI to provide intelligent campaign analysis, optimization recommendations, and account management for real estate investor campaigns.

### Key Features

- 🤖 **AI-Powered Analysis** - Claude AI provides context-aware optimization recommendations
- 📊 **Comprehensive Campaign Analysis** - Deep dive into performance metrics and opportunities
- 📝 **Ad Copy Optimization** - Specialized A/B testing recommendations with character limit compliance
- 📄 **Biweekly Client Reports** - Professional 2-page PDF reports for clients
- 💬 **AI Q&A** - Ask Claude questions about Google Ads management
- ❓ **Help Center** - AI-powered documentation assistant with instant answers from app documentation
- ➕ **Account Management** - Create sub-accounts and campaigns directly from the app
- 📸 **Change Tracking** - Automatic and manual change tracking for continuous optimization

### Target Audience

- Real estate investors managing Google Ads campaigns
- PPC managers handling multiple client accounts
- Marketing agencies specializing in real estate lead generation
- Anyone managing Google Ads campaigns targeting motivated and distressed home sellers

---

## System Architecture & Integrations

### Core Technologies

1. **Streamlit** - Web application framework
   - Provides the user interface
   - Handles session state management
   - Deployed on Streamlit Cloud

2. **Google Ads API** - Campaign data and management
   - Fetches comprehensive campaign data
   - Creates sub-accounts and campaigns
   - Requires OAuth 2.0 authentication
   - Supports MCC (Manager) accounts

3. **Anthropic Claude API** - AI analysis engine
   - Provides intelligent campaign analysis
   - Generates optimization recommendations
   - Creates client-friendly reports
   - Answers Google Ads management questions
   - Uses modular prompt system for efficient token usage (20-60% reduction)
   - See [Claude Prompt System](06_CLAUDE_PROMPT_SYSTEM.md) for architecture details

4. **Google Drive API** - Report storage
   - Uploads PDF reports to organized folders
   - Supports multiple report types (analysis, biweekly, Q&A)

5. **Help System** - Documentation assistant
   - Index-based documentation loading for token optimization (~35% savings)
   - On-demand content loading (only loads 2 most relevant docs per query)
   - Smart caching in session state
   - Uses Claude Haiku for fast, cost-effective responses

### Data Flow

```
User Input (Web App)
    ↓
Streamlit App (app.py)
    ↓
┌─────────────────────┬──────────────────────┬─────────────────────┐
│                     │                      │                     │
Google Ads API    Claude API          Google Drive API
    │                     │                      │
    ↓                     ↓                      ↓
Campaign Data    AI Analysis          Report Storage
    │                     │                      │
    └─────────────────────┴──────────────────────┘
                    ↓
            Results Display
                    ↓
            User Actions
```

### Integration Details

#### Google Ads API Integration

**Purpose:** Fetch campaign data and manage accounts

**What It Does:**
- Retrieves campaign performance metrics
- Fetches keyword, ad group, and ad data
- Gets search term performance
- Creates new sub-accounts
- Creates new campaigns

**Authentication:**
- OAuth 2.0 flow
- Refresh token stored securely
- Supports both local (.env) and cloud (Streamlit secrets) configurations

**Data Retrieved:**
- Campaign metrics (impressions, clicks, CTR, conversions, ROAS)
- Keyword performance (status, bids, match types, quality scores)
- Ad group performance
- Ad copy (all headlines and descriptions)
- Search term data
- Bidding strategy settings

#### Claude AI Integration

**Purpose:** Intelligent analysis and recommendations

**Models Available:**
- Claude Sonnet 4 (recommended) - Best balance of quality and cost
- Claude 3.5 Haiku - Fast and cost-effective
- Claude 3 Opus - Most powerful, higher cost

**What Claude Does:**
- Analyzes campaign performance data
- Provides optimization recommendations
- Generates ad copy suggestions
- Creates biweekly client reports
- Answers Google Ads management questions
- Assesses impact of previous changes (with changelog context)

**Claude Prompt System:**
- Modular prompt architecture (core + optional modules)
- Dynamic module loading based on feature/page
- Reduced token usage (20-60% savings per analysis)
- Each page loads only the modules it needs
- See [Claude Prompt System Documentation](06_CLAUDE_PROMPT_SYSTEM.md) for complete details
- Context-aware analysis using changelog history
- Character limit compliance for ad copy
- Client-friendly report formatting

#### Google Drive Integration

**Purpose:** Organized report storage

**Folder Structure:**
- Optimization Reports: `/185ebaQUxrNIMLIp9R61PVWEHdLZghn`
- Ad Copy Optimization: `/1lWe5SH7VLV0LMZLlUWt8WW4JeOfamehn`
- Claude Q&A Chat History: `/1kMShfz38NWRkBK99GzwjDJTzyWi3TXFW`

**Report Types:**
- Campaign Analysis PDFs
- Ad Copy Optimization PDFs
- Biweekly Client Reports (2-page PDFs)
- Q&A Chat Log PDFs

---

## Getting Started

### Prerequisites

1. **Google Ads Account**
   - MCC (Manager) account or customer account
   - Google Ads API access enabled
   - Developer token (Basic or Standard access)

2. **Anthropic Account**
   - Claude API key
   - Access to Claude models (Sonnet 4 recommended)

3. **Google Cloud Project**
   - OAuth 2.0 credentials (Client ID and Secret)
   - Google Ads API enabled
   - Google Drive API enabled (for report storage)

### Initial Setup

See [02_SETUP.md](02_SETUP.md) for detailed setup instructions.

**Quick Setup Steps:**
1. Clone repository
2. Install dependencies (`pip install -r requirements.txt`)
3. Configure credentials (see [03_STREAMLIT_DEPLOYMENT.md](03_STREAMLIT_DEPLOYMENT.md))
4. Deploy to Streamlit Cloud or run locally

### First Time Access

1. Navigate to the web app URL
2. Check connection status in sidebar (should show "✅ Connected")
3. Select your Claude model in Settings
4. Start with "📊 Campaign Analysis" page

---

## Web App Pages Guide

### 📊 Campaign Analysis

**Purpose:** Get comprehensive optimization recommendations for your campaigns.

**How to Use:**

1. **Select Account & Campaign**
   - Choose account from dropdown
   - Select specific campaign or "All Campaigns"
   - Campaign list loads automatically

2. **Set Analysis Parameters**
   - **Date Range:** Number of days to analyze (default: 30)
   - **Optimization Goals:** Use defaults or enter custom goals

3. **Run Analysis**
   - Click "🚀 Run Comprehensive Analysis"
   - Wait for 3 steps:
     - Step 1: Fetching campaign data
     - Step 2: Formatting data
     - Step 3: Loading change history
     - Step 4: Claude analysis (1-2 minutes)

4. **Review Recommendations**
   - Analysis results display automatically
   - Includes performance insights and actionable recommendations
   - Previous changes (if any) are considered by Claude

5. **Save Snapshot (Optional)**
   - Click "💾 Save Snapshot" to save current campaign state
   - Enables automatic change detection later

6. **Track Changes**
   - **Automatic:** Use "🔍 Detect Changes" after making updates
   - **Manual:** Enter changes in text area and save

7. **Export Results**
   - "💾 Save to PDF" - Download PDF report
   - "📤 Upload to Google Drive" - Upload to Optimization Reports folder

**What You Get:**
- Performance analysis
- Keyword optimization recommendations
- Budget allocation suggestions
- Waste elimination recommendations
- Match type strategy guidance
- Ad copy improvement suggestions

**Tips:**
- Save snapshot after analysis for automatic change detection
- Review changelog context before running new analysis
- Use default optimization goals for real estate campaigns

---

### 📝 Ad Copy Optimization

**Purpose:** Get specialized ad copy recommendations with A/B testing suggestions.

**How to Use:**

1. **Select Account & Campaign**
   - Same as Campaign Analysis

2. **Set Date Range**
   - Typically 30 days for sufficient data

3. **Run Analysis**
   - Click "📝 Run Ad Copy Analysis"
   - Claude analyzes all headlines and descriptions
   - Focuses on keywords with 3+ conversions and >10% conversion rate

4. **Review Recommendations**
   - Specific headline/description replacements
   - Character limit compliance
   - High-converting keyword integration
   - A/B testing suggestions

5. **Export Results**
   - Save to PDF or upload to Google Drive (Ad Copy Optimization folder)

**What You Get:**
- Headline replacements (which headline to replace)
- Description replacements (which description to replace)
- Character count verification
- Keyword integration suggestions
- A/B testing recommendations

**Tips:**
- Focus on top-performing keywords (3+ conversions, >10% conversion rate)
- Test one change at a time for accurate results
- Keep character limits in mind (30 chars for headlines, 90 for descriptions)

---

### 🔍 Keyword Research

**Purpose:** Analyze keyword competition, search volume, and get AI-powered expansion recommendations using Google Keyword Planner data.

**How to Use:**

1. **Select Account**
   - Choose account from dropdown
   - Account is required for Keyword Planner API access

2. **Input Keywords**
   - **Option 1: Manual Entry**
     - Enter keywords one per line in the text area
     - Example: `sell my house fast`, `inherited property buyer`, `probate house cash offer`
   
   - **Option 2: Load from Campaign**
     - Select a campaign from dropdown
     - Click "Load Keywords from Selected Campaign"
     - All keywords from that campaign will be loaded automatically
   
   - **Option 3: Generate Suggestions from Seed Keywords**
     - Enter seed keywords (e.g., `we buy houses`, `foreclosure help`)
     - Click "Generate Keyword Suggestions"
     - System uses Keyword Planner to generate related keyword ideas

3. **Set Location Targeting (Optional)**
   - **Automatic (Recommended):** If you select a campaign and leave "Specify geographic targeting" unchecked:
     - System automatically detects and uses the campaign's geo-targeting locations
     - Search volume data will match your campaign's actual target locations
     - Shows: "📍 Using campaign's geo-targeting (X location(s))"
   
   - **Manual Override:** Check "Specify geographic targeting" to override campaign settings:
     - Enter location name (e.g., `Cleveland, Ohio`, `New York`, `United States`)
     - System resolves the location and uses it for search volume analysis
     - This overrides campaign geo-targeting if a campaign is selected
     - Leave blank for national/global data
   
   - **No Campaign Selected:** If no campaign is selected and geo-targeting is unchecked:
     - Uses national/global data (no specific location targeting)

4. **Run Analysis**
   - Click "🚀 Analyze Keywords"
   - System will:
     - Auto-detect campaign geo-targeting (if campaign selected and checkbox unchecked)
     - Fetch Keyword Planner data (search volume, competition, suggested bids) for the target locations
     - Send data to Claude for analysis
     - Generate recommendations

5. **Review Results**
   - **Keyword Planner Data Table:**
     - Shows search volume, competition level, suggested bid range for each keyword
     - Interactive table for easy review
   
   - **Claude's Analysis & Recommendations:**
     - Competition analysis (which keywords are too competitive)
     - Search volume assessment (scaling potential)
     - Keyword expansion recommendations (priority 1, 2, 3)
     - Budget allocation strategy
     - Market positioning insights

6. **Export Results**
   - "💾 Save to PDF" - Download keyword research report
   - "📤 Upload to Google Drive" - Upload to Google Drive folder

**What You Get:**
- Competition analysis for each keyword
- Search volume data (high/medium/low)
- Suggested bid estimates
- Keyword expansion recommendations (add, test, skip)
- Budget allocation strategy
- Quality Score indicators
- Market positioning insights

**Tips:**
- Use "Load from Campaign" to analyze existing campaign keywords
- Use "Generate Suggestions" to discover new keyword opportunities
- **Leave "Specify geographic targeting" unchecked when analyzing campaign keywords** - it will automatically use your campaign's geo-targeting for accurate search volume
- Check "Specify geographic targeting" only if you want to research keywords for a different location than your campaign targets
- Location format: Simple names work best (e.g., `Cleveland`, `Cleveland, Ohio`, `United States`)
- Review competition levels before adding high-competition keywords
- Focus on keywords with medium-high search volume (1K-10K/month) for best results

**When to Use:**
- Before launching a new campaign (use manual location entry)
- When expanding existing campaigns (auto-detects campaign geo-targeting)
- To find new keyword opportunities
- To assess competition levels in your target markets
- To get bid estimates for new keywords
- To research keywords for different locations than your campaign targets (check "Specify geographic targeting")

**Geo-Targeting Behavior:**
- **Unchecked + Campaign Selected:** Automatically uses campaign's geo-targeting (recommended for analyzing campaign keywords)
- **Checked + Location Entered:** Overrides campaign settings, uses only the entered location
- **Unchecked + No Campaign:** Uses national/global data

---

### 📄 Biweekly Reports

**Purpose:** Generate professional 2-page PDF reports for clients.

**How to Use:**

1. **Select Account & Campaign**
   - Choose client account and campaign

2. **Set Date Range**
   - Default: 14 days (biweekly)
   - Adjustable from 7-365 days

3. **Generate Report**
   - Click "📄 Generate Biweekly Report"
   - Claude creates client-friendly report
   - Includes performance overview, trends, and next steps

4. **Review Report**
   - Report displays in web app
   - Formatted with color-coded metrics
   - Professional layout

5. **Export Report**
   - "💾 Download PDF" - 2-page branded PDF
   - "📤 Upload to Google Drive" - Save to reports folder

**Report Contents:**
- **Page 1:**
  - Logo (branded)
  - Key Metrics (6 metrics in 2 columns)
  - Two-Week Trend

- **Page 2:**
  - What This Means
  - What's Working (table)
  - What We're Optimizing
  - Next Steps
  - Logo (footer)

**What You Get:**
- Client-friendly language
- Color-coded metrics (🟢 good, 🟡 okay, 🔴 needs attention)
- Action-oriented insights
- Professional branding

**Tips:**
- Use 14-day periods for biweekly reports
- Review report before sending to client
- Customize logo for branding

---

### 💬 Ask Claude

**Purpose:** Get answers to Google Ads management questions with optional campaign context.

**How to Use:**

1. **Enter Your Question**
   - Type your question in the text area
   - Examples:
     - "How do I improve my Quality Score?"
     - "What's the best bidding strategy for new campaigns?"
     - "Should I use broad match or exact match?"

2. **Add Campaign Context (Optional)**
   - Check "Include campaign data for context"
   - Select account and campaign
   - Claude will use current campaign data to answer

3. **Ask Question**
   - Click "💬 Ask Claude"
   - Response appears in chat interface

4. **Continue Conversation**
   - Ask follow-up questions
   - Chat history maintained in session

5. **Export Chat**
   - "💾 Download PDF" - Save chat log as PDF
   - "📤 Upload to Google Drive" - Save to Q&A folder

**What You Get:**
- Expert Google Ads advice
- Context-aware responses (if campaign data included)
- Conversational interface
- Chat history export

**Tips:**
- Include campaign data for more specific answers
- Ask follow-up questions for deeper insights
- Export important conversations for reference

---

### ➕ Create Account

**Purpose:** Create new Google Ads sub-accounts under your MCC.

**How to Use:**

1. **Enter Account Details**
   - **Account Name:** Descriptive name for the account
   - **Currency Code:** 3-letter code (e.g., USD, CAD)
   - **Time Zone:** Select from dropdown

2. **Review Account Settings**
   - Manager Account: False
   - Test Account: False
   - Tracking URL Template: Empty (client sets up)
   - Payment Method: Client must set up their own

3. **Create Account**
   - Click "➕ Create Sub-Account"
   - Account created in your MCC
   - Account ID displayed upon success

**What Happens:**
- New sub-account created under MCC
- Account appears in account selection dropdowns
- Client must set up payment method separately
- Conversion tracking set to "This Manager"

**Tips:**
- Use descriptive account names
- Select correct time zone for client location
- Note account ID for client records

---

### 🎯 Create Campaign

**Purpose:** Create new campaigns in existing sub-accounts.

**How to Use:**

1. **Select Account**
   - Choose sub-account from dropdown
   - Only sub-accounts (not MCC) can have campaigns

2. **Enter Campaign Details**
   - **Campaign Name:** Descriptive name
   - **Budget:** Daily budget amount
   - **Start Date:** Campaign start date
   - **End Date:** Optional end date

3. **Review Campaign Settings**
   - Bidding Strategy: Maximize Clicks
   - Network: Google Search only
   - Location Targeting: Presence Only
   - Negative Keyword List: Shared list applied

4. **Create Campaign**
   - Click "🎯 Create Campaign"
   - Campaign created with default settings
   - Campaign ID displayed upon success

**Default Settings:**
- Bidding: Maximize Clicks (for new campaigns)
- Network: Search only (no Display, YouTube, etc.)
- Location: Presence Only (targets users in location)
- Negative Keywords: Shared list applied

**Tips:**
- Start with Maximize Clicks, upgrade to Target CPA later
- Use descriptive campaign names
- Set appropriate daily budget

---

### ❓ Help Center

**Purpose:** Get instant answers to questions about the app using AI-powered documentation search.

**How to Use:**

1. **Access Help Center**
   - Click "❓ Help Center" button in the Settings section of the sidebar (underneath Claude Model selector)
   - Help Center page opens with suggested questions

2. **Ask Questions**
   - **Option 1: Click Suggested Questions**
     - Browse 12 pre-populated questions displayed in 3 columns
     - Click any question to get an instant answer
     - Additional questions available in "More Suggested Questions" expander
   
   - **Option 2: Type Your Question**
     - Use the chat input at the bottom: "Ask a question about the app..."
     - Type your question and press Enter
     - System searches documentation and provides answer

3. **Review Answers**
   - Answers appear in chat format with user and assistant messages
   - Source citations show which documentation files were referenced
   - Chat history persists during your session

4. **Clear Chat**
   - Click "🗑️ Clear Chat History" to start fresh

**What You Get:**
- Instant answers based on app documentation
- Step-by-step instructions when relevant
- Source citations for transparency
- Context-aware responses using Claude AI
- Optimized token usage (only loads relevant documentation)

**How It Works:**
- **Index-Based Loading:** System uses a lightweight index (titles, headers, keywords) to quickly identify relevant documentation
- **On-Demand Content:** Only loads the 2 most relevant documentation files per question (optimized for token usage)
- **Smart Caching:** Loaded documentation is cached in session state to prevent redundant loading
- **Token Optimization:** Saves ~35% tokens per query compared to loading all documentation

**Tips:**
- Use specific questions for better results (e.g., "How do I set up geo-targeting?" vs. "help")
- Suggested questions cover common topics - try them first
- Answers are based on documentation in the `docs/` folder
- If answer isn't helpful, try rephrasing your question

**When to Use:**
- Learning how to use a specific feature
- Troubleshooting setup or configuration issues
- Understanding how features work together
- Quick reference for common tasks
- Getting clarification on documentation

---

## Change Tracking System

### Overview

The change tracking system helps Claude provide context-aware recommendations by tracking what changes you've made between analyses.

### Two Methods

#### Method 1: Automatic Change Detection (Recommended)

**Workflow:**
1. Run campaign analysis
2. Click "💾 Save Snapshot" (saves current campaign state)
3. Make changes in Google Ads
4. Click "🔍 Detect Changes"
5. Review detected changes
6. Click "✅ Save to Changelog"

**What Gets Detected:**
- Budget changes
- Bidding strategy changes (including Target CPA/ROAS)
- Keyword status changes (paused/enabled/removed)
- Keyword bid changes
- Campaign/ad group status changes
- New keywords added

**Benefits:**
- No manual entry required
- Accurate change detection
- Automatic formatting

#### Method 2: Manual Entry

**Workflow:**
1. Run campaign analysis
2. Make changes in Google Ads
3. Enter changes in "Track Changes Made" text area
4. Click "💾 Save Changes to Changelog"

**When to Use:**
- Ad copy changes (not detected automatically)
- Negative keyword additions
- Other changes not captured by snapshot

**Benefits:**
- Capture all changes, including ad copy
- Add context and notes
- Flexible entry format

### How Changelog Helps Claude

When you run a new analysis, Claude:
- ✅ Recognizes what was already implemented
- ✅ Assesses impact of previous changes
- ✅ Avoids duplicate recommendations
- ✅ Builds on successes
- ✅ Tracks long-term progress

### Changelog Format

Changelog files are stored in `changelogs/` directory:
- Format: `{AccountName}_{CampaignName}.txt`
- Each entry includes:
  - Date/period
  - Performance summary (optional)
  - Changes made
  - Timestamp

---

## Best Practices

### Campaign Analysis

1. **Regular Analysis**
   - Run analysis every 2-4 weeks
   - Track changes between analyses
   - Build on previous optimizations

2. **Date Ranges**
   - Use 30 days for comprehensive analysis
   - Use 14 days for biweekly reports
   - Avoid very short ranges (<7 days) for statistical significance

3. **Optimization Goals**
   - Use default goals for real estate campaigns
   - Customize for specific objectives
   - Be specific in custom goals

### Change Tracking

1. **Save Snapshots**
   - Always save snapshot after analysis
   - Enables automatic change detection
   - Updates snapshot after saving changes

2. **Document Changes**
   - Track all changes, not just major ones
   - Include specific details (keyword names, amounts)
   - Note dates of changes

3. **Review Changelog**
   - Check previous changes before new analysis
   - Understand what worked and what didn't
   - Build on successful optimizations

### Report Generation

1. **Biweekly Reports**
   - Generate consistently every 2 weeks
   - Use same date ranges for comparison
   - Review before sending to clients

2. **Export Organization**
   - Use Google Drive for centralized storage
   - Download PDFs for local backup
   - Organize by client/account

### Model Selection

1. **Claude Sonnet 4** (Recommended)
   - Best balance of quality and cost
   - Fast response times
   - Excellent for all analysis types

2. **Claude 3.5 Haiku**
   - Fastest and most cost-effective
   - Good for simple questions
   - Use for Q&A when speed is priority

3. **Claude 3 Opus**
   - Most powerful analysis
   - Higher cost
   - Use for complex strategic questions

---

## Troubleshooting

### Connection Issues

**Problem:** "⚠️ Not Connected" in sidebar

**Solutions:**
- Check credentials in Streamlit secrets or .env file
- Verify Google Ads API access
- See [09_AUTHENTICATION_TROUBLESHOOTING.md](09_AUTHENTICATION_TROUBLESHOOTING.md)

### Analysis Hanging

**Problem:** Analysis stuck on "Claude is analyzing..."

**Solutions:**
- Wait 2-3 minutes (normal for complex analyses)
- Check Claude API key is valid
- Try different Claude model
- Check Streamlit Cloud logs for errors

### No Campaign Data

**Problem:** "No campaign data found"

**Solutions:**
- Verify account ID is correct
- Check campaign is not removed
- Ensure date range includes active period
- Verify API access to account

### Change Detection Not Working

**Problem:** "No snapshot found"

**Solutions:**
- Save snapshot after analysis first
- Check snapshots/ directory exists
- Verify account/campaign names match

### PDF Generation Errors

**Problem:** "Failed to create PDF"

**Solutions:**
- Check reportlab is installed
- Verify sufficient disk space
- Check Streamlit Cloud logs
- Try downloading instead of uploading

### Google Drive Upload Fails

**Problem:** "Failed to upload to Google Drive"

**Solutions:**
- Verify Google Drive API is enabled
- Check folder IDs are correct
- Ensure OAuth token has Drive scope
- Re-authenticate if needed

For more troubleshooting, see [09_AUTHENTICATION_TROUBLESHOOTING.md](09_AUTHENTICATION_TROUBLESHOOTING.md).

---

## Additional Resources

- [Setup Guide](02_SETUP.md) - Initial setup instructions
- [Streamlit Deployment](03_STREAMLIT_DEPLOYMENT.md) - Deploy to Streamlit Cloud
- [Claude Prompt System](06_CLAUDE_PROMPT_SYSTEM.md) - Modular prompt architecture and module usage
- [Authentication Troubleshooting](09_AUTHENTICATION_TROUBLESHOOTING.md) - Fix auth issues
- [Model Comparison](07_MODEL_COMPARISON.md) - Compare Claude models
- [Prompt Recommendations](08_PROMPT_RECOMMENDATIONS.md) - Optimize prompts

---

**Need Help?** Check the troubleshooting section or review the specific documentation for your issue.

