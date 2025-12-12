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
    page_icon="🏠",
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
    st.markdown('<h1 class="main-header">🏠 Real Estate Google Ads Analyzer</h1>', unsafe_allow_html=True)
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
    
    # Run analysis button
    if st.button("🚀 Run Comprehensive Analysis", type="primary", use_container_width=True):
        if not selected_account_id:
            st.error("Please select an account.")
            return
        
        with st.spinner("🤖 Claude is analyzing your campaign data..."):
            try:
                recommendations = st.session_state.analyzer.analyze(
                    customer_id=selected_account_id,
                    campaign_id=selected_campaign_id,
                    date_range_days=date_range,
                    optimization_goals=optimization_goals,
                    prompt_type='full'
                )
                
                st.success("✅ Analysis Complete!")
                st.markdown("---")
                st.markdown("### 📋 Optimization Recommendations")
                st.markdown(recommendations)
                
                # Save options
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Save to PDF", use_container_width=True):
                        # Save logic here
                        st.info("PDF save functionality will be implemented")
                with col2:
                    if st.button("📤 Upload to Google Drive", use_container_width=True):
                        # Upload logic here
                        st.info("Google Drive upload will be implemented")
                        
            except Exception as e:
                st.error(f"❌ Error running analysis: {str(e)}")

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
                
                st.success("✅ Ad Copy Analysis Complete!")
                st.markdown("---")
                st.markdown("### 📋 Ad Copy Recommendations")
                st.markdown(recommendations)
                
            except Exception as e:
                st.error(f"❌ Error running analysis: {str(e)}")

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
                
                st.success("✅ Report Generated!")
                st.markdown("---")
                st.markdown("### 📄 Biweekly Report Preview")
                st.markdown(report_content)
                
                # Save options
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Save to PDF", use_container_width=True, key="biweekly_pdf"):
                        # Get account name for filename
                        account_name = selected_account_display.split(" (")[0] if selected_account_display else "Account"
                        campaign_name = selected_campaign_display.split(" (")[0] if selected_campaign_display and selected_campaign_display != "All Campaigns" else "All Campaigns"
                        
                        from real_estate_analyzer import create_biweekly_report_pdf
                        import tempfile
                        import os
                        
                        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
                        temp_filepath = temp_file.name
                        temp_file.close()
                        
                        if create_biweekly_report_pdf(report_content, account_name, campaign_name, date_range, temp_filepath):
                            with open(temp_filepath, 'rb') as f:
                                st.download_button(
                                    label="📥 Download PDF",
                                    data=f.read(),
                                    file_name=f"{account_name}_BiweeklyReport_{datetime.now().strftime('%Y%m%d')}.pdf",
                                    mime="application/pdf",
                                    use_container_width=True
                                )
                            os.unlink(temp_filepath)
                        else:
                            st.error("Failed to create PDF")
                            
                with col2:
                    if st.button("📤 Upload to Google Drive", use_container_width=True, key="biweekly_drive"):
                        st.info("Google Drive upload functionality will be implemented")
                        
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

