## Biweekly Client Reporting Framework

### Report Design Philosophy: Clear, Concise, Actionable

**Core Principles**:
- **Keep it to 2-3 pages maximum** (clients won't read more)
- **Lead with what matters**: Cost per lead, lead volume, conversion trends
- **Show progress**: Compare to previous period and goals
- **Be honest**: Flag issues early, explain what you're doing to fix them
- **Action-oriented**: Every insight should have "What we're doing" or "What's next"
- **Visual-heavy**: Charts > tables > paragraphs

**What Clients Actually Care About**:
1. How many leads did I get?
2. What did each lead cost me?
3. Are things getting better or worse?
4. What are you doing to improve results?
5. Should I be worried about anything?

### Report Structure (2-3 Pages)

#### PAGE 1: Executive Summary & Key Metrics

**Section 1: Performance Snapshot** (Top of page)

Visual layout with 4-6 large metric cards showing:
- Total Leads (with % change vs. last period)
- Cost Per Lead (with % change vs. last period)
- Ad Spend (with % of budget used)
- Qualified Leads (if tracked)
- Phone Calls (if tracked)
- Closed Deals (if tracked)

**Use color coding**:
- 🟢 Green: Performance improving vs. last period
- 🟡 Yellow: Flat performance (±5%)
- 🔴 Red: Performance declining vs. last period

**Section 2: Two-Week Trend** (Middle of page)

Simple line chart showing daily leads over the 14-day period:
- X-axis: Dates (last 14 days)
- Y-axis: Number of leads
- One line: Total leads per day
- Shaded area: Target range (helps visualize if on track)

**Section 3: What This Means** (Bottom of page)

3-4 bullet points in plain English:
- ✅ "Your cost per lead decreased 8% - we paused underperforming keywords"
- ⚠️ "Lead volume dropped last Thursday due to budget limit - increasing budget this week"
- 🎯 "On track to hit 50-60 leads this month based on current pace"
- 📈 "Qualified lead rate improved to 64% (vs. 58% last period)"

**AVOID**: Technical jargon, detailed metrics tables, long paragraphs

---

#### PAGE 2: What's Working & What's Not

**Section 1: Top Performers** (1/3 of page)

"What's Driving Your Best Leads"

Simple table (3-5 rows max):

| Keyword/Ad Group | Leads | Cost/Lead | Why It's Working |
|------------------|-------|-----------|------------------|
| "Facing Foreclosure" | 8 | $198 | Strong pain point messaging |
| "Inherited Property" | 6 | $215 | High-intent motivated sellers |
| "Sell House Fast [City]" | 5 | $234 | Local + urgency combo |

**Keep descriptions short** - one reason per row

**Section 2: Areas We're Improving** (1/3 of page)

"What We're Optimizing This Week"

Bullet list (3-4 items max):
- 🔧 **Paused 8 underperforming keywords** → Saving $450/week, reallocating to proven performers
- 📝 **Testing new ad copy** → "Stop Foreclosure Fast" messaging showing +35% CTR improvement
- 🎯 **Refined targeting** → Excluding investor searches, focusing on motivated homeowners
- 💰 **Budget increase approved** → Going from $225/day to $275/day starting Monday

**Section 3: Lead Quality Insights** (1/3 of page)

If you track offline conversions (qualified/closed deals):

"Lead Quality This Period"

Visual funnel or simple bars showing:
- Total Leads → Qualified Leads → Under Contract → Closed Deals
- Conversion rates at each stage

Or if simpler:
- Phone calls: 22 (79% of leads)
- Form fills: 6 (21% of leads)
- Best performing lead source: Phone calls (85% qualification rate)

---

#### PAGE 3: Next Steps & Goals (Optional - only if needed)

**Section 1: Action Plan for Next 2 Weeks**

Clear list of what you're doing:

**Immediate Actions (This Week)**:
- ✅ Increase daily budget to $275 (approved)
- ✅ Launch new "Probate Property" ad group
- ✅ Add 30+ negative keywords to reduce wasted clicks

**Testing & Optimization (Next Week)**:
- 🧪 Test mobile-focused ad copy with click-to-call emphasis
- 🧪 Expand into 3 new zip codes based on foreclosure data
- 📊 Analyze weekend vs. weekday performance

**Section 2: Goals for Next Period**

Simple, specific targets:
- 🎯 Increase leads from 28 to 35-40 (with budget increase)
- 🎯 Maintain or improve cost per lead (target: $230-250)
- 🎯 Test 2 new ad variations in top-performing ad groups
- 🎯 Improve mobile conversion rate from 22% to 28%

**Section 3: Questions or Concerns?**

Simple footer:
"Have questions about this report? Want to discuss strategy? Reply to this email or call [your number]."

---

### Report Format Options

#### Option A: AI-Generated PDF Report (RECOMMENDED FOR THIS SYSTEM)

**This system can generate professional PDF reports directly using reportlab.**

**Pros**:
- Fully automated - AI generates the entire report
- Customizable - Can tailor to each client automatically
- Fast - Generate in seconds from campaign data
- Scalable - Same approach works for 1 or 100 clients
- Professional looking with charts and formatted tables

**Cons**:
- Initial prompt engineering to get format right
- May need refinement after first few reports

**When to use**: When using this AI system to analyze campaign data - the AI can generate the PDF in the same session

**How it works**:
1. User provides campaign data to AI (from Google Ads API)
2. AI analyzes performance using the strategist prompt
3. User requests: "Generate a biweekly client report PDF"
4. AI uses reportlab to create 2-page PDF with:
   - Page 1: Key metrics, trend visualization, "What This Means" summary
   - Page 2: Top performers, optimizations made, next steps
5. AI outputs PDF file ready to email to client

**Report Generation Instructions for AI**:

When user requests a biweekly client report PDF, follow these steps:

1. **Analyze the campaign data** using the strategist framework in this prompt

2. **Generate a 2-page PDF report** using reportlab with this structure:

**Page 1: Performance Overview**
- Header: Client name, date range, logo area
- Key metrics cards (4-6 metrics): Total Leads, Cost per Lead, Ad Spend, Qualified Leads, etc.
- Trend chart: Simple line or bar chart showing daily leads over 14-day period
- "What This Means" section: 3-4 bullet points in plain English explaining performance

**Page 2: Actions & Insights**
- "What's Working" table: 3-5 top performers with leads, cost per lead, and brief reason
- "What We're Optimizing" section: 2-3 bullets showing actions taken this period
- "Next Steps" section: 2-3 specific actions planned for next 2 weeks
- Footer: Contact information

**Technical specifications**:
- Use reportlab.platypus for structure (SimpleDocTemplate)
- Use letter size (8.5" x 11")
- Professional fonts: Helvetica or Times-Roman
- Color coding: Green for positive metrics, red for declining, yellow for flat
- Keep text concise - use bullet points, not paragraphs
- Include page numbers
- Save as client-friendly filename: `[ClientName]_Report_[DateRange].pdf`

**Color Coding for Metrics**:
- Use green text or background for improving metrics (↑)
- Use red text or background for declining metrics (↓)
- Use black/neutral for stable metrics (±5%)

**Chart Guidelines**:
- Keep charts simple - line or bar charts only
- Don't try to create complex visualizations
- Focus on daily lead trends over the 14-day period
- Label axes clearly
- Use appropriate scale (don't start Y-axis at 0 if misleading)

3. **Save the PDF** to the same Google Drive folder as optimization reports

4. **Provide a 2-3 sentence summary** of what's in the report

**Example AI Response**:
```
I've generated your biweekly client report PDF. Key highlights:
- Cost per lead improved 8% to $244.54 while volume increased 12%
- Paused 8 underperforming keywords and testing new foreclosure-focused ad copy
- Recommended increasing daily budget to $275 to capitalize on strong performance

[Link to PDF file]
```

---

### What NOT to Include in Reports

❌ **Impressions, CTR, Average Position** - Clients don't care, causes confusion
❌ **Quality Score details** - Too technical, not actionable for client
❌ **Search term reports** - Too granular, overwhelming
❌ **Detailed keyword bid changes** - Unnecessary detail
❌ **Long paragraphs explaining Google Ads mechanics** - Boring, confusing
❌ **More than 3 pages** - Nobody reads past page 3
❌ **Month-over-month comparisons in first 3 months** - Not enough data, causes panic
❌ **Industry benchmarks** - Usually not apples-to-apples, leads to arguments
❌ **Competitive analysis** - Too speculative, hard to defend

---

### Special Situations

#### First Report (Days 1-14 of new campaign)

**What to emphasize**:
- ✅ Campaign is live and running
- ✅ We're gathering data
- ✅ Initial trends (even if not statistically significant yet)
- ✅ What we're learning

**What to downplay**:
- ⚠️ Don't compare to goals yet (too early)
- ⚠️ Don't promise specific results
- ⚠️ Expect volatility message

**Template language**: "First 2 weeks are about data gathering and optimization. Early results show [positive metric] and we're [action you're taking]. Expect performance to stabilize over next 4-6 weeks."

---

#### Underperforming Period (Leads down, CPA up)

**How to present**:
- 🔴 Be honest: "Performance dipped this period"
- 💡 Explain why: "Increased competition in foreclosure keywords drove up costs"
- 🔧 Show action: "We're expanding into inherited property keywords where competition is lower"
- 📊 Provide context: "Still tracking for 45-50 leads this month (within 10% of goal)"

**What NOT to do**:
- ❌ Blame the client ("Your landing page isn't converting")
- ❌ Blame external factors only ("Market is just tough right now")
- ❌ Hide the bad news in jargon or buried in page 3
- ❌ Panic the client ("This is a disaster!")

**Template language**: "Cost per lead increased 12% this period due to [specific reason]. We've already implemented [specific changes] and expect to see improvement in the next report. This is a normal fluctuation and we're on it."

---

#### High-Performing Period (Crushing goals)

**How to present**:
- 🟢 Celebrate: "Best 2-week period yet!"
- 📈 Show the wins: "Cost per lead down 22%, volume up 15%"
- 🎯 Explain why: "New ad copy and budget increase drove results"
- 🚀 Look ahead: "Opportunity to scale - increase budget to $350/day?"

**What NOT to do**:
- ❌ Overpromise: "We'll keep improving every period" (regression to mean happens)
- ❌ Take all credit: "Our genius optimization" (luck plays a role)
- ❌ Ignore potential issues: (What if performance drops next period?)

**Template language**: "Exceptional results this period - 22% better CPA and 15% more leads. The [specific change] is really working. Let's discuss scaling up budget to capture even more opportunities while performance is strong."

---

### Report Delivery Best Practices

**Timing**: Send reports within 2 business days of period end
- Period ends Sunday → Send Tuesday morning
- Shows you're on top of things
- Gives client time to review before next period starts

**Delivery Method**: 
- Email with PDF attachment (always)
- Optional: Also share live Looker Studio link (for clients who want real-time access)
- Cc yourself and keep organized folder (for reference in future periods)

**Follow-up**:
- Give client 48 hours to respond
- If no response, brief check-in: "Got your report? Any questions?"
- Don't over-follow-up (they're busy)

**Standing Call** (Optional for high-value clients):
- 15-minute biweekly call to walk through report
- Screen share the live dashboard
- Discuss strategy and get immediate feedback
- Build relationship beyond just reports

---

### AI Prompt Integration Recommendations

When the AI analyzes campaign data for client reporting:

**Extract these insights automatically**:
1. % change in key metrics vs. previous period
2. Top 3 performing keywords/ad groups (by conversion and CPA)
3. Bottom 3 underperformers that should be paused/optimized
4. Anomalies or trends (sudden changes in performance)
5. Specific optimization actions taken this period
6. Recommended actions for next period

**Generate report-ready summaries**:
- 3-4 bullet "What This Means" points
- 2-3 "What We're Optimizing" actions
- 2-3 "Next Steps" with expected impact

**Flag potential client concerns**:
- Performance declining vs. previous period
- Not tracking to monthly goals
- Budget constraints limiting performance
- Low lead quality signals

**Use this prompt for report generation**:
```
"Analyze this campaign data for a biweekly client report. Client is a real estate investor 
who buys houses from motivated sellers. Focus on:
1. Lead volume and cost per lead vs. previous 14 days
2. What's working well (top performers)
3. What we optimized this period
4. Recommendations for next 2 weeks
5. If there are issues, explain in simple terms and what we're doing to fix

Keep explanations client-friendly - avoid jargon. Frame everything in terms of business 
impact (more leads, lower cost, better quality)."
```