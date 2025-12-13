# 5. Usage Guide (CLI - Legacy)

**Documentation Order:** #5 (Usage Guides)  
Complete guide for using the Real Estate Google Ads Analyzer via command-line interface.

## Quick Start

```bash
source venv/bin/activate
python real_estate_analyzer.py
```

Or use the quick script:
```bash
./run_real_estate.sh
```

## Step-by-Step Usage

### Step 1: Select Customer Account

The tool lists all accessible customer accounts from your MCC:

```
Available Customer Accounts:

1. Real Estate Investor Account (123-456-7890) [Account]
2. Property Investment LLC (234-567-8901) [Account]
3. Cash Home Buyers Inc (345-678-9012) [Account]
4. Use default from .env file

Select account (1-4):
```

**Tips:**
- Choose the account you want to analyze
- Option 4 uses the `GOOGLE_ADS_CUSTOMER_ID` from your `.env` file
- MCC accounts will show as "[MCC/Manager]"

### Step 2: Select Campaign

Choose a specific campaign or analyze all:

```
Available Campaigns:

1. ✓ Motivated Seller Campaign (ID: 123456789) [ENABLED]
2. ✓ Distressed Property Leads (ID: 234567890) [ENABLED]
3. ⏸ Foreclosure Leads (ID: 345678901) [PAUSED]
4. Analyze all campaigns

Select campaign (1-4):
```

**Tips:**
- Select a specific campaign for targeted analysis
- Choose "Analyze all campaigns" for account-wide insights
- Status indicators: ✓ = Enabled, ⏸ = Paused, ✗ = Removed

### Step 3: Set Date Range

Enter the number of days to analyze:

```
Enter number of days to analyze (default: 30): 60
```

**Recommendations:**
- **30 days**: Standard monthly analysis
- **60-90 days**: Better for identifying trends
- **7-14 days**: Quick performance check
- Minimum 7 days recommended for meaningful data

### Step 4: Optimization Goals

Use default goals or enter custom ones:

```
Use default optimization goals? (Y/n): y
```

**Default Goals:**
1. Improve CTR (Click-Through Rate)
2. Reduce cost per conversion
3. Increase conversion rate
4. Improve ROAS (Return on Ad Spend)
5. Optimize budget allocation

**Custom Goals Example:**
```
Enter your optimization goals (press Enter twice when done):
1. Reduce cost per lead by 20%
2. Increase phone call conversions
3. Improve quality of leads from "foreclosure" keywords
[Press Enter twice]
```

### Step 5: Analysis

Claude analyzes your data and provides recommendations:

```
📊 Fetching comprehensive campaign data...
📅 Date range: Last 30 days
🎯 Campaign ID: 123456789

Fetching account summary...
Fetching campaign data...
Fetching keyword data...

🤖 Claude Analysis in Progress...
This may take a minute. Claude is analyzing your campaign data...
```

**Analysis includes:**
- Campaign performance metrics
- Ad group performance
- Individual ad performance
- Keyword analysis with Quality Score
- Auction insights (competitive data)
- Budget allocation analysis

### Step 6: Review Recommendations

The output includes:

**Executive Summary**
- Overall campaign health
- Critical optimization opportunities

**Priority Recommendations**
- Top 3-5 highest-impact actions
- Expected impact
- Implementation priority (High/Medium/Low)

**Keyword Recommendations**
- New keywords to add
- Keywords to pause/remove
- Negative keywords
- Match type adjustments

**Bid & Budget Optimization**
- Bid adjustments
- Budget reallocation
- Competitive positioning strategies

**Ad Copy & Creative**
- Ad copy improvements
- A/B testing recommendations

**Targeting & Settings**
- Geographic adjustments
- Demographic targeting
- Scheduling optimizations

**Performance Projections**
- Expected metric improvements

### Step 7: Save Results (Optional)

```
Save recommendations to file? (y/N): y
✓ Recommendations saved to: recommendations_123_456_7890_123456789.txt
```

Files are saved in the project root with format:
`recommendations_{customer_id}_{campaign_id}.txt`

