"""
Keyword Planner Data Fetcher

Fetches keyword competition, search volume, and suggested bid data from Google Ads Keyword Planner API.
"""

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()


def fetch_keyword_planner_data(client, customer_id, keywords_list, geo_targets=None, language_code='en'):
    """
    Fetch Keyword Planner data for a list of keywords.
    
    Args:
        client: Google Ads API client
        customer_id: Customer account ID (format: 123-456-7890)
        keywords_list: List of keyword text strings to analyze
        geo_targets: Optional list of geo target constant resource names (e.g., ['geoTargetConstants/2840'] for US)
        language_code: Language code (default: 'en' for English)
    
    Returns:
        Dictionary with keyword planner data including:
        - competition: LOW, MEDIUM, or HIGH
        - avg_monthly_searches: Average monthly search volume
        - low_top_of_page_bid: Low end of suggested bid range
        - high_top_of_page_bid: High end of suggested bid range
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
        request.language_constant = f"languageConstants/{language_code}"
        
        # Add geo targeting if provided
        if geo_targets:
            request.geo_target_constants = geo_targets
        
        # Execute request
        response = keyword_plan_idea_service.generate_keyword_ideas(request=request)
        
        # Parse results
        keyword_data = {}
        for result in response.results:
            keyword_text = result.text
            
            # Get competition level
            competition = "UNKNOWN"
            if result.keyword_idea_metrics:
                competition_enum = result.keyword_idea_metrics.competition
                if competition_enum:
                    competition = competition_enum.name  # LOW, MEDIUM, HIGH
            
            # Get search volume
            avg_monthly_searches = 0
            if result.keyword_idea_metrics:
                avg_monthly_searches = result.keyword_idea_metrics.avg_monthly_searches or 0
            
            # Get suggested bid range
            low_bid = None
            high_bid = None
            if result.keyword_idea_metrics:
                if result.keyword_idea_metrics.low_top_of_page_bid_micros:
                    low_bid = result.keyword_idea_metrics.low_top_of_page_bid_micros / 1_000_000
                if result.keyword_idea_metrics.high_top_of_page_bid_micros:
                    high_bid = result.keyword_idea_metrics.high_top_of_page_bid_micros / 1_000_000
            
            keyword_data[keyword_text] = {
                'keyword_text': keyword_text,
                'competition': competition,
                'avg_monthly_searches': avg_monthly_searches,
                'low_top_of_page_bid': low_bid,
                'high_top_of_page_bid': high_bid,
                'suggested_bid_range': f"${low_bid:.2f}-${high_bid:.2f}" if low_bid and high_bid else "N/A"
            }
        
        return keyword_data
        
    except GoogleAdsException as ex:
        error_msg = ""
        for error in ex.failure.errors:
            error_msg += f"{error.error_code.error_code}: {error.message}\n"
        raise Exception(f"Google Ads API error fetching Keyword Planner data: {error_msg}")
    except Exception as e:
        raise Exception(f"Error fetching Keyword Planner data: {str(e)}")


def get_geo_target_constants(client, location_names):
    """
    Get geo target constant resource names from location names.
    
    Args:
        client: Google Ads API client
        location_names: List of location names (e.g., ['United States', 'New York', 'Cleveland'])
    
    Returns:
        List of geo target constant resource names (e.g., ['geoTargetConstants/2840'])
    """
    try:
        geo_target_constant_service = client.get_service("GeoTargetConstantService")
        geo_targets = []
        
        for location_name in location_names:
            # Build suggestion request
            request = client.get_type("SuggestGeoTargetConstantsRequest")
            request.locale = "en"
            request.country_code = "US"  # Default to US, can be made configurable
            request.location_names.names = [location_name]
            
            try:
                response = geo_target_constant_service.suggest_geoTarget_constants(request=request)
                if response.geoTargetConstant_suggestions:
                    # Get the first (most relevant) suggestion
                    geo_target = response.geoTargetConstant_suggestions[0].geoTargetConstant.resource_name
                    geo_targets.append(geo_target)
            except Exception as e:
                # If location not found, skip it
                print(f"Warning: Could not find geo target for '{location_name}': {e}")
                continue
        
        return geo_targets
        
    except Exception as e:
        print(f"Warning: Error getting geo targets: {e}")
        return []


def format_keyword_planner_for_prompt(keyword_planner_data, current_keyword_performance=None):
    """
    Format Keyword Planner data for inclusion in Claude prompt.
    
    Args:
        keyword_planner_data: Dictionary from fetch_keyword_planner_data
        current_keyword_performance: Optional dict with current keyword performance metrics
    
    Returns:
        Formatted string for prompt
    """
    if not keyword_planner_data:
        return ""
    
    lines = []
    lines.append("=== KEYWORD PLANNER DATA (Competition & Market Intelligence) ===")
    lines.append("")
    lines.append("This data shows search volume, competition level, and suggested bid ranges for keywords.")
    lines.append("Use this to identify:")
    lines.append("- Keywords that are too competitive for your budget/ROI")
    lines.append("- Quality Score problems (when your CPC >> suggested bid)")
    lines.append("- Low-competition opportunities to expand into")
    lines.append("- Realistic volume expectations for niche keywords")
    lines.append("")
    lines.append("KEYWORD PLANNER METRICS:")
    lines.append("")
    
    # Create table format
    lines.append("Keyword | Monthly Searches | Competition | Suggested Bid Range")
    lines.append("-" * 80)
    
    for keyword_text, data in keyword_planner_data.items():
        keyword = data.get('keyword_text', keyword_text)
        searches = data.get('avg_monthly_searches', 0)
        competition = data.get('competition', 'UNKNOWN')
        bid_range = data.get('suggested_bid_range', 'N/A')
        
        # Add current performance if available
        current_info = ""
        if current_keyword_performance and keyword_text in current_keyword_performance:
            perf = current_keyword_performance[keyword_text]
            current_cpc = perf.get('avg_cpc', 0)
            current_cpa = perf.get('cost_per_conversion', 0)
            conversions = perf.get('conversions', 0)
            current_info = f" | Current: ${current_cpc:.2f} CPC, ${current_cpa:.2f} CPA, {conversions} conv"
        
        lines.append(f"{keyword} | {searches:,} | {competition} | {bid_range}{current_info}")
    
    lines.append("")
    lines.append("=== END KEYWORD PLANNER DATA ===")
    lines.append("")
    
    return "\n".join(lines)


def get_related_keyword_suggestions(client, customer_id, seed_keywords, geo_targets=None, language_code='en'):
    """
    Get related keyword suggestions from Keyword Planner.
    
    Args:
        client: Google Ads API client
        customer_id: Customer account ID
        seed_keywords: List of seed keywords to generate suggestions from
        geo_targets: Optional list of geo target constants
        language_code: Language code (default: 'en')
    
    Returns:
        List of suggested keywords with planner data
    """
    customer_id_numeric = customer_id.replace("-", "")
    
    try:
        keyword_plan_idea_service = client.get_service("KeywordPlanIdeaService")
        
        # Build keyword seed
        keyword_seed = client.get_type("KeywordSeed")
        keyword_seed.keywords = seed_keywords
        
        # Build request
        request = client.get_type("GenerateKeywordIdeasRequest")
        request.customer_id = customer_id_numeric
        request.keyword_seed = keyword_seed
        request.language_constant = f"languageConstants/{language_code}"
        
        if geo_targets:
            request.geo_target_constants = geo_targets
        
        # Execute request
        response = keyword_plan_idea_service.generate_keyword_ideas(request=request)
        
        # Parse and return suggestions
        suggestions = []
        for result in response.results:
            keyword_text = result.text
            
            # Skip if it's one of the seed keywords
            if keyword_text.lower() in [k.lower() for k in seed_keywords]:
                continue
            
            competition = "UNKNOWN"
            avg_monthly_searches = 0
            low_bid = None
            high_bid = None
            
            if result.keyword_idea_metrics:
                if result.keyword_idea_metrics.competition:
                    competition = result.keyword_idea_metrics.competition.name
                avg_monthly_searches = result.keyword_idea_metrics.avg_monthly_searches or 0
                if result.keyword_idea_metrics.low_top_of_page_bid_micros:
                    low_bid = result.keyword_idea_metrics.low_top_of_page_bid_micros / 1_000_000
                if result.keyword_idea_metrics.high_top_of_page_bid_micros:
                    high_bid = result.keyword_idea_metrics.high_top_of_page_bid_micros / 1_000_000
            
            suggestions.append({
                'keyword_text': keyword_text,
                'competition': competition,
                'avg_monthly_searches': avg_monthly_searches,
                'low_top_of_page_bid': low_bid,
                'high_top_of_page_bid': high_bid,
                'suggested_bid_range': f"${low_bid:.2f}-${high_bid:.2f}" if low_bid and high_bid else "N/A"
            })
        
        # Sort by search volume (descending)
        suggestions.sort(key=lambda x: x['avg_monthly_searches'], reverse=True)
        
        return suggestions
        
    except GoogleAdsException as ex:
        error_msg = ""
        for error in ex.failure.errors:
            error_msg += f"{error.error_code.error_code}: {error.message}\n"
        raise Exception(f"Google Ads API error fetching keyword suggestions: {error_msg}")
    except Exception as e:
        raise Exception(f"Error fetching keyword suggestions: {str(e)}")

