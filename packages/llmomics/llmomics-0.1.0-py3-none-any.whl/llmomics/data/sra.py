"""SRA (Sequence Read Archive) data fetcher."""

import logging
from typing import Dict, Any, List
from Bio import Entrez
from llmomics.core.config import config


logger = logging.getLogger(__name__)


class SRAFetcher:
    """Fetcher for SRA (Sequence Read Archive) data."""

    def __init__(self):
        """Initialize SRA fetcher."""
        # Set Entrez email (required by NCBI)
        if config.ncbi_email:
            Entrez.email = config.ncbi_email
        else:
            Entrez.email = "user@example.com"
            logger.warning("NCBI email not set. Using default email.")

        # Set API key if available
        if config.ncbi_api_key:
            Entrez.api_key = config.ncbi_api_key

    def fetch(self, dataset_id: str) -> Dict[str, Any]:
        """Fetch basic dataset information from SRA.

        Args:
            dataset_id: SRA dataset ID (e.g., SRR123456, SRP123456)

        Returns:
            Dictionary containing dataset information
        """
        logger.info(f"Fetching SRA dataset: {dataset_id}")

        try:
            # Search for the dataset in SRA
            search_handle = Entrez.esearch(db="sra", term=dataset_id)
            search_results = Entrez.read(search_handle)
            search_handle.close()

            if not search_results["IdList"]:
                raise ValueError(f"Dataset {dataset_id} not found in SRA")

            # Fetch summary information
            summary_handle = Entrez.esummary(db="sra", id=search_results["IdList"][0])
            summary = Entrez.read(summary_handle)[0]
            summary_handle.close()

            # Parse the summary to extract relevant information
            exp_xml = summary.get("ExpXml", "")

            return {
                "id": dataset_id,
                "source": "sra",
                "title": summary.get("Title", ""),
                "organism": self._extract_organism(exp_xml),
                "platform": self._extract_platform(exp_xml),
                "library_strategy": self._extract_library_strategy(exp_xml),
                "submission_date": summary.get("CreateDate", ""),
                "update_date": summary.get("UpdateDate", ""),
            }

        except Exception as e:
            logger.error(f"Error fetching SRA dataset {dataset_id}: {e}")
            raise

    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for datasets in SRA.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of dataset information dictionaries
        """
        logger.info(f"Searching SRA for: {query}")

        try:
            # Search SRA
            search_handle = Entrez.esearch(db="sra", term=query, retmax=limit)
            search_results = Entrez.read(search_handle)
            search_handle.close()

            if not search_results["IdList"]:
                return []

            # Fetch summaries
            summary_handle = Entrez.esummary(
                db="sra", id=",".join(search_results["IdList"])
            )
            summaries = Entrez.read(summary_handle)
            summary_handle.close()

            results = []
            for summary in summaries:
                # Extract relevant information
                exp_xml = summary.get("ExpXml", "")
                runs = self._extract_runs(exp_xml)

                for run in runs:
                    results.append(
                        {
                            "id": run,
                            "source": "sra",
                            "title": summary.get("Title", ""),
                            "organism": self._extract_organism(exp_xml),
                            "platform": self._extract_platform(exp_xml),
                            "library_strategy": self._extract_library_strategy(exp_xml),
                        }
                    )

            return results[:limit]

        except Exception as e:
            logger.error(f"Error searching SRA: {e}")
            return []

    def get_metadata(self, dataset_id: str) -> Dict[str, Any]:
        """Get detailed metadata for an SRA dataset.

        Args:
            dataset_id: SRA dataset ID

        Returns:
            Detailed metadata dictionary
        """
        logger.info(f"Fetching detailed metadata for SRA dataset: {dataset_id}")

        # For MVP, return enhanced basic data
        # In production, this would fetch and parse full XML records
        metadata = self.fetch(dataset_id)
        metadata.update(
            {
                "detailed": True,
                "fastq_urls": self._generate_fastq_urls(dataset_id),
                "experiment_type": "RNA-Seq",  # Mock data
                "read_length": "150",  # Mock data
                "paired_end": True,  # Mock data
            }
        )

        return metadata

    def get_sample_info(self, dataset_id: str) -> List[Dict[str, Any]]:
        """Get sample information for an SRA dataset.

        Args:
            dataset_id: SRA dataset ID

        Returns:
            List of sample information dictionaries
        """
        logger.info(f"Fetching sample info for SRA dataset: {dataset_id}")

        # For MVP, return mock data
        # In production, this would parse actual sample metadata
        return [
            {
                "sample_id": f"SRS{i}",
                "run_id": f"SRR{i}",
                "title": f"Sample {i}",
                "source": "sra",
                "attributes": {
                    "tissue": "liver",
                    "treatment": "control" if i % 2 == 0 else "treated",
                },
            }
            for i in range(100001, 100005)
        ]

    def _extract_organism(self, exp_xml: str) -> str:
        """Extract organism from ExpXml string."""
        # Simplified extraction - in production would use proper XML parsing
        if "Homo sapiens" in exp_xml:
            return "Homo sapiens"
        elif "Mus musculus" in exp_xml:
            return "Mus musculus"
        else:
            return "Unknown"

    def _extract_platform(self, exp_xml: str) -> str:
        """Extract sequencing platform from ExpXml string."""
        # Simplified extraction
        if "ILLUMINA" in exp_xml:
            return "Illumina"
        elif "PACBIO" in exp_xml:
            return "PacBio"
        elif "OXFORD_NANOPORE" in exp_xml:
            return "Oxford Nanopore"
        else:
            return "Unknown"

    def _extract_library_strategy(self, exp_xml: str) -> str:
        """Extract library strategy from ExpXml string."""
        # Simplified extraction
        if "RNA-Seq" in exp_xml:
            return "RNA-Seq"
        elif "ChIP-Seq" in exp_xml:
            return "ChIP-Seq"
        elif "WGS" in exp_xml:
            return "WGS"
        else:
            return "Unknown"

    def _extract_runs(self, exp_xml: str) -> List[str]:
        """Extract run accessions from ExpXml string."""
        # Simplified extraction - returns mock data
        # In production would parse XML properly
        import re

        runs = re.findall(r"SRR\d+", exp_xml)
        return runs if runs else ["SRR000001"]

    def _generate_fastq_urls(self, dataset_id: str) -> List[str]:
        """Generate potential FASTQ download URLs."""
        # These are example URLs - actual implementation would determine correct paths
        base_url = "ftp://ftp.sra.ebi.ac.uk/vol1/fastq"

        if dataset_id.startswith("SRR"):
            # Extract the numeric part
            srr_num = dataset_id[3:]
            if len(srr_num) >= 6:
                dir1 = srr_num[:6]
                return [
                    f"{base_url}/{dir1}/{dataset_id}/{dataset_id}_1.fastq.gz",
                    f"{base_url}/{dir1}/{dataset_id}/{dataset_id}_2.fastq.gz",
                ]

        return []
