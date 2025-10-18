"""
Company Data Adapters

Concrete implementations of company data adapters for different sources.
"""

import httpx
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
logger = logging.getLogger(__name__)

from .base_adapter import CompanyDataAdapter
from models import CompanyInfo, FundingRound
from core.config import settings


class CrunchbaseCompanyAdapter(CompanyDataAdapter):
    """Crunchbase company data adapter."""

    def __init__(self, api_key: str = None):
        """Initialize Crunchbase adapter."""
        self.api_key = api_key or settings.crunchbase_api_key
        self.base_url = "https://api.crunchbase.com/v4"
        self.headers = (
            {"X-cb-user-key": self.api_key, "Content-Type": "application/json"}
            if self.api_key
            else {}
        )

    @property
    def source_name(self) -> str:
        return "crunchbase"

    @property
    def is_available(self) -> bool:
        return bool(self.api_key)

    def get_company_info(self, company_id: str) -> CompanyInfo:
        """Get company information from Crunchbase."""
        if not self.is_available:
            raise Exception("Crunchbase API key not configured")

        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.base_url}/entities/organizations/{company_id}",
                    headers=self.headers,
                    timeout=10.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    return self._parse_company_data(data)
                else:
                    logger.error(f"Crunchbase API error: {response.status_code}")
                    raise Exception(f"Crunchbase API error: {response.status_code}")

        except Exception as e:
            logger.error(f"Failed to get company info from Crunchbase: {str(e)}")
            raise

    def search_companies(
        self,
        query: str,
        limit: int = 10,
        location: Optional[str] = None,
        industry: Optional[str] = None,
    ) -> List[CompanyInfo]:
        """Search companies on Crunchbase."""
        if not self.is_available:
            raise Exception("Crunchbase API key not configured")

        try:
            params = {
                "query": query,
                "limit": limit,
                "field_ids": [
                    "identifier",
                    "name",
                    "short_description",
                    "location_identifiers",
                    "categories",
                    "founded_on",
                    "num_employees_enum",
                    "website",
                ],
            }

            if location:
                params["location_identifiers"] = location
            if industry:
                params["categories"] = industry

            with httpx.Client() as client:
                response = client.get(
                    f"{self.base_url}/searches/organizations",
                    headers=self.headers,
                    params=params,
                    timeout=10.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    return self._parse_search_results(data)
                else:
                    logger.error(f"Crunchbase search error: {response.status_code}")
                    raise Exception(f"Crunchbase search error: {response.status_code}")

        except Exception as e:
            logger.error(f"Failed to search companies on Crunchbase: {str(e)}")
            raise

    def get_company_funding(self, company_id: str) -> List[FundingRound]:
        """Get company funding from Crunchbase."""
        if not self.is_available:
            raise Exception("Crunchbase API key not configured")

        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.base_url}/entities/organizations/{company_id}/cards/funding_rounds",
                    headers=self.headers,
                    timeout=10.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    return self._parse_funding_data(data)
                else:
                    logger.error(
                        f"Crunchbase funding API error: {response.status_code}"
                    )
                    raise Exception(
                        f"Crunchbase funding API error: {response.status_code}"
                    )

        except Exception as e:
            logger.error(f"Failed to get funding info from Crunchbase: {str(e)}")
            raise

    def _parse_company_data(self, data: Dict[str, Any]) -> CompanyInfo:
        """Parse company data from Crunchbase API response."""
        try:
            entity = data.get("properties", {})

            return CompanyInfo(
                company_id=entity.get("identifier", {}).get("value", ""),
                name=entity.get("name", ""),
                description=entity.get("short_description", ""),
                website=entity.get("website", {}).get("value", ""),
                founded_year=entity.get("founded_on", {}).get("value", ""),
                employee_count=entity.get("num_employees_enum", {}).get("value", ""),
                location=self._parse_location(entity.get("location_identifiers", [])),
                industry=entity.get("industry", ""),
                categories=self._parse_categories(entity.get("categories", [])),
                funding_total=entity.get("total_funding_usd", {}).get("value", 0),
                last_funding_date=entity.get("last_funding_on", {}).get("value", ""),
                status=entity.get("operating_status", {}).get("value", ""),
                social_links=self._parse_social_links(entity.get("linkedin", {})),
            )
        except Exception as e:
            logger.error(f"Failed to parse Crunchbase company data: {str(e)}")
            raise

    def _parse_search_results(self, data: Dict[str, Any]) -> List[CompanyInfo]:
        """Parse search results from Crunchbase API response."""
        try:
            entities = data.get("entities", [])
            results = []

            for entity in entities:
                properties = entity.get("properties", {})
                results.append(
                    CompanyInfo(
                        company_id=properties.get("identifier", {}).get("value", ""),
                        name=properties.get("name", ""),
                        description=properties.get("short_description", ""),
                        website=properties.get("website", {}).get("value", ""),
                        location=self._parse_location(
                            properties.get("location_identifiers", [])
                        ),
                        categories=self._parse_categories(
                            properties.get("categories", [])
                        ),
                        employee_count=properties.get("num_employees_enum", {}).get(
                            "value", ""
                        ),
                    )
                )

            return results
        except Exception as e:
            logger.error(f"Failed to parse Crunchbase search results: {str(e)}")
            return []

    def _parse_funding_data(self, data: Dict[str, Any]) -> List[FundingRound]:
        """Parse funding data from Crunchbase API response."""
        try:
            cards = data.get("cards", [])
            funding_rounds = []

            for card in cards:
                properties = card.get("properties", {})
                funding_rounds.append(
                    FundingRound(
                        round_name=properties.get("announced_on", {}).get("value", ""),
                        announced_date=properties.get("announced_on", {}).get(
                            "value", ""
                        ),
                        money_raised=properties.get("money_raised", {}).get("value", 0),
                        money_raised_currency=properties.get(
                            "money_raised_currency", {}
                        ).get("value", "USD"),
                        investors=self._parse_investors(
                            properties.get("investors", [])
                        ),
                        round_type=properties.get("round_type", {}).get("value", ""),
                    )
                )

            return funding_rounds
        except Exception as e:
            logger.error(f"Failed to parse Crunchbase funding data: {str(e)}")
            return []

    def _parse_location(self, location_identifiers: List[Dict[str, Any]]) -> str:
        """Parse location information."""
        if not location_identifiers:
            return ""
        return location_identifiers[0].get("value", "")

    def _parse_categories(self, categories: List[Dict[str, Any]]) -> List[str]:
        """Parse category information."""
        return [cat.get("value", "") for cat in categories if cat.get("value")]

    def _parse_social_links(self, linkedin_data: Dict[str, Any]) -> Dict[str, str]:
        """Parse social media links."""
        return {"linkedin": linkedin_data.get("value", "")}

    def _parse_investors(self, investors: List[Dict[str, Any]]) -> List[str]:
        """Parse investor information."""
        return [inv.get("value", "") for inv in investors if inv.get("value")]


