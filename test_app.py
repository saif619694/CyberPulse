#!/usr/bin/env python3
"""
Optimized test script for CyberPulse application

Tests core functionality including:
- Database connectivity
- API endpoints
- Frontend components
- Performance benchmarks
"""

import sys
import requests
import time
import logging
from concurrent.futures import ThreadPoolExecutor
from app.shared.config import Config
from app.backend.database import db_manager
from app.frontend.utils.api_client import api_client

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CyberPulseTest:
    def __init__(self):
        self.base_url = Config.API_BASE_URL
        self.results = {}
        self.start_time = time.time()
    
    def test_database_connection(self):
        """Test MongoDB connection and operations"""
        logger.info("🔌 Testing database connection...")
        
        try:
            if not db_manager.connect():
                return False
            
            collection = db_manager.get_collection()
            count = collection.count_documents({})
            logger.info(f"📊 Database contains {count:,} documents")
            
            if count > 0:
                # Test query performance
                start_time = time.time()
                sample_doc = collection.find_one({})
                query_time = time.time() - start_time
                
                if sample_doc:
                    required_fields = ['company_name', 'amount', 'round', 'date']
                    missing_fields = [field for field in required_fields if field not in sample_doc]
                    
                    if missing_fields:
                        logger.warning(f"⚠️ Missing fields: {missing_fields}")
                    else:
                        logger.info(f"✅ Document structure valid (query: {query_time:.3f}s)")
            
            db_manager.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ Database test failed: {str(e)}")
            return False
    
    def test_api_endpoints(self):
        """Test all API endpoints with performance monitoring"""
        logger.info("🔧 Testing API endpoints...")
        
        endpoints = [
            ('/api/health', 'Health Check'),
            ('/api/funding-data?page=1&itemsPerPage=5', 'Funding Data'),
            ('/api/funding-rounds', 'Funding Rounds'),
            ('/api/stats', 'Statistics')
        ]
        
        results = {}
        
        for endpoint, name in endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}{endpoint}", timeout=30)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Endpoint-specific validations
                    if endpoint == '/api/health':
                        status = data.get('status', 'unknown')
                        logger.info(f"✅ {name}: {status} ({response_time:.3f}s)")
                    
                    elif 'funding-data' in endpoint:
                        total_count = data.get('totalCount', 0)
                        logger.info(f"✅ {name}: {total_count:,} records ({response_time:.3f}s)")
                    
                    elif 'funding-rounds' in endpoint:
                        rounds_count = len(data.get('rounds', []))
                        logger.info(f"✅ {name}: {rounds_count} rounds ({response_time:.3f}s)")
                    
                    elif endpoint == '/api/stats':
                        companies = data.get('total_companies', 0)
                        funding = data.get('total_funding', 0)
                        logger.info(f"✅ {name}: {companies:,} companies, ${funding:,} funding ({response_time:.3f}s)")
                    
                    results[name] = True
                else:
                    logger.error(f"❌ {name}: HTTP {response.status_code}")
                    results[name] = False
                    
            except Exception as e:
                logger.error(f"❌ {name} failed: {str(e)}")
                results[name] = False
        
        return all(results.values())
    
    def test_api_client_performance(self):
        """Test API client with caching and performance"""
        logger.info("📡 Testing API client performance...")
        
        try:
            # Test caching behavior
            start_time = time.time()
            data1 = api_client.get_funding_data(page=1, items_per_page=5)
            first_call_time = time.time() - start_time
            
            start_time = time.time()
            data2 = api_client.get_funding_data(page=1, items_per_page=5)
            second_call_time = time.time() - start_time
            
            if data1 and data2 and second_call_time < first_call_time:
                logger.info(f"✅ Caching working: {first_call_time:.3f}s -> {second_call_time:.3f}s")
            
            # Test concurrent requests
            def make_request(page):
                return api_client.get_funding_data(page=page, items_per_page=10)
            
            start_time = time.time()
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(make_request, i) for i in range(1, 6)]
                results = [future.result() for future in futures]
            
            concurrent_time = time.time() - start_time
            successful_requests = sum(1 for r in results if r and 'data' in r)
            
            logger.info(f"✅ Concurrent requests: {successful_requests}/5 successful ({concurrent_time:.3f}s)")
            
            return successful_requests >= 4  # Allow for 1 failure
            
        except Exception as e:
            logger.error(f"❌ API client test failed: {str(e)}")
            return False
    
    def test_ui_components(self):
        """Test UI components and formatters"""
        logger.info("🎨 Testing UI components...")
        
        try:
            from app.frontend.components.data_display import clean_html_text
            from app.frontend.utils.formatters import format_amount, format_date, get_round_color
            
            # Test amount formatting with edge cases
            test_cases = [
                (1000, "$1K"),
                (1500000, "$1.5M"),
                (2500000000, "$2.5B"),
                (0, "Undisclosed"),
                (None, "Undisclosed"),
                ("invalid", "Undisclosed")
            ]
            
            for amount, expected in test_cases:
                result = format_amount(amount)
                if result == expected:
                    logger.debug(f"✅ Amount formatting: {amount} -> {result}")
                else:
                    logger.error(f"❌ Amount formatting failed: {amount} -> {result} (expected {expected})")
                    return False
            
            # Test date formatting
            test_dates = ["2024-01-15", "2023-12-31", "invalid-date", ""]
            for date_str in test_dates:
                result = format_date(date_str)
                if result:  # Should always return something
                    logger.debug(f"✅ Date formatting: {date_str} -> {result}")
                else:
                    logger.error(f"❌ Date formatting failed for: {date_str}")
                    return False
            
            # Test round color consistency
            test_rounds = ["Seed", "Series A", "Pre-Seed", "Unknown", "Custom Round"]
            colors = {}
            for round_name in test_rounds:
                color1 = get_round_color(round_name)
                color2 = get_round_color(round_name)  # Should be consistent
                if color1 == color2 and color1.startswith('#') and len(color1) == 7:
                    colors[round_name] = color1
                    logger.debug(f"✅ Round color: {round_name} -> {color1}")
                else:
                    logger.error(f"❌ Round color inconsistent: {round_name}")
                    return False
            
            # Test HTML cleaning
            html_test = "<script>alert('test')</script><p>Safe content</p>"
            cleaned = clean_html_text(html_test)
            if "script" not in cleaned and "Safe content" in cleaned:
                logger.info("✅ HTML cleaning working properly")
            else:
                logger.error("❌ HTML cleaning failed")
                return False
            
            logger.info("✅ All UI component tests passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ UI components test failed: {str(e)}")
            return False
    
    def test_streamlit_accessibility(self):
        """Test if Streamlit frontend is accessible"""
        logger.info("🎨 Testing Streamlit frontend accessibility...")
        
        streamlit_url = f"http://{Config.STREAMLIT_HOST}:{Config.STREAMLIT_PORT}"
        
        try:
            # Try multiple times as Streamlit can be slow to start
            for attempt in range(3):
                try:
                    response = requests.get(streamlit_url, timeout=10)
                    if response.status_code == 200:
                        logger.info("✅ Streamlit frontend is accessible")
                        return True
                    else:
                        logger.warning(f"⚠️ Streamlit returned status {response.status_code}")
                except requests.exceptions.ConnectionError:
                    if attempt < 2:
                        logger.info(f"🔄 Streamlit not ready, retrying... ({attempt + 1}/3)")
                        time.sleep(5)
                    else:
                        raise
            
            return False
            
        except Exception as e:
            logger.warning(f"⚠️ Streamlit accessibility test failed: {str(e)}")
            logger.info("💡 Make sure Streamlit is running: streamlit run app/frontend/streamlit_app.py")
            return False
    
    def run_performance_benchmarks(self):
        """Run performance benchmarks"""
        logger.info("⚡ Running performance benchmarks...")
        
        try:
            # Database query performance
            if db_manager.connect():
                collection = db_manager.get_collection()
                
                # Test pagination performance
                start_time = time.time()
                list(collection.find({}).limit(50))
                query_time = time.time() - start_time
                
                if query_time < 1.0:
                    logger.info(f"✅ Database query performance: {query_time:.3f}s (good)")
                elif query_time < 3.0:
                    logger.warning(f"⚠️ Database query performance: {query_time:.3f}s (acceptable)")
                else:
                    logger.error(f"❌ Database query performance: {query_time:.3f}s (slow)")
                
                db_manager.close()
            
            # API response time benchmark
            endpoints_to_test = ['/api/health', '/api/funding-data?page=1&itemsPerPage=12']
            
            for endpoint in endpoints_to_test:
                start_time = time.time()
                response = requests.get(f"{self.base_url}{endpoint}", timeout=30)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    if response_time < 1.0:
                        logger.info(f"✅ {endpoint}: {response_time:.3f}s (fast)")
                    elif response_time < 3.0:
                        logger.warning(f"⚠️ {endpoint}: {response_time:.3f}s (acceptable)")
                    else:
                        logger.error(f"❌ {endpoint}: {response_time:.3f}s (slow)")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Performance benchmarks failed: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests and generate report"""
        logger.info("🚀 Starting CyberPulse comprehensive test suite...")
        logger.info("=" * 60)
        
        tests = [
            ("Database Connection", self.test_database_connection),
            ("API Endpoints", self.test_api_endpoints),
            ("API Client Performance", self.test_api_client_performance),
            ("UI Components", self.test_ui_components),
            ("Streamlit Frontend", self.test_streamlit_accessibility),
            ("Performance Benchmarks", self.run_performance_benchmarks),
        ]
        
        for test_name, test_func in tests:
            logger.info(f"\n📋 Running {test_name}...")
            start_time = time.time()
            
            try:
                self.results[test_name] = test_func()
                test_duration = time.time() - start_time
                status = "✅ PASS" if self.results[test_name] else "❌ FAIL"
                logger.info(f"{status} - {test_name} ({test_duration:.2f}s)")
            except Exception as e:
                self.results[test_name] = False
                logger.error(f"❌ CRASH - {test_name}: {str(e)}")
        
        # Generate summary report
        self._generate_report()
        
        return all(self.results.values())
    
    def _generate_report(self):
        """Generate test summary report"""
        total_duration = time.time() - self.start_time
        passed = sum(1 for result in self.results.values() if result)
        total = len(self.results)
        
        logger.info("\n" + "=" * 60)
        logger.info("📊 CYBERPULSE TEST REPORT")
        logger.info("=" * 60)
        
        for test_name, result in self.results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"{test_name:<30} {status}")
        
        logger.info("-" * 60)
        logger.info(f"Tests completed: {passed}/{total}")
        logger.info(f"Success rate: {(passed/total)*100:.1f}%")
        logger.info(f"Total duration: {total_duration:.2f}s")
        
        if passed == total:
            logger.info("🎉 All tests passed! CyberPulse is working optimally.")
            logger.info("🛡️ Enhanced cybersecurity funding intelligence ready!")
        else:
            logger.error("💥 Some tests failed. Please review the logs above.")
            failed_tests = [name for name, result in self.results.items() if not result]
            logger.error(f"Failed tests: {', '.join(failed_tests)}")

def main():
    """Main test execution"""
    test_suite = CyberPulseTest()
    success = test_suite.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()