"""
Real Estate Google Ads Analyzer - Streamlit Web App
Modern web interface for Google Ads campaign analysis and management
"""

import streamlit as st
import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from authenticate import get_client
from account_manager import select_account_interactive, select_campaign_interactive, list_customer_accounts
from account_campaign_manager import get_sub_accounts, create_sub_account, create_campaign, US_TIMEZONES
from real_estate_analyzer import RealEstateAnalyzer
from comprehensive_data_fetcher import fetch_comprehensive_campaign_data, format_campaign_data_for_prompt
from keyword_planner_fetcher import (
    fetch_keyword_planner_data, 
    get_related_keyword_suggestions,
    format_keyword_planner_for_prompt,
    get_geo_target_constants,
    get_campaign_geo_targets
)
from help_system import (
    load_documentation,
    find_relevant_docs,
    format_docs_for_prompt,
    get_document_citations,
    create_help_prompt,
    get_suggested_questions
)

# Load environment variables (works with .env file locally or Streamlit Cloud secrets)
load_dotenv()

# For Streamlit Cloud, also check secrets
if hasattr(st, 'secrets'):
    # Streamlit Cloud uses st.secrets instead of .env file
    try:
        os.environ['GOOGLE_ADS_DEVELOPER_TOKEN'] = st.secrets.get('GOOGLE_ADS_DEVELOPER_TOKEN', os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN', ''))
        os.environ['GOOGLE_ADS_CLIENT_ID'] = st.secrets.get('GOOGLE_ADS_CLIENT_ID', os.getenv('GOOGLE_ADS_CLIENT_ID', ''))
        os.environ['GOOGLE_ADS_CLIENT_SECRET'] = st.secrets.get('GOOGLE_ADS_CLIENT_SECRET', os.getenv('GOOGLE_ADS_CLIENT_SECRET', ''))
        os.environ['GOOGLE_ADS_CUSTOMER_ID'] = st.secrets.get('GOOGLE_ADS_CUSTOMER_ID', os.getenv('GOOGLE_ADS_CUSTOMER_ID', ''))
        os.environ['ANTHROPIC_API_KEY'] = st.secrets.get('ANTHROPIC_API_KEY', os.getenv('ANTHROPIC_API_KEY', ''))
    except Exception as e:
        # If secrets are not configured, use .env file (for local development)
        pass

# Page configuration
st.set_page_config(
    page_title="Google Ads Analyzer",
        page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a5490;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .success-box {
        padding: 1rem;
        border-radius: 5px;
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 5px;
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    /* Sidebar navigation button styles - unselected */
    div[data-testid*="nav_"] > button[kind="secondary"] {
        background-color: #2d3748 !important;
        border: 2px solid #1a202c !important;
        color: #e2e8f0 !important;
    }
    div[data-testid*="nav_"] > button[kind="secondary"]:hover {
        background-color: #374151 !important;
        border-color: #4b5563 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    /* Selected button style - lighter shade with darker outline */
    div[data-testid*="nav_"] > button[kind="primary"] {
        background-color: #4a5568 !important;
        border: 2px solid #2d3748 !important;
        color: white !important;
    }
    div[data-testid*="nav_"] > button[kind="primary"]:hover {
        background-color: #556270 !important;
        border-color: #374151 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'client' not in st.session_state:
    st.session_state.client = None
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = None
if 'selected_account' not in st.session_state:
    st.session_state.selected_account = None
if 'selected_campaign' not in st.session_state:
    st.session_state.selected_campaign = None
if 'selected_model' not in st.session_state:
    st.session_state.selected_model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")

def initialize_client():
    """Initialize Google Ads client."""
    if 'client' not in st.session_state or st.session_state.client is None:
        try:
            st.session_state.client = get_client()
            if st.session_state.client:
                return True
            else:
                st.error("❌ Failed to authenticate with Google Ads API. Please check your credentials.")
                return False
        except Exception as e:
            st.error(f"❌ Error initializing client: {str(e)}")
            return False
    return True

def initialize_analyzer():
    """Initialize Claude analyzer."""
    if 'analyzer' not in st.session_state or st.session_state.analyzer is None:
        try:
            # Use selected model from sidebar if available, otherwise use default
            model = st.session_state.get('selected_model', os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514"))
            st.session_state.analyzer = RealEstateAnalyzer(model=model)
            return True
        except Exception as e:
            st.error(f"❌ Error initializing Claude analyzer: {str(e)}")
            return False
    return True

def main():
    """Main application."""
    # Header
    st.markdown('<h1 class="main-header">Google Ads Account Manager - AI Agent</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-Powered Campaign Analysis & Management for Real Estate Investors</p>', unsafe_allow_html=True)
    
    # Sidebar navigation
    with st.sidebar:
        # Add logo at top of sidebar
        logo_paths = ['sidebar_logo.png', 'PPC_LAUNCH_logo.png', 'logo.png', 'ppc_launch_logo.png']
        logo_found = False
        for logo_path in logo_paths:
            if os.path.exists(logo_path):
                st.image(logo_path, use_container_width=True)
                logo_found = True
                break
        if not logo_found:
            # Fallback to placeholder if logo not found
            st.image("https://via.placeholder.com/200x60/1a5490/ffffff?text=Google+Ads", use_container_width=True)
        st.markdown("---")
        
        # Navigation buttons
        nav_items = [
            ("📊 Campaign Analysis", "📊 Campaign Analysis"),
            ("📝 Ad Copy Optimization", "📝 Ad Copy Optimization"),
            ("🔍 Keyword Research", "🔍 Keyword Research"),
            ("📄 Biweekly Reports", "📄 Biweekly Reports"),
            ("💬 Ask Claude", "💬 Ask Claude"),
            ("➕ Create Account", "➕ Create Account"),
            ("🎯 Create Campaign", "🎯 Create Campaign")
        ]
        
        for nav_text, nav_value in nav_items:
            is_selected = (st.session_state.get('current_page', '📊 Campaign Analysis') == nav_value)
            button_type = "primary" if is_selected else "secondary"
            
            if st.button(nav_text, key=f"nav_{nav_value}", use_container_width=True, type=button_type):
                st.session_state.current_page = nav_value
                st.rerun()
        
        page = st.session_state.get('current_page', '📊 Campaign Analysis')
        
        st.markdown("---")
        st.markdown("### Settings")
        
        # Model selection
        model_options = {
            "Claude Sonnet 4": "claude-sonnet-4-20250514",
            "Claude 3.5 Haiku": "claude-3-5-haiku-20241022",
            "Claude 3 Opus": "claude-3-opus-20240229"
        }
        selected_model = st.selectbox("Claude Model", list(model_options.keys()), index=0)
        # Store selected model for later use (analyzer not initialized yet)
        st.session_state.selected_model = model_options[selected_model]
        
        # Help Center button
        if st.button("❓ Help Center", use_container_width=True):
            st.session_state.help_page_triggered = True
            st.rerun()
        
        st.markdown("---")
        st.markdown("### Status")
        if 'client' in st.session_state and st.session_state.client:
            st.success("✅ Connected")
        else:
            st.warning("⚠️ Not Connected")
    
    # Initialize client if needed
    if not initialize_client():
        st.stop()
    
    # Initialize analyzer if needed
    if not initialize_analyzer():
        st.stop()
    
    # Update analyzer model if it was changed in sidebar
    if 'selected_model' in st.session_state and st.session_state.analyzer:
        st.session_state.analyzer.model = st.session_state.selected_model
    
    # Check if Help Center was triggered from Settings button
    if st.session_state.get('help_page_triggered', False):
        st.session_state.help_page_triggered = False
        show_help_chat()
    # Route to appropriate page
    elif page == "📊 Campaign Analysis":
        show_comprehensive_analysis()
    elif page == "📝 Ad Copy Optimization":
        show_ad_copy_optimization()
    elif page == "🔍 Keyword Research":
        show_keyword_research()
    elif page == "📄 Biweekly Reports":
        show_biweekly_reports()
    elif page == "💬 Ask Claude":
        show_qa_chat()
    elif page == "➕ Create Account":
        show_create_account()
    elif page == "🎯 Create Campaign":
        show_create_campaign()

def show_comprehensive_analysis():
    """Comprehensive campaign analysis page."""
    st.header("📊 Comprehensive Campaign Analysis")
    st.markdown("Get detailed optimization recommendations for your campaigns.")
    
    # Account and campaign selection
    col1, col2 = st.columns(2)
    
    with col1:
        # Get accounts
        mcc_id = os.getenv("GOOGLE_ADS_CUSTOMER_ID")
        if mcc_id:
            try:
                accounts = list_customer_accounts(st.session_state.client, mcc_id)
                account_options = {f"{acc['descriptive_name']} ({acc['customer_id']})": acc['customer_id'] for acc in accounts}
                selected_account_display = st.selectbox("Select Account", list(account_options.keys()))
                selected_account_id = account_options[selected_account_display]
            except Exception as e:
                st.error(f"Error loading accounts: {e}")
                st.stop()
        else:
            selected_account_id = st.text_input("Enter Customer ID", value="")
    
    with col2:
        # Get campaigns
        if selected_account_id:
            try:
                from account_manager import list_campaigns
                campaigns = list_campaigns(st.session_state.client, selected_account_id)
                campaign_options = {f"{camp['campaign_name']} (ID: {camp['campaign_id']})": camp['campaign_id'] for camp in campaigns}
                campaign_options["All Campaigns"] = None
                selected_campaign_display = st.selectbox("Select Campaign", list(campaign_options.keys()))
                selected_campaign_id = campaign_options[selected_campaign_display]
            except Exception as e:
                st.warning(f"Could not load campaigns: {e}")
                selected_campaign_id = None
        else:
            selected_campaign_id = None
    
    # Analysis parameters
    st.markdown("### Analysis Parameters")
    col1, col2 = st.columns(2)
    
    with col1:
        date_range = st.number_input("Date Range (days)", min_value=7, max_value=365, value=30, step=1)
    
    with col2:
        use_default_goals = st.checkbox("Use Default Optimization Goals", value=True)
    
    optimization_goals = None
    if not use_default_goals:
        optimization_goals = st.text_area("Custom Optimization Goals", height=100,
            placeholder="Enter your optimization goals, one per line...")
    
    # Display stored results if they exist (persists across button clicks)
    if 'analysis_results' in st.session_state and st.session_state['analysis_results']:
        results = st.session_state['analysis_results']
        st.markdown("---")
        st.markdown("### 📋 Optimization Recommendations")
        st.markdown(results['recommendations'])
        
        # Snapshot and Change Detection section
        st.markdown("---")
        st.markdown("### 📸 Snapshot & Change Detection")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save Snapshot", use_container_width=True, type="secondary", key="save_snapshot", 
                        help="Save current campaign state for automatic change detection later"):
                from snapshot_manager import save_snapshot
                account_name = results['account_display'].split(" (")[0] if results['account_display'] else None
                campaign_name = results['campaign_display'].split(" (")[0] if results['campaign_display'] and results['campaign_display'] != "All Campaigns" else None
                
                if 'campaign_data' in results:
                    snapshot_path = save_snapshot(
                        account_id=results['account_id'],
                        campaign_id=results['campaign_id'],
                        account_name=account_name,
                        campaign_name=campaign_name,
                        campaign_data=results['campaign_data']
                    )
                    if snapshot_path:
                        st.success("✅ Snapshot saved! You can now detect changes automatically after making updates in Google Ads.")
                    else:
                        st.error("❌ Failed to save snapshot.")
                else:
                    st.warning("⚠️ Campaign data not available. Please run analysis again.")
        
        with col2:
            if st.button("🔍 Detect Changes", use_container_width=True, type="secondary", key="detect_changes",
                        help="Compare current campaign state with saved snapshot and auto-generate changelog"):
                _detect_and_save_changes(results)
        
        # Change tracking section - Manual entry (still available)
        st.markdown("---")
        st.markdown("### 📝 Track Changes Made (Manual Entry)")
        st.info("💡 **Option 1 - Manual:** After implementing recommendations, document the changes here. **Option 2 - Automatic:** Use 'Save Snapshot' above, then 'Detect Changes' after making updates in Google Ads.")
        
        # Show previous changelog if exists
        if results.get('changelog_content'):
            with st.expander("📜 View Previous Changes", expanded=False):
                st.text_area("Previous Changes", results['changelog_content'], height=200, disabled=True, key="prev_changelog_display")
        
        # Text area for entering new changes
        changes_text = st.text_area(
            "Enter changes made to this campaign (one per line):",
            height=150,
            placeholder="Example:\n- Paused 8 underperforming keywords: 'sell my house as is', 'companies that buy houses'\n- Increased budget from $246/day to $275/day\n- Added 25 negative keywords (attorney, lawyer, agent, realtor)\n- Updated Foreclosure ad group copy with urgency messaging",
            key="changes_input",
            help="Enter each change on a new line. Be specific with details like keyword names, budget amounts, dates, etc."
        )
        
        # Save changes button
        col1, col2 = st.columns([2, 1])
        with col1:
            if st.button("💾 Save Changes to Changelog", use_container_width=True, type="primary", key="save_changes"):
                if changes_text.strip():
                    from changelog_manager import write_changelog_entry
                    account_name = results['account_display'].split(" (")[0] if results['account_display'] else None
                    campaign_name = results['campaign_display'].split(" (")[0] if results['campaign_display'] and results['campaign_display'] != "All Campaigns" else None
                    
                    success = write_changelog_entry(
                        account_id=results['account_id'],
                        campaign_id=results['campaign_id'],
                        account_name=account_name,
                        campaign_name=campaign_name,
                        changes_text=changes_text
                    )
                    
                    if success:
                        st.success("✅ Changes saved to changelog! They will be included in future analyses.")
                        # Clear the text area
                        st.session_state['changes_input'] = ""
                        st.rerun()
                    else:
                        st.error("❌ Failed to save changes. Please try again.")
                else:
                    st.warning("⚠️ Please enter at least one change before saving.")
        
        # Save options (PDF and Drive) - moved after change tracking
        st.markdown("---")
        st.markdown("### 💾 Export Options")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save to PDF", use_container_width=True, key="save_pdf_analysis_stored"):
                _save_analysis_to_pdf()
        with col2:
            if st.button("📤 Upload to Google Drive", use_container_width=True, key="upload_drive_analysis_stored"):
                _upload_analysis_to_drive()
    
    # Run analysis button
    if st.button("🚀 Run Comprehensive Analysis", type="primary", use_container_width=True):
        if not selected_account_id:
            st.error("Please select an account.")
            return
        
        # Create progress container
        progress_container = st.container()
        with progress_container:
            status_text = st.empty()
            status_text.info("🔄 Step 1/3: Fetching campaign data from Google Ads API...")
            
            try:
                # Step 1: Fetch data (this might take time)
                status_text.info("🔄 Step 1/3: Fetching campaign data from Google Ads API...")
                
                # We need to fetch data first to show progress
                from comprehensive_data_fetcher import fetch_comprehensive_campaign_data, format_campaign_data_for_prompt
                api_call_counter = {'count': 0}
                data = fetch_comprehensive_campaign_data(
                    st.session_state.client,
                    selected_account_id,
                    campaign_id=selected_campaign_id,
                    date_range_days=date_range,
                    api_call_counter=api_call_counter
                )
                
                if not data['campaigns']:
                    st.error("No campaign data found for the selected account/campaign.")
                    return
                
                # Step 2: Format data
                status_text.info("🔄 Step 2/3: Formatting data for analysis...")
                campaign_data_str = format_campaign_data_for_prompt(data)
                
                # Step 3: Read changelog for context (if exists)
                status_text.info("🔄 Step 3/4: Loading change history...")
                from changelog_manager import read_changelog, format_changelog_for_prompt
                changelog_content = read_changelog(
                    account_id=selected_account_id,
                    campaign_id=selected_campaign_id,
                    account_name=selected_account_display.split(" (")[0] if selected_account_display else None,
                    campaign_name=selected_campaign_display.split(" (")[0] if selected_campaign_display and selected_campaign_display != "All Campaigns" else None
                )
                changelog_context = format_changelog_for_prompt(changelog_content) if changelog_content else None
                
                # Step 4: Call Claude (pass pre-fetched data to avoid re-fetching)
                status_text.info("🔄 Step 4/4: Claude is analyzing your campaign data... (this may take 1-2 minutes)")
                
                try:
                    recommendations = st.session_state.analyzer.analyze(
                        customer_id=selected_account_id,
                        campaign_id=selected_campaign_id,
                        date_range_days=date_range,
                        optimization_goals=optimization_goals,
                        prompt_type='full',
                        pre_fetched_data=data,  # Pass pre-fetched data
                        changelog_context=changelog_context  # Pass changelog context
                    )
                    
                    # Store results in session state so they persist across button clicks
                    st.session_state['analysis_results'] = {
                        'recommendations': recommendations,
                        'account_id': selected_account_id,
                        'account_display': selected_account_display,
                        'campaign_id': selected_campaign_id,
                        'campaign_display': selected_campaign_display,
                        'date_range': date_range,
                        'changelog_content': changelog_content,  # Store for display
                        'campaign_data': data  # Store campaign data for snapshot
                    }
                    
                    status_text.empty()
                    st.success("✅ Analysis Complete!")
                    st.rerun()  # Rerun to show the results below
                except Exception as e:
                    status_text.empty()
                    st.error(f"❌ Error during analysis: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
                    return
            
            except Exception as e:
                st.error(f"❌ Error running analysis: {str(e)}")

def _detect_and_save_changes(results):
    """Detect changes by comparing current state with snapshot, then save to changelog."""
    from snapshot_manager import load_snapshot, compare_snapshots, format_changes_for_changelog
    from comprehensive_data_fetcher import fetch_comprehensive_campaign_data
    from changelog_manager import write_changelog_entry
    import streamlit as st
    
    account_name = results['account_display'].split(" (")[0] if results['account_display'] else None
    campaign_name = results['campaign_display'].split(" (")[0] if results['campaign_display'] and results['campaign_display'] != "All Campaigns" else None
    
    # Load snapshot
    old_snapshot = load_snapshot(
        account_id=results['account_id'],
        campaign_id=results['campaign_id'],
        account_name=account_name,
        campaign_name=campaign_name
    )
    
    if not old_snapshot:
        st.warning("⚠️ No snapshot found. Please save a snapshot first after running an analysis.")
        return
    
    # Fetch current campaign state
    with st.spinner("🔄 Fetching current campaign state..."):
        try:
            api_call_counter = {'count': 0}
            current_data = fetch_comprehensive_campaign_data(
                st.session_state.client,
                results['account_id'],
                campaign_id=results['campaign_id'],
                date_range_days=7,  # Just need current state, not historical
                api_call_counter=api_call_counter
            )
        except Exception as e:
            st.error(f"❌ Error fetching current campaign data: {str(e)}")
            return
    
    # Compare snapshots
    with st.spinner("🔍 Comparing snapshots..."):
        changes = compare_snapshots(old_snapshot, current_data)
    
    # Format changes for display
    changes_text = format_changes_for_changelog(changes)
    
    if changes_text == "No structural changes detected.":
        st.info("ℹ️ No changes detected. Campaign state matches the saved snapshot.")
        return
    
    # Display detected changes
    st.markdown("### 🔍 Detected Changes")
    st.text_area("Changes Detected", changes_text, height=300, disabled=True, key="detected_changes_display")
    
    # Option to save to changelog
    if st.button("✅ Save to Changelog", use_container_width=True, type="primary", key="save_detected_changes"):
        success = write_changelog_entry(
            account_id=results['account_id'],
            campaign_id=results['campaign_id'],
            account_name=account_name,
            campaign_name=campaign_name,
            changes_text=changes_text
        )
        
        if success:
            st.success("✅ Changes automatically saved to changelog! They will be included in future analyses.")
            # Update snapshot to current state
            from snapshot_manager import save_snapshot
            save_snapshot(
                account_id=results['account_id'],
                campaign_id=results['campaign_id'],
                account_name=account_name,
                campaign_name=campaign_name,
                campaign_data=current_data
            )
            st.rerun()
        else:
            st.error("❌ Failed to save changes to changelog.")

def _save_analysis_to_pdf():
    """Helper function to save analysis to PDF."""
    if 'analysis_results' not in st.session_state:
        st.error("No analysis results to save. Please run an analysis first.")
        return
    
    results = st.session_state['analysis_results']
    account_name = results['account_display'].split(" (")[0] if results['account_display'] else "Account"
    campaign_name = results['campaign_display'].split(" (")[0] if results['campaign_display'] and results['campaign_display'] != "All Campaigns" else "All Campaigns"
    
    try:
        from real_estate_analyzer import create_pdf_report
        import tempfile
        import os
        from datetime import datetime
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_filepath = temp_file.name
        temp_file.close()
        
        if create_pdf_report(
            results['recommendations'],
            account_name,
            campaign_name,
            results['date_range'],
            temp_filepath
        ):
            with open(temp_filepath, 'rb') as f:
                st.download_button(
                    label="📥 Download PDF",
                    data=f.read(),
                    file_name=f"{account_name}_{campaign_name}_Analysis_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key=f"download_pdf_{datetime.now().timestamp()}"
                )
            os.unlink(temp_filepath)
            st.success("✅ PDF created successfully! Click the download button above.")
        else:
            st.error("❌ Failed to create PDF")
    except Exception as e:
        st.error(f"❌ Error creating PDF: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

# Google Drive folder IDs for different report types
DRIVE_FOLDER_IDS = {
    'optimization_reports': '185ebaQUxrNIMLIiNp9R61PVWEHdLZghn',
    'ad_copy_optimization': '1lWe5SH7VLV0LMZLlUWt8WW4JeOfamehn',
    'qa_chat': '1kMShfz38NWRkBK99GzwjDJTzyWi3TXFW',
    'biweekly_reports': '185ebaQUxrNIMLIiNp9R61PVWEHdLZghn'  # Same as optimization reports
}

def _upload_analysis_to_drive():
    """Helper function to upload analysis to Google Drive."""
    if 'analysis_results' not in st.session_state:
        st.error("No analysis results to upload. Please run an analysis first.")
        return
    
    results = st.session_state['analysis_results']
    account_name = results['account_display'].split(" (")[0] if results['account_display'] else "Account"
    campaign_name = results['campaign_display'].split(" (")[0] if results['campaign_display'] and results['campaign_display'] != "All Campaigns" else "All Campaigns"
    
    try:
        from real_estate_analyzer import create_pdf_report, upload_to_drive, get_drive_service
        import tempfile
        import os
        from datetime import datetime
        
        # Create temporary PDF
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_filepath = temp_file.name
        temp_file.close()
        
        # Generate PDF
        if not create_pdf_report(
            results['recommendations'],
            account_name,
            campaign_name,
            results['date_range'],
            temp_filepath
        ):
            st.error("❌ Failed to create PDF for upload")
            return
        
        # Get Drive service
        drive_service = get_drive_service()
        if not drive_service:
            st.error("❌ Could not authenticate with Google Drive. Please check your credentials.")
            os.unlink(temp_filepath)
            return
        
        # Use specific folder ID for optimization reports
        folder_id = DRIVE_FOLDER_IDS['optimization_reports']
        
        # Upload file
        filename = f"{account_name}_{campaign_name}_Analysis_{datetime.now().strftime('%Y%m%d')}.pdf"
        file_id, file_link = upload_to_drive(drive_service, temp_filepath, filename, folder_id)
        
        # Clean up temp file
        os.unlink(temp_filepath)
        
        if file_id and file_link:
            st.success(f"✅ Successfully uploaded to Google Drive!")
            st.markdown(f"📁 [View file in Google Drive]({file_link})")
        else:
            st.error("❌ Failed to upload to Google Drive")
    except Exception as e:
        st.error(f"❌ Error uploading to Google Drive: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

def show_ad_copy_optimization():
    """Ad copy optimization page."""
    st.header("📝 Ad Copy Optimization")
    st.markdown("Get AI-powered ad copy recommendations with character limits and A/B testing suggestions.")
    
    # Account and campaign selection
    col1, col2 = st.columns(2)
    
    with col1:
        mcc_id = os.getenv("GOOGLE_ADS_CUSTOMER_ID")
        if mcc_id:
            try:
                accounts = list_customer_accounts(st.session_state.client, mcc_id)
                account_options = {f"{acc['descriptive_name']} ({acc['customer_id']})": acc['customer_id'] for acc in accounts}
                selected_account_display = st.selectbox("Select Account", list(account_options.keys()))
                selected_account_id = account_options[selected_account_display]
            except Exception as e:
                st.error(f"Error loading accounts: {e}")
                st.stop()
        else:
            selected_account_id = st.text_input("Enter Customer ID", value="")
    
    with col2:
        if selected_account_id:
            try:
                from account_manager import list_campaigns
                campaigns = list_campaigns(st.session_state.client, selected_account_id)
                campaign_options = {f"{camp['campaign_name']} (ID: {camp['campaign_id']})": camp['campaign_id'] for camp in campaigns}
                campaign_options["All Campaigns"] = None
                selected_campaign_display = st.selectbox("Select Campaign", list(campaign_options.keys()))
                selected_campaign_id = campaign_options[selected_campaign_display]
            except Exception as e:
                st.warning(f"Could not load campaigns: {e}")
                selected_campaign_id = None
        else:
            selected_campaign_id = None
    
    # Analysis parameters
    date_range = st.number_input("Date Range (days)", min_value=7, max_value=365, value=30, step=1, key="ad_copy_date_range")
    
    # Run analysis button
    if st.button("🚀 Run Ad Copy Analysis", type="primary", use_container_width=True):
        if not selected_account_id:
            st.error("Please select an account.")
            return
        
        with st.spinner("🤖 Claude is analyzing your ad copy..."):
            try:
                recommendations = st.session_state.analyzer.analyze(
                    customer_id=selected_account_id,
                    campaign_id=selected_campaign_id,
                    date_range_days=date_range,
                    optimization_goals=None,
                    prompt_type='ad_copy'
                )
                
                # Store results in session state
                st.session_state['ad_copy_results'] = {
                    'recommendations': recommendations,
                    'account_id': selected_account_id,
                    'account_display': selected_account_display,
                    'campaign_id': selected_campaign_id,
                    'campaign_display': selected_campaign_display,
                    'date_range': date_range
                }
                
                st.success("✅ Ad Copy Analysis Complete!")
                st.rerun()  # Rerun to show results below
                
            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
    
    # Display stored results if they exist
    if 'ad_copy_results' in st.session_state and st.session_state['ad_copy_results']:
        results = st.session_state['ad_copy_results']
        st.markdown("---")
        st.markdown("### 📋 Ad Copy Recommendations")
        st.markdown(results['recommendations'])
        
        # Save options
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save to PDF", use_container_width=True, key="ad_copy_pdf_stored"):
                _save_ad_copy_to_pdf()
        with col2:
            if st.button("📤 Upload to Google Drive", use_container_width=True, key="ad_copy_drive_stored"):
                _upload_ad_copy_to_drive()

def _save_ad_copy_to_pdf():
    """Helper function to save ad copy analysis to PDF."""
    if 'ad_copy_results' not in st.session_state:
        st.error("No ad copy analysis to save. Please run an analysis first.")
        return
    
    results = st.session_state['ad_copy_results']
    account_name = results['account_display'].split(" (")[0] if results['account_display'] else "Account"
    campaign_name = results['campaign_display'].split(" (")[0] if results['campaign_display'] and results['campaign_display'] != "All Campaigns" else "All Campaigns"
    
    try:
        from real_estate_analyzer import create_pdf_report
        import tempfile
        import os
        from datetime import datetime
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_filepath = temp_file.name
        temp_file.close()
        
        if create_pdf_report(
            results['recommendations'],
            account_name,
            campaign_name,
            results['date_range'],
            temp_filepath
        ):
            with open(temp_filepath, 'rb') as f:
                st.download_button(
                    label="📥 Download PDF",
                    data=f.read(),
                    file_name=f"{account_name}_{campaign_name}_AdCopy_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key=f"download_ad_copy_{datetime.now().timestamp()}"
                )
            os.unlink(temp_filepath)
            st.success("✅ PDF created successfully! Click the download button above.")
        else:
            st.error("❌ Failed to create PDF")
    except Exception as e:
        st.error(f"❌ Error creating PDF: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

def _upload_ad_copy_to_drive():
    """Helper function to upload ad copy analysis to Google Drive."""
    if 'ad_copy_results' not in st.session_state:
        st.error("No ad copy analysis to upload. Please run an analysis first.")
        return
    
    results = st.session_state['ad_copy_results']
    account_name = results['account_display'].split(" (")[0] if results['account_display'] else "Account"
    campaign_name = results['campaign_display'].split(" (")[0] if results['campaign_display'] and results['campaign_display'] != "All Campaigns" else "All Campaigns"
    
    try:
        from real_estate_analyzer import create_pdf_report, upload_to_drive, get_drive_service
        import tempfile
        import os
        from datetime import datetime
        
        # Create temporary PDF
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_filepath = temp_file.name
        temp_file.close()
        
        # Generate PDF
        if not create_pdf_report(
            results['recommendations'],
            account_name,
            campaign_name,
            results['date_range'],
            temp_filepath
        ):
            st.error("❌ Failed to create PDF for upload")
            return
        
        # Get Drive service
        drive_service = get_drive_service()
        if not drive_service:
            st.error("❌ Could not authenticate with Google Drive. Please check your credentials.")
            os.unlink(temp_filepath)
            return
        
        # Use specific folder ID for ad copy optimization
        folder_id = DRIVE_FOLDER_IDS['ad_copy_optimization']
        
        # Upload file
        filename = f"{account_name}_{campaign_name}_AdCopy_{datetime.now().strftime('%Y%m%d')}.pdf"
        file_id, file_link = upload_to_drive(drive_service, temp_filepath, filename, folder_id)
        
        # Clean up temp file
        os.unlink(temp_filepath)
        
        if file_id and file_link:
            st.success(f"✅ Successfully uploaded to Google Drive!")
            st.markdown(f"📁 [View file in Google Drive]({file_link})")
        else:
            st.error("❌ Failed to upload to Google Drive")
    except Exception as e:
        st.error(f"❌ Error uploading to Google Drive: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

def show_biweekly_reports():
    """Biweekly reports page."""
    st.header("📄 Biweekly Client Reports")
    st.markdown("Generate professional 2-page PDF reports for your clients.")
    
    # Account and campaign selection
    col1, col2 = st.columns(2)
    
    with col1:
        mcc_id = os.getenv("GOOGLE_ADS_CUSTOMER_ID")
        if mcc_id:
            try:
                accounts = list_customer_accounts(st.session_state.client, mcc_id)
                account_options = {f"{acc['descriptive_name']} ({acc['customer_id']})": acc['customer_id'] for acc in accounts}
                selected_account_display = st.selectbox("Select Account", list(account_options.keys()), key="biweekly_account")
                selected_account_id = account_options[selected_account_display]
            except Exception as e:
                st.error(f"Error loading accounts: {e}")
                st.stop()
        else:
            selected_account_id = st.text_input("Enter Customer ID", value="", key="biweekly_account_input")
    
    with col2:
        if selected_account_id:
            try:
                from account_manager import list_campaigns
                campaigns = list_campaigns(st.session_state.client, selected_account_id)
                campaign_options = {f"{camp['campaign_name']} (ID: {camp['campaign_id']})": camp['campaign_id'] for camp in campaigns}
                campaign_options["All Campaigns"] = None
                selected_campaign_display = st.selectbox("Select Campaign", list(campaign_options.keys()), key="biweekly_campaign")
                selected_campaign_id = campaign_options[selected_campaign_display]
            except Exception as e:
                st.warning(f"Could not load campaigns: {e}")
                selected_campaign_id = None
        else:
            selected_campaign_id = None
    
    # Date range (default to 14 days for biweekly)
    date_range = st.number_input("Date Range (days)", min_value=7, max_value=365, value=14, step=1, key="biweekly_date_range")
    st.info("💡 Biweekly reports typically use 14 days of data.")
    
    # Generate report button
    if st.button("📄 Generate Biweekly Report", type="primary", use_container_width=True):
        if not selected_account_id:
            st.error("Please select an account.")
            return
        
        with st.spinner("🤖 Claude is generating your biweekly report..."):
            try:
                report_content = st.session_state.analyzer.analyze(
                    customer_id=selected_account_id,
                    campaign_id=selected_campaign_id,
                    date_range_days=date_range,
                    optimization_goals=None,
                    prompt_type='biweekly_report'
                )
                
                # Store results in session state
                st.session_state['biweekly_results'] = {
                    'report_content': report_content,
                    'account_id': selected_account_id,
                    'account_display': selected_account_display,
                    'campaign_id': selected_campaign_id,
                    'campaign_display': selected_campaign_display,
                    'date_range': date_range
                }
                
                st.success("✅ Report Generated!")
                st.rerun()  # Rerun to show results below
                        
            except Exception as e:
                st.error(f"❌ Error generating report: {str(e)}")
    
    # Display stored results if they exist
    if 'biweekly_results' in st.session_state and st.session_state['biweekly_results']:
        results = st.session_state['biweekly_results']
        st.markdown("---")
        st.markdown("### 📄 Biweekly Report Preview")
        # Format the content to ensure bullet points are on separate lines
        formatted_content = results['report_content']
        import re
        # Split content by sections and format bullets
        # For sections with bullets, ensure each bullet is on its own line
        # Pattern: Find bullets that are on the same line and separate them
        lines = formatted_content.split('\n')
        formatted_lines = []
        in_bullet_section = False
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            # Detect bullet sections
            if re.match(r'^\*\*?(What This Means|What We\'re Optimizing|Next Steps)', stripped, re.IGNORECASE):
                in_bullet_section = True
                formatted_lines.append(line)
                continue
            # Detect end of bullet section (next section header or blank line followed by header)
            if stripped and not stripped.startswith('•') and not stripped.startswith('-') and re.match(r'^\*\*?[A-Z]', stripped):
                in_bullet_section = False
                formatted_lines.append(line)
                continue
            
            if in_bullet_section and stripped:
                # If line contains multiple bullets, split them
                if '•' in stripped and stripped.count('•') > 1:
                    # Split by bullet and add each on new line
                    parts = re.split(r'(•\s+)', stripped)
                    for j in range(1, len(parts), 2):
                        if j+1 < len(parts):
                            bullet_text = parts[j] + parts[j+1].strip()
                            formatted_lines.append(bullet_text)
                            formatted_lines.append('')  # Add blank line after each bullet
                else:
                    formatted_lines.append(line)
                    # Add blank line after bullet if not already present
                    if (stripped.startswith('•') or stripped.startswith('-')) and i+1 < len(lines):
                        next_line = lines[i+1].strip() if i+1 < len(lines) else ''
                        if next_line and (next_line.startswith('•') or next_line.startswith('-')):
                            formatted_lines.append('')  # Add blank line between bullets
            else:
                formatted_lines.append(line)
        
        formatted_content = '\n'.join(formatted_lines)
        st.markdown(formatted_content)
        
        # Save options
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save to PDF", use_container_width=True, key="biweekly_pdf_stored"):
                _save_biweekly_to_pdf()
        with col2:
            if st.button("📤 Upload to Google Drive", use_container_width=True, key="biweekly_drive_stored"):
                _upload_biweekly_to_drive()

def _save_biweekly_to_pdf():
    """Helper function to save biweekly report to PDF."""
    if 'biweekly_results' not in st.session_state:
        st.error("No biweekly report to save. Please generate a report first.")
        return
    
    results = st.session_state['biweekly_results']
    account_name = results['account_display'].split(" (")[0] if results['account_display'] else "Account"
    campaign_name = results['campaign_display'].split(" (")[0] if results['campaign_display'] and results['campaign_display'] != "All Campaigns" else "All Campaigns"
    
    try:
        from real_estate_analyzer import create_biweekly_report_pdf
        import tempfile
        import os
        from datetime import datetime
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_filepath = temp_file.name
        temp_file.close()
        
        try:
            # Try to create PDF and capture any errors
            pdf_result = create_biweekly_report_pdf(
                results['report_content'], 
                account_name, 
                campaign_name, 
                results['date_range'], 
                temp_filepath
            )
            
            if pdf_result:
                # Check if file was actually created
                if os.path.exists(temp_filepath) and os.path.getsize(temp_filepath) > 0:
                    with open(temp_filepath, 'rb') as f:
                        st.download_button(
                            label="📥 Download PDF",
                            data=f.read(),
                            file_name=f"{account_name}_BiweeklyReport_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                            key=f"download_biweekly_{datetime.now().timestamp()}"
                        )
                    os.unlink(temp_filepath)
                    st.success("✅ PDF created successfully! Click the download button above.")
                else:
                    st.error("❌ PDF file was not created or is empty.")
                    st.info("💡 Check the error details below or in Streamlit Cloud logs.")
                    # Try to get error from st.session_state if available
                    if 'pdf_error' in st.session_state:
                        with st.expander("Error Details", expanded=True):
                            st.code(st.session_state['pdf_error'])
            else:
                st.error("❌ Failed to create PDF.")
                st.info("💡 Check the error details below or in Streamlit Cloud logs.")
                # Try to get error from st.session_state if available
                if 'pdf_error' in st.session_state:
                    with st.expander("Error Details", expanded=True):
                        st.code(st.session_state['pdf_error'])
        except Exception as e:
            st.error(f"❌ Error creating PDF: {str(e)}")
            import traceback
            error_trace = traceback.format_exc()
            with st.expander("Show detailed error", expanded=True):
                st.code(error_trace)
            # Clean up temp file if it exists
            if os.path.exists(temp_filepath):
                os.unlink(temp_filepath)
    except Exception as e:
        st.error(f"❌ Error creating PDF: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

def _upload_biweekly_to_drive():
    """Helper function to upload biweekly report to Google Drive."""
    if 'biweekly_results' not in st.session_state:
        st.error("No biweekly report to upload. Please generate a report first.")
        return
    
    results = st.session_state['biweekly_results']
    account_name = results['account_display'].split(" (")[0] if results['account_display'] else "Account"
    campaign_name = results['campaign_display'].split(" (")[0] if results['campaign_display'] and results['campaign_display'] != "All Campaigns" else "All Campaigns"
    
    try:
        from real_estate_analyzer import create_biweekly_report_pdf, upload_to_drive, get_drive_service
        import tempfile
        import os
        from datetime import datetime
        
        # Create temporary PDF
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_filepath = temp_file.name
        temp_file.close()
        
        # Generate PDF
        try:
            if not create_biweekly_report_pdf(results['report_content'], account_name, campaign_name, results['date_range'], temp_filepath):
                st.error("❌ Failed to create PDF for upload. Check the logs for details.")
                return
        except Exception as e:
            st.error(f"❌ Error creating PDF: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
            os.unlink(temp_filepath) if os.path.exists(temp_filepath) else None
            return
        
        # Get Drive service
        drive_service = get_drive_service()
        if not drive_service:
            st.error("❌ Could not authenticate with Google Drive. Please check your credentials.")
            os.unlink(temp_filepath)
            return
        
        # Use specific folder ID for biweekly reports
        folder_id = DRIVE_FOLDER_IDS['biweekly_reports']
        
        # Upload file
        filename = f"{account_name}_BiweeklyReport_{datetime.now().strftime('%Y%m%d')}.pdf"
        file_id, file_link = upload_to_drive(drive_service, temp_filepath, filename, folder_id)
        
        # Clean up temp file
        os.unlink(temp_filepath)
        
        if file_id and file_link:
            st.success(f"✅ Successfully uploaded to Google Drive!")
            st.markdown(f"📁 [View file in Google Drive]({file_link})")
        else:
            st.error("❌ Failed to upload to Google Drive")
    except Exception as e:
        st.error(f"❌ Error uploading to Google Drive: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

def show_qa_chat():
    """Q&A chat with Claude."""
    st.header("💬 Ask Claude")
    st.markdown("Get expert advice on Google Ads management.")
    
    # Initialize chat history
    if "qa_messages" not in st.session_state:
        st.session_state.qa_messages = []
    
    # Display chat history
    for message in st.session_state.qa_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Save options (show if there are messages)
    if st.session_state.qa_messages:
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save to PDF", use_container_width=True, key="qa_pdf"):
                _save_qa_to_pdf()
        with col2:
            if st.button("📤 Upload to Google Drive", use_container_width=True, key="qa_drive"):
                _upload_qa_to_drive()
    
    # User input
    user_question = st.chat_input("Ask Claude a question about Google Ads management...")
    
    if user_question:
        # Add user message
        st.session_state.qa_messages.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.markdown(user_question)
        
        # Get Claude's response
        with st.chat_message("assistant"):
            with st.spinner("Claude is thinking..."):
                try:
                    # Use modular prompt system for Q&A
                    from prompt_loader import get_prompt_for_page
                    try:
                        qa_prompt = get_prompt_for_page('qa', user_question=user_question)
                        qa_prompt = f"{qa_prompt}\n\n## Campaign Data Context:\n\nNo campaign data provided.\n\n## User Question:\n\n{user_question}"
                    except Exception as e:
                        # Fallback to legacy template
                        from real_estate_analyzer import QA_PROMPT_TEMPLATE
                        qa_prompt = QA_PROMPT_TEMPLATE.replace('{user_question}', user_question)
                        qa_prompt = qa_prompt.replace('{campaign_data_context}', "No campaign data provided.")
                    
                    system_message = "You are a Google Ads Senior Account Manager and Strategist. Answer the user's question with expert knowledge and actionable advice."
                    
                    message = st.session_state.analyzer.claude.messages.create(
                        model=st.session_state.analyzer.model,
                        max_tokens=8192,
                        system=system_message,
                        messages=[{"role": "user", "content": qa_prompt}]
                    )
                    
                    response = message.content[0].text
                    st.markdown(response)
                    st.session_state.qa_messages.append({"role": "assistant", "content": response})
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

def _save_qa_to_pdf():
    """Helper function to save Q&A chat to PDF."""
    if 'qa_messages' not in st.session_state or not st.session_state.qa_messages:
        st.error("No Q&A chat history to save. Please ask Claude a question first.")
        return
    
    try:
        from real_estate_analyzer import create_qa_chat_pdf
        import tempfile
        import os
        from datetime import datetime
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_filepath = temp_file.name
        temp_file.close()
        
        # create_qa_chat_pdf requires account_name and campaign_name, but for Q&A we don't have those
        # Use generic names
        if create_qa_chat_pdf(st.session_state.qa_messages, "Q&A Session", "Claude Chat", temp_filepath):
            with open(temp_filepath, 'rb') as f:
                st.download_button(
                    label="📥 Download PDF",
                    data=f.read(),
                    file_name=f"Claude_QA_Session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key=f"download_qa_{datetime.now().timestamp()}"
                )
            os.unlink(temp_filepath)
            st.success("✅ PDF created successfully! Click the download button above.")
        else:
            st.error("❌ Failed to create PDF")
    except Exception as e:
        st.error(f"❌ Error creating PDF: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

def _upload_qa_to_drive():
    """Helper function to upload Q&A chat to Google Drive."""
    if 'qa_messages' not in st.session_state or not st.session_state.qa_messages:
        st.error("No Q&A chat history to upload. Please ask Claude a question first.")
        return
    
    try:
        from real_estate_analyzer import create_qa_chat_pdf, upload_to_drive, get_drive_service
        import tempfile
        import os
        from datetime import datetime
        
        # Create temporary PDF
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_filepath = temp_file.name
        temp_file.close()
        
        # Generate PDF (create_qa_chat_pdf requires account_name and campaign_name)
        if not create_qa_chat_pdf(st.session_state.qa_messages, "Q&A Session", "Claude Chat", temp_filepath):
            st.error("❌ Failed to create PDF for upload")
            return
        
        # Get Drive service
        drive_service = get_drive_service()
        if not drive_service:
            st.error("❌ Could not authenticate with Google Drive. Please check your credentials.")
            os.unlink(temp_filepath)
            return
        
        # Use specific folder ID for Q&A chats
        folder_id = DRIVE_FOLDER_IDS['qa_chat']
        
        # Upload file
        filename = f"Claude_QA_Session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        file_id, file_link = upload_to_drive(drive_service, temp_filepath, filename, folder_id)
        
        # Clean up temp file
        os.unlink(temp_filepath)
        
        if file_id and file_link:
            st.success(f"✅ Successfully uploaded to Google Drive!")
            st.markdown(f"📁 [View file in Google Drive]({file_link})")
        else:
            st.error("❌ Failed to upload to Google Drive")
    except Exception as e:
        st.error(f"❌ Error uploading to Google Drive: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

def show_create_account():
    """Create new sub-account page."""
    st.header("➕ Create New Sub-Account")
    st.markdown("Create a new Google Ads sub-account under your MCC.")
    
    mcc_id = os.getenv("GOOGLE_ADS_CUSTOMER_ID")
    if not mcc_id:
        st.error("MCC Customer ID not found in environment variables.")
        st.stop()
    
    st.info(f"Creating account under MCC: {mcc_id}")
    
    # Account creation form
    with st.form("create_account_form"):
        account_name = st.text_input("Account Name *", placeholder="e.g., Real Estate Investor LLC")
        currency_code = st.selectbox("Currency *", ["USD", "CAD", "GBP", "EUR", "AUD"], index=0)
        time_zone = st.selectbox("Time Zone *", list(US_TIMEZONES.keys()), format_func=lambda x: US_TIMEZONES[x])
        
        st.markdown("### Account Settings")
        st.info("""
        **Default Settings:**
        - Account Name: As specified above
        - Currency: As selected above
        - Time Zone: As selected above
        - Manager Account: False (prevents automatic MCC payment profile linking)
        - Test Account: False (production account)
        - Tracking URL Template: Empty (can be set up later)
        - Payment Method: Client must set up their own payment method in Google Ads
        """)
        
        submitted = st.form_submit_button("Create Sub-Account", type="primary", use_container_width=True)
        
        if submitted:
            if not account_name:
                st.error("Please enter an account name.")
            else:
                with st.spinner("Creating sub-account..."):
                    try:
                        new_account_id = create_sub_account(
                            st.session_state.client,
                            mcc_id,
                            account_name,
                            currency_code,
                            time_zone
                        )
                        
                        if new_account_id:
                            st.success(f"✅ Sub-account created successfully!")
                            st.markdown(f"**Account ID:** `{new_account_id}`")
                            st.info("💡 The account has been created. The client will need to set up their own payment method in Google Ads.")
                    except Exception as e:
                        st.error(f"❌ Error creating account: {str(e)}")

def show_keyword_research():
    """Keyword Research page with Keyword Planner integration."""
    st.header("🔍 Keyword Research")
    st.markdown("Analyze keyword competition, search volume, and get AI-powered expansion recommendations.")
    
    # Account selection
    col1, col2 = st.columns(2)
    
    with col1:
        mcc_id = os.getenv("GOOGLE_ADS_CUSTOMER_ID")
        if mcc_id:
            try:
                accounts = list_customer_accounts(st.session_state.client, mcc_id)
                account_options = {f"{acc['descriptive_name']} ({acc['customer_id']})": acc['customer_id'] for acc in accounts}
                selected_account_display = st.selectbox("Select Account", list(account_options.keys()))
                selected_account_id = account_options[selected_account_display]
            except Exception as e:
                st.error(f"Error loading accounts: {e}")
                st.stop()
        else:
            selected_account_id = st.text_input("Enter Customer ID", value="")
    
    with col2:
        # Optional: Select campaign to get existing keywords
        if selected_account_id:
            try:
                from account_manager import list_campaigns
                campaigns = list_campaigns(st.session_state.client, selected_account_id)
                campaign_options = {f"{camp['campaign_name']} (ID: {camp['campaign_id']})": camp['campaign_id'] for camp in campaigns}
                campaign_options["None - Enter keywords manually"] = None
                selected_campaign_display = st.selectbox("Select Campaign (Optional)", list(campaign_options.keys()))
                selected_campaign_id = campaign_options[selected_campaign_display]
            except Exception as e:
                st.warning(f"Could not load campaigns: {e}")
                selected_campaign_id = None
        else:
            selected_campaign_id = None
    
    st.markdown("---")
    
    # Keyword input method
    input_method = st.radio(
        "Keyword Input Method",
        ["Enter keywords manually", "Load from campaign", "Generate suggestions from seed keywords"],
        horizontal=True
    )
    
    keywords_list = []
    
    if input_method == "Enter keywords manually":
        keywords_input = st.text_area(
            "Enter keywords (one per line)",
            height=150,
            placeholder="we buy houses\nsell my house fast\ninherited property buyer\ncash home buyer",
            help="Enter one keyword per line"
        )
        if keywords_input:
            keywords_list = [k.strip() for k in keywords_input.split("\n") if k.strip()]
    
    elif input_method == "Load from campaign":
        if not selected_campaign_id:
            st.warning("⚠️ Please select a campaign first.")
        else:
            if st.button("📥 Load Keywords from Campaign"):
                with st.spinner("Loading keywords from campaign..."):
                    try:
                        # Fetch campaign data to get keywords
                        data = fetch_comprehensive_campaign_data(
                            st.session_state.client,
                            selected_account_id,
                            campaign_id=selected_campaign_id,
                            date_range_days=30
                        )
                        
                        # Extract unique keywords
                        keywords_list = list(set([kw['keyword'] for kw in data.get('keywords', [])]))
                        
                        if keywords_list:
                            st.success(f"✅ Loaded {len(keywords_list)} keywords from campaign")
                            # Display keywords in text area for editing
                            keywords_text = "\n".join(keywords_list[:50])  # Limit to 50 for display
                            keywords_input = st.text_area(
                                "Keywords (editable)",
                                value=keywords_text,
                                height=200,
                                help="Edit keywords if needed, then click 'Analyze Keywords' below"
                            )
                            keywords_list = [k.strip() for k in keywords_input.split("\n") if k.strip()]
                        else:
                            st.warning("No keywords found in this campaign.")
                    except Exception as e:
                        st.error(f"Error loading keywords: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())
    
    elif input_method == "Generate suggestions from seed keywords":
        seed_keywords_input = st.text_area(
            "Enter seed keywords (one per line)",
            height=100,
            placeholder="we buy houses\ncash home buyer",
            help="Enter 1-3 seed keywords to generate related suggestions"
        )
        if seed_keywords_input:
            seed_keywords = [k.strip() for k in seed_keywords_input.split("\n") if k.strip()]
            if seed_keywords:
                if st.button("🔍 Generate Keyword Suggestions"):
                    with st.spinner("Generating keyword suggestions from Keyword Planner..."):
                        try:
                            suggestions = get_related_keyword_suggestions(
                                st.session_state.client,
                                selected_account_id,
                                seed_keywords
                            )
                            
                            if suggestions:
                                # Show top 50 suggestions
                                st.success(f"✅ Generated {len(suggestions)} keyword suggestions")
                                
                                # Display as selectable list
                                suggestion_texts = [f"{s['keyword_text']} ({s['avg_monthly_searches']:,} searches/mo, {s['competition']})" 
                                                   for s in suggestions[:50]]
                                selected_suggestions = st.multiselect(
                                    "Select keywords to analyze",
                                    suggestion_texts,
                                    default=suggestion_texts[:10] if len(suggestion_texts) >= 10 else suggestion_texts,
                                    help="Select keywords you want to analyze further"
                                )
                                
                                # Extract keyword text from selected
                                keywords_list = [s.split(" (")[0] for s in selected_suggestions]
                            else:
                                st.warning("No suggestions generated. Try different seed keywords.")
                        except Exception as e:
                            st.error(f"Error generating suggestions: {str(e)}")
                            import traceback
                            st.code(traceback.format_exc())
    
    st.markdown("---")
    
    # Geo targeting (optional)
    geo_targeting = st.checkbox("Specify geographic targeting", help="Override campaign location targeting. If unchecked and a campaign is selected, uses campaign's geo-targeting automatically.")
    geo_targets = None
    geo_display_names = []
    
    # Auto-detect campaign geo-targeting if checkbox is unchecked and campaign is selected
    # Store in session state to avoid re-fetching on every rerun
    campaign_geo_cache_key = f'campaign_geo_{selected_campaign_id}' if selected_campaign_id else None
    
    if not geo_targeting and selected_campaign_id:
        # Check cache first
        if campaign_geo_cache_key and campaign_geo_cache_key in st.session_state:
            geo_targets = st.session_state[campaign_geo_cache_key]
            if geo_targets:
                st.info(f"📍 Using campaign's geo-targeting ({len(geo_targets)} location(s))")
            else:
                st.info("📍 Campaign has no specific geo-targeting (using national/global data)")
        else:
            # Fetch campaign geo-targeting
            try:
                campaign_geo_targets = get_campaign_geo_targets(st.session_state.client, selected_account_id, selected_campaign_id)
                if campaign_geo_targets:
                    geo_targets = campaign_geo_targets
                    if campaign_geo_cache_key:
                        st.session_state[campaign_geo_cache_key] = campaign_geo_targets
                    st.info(f"📍 Using campaign's geo-targeting ({len(campaign_geo_targets)} location(s))")
                else:
                    geo_targets = None
                    if campaign_geo_cache_key:
                        st.session_state[campaign_geo_cache_key] = []
                    st.info("📍 Campaign has no specific geo-targeting (using national/global data)")
            except Exception as e:
                geo_targets = None
                if campaign_geo_cache_key:
                    st.session_state[campaign_geo_cache_key] = []
                st.info(f"📍 Could not detect campaign geo-targeting: {e}. Using national/global data.")
    
    if geo_targeting:
        geo_input = st.text_input(
            "Location (e.g., 'United States', 'Cleveland', 'New York')",
            placeholder="United States",
            help="Enter location name. This will override campaign geo-targeting. Leave blank for national data."
        )
        if geo_input:
            with st.spinner("Looking up location..."):
                try:
                    geo_targets = get_geo_target_constants(st.session_state.client, [geo_input])
                    if geo_targets:
                        geo_display_names = [geo_input]
                        st.success(f"✅ Location set: {geo_input}")
                    else:
                        st.warning(f"⚠️ Could not find location '{geo_input}'. Using national data.")
                        geo_targets = None
                except Exception as e:
                    st.warning(f"⚠️ Error looking up location: {e}. Using national data.")
                    geo_targets = None
    
    # Analyze button
    if st.button("🚀 Analyze Keywords", type="primary", use_container_width=True):
        if not selected_account_id:
            st.error("Please select an account.")
            return
        
        if not keywords_list:
            st.error("Please enter or load keywords to analyze.")
            return
        
        if len(keywords_list) > 50:
            st.warning(f"⚠️ You have {len(keywords_list)} keywords. Analyzing first 50 for performance.")
            keywords_list = keywords_list[:50]
        
        with st.spinner("🔍 Fetching Keyword Planner data..."):
            try:
                # Fetch Keyword Planner data
                planner_data = fetch_keyword_planner_data(
                    st.session_state.client,
                    selected_account_id,
                    keywords_list,
                    geo_targets=geo_targets
                )
                
                if not planner_data:
                    st.error("No data returned from Keyword Planner. Please check your keywords and try again.")
                    return
                
                st.success(f"✅ Fetched data for {len(planner_data)} keywords")
                
                # Optionally fetch current campaign performance for comparison
                current_performance = None
                if selected_campaign_id:
                    with st.spinner("📊 Fetching current campaign performance for comparison..."):
                        try:
                            data = fetch_comprehensive_campaign_data(
                                st.session_state.client,
                                selected_account_id,
                                campaign_id=selected_campaign_id,
                                date_range_days=30
                            )
                            
                            # Build performance dict by keyword
                            current_performance = {}
                            for kw in data.get('keywords', []):
                                keyword_text = kw['keyword']
                                current_performance[keyword_text] = {
                                    'avg_cpc': kw.get('avg_cpc', 0),
                                    'cost_per_conversion': kw.get('cost_per_conversion', 0),
                                    'conversions': kw.get('conversions', 0),
                                    'impressions': kw.get('impressions', 0),
                                    'clicks': kw.get('clicks', 0)
                                }
                        except Exception as e:
                            st.warning(f"Could not fetch campaign performance: {e}")
                
                # Format data for Claude prompt
                planner_formatted = format_keyword_planner_for_prompt(planner_data, current_performance)
                
                # Use modular prompt system for keyword research
                from prompt_loader import get_prompt_for_page
                try:
                    keyword_research_prompt = get_prompt_for_page('keyword_research')
                    # Replace placeholders
                    keyword_research_prompt = keyword_research_prompt.replace('{KEYWORD_PLANNER_DATA}', planner_formatted)
                    # Build geo context string
                    if geo_display_names:
                        geo_context = f"Location Targeting: {', '.join(geo_display_names)}"
                    elif geo_targets and selected_campaign_id and not geo_targeting:
                        geo_context = f"Location Targeting: Campaign's geo-targeting ({len(geo_targets)} location(s))"
                    elif geo_targets:
                        geo_context = f"Location Targeting: {len(geo_targets)} location(s)"
                    else:
                        geo_context = "Location Targeting: None (National/Global)"
                    keyword_research_prompt = keyword_research_prompt.replace('{GEO_TARGETING_CONTEXT}', geo_context)
                except Exception as e:
                    # Fallback to inline prompt if modular system fails
                    st.warning(f"⚠️  Using fallback prompt: {e}")
                    keyword_research_prompt = f"""# Keyword Research & Competitive Analysis

You are an elite Google Ads Senior Account Manager specializing in real estate investor marketing. Analyze the following Keyword Planner data and provide strategic recommendations.

## KEYWORD PLANNER DATA:

{planner_formatted}

## YOUR TASK:

Analyze this keyword data and provide:

### 1. Competition Analysis
- Which keywords are too competitive for typical real estate investor budgets?
- Which keywords have LOW competition (opportunities)?
- Which keywords show Quality Score problems (if current CPC data provided)?

### 2. Search Volume Assessment
- Which keywords have realistic volume for scaling?
- Which are micro-niches (can't scale)?
- Which have high volume but wrong intent?

### 3. Keyword Expansion Recommendations
- Prioritize keywords to ADD (low competition, high intent, good volume)
- Identify keywords to PAUSE (too competitive, wrong intent, low volume)
- Suggest related keywords to test

### 4. Budget Allocation Strategy
- How should budget be allocated across competition tiers?
- Expected impact of adding recommended keywords
- Risk assessment for high-competition keywords

### 5. Market Positioning
- What does this data tell us about market competition?
- Where are the opportunities vs. saturated areas?
- Geographic insights (if geo-targeting provided)

## OUTPUT FORMAT:

Structure your response as:

**COMPETITION ANALYSIS:**
[Analysis of competition levels]

**SEARCH VOLUME ASSESSMENT:**
[Volume analysis and scaling potential]

**KEYWORD EXPANSION RECOMMENDATIONS:**
- Priority 1 (Add Immediately): [List with rationale]
- Priority 2 (Test): [List with rationale]
- Priority 3 (Skip): [List with rationale]

**BUDGET ALLOCATION STRATEGY:**
[How to allocate budget across keywords]

**QUALITY SCORE ISSUES (if applicable):**
[Keywords with CPC >> suggested bid]

**MARKET POSITIONING:**
[Overall market insights]

Provide specific, actionable recommendations with expected impact.
"""
                
                # Get Claude analysis
                with st.spinner("🤖 Claude is analyzing keyword data..."):
                    try:
                        response = st.session_state.analyzer.claude.messages.create(
                            model=st.session_state.analyzer.model,
                            max_tokens=4096,
                            system="You are an expert Google Ads strategist specializing in real estate investor marketing.",
                            messages=[{"role": "user", "content": keyword_research_prompt}]
                        )
                        
                        recommendations = response.content[0].text
                        
                        # Store results
                        geo_targeting_display = None
                        if geo_targeting and geo_input:
                            geo_targeting_display = geo_input
                        elif geo_targets and selected_campaign_id and not geo_targeting:
                            geo_targeting_display = f"Campaign geo-targeting ({len(geo_targets)} location(s))"
                        elif geo_targets:
                            geo_targeting_display = f"{len(geo_targets)} location(s)"
                        
                        st.session_state['keyword_research_results'] = {
                            'recommendations': recommendations,
                            'planner_data': planner_data,
                            'keywords_analyzed': keywords_list,
                            'account_id': selected_account_id,
                            'account_display': selected_account_display,
                            'campaign_id': selected_campaign_id,
                            'campaign_display': selected_campaign_display if selected_campaign_id else None,
                            'geo_targeting': geo_targeting_display
                        }
                        
                        st.success("✅ Keyword Research Analysis Complete!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error during Claude analysis: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())
                
            except Exception as e:
                st.error(f"❌ Error fetching Keyword Planner data: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
    
    # Display results if available
    if 'keyword_research_results' in st.session_state and st.session_state['keyword_research_results']:
        results = st.session_state['keyword_research_results']
        
        st.markdown("---")
        st.markdown("### 📊 Keyword Planner Data")
        
        # Display planner data in a table
        import pandas as pd
        planner_df_data = []
        for keyword, data in results['planner_data'].items():
            planner_df_data.append({
                'Keyword': keyword,
                'Monthly Searches': f"{data.get('avg_monthly_searches', 0):,}",
                'Competition': data.get('competition', 'UNKNOWN'),
                'Suggested Bid Range': data.get('suggested_bid_range', 'N/A')
            })
        
        if planner_df_data:
            planner_df = pd.DataFrame(planner_df_data)
            st.dataframe(planner_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.markdown("### 🤖 Claude's Analysis & Recommendations")
        st.markdown(results['recommendations'])
        
        # Export options
        st.markdown("---")
        st.markdown("### 💾 Export Options")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save to PDF", use_container_width=True, key="keyword_research_pdf"):
                _save_keyword_research_to_pdf()
        with col2:
            if st.button("📤 Upload to Google Drive", use_container_width=True, key="keyword_research_drive"):
                _upload_keyword_research_to_drive()

def _save_keyword_research_to_pdf():
    """Helper function to save keyword research to PDF."""
    if 'keyword_research_results' not in st.session_state:
        st.error("No keyword research to save. Please run an analysis first.")
        return
    
    results = st.session_state['keyword_research_results']
    account_name = results['account_display'].split(" (")[0] if results['account_display'] else "Account"
    campaign_name = results['campaign_display'].split(" (")[0] if results['campaign_display'] and results['campaign_display'] != "All Campaigns" else "Keyword Research"
    
    try:
        from real_estate_analyzer import create_pdf_report
        import tempfile
        
        temp_filepath = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf').name
        
        # Create PDF with keyword research content
        title = f"Keyword Research Report - {account_name}"
        if results.get('geo_targeting'):
            title += f" ({results['geo_targeting']})"
        
        content = f"""
KEYWORD RESEARCH REPORT
{account_name}
{datetime.now().strftime('%B %d, %Y')}

Keywords Analyzed: {len(results['keywords_analyzed'])}
"""
        if results.get('campaign_display'):
            content += f"Campaign: {campaign_name}\n"
        if results.get('geo_targeting'):
            content += f"Location: {results['geo_targeting']}\n"
        
        content += "\n" + "="*80 + "\n\n"
        content += "KEYWORD PLANNER DATA\n"
        content += "="*80 + "\n\n"
        
        # Add planner data table
        for keyword, data in results['planner_data'].items():
            content += f"Keyword: {keyword}\n"
            content += f"  Monthly Searches: {data.get('avg_monthly_searches', 0):,}\n"
            content += f"  Competition: {data.get('competition', 'UNKNOWN')}\n"
            content += f"  Suggested Bid Range: {data.get('suggested_bid_range', 'N/A')}\n\n"
        
        content += "\n" + "="*80 + "\n\n"
        content += "CLAUDE'S ANALYSIS & RECOMMENDATIONS\n"
        content += "="*80 + "\n\n"
        content += results['recommendations']
        
        if create_pdf_report(
            content,
            account_name,
            campaign_name,
            f"Keyword Research - {len(results['keywords_analyzed'])} keywords",
            temp_filepath
        ):
            # Download PDF
            with open(temp_filepath, 'rb') as pdf_file:
                st.download_button(
                    label="📥 Download PDF",
                    data=pdf_file.read(),
                    file_name=f"{account_name}_KeywordResearch_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    key="download_keyword_research_pdf"
                )
            os.unlink(temp_filepath)
        else:
            st.error("❌ Failed to create PDF")
    except Exception as e:
        st.error(f"❌ Error creating PDF: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

def _upload_keyword_research_to_drive():
    """Helper function to upload keyword research to Google Drive."""
    if 'keyword_research_results' not in st.session_state:
        st.error("No keyword research to upload. Please run an analysis first.")
        return
    
    results = st.session_state['keyword_research_results']
    account_name = results['account_display'].split(" (")[0] if results['account_display'] else "Account"
    campaign_name = results['campaign_display'].split(" (")[0] if results['campaign_display'] and results['campaign_display'] != "All Campaigns" else "Keyword Research"
    
    try:
        from real_estate_analyzer import create_pdf_report, get_drive_service, upload_to_drive
        import tempfile
        
        temp_filepath = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf').name
        
        # Create PDF (same as save function)
        title = f"Keyword Research Report - {account_name}"
        if results.get('geo_targeting'):
            title += f" ({results['geo_targeting']})"
        
        content = f"""
KEYWORD RESEARCH REPORT
{account_name}
{datetime.now().strftime('%B %d, %Y')}

Keywords Analyzed: {len(results['keywords_analyzed'])}
"""
        if results.get('campaign_display'):
            content += f"Campaign: {campaign_name}\n"
        if results.get('geo_targeting'):
            content += f"Location: {results['geo_targeting']}\n"
        
        content += "\n" + "="*80 + "\n\n"
        content += "KEYWORD PLANNER DATA\n"
        content += "="*80 + "\n\n"
        
        for keyword, data in results['planner_data'].items():
            content += f"Keyword: {keyword}\n"
            content += f"  Monthly Searches: {data.get('avg_monthly_searches', 0):,}\n"
            content += f"  Competition: {data.get('competition', 'UNKNOWN')}\n"
            content += f"  Suggested Bid Range: {data.get('suggested_bid_range', 'N/A')}\n\n"
        
        content += "\n" + "="*80 + "\n\n"
        content += "CLAUDE'S ANALYSIS & RECOMMENDATIONS\n"
        content += "="*80 + "\n\n"
        content += results['recommendations']
        
        if not create_pdf_report(
            content,
            account_name,
            campaign_name,
            f"Keyword Research - {len(results['keywords_analyzed'])} keywords",
            temp_filepath
        ):
            st.error("❌ Failed to create PDF for upload")
            return
        
        # Get Drive service
        from real_estate_analyzer import get_drive_service, upload_to_drive
        drive_service = get_drive_service()
        if not drive_service:
            st.error("❌ Could not authenticate with Google Drive. Please check your credentials.")
            os.unlink(temp_filepath)
            return
        
        # Use optimization reports folder (or create a keyword research folder)
        folder_id = DRIVE_FOLDER_IDS.get('optimization_reports')  # Use same folder for now
        
        # Upload file
        filename = f"{account_name}_KeywordResearch_{datetime.now().strftime('%Y%m%d')}.pdf"
        file_id, file_link = upload_to_drive(drive_service, temp_filepath, filename, folder_id)
        
        # Clean up temp file
        os.unlink(temp_filepath)
        
        if file_id and file_link:
            st.success(f"✅ Successfully uploaded to Google Drive!")
            st.markdown(f"📁 [View file in Google Drive]({file_link})")
        else:
            st.error("❌ Failed to upload to Google Drive")
    except Exception as e:
        st.error(f"❌ Error uploading to Google Drive: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

def show_create_campaign():
    """Create new campaign page."""
    st.header("🎯 Create New Campaign")
    st.markdown("Create a new Google Ads campaign for a sub-account.")
    
    mcc_id = os.getenv("GOOGLE_ADS_CUSTOMER_ID")
    if not mcc_id:
        st.error("MCC Customer ID not found in environment variables.")
        st.stop()
    
    # Get sub-accounts
    try:
        sub_accounts = get_sub_accounts(st.session_state.client, mcc_id)
        if not sub_accounts:
            st.warning("No sub-accounts found. Please create a sub-account first.")
            st.stop()
        
        account_options = {acc['display']: acc['id'] for acc in sub_accounts}
        selected_account_display = st.selectbox("Select Sub-Account", list(account_options.keys()))
        selected_account_id = account_options[selected_account_display]
        
    except Exception as e:
        st.error(f"Error loading sub-accounts: {e}")
        st.stop()
    
    # Campaign creation form
    with st.form("create_campaign_form"):
        campaign_name = st.text_input("Campaign Name *", placeholder="e.g., Motivated Seller Campaign - Q1 2025")
        budget_amount = st.number_input("Daily Budget ($) *", min_value=1.0, max_value=10000.0, value=50.0, step=1.0)
        
        st.markdown("### Campaign Settings")
        st.info("""
        **Default Settings:**
        - Bidding Strategy: Maximize Clicks
        - Network: Google Search only
        - Location Targeting: Presence Only
        - Status: Paused (you can enable it after setup)
        - Negative Keywords: PPCL List will be applied
        """)
        
        submitted = st.form_submit_button("Create Campaign", type="primary", use_container_width=True)
        
        if submitted:
            if not campaign_name:
                st.error("Please enter a campaign name.")
            else:
                with st.spinner("Creating campaign..."):
                    try:
                        campaign_id = create_campaign(
                            st.session_state.client,
                            selected_account_id,
                            campaign_name,
                            budget_amount
                        )
                        
                        if campaign_id:
                            st.success(f"✅ Campaign created successfully!")
                            st.markdown(f"**Campaign ID:** `{campaign_id}`")
                            st.info("💡 The campaign has been created in PAUSED status. You can enable it after adding ad groups, ads, and keywords.")
                    except Exception as e:
                        st.error(f"❌ Error creating campaign: {str(e)}")


def show_help_chat():
    """Help & Documentation chat page."""
    st.header("❓ Help Center")
    st.markdown("Ask questions about the app and get instant answers from the documentation.")
    
    # Initialize chat history in session state
    if 'help_chat_history' not in st.session_state:
        st.session_state.help_chat_history = []
    
    # Load documentation (cache in session state)
    if 'help_docs' not in st.session_state:
        with st.spinner("Loading documentation..."):
            st.session_state.help_docs = load_documentation()
    
    # Check if there's a pending question to process
    if 'pending_help_question' in st.session_state and st.session_state.pending_help_question:
        user_question = st.session_state.pending_help_question
        st.session_state.pending_help_question = None  # Clear it
        
        # Add user question to chat history if not already there
        if not st.session_state.help_chat_history or st.session_state.help_chat_history[-1].get("content") != user_question:
            st.session_state.help_chat_history.append({
                "role": "user",
                "content": user_question
            })
        
        # Process the question
        _process_help_question(user_question, st.session_state.help_docs)
        st.rerun()
    
    # Display suggested questions
    st.markdown("### 💡 Suggested Questions")
    suggested_questions = get_suggested_questions()
    
    # Create columns for suggested questions
    cols = st.columns(3)
    for idx, question in enumerate(suggested_questions[:9]):  # Show first 9 in 3 columns
        col_idx = idx % 3
        with cols[col_idx]:
            if st.button(question, key=f"suggested_{idx}", use_container_width=True):
                # Set pending question to process
                st.session_state.pending_help_question = question
                st.rerun()
    
    # Show more suggestions in expander
    if len(suggested_questions) > 9:
        with st.expander("More Suggested Questions"):
            for idx, question in enumerate(suggested_questions[9:], start=9):
                if st.button(question, key=f"suggested_{idx}", use_container_width=True):
                    # Set pending question to process
                    st.session_state.pending_help_question = question
                    st.rerun()
    
    st.markdown("---")
    
    # Display chat history
    if st.session_state.help_chat_history:
        st.markdown("### 💬 Chat History")
        for idx, message in enumerate(st.session_state.help_chat_history):
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.write(message["content"])
            else:
                with st.chat_message("assistant"):
                    st.markdown(message["content"])
                    if "sources" in message:
                        st.caption(f"📚 Sources: {', '.join(message['sources'])}")
    
    # Chat input
    st.markdown("---")
    user_question = st.chat_input("Ask a question about the app...")
    
    if user_question:
        # Set pending question to process
        st.session_state.pending_help_question = user_question
        st.rerun()


def _process_help_question(user_question: str, help_docs: dict):
    """Process a help question and get answer from Claude."""
    # Find relevant documentation
    with st.spinner("🔍 Searching documentation..."):
        relevant_docs = find_relevant_docs(user_question, help_docs)
        
        if not relevant_docs:
            # No relevant docs found
            st.session_state.help_chat_history.append({
                "role": "assistant",
                "content": "I couldn't find relevant information in the documentation for your question. Please try rephrasing or ask about a different topic.",
                "sources": []
            })
            return
        
        # Format docs for prompt
        formatted_docs = format_docs_for_prompt(relevant_docs)
        citations = get_document_citations(relevant_docs)
        
        # Create prompt
        help_prompt = create_help_prompt(user_question, formatted_docs)
        
        # Get answer from Claude (use Haiku for faster/cheaper responses)
        with st.spinner("🤖 Getting answer from Claude..."):
            try:
                # Use Haiku model for help queries (faster and cheaper)
                haiku_model = "claude-3-5-haiku-20241022"
                
                response = st.session_state.analyzer.claude.messages.create(
                    model=haiku_model,
                    max_tokens=2048,
                    system="You are a helpful documentation assistant. Provide clear, concise answers based on the documentation provided.",
                    messages=[{"role": "user", "content": help_prompt}]
                )
                
                answer = response.content[0].text
                
                # Add assistant response to chat history
                st.session_state.help_chat_history.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": citations
                })
                
            except Exception as e:
                st.error(f"❌ Error getting answer: {str(e)}")
                st.session_state.help_chat_history.append({
                    "role": "assistant",
                    "content": f"Sorry, I encountered an error: {str(e)}",
                    "sources": []
                })
    
    # Clear chat button
    if st.session_state.help_chat_history:
        st.markdown("---")
        if st.button("🗑️ Clear Chat History", type="secondary"):
            st.session_state.help_chat_history = []
            st.rerun()


if __name__ == "__main__":
    main()

