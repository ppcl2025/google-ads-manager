# Prompt Review & Recommendations

## What to Keep from Your New Prompt (Excellent Additions)

### ✅ **Bidding Strategy Progression Framework** (CRITICAL - Keep This!)
This is the most valuable addition. The Maximize Clicks → Maximize Conversions → Target CPA framework is:
- Highly specific to real estate investor campaigns
- Data-driven with clear thresholds
- Addresses a common mistake (premature bidding strategy changes)
- Includes decision matrix and readiness checks

**Recommendation**: Keep this entire section - it's gold for real estate campaigns.

### ✅ **Real Estate Investor Specific Context**
- Lead quality vs. volume balance
- Market cycle awareness
- Geographic performance considerations
- Seasonal patterns
- Seller motivation psychology

**Recommendation**: Keep all of this - very valuable domain expertise.

### ✅ **Industry Best Practices**
The 14 best practices are excellent and specific to real estate investor campaigns.

**Recommendation**: Keep this section.

### ✅ **Red Flags Section**
Very helpful for identifying critical issues quickly.

**Recommendation**: Keep this, but integrate into analysis framework.

### ✅ **Context Questions**
Good for when more information is needed, but...

**Recommendation**: Keep but add instruction: "Only ask these if absolutely necessary - otherwise infer from data."

## What to Keep from Old Prompt (Critical for Output Quality)

### ✅ **Strict Output Format with Tags**
The old prompt requires:
```
<recommendations>
**EXECUTIVE SUMMARY**
...
</recommendations>
```

**Why Keep**: Your code extracts content between these tags. Without them, the response extraction won't work properly.

### ✅ **"DO NOT Ask Questions" Instructions**
The old prompt explicitly states:
- DO NOT ask questions or request permission
- IMMEDIATELY start with <recommendations>
- Provide complete analysis without introductory text

**Why Keep**: Without this, Claude will ask "Would you like me to proceed?" instead of providing analysis.

### ✅ **Specific Recommendation Structure**
The old prompt requires:
- Exact ad group names, keyword text, ad IDs
- Specific bid amounts/percentages
- Exact ad copy rewrites
- Reference specific data points

**Why Keep**: This ensures actionable, implementable recommendations rather than vague advice.

### ✅ **All Sections Must Be Included**
The old prompt lists ALL required sections and says "do not skip any sections."

**Why Keep**: Prevents truncation messages like "DETAILED RECOMMENDATIONS CONTINUE IN FULL RESPONSE..."

### ✅ **Scratchpad Section**
The old prompt includes a scratchpad for working through analysis before providing recommendations.

**Why Keep**: Helps Claude organize thoughts and provide more structured output.

## Recommended Merged Structure

1. **Start with your new prompt** (the comprehensive role definition and expertise)
2. **Add the bidding strategy progression framework** (your best addition)
3. **Include the analysis framework** from your new prompt
4. **Add the strict output requirements** from the old prompt
5. **Include the specific recommendation structure** from the old prompt
6. **End with the output format** from the old prompt (with <recommendations> tags)

## Key Integration Points

### Merge the Analysis Framework
Your new prompt has a great analysis framework. Enhance it with:
- The specific granular analysis instructions from the old prompt (ad group by ad group, keyword by keyword)
- The requirement to reference specific names/IDs

### Merge the Recommendation Format
Your new prompt has a good recommendation structure. Enhance it with:
- The exact output format from the old prompt (<recommendations> tags)
- The requirement for specific data points (ad group names, keyword text, exact metrics)
- The "all sections must be included" requirement

### Add Output Requirements
Your new prompt doesn't have the strict output requirements. Add:
- DO NOT ask questions
- Start immediately with <recommendations>
- Include ALL sections
- Reference specific data points
- Provide exact, actionable recommendations

## Specific Recommendations

1. **Keep your bidding strategy progression framework** - it's the best part
2. **Add the <recommendations> tag structure** - required for code to work
3. **Add "DO NOT ask questions" instructions** - prevents confirmation requests
4. **Add the scratchpad section** - helps with structured thinking
5. **Merge the granular analysis instructions** - old prompt's "for EACH ad group" approach
6. **Keep your industry best practices** - very valuable
7. **Keep your red flags** - helpful for quick issue identification
8. **Add the "all sections must be included" requirement** - prevents truncation

## What to Remove/Modify

1. **Context Questions Section**: Modify to say "Only ask if absolutely necessary - otherwise infer from data"
2. **Output Format Preferences**: Replace with the strict <recommendations> format from old prompt
3. **Communication Style**: Keep but add emphasis on "specific data points" and "exact recommendations"

## Final Recommendation

Your new prompt is excellent and much more comprehensive. However, you need to:
1. Add the strict output format requirements from the old prompt
2. Add the <recommendations> tag structure
3. Add the "do not ask questions" instructions
4. Merge the granular "for EACH" analysis approach from the old prompt
5. Keep all your excellent additions (bidding strategy, industry best practices, etc.)

The result will be a comprehensive, strategic prompt that also produces the structured, actionable output your code expects.

