"""Command line interface for FastAPI CLI."""

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

from .generator import FastAPIProjectGenerator

console = Console()


def print_banner() -> None:
    """Print the CLI banner."""
    banner = """
    ██████╗  ██████╗  ████████╗ 
    ╚════██╗ ██╔══██╗ ██╔════╝
     ██████╔╝██║  ██║ ██║     
        ██║  ██████╔╝  ██║     
        ██║  ██║       ██╚════╗ 
    ██████╔╝ ██╚═╝     ██████═╝ 
"""
    console.print(Panel(banner, style="bold blue"))


@click.group()
@click.version_option()
def cli() -> None:
    """DreiPC Python CLI - Create FastAPI projects with best practices."""
    pass


@cli.command()
@click.argument("project_name")
@click.option(
    "--author",
    default="Your Name",
    help="Author name for the project",
)
@click.option(
    "--email",
    default="your.email@example.com",
    help="Author email for the project",
)
@click.option(
    "--description",
    help="Project description",
)
@click.option(
    "--interactive",
    "-i",
    is_flag=True,
    help="Interactive mode for configuration",
)
def create(
    project_name: str,
    author: str,
    email: str,
    description: str,
    interactive: bool,
) -> None:
    """Create a new FastAPI project."""
    print_banner()
    
    # Validate project name
    if not project_name.replace("-", "").replace("_", "").isalnum():
        console.print(
            "[red]Error: Project name should contain only alphanumeric characters, hyphens, and underscores.[/red]"
        )
        sys.exit(1)
    
    # Check if directory already exists
    project_path = Path.cwd() / project_name
    if project_path.exists():
        if not Confirm.ask(f"Directory '{project_name}' already exists. Continue?"):
            console.print("[yellow]Operation cancelled.[/yellow]")
            sys.exit(0)
    
    # Interactive mode
    if interactive:
        console.print("\n[bold]Project Configuration[/bold]")
        
        if not description:
            description = Prompt.ask(
                "Project description",
                default=f"A FastAPI application - {project_name}",
            )
        
        author = Prompt.ask("Author name", default=author)
        email = Prompt.ask("Author email", default=email)
    
    if not description:
        description = f"A FastAPI application - {project_name}"
    
    # Create configuration
    config = {
        "project_name": project_name,
        "description": description,
        "author": author,
        "email": email,
    }
    
    # Show configuration
    console.print(f"\n[cyan]Creating project:[/cyan] {project_name}")
    console.print(f"[cyan]Description:[/cyan] {description}")
    console.print(f"[cyan]Author:[/cyan] {author} <{email}>")
    
    if interactive and not Confirm.ask("\nProceed with project creation?"):
        console.print("[yellow]Operation cancelled.[/yellow]")
        sys.exit(0)
    
    # Generate project
    try:
        generator = FastAPIProjectGenerator(config)
        generator.create_project()
        
        console.print(f"\n[green]✅ Project '{project_name}' created successfully![/green]")
        _show_next_steps(project_name)
        
    except Exception as e:
        console.print(f"[red]❌ Error creating project: {e}[/red]")
        sys.exit(1)


def _show_next_steps(project_name: str) -> None:
    """Show next steps after project creation."""
    steps = f"""
[bold green]Next Steps:[/bold green]

1. Navigate to your project:
   [cyan]cd {project_name}[/cyan]

2. Install dependencies:
   [cyan]poetry install[/cyan]

3. Copy environment variables:
   [cyan]cp .env.example .env[/cyan]

4. Run the application:
   [cyan]poetry run uvicorn app.main:app --reload[/cyan]

5. Open in browser:
   [cyan]http://localhost:8000/docs[/cyan]

[bold]Available commands:[/bold]
• [cyan]make run[/cyan]        - Start the development server
• [cyan]make test[/cyan]       - Run tests
• [cyan]make format[/cyan]     - Format code
• [cyan]make lint[/cyan]       - Lint code

[bold yellow]Happy coding! 🚀[/bold yellow]
    """
    console.print(Panel(steps, expand=False))


def main() -> None:
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()