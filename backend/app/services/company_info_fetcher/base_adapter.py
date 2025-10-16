"""
Base Adapter for Company Data Sources

Abstract base class for company data adapters.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from models import CompanyInfo, FundingRound


class CompanyDataAdapter(ABC):
    """Abstract adapter for company data sources."""

    @abstractmethod
    async def get_company_info(self, company_id: str) -> CompanyInfo:
        """Get company information."""
        pass

    @abstractmethod
    async def search_companies(
        self,
        query: str,
        limit: int = 10,
        location: Optional[str] = None,
        industry: Optional[str] = None,
    ) -> List[CompanyInfo]:
        """Search for companies."""
        pass

    @abstractmethod
    async def get_company_funding(self, company_id: str) -> List[FundingRound]:
        """Get company funding information."""
        pass

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Get the name of this data source."""
        pass

    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Check if this adapter is available."""
        pass
