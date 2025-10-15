"""
Unit tests for CompanyInfoFetcher service using unittest.
"""

import unittest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from backend.app.services.company_info_fetcher import (
    CompanyInfoFetcher,
    CompanyInfo,
    FundingRound,
    CompanySearchResult,
)
from backend.app.services.company_info_fetcher.adapters import (
    CrunchbaseCompanyAdapter,
    LinkedInCompanyAdapter,
    MockCompanyAdapter,
)
from tests.test_utils import AsyncTestCase, MockDataFactory, MockAPIFactory


class TestCompanyInfoFetcher(AsyncTestCase):
    """Test cases for CompanyInfoFetcher service."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.company_fetcher = None

    def create_company_fetcher(self):
        """Create CompanyInfoFetcher instance for testing."""
        with (
            patch("backend.app.services.company_info_fetcher.CrunchbaseCompanyAdapter"),
            patch("backend.app.services.company_info_fetcher.LinkedInCompanyAdapter"),
            patch("backend.app.services.company_info_fetcher.MockCompanyAdapter"),
        ):
            return CompanyInfoFetcher()

    def test_company_info_fetcher_initialization(self):
        """Test CompanyInfoFetcher initialization."""
        # Act
        self.company_fetcher = self.create_company_fetcher()

        # Assert
        self.assertIsInstance(self.company_fetcher, CompanyInfoFetcher)
        self.assertIsInstance(self.company_fetcher.adapters, dict)

    def test_get_company_info_success(self):
        """Test successful company info retrieval."""
        # Arrange
        self.company_fetcher = self.create_company_fetcher()
        mock_company_info = MockDataFactory.create_company_info()

        # Mock adapter
        mock_adapter = Mock()
        mock_adapter.get_company_info = AsyncMock(
            return_value=CompanyInfo(**mock_company_info)
        )
        self.company_fetcher.adapters = {"crunchbase": mock_adapter}

        # Act
        company_info = self.run_async(
            self.company_fetcher.get_company_info("techcorp_123")
        )

        # Assert
        self.assertIsInstance(company_info, CompanyInfo)
        self.assertEqual(company_info.company_id, "techcorp_123")

    def test_get_company_info_fallback(self):
        """Test company info retrieval with fallback."""
        # Arrange
        self.company_fetcher = self.create_company_fetcher()
        mock_company_info = MockDataFactory.create_company_info()

        # Mock adapters - first fails, second succeeds
        mock_adapter1 = Mock()
        mock_adapter1.get_company_info = AsyncMock(side_effect=Exception("API error"))

        mock_adapter2 = Mock()
        mock_adapter2.get_company_info = AsyncMock(
            return_value=CompanyInfo(**mock_company_info)
        )

        self.company_fetcher.adapters = {
            "crunchbase": mock_adapter1,
            "linkedin": mock_adapter2,
        }

        # Act
        company_info = self.run_async(
            self.company_fetcher.get_company_info("techcorp_123")
        )

        # Assert
        self.assertIsInstance(company_info, CompanyInfo)
        self.assertEqual(company_info.company_id, "techcorp_123")

    def test_get_company_info_all_fail(self):
        """Test company info retrieval when all adapters fail."""
        # Arrange
        self.company_fetcher = self.create_company_fetcher()

        # Mock all adapters to fail
        mock_adapter = Mock()
        mock_adapter.get_company_info = AsyncMock(side_effect=Exception("API error"))
        self.company_fetcher.adapters = {"crunchbase": mock_adapter}

        # Act & Assert
        with self.assertRaises(Exception):
            self.run_async(self.company_fetcher.get_company_info("techcorp_123"))

    def test_search_companies_success(self):
        """Test successful company search."""
        # Arrange
        self.company_fetcher = self.create_company_fetcher()
        mock_companies = [MockDataFactory.create_company_info()]

        # Mock adapter
        mock_adapter = Mock()
        mock_adapter.search_companies = AsyncMock(
            return_value=[CompanyInfo(**mock_companies[0])]
        )
        self.company_fetcher.adapters = {"crunchbase": mock_adapter}

        # Act
        search_result = self.run_async(
            self.company_fetcher.search_companies(
                query="TechCorp",
                limit=10,
                location="San Francisco",
                industry="Technology",
            )
        )

        # Assert
        self.assertIsInstance(search_result, CompanySearchResult)
        self.assertEqual(len(search_result.companies), 1)
        self.assertIn("crunchbase", search_result.sources_used)

    def test_search_companies_multiple_sources(self):
        """Test company search with multiple sources."""
        # Arrange
        self.company_fetcher = self.create_company_fetcher()
        mock_company_info = MockDataFactory.create_company_info()

        # Mock multiple adapters
        mock_adapter1 = Mock()
        mock_adapter1.search_companies = AsyncMock(
            return_value=[CompanyInfo(**mock_company_info)]
        )

        mock_adapter2 = Mock()
        mock_adapter2.search_companies = AsyncMock(
            return_value=[CompanyInfo(**mock_company_info)]
        )

        self.company_fetcher.adapters = {
            "crunchbase": mock_adapter1,
            "linkedin": mock_adapter2,
        }

        # Act
        search_result = self.run_async(
            self.company_fetcher.search_companies(query="TechCorp", limit=10)
        )

        # Assert
        self.assertIsInstance(search_result, CompanySearchResult)
        self.assertGreater(len(search_result.companies), 0)
        self.assertIn("crunchbase", search_result.sources_used)
        self.assertIn("linkedin", search_result.sources_used)

    def test_search_companies_exception_handling(self):
        """Test company search exception handling."""
        # Arrange
        self.company_fetcher = self.create_company_fetcher()

        # Mock adapter to raise exception
        mock_adapter = Mock()
        mock_adapter.search_companies = AsyncMock(side_effect=Exception("API error"))
        self.company_fetcher.adapters = {"crunchbase": mock_adapter}

        # Act
        search_result = self.run_async(
            self.company_fetcher.search_companies(query="TechCorp", limit=10)
        )

        # Assert
        self.assertIsInstance(search_result, CompanySearchResult)
        self.assertEqual(len(search_result.companies), 0)
        self.assertEqual(len(search_result.sources_used), 0)

    def test_get_company_funding_success(self):
        """Test successful company funding retrieval."""
        # Arrange
        self.company_fetcher = self.create_company_fetcher()
        mock_funding = [
            {
                "round_name": "Series A",
                "announced_date": "2023-01-01",
                "money_raised": 10000000,
                "investors": ["VC Fund 1", "VC Fund 2"],
            }
        ]

        # Mock adapter
        mock_adapter = Mock()
        mock_adapter.get_company_funding = AsyncMock(
            return_value=[FundingRound(**mock_funding[0])]
        )
        self.company_fetcher.adapters = {"crunchbase": mock_adapter}

        # Act
        funding_rounds = self.run_async(
            self.company_fetcher.get_company_funding("techcorp_123")
        )

        # Assert
        self.assertIsInstance(funding_rounds, list)
        self.assertEqual(len(funding_rounds), 1)
        self.assertEqual(funding_rounds[0].round_name, "Series A")

    def test_get_company_funding_fallback(self):
        """Test company funding retrieval with fallback."""
        # Arrange
        self.company_fetcher = self.create_company_fetcher()
        mock_funding = [
            {
                "round_name": "Series A",
                "announced_date": "2023-01-01",
                "money_raised": 10000000,
                "investors": ["VC Fund 1"],
            }
        ]

        # Mock adapters - first fails, second succeeds
        mock_adapter1 = Mock()
        mock_adapter1.get_company_funding = AsyncMock(
            side_effect=Exception("API error")
        )

        mock_adapter2 = Mock()
        mock_adapter2.get_company_funding = AsyncMock(
            return_value=[FundingRound(**mock_funding[0])]
        )

        self.company_fetcher.adapters = {
            "crunchbase": mock_adapter1,
            "linkedin": mock_adapter2,
        }

        # Act
        funding_rounds = self.run_async(
            self.company_fetcher.get_company_funding("techcorp_123")
        )

        # Assert
        self.assertIsInstance(funding_rounds, list)
        self.assertEqual(len(funding_rounds), 1)

    def test_get_available_sources(self):
        """Test getting available sources."""
        # Arrange
        self.company_fetcher = self.create_company_fetcher()

        # Mock adapters with different availability
        mock_adapter1 = Mock()
        mock_adapter1.is_available = True

        mock_adapter2 = Mock()
        mock_adapter2.is_available = False

        self.company_fetcher.adapters = {
            "crunchbase": mock_adapter1,
            "linkedin": mock_adapter2,
        }

        # Act
        available_sources = self.company_fetcher.get_available_sources()

        # Assert
        self.assertIsInstance(available_sources, list)
        self.assertIn("crunchbase", available_sources)
        self.assertNotIn("linkedin", available_sources)

    def test_get_source_info(self):
        """Test getting source information."""
        # Arrange
        self.company_fetcher = self.create_company_fetcher()

        # Mock adapters
        mock_adapter1 = Mock()
        mock_adapter1.source_name = "crunchbase"
        mock_adapter1.is_available = True

        mock_adapter2 = Mock()
        mock_adapter2.source_name = "linkedin"
        mock_adapter2.is_available = False

        self.company_fetcher.adapters = {
            "crunchbase": mock_adapter1,
            "linkedin": mock_adapter2,
        }

        # Act
        source_info = self.company_fetcher.get_source_info()

        # Assert
        self.assertIsInstance(source_info, dict)
        self.assertIn("crunchbase", source_info)
        self.assertIn("linkedin", source_info)
        self.assertTrue(source_info["crunchbase"]["available"])
        self.assertFalse(source_info["linkedin"]["available"])

    def test_deduplicate_companies(self):
        """Test company deduplication."""
        # Arrange
        self.company_fetcher = self.create_company_fetcher()

        # Create duplicate companies
        company1 = CompanyInfo(
            company_id="1",
            name="TechCorp",
            website="https://techcorp.com",
            description="Tech company",
        )
        company2 = CompanyInfo(
            company_id="2",
            name="TechCorp",
            website="https://techcorp.com",
            description="Tech company",
        )
        company3 = CompanyInfo(
            company_id="3",
            name="OtherCorp",
            website="https://othercorp.com",
            description="Other company",
        )

        companies = [company1, company2, company3]

        # Act
        unique_companies = self.company_fetcher._deduplicate_companies(companies)

        # Assert
        self.assertEqual(len(unique_companies), 2)  # Should remove one duplicate
        self.assertEqual(unique_companies[0].name, "TechCorp")
        self.assertEqual(unique_companies[1].name, "OtherCorp")


class TestCrunchbaseCompanyAdapter(AsyncTestCase):
    """Test cases for CrunchbaseCompanyAdapter."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.adapter = None

    def create_adapter(self):
        """Create CrunchbaseCompanyAdapter instance for testing."""
        with patch(
            "backend.app.services.company_info_fetcher.adapters.httpx.AsyncClient"
        ):
            return CrunchbaseCompanyAdapter(api_key="test_key")

    def test_crunchbase_adapter_initialization(self):
        """Test CrunchbaseCompanyAdapter initialization."""
        # Act
        self.adapter = self.create_adapter()

        # Assert
        self.assertIsInstance(self.adapter, CrunchbaseCompanyAdapter)
        self.assertEqual(self.adapter.source_name, "crunchbase")
        self.assertTrue(self.adapter.is_available)

    def test_crunchbase_adapter_no_api_key(self):
        """Test CrunchbaseCompanyAdapter without API key."""
        # Act
        adapter = CrunchbaseCompanyAdapter()

        # Assert
        self.assertFalse(adapter.is_available)

    def test_get_company_info_success(self):
        """Test successful company info retrieval from Crunchbase."""
        # Arrange
        self.adapter = self.create_adapter()
        mock_response = MockAPIFactory.create_crunchbase_response()

        # Mock httpx client
        with patch(
            "backend.app.services.company_info_fetcher.adapters.httpx.AsyncClient"
        ) as mock_client:
            mock_response_obj = Mock()
            mock_response_obj.status_code = 200
            mock_response_obj.json.return_value = mock_response
            mock_client.return_value.__aenter__.return_value.get.return_value = (
                mock_response_obj
            )

            # Act
            company_info = self.run_async(self.adapter.get_company_info("techcorp"))

            # Assert
            self.assertIsInstance(company_info, CompanyInfo)
            self.assertEqual(company_info.name, "TechCorp")

    def test_get_company_info_api_error(self):
        """Test company info retrieval with API error."""
        # Arrange
        self.adapter = self.create_adapter()

        # Mock httpx client to return error
        with patch(
            "backend.app.services.company_info_fetcher.adapters.httpx.AsyncClient"
        ) as mock_client:
            mock_response_obj = Mock()
            mock_response_obj.status_code = 400
            mock_client.return_value.__aenter__.return_value.get.return_value = (
                mock_response_obj
            )

            # Act & Assert
            with self.assertRaises(Exception):
                self.run_async(self.adapter.get_company_info("techcorp"))

    def test_search_companies_success(self):
        """Test successful company search on Crunchbase."""
        # Arrange
        self.adapter = self.create_adapter()
        mock_response = MockAPIFactory.create_crunchbase_response()

        # Mock httpx client
        with patch(
            "backend.app.services.company_info_fetcher.adapters.httpx.AsyncClient"
        ) as mock_client:
            mock_response_obj = Mock()
            mock_response_obj.status_code = 200
            mock_response_obj.json.return_value = mock_response
            mock_client.return_value.__aenter__.return_value.get.return_value = (
                mock_response_obj
            )

            # Act
            companies = self.run_async(
                self.adapter.search_companies(
                    query="TechCorp",
                    limit=10,
                    location="San Francisco",
                    industry="Technology",
                )
            )

            # Assert
            self.assertIsInstance(companies, list)
            self.assertEqual(len(companies), 1)
            self.assertEqual(companies[0].name, "TechCorp")

    def test_get_company_funding_success(self):
        """Test successful company funding retrieval from Crunchbase."""
        # Arrange
        self.adapter = self.create_adapter()
        mock_funding_response = {
            "cards": [
                {
                    "properties": {
                        "announced_on": {"value": "2023-01-01"},
                        "money_raised": {"value": 10000000},
                        "money_raised_currency": {"value": "USD"},
                        "investors": [{"value": "VC Fund 1"}],
                        "round_type": {"value": "Series A"},
                    }
                }
            ]
        }

        # Mock httpx client
        with patch(
            "backend.app.services.company_info_fetcher.adapters.httpx.AsyncClient"
        ) as mock_client:
            mock_response_obj = Mock()
            mock_response_obj.status_code = 200
            mock_response_obj.json.return_value = mock_funding_response
            mock_client.return_value.__aenter__.return_value.get.return_value = (
                mock_response_obj
            )

            # Act
            funding_rounds = self.run_async(
                self.adapter.get_company_funding("techcorp")
            )

            # Assert
            self.assertIsInstance(funding_rounds, list)
            self.assertEqual(len(funding_rounds), 1)
            self.assertEqual(funding_rounds[0].round_name, "2023-01-01")


