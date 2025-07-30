"""LLM provider interface for communication with language models."""

import json
import logging
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from openai import OpenAI
from llmomics.core.config import config


logger = logging.getLogger(__name__)


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate a response from the LLM."""
        pass

    @abstractmethod
    def generate_structured(
        self, prompt: str, schema: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        """Generate a structured response matching the provided schema."""
        pass


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider implementation."""

    def __init__(self, api_key: str, model: str = "gpt-4"):
        """Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key
            model: Model name to use (default: gpt-4)
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        logger.info(f"Initialized OpenAI provider with model: {model}")

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate a response from OpenAI.

        Args:
            prompt: The prompt to send to the model
            **kwargs: Additional parameters for the API call

        Returns:
            The generated response text
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a bioinformatics expert assistant that helps create analysis pipelines.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 2000),
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating response from OpenAI: {e}")
            raise

    def generate_structured(
        self, prompt: str, schema: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        """Generate a structured response matching the provided schema.

        Args:
            prompt: The prompt to send to the model
            schema: JSON schema for the expected response
            **kwargs: Additional parameters for the API call

        Returns:
            Parsed JSON response matching the schema
        """
        system_prompt = f"""You are a bioinformatics expert assistant that helps create analysis pipelines.
        You must respond with valid JSON that matches this schema:
        {json.dumps(schema, indent=2)}
        
        IMPORTANT: Your response must be valid JSON only, no additional text or explanation.
        """

        # Models that support JSON mode
        json_mode_models = [
            "gpt-4-turbo",
            "gpt-4-turbo-preview",
            "gpt-4-0125-preview",
            "gpt-4-1106-preview",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-1106",
        ]

        # Use JSON mode if model supports it, otherwise use careful prompting
        use_json_mode = self.model in json_mode_models

        try:
            # Prepare the API call parameters
            api_params = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                "temperature": kwargs.get("temperature", 0.3),
                "max_tokens": kwargs.get("max_tokens", 2000),
            }

            # Add response_format only for compatible models
            if use_json_mode:
                api_params["response_format"] = {"type": "json_object"}

            response = self.client.chat.completions.create(**api_params)

            # Parse the response
            content = response.choices[0].message.content.strip()

            # If not using JSON mode, try to extract JSON from the response
            if not use_json_mode:
                # Look for JSON in the response (handle cases where model adds extra text)
                import re

                json_match = re.search(r"\{.*\}", content, re.DOTALL)
                if json_match:
                    content = json_match.group()

            result = json.loads(content)
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response content: {content}")

            # Fallback: try a simpler approach
            try:
                logger.info("Attempting fallback JSON parsing...")
                # Try to fix common JSON issues
                fixed_content = content.replace("'", '"')  # Replace single quotes
                fixed_content = re.sub(
                    r",\s*}", "}", fixed_content
                )  # Remove trailing commas
                result = json.loads(fixed_content)
                return result
            except:
                # If all else fails, return a basic structure
                logger.warning("Using fallback response structure")
                return {
                    "pipeline_type": "rna-seq",
                    "analysis_type": "differential-expression",
                    "tools": [],
                    "parameters": {},
                    "dataset_ids": [],
                }

        except Exception as e:
            logger.error(f"Error generating structured response from OpenAI: {e}")
            raise


class LLMProvider:
    """Main LLM provider interface."""

    def __init__(self, provider: Optional[str] = None):
        """Initialize LLM provider.

        Args:
            provider: Provider name (default: from config)
        """
        provider = provider or config.llm_provider

        if provider == "openai":
            config.validate_llm_config()
            llm_config = config.get_llm_config()
            self._provider = OpenAIProvider(
                api_key=llm_config["api_key"], model=llm_config["model"]
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    def analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze a natural language query to extract pipeline requirements.

        Args:
            query: Natural language query

        Returns:
            Structured analysis of the query
        """
        schema = {
            "type": "object",
            "properties": {
                "pipeline_type": {
                    "type": "string",
                    "description": "Type of bioinformatics pipeline (e.g., rna-seq, chip-seq, variant-calling)",
                },
                "analysis_type": {
                    "type": "string",
                    "description": "Specific analysis to perform (e.g., differential-expression, peak-calling)",
                },
                "dataset_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Dataset IDs mentioned (e.g., GSE123456)",
                },
                "tools": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific tools mentioned (e.g., DESeq2, STAR, samtools)",
                },
                "parameters": {
                    "type": "object",
                    "description": "Additional parameters extracted from the query",
                },
            },
            "required": ["pipeline_type", "analysis_type"],
        }

        prompt = f"""Analyze this bioinformatics query and extract key information:

Query: {query}

Extract:
1. The type of bioinformatics pipeline needed
2. The specific analysis to perform
3. Any dataset IDs mentioned (GEO, SRA, etc.)
4. Specific tools or methods mentioned
5. Any parameters or specifications
"""

        return self._provider.generate_structured(prompt, schema)

    def generate_pipeline_plan(self, analysis: Dict[str, Any]) -> str:
        """Generate a detailed pipeline plan based on the analysis.

        Args:
            analysis: Structured analysis from analyze_query

        Returns:
            Detailed pipeline plan
        """
        prompt = f"""Create a detailed bioinformatics pipeline plan based on this analysis:

Pipeline Type: {analysis['pipeline_type']}
Analysis Type: {analysis['analysis_type']}
Tools: {', '.join(analysis.get('tools', []))}
Datasets: {', '.join(analysis.get('dataset_ids', []))}

Provide a step-by-step plan including:
1. Data acquisition and preprocessing steps
2. Quality control steps
3. Main analysis steps
4. Output generation and visualization
5. Required software and dependencies

Format the plan in a clear, structured way that can be converted to a Snakemake workflow.
"""

        return self._provider.generate(prompt)

    def generate(self, prompt: str, **kwargs) -> str:
        """Direct generation method.

        Args:
            prompt: The prompt to send to the model
            **kwargs: Additional parameters

        Returns:
            Generated response
        """
        return self._provider.generate(prompt, **kwargs)
