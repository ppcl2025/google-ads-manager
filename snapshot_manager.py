"""
Snapshot Manager for Campaign Change Detection

This module handles saving and comparing campaign snapshots to automatically
detect changes made between analysis reports.
"""

import os
import json
from datetime import datetime
from pathlib import Path


SNAPSHOT_DIR = "snapshots"


def ensure_snapshot_dir():
    """Ensure the snapshot directory exists."""
    Path(SNAPSHOT_DIR).mkdir(exist_ok=True)
    # Add .gitkeep to ensure directory is tracked in git
    gitkeep_path = os.path.join(SNAPSHOT_DIR, ".gitkeep")
    if not os.path.exists(gitkeep_path):
        with open(gitkeep_path, 'w') as f:
            f.write("# Snapshot directory for change detection\n")


def get_snapshot_path(account_id, campaign_id=None, account_name=None, campaign_name=None):
    """
    Get the file path for a snapshot.
    
    Args:
        account_id: Account ID (e.g., "9660434837")
        campaign_id: Optional campaign ID (e.g., "22557679902")
        account_name: Optional account name for filename
        campaign_name: Optional campaign name for filename
    
    Returns:
        Path to snapshot file
    """
    ensure_snapshot_dir()
    
    # Create a safe filename
    if account_name and campaign_name:
        safe_account = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in account_name).strip()
        safe_campaign = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in campaign_name).strip()
        filename = f"{safe_account}_{safe_campaign}.json"
    elif account_name:
        safe_account = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in account_name).strip()
        filename = f"{safe_account}.json"
    else:
        # Fallback to IDs
        if campaign_id:
            filename = f"{account_id}_{campaign_id}.json"
        else:
            filename = f"{account_id}.json"
    
    # Replace spaces with underscores and limit length
    filename = filename.replace(' ', '_')
    if len(filename) > 200:  # Limit filename length
        filename = filename[:200] + ".json"
    
    return os.path.join(SNAPSHOT_DIR, filename)


def save_snapshot(account_id, campaign_id=None, account_name=None, campaign_name=None, campaign_data=None):
    """
    Save a snapshot of campaign state.
    
    Args:
        account_id: Account ID
        campaign_id: Optional campaign ID
        account_name: Optional account name
        campaign_name: Optional campaign name
        campaign_data: Dictionary containing campaign data from comprehensive_data_fetcher
    
    Returns:
        Path to saved snapshot, or None if failed
    """
    ensure_snapshot_dir()
    snapshot_path = get_snapshot_path(account_id, campaign_id, account_name, campaign_name)
    
    if not campaign_data:
        return None
    
    # Extract key settings for snapshot
    snapshot = {
        'timestamp': datetime.now().isoformat(),
        'account_id': account_id,
        'campaign_id': campaign_id,
        'account_name': account_name,
        'campaign_name': campaign_name,
        'campaigns': [],
        'ad_groups': [],
        'keywords': []
    }
    
    # Extract campaign settings
    if 'campaigns' in campaign_data:
        for campaign in campaign_data['campaigns']:
            campaign_snapshot = {
                'campaign_id': campaign.get('campaign_id'),
                'campaign_name': campaign.get('campaign_name'),
                'status': campaign.get('status'),
                'budget': campaign.get('budget'),
                'bidding_strategy': campaign.get('bidding_strategy'),
                'bidding_strategy_type': campaign.get('bidding_strategy_type'),
                'is_smart_bidding': campaign.get('is_smart_bidding', False),
                'target_cpa': campaign.get('target_cpa'),
                'target_roas': campaign.get('target_roas'),
                'channel_type': campaign.get('channel_type'),
                'start_date': campaign.get('start_date'),
                'end_date': campaign.get('end_date')
            }
            snapshot['campaigns'].append(campaign_snapshot)
    
    # Extract ad group settings
    if 'ad_groups' in campaign_data:
        for ad_group in campaign_data['ad_groups']:
            ad_group_snapshot = {
                'ad_group_id': ad_group.get('ad_group_id'),
                'ad_group_name': ad_group.get('ad_group_name'),
                'campaign_id': ad_group.get('campaign_id'),
                'status': ad_group.get('status'),
                'cpc_bid': ad_group.get('cpc_bid')
            }
            snapshot['ad_groups'].append(ad_group_snapshot)
    
    # Extract keyword settings
    if 'keywords' in campaign_data:
        for keyword in campaign_data['keywords']:
            keyword_snapshot = {
                'keyword_id': keyword.get('keyword_id'),
                'keyword_text': keyword.get('keyword_text'),
                'ad_group_id': keyword.get('ad_group_id'),
                'campaign_id': keyword.get('campaign_id'),
                'match_type': keyword.get('match_type'),
                'status': keyword.get('status'),
                'cpc_bid': keyword.get('cpc_bid'),
                'quality_score': keyword.get('quality_score')
            }
            snapshot['keywords'].append(keyword_snapshot)
    
    # Save to file
    try:
        with open(snapshot_path, 'w', encoding='utf-8') as f:
            json.dump(snapshot, f, indent=2, ensure_ascii=False)
        return snapshot_path
    except Exception as e:
        print(f"Error saving snapshot: {e}")
        return None


