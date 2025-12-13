"""
Real Estate Google Ads Analyzer - Streamlit Web App
Modern web interface for Google Ads campaign analysis and management
"""

import streamlit as st
import os
import sys
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from authenticate import get_client
from account_manager import select_account_interactive, select_campaign_interactive, list_customer_accounts
from account_campaign_manager import get_sub_accounts, create_sub_account, create_campaign, US_TIMEZONES
from real_estate_analyzer import RealEstateAnalyzer
from comprehensive_data_fetcher import fetch_comprehensive_campaign_data, format_campaign_data_for_prompt
from keyword_planner_fetcher import fetch_keyword_planner_data, format_keyword_planner_for_prompt, get_geo_target_for_campaign, fetch_campaign_keywords

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
    }
    
    /* Sidebar Navigation Buttons */
    .nav-button {
        width: 100%;
        padding: 0.75rem 1rem;
        margin: 0.25rem 0;
        border: none;
        border-radius: 8px;
        background-color: transparent;
        color: rgba(255, 255, 255, 0.9);
        font-size: 0.95rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: left;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .nav-button:hover {
        background-color: rgba(255, 255, 255, 0.1);
        transform: translateX(4px);
    }
    
    .nav-button.active {
        background-color: #FF4444;
        color: white;
        font-weight: 600;
    }
    
    .nav-button.active:hover {
        background-color: #FF6666;
        transform: translateX(4px);
    }
    
    .nav-icon {
        font-size: 1.2rem;
        width: 24px;
        text-align: center;
    }
    
    /* Hide Streamlit's default button styling for nav buttons */
    div[data-testid="stSidebar"] .nav-button-container button {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
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
if 'current_page' not in st.session_state:
    st.session_state.current_page = "📊 Campaign Analysis"

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
        
        # Navigation buttons with icons
        nav_items = [
            ("📊 Campaign Analysis", "📊"),
            ("📝 Ad Copy Optimization", "📝"),
            ("🔍 Keyword Research", "🔍"),
            ("📄 Biweekly Reports", "📄"),
            ("💬 Ask Claude", "💬"),
            ("➕ Create Account", "➕"),
            ("🎯 Create Campaign", "🎯")
        ]
        
        # Create navigation buttons
        for page_name, icon in nav_items:
            # Use .get() with default to avoid KeyError if not initialized yet
            current_page = st.session_state.get('current_page', "📊 Campaign Analysis")
            is_active = current_page == page_name
            button_label = page_name
            
            # Use button with custom styling
            if st.button(
                button_label,
                key=f"nav_{page_name}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.current_page = page_name
                st.rerun()
        
        # Add CSS to style navigation buttons with hover effects
        st.markdown("""
        <style>
        /* Style all sidebar buttons */
        div[data-testid="stSidebar"] [data-testid="stButton"] > button {
            width: 100% !important;
            padding: 0.75rem 1rem !important;
            margin: 0.25rem 0 !important;
            border: none !important;
            border-radius: 8px !important;
            background-color: transparent !important;
            color: rgba(255, 255, 255, 0.9) !important;
            font-size: 0.95rem !important;
            font-weight: 500 !important;
            text-align: left !important;
            transition: all 0.3s ease !important;
            box-shadow: none !important;
            justify-content: flex-start !important;
        }
        
        /* Hover effect for inactive buttons */
        div[data-testid="stSidebar"] [data-testid="stButton"] > button[kind="secondary"]:hover {
            background-color: rgba(255, 255, 255, 0.1) !important;
            transform: translateX(4px) !important;
            color: white !important;
        }
        
        /* Active button styling (primary type) */
        div[data-testid="stSidebar"] [data-testid="stButton"] > button[kind="primary"] {
            background-color: #FF4444 !important;
            color: white !important;
            font-weight: 600 !important;
        }
        
        /* Hover effect for active button */
        div[data-testid="stSidebar"] [data-testid="stButton"] > button[kind="primary"]:hover {
            background-color: #FF6666 !important;
            transform: translateX(4px) !important;
        }
        
        /* Remove focus outline */
        div[data-testid="stSidebar"] [data-testid="stButton"] > button:focus {
            box-shadow: none !important;
            outline: none !important;
        }
        
        /* Ensure buttons don't have default Streamlit styling */
        div[data-testid="stSidebar"] [data-testid="stButton"] > button:not([kind="primary"]) {
            background-color: transparent !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
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
    
    # Route to appropriate page
    # Use .get() with default to avoid KeyError if not initialized yet
    page = st.session_state.get('current_page', "📊 Campaign Analysis")
    if page == "📊 Campaign Analysis":
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

def show_keyword_research():
    """Keyword Research page."""
    st.header("🔍 Keyword Research")
    st.markdown("Research keywords, competition, and search volume using Google Keyword Planner API.")
    
    # Initialize session state for keyword research
    if 'keyword_research_results' not in st.session_state:
        st.session_state.keyword_research_results = None
    if 'keyword_research_claude_recommendations' not in st.session_state:
        st.session_state.keyword_research_claude_recommendations = None
    
    # Account selection (optional - for geo targeting)
    st.markdown("### Step 1: Select Account (Optional)")
    st.markdown("Select an account to use its campaign's geo targeting, or leave blank for general research.")
    
    col1, col2 = st.columns(2)
    with col1:
        try:
            accounts = list_customer_accounts(st.session_state.client)
            if accounts:
                account_options = {acc['descriptive_name']: acc['customer_id'] for acc in accounts}
                selected_account_name = st.selectbox(
                    "Select Account",
                    ["None (General Research)"] + list(account_options.keys()),
                    key="kw_research_account"
                )
                selected_account_id = account_options.get(selected_account_name) if selected_account_name != "None (General Research)" else None
            else:
                st.warning("No accounts found.")
                selected_account_id = None
        except Exception as e:
            st.error(f"Error loading accounts: {str(e)}")
            selected_account_id = None
    
    # Campaign selection (for loading keywords and geo targeting)
    campaign_id = None
    geo_targets = None
    with col2:
        if selected_account_id:
            try:
                campaigns = []
                ga_service = st.session_state.client.get_service("GoogleAdsService")
                customer_id_numeric = selected_account_id.replace("-", "")
                query = """
                    SELECT
                        campaign.id,
                        campaign.name,
                        campaign.status
                    FROM campaign
                    WHERE campaign.status != 'REMOVED'
                    ORDER BY campaign.name
                """
                response = ga_service.search(customer_id=customer_id_numeric, query=query)
                for row in response:
                    campaigns.append({
                        'id': row.campaign.id,
                        'name': row.campaign.name
                    })
                
                if campaigns:
                    campaign_options = {f"{c['name']} (ID: {c['id']})": c['id'] for c in campaigns}
                    selected_campaign_display = st.selectbox(
                        "Select Campaign",
                        ["None"] + list(campaign_options.keys()),
                        key="kw_research_campaign"
                    )
                    if selected_campaign_display != "None":
                        campaign_id = campaign_options[selected_campaign_display]
                        # Get geo targets from campaign (will be overridden if manual locations specified)
                        geo_targets = get_geo_target_for_campaign(st.session_state.client, selected_account_id, campaign_id)
            except Exception as e:
                st.warning(f"Could not load campaigns: {str(e)}")
    
    st.markdown("---")
    
    # Geographic Locations Override
    st.markdown("### Step 2: Geographic Locations (Optional)")
    specify_geo_locations = st.checkbox(
        "Specifying Geographic Locations",
        key="kw_specify_geo",
        help="Check this to manually specify geographic locations that will override campaign geo targeting"
    )
    
    manual_geo_targets = None
    if specify_geo_locations:
        geo_input = st.text_area(
            "Enter Geographic Locations",
            placeholder="Enter location names or geo target constants (one per line)\nExample:\nUnited States\ngeoTargetConstants/2840\nNew York",
            height=100,
            key="kw_manual_geo"
        )
        if geo_input.strip():
            # Parse geo targets - can be location names or geo target constants
            geo_lines = [line.strip() for line in geo_input.split('\n') if line.strip()]
            manual_geo_targets = []
            for geo_line in geo_lines:
                if geo_line.startswith("geoTargetConstants/"):
                    manual_geo_targets.append(geo_line)
                else:
                    # For location names, we'd need to look them up, but for now just store as-is
                    # The API will handle validation
                    manual_geo_targets.append(geo_line)
            if manual_geo_targets:
                geo_targets = manual_geo_targets  # Override campaign geo targets
    
    st.markdown("---")
    
    # Keyword input - with option to load from campaign
    st.markdown("### Step 3: Keywords to Research")
    
    load_from_campaign = st.checkbox(
        "Load Keywords from Selected Campaign",
        key="kw_load_from_campaign",
        help="Check this to automatically load all keywords from the selected campaign"
    )
    
    campaign_keywords_loaded = False
    if load_from_campaign and campaign_id and selected_account_id:
        try:
            with st.spinner("Loading keywords from campaign..."):
                campaign_keywords = fetch_campaign_keywords(st.session_state.client, selected_account_id, campaign_id)
                if campaign_keywords:
                    keyword_input = "\n".join(campaign_keywords)
                    st.session_state.kw_research_input = keyword_input
                    campaign_keywords_loaded = True
                    st.success(f"✅ Loaded {len(campaign_keywords)} keywords from campaign")
                else:
                    st.warning("No keywords found in the selected campaign.")
        except Exception as e:
            st.error(f"❌ Error loading campaign keywords: {str(e)}")
    
    keyword_input = st.text_area(
        "Keywords to Research",
        placeholder="sell house fast\ncash for houses\nwe buy houses\n\nOr check 'Load Keywords from Selected Campaign' to load from a campaign",
        height=150,
        key="kw_research_input",
        value=st.session_state.get('kw_research_input', '')
    )
    
    # Research options
    col1, col2 = st.columns(2)
    with col1:
        include_claude_analysis = st.checkbox("Get Claude AI Recommendations", value=True, key="kw_include_claude")
    with col2:
        max_related_keywords = st.number_input("Max Related Keywords", min_value=5, max_value=50, value=20, key="kw_max_related")
    
    # Research button
    if st.button("🔍 Research Keywords", type="primary", use_container_width=True):
        if not keyword_input.strip():
            st.error("Please enter at least one keyword to research.")
        else:
            # Parse keywords
            keywords_list = []
            for line in keyword_input.split('\n'):
                line = line.strip()
                if ',' in line:
                    keywords_list.extend([kw.strip() for kw in line.split(',') if kw.strip()])
                elif line:
                    keywords_list.append(line)
            
            if not keywords_list:
                st.error("No valid keywords found. Please enter keywords.")
            else:
                # Determine customer ID for API call
                api_customer_id = selected_account_id if selected_account_id else os.getenv("GOOGLE_ADS_CUSTOMER_ID")
                if not api_customer_id:
                    st.error("Please select an account or set GOOGLE_ADS_CUSTOMER_ID in environment variables.")
                else:
                    with st.spinner(f"🔍 Researching {len(keywords_list)} keyword(s)..."):
                        try:
                            # Fetch keyword planner data
                            planner_data = fetch_keyword_planner_data(
                                st.session_state.client,
                                api_customer_id,
                                keywords_list,
                                geo_targets=geo_targets,
                                language_code="en"
                            )
                            
                            st.session_state.keyword_research_results = {
                                'planner_data': planner_data,
                                'seed_keywords': keywords_list,
                                'account_id': api_customer_id,
                                'campaign_id': campaign_id
                            }
                            
                            st.success(f"✅ Found data for {len(planner_data.get('keywords', []))} keywords and {len(planner_data.get('related_keywords', []))} related keywords!")
                            
                            # Get Claude recommendations if requested
                            if include_claude_analysis:
                                with st.spinner("🤖 Getting Claude AI recommendations..."):
                                    try:
                                        # Format data for Claude
                                        planner_text = format_keyword_planner_for_prompt(planner_data)
                                        
                                        # Create prompt for Claude with focus on search volume and competition
                                        keyword_prompt = f"""You are a Google Ads keyword research expert specializing in real estate investor campaigns targeting motivated and distressed home sellers.

Analyze the following Keyword Planner data and provide strategic recommendations:

{planner_text}

**Your Task - Focus on Search Volume and Competition Analysis:**

1. **Low Search Volume Keywords** (< 1,000 searches/month):
   - Identify all keywords with low search volume
   - Assess if they're still valuable (high intent, low competition)
   - Recommend whether to keep, pause, or expand these keywords
   - Note: Low volume keywords often have higher conversion rates but limited reach

2. **High Search Volume Keywords** (> 10,000 searches/month):
   - Identify all keywords with high search volume
   - Assess competition levels and bid requirements
   - Determine if they're too broad for motivated seller intent
   - Recommend match type strategy (exact vs phrase vs broad)

3. **Low Competition Keywords**:
   - Identify keywords with LOW competition
   - Highlight opportunities for lower CPCs and easier ranking
   - Recommend bid adjustments and budget allocation
   - These are prime opportunities for expansion

4. **High Competition Keywords**:
   - Identify keywords with HIGH competition
   - Assess if the suggested bids are within budget
   - Determine if Quality Score improvements could help
   - Recommend whether to continue bidding or pause

5. **Optimal Keywords** (Medium volume + Low-Medium competition):
   - Identify the "sweet spot" keywords (1K-10K searches/month, LOW-MEDIUM competition)
   - These are your best opportunities for scaling
   - Recommend bid ranges and expected performance

6. **Keyword Categorization Summary**:
   - Create a clear summary table categorizing keywords by:
     * Low Search Volume + Low Competition (Keep/Expand)
     * Low Search Volume + High Competition (Consider pausing)
     * High Search Volume + Low Competition (Scale aggressively)
     * High Search Volume + High Competition (Monitor closely)
     * Medium Search Volume + Low Competition (Best opportunities)

7. **Action Items**: Provide 3-5 specific, actionable recommendations based on your analysis

Format your response clearly with sections for each analysis area. Be specific about which keywords fall into each category."""
                                        
                                        # Get Claude analysis
                                        if 'analyzer' in st.session_state and st.session_state.analyzer:
                                            try:
                                                claude_response = st.session_state.analyzer.claude.messages.create(
                                                    model=st.session_state.analyzer.model,
                                                    max_tokens=2000,
                                                    messages=[
                                                        {"role": "user", "content": keyword_prompt}
                                                    ]
                                                )
                                                recommendations = claude_response.content[0].text
                                                st.session_state.keyword_research_claude_recommendations = recommendations
                                            except Exception as claude_error:
                                                st.warning(f"Could not get Claude recommendations: {str(claude_error)}")
                                                st.session_state.keyword_research_claude_recommendations = None
                                        else:
                                            st.warning("Claude analyzer not initialized. Skipping AI recommendations.")
                                    except Exception as e:
                                        st.warning(f"Could not get Claude recommendations: {str(e)}")
                                        st.session_state.keyword_research_claude_recommendations = None
                            
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Error researching keywords: {str(e)}")
                            import traceback
                            st.code(traceback.format_exc())
    
    # Display results
    if st.session_state.keyword_research_results:
        st.markdown("---")
        st.markdown("### 📊 Research Results")
        
        planner_data = st.session_state.keyword_research_results['planner_data']
        
        # Display seed keywords data
        if planner_data.get('keywords'):
            st.markdown("#### Seed Keywords Analysis")
            
            # Prepare data for table
            keywords_table_data = []
            for kw in planner_data['keywords']:
                competition_badge = ""
                if kw.get('competition') == 'LOW':
                    competition_badge = "🟢 LOW"
                elif kw.get('competition') == 'MEDIUM':
                    competition_badge = "🟡 MEDIUM"
                elif kw.get('competition') == 'HIGH':
                    competition_badge = "🔴 HIGH"
                else:
                    competition_badge = "⚪ UNKNOWN"
                
                bid_range = ""
                if kw.get('low_top_of_page_bid') and kw.get('high_top_of_page_bid'):
                    bid_range = f"${kw['low_top_of_page_bid']:.2f} - ${kw['high_top_of_page_bid']:.2f}"
                elif kw.get('low_top_of_page_bid'):
                    bid_range = f"${kw['low_top_of_page_bid']:.2f}+"
                else:
                    bid_range = "N/A"
                
                keywords_table_data.append({
                    "Keyword": kw['keyword_text'],
                    "Monthly Searches": f"{kw.get('avg_monthly_searches', 0):,}" if kw.get('avg_monthly_searches') else "N/A",
                    "Competition": competition_badge,
                    "Suggested Bid Range": bid_range
                })
            
            df_keywords = pd.DataFrame(keywords_table_data)
            st.dataframe(df_keywords, use_container_width=True, hide_index=True)
        
        # Display related keywords
        if planner_data.get('related_keywords'):
            st.markdown("#### Related Keyword Opportunities")
            st.markdown(f"Found {len(planner_data['related_keywords'])} related keywords. Showing top {min(max_related_keywords, len(planner_data['related_keywords']))}:")
            
            related_table_data = []
            for kw in planner_data['related_keywords'][:max_related_keywords]:
                competition_badge = ""
                if kw.get('competition') == 'LOW':
                    competition_badge = "🟢 LOW"
                elif kw.get('competition') == 'MEDIUM':
                    competition_badge = "🟡 MEDIUM"
                elif kw.get('competition') == 'HIGH':
                    competition_badge = "🔴 HIGH"
                else:
                    competition_badge = "⚪ UNKNOWN"
                
                bid_range = ""
                if kw.get('low_top_of_page_bid') and kw.get('high_top_of_page_bid'):
                    bid_range = f"${kw['low_top_of_page_bid']:.2f} - ${kw['high_top_of_page_bid']:.2f}"
                elif kw.get('low_top_of_page_bid'):
                    bid_range = f"${kw['low_top_of_page_bid']:.2f}+"
                else:
                    bid_range = "N/A"
                
                related_table_data.append({
                    "Keyword": kw['keyword_text'],
                    "Monthly Searches": f"{kw.get('avg_monthly_searches', 0):,}" if kw.get('avg_monthly_searches') else "N/A",
                    "Competition": competition_badge,
                    "Suggested Bid Range": bid_range
                })
            
            df_related = pd.DataFrame(related_table_data)
            st.dataframe(df_related, use_container_width=True, hide_index=True)
        
        # Display Claude recommendations
        if st.session_state.keyword_research_claude_recommendations:
            st.markdown("---")
            st.markdown("### 🤖 Claude AI Recommendations")
            st.markdown(st.session_state.keyword_research_claude_recommendations)
        
        # Export options
        st.markdown("---")
        st.markdown("### 💾 Export Results")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📥 Download as CSV", use_container_width=True):
                try:
                    import pandas as pd
                    import io
                    
                    # Combine all keywords
                    all_keywords = []
                    if planner_data.get('keywords'):
                        for kw in planner_data['keywords']:
                            all_keywords.append({
                                "Type": "Seed Keyword",
                                "Keyword": kw['keyword_text'],
                                "Monthly Searches": kw.get('avg_monthly_searches', 0) or 0,
                                "Competition": kw.get('competition', 'UNKNOWN'),
                                "Low Bid": kw.get('low_top_of_page_bid', 0) or 0,
                                "High Bid": kw.get('high_top_of_page_bid', 0) or 0
                            })
                    if planner_data.get('related_keywords'):
                        for kw in planner_data['related_keywords']:
                            all_keywords.append({
                                "Type": "Related Keyword",
                                "Keyword": kw['keyword_text'],
                                "Monthly Searches": kw.get('avg_monthly_searches', 0) or 0,
                                "Competition": kw.get('competition', 'UNKNOWN'),
                                "Low Bid": kw.get('low_top_of_page_bid', 0) or 0,
                                "High Bid": kw.get('high_top_of_page_bid', 0) or 0
                            })
                    
                    df_export = pd.DataFrame(all_keywords)
                    csv = df_export.to_csv(index=False)
                    st.download_button(
                        label="⬇️ Download CSV",
                        data=csv,
                        file_name=f"keyword_research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                except Exception as e:
                    st.error(f"❌ Error creating CSV: {str(e)}")
        
        with col2:
            if st.button("📤 Upload to Google Drive", use_container_width=True):
                try:
                    from real_estate_analyzer import upload_to_drive, get_drive_service
                    import tempfile
                    import pandas as pd
                    
                    # Create CSV file
                    all_keywords = []
                    if planner_data.get('keywords'):
                        for kw in planner_data['keywords']:
                            all_keywords.append({
                                "Type": "Seed Keyword",
                                "Keyword": kw['keyword_text'],
                                "Monthly Searches": kw.get('avg_monthly_searches', 0) or 0,
                                "Competition": kw.get('competition', 'UNKNOWN'),
                                "Low Bid": kw.get('low_top_of_page_bid', 0) or 0,
                                "High Bid": kw.get('high_top_of_page_bid', 0) or 0
                            })
                    if planner_data.get('related_keywords'):
                        for kw in planner_data['related_keywords']:
                            all_keywords.append({
                                "Type": "Related Keyword",
                                "Keyword": kw['keyword_text'],
                                "Monthly Searches": kw.get('avg_monthly_searches', 0) or 0,
                                "Competition": kw.get('competition', 'UNKNOWN'),
                                "Low Bid": kw.get('low_top_of_page_bid', 0) or 0,
                                "High Bid": kw.get('high_top_of_page_bid', 0) or 0
                            })
                    
                    df_export = pd.DataFrame(all_keywords)
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='w')
                    df_export.to_csv(temp_file.name, index=False)
                    temp_file.close()
                    
                    # Upload to Google Drive
                    folder_id = "1kMShfz38NWRkBK99GzwjDJTzyWi3TXFW"  # Using Q&A folder for now, can create dedicated folder
                    drive_service = get_drive_service()
                    file_name = f"keyword_research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    
                    uploaded_file_id = upload_to_drive(drive_service, temp_file.name, file_name, folder_id)
                    os.unlink(temp_file.name)
                    
                    if uploaded_file_id:
                        st.success(f"✅ Uploaded to Google Drive!")
                        st.markdown(f"**File:** {file_name}")
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

if __name__ == "__main__":
    main()

