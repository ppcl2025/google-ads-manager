# 6. Claude Prompt System - Modular Architecture

**Version:** 2.0  
**Last Updated:** December 2024  
**Documentation Order:** #6 (Technical & Advanced Topics)

---

## Overview

The Google Ads Account Manager uses a **modular prompt system** that dynamically loads only the prompt components needed for each feature/page. This approach significantly reduces token usage, improves response times, and makes prompt maintenance easier.

### Why Modular Prompts?

**Before (Monolithic):**
- Single large prompt (~166,000 characters, ~41,000-50,000 tokens)
- Every analysis used the full prompt, even when only specific features were needed
- High token costs and slower response times
- Difficult to update specific sections

**After (Modular):**
- Core prompt + optional modules loaded on-demand
- Campaign Analysis: ~134,000 characters (only needed modules)
- Ad Copy Optimization: ~69,000 characters (core + ad copy module)
- Keyword Research: ~65,000 characters (core + keyword modules)
- **Result: 20-60% token reduction** depending on feature

---

## Architecture

### Directory Structure

```
prompts/
├── core/
│   └── core_prompt.md          # Always loaded - base expertise and frameworks
└── modules/
    ├── bidding_strategy.md      # Bidding progression framework
    ├── smart_bidding.md         # Smart bidding guidance
    ├── ad_copy.md               # Ad copy best practices
    ├── offline_conversions.md   # Offline conversion tracking
    ├── mcc_portfolio.md         # MCC portfolio strategies
    ├── change_tracking.md       # Change tracking context
    ├── keyword_planner.md       # Keyword Planner integration
    ├── biweekly_reporting.md   # Client reporting framework
    └── keyword_research.md      # Keyword research analysis
```

### Core Prompt (`core_prompt.md`)

**Always loaded** - Contains the foundation of Claude's expertise:

- **Core Responsibilities** - Role definition and expertise areas
- **Real Estate Investor Analysis** - Specialized analysis priorities for motivated/distressed sellers
- **Match Type Strategy** - Exact, phrase, and broad match optimization
- **Analysis Framework** - How to structure recommendations
- **Recommendation Format** - Standardized output structure
- **Communication Style** - How to communicate with clients
- **Key Performance Indicators** - Metrics to monitor
- **Search Term Analysis** - Methodology for search term reports
- **Industry Best Practices** - Real estate investor campaign best practices
- **Quality Score Strategy** - QS improvement tactics
- **Red Flags** - Critical issues to watch for
- **Analysis Workflow** - Step-by-step analysis process
- **Context Questions** - When and how to ask for more information

**Size:** ~72,000 characters (~18,000 tokens)

---

## Module Descriptions

### 1. Bidding Strategy Module (`bidding_strategy.md`)

**Purpose:** Framework for bidding strategy progression and optimization

**When Used:**
- ✅ Campaign Analysis (full)
- ❌ Ad Copy Optimization
- ❌ Keyword Research
- ❌ Biweekly Reports
- ❌ Q&A (only if question is about bidding)

**Contents:**
- Bidding strategy progression (Maximize Clicks → Maximize Conversions → Target CPA)
- Threshold criteria for progression
- Manual vs. Smart bidding guidance
- Budget constraint analysis
- CPA stability assessment

**Size:** ~8,000 characters (~2,000 tokens)

---

### 2. Smart Bidding Module (`smart_bidding.md`)

**Purpose:** Detailed guidance on smart bidding strategies and constraints

**When Used:**
- ✅ Campaign Analysis (full)
- ❌ Ad Copy Optimization
- ❌ Keyword Research
- ❌ Biweekly Reports
- ❌ Q&A (only if question is about smart bidding)

**Contents:**
- Maximize Conversions strategy
- Target CPA optimization
- Target ROAS strategy
- Smart bidding constraints and limitations
- When NOT to use smart bidding
- Device/location bid adjustment guidance with smart bidding

**Size:** ~3,000 characters (~750 tokens)

---

### 3. Ad Copy Module (`ad_copy.md`)

**Purpose:** Ad copy optimization, A/B testing, and character limit compliance

**When Used:**
- ✅ Campaign Analysis (full)
- ✅ Ad Copy Optimization page
- ❌ Keyword Research
- ❌ Biweekly Reports
- ❌ Q&A (only if question is about ad copy)

**Contents:**
- Headline optimization (30 character limit)
- Description optimization (90 character limit)
- Dynamic Keyword Insertion (DKI) syntax
- A/B testing frameworks
- Pain point messaging
- Character count verification
- Ad copy replacement instructions