## Model Selection

When you start the analyzer, you can choose the Claude model:

```
Claude Model Selection:
1. Claude 3.5 Sonnet (Recommended - Best balance)
2. Claude 3.7 Sonnet (Newer, more capable)
3. Claude 3 Opus (Most powerful, higher cost)
4. Use current setting: claude-3-5-sonnet-20241022

Select model (1-4, default: 4):
```

**Recommendation:** Use Claude 3.5 Sonnet (option 1) for best balance of performance and cost.

See [MODEL_COMPARISON.md](MODEL_COMPARISON.md) for detailed comparison.

## Example Output

```
📋 OPTIMIZATION RECOMMENDATIONS
============================================================

**EXECUTIVE SUMMARY**

Your campaign shows strong conversion performance (3.2% conversion rate) 
but is losing 35% of potential impressions due to budget constraints. 
The primary opportunity is expanding high-ROAS keywords while pausing 
underperforming broad match terms.

**PRIORITY RECOMMENDATIONS**

1. **Increase Budget for "Motivated Seller" Campaign** [HIGH PRIORITY]
   - Current budget: $2,000/month
   - Recommended: $3,500/month (+75%)
   - Expected impact: +45% conversions, maintain 4.2 ROAS
   - Budget lost share: 35% indicates significant opportunity

2. **Pause 12 Broad Match Keywords with Zero Conversions** [HIGH PRIORITY]
   - Keywords: "sell house", "home buyer", etc.
   - Current spend: $450/month
   - Expected savings: $450/month, reallocate to exact match
   ...

**KEYWORD RECOMMENDATIONS**

New Keywords to Add:
- "sell house fast cash" (Exact Match) - High intent, lower competition
- "avoid foreclosure help" (Phrase Match) - Targets distressed sellers
- "inherited property sale" (Exact Match) - Niche but high-value
...

**PERFORMANCE PROJECTIONS**

If recommendations are implemented:
- CTR: +0.8% (from 2.1% to 2.9%)
- Cost per Conversion: -$15 (from $85 to $70)
- Conversion Rate: +0.5% (from 3.2% to 3.7%)
- Monthly Conversions: +25 (from 80 to 105)
```

## Best Practices

### 1. Regular Analysis
- **Monthly**: Standard optimization review
- **Quarterly**: Strategic deep dive
- **After Changes**: Analyze impact of optimizations

### 2. Date Range Selection
- Use 30+ days for meaningful trends
- Longer periods (60-90 days) for seasonal analysis
- Shorter periods (7-14 days) for quick checks

### 3. Campaign Selection
- Analyze individual campaigns for specific insights
- Use "all campaigns" for account-wide strategy
- Focus on active campaigns first

### 4. Goal Customization
- Align goals with business objectives
- Be specific (e.g., "reduce cost per lead by 20%")
- Prioritize 3-5 key goals

### 5. Implementation
- Start with High-priority recommendations
- Test changes incrementally
- Monitor results and iterate

## Advanced Usage

### Custom Model Selection

Set default model in `.env`:
```env
CLAUDE_MODEL=claude-3-5-sonnet-20241022
```

Available models:
- `claude-3-5-sonnet-20241022` (recommended)
- `claude-3-7-sonnet-20250219` (newer)
- `claude-3-opus-20240229` (premium)

### Analyzing Multiple Accounts

1. Run the analyzer
2. Select different accounts from the list
3. Save recommendations with different filenames
4. Compare results across accounts

### Exporting for Team Review

Save recommendations and share:
```bash
# Analysis will prompt to save
# Or manually copy output
python real_estate_analyzer.py > analysis_output.txt
```

## Troubleshooting

### "No accessible customer accounts found"
- Verify MCC account ID in `.env`
- Ensure API access is enabled
- Check account linking in Google Ads

### "No campaign data found"
- Verify account has active campaigns
- Check date range (may be too short)
- Ensure campaigns aren't all paused

### "Error fetching data"
- Check internet connection
- Verify API credentials
- Ensure account has sufficient data

