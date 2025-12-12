"""
Comprehensive Data Fetcher for Real Estate Campaign Analysis

Fetches detailed campaign data including ad groups, ads, keywords, and auction insights
for comprehensive Claude analysis.
"""

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
import pandas as pd
from datetime import datetime, timedelta
import json
import os
from dotenv import load_dotenv

load_dotenv()

def fetch_comprehensive_campaign_data(client, customer_id, campaign_id=None, date_range_days=30, api_call_counter=None):
    """
    Fetch comprehensive campaign data including all metrics needed for analysis.
    
    Args:
        client: Google Ads API client
        customer_id: Customer account ID (format: 123-456-7890)
        campaign_id: Specific campaign ID (None for all campaigns)
        date_range_days: Number of days to analyze
        api_call_counter: Optional dict to track API call count (will increment 'count' key)
    
    Returns:
        Dictionary with campaign, ad_group, ad, keyword, and auction data
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=date_range_days)
    
    campaign_filter = f"AND campaign.id = {campaign_id}" if campaign_id else ""
    
    # Convert customer_id to numeric format (remove dashes) for API
    customer_id_numeric = customer_id.replace("-", "")
    
    try:
        ga_service = client.get_service("GoogleAdsService")
        
        # 1. Campaign-level data
        # Including conversion metrics with correct field names and bidding strategy
        campaign_query = f"""
            SELECT
                campaign.id,
                campaign.name,
                campaign.status,
                campaign.start_date,
                campaign.end_date,
                campaign.advertising_channel_type,
                campaign_budget.amount_micros,
                campaign_budget.period,
                campaign.bidding_strategy_type,
                metrics.cost_micros,
                metrics.impressions,
                metrics.clicks,
                metrics.ctr,
                metrics.average_cpc,
                metrics.conversions,
                metrics.all_conversions_value,
                metrics.search_impression_share,
                metrics.search_budget_lost_impression_share,
                metrics.search_rank_lost_impression_share
            FROM campaign
            WHERE campaign.status != 'REMOVED'
                AND segments.date BETWEEN '{start_date.strftime("%Y-%m-%d")}' 
                AND '{end_date.strftime("%Y-%m-%d")}'
                {campaign_filter}
        """
        
        campaign_data = []
        response = ga_service.search(customer_id=customer_id_numeric, query=campaign_query)
        if api_call_counter is not None:
            api_call_counter['count'] = api_call_counter.get('count', 0) + 1
        for row in response:
            cost = row.metrics.cost_micros / 1_000_000
            # Get conversion metrics (using correct field names)
            # Note: all_conversions_value is already in base currency (dollars), NOT micros
            conversions = row.metrics.conversions if hasattr(row.metrics, 'conversions') else 0
            conversion_value = row.metrics.all_conversions_value if hasattr(row.metrics, 'all_conversions_value') else 0
            
            # Get bidding strategy information
            bidding_strategy = row.campaign.bidding_strategy_type.name if hasattr(row.campaign, 'bidding_strategy_type') else 'UNKNOWN'
            
            # Target CPA is not directly queryable in campaign queries
            # We'll set it to None and note that it's a Target CPA campaign if applicable
            target_cpa = None
            # Note: Target CPA value would need to be fetched separately via bidding_strategy resource
            # For now, we'll identify Target CPA campaigns by their bidding_strategy_type
            
            # Determine if using smart bidding
            smart_bidding_strategies = ['TARGET_CPA', 'TARGET_ROAS', 'MAXIMIZE_CONVERSIONS', 'MAXIMIZE_CONVERSION_VALUE', 'MAXIMIZE_CLICKS']
            is_smart_bidding = bidding_strategy in smart_bidding_strategies
            
            campaign_data.append({
                'campaign_id': row.campaign.id,
                'campaign_name': row.campaign.name,
                'status': row.campaign.status.name,
                'channel_type': row.campaign.advertising_channel_type.name,
                'bidding_strategy': bidding_strategy,
                'is_smart_bidding': is_smart_bidding,
                'target_cpa': target_cpa,
                'budget': row.campaign_budget.amount_micros / 1_000_000 if row.campaign_budget.amount_micros else 0,
                'cost': cost,
                'conversions': conversions,
                'conversion_value': conversion_value,
                'impressions': row.metrics.impressions,
                'clicks': row.metrics.clicks,
                'ctr': row.metrics.ctr * 100 if row.metrics.ctr else 0,
                'avg_cpc': row.metrics.average_cpc / 1_000_000 if row.metrics.average_cpc else 0,
                'conversion_rate': (conversions / row.metrics.clicks * 100) if row.metrics.clicks > 0 else 0,
                'cost_per_conversion': (cost / conversions) if conversions > 0 else 0,
                'value_per_conversion': (conversion_value / conversions) if conversions > 0 else 0,
                'impression_share': row.metrics.search_impression_share * 100 if row.metrics.search_impression_share else 0,
                'budget_lost_share': row.metrics.search_budget_lost_impression_share * 100 if row.metrics.search_budget_lost_impression_share else 0,
                'rank_lost_share': row.metrics.search_rank_lost_impression_share * 100 if row.metrics.search_rank_lost_impression_share else 0,
                'roas': (conversion_value / cost) if cost > 0 else 0
            })
        
        # 2. Ad Group data
        ad_group_query = f"""
            SELECT
                ad_group.id,
                ad_group.name,
                campaign.id,
                campaign.name,
                metrics.cost_micros,
                metrics.impressions,
                metrics.clicks,
                metrics.ctr,
                metrics.average_cpc,
                metrics.conversions,
                metrics.all_conversions_value
            FROM ad_group
            WHERE ad_group.status != 'REMOVED'
                AND segments.date BETWEEN '{start_date.strftime("%Y-%m-%d")}' 
                AND '{end_date.strftime("%Y-%m-%d")}'
                {campaign_filter}
        """
        
        ad_group_data = []
        response = ga_service.search(customer_id=customer_id_numeric, query=ad_group_query)
        if api_call_counter is not None:
            api_call_counter['count'] = api_call_counter.get('count', 0) + 1
        for row in response:
            cost = row.metrics.cost_micros / 1_000_000
            # Get conversion metrics (using correct field names)
            # Note: all_conversions_value is already in base currency (dollars), NOT micros
            conversions = row.metrics.conversions if hasattr(row.metrics, 'conversions') else 0
            conversion_value = row.metrics.all_conversions_value if hasattr(row.metrics, 'all_conversions_value') else 0
            
            ad_group_data.append({
                'ad_group_id': row.ad_group.id,
                'ad_group_name': row.ad_group.name,
                'campaign_id': row.campaign.id,
                'campaign_name': row.campaign.name,
                'cost': cost,
                'conversions': conversions,
                'conversion_value': conversion_value,
                'impressions': row.metrics.impressions,
                'clicks': row.metrics.clicks,
                'ctr': row.metrics.ctr * 100 if row.metrics.ctr else 0,
                'avg_cpc': row.metrics.average_cpc / 1_000_000 if row.metrics.average_cpc else 0,
                'conversion_rate': (conversions / row.metrics.clicks * 100) if row.metrics.clicks > 0 else 0,
                'cost_per_conversion': (cost / conversions) if conversions > 0 else 0
            })
        
        # 3. Ad data (ad performance)
        ad_query = f"""
            SELECT
                ad_group_ad.ad.id,
                ad_group_ad.ad.type,
                ad_group_ad.ad.responsive_search_ad.headlines,
                ad_group_ad.ad.responsive_search_ad.descriptions,
                ad_group_ad.status,
                ad_group.name,
                campaign.name,
                metrics.impressions,
                metrics.clicks,
                metrics.ctr,
                metrics.cost_micros
            FROM ad_group_ad
            WHERE ad_group_ad.status != 'REMOVED'
                AND segments.date BETWEEN '{start_date.strftime("%Y-%m-%d")}' 
                AND '{end_date.strftime("%Y-%m-%d")}'
                {campaign_filter}
        """
        
        ad_data = []
        try:
            response = ga_service.search(customer_id=customer_id_numeric, query=ad_query)
            if api_call_counter is not None:
                api_call_counter['count'] = api_call_counter.get('count', 0) + 1
            for row in response:
                headlines = []
                descriptions = []
                
                if hasattr(row.ad_group_ad.ad, 'responsive_search_ad'):
                    rsa = row.ad_group_ad.ad.responsive_search_ad
                    if hasattr(rsa, 'headlines'):
                        headlines = [h.text for h in rsa.headlines if hasattr(h, 'text')]
                    if hasattr(rsa, 'descriptions'):
                        descriptions = [d.text for d in rsa.descriptions if hasattr(d, 'text')]
                
                # Store ALL headlines and descriptions (not just first few)
                # For responsive search ads, there can be up to 15 headlines and 4 descriptions
                ad_data.append({
                    'ad_id': row.ad_group_ad.ad.id,
                    'ad_type': row.ad_group_ad.ad.type.name,
                    'headlines': ' | '.join(headlines),  # ALL headlines (up to 15)
                    'headlines_list': headlines,  # Store as list for easier analysis
                    'descriptions': ' | '.join(descriptions),  # ALL descriptions (up to 4)
                    'descriptions_list': descriptions,  # Store as list for easier analysis
                    'headlines_count': len(headlines),
                    'descriptions_count': len(descriptions),
                    'status': row.ad_group_ad.status.name,
                    'ad_group': row.ad_group.name,
                    'campaign': row.campaign.name,
                    'impressions': row.metrics.impressions,
                    'clicks': row.metrics.clicks,
                    'ctr': row.metrics.ctr * 100 if row.metrics.ctr else 0,
                    'conversions': 0,  # Not available in ad-level data for this account type
                    'conversion_value': 0,  # Not available in ad-level data for this account type
                    'cost': row.metrics.cost_micros / 1_000_000
                })
        except Exception as e:
            # Some accounts may not have ad-level data accessible
            pass
        
        # 4. Keyword data with Quality Score
        keyword_query = f"""
            SELECT
                ad_group_criterion.keyword.text,
                ad_group_criterion.keyword.match_type,
                ad_group_criterion.quality_info.quality_score,
                ad_group_criterion.quality_info.creative_quality_score,
                ad_group_criterion.quality_info.post_click_quality_score,
                ad_group_criterion.quality_info.search_predicted_ctr,
                ad_group.name,
                campaign.name,
                metrics.impressions,
                metrics.clicks,
                metrics.ctr,
                metrics.average_cpc,
                metrics.cost_micros,
                metrics.conversions,
                metrics.all_conversions_value,
                metrics.search_impression_share,
                metrics.search_rank_lost_impression_share
            FROM keyword_view
            WHERE ad_group_criterion.status != 'REMOVED'
                AND segments.date BETWEEN '{start_date.strftime("%Y-%m-%d")}' 
                AND '{end_date.strftime("%Y-%m-%d")}'
                {campaign_filter}
            ORDER BY metrics.cost_micros DESC
        """
        
        keyword_data = []
        response = ga_service.search(customer_id=customer_id_numeric, query=keyword_query)
        if api_call_counter is not None:
            api_call_counter['count'] = api_call_counter.get('count', 0) + 1
        for row in response:
            # Get conversion metrics (using correct field names)
            # Note: all_conversions_value is already in base currency (dollars), NOT micros
            conversions = row.metrics.conversions if hasattr(row.metrics, 'conversions') else 0
            conversion_value = row.metrics.all_conversions_value if hasattr(row.metrics, 'all_conversions_value') else 0
            cost = row.metrics.cost_micros / 1_000_000
            
            keyword_data.append({
                'keyword': row.ad_group_criterion.keyword.text,
                'match_type': row.ad_group_criterion.keyword.match_type.name,
                'quality_score': row.ad_group_criterion.quality_info.quality_score if hasattr(row.ad_group_criterion, 'quality_info') and row.ad_group_criterion.quality_info.quality_score else 0,
                'creative_quality': row.ad_group_criterion.quality_info.creative_quality_score.name if hasattr(row.ad_group_criterion, 'quality_info') and hasattr(row.ad_group_criterion.quality_info, 'creative_quality_score') else 'N/A',
                'post_click_quality': row.ad_group_criterion.quality_info.post_click_quality_score.name if hasattr(row.ad_group_criterion, 'quality_info') and hasattr(row.ad_group_criterion.quality_info, 'post_click_quality_score') else 'N/A',
                'expected_ctr': row.ad_group_criterion.quality_info.search_predicted_ctr.name if hasattr(row.ad_group_criterion, 'quality_info') and hasattr(row.ad_group_criterion.quality_info, 'search_predicted_ctr') else 'N/A',
                'ad_group': row.ad_group.name,
                'campaign': row.campaign.name,
                'impressions': row.metrics.impressions,
                'clicks': row.metrics.clicks,
                'ctr': row.metrics.ctr * 100 if row.metrics.ctr else 0,
                'avg_cpc': row.metrics.average_cpc / 1_000_000 if row.metrics.average_cpc else 0,
                'cost': cost,
                'conversions': conversions,
                'conversion_value': conversion_value,
                'conversion_rate': (conversions / row.metrics.clicks * 100) if row.metrics.clicks > 0 else 0,
                'cost_per_conversion': (cost / conversions) if conversions > 0 else 0,
                'impression_share': row.metrics.search_impression_share * 100 if row.metrics.search_impression_share else 0,
                'rank_lost_share': row.metrics.search_rank_lost_impression_share * 100 if row.metrics.search_rank_lost_impression_share else 0
            })
        
        # 5. Search terms (actual search queries that triggered ads)
        search_term_query = f"""
            SELECT
                search_term_view.search_term,
                ad_group.id,
                ad_group.name,
                campaign.id,
                campaign.name,
                metrics.impressions,
                metrics.clicks,
                metrics.ctr,
                metrics.cost_micros,
                metrics.average_cpc,
                metrics.conversions,
                metrics.all_conversions_value
            FROM search_term_view
            WHERE segments.date BETWEEN '{start_date.strftime("%Y-%m-%d")}' 
                AND '{end_date.strftime("%Y-%m-%d")}'
                {campaign_filter}
            ORDER BY metrics.cost_micros DESC
            LIMIT 500
        """
        
        search_terms_data = []
        try:
            response = ga_service.search(customer_id=customer_id_numeric, query=search_term_query)
            if api_call_counter is not None:
                api_call_counter['count'] = api_call_counter.get('count', 0) + 1
            for row in response:
                cost = row.metrics.cost_micros / 1_000_000
                # Note: all_conversions_value is already in base currency (dollars), NOT micros
                conversions = row.metrics.conversions if hasattr(row.metrics, 'conversions') else 0
                conversion_value = row.metrics.all_conversions_value if hasattr(row.metrics, 'all_conversions_value') else 0
                
                search_terms_data.append({
                    'search_term': row.search_term_view.search_term,
                    'ad_group_id': row.ad_group.id,
                    'ad_group_name': row.ad_group.name,
                    'campaign_id': row.campaign.id,
                    'campaign_name': row.campaign.name,
                    'impressions': row.metrics.impressions,
                    'clicks': row.metrics.clicks,
                    'ctr': row.metrics.ctr * 100 if row.metrics.ctr else 0,
                    'cost': cost,
                    'avg_cpc': row.metrics.average_cpc / 1_000_000 if row.metrics.average_cpc else 0,
                    'conversions': conversions,
                    'conversion_value': conversion_value,
                    'conversion_rate': (conversions / row.metrics.clicks * 100) if row.metrics.clicks > 0 else 0,
                    'cost_per_conversion': (cost / conversions) if conversions > 0 else 0
                })
        except Exception as e:
            # Search terms may not be available for all accounts or may require specific permissions
            pass
        
        # 6. Auction insights (competitive data)
        # Note: Auction insights are not available via Google Ads API for most account types
        # This data must be accessed through the Google Ads UI
        # Setting empty data structure for compatibility
        auction_data = []
        
        return {
            'campaigns': campaign_data,
            'ad_groups': ad_group_data,
            'ads': ad_data,
            'keywords': keyword_data,
            'search_terms': search_terms_data,
            'auction_insights': auction_data,
            'date_range': {
                'start_date': start_date.strftime("%Y-%m-%d"),
                'end_date': end_date.strftime("%Y-%m-%d"),
                'days': date_range_days
            }
        }
        
    except GoogleAdsException as ex:
        raise Exception(f"Google Ads API error: {ex.error.message()}")

def format_campaign_data_for_prompt(data):
    """Format comprehensive campaign data for Claude prompt."""
    output = []
    
    # Helper function to safely format strings that might contain curly braces (DKI syntax)
    def safe_format(template, **kwargs):
        """Format string while preserving curly braces in values (for DKI syntax like {KeyWord:...})."""
        # Replace { with {{ and } with }} in all values first
        safe_kwargs = {}
        for key, value in kwargs.items():
            if isinstance(value, str):
                # Escape curly braces in string values
                safe_kwargs[key] = value.replace('{', '{{').replace('}', '}}')
            else:
                safe_kwargs[key] = value
        # Now format the template
        return template.format(**safe_kwargs)
    
    # Campaign summary
    output.append("=== CAMPAIGN PERFORMANCE ===")
    if data['campaigns']:
        for campaign in data['campaigns']:
            # Use .format() instead of f-string to avoid issues with curly braces in data
            campaign_text = """Campaign: {campaign_name} (ID: {campaign_id})
