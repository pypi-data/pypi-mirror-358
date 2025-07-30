"""Query parser for extracting structured information from natural language queries."""

import re
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class ParsedQuery:
    """Structured representation of a parsed query."""

    raw_query: str
    pipeline_type: Optional[str] = None
    analysis_type: Optional[str] = None
    dataset_ids: List[str] = None
    tools: List[str] = None
    parameters: Dict[str, Any] = None

    def __post_init__(self):
        if self.dataset_ids is None:
            self.dataset_ids = []
        if self.tools is None:
            self.tools = []
        if self.parameters is None:
            self.parameters = {}


class QueryParser:
    """Parser for natural language bioinformatics queries."""

    # Common patterns for dataset IDs
    DATASET_PATTERNS = {
        "geo": re.compile(r"GSE\d+", re.IGNORECASE),
        "sra": re.compile(r"SR[ARXP]\d+", re.IGNORECASE),
        "arrayexpress": re.compile(r"E-\w+-\d+", re.IGNORECASE),
    }

    # Common bioinformatics tools
    KNOWN_TOOLS = {
        "deseq2",
        "edger",
        "limma",
        "star",
        "hisat2",
        "bowtie2",
        "bwa",
        "samtools",
        "bcftools",
        "gatk",
        "fastqc",
        "trimmomatic",
        "cutadapt",
        "macs2",
        "homer",
        "bedtools",
        "featurecounts",
        "htseq",
        "salmon",
        "kallisto",
        "stringtie",
        "cufflinks",
        "tophat",
    }

    # Pipeline type keywords
    PIPELINE_KEYWORDS = {
        "rna-seq": ["rna-seq", "rnaseq", "transcriptome", "expression"],
        "chip-seq": ["chip-seq", "chipseq", "chromatin"],
        "atac-seq": ["atac-seq", "atacseq", "accessibility"],
        "variant-calling": ["variant", "snp", "mutation", "vcf"],
        "methylation": ["methylation", "bisulfite", "methylome"],
        "proteomics": ["proteomics", "mass-spec", "ms/ms"],
    }

    # Analysis type keywords
    ANALYSIS_KEYWORDS = {
        "differential-expression": [
            "differential",
            "degs",
            "expression",
            "de analysis",
        ],
        "peak-calling": ["peak", "peaks", "enrichment"],
        "variant-calling": ["variant", "calling", "snp"],
        "alignment": ["align", "alignment", "mapping"],
        "quantification": ["quantify", "quantification", "count"],
        "quality-control": ["qc", "quality", "control"],
    }

    def parse(self, query: str) -> ParsedQuery:
        """Parse a natural language query.

        Args:
            query: Natural language query

        Returns:
            ParsedQuery object with extracted information
        """
        logger.info(f"Parsing query: {query}")

        # Convert to lowercase for pattern matching
        query_lower = query.lower()

        # Extract dataset IDs
        dataset_ids = self._extract_dataset_ids(query)

        # Extract tools
        tools = self._extract_tools(query_lower)

        # Determine pipeline type
        pipeline_type = self._determine_pipeline_type(query_lower)

        # Determine analysis type
        analysis_type = self._determine_analysis_type(query_lower)

        # Extract parameters
        parameters = self._extract_parameters(query)

        parsed = ParsedQuery(
            raw_query=query,
            pipeline_type=pipeline_type,
            analysis_type=analysis_type,
            dataset_ids=dataset_ids,
            tools=tools,
            parameters=parameters,
        )

        logger.info(f"Parsed query: {parsed}")
        return parsed

    def _extract_dataset_ids(self, query: str) -> List[str]:
        """Extract dataset IDs from query."""
        dataset_ids = []

        for source, pattern in self.DATASET_PATTERNS.items():
            matches = pattern.findall(query)
            for match in matches:
                dataset_ids.append(match.upper())

        return dataset_ids

    def _extract_tools(self, query_lower: str) -> List[str]:
        """Extract mentioned tools from query."""
        tools = []

        for tool in self.KNOWN_TOOLS:
            if tool in query_lower:
                tools.append(tool)

        return tools

    def _determine_pipeline_type(self, query_lower: str) -> Optional[str]:
        """Determine the pipeline type from query."""
        for pipeline_type, keywords in self.PIPELINE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in query_lower:
                    return pipeline_type

        return None

    def _determine_analysis_type(self, query_lower: str) -> Optional[str]:
        """Determine the analysis type from query."""
        for analysis_type, keywords in self.ANALYSIS_KEYWORDS.items():
            for keyword in keywords:
                if keyword in query_lower:
                    return analysis_type

        return None

    def _extract_parameters(self, query: str) -> Dict[str, Any]:
        """Extract additional parameters from query."""
        parameters = {}

        # Extract p-value threshold
        p_value_match = re.search(
            r"p[- ]?value[:\s<>=]+(\d*\.?\d+)", query, re.IGNORECASE
        )
        if p_value_match:
            parameters["p_value"] = float(p_value_match.group(1))

        # Extract fold change threshold
        fc_match = re.search(
            r"fold[- ]?change[:\s<>=]+(\d*\.?\d+)", query, re.IGNORECASE
        )
        if fc_match:
            parameters["fold_change"] = float(fc_match.group(1))

        # Extract FDR/q-value threshold
        fdr_match = re.search(
            r"(?:fdr|q[- ]?value)[:\s<>=]+(\d*\.?\d+)", query, re.IGNORECASE
        )
        if fdr_match:
            parameters["fdr"] = float(fdr_match.group(1))

        return parameters
