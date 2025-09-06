
## Installer erstellen (für Windows)

Um eine einfach zu verteilende `setup.exe`-Datei für Windows zu erstellen, werden **PyInstaller** und **NSIS (Nullsoft Scriptable Install System)** verwendet.

### Voraussetzungen

1.  **Python-Abhängigkeiten installieren**:
    Stellen Sie sicher, dass alle Entwicklungs-Abhängigkeiten installiert sind:
    ```bash
    pip install -r requirements.txt
    ```

2.  **NSIS installieren**:
    Laden und installieren Sie NSIS von der offiziellen Webseite. Fügen Sie das Installationsverzeichnis von NSIS zu Ihrer `PATH`-Umgebungsvariable hinzu, damit der Befehl `makensis` in der Konsole verfügbar ist.
    *   **Download**: [NSIS Website](https://nsis.sourceforge.io/Download)

### Build-Prozess

Der gesamte Prozess wird durch das `build.py`-Skript und die NSIS-Konfigurationsdatei gesteuert.

1.  **(Optional) Icon ersetzen**:
    Ersetzen Sie die Platzhalter-Datei `assets/icon.ico` durch ein eigenes Icon für Ihre Anwendung.

2.  **Anwendung paketieren**:
    Führen Sie das `build.py`-Skript aus. Dieses Skript nutzt PyInstaller, um Ihre Anwendung in den `dist/SinisterSnare`-Ordner zu bündeln.
    ```bash
   pyinstaller run_gui.spec
    ```

3.  **Installer erstellen**:
    Kompilieren Sie das `installer.nsi`-Skript mit NSIS. Stellen Sie sicher, dass Sie sich im Hauptverzeichnis des Projekts befinden.
    ```bash
    makensis installer.nsi
    ```

Nach Abschluss dieses Befehls finden Sie die fertige Installationsdatei `Sinister_Snare_Installer.exe` im Hauptverzeichnis Ihres Projekts. Diese Datei kann nun an andere Benutzer verteilt werden.
