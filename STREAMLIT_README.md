# Streamlit Web App - Google Ads Analyzer

Modern web interface for Google Ads campaign analysis and management.

## Features

### 📊 Campaign Analysis
- Comprehensive campaign optimization recommendations
- Keyword, ad group, and bidding strategy analysis
- Budget allocation insights
- Performance metrics and trends

### 📝 Ad Copy Optimization
- AI-powered ad copy recommendations
- Character limit compliance (30 chars headlines, 90 chars descriptions)
- A/B testing suggestions
- High-converting keyword integration

### 📄 Biweekly Reports
- Professional 2-page PDF reports
- Client-friendly format
- Performance overview and insights
- Download or upload to Google Drive

### 💬 Ask Claude
- Interactive Q&A with Claude AI
- Expert Google Ads management advice
- Context-aware responses
- Conversation history

### ➕ Create Account
- Create new Google Ads sub-accounts under MCC
- Configure currency and timezone
- Automatic conversion tracking setup

### 🎯 Create Campaign
- Create new campaigns for sub-accounts
- Set daily budgets
- Configure bidding strategies (Maximize Clicks)
- Apply negative keyword lists

## Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up environment variables:**
Create a `.env` file with:
```env
GOOGLE_ADS_DEVELOPER_TOKEN=your_token
GOOGLE_ADS_CLIENT_ID=your_client_id
GOOGLE_ADS_CLIENT_SECRET=your_secret
GOOGLE_ADS_CUSTOMER_ID=your_mcc_id
ANTHROPIC_API_KEY=your_claude_key
```

3. **Authenticate:**
```bash
python authenticate.py
```

## Running the App

### Local Development
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### Streamlit Cloud Deployment

1. **Push to GitHub:**
   - Create a new repository
   - Push your code

2. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Connect your GitHub repository
   - Set the main file path: `app.py`
   - Add your secrets in the Streamlit Cloud dashboard:
     - `GOOGLE_ADS_DEVELOPER_TOKEN`
     - `GOOGLE_ADS_CLIENT_ID`
     - `GOOGLE_ADS_CLIENT_SECRET`
     - `GOOGLE_ADS_CUSTOMER_ID`
     - `ANTHROPIC_API_KEY`
     - Upload `token.json` file (or configure OAuth)

3. **Deploy:**
   - Click "Deploy"
   - Wait for deployment to complete
   - Access your app via the provided URL

## Usage

1. **Select a page** from the sidebar navigation
2. **Choose account and campaign** (for analysis pages)
3. **Configure parameters** (date range, goals, etc.)
4. **Run analysis** or create accounts/campaigns
5. **View results** and download/upload reports

## UI Features

- **Modern Design:** Clean, professional interface
- **Responsive Layout:** Works on desktop and tablet
- **Real-time Updates:** Live analysis progress
- **Export Options:** PDF download and Google Drive upload
- **Chat Interface:** Interactive Q&A with Claude

## Troubleshooting

### Authentication Issues
- Run `python authenticate.py` to refresh tokens
- Check that `token.json` exists and is valid
- Verify environment variables are set correctly

### Import Errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check that all Python files are in the same directory

### API Errors
- Verify Google Ads API credentials
- Check Claude API key is valid
- Ensure MCC account has proper permissions

## Notes

- The app uses session state to maintain connections
- Analysis results are cached during the session
- PDF generation requires reportlab
- Google Drive upload requires proper OAuth setup