**Size:** ~5,000 characters (~1,250 tokens)

---

### 4. Offline Conversions Module (`offline_conversions.md`)

**Purpose:** Offline conversion tracking strategy for real estate investor funnel

**When Used:**
- ✅ Campaign Analysis (full)
- ❌ Ad Copy Optimization
- ❌ Keyword Research
- ❌ Biweekly Reports
- ❌ Q&A (only if question is about conversions)

**Contents:**
- Real estate investor funnel stages
- GCLID tracking and matching
- Conversion import best practices
- Conversion value assignment
- Funnel analysis (Engaged → Qualified → Under Contract → Closed Deal)
- Attribution modeling

**Size:** ~6,000 characters (~1,500 tokens)

---

### 5. MCC Portfolio Module (`mcc_portfolio.md`)

**Purpose:** Multi-client account management and portfolio bid strategies

**When Used:**
- ✅ Campaign Analysis (full)
- ❌ Ad Copy Optimization
- ❌ Keyword Research
- ❌ Biweekly Reports
- ❌ Q&A (only if question is about MCC)

**Contents:**
- MCC account structure
- Portfolio bid strategies
- Shared budget management
- Cross-account optimization
- Client account isolation

**Size:** ~5,000 characters (~1,250 tokens)

---

### 6. Change Tracking Module (`change_tracking.md`)

**Purpose:** Context-aware analysis using changelog and snapshot data

**When Used:**
- ✅ Campaign Analysis (full)
- ✅ Biweekly Reports
- ❌ Ad Copy Optimization
- ❌ Keyword Research
- ❌ Q&A (only if question references previous changes)

**Contents:**
- Changelog integration
- Snapshot-based change detection
- Context-aware recommendations (avoid repeating previous recommendations)
- Impact assessment of previous changes
- Before/after metric comparison

**Size:** ~6,000 characters (~1,500 tokens)

---

### 7. Keyword Planner Module (`keyword_planner.md`)

**Purpose:** Keyword Planner API integration and analysis framework

**When Used:**
- ✅ Campaign Analysis (full, if keyword planner data provided)
- ✅ Keyword Research page
- ❌ Ad Copy Optimization
- ❌ Biweekly Reports
- ❌ Q&A (only if question is about keyword research)

**Contents:**
- Competition analysis
- Search volume assessment
- Suggested bid analysis
- Keyword expansion recommendations
- Quality Score indicators from Keyword Planner data

**Size:** ~8,000 characters (~2,000 tokens)

---

### 8. Biweekly Reporting Module (`biweekly_reporting.md`)

**Purpose:** Framework for generating client-friendly biweekly reports

**When Used:**
- ✅ Biweekly Reports page
- ❌ Campaign Analysis
- ❌ Ad Copy Optimization
- ❌ Keyword Research
- ❌ Q&A

**Contents:**
- Report structure (2-page format)
- Key metrics selection
- Client-friendly language guidelines
- Plain English explanations
- Performance trend analysis
- Action items and next steps

**Size:** ~8,000 characters (~2,000 tokens)

---

### 9. Keyword Research Module (`keyword_research.md`)

**Purpose:** Specialized prompt for keyword research analysis

**When Used:**
- ✅ Keyword Research page
- ❌ Campaign Analysis
- ❌ Ad Copy Optimization
- ❌ Biweekly Reports
- ❌ Q&A

**Contents:**
- Competition analysis framework
- Search volume assessment
- Keyword expansion recommendations
- Budget allocation strategy
- Market positioning insights

**Size:** ~2,000 characters (~500 tokens)

---

## Module Loading System

### How It Works

The `prompt_loader.py` module handles dynamic loading:

1. **Page Type Detection** - Identifies which page/feature is being used
2. **Module Selection** - Loads only required modules based on configuration
3. **Module Combination** - Combines core + selected modules
4. **Fallback** - Falls back to legacy templates if modules fail to load

### Configuration (`PAGE_PROMPT_CONFIGS`)

```python
PAGE_PROMPT_CONFIGS = {
    'campaign_analysis': [
        'core', 
        'bidding_strategy', 
        'smart_bidding', 
        'ad_copy',
        'offline_conversions', 
        'mcc_portfolio', 
        'change_tracking'
    ],
    'ad_copy': ['core', 'ad_copy'],
    'keyword_research': ['core', 'keyword_planner', 'keyword_research'],
    'biweekly_report': ['core', 'biweekly_reporting', 'change_tracking'],
    'qa': ['core']  # Dynamic module detection based on question
}
```

