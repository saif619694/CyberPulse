#!/usr/bin/env python3
"""
Test script for CyberPulse application

This script tests the main functionality of the application including:
- Database connection
- API endpoints
- Data collection
- Basic frontend functionality
"""

import sys
import requests
import time
import logging
from app.shared.config import Config
from app.backend.database import db_manager
from app.frontend.utils.api_client import api_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_connection():
    """Test MongoDB connection"""
    logger.info("🔌 Testing database connection...")
    
    try:
        success = db_manager.connect()
        if success:
            logger.info("✅ Database connection successful")
            
            # Test basic operations
            collection = db_manager.get_collection()
            count = collection.count_documents({})
            logger.info(f"📊 Total documents in database: {count}")
            
            db_manager.close()
            return True
        else:
            logger.error("❌ Database connection failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Database test failed: {str(e)}")
        return False

def test_api_endpoints():
    """Test API endpoints"""
    logger.info("🔧 Testing API endpoints...")
    
    base_url = Config.API_BASE_URL
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        if response.status_code == 200:
            logger.info("✅ Health endpoint working")
        else:
            logger.error(f"❌ Health endpoint returned {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Health endpoint test failed: {str(e)}")
        return False
    
    # Test funding data endpoint
    try:
        response = requests.get(f"{base_url}/api/funding-data?page=1&itemsPerPage=5", timeout=30)
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Funding data endpoint working - {data.get('totalCount', 0)} total records")
        else:
            logger.error(f"❌ Funding data endpoint returned {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Funding data endpoint test failed: {str(e)}")
        return False
    
    # Test funding rounds endpoint
    try:
        response = requests.get(f"{base_url}/api/funding-rounds", timeout=10)
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Funding rounds endpoint working - {len(data.get('rounds', []))} rounds available")
        else:
            logger.error(f"❌ Funding rounds endpoint returned {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Funding rounds endpoint test failed: {str(e)}")
        return False
    
    return True

def test_api_client():
    """Test API client functionality"""
    logger.info("📡 Testing API client...")
    
    try:
        # Test health check
        is_healthy = api_client.health_check()
        if is_healthy:
            logger.info("✅ API client health check successful")
        else:
            logger.error("❌ API client health check failed")
            return False
        
        # Test funding data fetch
        data = api_client.get_funding_data(page=1, items_per_page=5)
        if data and 'data' in data:
            logger.info(f"✅ API client data fetch successful - {len(data['data'])} records retrieved")
        else:
            logger.error("❌ API client data fetch failed")
            return False
        
        # Test funding rounds fetch
        rounds = api_client.get_funding_rounds()
        if isinstance(rounds, list):
            logger.info(f"✅ API client rounds fetch successful - {len(rounds)} rounds")
        else:
            logger.error("❌ API client rounds fetch failed")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ API client test failed: {str(e)}")
        return False

def test_data_collection():
    """Test data collection functionality (optional - can be slow)"""
    logger.info("🔍 Testing data collection functionality...")
    
    try:
        from app.backend.security_funded import get_links, parse_article
        
        # Test link fetching
        links = get_links()
        if links and len(links.get('links', [])) > 0:
            logger.info(f"✅ Link fetching successful - {len(links['links'])} links found")
            
            # Test parsing one article (if available)
            if links['links']:
                test_link = links['links'][0]
                logger.info(f"🔍 Testing article parsing with: {test_link}")
                
                parsed_data = parse_article(test_link)
                if parsed_data:
                    logger.info(f"✅ Article parsing successful - {len(parsed_data)} companies found")
                else:
                    logger.warning("⚠️ Article parsing returned no data (may be normal)")
            
            return True
        else:
            logger.warning("⚠️ No links found (may be normal)")
            return True
            
    except Exception as e:
        logger.error(f"❌ Data collection test failed: {str(e)}")
        return False

def test_streamlit_accessibility():
    """Test if Streamlit frontend is accessible"""
    logger.info("🎨 Testing Streamlit frontend accessibility...")
    
    streamlit_url = f"http://{Config.STREAMLIT_HOST}:{Config.STREAMLIT_PORT}"
    
    try:
        response = requests.get(streamlit_url, timeout=10)
        if response.status_code == 200:
            logger.info("✅ Streamlit frontend is accessible")
            return True
        else:
            logger.warning(f"⚠️ Streamlit returned status {response.status_code}")
            return False
    except Exception as e:
        logger.warning(f"⚠️ Streamlit accessibility test failed: {str(e)}")
        logger.info("💡 Make sure Streamlit is running on the configured port")
        return False

def run_all_tests():
    """Run all tests"""
    logger.info("🚀 Starting CyberPulse application tests...")
    logger.info("=" * 50)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("API Endpoints", test_api_endpoints),
        ("API Client", test_api_client),
        ("Streamlit Frontend", test_streamlit_accessibility),
        ("Data Collection", test_data_collection),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 Running {test_name} test...")
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"❌ {test_name} test crashed: {str(e)}")
            results[test_name] = False
        
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("📊 TEST RESULTS SUMMARY")
    logger.info("=" * 50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name:<25} {status}")
    
    logger.info("-" * 50)
    logger.info(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        logger.info("🎉 All tests passed! Application is working correctly.")
        return True
    else:
        logger.error("💥 Some tests failed. Please check the logs above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)