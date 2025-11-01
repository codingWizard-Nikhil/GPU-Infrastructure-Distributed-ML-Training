import click
import requests
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from secrets import API_URL

console = Console()


@click.group()
def cli():
    """Remote Compute Client - Submit and manage jobs"""
    pass


@cli.command()
@click.argument('code')
def submit(code):
    """Submit a new job"""
    try:
        response = requests.post(
            f"{API_URL}/jobs",
            json={"code": code}
        )
        response.raise_for_status()
        job = response.json()
        
        console.print(f"✓ Job submitted successfully!", style="bold green")
        console.print(f"Job ID: {job['id']}", style="cyan")
        console.print(f"Status: {job['status']}", style="yellow")
        
    except requests.exceptions.RequestException as e:
        console.print(f"✗ Error submitting job: {e}", style="bold red")


@cli.command()
@click.argument('job_id')
def get(job_id):
    """Get job status and results"""
    try:
        response = requests.get(f"{API_URL}/jobs/{job_id}")
        response.raise_for_status()
        job = response.json()
        
        console.print(f"\n[bold]Job {job['id']}[/bold]")
        console.print(f"Status: [{get_status_color(job['status'])}]{job['status']}[/]")
        console.print(f"Submitted: {job['submitted_at']}")
        
        if job['started_at']:
            console.print(f"Started: {job['started_at']}")
        if job['completed_at']:
            console.print(f"Completed: {job['completed_at']}")
        
        console.print(f"\n[bold]Code:[/bold]\n{job['code']}")
        
        if job['result']:
            console.print(f"\n[bold green]Result:[/bold green]\n{job['result']}")
        
        if job['error']:
            console.print(f"\n[bold red]Error:[/bold red]\n{job['error']}")
            
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            console.print(f"✗ Job not found: {job_id}", style="bold red")
        else:
            console.print(f"✗ Error: {e}", style="bold red")
    except requests.exceptions.RequestException as e:
        console.print(f"✗ Error: {e}", style="bold red")


@cli.command()
def list():
    """List all jobs"""
    try:
        response = requests.get(f"{API_URL}/jobs")
        response.raise_for_status()
        jobs = response.json()
        
        if not jobs:
            console.print("No jobs found.", style="yellow")
            return
        
        table = Table(title="Jobs")
        table.add_column("ID", style="cyan")
        table.add_column("Status", style="magenta")
        table.add_column("Submitted", style="green")
        table.add_column("Code", style="white")
        
        for job in jobs:
            # Truncate code if too long
            code = job['code'][:50] + "..." if len(job['code']) > 50 else job['code']
            table.add_row(
                job['id'],
                job['status'],
                job['submitted_at'][:19],
                code
            )
        
        console.print(table)
        
    except requests.exceptions.RequestException as e:
        console.print(f"✗ Error listing jobs: {e}", style="bold red")


def get_status_color(status):
    """Get color for job status"""
    colors = {
        "pending": "yellow",
        "running": "blue",
        "completed": "green",
        "failed": "red"
    }
    return colors.get(status, "white")


if __name__ == "__main__":
    cli()