### Slow Analysis
- Reduce date range
- Select specific campaign instead of "all"
- Use Claude 3.5 Sonnet (faster than Opus)

## Tips for Best Results

1. **Data Quality**: Ensure campaigns have sufficient data (100+ clicks recommended)
2. **Date Range**: Use 30+ days for reliable insights
3. **Specific Goals**: Custom goals get better recommendations
4. **Regular Reviews**: Monthly analysis catches issues early
5. **Implementation**: Act on High-priority recommendations first

## Next Steps

After getting recommendations:

1. **Review Priority Items** - Focus on High-priority recommendations
2. **Plan Implementation** - Schedule changes in Google Ads
3. **Monitor Results** - Track performance after changes
4. **Iterate** - Run analysis again after 2-4 weeks

For setup instructions, see [SETUP.md](SETUP.md).

# Real Estate Google Ads Analyzer Guide

## Overview

Specialized analyzer for real estate investor clients targeting motivated and distressed home sellers. Uses a comprehensive Claude prompt to provide detailed optimization recommendations.

## Features

- ✅ **MCC Account Selection** - Choose from all accessible customer accounts
- ✅ **Campaign Selection** - Select specific campaign or analyze all
- ✅ **Comprehensive Data Analysis** - Campaigns, ad groups, ads, keywords, and auction insights
- ✅ **Custom Claude Prompt** - Specialized analysis framework for real estate campaigns
- ✅ **Actionable Recommendations** - Specific, prioritized optimization suggestions

## Quick Start

```bash
source venv/bin/activate
python real_estate_analyzer.py
```

Or use the quick script:
```bash
./run_real_estate.sh
```

## Usage Flow

### Step 1: Select Customer Account

The tool will list all accessible customer accounts from your MCC:
```
Available Customer Accounts:

1. Real Estate Investor Account (123-456-7890) [Account]
2. Property Investment LLC (234-567-8901) [Account]
3. Cash Home Buyers Inc (345-678-9012) [Account]
4. Use default from .env file

Select account (1-4):
```

### Step 2: Select Campaign

Choose a specific campaign or analyze all:
```
Available Campaigns:

1. ✓ Motivated Seller Campaign (ID: 123456789) [ENABLED]
2. ✓ Distressed Property Leads (ID: 234567890) [ENABLED]
3. ⏸ Foreclosure Leads (ID: 345678901) [PAUSED]
4. Analyze all campaigns

Select campaign (1-4):
```

### Step 3: Set Date Range

Enter the number of days to analyze (default: 30):
```
Enter number of days to analyze (default: 30): 60
```

### Step 4: Optimization Goals

Use default goals or enter custom ones:
```
Use default optimization goals? (Y/n): y
```

Default goals:
1. Improve CTR (Click-Through Rate)
2. Reduce cost per conversion
3. Increase conversion rate
4. Improve ROAS (Return on Ad Spend)
5. Optimize budget allocation

### Step 5: Analysis

Claude will analyze your data and provide comprehensive recommendations.

## Analysis Framework

The analyzer uses a specialized prompt that examines:

1. **Campaign Performance Review**
   - Impressions, clicks, CTR
   - Conversions, conversion rate
   - CPC, cost per conversion
   - ROAS

2. **Ad Group Analysis**
   - Top and underperforming ad groups
   - Performance patterns

3. **Ad Copy Evaluation**
   - Best performing ad copy
   - Underperforming ads

4. **Keyword Performance**
   - Quality Score analysis
   - Cost efficiency
   - Match type effectiveness
   - Negative keyword opportunities

5. **Auction Insights**
   - Impression share
   - Competitive overlap
   - Position metrics
   - Outranking share

6. **Budget Allocation**
   - Efficiency across campaigns/ad groups

## Output Structure

The recommendations include:

### Executive Summary
Brief overview of campaign health and critical opportunities.

### Priority Recommendations
Top 3-5 highest-impact recommendations with:
- Specific actions
- Expected impact
- Implementation priority (High/Medium/Low)

### Keyword Recommendations
- New keywords to add (with rationale)
- Keywords to pause/remove
- Negative keywords
- Match type adjustments

