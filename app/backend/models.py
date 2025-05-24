from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Investor:
    name: str
    url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'url': self.url or ''
        }

@dataclass
class CompanyData:
    description: str
    company_name: str
    company_url: str
    amount: int
    round: str
    investors: List[Investor]
    story_link: str
    source: str
    date: str
    company_type: str
    reference: str
    created_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'description': self.description,
            'company_name': self.company_name,
            'company_url': self.company_url,
            'amount': self.amount,
            'round': self.round,
            'investors': [investor.to_dict() for investor in self.investors],
            'story_link': self.story_link,
            'source': self.source,
            'date': self.date,
            'company_type': self.company_type,
            'reference': self.reference,
            'created_at': self.created_at or datetime.now().isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CompanyData':
        investors = []
        for inv_data in data.get('investors', []):
            if isinstance(inv_data, dict):
                investors.append(Investor(
                    name=inv_data.get('name', ''),
                    url=inv_data.get('url', '')
                ))
            else:
                investors.append(Investor(name=str(inv_data)))
        
        return cls(
            description=data.get('description', ''),
            company_name=data.get('company_name', ''),
            company_url=data.get('company_url', ''),
            amount=data.get('amount', 0),
            round=data.get('round', ''),
            investors=investors,
            story_link=data.get('story_link', ''),
            source=data.get('source', ''),
            date=data.get('date', ''),
            company_type=data.get('company_type', ''),
            reference=data.get('reference', ''),
            created_at=data.get('created_at')
        )

@dataclass
class PaginationParams:
    page: int = 1
    items_per_page: int = 12
    sort_field: str = 'date'
    sort_direction: str = 'desc'
    search: Optional[str] = None
    filter_round: Optional[str] = None
    
    def get_skip(self) -> int:
        return (self.page - 1) * self.items_per_page

@dataclass
class PaginatedResponse:
    data: List[Dict[str, Any]]
    total_count: int
    total_pages: int
    current_page: int
    items_per_page: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'data': self.data,
            'totalCount': self.total_count,
            'totalPages': self.total_pages,
            'currentPage': self.current_page,
            'itemsPerPage': self.items_per_page
        }