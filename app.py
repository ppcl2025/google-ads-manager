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
        st.image("https://via.placeholder.com/200x60/1a5490/ffffff?text=Google+Ads", use_container_width=True)
        st.markdown("---")
        
        page = st.radio(
            "Navigation",
            [
                "📊 Campaign Analysis",
                "📝 Ad Copy Optimization",
                "📄 Biweekly Reports",
                "💬 Ask Claude",
                "➕ Create Account",
                "🎯 Create Campaign"
            ],
            label_visibility="collapsed"
        )
        
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
    if page == "📊 Campaign Analysis":
        show_comprehensive_analysis()
    elif page == "📝 Ad Copy Optimization":
        show_ad_copy_optimization()
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
        
        # Save options (always visible when results exist)
        st.markdown("---")
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
                
                # Step 3: Call Claude (pass pre-fetched data to avoid re-fetching)
                status_text.info("🔄 Step 3/3: Claude is analyzing your campaign data... (this may take 1-2 minutes)")
                
                try:
                    recommendations = st.session_state.analyzer.analyze(
                        customer_id=selected_account_id,
                        campaign_id=selected_campaign_id,
                        date_range_days=date_range,
                        optimization_goals=optimization_goals,
                        prompt_type='full',
                        pre_fetched_data=data  # Pass pre-fetched data
                    )
                    
                    # Store results in session state so they persist across button clicks
                    st.session_state['analysis_results'] = {
                        'recommendations': recommendations,
                        'account_id': selected_account_id,
                        'account_display': selected_account_display,
                        'campaign_id': selected_campaign_id,
                        'campaign_display': selected_campaign_display,
                        'date_range': date_range
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
                account_options = {f"{acc['name']} ({acc['id']})": acc['id'] for acc in accounts}
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
        st.markdown(results['report_content'])
        
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
        
        if create_biweekly_report_pdf(results['report_content'], account_name, campaign_name, results['date_range'], temp_filepath):
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
            st.error("❌ Failed to create PDF")
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
        if not create_biweekly_report_pdf(results['report_content'], account_name, campaign_name, results['date_range'], temp_filepath):
            st.error("❌ Failed to create PDF for upload")
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
                        
            except Exception as e:
                st.error(f"❌ Error generating report: {str(e)}")

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

