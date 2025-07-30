"""Pipeline generator for creating Snakemake workflows."""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
from llmomics.core.config import config
from llmomics.pipeline.templates import PIPELINE_TEMPLATES


logger = logging.getLogger(__name__)


class PipelineGenerator:
    """Generator for creating Snakemake pipelines from specifications."""

    def __init__(self):
        """Initialize pipeline generator."""
        self.template_dir = config.template_dir
        self.output_dir = config.output_dir

        # Set up Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def generate(
        self,
        pipeline_type: str,
        analysis_type: str,
        dataset_info: Optional[Dict[str, Any]] = None,
        parameters: Optional[Dict[str, Any]] = None,
        custom_steps: Optional[List[Dict[str, Any]]] = None,
    ) -> Path:
        """Generate a Snakemake pipeline.

        Args:
            pipeline_type: Type of pipeline (e.g., rna-seq, chip-seq)
            analysis_type: Type of analysis (e.g., differential-expression)
            dataset_info: Information about the dataset
            parameters: Analysis parameters
            custom_steps: Custom pipeline steps from LLM

        Returns:
            Path to the generated Snakefile
        """
        logger.info(f"Generating {pipeline_type} pipeline for {analysis_type}")

        # Prepare context for template
        context = {
            "pipeline_type": pipeline_type,
            "analysis_type": analysis_type,
            "dataset": dataset_info or {},
            "params": parameters or {},
            "custom_steps": custom_steps or [],
            "generated_date": datetime.now().isoformat(),
            "llmomics_version": "0.1.0",
        }

        # Select appropriate template
        template_name = self._select_template(pipeline_type, analysis_type)

        if template_name in PIPELINE_TEMPLATES:
            # Use built-in template
            snakefile_content = PIPELINE_TEMPLATES[template_name].format(**context)
        else:
            # Try to load from file
            try:
                template = self.env.get_template(f"{template_name}.smk")
                snakefile_content = template.render(**context)
            except Exception as e:
                logger.warning(f"Template not found, using generic template: {e}")
                snakefile_content = self._generate_generic_pipeline(context)

        # Create output directory
        pipeline_name = f"{pipeline_type}_{analysis_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        pipeline_dir = self.output_dir / pipeline_name
        pipeline_dir.mkdir(parents=True, exist_ok=True)

        # Write Snakefile
        snakefile_path = pipeline_dir / "Snakefile"
        snakefile_path.write_text(snakefile_content)

        # Write configuration file
        config_path = pipeline_dir / "config.yaml"
        self._write_config(config_path, context)

        # Write sample sheet if dataset info is provided
        if dataset_info and "samples" in dataset_info:
            samples_path = pipeline_dir / "samples.tsv"
            self._write_samples(samples_path, dataset_info["samples"])

        # Write README
        readme_path = pipeline_dir / "README.md"
        self._write_readme(readme_path, context)

        logger.info(f"Pipeline generated successfully at: {pipeline_dir}")
        return snakefile_path

    def generate_from_plan(self, plan: str, metadata: Dict[str, Any]) -> Path:
        """Generate a pipeline from an LLM-generated plan.

        Args:
            plan: LLM-generated pipeline plan
            metadata: Additional metadata (query analysis, dataset info, etc.)

        Returns:
            Path to the generated Snakefile
        """
        logger.info("Generating pipeline from LLM plan")

        # Parse the plan to extract steps
        steps = self._parse_plan(plan)

        # Generate the pipeline
        return self.generate(
            pipeline_type=metadata.get("pipeline_type", "custom"),
            analysis_type=metadata.get("analysis_type", "custom"),
            dataset_info=metadata.get("dataset_info"),
            parameters=metadata.get("parameters"),
            custom_steps=steps,
        )

    def _select_template(self, pipeline_type: str, analysis_type: str) -> str:
        """Select the appropriate template based on pipeline and analysis type."""
        # Map common combinations to templates
        template_map = {
            ("rna-seq", "differential-expression"): "rnaseq_deseq2",
            ("chip-seq", "peak-calling"): "chipseq_macs2",
            ("variant-calling", "variant-calling"): "variant_gatk",
        }

        return template_map.get((pipeline_type, analysis_type), "generic")

    def _generate_generic_pipeline(self, context: Dict[str, Any]) -> str:
        """Generate a generic pipeline when no specific template is available."""
        pipeline = f"""# Generated by LLMomics v{context['llmomics_version']}
# Date: {context['generated_date']}
# Pipeline Type: {context['pipeline_type']}
# Analysis Type: {context['analysis_type']}

import os
from pathlib import Path

# Configuration
configfile: "config.yaml"

# Working directory
workdir: config.get("workdir", ".")

# Input/output directories
INPUT_DIR = Path(config.get("input_dir", "input"))
OUTPUT_DIR = Path(config.get("output_dir", "output"))
LOG_DIR = Path(config.get("log_dir", "logs"))

# Create directories
for dir_path in [OUTPUT_DIR, LOG_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# Default rule
rule all:
    input:
        OUTPUT_DIR / "analysis_complete.txt"

"""

        # Add custom steps if provided
        if context.get("custom_steps"):
            for i, step in enumerate(context["custom_steps"]):
                rule_name = step.get("name", f"step_{i+1}")
                pipeline += f"""
rule {rule_name}:
    input:
        {step.get('input', 'INPUT_DIR / "data.txt"')}
    output:
        {step.get('output', f'OUTPUT_DIR / "{rule_name}_output.txt"')}
    log:
        LOG_DIR / "{rule_name}.log"
    shell:
        '''
        {step.get('command', f'echo "Running {rule_name}" > {{output}}')}
        '''
"""

        # Add completion rule
        pipeline += """
rule complete_analysis:
    input:
        # Add all final outputs here
    output:
        OUTPUT_DIR / "analysis_complete.txt"
    shell:
        "echo 'Analysis completed successfully' > {output}"
"""

        return pipeline

    def _parse_plan(self, plan: str) -> List[Dict[str, Any]]:
        """Parse an LLM-generated plan into pipeline steps."""
        # This is a simplified parser
        # In production, would use more sophisticated parsing
        steps = []

        # Try to identify steps in the plan
        lines = plan.split("\n")
        current_step = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Look for step indicators
            if any(
                line.lower().startswith(prefix) for prefix in ["step", "1.", "2.", "3."]
            ):
                if current_step:
                    steps.append(current_step)
                current_step = {
                    "name": f"step_{len(steps) + 1}",
                    "description": line,
                    "command": "echo 'Step placeholder'",
                }
            elif current_step and line:
                # Add to description
                current_step["description"] += f" {line}"

        if current_step:
            steps.append(current_step)

        return steps

    def _write_config(self, path: Path, context: Dict[str, Any]) -> None:
        """Write configuration file."""
        import yaml

        config_data = {
            "pipeline_type": context["pipeline_type"],
            "analysis_type": context["analysis_type"],
            "generated_date": context["generated_date"],
            "llmomics_version": context["llmomics_version"],
            "workdir": ".",
            "input_dir": "input",
            "output_dir": "output",
            "log_dir": "logs",
            "threads": {
                "default": 1,
                "alignment": 8,
                "sorting": 4,
            },
            "params": context.get("params", {}),
        }

        # Add dataset info if available
        if context.get("dataset"):
            config_data["dataset"] = context["dataset"]

        with open(path, "w") as f:
            yaml.dump(config_data, f, default_flow_style=False)

    def _write_samples(self, path: Path, samples: List[Dict[str, Any]]) -> None:
        """Write sample sheet."""
        import pandas as pd

        # Convert to DataFrame and write as TSV
        df = pd.DataFrame(samples)
        df.to_csv(path, sep="\t", index=False)

    def _write_readme(self, path: Path, context: Dict[str, Any]) -> None:
        """Write README file."""
        readme = f"""# {context['pipeline_type'].title()} Pipeline

Generated by LLMomics v{context['llmomics_version']} on {context['generated_date']}

## Overview

This pipeline performs {context['analysis_type']} analysis for {context['pipeline_type']} data.

## Requirements

- Snakemake >= 7.0
- Conda/Mamba (recommended for environment management)

## Usage

1. Install Snakemake:
   ```bash
   conda install -c conda-forge -c bioconda snakemake
   ```

2. Prepare your input data in the `input/` directory

3. Run the pipeline:
   ```bash
   snakemake --use-conda --cores 8
   ```

## Configuration

Edit `config.yaml` to customize pipeline parameters.

## Output

Results will be saved in the `output/` directory.

## Dataset Information

"""

        if context.get("dataset"):
            dataset = context["dataset"]
            readme += f"""
- **ID**: {dataset.get('id', 'N/A')}
- **Source**: {dataset.get('source', 'N/A')}
- **Title**: {dataset.get('title', 'N/A')}
- **Samples**: {dataset.get('samples', 'N/A')}
"""

        path.write_text(readme)
