"""Command-line interface for LLMomics."""

import sys
import logging
from pathlib import Path
import click
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from llmomics import __version__
from llmomics.core import LLMProvider
from llmomics.core.query_parser import QueryParser
from llmomics.data import DataFetcher
from llmomics.pipeline import PipelineGenerator


# Set up rich console
console = Console()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(console=console, rich_tracebacks=True)],
)
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(__version__, prog_name="LLMomics")
def cli():
    """LLMomics - LLM-powered bioinformatics pipeline generation.

    Generate complete bioinformatics pipelines from natural language queries.
    """
    pass


@cli.command()
@click.argument("query")
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(path_type=Path),
    help="Output directory for generated pipeline",
)
@click.option(
    "--provider",
    "-p",
    type=click.Choice(["openai"]),
    default="openai",
    help="LLM provider to use",
)
@click.option("--no-fetch-data", is_flag=True, help="Skip data fetching step")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def run(
    query: str, output_dir: Path, provider: str, no_fetch_data: bool, verbose: bool
):
    """Generate a bioinformatics pipeline from a natural language query.

    Example:
        llmomics run "Perform differential expression analysis with DESeq2 on GSE123456"
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    console.print(
        Panel.fit(
            f"[bold blue]LLMomics v{__version__}[/bold blue]\n"
            f"Generating pipeline from query: [italic]{query}[/italic]",
            title="Welcome to LLMomics",
        )
    )

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:

            # Step 1: Parse query
            task = progress.add_task("[cyan]Parsing query...", total=None)
            parser = QueryParser()
            parsed_query = parser.parse(query)
            progress.update(task, completed=True)

            # Display parsed information
            _display_parsed_query(parsed_query)

            # Step 2: Analyze with LLM
            task = progress.add_task("[cyan]Analyzing query with LLM...", total=None)
            llm = LLMProvider(provider=provider)
            analysis = llm.analyze_query(query)
            progress.update(task, completed=True)

            # Step 3: Fetch dataset information
            dataset_info = None
            if not no_fetch_data and (
                parsed_query.dataset_ids or analysis.get("dataset_ids")
            ):
                task = progress.add_task(
                    "[cyan]Fetching dataset information...", total=None
                )
                fetcher = DataFetcher()
                dataset_ids = parsed_query.dataset_ids or analysis.get(
                    "dataset_ids", []
                )

                if dataset_ids:
                    dataset_id = dataset_ids[0]  # Use first dataset
                    try:
                        dataset_info = fetcher.fetch(dataset_id)
                        console.print(
                            f"[green]Found dataset:[/green] {dataset_info['title']}"
                        )
                    except Exception as e:
                        console.print(
                            f"[yellow]Warning:[/yellow] Could not fetch dataset {dataset_id}: {e}"
                        )

                progress.update(task, completed=True)

            # Step 4: Generate pipeline plan
            task = progress.add_task("[cyan]Generating pipeline plan...", total=None)
            plan = llm.generate_pipeline_plan(analysis)
            progress.update(task, completed=True)

            # Step 5: Generate Snakemake pipeline
            task = progress.add_task("[cyan]Creating Snakemake pipeline...", total=None)
            generator = PipelineGenerator()

            # Override output directory if specified
            if output_dir:
                generator.output_dir = output_dir

            # Prepare metadata
            metadata = {
                "pipeline_type": analysis.get(
                    "pipeline_type", parsed_query.pipeline_type
                ),
                "analysis_type": analysis.get(
                    "analysis_type", parsed_query.analysis_type
                ),
                "dataset_info": dataset_info,
                "parameters": {
                    **parsed_query.parameters,
                    **analysis.get("parameters", {}),
                },
            }

            snakefile_path = generator.generate_from_plan(plan, metadata)
            progress.update(task, completed=True)

        # Success message
        pipeline_dir = snakefile_path.parent
        console.print("\n[bold green]Pipeline generated successfully![/bold green]")
        console.print(f"Location: [blue]{pipeline_dir}[/blue]\n")

        # Display next steps
        console.print(
            Panel(
                "[bold]Next steps:[/bold]\n\n"
                f"1. Navigate to the pipeline directory:\n"
                f"   [cyan]cd {pipeline_dir}[/cyan]\n\n"
                f"2. Review and edit the configuration:\n"
                f"   [cyan]nano config.yaml[/cyan]\n\n"
                f"3. Prepare your input data in the input/ directory\n\n"
                f"4. Run the pipeline:\n"
                f"   [cyan]snakemake --use-conda --cores 8[/cyan]",
                title="Getting Started",
            )
        )

    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        if verbose:
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.argument("dataset_id")
@click.option(
    "--database",
    "-d",
    type=click.Choice(["geo", "sra"]),
    help="Specify database (auto-detected if not provided)",
)
def fetch(dataset_id: str, database: str):
    """Fetch information about a dataset from public databases.

    Example:
        llmomics fetch GSE123456
    """
    console.print(f"[cyan]Fetching dataset: {dataset_id}[/cyan]")

    try:
        fetcher = DataFetcher()

        if database:
            # Use specific database
            dataset_info = fetcher._fetchers[database].fetch(dataset_id)
        else:
            # Auto-detect
            dataset_info = fetcher.fetch(dataset_id)

        # Display dataset information
        table = Table(title=f"Dataset: {dataset_id}")
        table.add_column("Field", style="cyan")
        table.add_column("Value")

        for key, value in dataset_info.items():
            if key != "raw_xml":  # Skip raw XML
                table.add_row(key.replace("_", " ").title(), str(value))

        console.print(table)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


@cli.command()
@click.argument("query")
@click.option(
    "--database",
    "-d",
    type=click.Choice(["geo", "sra", "all"]),
    default="all",
    help="Database to search",
)
@click.option("--limit", "-l", type=int, default=10, help="Maximum number of results")
def search(query: str, database: str, limit: int):
    """Search for datasets in public databases.

    Example:
        llmomics search "RNA-seq liver cancer"
    """
    console.print(f"[cyan]Searching for: {query}[/cyan]")

    try:
        fetcher = DataFetcher()

        if database == "all":
            results = fetcher.search(query, limit=limit)
        else:
            results = fetcher.search(query, database=database, limit=limit)

        if not results:
            console.print("[yellow]No results found.[/yellow]")
            return

        # Display results
        table = Table(title=f"Search Results ({len(results)} found)")
        table.add_column("ID", style="cyan")
        table.add_column("Source")
        table.add_column("Title")
        table.add_column("Type/Strategy")

        for result in results:
            table.add_row(
                result.get("id", ""),
                result.get("source", ""),
                result.get("title", "")[:60] + "...",
                result.get("type", result.get("library_strategy", "")),
            )

        console.print(table)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


@cli.command()
def config():
    """Display current configuration."""
    from llmomics.core.config import config

    table = Table(title="LLMomics Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value")
    table.add_column("Source")

    # LLM settings
    table.add_row("LLM Provider", config.llm_provider, "config/env")
    table.add_row("OpenAI Model", config.openai_model, "config/env")
    table.add_row(
        "OpenAI API Key", "***" if config.openai_api_key else "Not set", "env"
    )

    # NCBI settings
    table.add_row("NCBI Email", config.ncbi_email or "Not set", "env")
    table.add_row("NCBI API Key", "***" if config.ncbi_api_key else "Not set", "env")

    # Directories
    table.add_row("Output Directory", str(config.output_dir), "config")
    table.add_row("Template Directory", str(config.template_dir), "config")

    console.print(table)

    if not config.openai_api_key:
        console.print(
            "\n[yellow]Warning: OpenAI API key not set. Set OPENAI_API_KEY environment variable.[/yellow]"
        )


def _display_parsed_query(parsed_query):
    """Display parsed query information."""
    table = Table(title="Query Analysis")
    table.add_column("Component", style="cyan")
    table.add_column("Value")

    if parsed_query.pipeline_type:
        table.add_row("Pipeline Type", parsed_query.pipeline_type)
    if parsed_query.analysis_type:
        table.add_row("Analysis Type", parsed_query.analysis_type)
    if parsed_query.dataset_ids:
        table.add_row("Dataset IDs", ", ".join(parsed_query.dataset_ids))
    if parsed_query.tools:
        table.add_row("Tools", ", ".join(parsed_query.tools))
    if parsed_query.parameters:
        params_str = ", ".join(f"{k}={v}" for k, v in parsed_query.parameters.items())
        table.add_row("Parameters", params_str)

    console.print(table)


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