def load_snapshot(account_id, campaign_id=None, account_name=None, campaign_name=None):
    """
    Load the most recent snapshot for an account/campaign.
    
    Returns:
        Snapshot dictionary, or None if not found
    """
    snapshot_path = get_snapshot_path(account_id, campaign_id, account_name, campaign_name)
    
    if os.path.exists(snapshot_path):
        try:
            with open(snapshot_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading snapshot: {e}")
            return None
    return None


def compare_snapshots(old_snapshot, current_data):
    """
    Compare old snapshot with current campaign data to detect changes.
    
    Args:
        old_snapshot: Previous snapshot dictionary
        current_data: Current campaign data from comprehensive_data_fetcher
    
    Returns:
        Dictionary of detected changes
    """
    changes = {
        'budget_changes': [],
        'status_changes': [],
        'keyword_changes': [],
        'ad_group_changes': [],
        'bidding_strategy_changes': [],
        'new_keywords': [],
        'removed_keywords': [],
        'timestamp': datetime.now().isoformat()
    }
    
    if not old_snapshot:
        return changes
    
    # Compare campaigns
    old_campaigns = {c['campaign_id']: c for c in old_snapshot.get('campaigns', [])}
    current_campaigns = {c['campaign_id']: c for c in current_data.get('campaigns', [])}
    
    for campaign_id, old_campaign in old_campaigns.items():
        if campaign_id in current_campaigns:
            current_campaign = current_campaigns[campaign_id]
            
            # Budget changes
            old_budget = old_campaign.get('budget', 0)
            current_budget = current_campaign.get('budget', 0)
            if abs(old_budget - current_budget) > 0.01:  # Allow for floating point differences
                changes['budget_changes'].append({
                    'campaign_id': campaign_id,
                    'campaign_name': old_campaign.get('campaign_name'),
                    'old_budget': old_budget,
                    'new_budget': current_budget,
                    'change': current_budget - old_budget
                })
            
            # Status changes
            if old_campaign.get('status') != current_campaign.get('status'):
                changes['status_changes'].append({
                    'campaign_id': campaign_id,
                    'campaign_name': old_campaign.get('campaign_name'),
                    'old_status': old_campaign.get('status'),
                    'new_status': current_campaign.get('status')
                })
            
            # Bidding strategy changes
            old_bidding = old_campaign.get('bidding_strategy')
            current_bidding = current_campaign.get('bidding_strategy')
            if old_bidding != current_bidding:
                changes['bidding_strategy_changes'].append({
                    'campaign_id': campaign_id,
                    'campaign_name': old_campaign.get('campaign_name'),
                    'old_strategy': old_bidding,
                    'new_strategy': current_bidding,
                    'old_target_cpa': old_campaign.get('target_cpa'),
                    'new_target_cpa': current_campaign.get('target_cpa'),
                    'old_target_roas': old_campaign.get('target_roas'),
                    'new_target_roas': current_campaign.get('target_roas')
                })
    
    # Compare keywords
    old_keywords = {}
    for kw in old_snapshot.get('keywords', []):
        key = (kw.get('keyword_id'), kw.get('ad_group_id'))
        old_keywords[key] = kw
    
    current_keywords = {}
    for kw in current_data.get('keywords', []):
        key = (kw.get('keyword_id'), kw.get('ad_group_id'))
        current_keywords[key] = kw
    
    # Find status changes, bid changes, and removed keywords
    for key, old_kw in old_keywords.items():
        if key in current_keywords:
            current_kw = current_keywords[key]
            
            # Status changes
            if old_kw.get('status') != current_kw.get('status'):
                changes['keyword_changes'].append({
                    'keyword_id': old_kw.get('keyword_id'),
                    'keyword_text': old_kw.get('keyword_text'),
                    'ad_group_id': old_kw.get('ad_group_id'),
                    'old_status': old_kw.get('status'),
                    'new_status': current_kw.get('status'),
                    'match_type': old_kw.get('match_type')
                })
            
            # Bid changes (if significant)
            old_bid = old_kw.get('cpc_bid', 0)
            current_bid = current_kw.get('cpc_bid', 0)
            if old_bid and current_bid and abs(old_bid - current_bid) > 0.01:
                changes['keyword_changes'].append({
                    'keyword_id': old_kw.get('keyword_id'),
                    'keyword_text': old_kw.get('keyword_text'),
                    'ad_group_id': old_kw.get('ad_group_id'),
                    'old_bid': old_bid,
                    'new_bid': current_bid,
                    'change': current_bid - old_bid,
                    'match_type': old_kw.get('match_type')
                })
        else:
            # Keyword removed
            changes['removed_keywords'].append({
                'keyword_id': old_kw.get('keyword_id'),
                'keyword_text': old_kw.get('keyword_text'),
                'ad_group_id': old_kw.get('ad_group_id'),
                'match_type': old_kw.get('match_type')
            })
    
    # Find new keywords
    for key, current_kw in current_keywords.items():
        if key not in old_keywords:
            changes['new_keywords'].append({
                'keyword_id': current_kw.get('keyword_id'),
                'keyword_text': current_kw.get('keyword_text'),
                'ad_group_id': current_kw.get('ad_group_id'),
                'status': current_kw.get('status'),
                'match_type': current_kw.get('match_type'),
                'cpc_bid': current_kw.get('cpc_bid')
            })
    
    # Compare ad groups
    old_ad_groups = {ag['ad_group_id']: ag for ag in old_snapshot.get('ad_groups', [])}
    current_ad_groups = {ag['ad_group_id']: ag for ag in current_data.get('ad_groups', [])}
    
    for ag_id, old_ag in old_ad_groups.items():
        if ag_id in current_ad_groups:
            current_ag = current_ad_groups[ag_id]
            
            # Status changes
            if old_ag.get('status') != current_ag.get('status'):
                changes['ad_group_changes'].append({
                    'ad_group_id': ag_id,
                    'ad_group_name': old_ag.get('ad_group_name'),
                    'old_status': old_ag.get('status'),
                    'new_status': current_ag.get('status')
                })
    
    return changes


def format_changes_for_changelog(changes):
    """
    Format detected changes into changelog entry text.
    
    Args:
        changes: Dictionary of changes from compare_snapshots
    
    Returns:
        Formatted text string for changelog
    """
    lines = []
    
    if changes['budget_changes']:
        lines.append("Budget Changes:")
        for change in changes['budget_changes']:
            lines.append(f"  • {change['campaign_name']}: ${change['old_budget']:.2f}/day → ${change['new_budget']:.2f}/day (${change['change']:+.2f})")
    
    if changes['bidding_strategy_changes']:
        lines.append("Bidding Strategy Changes:")
        for change in changes['bidding_strategy_changes']:
            strategy_text = f"{change['old_strategy']} → {change['new_strategy']}"
            if change.get('new_target_cpa'):
                strategy_text += f" (Target CPA: ${change['new_target_cpa']:.2f})"
            if change.get('new_target_roas'):
                strategy_text += f" (Target ROAS: {change['new_target_roas']:.2f})"
            lines.append(f"  • {change['campaign_name']}: {strategy_text}")
    
    if changes['status_changes']:
        lines.append("Campaign Status Changes:")
        for change in changes['status_changes']:
            lines.append(f"  • {change['campaign_name']}: {change['old_status']} → {change['new_status']}")
    
    paused_keywords = [kw for kw in changes['keyword_changes'] if kw.get('new_status') == 'PAUSED']
    enabled_keywords = [kw for kw in changes['keyword_changes'] if kw.get('new_status') == 'ENABLED']
    
    if paused_keywords:
        lines.append(f"Keywords Paused ({len(paused_keywords)}):")
        for kw in paused_keywords[:10]:  # Limit to 10 for readability
            lines.append(f"  • {kw['keyword_text']} ({kw.get('match_type', 'N/A')})")
        if len(paused_keywords) > 10:
            lines.append(f"  ... and {len(paused_keywords) - 10} more")
    
    if enabled_keywords:
        lines.append(f"Keywords Enabled ({len(enabled_keywords)}):")
        for kw in enabled_keywords[:10]:
            lines.append(f"  • {kw['keyword_text']} ({kw.get('match_type', 'N/A')})")
        if len(enabled_keywords) > 10:
            lines.append(f"  ... and {len(enabled_keywords) - 10} more")
    
    if changes['removed_keywords']:
        lines.append(f"Keywords Removed ({len(changes['removed_keywords'])}):")
        for kw in changes['removed_keywords'][:10]:
            lines.append(f"  • {kw['keyword_text']} ({kw.get('match_type', 'N/A')})")
        if len(changes['removed_keywords']) > 10:
            lines.append(f"  ... and {len(changes['removed_keywords']) - 10} more")
    
    if changes['new_keywords']:
        lines.append(f"New Keywords Added ({len(changes['new_keywords'])}):")
        for kw in changes['new_keywords'][:10]:
            lines.append(f"  • {kw['keyword_text']} ({kw.get('match_type', 'N/A')})")
        if len(changes['new_keywords']) > 10:
            lines.append(f"  ... and {len(changes['new_keywords']) - 10} more")
    
    if changes['ad_group_changes']:
        lines.append("Ad Group Status Changes:")
        for change in changes['ad_group_changes']:
            lines.append(f"  • {change['ad_group_name']}: {change['old_status']} → {change['new_status']}")
    
    return "\n".join(lines) if lines else "No structural changes detected."