class MockCompanyAdapter(CompanyDataAdapter):
    """Mock company data adapter for testing."""

    @property
    def source_name(self) -> str:
        return "mock"

    @property
    def is_available(self) -> bool:
        return True

    async def get_company_info(self, company_id: str) -> CompanyInfo:
        """Get mock company information."""
        return CompanyInfo(
            company_id=company_id,
            name="Mock Company",
            description="Mock technology company for testing",
            website="https://mockcompany.com",
            founded_year="2020",
            employee_count="100-500",
            location="San Francisco, CA",
            industry="Technology",
            categories=["Software", "AI"],
            funding_total=10000000,
            last_funding_date="2023-01-01",
            status="Operating",
            social_links={"linkedin": "https://linkedin.com/company/mockcompany"},
        )

    async def search_companies(
        self,
        query: str,
        limit: int = 10,
        location: Optional[str] = None,
        industry: Optional[str] = None,
    ) -> List[CompanyInfo]:
        """Get mock company search results."""
        return [
            CompanyInfo(
                company_id=f"mock_{i}",
                name=f"Mock Company {i}",
                description=f"Mock technology company {i}",
                website=f"https://mockcompany{i}.com",
                location=location or "San Francisco, CA",
                industry=industry or "Technology",
            )
            for i in range(1, limit + 1)
        ]

    async def get_company_funding(self, company_id: str) -> List[FundingRound]:
        """Get mock company funding."""
        return [
            FundingRound(
                round_name="Seed Round",
                announced_date="2023-01-01",
                money_raised=1000000,
                investors=["Mock VC Fund"],
                round_type="Seed",
            )
        ]