### Dynamic Module Detection (Q&A)

For Q&A, the system analyzes the user's question and loads additional modules:

- **Bidding questions** → Loads `bidding_strategy` + `smart_bidding`
- **Ad copy questions** → Loads `ad_copy`
- **Conversion questions** → Loads `offline_conversions`
- **Keyword questions** → Loads `keyword_planner`
- **MCC questions** → Loads `mcc_portfolio`
- **Reporting questions** → Loads `biweekly_reporting`

---

## Usage by Page/Feature

This section details which modules are loaded for each page/feature and why each module is needed.

---

### 📊 Campaign Analysis Page

**Purpose:** Comprehensive campaign optimization analysis with full context

**Modules Loaded:**

1. **Core Prompt** (`core_prompt.md`)
   - **Why:** Foundation expertise required for all analysis
   - **Provides:** Core responsibilities, real estate analysis priorities, match type strategy, recommendation format, KPIs, best practices
   - **Size:** ~72,000 characters

2. **Bidding Strategy Module** (`bidding_strategy.md`)
   - **Why:** Campaign analysis must evaluate bidding strategy progression
   - **Provides:** Framework for assessing Maximize Clicks → Maximize Conversions → Target CPA progression, threshold criteria, budget constraints
   - **Size:** ~8,000 characters

3. **Smart Bidding Module** (`smart_bidding.md`)
   - **Why:** Need to provide guidance on smart bidding optimization
   - **Provides:** Maximize Conversions strategy, Target CPA/ROAS guidance, smart bidding constraints, device/location bid adjustment guidance
   - **Size:** ~3,000 characters

4. **Ad Copy Module** (`ad_copy.md`)
   - **Why:** Ad copy optimization is part of comprehensive analysis
   - **Provides:** Headline/description optimization, character limits, DKI syntax, A/B testing frameworks
   - **Size:** ~5,000 characters

5. **Offline Conversions Module** (`offline_conversions.md`)
   - **Why:** Real estate investor funnel requires offline conversion tracking analysis
   - **Provides:** Funnel stages (Engaged → Qualified → Under Contract → Closed Deal), GCLID tracking, conversion import best practices
   - **Size:** ~6,000 characters

6. **MCC Portfolio Module** (`mcc_portfolio.md`)
   - **Why:** Many users manage multiple client accounts via MCC
   - **Provides:** Portfolio bid strategies, shared budget management, cross-account optimization
   - **Size:** ~5,000 characters

7. **Change Tracking Module** (`change_tracking.md`)
   - **Why:** Context-aware analysis requires knowledge of previous changes
   - **Provides:** Changelog integration, snapshot-based change detection, context-aware recommendations
   - **Size:** ~6,000 characters

**Total Size:** ~134,000 characters (~33,500 tokens)

**Use Case:** 
- Full campaign optimization recommendations
- Bidding strategy evaluation and progression
- Ad copy improvements
- Budget allocation
- Waste elimination
- Performance analysis with historical context

**When to Use:**
- Regular campaign reviews
- Monthly optimization cycles
- After making significant changes
- When performance needs improvement

---

### 📝 Ad Copy Optimization Page

**Purpose:** Focused ad copy improvements and A/B testing recommendations

**Modules Loaded:**

1. **Core Prompt** (`core_prompt.md`)
   - **Why:** Foundation expertise and recommendation format needed
   - **Provides:** Core responsibilities, real estate analysis priorities, recommendation structure, communication style
   - **Size:** ~72,000 characters

2. **Ad Copy Module** (`ad_copy.md`)
   - **Why:** This page is specifically for ad copy optimization
   - **Provides:** 
     - Headline optimization (30 character limit with verification)
     - Description optimization (90 character limit with verification)
     - Dynamic Keyword Insertion (DKI) syntax handling
     - A/B testing frameworks
     - Pain point messaging strategies
     - Character count verification for all recommendations
     - Specific replacement instructions (which headline/description to replace)
   - **Size:** ~5,000 characters

**Total Size:** ~69,000 characters (~17,250 tokens)

**Use Case:**
- Improving ad copy performance
- A/B testing new ad variations
- Maximizing character usage (headlines/descriptions)
- Incorporating high-converting keywords into ad copy
- Replacing underperforming ads with optimized versions

**What This Page Does:**
- Analyzes all headlines and descriptions (not just a few)
- Uses statistically significant keywords (most conversions + conversion rate >10%)
- Provides exact character counts for all recommendations
- Specifies which headline/description to replace
- Ensures all recommendations comply with Google Ads character limits

