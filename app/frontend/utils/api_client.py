import requests
import logging
import time
from typing import Dict, Any, List, Optional
from app.shared.config import Config

logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or Config.API_BASE_URL
        self.session = requests.Session()
        self.session.timeout = 30  # 30 seconds timeout
        
        # Add retries for connection issues
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Simple cache
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes
        
        logger.info(f"API Client initialized with base URL: {self.base_url}")
    
    def _get_cache_key(self, endpoint: str, params: Dict[str, Any] = None) -> str:
        """Generate cache key for request"""
        key = f"{endpoint}"
        if params:
            sorted_params = sorted(params.items())
            key += f"_{hash(str(sorted_params))}"
        return key
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid"""
        if key not in self._cache:
            return False
        
        cached_time, _ = self._cache[key]
        return time.time() - cached_time < self._cache_ttl
    
    def _get_cached_data(self, key: str) -> Any:
        """Get cached data if valid"""
        if self._is_cache_valid(key):
            _, data = self._cache[key]
            return data
        return None
    
    def _cache_data(self, key: str, data: Any):
        """Cache data with timestamp"""
        self._cache[key] = (time.time(), data)
    
    def _make_request(self, method: str, endpoint: str, use_cache: bool = True, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to API with better error handling"""
        url = f"{self.base_url}{endpoint}"
        
        # Check cache for GET requests
        if method.upper() == 'GET' and use_cache:
            cache_key = self._get_cache_key(endpoint, kwargs.get('params'))
            cached_data = self._get_cached_data(cache_key)
            if cached_data is not None:
                logger.debug(f"Returning cached data for {endpoint}")
                return cached_data
        
        logger.debug(f"Making {method} request to: {url}")
        
        try:
            response = self.session.request(method, url, **kwargs)
            logger.debug(f"Response status: {response.status_code}")
            response.raise_for_status()
            
            # Handle empty responses
            if not response.content:
                return {}
                
            data = response.json()
            
            # Cache successful GET responses
            if method.upper() == 'GET' and use_cache:
                cache_key = self._get_cache_key(endpoint, kwargs.get('params'))
                self._cache_data(cache_key, data)
            
            return data
            
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection failed to {url}: {str(e)}")
            raise Exception(f"Cannot connect to backend API at {url}. Is the backend server running?")
            
        except requests.exceptions.Timeout as e:
            logger.error(f"Request timeout to {url}: {str(e)}")
            raise Exception(f"Request timeout. Backend server may be overloaded.")
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error {response.status_code} for {url}: {str(e)}")
            try:
                error_detail = response.json().get('error', str(e))
            except:
                error_detail = str(e)
            raise Exception(f"API request failed: {error_detail}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed to {url}: {str(e)}")
            raise Exception(f"API request failed: {str(e)}")
            
        except ValueError as e:
            logger.error(f"Failed to parse JSON response from {url}: {str(e)}")
            logger.debug(f"Response content: {response.text[:500]}")
            raise Exception("Invalid response format from API")
    
    def test_connection(self) -> Dict[str, Any]:
        """Test API connection with detailed diagnostics"""
        diagnostics = {
            "base_url": self.base_url,
            "health_check": False,
            "connection_error": None,
            "response_time": None
        }
        
        try:
            start_time = time.time()
            result = self._make_request('GET', '/api/health', use_cache=False)
            diagnostics["response_time"] = time.time() - start_time
            diagnostics["health_check"] = result.get('status') == 'healthy'
            diagnostics["response"] = result
        except Exception as e:
            diagnostics["connection_error"] = str(e)
            
        return diagnostics
    
    def get_funding_data(self, 
                        page: int = 1,
                        items_per_page: int = 12,
                        sort_field: str = 'date',
                        sort_direction: str = 'desc',
                        search: Optional[str] = None,
                        filter_round: Optional[str] = None) -> Dict[str, Any]:
        """Get paginated funding data"""
        params = {
            'page': page,
            'itemsPerPage': items_per_page,
            'sortField': sort_field,
            'sortDirection': sort_direction
        }
        
        if search:
            params['search'] = search
        if filter_round:
            params['filterRound'] = filter_round
        
        logger.info(f"Fetching funding data: page={page}, items={items_per_page}")
        return self._make_request('GET', '/api/funding-data', params=params)
    
    def get_funding_rounds(self) -> List[str]:
        """Get available funding rounds"""
        response = self._make_request('GET', '/api/funding-rounds')
        return response.get('rounds', [])
    
    def trigger_data_collection(self) -> Dict[str, Any]:
        """Trigger fresh data collection"""
        logger.info("Triggering data collection...")
        
        # Clear relevant caches when new data is collected
        cache_keys_to_clear = [key for key in self._cache.keys() if 'funding-data' in key or 'stats' in key]
        for key in cache_keys_to_clear:
            del self._cache[key]
        
        return self._make_request('GET', '/api/get_data', use_cache=False)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        return self._make_request('GET', '/api/stats')
    
    def health_check(self) -> bool:
        """Check API health"""
        try:
            response = self._make_request('GET', '/api/health', use_cache=False)
            return response.get('status') == 'healthy'
        except Exception as e:
            logger.warning(f"Health check failed: {str(e)}")
            return False
    
    def clear_cache(self):
        """Clear all cached data"""
        self._cache.clear()
        logger.info("API client cache cleared")

# Global API client instance
api_client = APIClient()