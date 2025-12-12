# Prompt Modules

This directory contains modular prompt components for the Google Ads Strategist AI system.

## Quick Reference

- **Core Prompt:** Always loaded - base expertise and frameworks
- **Modules:** Loaded on-demand based on page/feature
- **Result:** 20-60% token reduction vs. monolithic prompt

## Structure

- `core/` - Core prompt components (always loaded)
  - `core_prompt.md` - Foundation expertise (~72K chars)
- `modules/` - Optional modules (loaded based on page/feature)
  - See module descriptions below

## Available Modules

### Core Components
- **`core_prompt.md`** - Core responsibilities, real estate analysis, match type strategy, supporting sections
  - Always loaded for all features
  - Contains universal expertise and frameworks

### Optional Modules

1. **`bidding_strategy.md`** (~8K chars)
   - Bidding progression framework
   - Used in: Campaign Analysis

2. **`smart_bidding.md`** (~3K chars)
   - Smart bidding guidance and constraints
   - Used in: Campaign Analysis

3. **`ad_copy.md`** (~5K chars)
   - Ad copy best practices and character limits
   - Used in: Campaign Analysis, Ad Copy Optimization

4. **`offline_conversions.md`** (~6K chars)
   - Offline conversion tracking strategy
   - Used in: Campaign Analysis

5. **`mcc_portfolio.md`** (~5K chars)
   - MCC portfolio bid strategies
   - Used in: Campaign Analysis

6. **`change_tracking.md`** (~6K chars)
   - Change tracking and context-aware analysis
   - Used in: Campaign Analysis, Biweekly Reports

7. **`keyword_planner.md`** (~8K chars)
   - Keyword Planner integration and analysis
   - Used in: Campaign Analysis (optional), Keyword Research

8. **`biweekly_reporting.md`** (~8K chars)
   - Biweekly client reporting framework
   - Used in: Biweekly Reports

9. **`keyword_research.md`** (~2K chars)
   - Keyword research analysis framework
   - Used in: Keyword Research

## Module Loading

The `prompt_loader.py` script handles loading and combining modules based on the page type.

### Example Usage

```python
from prompt_loader import get_prompt_for_page

# Campaign Analysis (loads core + 6 modules)
prompt = get_prompt_for_page('campaign_analysis')

# Ad Copy Optimization (loads core + ad_copy)
prompt = get_prompt_for_page('ad_copy')

# Keyword Research (loads core + keyword modules)
prompt = get_prompt_for_page('keyword_research')
```

## Module Combinations by Page

| Page/Feature | Modules Loaded | Total Size |
|--------------|----------------|------------|
| Campaign Analysis | Core + Bidding + Smart Bidding + Ad Copy + Offline + MCC + Change Tracking | ~134K chars |
| Ad Copy Optimization | Core + Ad Copy | ~69K chars |
| Keyword Research | Core + Keyword Planner + Keyword Research | ~65K chars |
| Biweekly Reports | Core + Biweekly Reporting + Change Tracking | ~86K chars |
| Q&A | Core + Dynamic (based on question) | ~18K+ chars |

## Documentation

For comprehensive documentation, see:
- **[Claude Prompt System Guide](../docs/CLAUDE_PROMPT_SYSTEM.md)** - Complete guide to the modular prompt system
- **[User Guide](../docs/USER_GUIDE.md)** - Web app usage guide

## Maintenance

- **Updating Modules:** Edit the `.md` file directly - changes take effect immediately
- **Adding Modules:** Create new `.md` file and add to `PAGE_PROMPT_CONFIGS` in `prompt_loader.py`
- **Core Updates:** Edit `core_prompt.md` - affects all features