**Why Not Other Modules:**
- Bidding Strategy: Not needed for ad copy focus
- Smart Bidding: Not relevant to creative optimization
- Offline Conversions: Not analyzing conversion tracking
- MCC Portfolio: Not managing multiple accounts
- Change Tracking: Can be added if needed, but not required for ad copy analysis

---

### 🔍 Keyword Research Page

**Purpose:** Keyword competition, search volume, and expansion analysis using Keyword Planner data

**Modules Loaded:**

1. **Core Prompt** (`core_prompt.md`)
   - **Why:** Foundation expertise needed for keyword analysis
   - **Provides:** Core responsibilities, real estate analysis priorities, match type strategy, recommendation format
   - **Size:** ~72,000 characters

2. **Keyword Planner Module** (`keyword_planner.md`)
   - **Why:** This page analyzes Keyword Planner API data
   - **Provides:**
     - Competition analysis framework (low/medium/high competition)
     - Search volume assessment (high/medium/low volume)
     - Suggested bid analysis and comparison
     - Keyword expansion recommendations
     - Quality Score indicators from Keyword Planner data
     - Integration guidance for combining Keyword Planner insights with campaign performance
   - **Size:** ~8,000 characters

3. **Keyword Research Module** (`keyword_research.md`)
   - **Why:** Specialized framework for keyword research analysis
   - **Provides:**
     - Competition analysis structure
     - Search volume assessment methodology
     - Keyword expansion recommendation format
     - Budget allocation strategy for keywords
     - Market positioning insights framework
     - Output format for keyword research reports
   - **Size:** ~2,000 characters

**Total Size:** ~65,000 characters (~16,250 tokens)

**Use Case:**
- Analyzing keyword competition levels
- Assessing search volume opportunities
  - **Automatically matches campaign geo-targeting** when campaign is selected and "Specify geographic targeting" is unchecked
  - Uses manually specified location when checkbox is checked
- Getting bid estimate recommendations
- Finding new keywords to add
- Identifying negative keyword opportunities
- Understanding market competition landscape
- Geographic keyword insights (auto-detected from campaign or manually specified)

**What This Page Does:**
- Fetches Keyword Planner data (search volume, competition, suggested bids)
- **Automatically detects campaign geo-targeting** when a campaign is selected (unless overridden)
- Analyzes keyword opportunities vs. saturated areas
- Provides prioritized keyword expansion recommendations
- Suggests budget allocation across competition tiers
- Identifies Quality Score issues from bid comparisons
- Provides location-specific search volume data matching campaign targeting

**Why Not Other Modules:**
- Bidding Strategy: Not evaluating campaign bidding (this is keyword research)
- Smart Bidding: Not relevant to keyword research
- Ad Copy: Not optimizing ad creative
- Offline Conversions: Not analyzing conversion tracking
- MCC Portfolio: Not managing multiple accounts
- Change Tracking: Not analyzing campaign changes
- Biweekly Reporting: Not generating client reports

---

### 📄 Biweekly Reports Page

**Purpose:** Generate client-friendly 2-page performance reports

**Modules Loaded:**

1. **Core Prompt** (`core_prompt.md`)
   - **Why:** Foundation expertise and KPIs needed for reporting
   - **Provides:** Core responsibilities, real estate analysis priorities, KPIs, communication style (client-friendly)
   - **Size:** ~72,000 characters

2. **Biweekly Reporting Module** (`biweekly_reporting.md`)
   - **Why:** This page is specifically for generating biweekly reports
   - **Provides:**
     - Report structure (2-page format with specific sections)
     - Key metrics selection and formatting
     - Client-friendly language guidelines (plain English, no jargon)
     - Performance trend analysis framework
     - "What's Working" table format
     - "What We're Optimizing" section format
     - "Next Steps" action items format
     - Special situation handling (new campaigns, performance declines, improvements)
     - Output format with exact structure requirements
   - **Size:** ~8,000 characters

3. **Change Tracking Module** (`change_tracking.md`)
   - **Why:** Reports should reference what changes were made during the period
   - **Provides:**
     - Context about previous changes
     - Impact assessment of changes made
     - Before/after metric comparison
     - Helps explain "What We're Optimizing" section with actual changes
   - **Size:** ~6,000 characters

**Total Size:** ~86,000 characters (~21,500 tokens)