Status: {status}
Channel Type: {channel_type}
Bidding Strategy: {bidding_strategy} {bidding_type}
Target CPA: {target_cpa}
Budget: ${budget:.2f}
Cost: ${cost:.2f}
Impressions: {impressions:,}
Clicks: {clicks:,}
CTR: {ctr:.2f}%
Avg CPC: ${avg_cpc:.2f}
Conversions: {conversions}
Conversion Rate: {conversion_rate:.2f}%
Cost per Conversion: ${cost_per_conversion:.2f}
Conversion Value: ${conversion_value:.2f}
ROAS: {roas:.2f}
Impression Share: {impression_share:.2f}%
Budget Lost Share: {budget_lost_share:.2f}%
Rank Lost Share: {rank_lost_share:.2f}%
""".format(
                campaign_name=campaign['campaign_name'],
                campaign_id=campaign['campaign_id'],
                status=campaign['status'],
                channel_type=campaign['channel_type'],
                bidding_strategy=campaign.get('bidding_strategy', 'N/A'),
                bidding_type='(Smart Bidding)' if campaign.get('is_smart_bidding', False) else '(Manual Bidding)',
                target_cpa='${:.2f}'.format(campaign.get('target_cpa')) if campaign.get('target_cpa') else 'N/A',
                budget=campaign['budget'],
                cost=campaign['cost'],
                impressions=campaign['impressions'],
                clicks=campaign['clicks'],
                ctr=campaign['ctr'],
                avg_cpc=campaign['avg_cpc'],
                conversions=campaign['conversions'],
                conversion_rate=campaign['conversion_rate'],
                cost_per_conversion=campaign['cost_per_conversion'],
                conversion_value=campaign['conversion_value'],
                roas=campaign['roas'],
                impression_share=campaign['impression_share'],
                budget_lost_share=campaign['budget_lost_share'],
                rank_lost_share=campaign['rank_lost_share']
            )
            output.append(campaign_text)
    else:
        output.append("No campaign data available.")
    
    # Ad Groups - Sort by cost for better analysis
    output.append("\n=== AD GROUP PERFORMANCE ===")
    if data['ad_groups']:
        df_adgroups = pd.DataFrame(data['ad_groups'])
        # Sort by cost descending to show highest spenders first
        df_adgroups = df_adgroups.sort_values('cost', ascending=False)
        output.append("Total Ad Groups: {}\n".format(len(df_adgroups)))
        output.append(df_adgroups.to_string(index=False))
        # Add summary statistics
        if len(df_adgroups) > 0:
            output.append("\nAd Group Summary:")
            output.append("  Average CTR: {:.2f}%".format(df_adgroups['ctr'].mean()))
            output.append("  Average CPC: ${:.2f}".format(df_adgroups['avg_cpc'].mean()))
            output.append("  Average Conversion Rate: {:.2f}%".format(df_adgroups['conversion_rate'].mean()))
            output.append("  Average Cost per Conversion: ${:.2f}".format(df_adgroups['cost_per_conversion'].mean()))
    else:
        output.append("No ad group data available.")
    
    # Keywords - Sort by cost for better analysis
    output.append("\n=== KEYWORD PERFORMANCE ===")
    if data['keywords']:
        df_keywords = pd.DataFrame(data['keywords'])
        # Sort by cost descending to show highest spenders first
        df_keywords = df_keywords.sort_values('cost', ascending=False)
        # Show all keywords, but note if there are many
        if len(df_keywords) > 200:
            output.append("(Showing top 200 of {} keywords by cost)\n".format(len(df_keywords)))
            df_keywords = df_keywords.head(200)
        else:
            output.append("Total Keywords: {}\n".format(len(df_keywords)))
        output.append(df_keywords.to_string(index=False))
        # Add summary statistics
        if len(df_keywords) > 0:
            output.append("\nKeyword Summary:")
            output.append("  Average Quality Score: {:.1f}".format(df_keywords[df_keywords['quality_score'] > 0]['quality_score'].mean()))
            output.append("  Average CTR: {:.2f}%".format(df_keywords['ctr'].mean()))
            output.append("  Average CPC: ${:.2f}".format(df_keywords['avg_cpc'].mean()))
            output.append("  Average Conversion Rate: {:.2f}%".format(df_keywords['conversion_rate'].mean()))
            output.append("  Keywords with 0 conversions: {}".format(len(df_keywords[df_keywords['conversions'] == 0])))
            output.append("  Keywords with Quality Score < 7: {}".format(len(df_keywords[(df_keywords['quality_score'] > 0) & (df_keywords['quality_score'] < 7)])))
    else:
        output.append("No keyword data available.")
    
    # Ads - Sort by cost for better analysis
    output.append("\n=== AD PERFORMANCE ===")
    if data['ads']:
        # Format ads with ALL headlines and descriptions clearly listed
        df_ads = pd.DataFrame(data['ads'])
        # Sort by cost descending to show highest spenders first
        df_ads = df_ads.sort_values('cost', ascending=False)
        if len(df_ads) > 100:
            output.append("(Showing top 100 of {} ads by cost)\n".format(len(df_ads)))
            df_ads = df_ads.head(100)
        else:
            output.append("Total Ads: {}\n".format(len(df_ads)))
        
        # Format each ad with all headlines and descriptions clearly listed
        for idx, ad in df_ads.iterrows():
            output.append("\n--- Ad ID: {} ---".format(ad['ad_id']))
            output.append("Ad Group: {} | Campaign: {}".format(ad['ad_group'], ad['campaign']))
            output.append("Status: {} | Type: {}".format(ad['status'], ad['ad_type']))
            output.append("Performance: ${:.2f} cost | {:,} impressions | {:,} clicks | {:.2f}% CTR".format(
                ad['cost'], ad['impressions'], ad['clicks'], ad['ctr']))
            
            # List ALL headlines with character counts
            if 'headlines_list' in ad and isinstance(ad['headlines_list'], list):
                output.append("\nHeadlines ({} total):".format(len(ad['headlines_list'])))
                for i, headline in enumerate(ad['headlines_list'], 1):
                    char_count = len(headline)
                    output.append("  H{}: \"{}\" [{}/30]".format(i, headline, char_count))
            elif 'headlines' in ad:
                # Fallback if list not available, parse from joined string
                headlines = [h.strip() for h in str(ad['headlines']).split('|')]
                output.append("\nHeadlines ({} total):".format(len(headlines)))
                for i, headline in enumerate(headlines, 1):
                    char_count = len(headline)
                    output.append("  H{}: \"{}\" [{}/30]".format(i, headline, char_count))
            
            # List ALL descriptions with character counts
            if 'descriptions_list' in ad and isinstance(ad['descriptions_list'], list):
                output.append("\nDescriptions ({} total):".format(len(ad['descriptions_list'])))
                for i, desc in enumerate(ad['descriptions_list'], 1):
                    char_count = len(desc)
                    output.append("  D{}: \"{}\" [{}/90]".format(i, desc, char_count))
            elif 'descriptions' in ad:
                # Fallback if list not available, parse from joined string
                descriptions = [d.strip() for d in str(ad['descriptions']).split('|')]
                output.append("\nDescriptions ({} total):".format(len(descriptions)))
                for i, desc in enumerate(descriptions, 1):
                    char_count = len(desc)
                    output.append("  D{}: \"{}\" [{}/90]".format(i, desc, char_count))
            output.append("")  # Empty line between ads
        
        # Add summary statistics
        if len(df_ads) > 0:
            output.append("\nAd Summary:")
            output.append("  Average CTR: {:.2f}%".format(df_ads['ctr'].mean()))
            output.append("  Average Cost: ${:.2f}".format(df_ads['cost'].mean()))
    else:
        output.append("No ad data available.")
    
    # Search Terms (actual queries that triggered ads)
    output.append("\n=== SEARCH TERMS PERFORMANCE ===")
    if data.get('search_terms'):
        df_search_terms = pd.DataFrame(data['search_terms'])
        # Show top performing and underperforming search terms
        if len(df_search_terms) > 100:
            output.append("(Showing top 100 of {} search terms)\n".format(len(data['search_terms'])))
            df_search_terms = df_search_terms.head(100)
        output.append(df_search_terms.to_string(index=False))
    else:
        output.append("No search terms data available. This may require additional API permissions.")
    
    # Auction Insights
    output.append("\n=== AUCTION INSIGHTS (COMPETITIVE DATA) ===")
    if data['auction_insights']:
        df_auction = pd.DataFrame(data['auction_insights'])
        output.append(df_auction.to_string(index=False))
    else:
        output.append("No auction insights data available via API. Access this data through Google Ads UI.")
    
    return "\n".join(output)