class TestLinkedInCompanyAdapter(AsyncTestCase):
    """Test cases for LinkedInCompanyAdapter."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.adapter = None

    def create_adapter(self):
        """Create LinkedInCompanyAdapter instance for testing."""
        return LinkedInCompanyAdapter(api_key="test_key")

    def test_linkedin_adapter_initialization(self):
        """Test LinkedInCompanyAdapter initialization."""
        # Act
        self.adapter = self.create_adapter()

        # Assert
        self.assertIsInstance(self.adapter, LinkedInCompanyAdapter)
        self.assertEqual(self.adapter.source_name, "linkedin")
        self.assertTrue(self.adapter.is_available)

    def test_linkedin_adapter_no_api_key(self):
        """Test LinkedInCompanyAdapter without API key."""
        # Act
        adapter = LinkedInCompanyAdapter()

        # Assert
        self.assertFalse(adapter.is_available)

    def test_get_company_info_success(self):
        """Test successful company info retrieval from LinkedIn."""
        # Arrange
        self.adapter = self.create_adapter()

        # Act
        company_info = self.run_async(self.adapter.get_company_info("linkedin_123"))

        # Assert
        self.assertIsInstance(company_info, CompanyInfo)
        self.assertEqual(company_info.company_id, "linkedin_123")
        self.assertEqual(company_info.name, "LinkedIn Company")

    def test_search_companies_success(self):
        """Test successful company search on LinkedIn."""
        # Arrange
        self.adapter = self.create_adapter()

        # Act
        companies = self.run_async(
            self.adapter.search_companies(
                query="TechCorp",
                limit=10,
                location="San Francisco",
                industry="Technology",
            )
        )

        # Assert
        self.assertIsInstance(companies, list)
        self.assertGreater(len(companies), 0)
        self.assertEqual(companies[0].name, "LinkedIn Company 1")

    def test_get_company_funding_success(self):
        """Test successful company funding retrieval from LinkedIn."""
        # Arrange
        self.adapter = self.create_adapter()

        # Act
        funding_rounds = self.run_async(
            self.adapter.get_company_funding("linkedin_123")
        )

        # Assert
        self.assertIsInstance(funding_rounds, list)
        self.assertEqual(len(funding_rounds), 1)
        self.assertEqual(funding_rounds[0].round_name, "IPO")


class TestMockCompanyAdapter(AsyncTestCase):
    """Test cases for MockCompanyAdapter."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.adapter = MockCompanyAdapter()

    def test_mock_adapter_initialization(self):
        """Test MockCompanyAdapter initialization."""
        # Assert
        self.assertIsInstance(self.adapter, MockCompanyAdapter)
        self.assertEqual(self.adapter.source_name, "mock")
        self.assertTrue(self.adapter.is_available)

    def test_get_company_info_success(self):
        """Test successful company info retrieval from mock adapter."""
        # Act
        company_info = self.run_async(self.adapter.get_company_info("mock_123"))

        # Assert
        self.assertIsInstance(company_info, CompanyInfo)
        self.assertEqual(company_info.company_id, "mock_123")
        self.assertEqual(company_info.name, "Mock Company")

    def test_search_companies_success(self):
        """Test successful company search on mock adapter."""
        # Act
        companies = self.run_async(
            self.adapter.search_companies(
                query="MockCorp",
                limit=10,
                location="San Francisco",
                industry="Technology",
            )
        )

        # Assert
        self.assertIsInstance(companies, list)
        self.assertGreater(len(companies), 0)
        self.assertEqual(companies[0].name, "Mock Company 1")

    def test_get_company_funding_success(self):
        """Test successful company funding retrieval from mock adapter."""
        # Act
        funding_rounds = self.run_async(self.adapter.get_company_funding("mock_123"))

        # Assert
        self.assertIsInstance(funding_rounds, list)
        self.assertEqual(len(funding_rounds), 1)
        self.assertEqual(funding_rounds[0].round_name, "Seed Round")


if __name__ == "__main__":
    unittest.main()