**Use Case:**
- Generating professional client reports
- Summarizing 14-day performance periods
- Highlighting key wins and optimizations
- Providing client-friendly explanations
- Setting expectations for next period

**What This Page Does:**
- Analyzes last 14 days of campaign data
- Generates 2-page PDF report with company branding
- Formats metrics with color indicators (🟢🟡🔴)
- Creates "What's Working" table with top performers
- Lists optimizations made during the period
- Provides next steps for following 2 weeks

**Report Structure:**
- **Page 1:** Key Metrics, Two-Week Trend, "What This Means"
- **Page 2:** What's Working table, What We're Optimizing, Next Steps

**Why Not Other Modules:**
- Bidding Strategy: Not providing detailed bidding recommendations (report is summary)
- Smart Bidding: Not evaluating smart bidding strategy
- Ad Copy: Not analyzing ad copy (report is high-level)
- Offline Conversions: May reference but not deep analysis
- MCC Portfolio: Not managing multiple accounts
- Keyword Planner: Not doing keyword research

---

### 💬 Ask Claude (Q&A) Page

**Purpose:** Answer specific Google Ads management questions with dynamic module loading

**Modules Loaded:**

1. **Core Prompt** (`core_prompt.md`) - **Always Loaded**
   - **Why:** Foundation expertise required for all questions
   - **Provides:** Core responsibilities, real estate analysis priorities, best practices, general Google Ads knowledge
   - **Size:** ~72,000 characters

2. **Dynamic Modules** - **Loaded Based on Question Content**

   The system analyzes the user's question and automatically loads additional modules:

   **Bidding Strategy + Smart Bidding Modules:**
   - **Triggered by:** Questions about bidding, bid strategy, maximize clicks, maximize conversions, target CPA, target ROAS
   - **Provides:** Bidding progression framework, smart bidding guidance, threshold criteria
   - **Example Questions:**
     - "How do I optimize my bidding strategy?"
     - "When should I switch from Maximize Clicks to Maximize Conversions?"
     - "What's the best bidding strategy for my campaign?"

   **Ad Copy Module:**
   - **Triggered by:** Questions about ad copy, headlines, descriptions, ad text, creative
   - **Provides:** Ad copy best practices, character limits, A/B testing, DKI syntax
   - **Example Questions:**
     - "How do I write better ad headlines?"
     - "What's the character limit for descriptions?"
     - "How do I use dynamic keyword insertion?"

   **Offline Conversions Module:**
   - **Triggered by:** Questions about conversions, offline conversion, GCLID, funnel, conversion tracking
   - **Provides:** Offline conversion tracking strategy, funnel stages, GCLID matching
   - **Example Questions:**
     - "How do I track offline conversions?"
     - "What's the best way to import conversions to Google Ads?"
     - "How do I set up GCLID tracking?"

   **Keyword Planner Module:**
   - **Triggered by:** Questions about keywords, match type, search term, negative keyword, keyword research
   - **Provides:** Keyword Planner integration, competition analysis, search volume assessment
   - **Example Questions:**
     - "How do I find new keywords?"
     - "What's the difference between match types?"
     - "How do I use Keyword Planner?"

   **MCC Portfolio Module:**
   - **Triggered by:** Questions about MCC, portfolio, multi-client, shared accounts
   - **Provides:** MCC account structure, portfolio bid strategies, shared budget management
   - **Example Questions:**
     - "How do I manage multiple client accounts?"
     - "What are portfolio bid strategies?"
     - "How do I set up an MCC account?"

   **Biweekly Reporting Module:**
   - **Triggered by:** Questions about reports, client reports, biweekly reports, reporting
   - **Provides:** Report structure, client-friendly language, metrics selection
   - **Example Questions:**
     - "How do I create a client report?"
     - "What metrics should I include in reports?"
     - "How do I explain performance to clients?"

   **Change Tracking Module:**
   - **Triggered by:** Questions referencing previous changes, changelog, history
   - **Provides:** Change tracking context, impact assessment
   - **Example Questions:**
     - "What changes did I make last month?"
     - "How do I track campaign changes?"

**Base Size:** ~72,000 characters (~18,000 tokens)  
**With Modules:** Varies based on question (typically +2,000 to +16,000 tokens)

**Use Case:**
- Getting expert advice on specific Google Ads topics
- Understanding best practices
- Troubleshooting issues
- Learning optimization techniques
- Getting recommendations for specific situations

**How It Works:**
1. User asks a question
2. System analyzes question content
3. Detects relevant keywords (bidding, ad copy, conversions, etc.)
4. Loads appropriate modules dynamically
5. Combines core + detected modules
6. Claude answers with full context from loaded modules

