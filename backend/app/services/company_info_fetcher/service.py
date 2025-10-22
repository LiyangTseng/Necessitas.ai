"""
Company Info Fetcher Service

Main service class that orchestrates company data retrieval from multiple sources.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
logger = logging.getLogger(__name__)

from .base_adapter import CompanyDataAdapter
from .adapters import CrunchbaseCompanyAdapter, MockCompanyAdapter
from models import CompanyInfo, FundingRound, CompanySearchResult
from core.env import CRUNCHBASE_API_KEY


class CompanyInfoFetcher:
    """Unified service for company information retrieval."""

    def __init__(self):
        """Initialize the company info fetcher."""
        self.adapters: Dict[str, CompanyDataAdapter] = {}
        self._setup_adapters()

    def _setup_adapters(self):
        """Setup available adapters."""
        # Add Crunchbase adapter
        try:
            crunchbase_adapter = CrunchbaseCompanyAdapter()
            if crunchbase_adapter.is_available:
                self.adapters["crunchbase"] = crunchbase_adapter
                logger.info("Crunchbase adapter initialized")
            else:
                logger.warning("Crunchbase adapter not available - API key missing")
        except Exception as e:
            logger.warning(f"Failed to setup Crunchbase adapter: {e}")

        # Always add mock adapter as fallback
        self.adapters["mock"] = MockCompanyAdapter()
        logger.info("Mock adapter initialized as fallback")

    async def get_company_info(
        self, company_id: str, source: str = "primary"
    ) -> CompanyInfo:
        """
        Get company information from specified source.

        Args:
            company_id: Company identifier
            source: Data source to use ('primary' tries all available sources)

        Returns:
            Company information
        """
        try:
            if source == "primary":
                # Try sources in order of preference
                sources = ["crunchbase", "linkedin", "mock"]
            else:
                sources = [source, "mock"]

            for src in sources:
                if src in self.adapters:
                    try:
                        logger.info(f"Attempting to get company info from {src}")
                        return await self.adapters[src].get_company_info(company_id)
                    except Exception as e:
                        logger.warning(f"Failed to get company info from {src}: {e}")
                        continue

            raise Exception("All company data sources failed")

        except Exception as e:
            logger.error(f"Failed to get company info: {str(e)}")
            raise

    async def search_companies(
        self,
        query: str,
        limit: int = 10,
        location: Optional[str] = None,
        industry: Optional[str] = None,
        sources: List[str] = None,
    ) -> CompanySearchResult:
        """
        Search for companies across multiple sources.

        Args:
            query: Search query
            limit: Number of results
            location: Optional location filter
            industry: Optional industry filter
            sources: List of sources to search (None = all available)

        Returns:
            Company search results with metadata
        """
        start_time = datetime.now()

        try:
            if sources is None:
                # Use all available sources except mock
                sources = [
                    name for name, adapter in self.adapters.items() if name != "mock"
                ]
                if not sources:
                    sources = ["mock"]

            all_companies = []
            sources_used = []

            for source in sources:
                if source in self.adapters:
                    try:
                        logger.info(f"Searching companies on {source}")
                        companies = await self.adapters[source].search_companies(
                            query, limit // len(sources), location, industry
                        )
                        all_companies.extend(companies)
                        sources_used.append(source)
                    except Exception as e:
                        logger.warning(f"Failed to search companies on {source}: {e}")
                        continue

            # Deduplicate and limit results
            unique_companies = self._deduplicate_companies(all_companies)[:limit]

            search_time = (datetime.now() - start_time).total_seconds() * 1000

            return CompanySearchResult(
                companies=unique_companies,
                total_count=len(unique_companies),
                page=1,
                limit=limit,
                sources_used=sources_used,
                search_time_ms=search_time,
            )

        except Exception as e:
            logger.error(f"Failed to search companies: {str(e)}")
            # Return empty result instead of raising
            return CompanySearchResult(
                companies=[],
                total_count=0,
                page=1,
                limit=limit,
                sources_used=[],
                search_time_ms=0,
            )

    async def get_company_funding(
        self, company_id: str, source: str = "primary"
    ) -> List[FundingRound]:
        """
        Get company funding information.

        Args:
            company_id: Company identifier
            source: Data source to use

        Returns:
            List of funding rounds
        """
        try:
            if source == "primary":
                sources = ["crunchbase", "linkedin", "mock"]
            else:
                sources = [source, "mock"]

            for src in sources:
                if src in self.adapters:
                    try:
                        logger.info(f"Getting funding info from {src}")
                        return await self.adapters[src].get_company_funding(company_id)
                    except Exception as e:
                        logger.warning(f"Failed to get funding info from {src}: {e}")
                        continue

            return []

        except Exception as e:
            logger.error(f"Failed to get company funding: {str(e)}")
            return []

    def _deduplicate_companies(self, companies: List[CompanyInfo]) -> List[CompanyInfo]:
        """Remove duplicate companies based on name and website."""
        seen = set()
        unique_companies = []

        for company in companies:
            # Create a key based on name and website
            key = (company.name.lower().strip(), company.website.lower().strip())
            if key not in seen:
                seen.add(key)
                unique_companies.append(company)

        return unique_companies

    def get_available_sources(self) -> List[str]:
        """Get list of available data sources."""
        return [name for name, adapter in self.adapters.items() if adapter.is_available]

    def get_source_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about available sources."""
        info = {}
        for name, adapter in self.adapters.items():
            info[name] = {
                "name": adapter.source_name,
                "available": adapter.is_available,
                "type": "external" if name != "mock" else "mock",
            }
        return info
