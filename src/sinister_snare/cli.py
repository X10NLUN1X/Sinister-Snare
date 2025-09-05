# sinister_snare/cli.py
import click
from rich.console import Console

# KORREKTUR: Absolute Importe, um PyInstaller-Probleme zu lösen
from sinister_snare import db_handler, scheduler, analyzer

console = Console()

@click.group()
def cli():
    """Sinister Snare - Ein Tool zur Analyse von Handelsrouten."""
    pass

@cli.command()
def initdb():
    """Initialisiert die Datenbank."""
    db_handler.init_db()
    console.print("[green]Datenbank erfolgreich initialisiert.[/green]")

@cli.command()
def update():
    """Aktualisiert die Handelsdaten von der API."""
    scheduler.update_job()

@cli.command()
def show():
    """Zeigt die Top 5 der profitabelsten Routen an."""
    console.print("[bold cyan]Lade und analysiere die neuesten Daten...[/bold cyan]")
    
    db_data = db_handler.get_latest_routes_from_db()
    if db_data.empty:
        console.print("[bold red]Datenbank ist leer. Führen Sie zuerst 'update' aus.[/bold red]")
        return
        
    analyzed_data = analyzer.analyze_routes(db_data)
    
    console.print("\n[bold green]Top 5 profitabelste Routen:[/bold green]")
    console.print(analyzed_data.head(5).to_string())

if __name__ == '__main__':
    cli()