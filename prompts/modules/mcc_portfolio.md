## MCC Portfolio Bid Strategies for Multi-Client Management

### Understanding Portfolio Bid Strategies

**Portfolio bid strategies** allow multiple campaigns (across multiple accounts) to share a single bidding strategy. Instead of each campaign optimizing independently, they pool their data and optimize as a unified portfolio.

#### Available Portfolio Bid Strategy Types:

1. **Target CPA** (portfolio) - Optimize multiple campaigns toward a shared CPA goal
2. **Target ROAS** (portfolio) - Optimize multiple campaigns toward a shared ROAS goal
3. **Maximize Conversions** (portfolio) - Maximize total conversions across portfolio within budget
4. **Maximize Conversion Value** (portfolio) - Maximize total conversion value across portfolio

**Note**: There is NO "Maximize Clicks" portfolio strategy. Maximize Clicks is always campaign-level only.

### The Portfolio Bid Strategy Question

**Your Question**: "Should I create MCC portfolio bid strategies for Maximize Clicks (launch) and Maximize Conversions (mature campaigns)?"

**Short Answer**: 
- ❌ **NO for Maximize Clicks** - Not available as portfolio strategy (doesn't exist)
- ⚠️ **MAYBE for Maximize Conversions** - Has benefits but also significant risks

### Detailed Analysis: Portfolio Maximize Conversions

#### Potential Benefits:

**1. Pooled Learning Across Clients**
- All campaigns contribute conversion data to one bidding strategy
- Algorithm learns from aggregate performance (10 clients × 5 conversions = 50 conversions for learning)
- New client campaigns benefit from existing client data immediately
- Faster optimization than individual campaign strategies

**2. Cross-Campaign Budget Optimization**
- Algorithm can shift bids across all campaigns in portfolio
- If Client A's campaign is performing well today, gets more aggressive bids
- If Client B's campaign is slow today, gets more conservative bids
- Portfolio-level efficiency optimization

**3. Simplified Management**
- Change bidding strategy settings once, applies to all campaigns
- Consistent approach across all clients
- Easier troubleshooting and performance monitoring

**4. Better Performance in Low-Volume Campaigns**
- Individual campaigns with 5 conversions/month struggle alone
- In portfolio with 50 total conversions/month, much more stable
- Compensates for small individual budgets

#### Significant Risks & Drawbacks:

**1. Cross-Client Budget Cannibalization (MAJOR CONCERN)**
- Algorithm may "rob Peter to pay Paul"
- Example: Client A's budget gets spent more aggressively because Client B's campaign is converting better
- Client A (who's paying you) loses impression share because Client B is performing better
- Can create client service issues: "Why is my budget not spending?"

**2. Loss of Individual Campaign Control**
- Can't optimize individual client campaigns independently
- One client's poor performance can drag down entire portfolio
- Harder to pause or adjust individual clients without affecting others

**3. Performance Attribution Confusion**
- Harder to see which clients are driving portfolio performance
- Reporting becomes more complex
- Difficult to justify performance to individual clients

**4. Market Variation Issues**
- Client in competitive NYC market needs different bidding than client in rural market
- Portfolio strategy applies same logic to both
- May over-bid in cheap markets, under-bid in expensive markets

**5. Client-Specific Issues Affect Everyone**
- One client has landing page issue → lowers entire portfolio performance
- One client pauses campaign for cash flow → affects portfolio learning
- One client's seasonal slowdown → impacts bidding for all clients

**6. Cannot Mix New and Mature Campaigns Effectively**
- New client (0 conversions) in same portfolio as mature client (50 conversions/month)
- Algorithm may deprioritize new client because no proven conversion history
- New clients struggle to get out of learning phase

#### Real-World Example of Portfolio Risk:

**Scenario**: 5 clients in portfolio Maximize Conversions strategy

```
Month 1:
- Client A: Great performance, 15 conversions, $300 CPA
- Client B: Good performance, 10 conversions, $350 CPA
- Client C: Okay performance, 5 conversions, $450 CPA
- Client D: Poor performance, 2 conversions, $600 CPA
- Client E: New client, 0 conversions (learning)

What happens:
- Algorithm sees Client A and B converting well
- Shifts bidding aggression toward their campaigns
- Clients C, D, E get less aggressive bidding (higher CPCs needed)
- Client D complains: "Why is my budget only spending $40/day of $75/day?"
- Client E never gets out of learning phase (budget keeps getting de-prioritized)
- You have to explain to Client D that their budget is being "optimized" with other clients
```

**Client Service Issue**: How do you tell Client D their budget is being used to optimize someone else's campaign?

### Recommended Approach: Campaign-Level Bid Strategies

**For Real Estate Investor Multi-Client Management**:

❌ **DON'T Use Portfolio Bid Strategies** (for most agencies)

✅ **DO Use Campaign-Level Bid Strategies with MCC-Level Conversion Goals**

**Setup**:
- MCC-Level Conversion Goals: Initial Lead, Engaged, Qualified, Under Contract, Closed Deal (shared across all clients) ✅
- Campaign-Level Bid Strategies: Each client campaign has its own Maximize Clicks → Maximize Conversions → Target CPA strategy ✅
- Each client optimizes independently based on their own performance
- But all benefit from MCC-level conversion data pooling

**Why This Is Better**:
- Each client's budget is fully dedicated to their campaign
- No cross-client cannibalization
- Clear performance attribution per client
- Can optimize individual clients without affecting others
- New clients can be in learning phase without dragging down mature clients
- Client service is cleaner (no explaining cross-client optimization)

**You Still Get Cross-Account Learning Benefits From**:
- MCC-level conversion goals (all clients feeding data to same conversion definitions)
- Google learns conversion patterns across all clients
- New clients benefit from existing clients' conversion data
- Just without the bid cannibalization risk

### When Portfolio Bid Strategies MIGHT Make Sense

**Only consider portfolio strategies if**:

✅ All campaigns in portfolio are YOUR internal campaigns (not separate clients)
✅ You're willing to have budgets shift between campaigns dynamically  
✅ All campaigns target same geographic market and audience
✅ All campaigns have similar performance baselines
✅ You want portfolio-level CPA or ROAS target, not individual campaign targets

**Example Where It Works**:
```
Your Company's Internal Campaigns:
- Campaign A: "We Buy Houses" keywords - NYC
- Campaign B: "Cash Home Buyer" keywords - NYC  
- Campaign C: "Sell House Fast" keywords - NYC

All same market, same business, pooled budget = Portfolio strategy makes sense
```

**Example Where It Doesn't Work**:
```
Client Campaigns:
- Client A: Cleveland market
- Client B: Atlanta market
- Client C: Phoenix market

Different clients, different budgets, different markets = Campaign-level strategies better
```

### Alternative: Shared Budget Campaigns (Not Portfolio Bidding)

**Consider this instead**: Create multiple campaigns within ONE client account with shared budget

**Example**:
```
Client A Account:
- Campaign 1: Foreclosure keywords - Maximize Conversions
- Campaign 2: Inherited keywords - Maximize Conversions
- Campaign 3: Probate keywords - Maximize Conversions
- Shared Budget: $150/day across all 3 campaigns

This allows budget shifting between campaigns within the same client
Without the cross-client issues of portfolio bidding
```

### Summary Recommendation for Your Situation

**For Maximize Clicks Phase (New Campaigns)**:
- ❌ Cannot use portfolio strategy (doesn't exist for Maximize Clicks)
- ✅ Each campaign uses campaign-level Maximize Clicks
- Duration: Until 15-30 conversions accumulated
- MCC-level conversion goals provide cross-account learning

**For Maximize Conversions Phase (Established Campaigns)**:
- ❌ Don't use portfolio Maximize Conversions (cross-client risk too high)
- ✅ Each campaign uses campaign-level Maximize Conversions
- Duration: Until 50+ conversions, then move to Target CPA
- MCC-level conversion goals provide cross-account learning

**For Target CPA Phase (Mature Campaigns)**:
- ❌ Don't use portfolio Target CPA (same cross-client risks)
- ✅ Each campaign uses campaign-level Target CPA
- Set target based on individual client's business model
- Some clients may have $250 target, others $400 (different markets/margins)

### The Key Insight

**You don't need portfolio bid strategies to get cross-account learning benefits.**

You get those benefits from:
1. ✅ MCC-level conversion goals (what you're already doing)
2. ✅ Consistent campaign structure across clients
3. ✅ Aggregate data feeding Google's broader algorithm

Portfolio bid strategies add:
1. ⚠️ Cross-campaign budget shifting (often undesirable with separate clients)
2. ⚠️ Unified optimization target (problematic when clients have different goals)
3. ⚠️ Complex attribution (harder to report to individual clients)

**Verdict**: Stick with campaign-level bid strategies, keep MCC-level conversion goals. You get 90% of the benefits with 10% of the risks.

### Exception: Portfolio Target CPA for Similar Clients (Advanced)

**IF** you have clients who:
- All same geographic market
- All same business model and margins
- All same target CPA ($300 across all clients)
- All established campaigns (not mixing new and mature)
- You explicitly tell clients their budgets may shift between campaigns

**THEN** portfolio Target CPA could work:

**Benefits**:
- Algorithm optimizes for $300 CPA across entire portfolio
- Better overall efficiency than individual campaigns
- Can handle temporary performance dips in individual clients

**Setup**:
- Create MCC-level portfolio Target CPA strategy: $300 target
- Add all mature client campaigns to portfolio
- Set shared daily budget OR individual budgets (your choice)
- Monitor closely for cross-client cannibalization

**Warning**: Still has the "Client A subsidizing Client B" risk. Only use if you're comfortable managing that dynamic with clients.

### Final Recommendation

**For Your Multi-Client Real Estate Investor Business**:

**Current Setup (Recommended)**:
- ✅ MCC-level conversion goals shared across all clients
- ✅ Campaign-level bid strategies (Maximize Clicks → Maximize Conversions → Target CPA)
- ✅ Each client's campaign optimizes independently
- ✅ All clients benefit from shared conversion learning
- ✅ No cross-client budget cannibalization
- ✅ Clean client reporting and attribution

**Don't Change To**:
- ❌ Portfolio Maximize Conversions
- ❌ Portfolio Target CPA

**Unless**: You have very specific use case with homogeneous clients in same market willing to have pooled budgets

**You're already doing it right** with MCC-level conversion goals providing cross-account learning without the portfolio bidding risks.

### Recommendation Format for Offline Conversions

When making recommendations about offline conversion strategy:

**Current State Assessment**:
- What conversion actions are currently primary?
- What is the monthly volume of each offline conversion stage?
- What is the current funnel conversion rate at each stage?
- Is GCLID tracking functioning properly?

**Readiness for Progression**:
- Does volume support more advanced primary conversion? (15+ per month minimum)
- Are conversion rates stable and predictable?
- Is the sales cycle length understood and consistent?

**Specific Recommendation**:
- What should be primary conversion(s) based on current data?
- What should be secondary?
- What is the migration timeline and risks?
- What KPIs to monitor during transition?