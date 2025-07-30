"""
LLMomics: LLM-powered bioinformatics pipeline generation from natural language.

A Python library that leverages Large Language Models to automatically create
bioinformatics pipelines from natural language queries, making omics analyses
accessible to researchers without extensive computational backgrounds.
"""

__version__ = "0.1.0"
__author__ = "Allan Paulo"
__email__ = "allanpaulo2@hotmail.com"

from llmomics.core import LLMProvider
from llmomics.data import DataFetcher
from llmomics.pipeline import PipelineGenerator

__all__ = ["LLMProvider", "DataFetcher", "PipelineGenerator"]
