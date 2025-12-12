"""
Google Ads Manager - Streamlit App Entry Point
This file serves as the entry point for Streamlit Cloud compatibility.
It imports and runs the main app from app.py

NOTE: This is a wrapper file. The actual app is in app.py.
Streamlit Cloud is configured to run this file, which then loads app.py.
"""

import streamlit as st
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the main app
try:
    from app import main
    main()
except ImportError as e:
    st.error(f"Error importing app: {e}")
    st.info("Make sure app.py exists in the same directory.")
    st.code(str(e))
except Exception as e:
    st.error(f"Error running app: {e}")
    import traceback
    with st.expander("Error Details"):
        st.code(traceback.format_exc())
