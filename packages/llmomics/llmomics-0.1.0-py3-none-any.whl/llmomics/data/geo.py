"""GEO (Gene Expression Omnibus) data fetcher."""

import logging
import requests
import xml.etree.ElementTree as ET
from typing import Dict, Any, List
from Bio import Entrez
from llmomics.core.config import config


logger = logging.getLogger(__name__)


class GEOFetcher:
    """Fetcher for GEO (Gene Expression Omnibus) data."""

    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    def __init__(self):
        """Initialize GEO fetcher."""
        # Set Entrez email (required by NCBI)
        if config.ncbi_email:
            Entrez.email = config.ncbi_email
        else:
            Entrez.email = "user@example.com"  # Default email
            logger.warning("NCBI email not set. Using default email.")

        # Set API key if available
        if config.ncbi_api_key:
            Entrez.api_key = config.ncbi_api_key

    def fetch(self, dataset_id: str) -> Dict[str, Any]:
        """Fetch basic dataset information from GEO.

        Args:
            dataset_id: GEO dataset ID (e.g., GSE123456)

        Returns:
            Dictionary containing dataset information
        """
        logger.info(f"Fetching GEO dataset: {dataset_id}")

        try:
            # Search for the dataset in GEO
            search_handle = Entrez.esearch(db="gds", term=dataset_id)
            search_results = Entrez.read(search_handle)
            search_handle.close()

            if not search_results["IdList"]:
                raise ValueError(f"Dataset {dataset_id} not found in GEO")

            # Fetch summary information
            summary_handle = Entrez.esummary(db="gds", id=search_results["IdList"][0])
            summary = Entrez.read(summary_handle)[0]
            summary_handle.close()

            return {
                "id": dataset_id,
                "source": "geo",
                "title": summary.get("title", ""),
                "summary": summary.get("summary", ""),
                "platform": summary.get("GPL", ""),
                "samples": int(summary.get("n_samples", 0)),
                "type": summary.get("gdsType", ""),
                "pubmed_id": summary.get("PDAT", ""),
            }

        except Exception as e:
            logger.error(f"Error fetching GEO dataset {dataset_id}: {e}")
            raise

    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for datasets in GEO.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of dataset information dictionaries
        """
        logger.info(f"Searching GEO for: {query}")

        try:
            # Search GEO
            search_handle = Entrez.esearch(
                db="gds", term=f"{query}[All Fields]", retmax=limit
            )
            search_results = Entrez.read(search_handle)
            search_handle.close()

            if not search_results["IdList"]:
                return []

            # Fetch summaries
            summary_handle = Entrez.esummary(
                db="gds", id=",".join(search_results["IdList"])
            )
            summaries = Entrez.read(summary_handle)
            summary_handle.close()

            results = []
            for summary in summaries:
                # Extract accession from summary
                accession = summary.get("Accession", "")
                if not accession:
                    continue

                results.append(
                    {
                        "id": accession,
                        "source": "geo",
                        "title": summary.get("title", ""),
                        "summary": summary.get("summary", ""),
                        "platform": summary.get("GPL", ""),
                        "samples": int(summary.get("n_samples", 0)),
                        "type": summary.get("gdsType", ""),
                    }
                )

            return results

        except Exception as e:
            logger.error(f"Error searching GEO: {e}")
            return []

    def get_metadata(self, dataset_id: str) -> Dict[str, Any]:
        """Get detailed metadata for a GEO dataset.

        Args:
            dataset_id: GEO dataset ID

        Returns:
            Detailed metadata dictionary
        """
        logger.info(f"Fetching detailed metadata for GEO dataset: {dataset_id}")

        try:
            # Use NCBI E-utilities to fetch detailed record
            fetch_url = f"{self.BASE_URL}/efetch.fcgi"
            params = {"db": "gds", "id": dataset_id, "retmode": "xml"}

            response = requests.get(fetch_url, params=params)
            response.raise_for_status()

            # Parse XML response
            root = ET.fromstring(response.text)

            # Extract metadata
            metadata = {
                "id": dataset_id,
                "source": "geo",
                "raw_xml": response.text,  # Keep raw XML for reference
            }

            # Try to extract common fields
            # This is simplified - real implementation would parse more thoroughly
            for elem in root.iter():
                if elem.tag == "title":
                    metadata["title"] = elem.text
                elif elem.tag == "summary":
                    metadata["summary"] = elem.text
                elif elem.tag == "type":
                    metadata["type"] = elem.text

            return metadata

        except Exception as e:
            logger.error(f"Error fetching metadata for {dataset_id}: {e}")
            # Fall back to basic fetch
            return self.fetch(dataset_id)

    def get_sample_info(self, dataset_id: str) -> List[Dict[str, Any]]:
        """Get sample information for a GEO dataset.

        Args:
            dataset_id: GEO dataset ID

        Returns:
            List of sample information dictionaries
        """
        logger.info(f"Fetching sample info for GEO dataset: {dataset_id}")

        # For MVP, return mock data
        # In production, this would parse the actual sample data
        return [
            {
                "sample_id": f"GSM{i}",
                "title": f"Sample {i}",
                "source": "geo",
                "characteristics": {},
            }
            for i in range(1, 5)
        ]
