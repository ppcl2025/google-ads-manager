"""
Keyword Planner Data Fetcher

Fetches keyword competition, search volume, and suggested bid data from Google Ads Keyword Planner API.
"""

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from datetime import datetime
import os


def fetch_keyword_planner_data(client, customer_id, keywords_list, geo_targets=None, language_code="en"):
    """
    Fetch Keyword Planner data for given keywords.
    
    Args:
        client: Google Ads API client
        customer_id: Customer account ID (format: 123-456-7890)
        keywords_list: List of keyword texts to analyze
        geo_targets: Optional list of geo target constant resource names
        language_code: Language code (default: "en" for English)
    
    Returns:
        Dictionary with keyword planner data
    """
    customer_id_numeric = customer_id.replace("-", "")
    
    try:
        keyword_plan_idea_service = client.get_service("KeywordPlanIdeaService")
        
        # Build keyword seed
        keyword_seed = client.get_type("KeywordSeed")
        keyword_seed.keywords = keywords_list
        
        # Build request
        request = client.get_type("GenerateKeywordIdeasRequest")
        request.customer_id = customer_id_numeric
        request.keyword_seed = keyword_seed
        
        # Set language code if the field exists (API version dependent)
        try:
            if hasattr(request, 'language_code'):
                request.language_code = language_code
            elif hasattr(request, 'language'):
                request.language = language_code
            # If neither field exists, language defaults to account/campaign settings
        except (AttributeError, ValueError) as lang_error:
            # Language code is optional - continue without it
            pass
        
        # Handle geo target constants if provided
        # Note: Geo targeting in Keyword Planner API v22+ may have different requirements
        # We'll make it optional and handle errors gracefully
        if geo_targets:
            try:
                # Try to set geo targets using the available method for this API version
                # In some API versions, geo targets might not be directly supported in Keyword Planner
                # or may require different handling
                
                # First, try to see what fields are available on the request
                if hasattr(request, 'geo_target_constants'):
                    # Try to create geo target constant objects if the type exists
                    try:
                        geo_target_constant_type = client.get_type("KeywordPlanGeoTargetConstant")
                        geo_target_constants_list = []
                        for geo_target in geo_targets:
                            if not geo_target.startswith("geoTargetConstants/"):
                                if geo_target.isdigit():
                                    geo_target = f"geoTargetConstants/{geo_target}"
                                else:
                                    continue  # Skip invalid formats
                            geo_target_obj = geo_target_constant_type()
                            geo_target_obj.geo_target_constant = geo_target
                            geo_target_constants_list.append(geo_target_obj)
                        if geo_target_constants_list:
                            request.geo_target_constants = geo_target_constants_list
                    except (ValueError, AttributeError):
                        # Type doesn't exist in this API version - skip geo targeting
                        # This is acceptable as geo targeting is optional
                        pass
            except Exception as geo_error:
                # Geo targeting is optional - continue without it
                # This allows keyword research to work even if geo targeting fails
                pass
        
        # Get KeywordPlanNetwork enum from client (using client.enums instead of version-specific import)
        request.keyword_plan_network = client.enums.KeywordPlanNetworkEnum.KeywordPlanNetwork.GOOGLE_SEARCH
        
        # Make API call
        response = keyword_plan_idea_service.generate_keyword_ideas(request=request)
        
        # Parse results
        keyword_data = []
        related_keywords = []
        
        for result in response.results:
            keyword_metrics = result.keyword_idea_metrics
            
            keyword_info = {
                'keyword_text': result.text,
                'avg_monthly_searches': keyword_metrics.avg_monthly_searches if keyword_metrics.avg_monthly_searches else 0,
                'competition': _map_competition_index(keyword_metrics.competition_index) if keyword_metrics.competition_index else 'UNKNOWN',
                'competition_index': keyword_metrics.competition_index if keyword_metrics.competition_index else None,
                'low_top_of_page_bid_micros': keyword_metrics.low_top_of_page_bid_micros.value if keyword_metrics.low_top_of_page_bid_micros else None,
                'high_top_of_page_bid_micros': keyword_metrics.high_top_of_page_bid_micros.value if keyword_metrics.high_top_of_page_bid_micros else None,
                'low_top_of_page_bid': (keyword_metrics.low_top_of_page_bid_micros.value / 1_000_000) if keyword_metrics.low_top_of_page_bid_micros else None,
                'high_top_of_page_bid': (keyword_metrics.high_top_of_page_bid_micros.value / 1_000_000) if keyword_metrics.high_top_of_page_bid_micros else None,
            }
            
            # Check if this is one of the original keywords or a related keyword
            if result.text.lower() in [kw.lower() for kw in keywords_list]:
                keyword_data.append(keyword_info)
            else:
                related_keywords.append(keyword_info)
        
        return {
            'keywords': keyword_data,
            'related_keywords': related_keywords[:20]
        }
        
    except GoogleAdsException as ex:
        error_message = ""
        for error in ex.failure.errors:
            error_message += f"{error.error_code.error_code}: {error.message}\n"
        raise Exception(f"Google Ads API error fetching Keyword Planner data: {error_message}")
    except Exception as e:
        raise Exception(f"Error fetching Keyword Planner data: {str(e)}")