**Example:**
- **Question:** "How do I optimize my bidding strategy for a campaign with 50 conversions?"
- **Modules Loaded:** Core + Bidding Strategy + Smart Bidding
- **Total Size:** ~83,000 characters (~20,750 tokens)
- **Response:** Includes bidding progression framework, threshold criteria, smart bidding guidance

**Why This Approach:**
- **Efficiency:** Only loads modules relevant to the question
- **Accuracy:** Provides full context for specific topics
- **Flexibility:** Handles any Google Ads question
- **Token Savings:** Base prompt is minimal, modules added only when needed

---

## Token Usage Comparison

### Before (Monolithic Prompt)

| Feature | Token Usage | Notes |
|---------|-------------|-------|
| Campaign Analysis | ~45,000 | Full prompt always loaded |
| Ad Copy Optimization | ~45,000 | Full prompt (wasteful) |
| Keyword Research | ~45,000 | Full prompt (wasteful) |
| Biweekly Report | ~45,000 | Full prompt (wasteful) |
| Q&A | ~45,000 | Full prompt (wasteful) |

**Average per session:** ~45,000 tokens

### After (Modular System)

| Feature | Token Usage | Savings |
|---------|-------------|---------|
| Campaign Analysis | ~33,500 | 26% reduction |
| Ad Copy Optimization | ~17,250 | 62% reduction |
| Keyword Research | ~16,250 | 64% reduction |
| Biweekly Report | ~21,500 | 52% reduction |
| Q&A (base) | ~18,000 | 60% reduction |

**Average per session:** ~21,500 tokens (52% reduction)

---

## Maintenance & Updates

### Updating a Module

1. Edit the module file in `prompts/modules/`
2. Changes take effect immediately (no code changes needed)
3. All pages using that module will get the updated prompt

### Adding a New Module

1. Create new `.md` file in `prompts/modules/`
2. Add module to `PAGE_PROMPT_CONFIGS` in `prompt_loader.py`
3. Update this documentation

### Updating Core Prompt

1. Edit `prompts/core/core_prompt.md`
2. Changes affect all features (since core is always loaded)
3. Test thoroughly as this impacts all pages

---

## Technical Implementation

### Loading Function

```python
from prompt_loader import get_prompt_for_page

# Load prompt for campaign analysis
prompt = get_prompt_for_page('campaign_analysis')

# Load prompt for Q&A with dynamic detection
prompt = get_prompt_for_page('qa', user_question="How do I optimize bidding?")
```

### Integration in Code

The `real_estate_analyzer.py` uses the modular system:

```python
def _get_prompt_template(prompt_type='full', **kwargs):
    """Load prompt template using modular system."""
    page_type_map = {
        'full': 'campaign_analysis',
        'ad_copy': 'ad_copy',
        'biweekly_report': 'biweekly_report',
        'qa': 'qa',
        'keyword_research': 'keyword_research'
    }
    page_type = page_type_map.get(prompt_type, 'campaign_analysis')
    return get_prompt_for_page(page_type, **kwargs)
```

### Fallback System

If module loading fails, the system falls back to legacy prompt templates defined in `real_estate_analyzer.py`. This ensures backward compatibility and reliability.

---

## Best Practices

1. **Keep Core Prompt Focused** - Only include universal expertise in core
2. **Module Specificity** - Each module should be highly focused on its domain
3. **Avoid Duplication** - Don't repeat content across modules
4. **Test After Updates** - Always test after modifying prompts
5. **Monitor Token Usage** - Track token consumption to optimize further

---

## Future Enhancements

Potential improvements to the modular system:

- **Module Versioning** - Track versions of modules for A/B testing
- **Conditional Loading** - Load modules based on campaign data (e.g., only load offline_conversions if tracking is enabled)
- **Module Caching** - Cache loaded modules to reduce file I/O
- **Analytics** - Track which modules are most used
- **Custom Module Sets** - Allow users to create custom module combinations

---

## Related Documentation

- [User Guide](01_USER_GUIDE.md) - Complete web app usage guide
- [Prompt Recommendations](08_PROMPT_RECOMMENDATIONS.md) - Tips for optimizing prompts
- [Setup Guide](02_SETUP.md) - Installation and configuration

---

## Questions?

For questions about the prompt system, refer to:
- `prompt_loader.py` - Implementation details
- `prompts/README.md` - Quick reference
- This document - Comprehensive guide

