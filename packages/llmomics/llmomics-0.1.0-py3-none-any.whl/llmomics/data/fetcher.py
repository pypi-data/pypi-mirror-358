"""Main data fetcher interface for accessing bioinformatics databases."""

import logging
from typing import Dict, Any, List, Optional
from llmomics.data.geo import GEOFetcher
from llmomics.data.sra import SRAFetcher


logger = logging.getLogger(__name__)


class DataFetcher:
    """Unified interface for fetching data from various bioinformatics databases."""

    def __init__(self):
        """Initialize data fetcher with all available sources."""
        self.geo = GEOFetcher()
        self.sra = SRAFetcher()
        self._fetchers = {
            "geo": self.geo,
            "sra": self.sra,
        }

    def fetch(self, dataset_id: str) -> Dict[str, Any]:
        """Fetch dataset information based on ID.

        Args:
            dataset_id: Dataset identifier (e.g., GSE123456, SRR123456)

        Returns:
            Dictionary containing dataset information
        """
        # Determine the source based on ID pattern
        source = self._identify_source(dataset_id)

        if source and source in self._fetchers:
            return self._fetchers[source].fetch(dataset_id)
        else:
            raise ValueError(f"Unable to determine source for dataset ID: {dataset_id}")

    def search(
        self, query: str, database: Optional[str] = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for datasets across databases.

        Args:
            query: Search query
            database: Specific database to search (optional)
            limit: Maximum number of results

        Returns:
            List of dataset information dictionaries
        """
        results = []

        if database:
            if database in self._fetchers:
                results = self._fetchers[database].search(query, limit)
            else:
                raise ValueError(f"Unknown database: {database}")
        else:
            # Search all databases
            for fetcher in self._fetchers.values():
                try:
                    db_results = fetcher.search(query, limit)
                    results.extend(db_results)
                except Exception as e:
                    logger.warning(f"Error searching database: {e}")

        return results[:limit]

    def get_metadata(self, dataset_id: str) -> Dict[str, Any]:
        """Get detailed metadata for a dataset.

        Args:
            dataset_id: Dataset identifier

        Returns:
            Detailed metadata dictionary
        """
        source = self._identify_source(dataset_id)

        if source and source in self._fetchers:
            return self._fetchers[source].get_metadata(dataset_id)
        else:
            raise ValueError(f"Unable to determine source for dataset ID: {dataset_id}")

    def get_sample_info(self, dataset_id: str) -> List[Dict[str, Any]]:
        """Get sample information for a dataset.

        Args:
            dataset_id: Dataset identifier

        Returns:
            List of sample information dictionaries
        """
        source = self._identify_source(dataset_id)

        if source and source in self._fetchers:
            return self._fetchers[source].get_sample_info(dataset_id)
        else:
            raise ValueError(f"Unable to determine source for dataset ID: {dataset_id}")

    def _identify_source(self, dataset_id: str) -> Optional[str]:
        """Identify the source database based on ID pattern.

        Args:
            dataset_id: Dataset identifier

        Returns:
            Source database name or None
        """
        dataset_id_upper = dataset_id.upper()

        if dataset_id_upper.startswith("GSE") or dataset_id_upper.startswith("GSM"):
            return "geo"
        elif dataset_id_upper.startswith("SR"):
            return "sra"
        elif dataset_id_upper.startswith("E-"):
            return "arrayexpress"
        else:
            return None