### Bid & Budget Optimization
- Bid adjustment recommendations
- Budget reallocation suggestions
- Competitive positioning strategies

### Ad Copy & Creative
- Specific ad copy improvements
- A/B testing recommendations

### Targeting & Settings
- Geographic adjustments
- Demographic targeting
- Scheduling optimizations
- Device bid adjustments

### Performance Projections
Expected improvements in:
- CTR
- Cost per conversion
- Conversion rate

## Example Output

```
📋 OPTIMIZATION RECOMMENDATIONS
============================================================

**EXECUTIVE SUMMARY**

Your campaign shows strong conversion performance (3.2% conversion rate) 
but is losing 35% of potential impressions due to budget constraints. 
The primary opportunity is expanding high-ROAS keywords while pausing 
underperforming broad match terms.

**PRIORITY RECOMMENDATIONS**

1. **Increase Budget for "Motivated Seller" Campaign** [HIGH PRIORITY]
   - Current budget: $2,000/month
   - Recommended: $3,500/month (+75%)
   - Expected impact: +45% conversions, maintain 4.2 ROAS
   - Budget lost share: 35% indicates significant opportunity

2. **Pause 12 Broad Match Keywords with Zero Conversions** [HIGH PRIORITY]
   - Keywords: "sell house", "home buyer", etc.
   - Current spend: $450/month
   - Expected savings: $450/month, reallocate to exact match
   ...

**KEYWORD RECOMMENDATIONS**

New Keywords to Add:
- "sell house fast cash" (Exact Match) - High intent, lower competition
- "avoid foreclosure help" (Phrase Match) - Targets distressed sellers
- "inherited property sale" (Exact Match) - Niche but high-value
...

**BID & BUDGET OPTIMIZATION**

- Increase bids on "cash home buyer" keywords by 15% (currently position 3.2)
- Decrease bids on "real estate" broad match by 20% (low conversion rate)
- Shift $500/month from "General Leads" to "Motivated Seller" campaign
...

**PERFORMANCE PROJECTIONS**

If recommendations are implemented:
- CTR: +0.8% (from 2.1% to 2.9%)
- Cost per Conversion: -$15 (from $85 to $70)
- Conversion Rate: +0.5% (from 3.2% to 3.7%)
- Monthly Conversions: +25 (from 80 to 105)
```

## Saving Results

After analysis, you can save recommendations to a file:
```
Save recommendations to file? (y/N): y
✓ Recommendations saved to: recommendations_123_456_7890_123456789.txt
```

## Troubleshooting

### "No accessible customer accounts found"
- Verify your MCC account ID in `.env`
- Ensure API access is enabled for the MCC
- Check that you're authenticated with the correct account

### "No campaign data found"
- Verify the selected account has active campaigns
- Check the date range (campaigns may not have data for selected period)
- Ensure campaigns are not all paused/removed

### "Error listing customer accounts"
- Your account may not be an MCC or may not have linked accounts
- Try using a specific customer ID directly in `.env`

## Advanced Usage

### Analyze Specific Campaign via Command Line

You can modify the script to accept command-line arguments, or directly edit the code to hardcode:
- Customer ID
- Campaign ID
- Date range
- Optimization goals

### Custom Optimization Goals

Enter specific goals when prompted:
```
Enter your optimization goals (press Enter twice when done):
1. Reduce cost per lead by 20%
2. Increase phone call conversions
3. Improve quality of leads from "foreclosure" keywords
[Press Enter twice]
```

## Cost Considerations

- **Google Ads API**: Free
- **Claude API**: ~$0.03-0.05 per analysis (depends on data volume)
  - Uses Claude 3.5 Sonnet
  - Typical analysis: 5,000-10,000 tokens

## Best Practices

1. **Regular Analysis**: Run monthly or after significant campaign changes
2. **Date Range**: Use 30-90 days for meaningful data
3. **Campaign Selection**: Analyze individual campaigns for specific insights
4. **Goal Alignment**: Customize optimization goals based on business objectives
5. **Implementation**: Prioritize High-priority recommendations first

