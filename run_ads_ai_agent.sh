#!/bin/bash

# Navigate to your project directory
cd ~/google-ads-manager

# Activate the virtual environment
source venv/bin/activate

# Run the Streamlit app
streamlit run google_ads_manager.py

# Open the browser (optional, but ensures it opens)
open http://localhost:56230