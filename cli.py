# sinister_snare/cli.py
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, TaskID

# KORREKTUR: Absolute Importe, um PyInstaller-Probleme zu lösen
import db_handler
import scheduler
import analyzer
import uex_client

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

@cli.command()
def grab_database():
    """Lädt die komplette UEXCorp-Datenbank herunter und speichert sie lokal."""
    console.print("[bold cyan]Starte vollständigen Datenbankdownload von UEXCorp...[/bold cyan]")
    
    with Progress() as progress:
        task = progress.add_task("[cyan]Lade komplette Datenbank...", total=4)
        
        try:
            # Initialisiere Datenbank falls nötig
            db_handler.init_db()
            progress.advance(task)
            
            # Lade alle Daten
            all_data = uex_client.grab_complete_database()
            progress.advance(task)
            
            # Speichere in lokaler Datenbank
            db_handler.save_complete_database(all_data)
            progress.advance(task)
            
            # Zeige Zusammenfassung
            progress.advance(task)
            
        except Exception as e:
            console.print(f"[bold red]Fehler beim Datenbankdownload: {e}[/bold red]")
            return
    
    console.print("[bold green]✓ Vollständiger Datenbankdownload abgeschlossen![/bold green]")
    
    # Zeige Statistiken
    status = db_handler.get_database_status()
    table = Table(title="Datenbankinhalt")
    table.add_column("Datentyp", style="cyan")
    table.add_column("Anzahl Einträge", style="green")
    
    for table_name, count in status.items():
        if table_name.endswith('_download') or table_name.startswith('last_'):
            continue
        table.add_row(table_name.replace('_', ' ').title(), str(count))
    
    console.print(table)

@cli.command()
def status():
    """Zeigt den aktuellen Datenbankstatus an."""
    console.print("[bold cyan]Datenbankstatus:[/bold cyan]")
    
    status = db_handler.get_database_status()
    if not status:
        console.print("[bold red]Fehler beim Abrufen des Datenbankstatus.[/bold red]")
        return
    
    table = Table(title="Datenbankinhalt")
    table.add_column("Tabelle", style="cyan")
    table.add_column("Anzahl Einträge", style="green")
    
    for table_name, count in status.items():
        if table_name.endswith('_download') or table_name.startswith('last_'):
            continue
        table.add_row(table_name.replace('_', ' ').title(), str(count))
    
    console.print(table)
    
    if 'last_download' in status:
        console.print(f"\n[bold]Letzter Download:[/bold] {status['last_download']}")
        success_text = "[green]Erfolgreich[/green]" if status.get('last_download_success') else "[red]Fehlgeschlagen[/red]"
        console.print(f"[bold]Status:[/bold] {success_text}")

if __name__ == '__main__':
    cli()