def _map_competition_index(competition_index):
    """Map competition index (0-100) to LOW/MEDIUM/HIGH."""
    if competition_index is None:
        return 'UNKNOWN'
    if competition_index <= 33:
        return 'LOW'
    elif competition_index <= 66:
        return 'MEDIUM'
    else:
        return 'HIGH'


def get_geo_target_for_campaign(client, customer_id, campaign_id):
    """Get geo target constants for a campaign's location targeting."""
    customer_id_numeric = customer_id.replace("-", "")
    
    try:
        ga_service = client.get_service("GoogleAdsService")
        query = f"""
            SELECT
                campaign_criterion.location.geo_target_constant
            FROM campaign_criterion
            WHERE campaign.id = {campaign_id}
                AND campaign_criterion.type = 'LOCATION'
                AND campaign_criterion.location.geo_target_constant IS NOT NULL
        """
        
        geo_targets = []
        response = ga_service.search(customer_id=customer_id_numeric, query=query)
        
        for row in response:
            if hasattr(row.campaign_criterion, 'location') and row.campaign_criterion.location.geo_target_constant:
                geo_target = row.campaign_criterion.location.geo_target_constant
                geo_targets.append(geo_target)
        
        return geo_targets if geo_targets else None
    except Exception as e:
        return None


def fetch_campaign_keywords(client, customer_id, campaign_id):
    """
    Fetch all keywords from a specific campaign.
    
    Args:
        client: Google Ads API client
        customer_id: Customer account ID (format: 123-456-7890)
        campaign_id: Campaign ID to fetch keywords from
    
    Returns:
        List of keyword text strings (unique, no duplicates)
    """
    customer_id_numeric = customer_id.replace("-", "")
    
    try:
        ga_service = client.get_service("GoogleAdsService")
        query = f"""
            SELECT
                ad_group_criterion.keyword.text,
                ad_group_criterion.keyword.match_type
            FROM keyword_view
            WHERE campaign.id = {campaign_id}
                AND ad_group_criterion.status != 'REMOVED'
        """
        
        keywords_set = set()  # Use set to avoid duplicates
        response = ga_service.search(customer_id=customer_id_numeric, query=query)
        
        for row in response:
            if hasattr(row.ad_group_criterion, 'keyword') and row.ad_group_criterion.keyword.text:
                keyword_text = row.ad_group_criterion.keyword.text.strip()
                if keyword_text:
                    keywords_set.add(keyword_text)
        
        return sorted(list(keywords_set))  # Return sorted list
    except GoogleAdsException as ex:
        error_message = ""
        for error in ex.failure.errors:
            error_message += f"{error.error_code.error_code}: {error.message}\n"
        raise Exception(f"Google Ads API error fetching campaign keywords: {error_message}")
    except Exception as e:
        raise Exception(f"Error fetching campaign keywords: {str(e)}")


def format_keyword_planner_for_prompt(planner_data, current_keyword_performance=None):
    """Format Keyword Planner data for Claude prompt."""
    output = []
    output.append("=== KEYWORD PLANNER DATA ===\n")
    
    if planner_data.get('keywords'):
        output.append("**Current Keywords - Competition & Market Data:**\n")
        for kw in planner_data['keywords']:
            line = f"- \"{kw['keyword_text']}\""
            if kw.get('avg_monthly_searches'):
                line += f" | {kw['avg_monthly_searches']:,} searches/month"
            if kw.get('competition'):
                line += f" | Competition: {kw['competition']}"
            if kw.get('low_top_of_page_bid') and kw.get('high_top_of_page_bid'):
                line += f" | Suggested Bid: ${kw['low_top_of_page_bid']:.2f}-${kw['high_top_of_page_bid']:.2f}"
            
            if current_keyword_performance and kw['keyword_text'] in current_keyword_performance:
                perf = current_keyword_performance[kw['keyword_text']]
                line += f" | Your CPC: ${perf.get('avg_cpc', 0):.2f}"
                if perf.get('avg_cpc') and kw.get('high_top_of_page_bid'):
                    if perf['avg_cpc'] > kw['high_top_of_page_bid'] * 1.5:
                        line += " ⚠️ (2x+ over market - Quality Score issue)"
            
            output.append(line)
    
    if planner_data.get('related_keywords'):
        output.append("\n**Related Keyword Opportunities:**\n")
        for kw in planner_data['related_keywords'][:15]:
            line = f"- \"{kw['keyword_text']}\""
            if kw.get('avg_monthly_searches'):
                line += f" | {kw['avg_monthly_searches']:,} searches/month"
            if kw.get('competition'):
                line += f" | Competition: {kw['competition']}"
            if kw.get('low_top_of_page_bid') and kw.get('high_top_of_page_bid'):
                line += f" | Suggested Bid: ${kw['low_top_of_page_bid']:.2f}-${kw['high_top_of_page_bid']:.2f}"
            output.append(line)
    
    return "\n".join(output)
