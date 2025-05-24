import requests
import logging
from typing import Dict, Any, List, Optional
from app.shared.config import Config

logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or Config.API_BASE_URL
        self.session = requests.Session()
        self.session.timeout = 30  # 30 seconds timeout
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {method} {url} - {str(e)}")
            raise Exception(f"API request failed: {str(e)}")
        except ValueError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            raise Exception("Invalid response format")
    
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
        
        return self._make_request('GET', '/api/funding-data', params=params)
    
    def get_funding_rounds(self) -> List[str]:
        """Get available funding rounds"""
        response = self._make_request('GET', '/api/funding-rounds')
        return response.get('rounds', [])
    
    def trigger_data_collection(self) -> Dict[str, Any]:
        """Trigger fresh data collection"""
        return self._make_request('GET', '/api/get_data')
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        return self._make_request('GET', '/api/stats')
    
    def health_check(self) -> bool:
        """Check API health"""
        try:
            response = self._make_request('GET', '/api/health')
            return response.get('status') == 'healthy'
        except:
            return False

# Global API client instance
api_client = APIClient()