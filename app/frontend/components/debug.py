import streamlit as st
import requests
import json
from app.frontend.utils.api_client import api_client
from app.shared.config import Config

def display_debug_panel():
    """Display debug panel for troubleshooting connectivity issues"""
    
    st.markdown("### 🐛 Debug Information")
    
    with st.expander("🔌 Connection Diagnostics", expanded=True):
        
        # Configuration info
        st.markdown("#### 📋 Configuration")
        config_data = {
            "API Base URL": Config.API_BASE_URL,
            "Flask Host": Config.FLASK_HOST,
            "Flask Port": Config.FLASK_PORT,
            "Streamlit Host": Config.STREAMLIT_HOST,
            "Streamlit Port": Config.STREAMLIT_PORT,
            "Database Name": Config.DB_NAME,
            "Collection Name": Config.COLLECTION_NAME
        }
        
        for key, value in config_data.items():
            st.text(f"{key}: {value}")
        
        st.markdown("---")
        
        # API Connection Test
        st.markdown("#### 🔧 API Connection Test")
        
        if st.button("🧪 Test API Connection", type="primary"):
            with st.spinner("Testing API connection..."):
                
                # Test direct URL access
                st.markdown("**Direct URL Test:**")
                try:
                    response = requests.get(f"{Config.API_BASE_URL}/api/health", timeout=10)
                    if response.status_code == 200:
                        st.success(f"✅ Direct connection successful (Status: {response.status_code})")
                        
                        # Show health data
                        health_data = response.json()
                        st.json(health_data)
                    else:
                        st.error(f"❌ Direct connection failed (Status: {response.status_code})")
                        st.text(response.text)
                        
                except requests.exceptions.ConnectionError as e:
                    st.error(f"❌ Connection Error: {str(e)}")
                    st.warning("Backend server may not be running or accessible")
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                
                st.markdown("---")
                
                # Test API Client
                st.markdown("**API Client Test:**")
                try:
                    diagnostics = api_client.test_connection()
                    
                    if diagnostics["health_check"]:
                        st.success("✅ API Client connection successful")
                        st.metric("Response Time", f"{diagnostics['response_time']:.2f}s")
                    else:
                        st.error("❌ API Client connection failed")
                    
                    if diagnostics["connection_error"]:
                        st.error(f"Error: {diagnostics['connection_error']}")
                    
                    # Show full diagnostics
                    with st.expander("Full Diagnostics"):
                        st.json(diagnostics)
                        
                except Exception as e:
                    st.error(f"❌ API Client test failed: {str(e)}")
        
        st.markdown("---")
        
        # Quick data test
        st.markdown("#### 📊 Data Access Test")
        
        if st.button("🧪 Test Data Endpoints"):
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Funding Data:**")
                try:
                    data = api_client.get_funding_data(page=1, items_per_page=1)
                    st.success(f"✅ Retrieved {data.get('totalCount', 0)} total records")
                    if data.get('data'):
                        st.json(data['data'][0])
                except Exception as e:
                    st.error(f"❌ Failed: {str(e)}")
            
            with col2:
                st.markdown("**Funding Rounds:**")
                try:
                    rounds = api_client.get_funding_rounds()
                    st.success(f"✅ Retrieved {len(rounds)} funding rounds")
                    st.json(rounds[:5])  # Show first 5
                except Exception as e:
                    st.error(f"❌ Failed: {str(e)}")
        
        st.markdown("---")
        
        # Manual endpoint test
        st.markdown("#### 🔗 Manual Endpoint Test")
        
        endpoint = st.text_input(
            "Endpoint to test", 
            value="/api/health",
            help="Enter an API endpoint to test manually"
        )
        
        if st.button("🔍 Test Endpoint"):
            if endpoint:
                try:
                    url = f"{Config.API_BASE_URL}{endpoint}"
                    st.info(f"Testing: {url}")
                    
                    response = requests.get(url, timeout=10)
                    
                    st.success(f"Status: {response.status_code}")
                    
                    # Try to parse as JSON
                    try:
                        json_data = response.json()
                        st.json(json_data)
                    except:
                        st.text(response.text)
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")

def display_troubleshooting_guide():
    """Display troubleshooting guide"""
    
    st.markdown("### 🆘 Troubleshooting Guide")
    
    with st.expander("Common Issues & Solutions"):
        
        st.markdown("""
        #### 🔴 "Cannot connect to backend API" Error
        
        **Possible Causes:**
        1. Backend server is not running
        2. Wrong API URL configuration
        3. Network connectivity issues
        4. Docker networking problems
        
        **Solutions:**
        1. Check if Flask server is running on port 8000
        2. Verify API_BASE_URL in configuration
        3. For Docker: ensure containers are on same network
        4. Check firewall settings
        
        ---
        
        #### 🔴 "Database connection failed" Error
        
        **Possible Causes:**
        1. MongoDB credentials are incorrect
        2. MongoDB Atlas not accessible
        3. Network timeout issues
        
        **Solutions:**
        1. Verify DB_USERNAME and DB_PASSWORD in .env file
        2. Check MongoDB Atlas whitelist settings
        3. Test MongoDB connection manually
        
        ---
        
        #### 🔴 "No data found" Issue
        
        **Possible Causes:**
        1. Database is empty
        2. Data collection hasn't run
        3. Query filters are too restrictive
        
        **Solutions:**
        1. Run data collection manually
        2. Check database for existing data
        3. Clear search filters
        
        ---
        
        #### 🔧 Development Setup
        
        **Local Development:**
        ```bash
        # Terminal 1 - Start Flask API
        python -m app.backend.main
        
        # Terminal 2 - Start Streamlit Frontend  
        streamlit run app/frontend/streamlit_app.py
        ```
        
        **Docker Development:**
        ```bash
        # Build and run
        docker-compose up --build
        
        # Check logs
        docker-compose logs -f
        ```
        """)

def display_environment_info():
    """Display environment information"""
    
    st.markdown("### 🌍 Environment Information")
    
    import os
    import sys
    import platform
    
    env_info = {
        "Python Version": sys.version,
        "Platform": platform.platform(),
        "Docker Environment": os.getenv("DOCKER_ENV", "false"),
        "Current Working Directory": os.getcwd(),
    }
    
    for key, value in env_info.items():
        st.text(f"{key}: {value}")
    
    # Environment variables (masked for security)
    st.markdown("**Environment Variables:**")
    sensitive_vars = ['DB_PASSWORD', 'SECRET_KEY']
    
    for var in ['FLASK_HOST', 'FLASK_PORT', 'API_BASE_URL', 'DB_USERNAME']:
        value = os.getenv(var, 'Not Set')
        if var in sensitive_vars:
            value = '*' * len(value) if value != 'Not Set' else 'Not Set'
        st.text(f"{var}: {value}")