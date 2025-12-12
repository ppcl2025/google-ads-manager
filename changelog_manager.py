"""
Change Log Manager for Campaign Analysis Tracking

This module handles reading and writing changelog files for each account/campaign combination.
Changelogs track changes made between analysis reports, providing context to Claude for
continuous optimization.
"""

import os
from datetime import datetime
from pathlib import Path


CHANGELOG_DIR = "changelogs"


def ensure_changelog_dir():
    """Ensure the changelog directory exists."""
    Path(CHANGELOG_DIR).mkdir(exist_ok=True)
    # Add .gitkeep to ensure directory is tracked in git
    gitkeep_path = os.path.join(CHANGELOG_DIR, ".gitkeep")
    if not os.path.exists(gitkeep_path):
        with open(gitkeep_path, 'w') as f:
            f.write("# Changelog directory\n")


def get_changelog_path(account_id, campaign_id=None, account_name=None, campaign_name=None):
    """
    Get the file path for a changelog.
    
    Args:
        account_id: Account ID (e.g., "9660434837")
        campaign_id: Optional campaign ID (e.g., "22557679902")
        account_name: Optional account name for filename (e.g., "Titan Home Solutions")
        campaign_name: Optional campaign name for filename (e.g., "PPCL Central NC v3")
    
    Returns:
        Path to changelog file
    """
    ensure_changelog_dir()
    
    # Create a safe filename
    if account_name and campaign_name:
        # Use names for readability: "Titan_Home_Solutions_PPCL_Central_NC_v3.txt"
        safe_account = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in account_name).strip()
        safe_campaign = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in campaign_name).strip()
        filename = f"{safe_account}_{safe_campaign}.txt"
    elif account_name:
        safe_account = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in account_name).strip()
        filename = f"{safe_account}.txt"
    else:
        # Fallback to IDs
        if campaign_id:
            filename = f"{account_id}_{campaign_id}.txt"
        else:
            filename = f"{account_id}.txt"
    
    # Replace spaces with underscores and limit length
    filename = filename.replace(' ', '_')
    if len(filename) > 200:  # Limit filename length
        filename = filename[:200] + ".txt"
    
    return os.path.join(CHANGELOG_DIR, filename)


def read_changelog(account_id, campaign_id=None, account_name=None, campaign_name=None):
    """
    Read changelog for an account/campaign.
    
    Returns:
        String content of changelog, or empty string if not found
    """
    changelog_path = get_changelog_path(account_id, campaign_id, account_name, campaign_name)
    
    if os.path.exists(changelog_path):
        try:
            with open(changelog_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Warning: Could not read changelog: {e}")
            return ""
    return ""


def write_changelog_entry(account_id, campaign_id=None, account_name=None, campaign_name=None, 
                         changes_text="", period_performance=None):
    """
    Write a new entry to the changelog.
    
    Args:
        account_id: Account ID
        campaign_id: Optional campaign ID
        account_name: Optional account name
        campaign_name: Optional campaign name
        changes_text: Text describing changes made
        period_performance: Optional dict with performance metrics (leads, cpa, spend, etc.)
    """
    ensure_changelog_dir()
    changelog_path = get_changelog_path(account_id, campaign_id, account_name, campaign_name)
    
    # Read existing content
    existing_content = ""
    if os.path.exists(changelog_path):
        try:
            with open(changelog_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()
        except Exception as e:
            print(f"Warning: Could not read existing changelog: {e}")
    
    # Create new entry
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    entry_lines = []
    entry_lines.append("=" * 80)
    entry_lines.append(f"PERIOD: {date_str}")
    entry_lines.append("=" * 80)
    
    if period_performance:
        entry_lines.append(f"\nPerformance Summary:")
        if 'leads' in period_performance:
            entry_lines.append(f"  - Leads: {period_performance['leads']}")
        if 'cpa' in period_performance:
            entry_lines.append(f"  - CPA: ${period_performance['cpa']}")
        if 'spend' in period_performance:
            entry_lines.append(f"  - Spend: ${period_performance['spend']}")
        if 'conversion_rate' in period_performance:
            entry_lines.append(f"  - Conversion Rate: {period_performance['conversion_rate']}%")
    
    if changes_text.strip():
        entry_lines.append(f"\nChanges Made ({timestamp}):")
        entry_lines.append("-" * 80)
        # Split by lines and add bullet points
        for line in changes_text.strip().split('\n'):
            line = line.strip()
            if line:
                entry_lines.append(f"  • {line}")
    
    entry_lines.append("\n")
    
    # Prepend new entry to existing content (most recent first)
    new_content = "\n".join(entry_lines) + "\n" + existing_content
    
    # Write to file
    try:
        with open(changelog_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    except Exception as e:
        print(f"Error writing changelog: {e}")
        return False


def format_changelog_for_prompt(changelog_content):
    """
    Format changelog content for inclusion in Claude prompt.
    
    Args:
        changelog_content: Raw changelog text
    
    Returns:
        Formatted string for prompt, or empty string if no content
    """
    if not changelog_content or not changelog_content.strip():
        return ""
    
    # Limit to last 3 periods to avoid prompt bloat
    lines = changelog_content.split('\n')
    periods = []
    current_period = []
    
    for line in lines:
        if line.startswith("=" * 80) or line.startswith("PERIOD:"):
            if current_period:
                periods.append('\n'.join(current_period))
            current_period = [line]
        else:
            current_period.append(line)
    
    if current_period:
        periods.append('\n'.join(current_period))
    
    # Take last 3 periods (most recent)
    recent_periods = periods[:3] if len(periods) > 3 else periods
    
    if not recent_periods:
        return ""
    
    formatted = "=== PREVIOUS CHANGES & CONTEXT ===\n\n"
    formatted += "\n\n".join(recent_periods)
    formatted += "\n\n=== END OF PREVIOUS CHANGES ===\n"
    
    return formatted

