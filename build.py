import os
import shutil
import subprocess
import sys

APP_NAME = "SinisterSnare"
ENTRY_POINT = "run_gui.py"
SRC_DIR = "src"

def build_application():
    print(">>> Starte Build-Prozess...")
    print(f"INFO: Arbeitsverzeichnis: {os.getcwd()}")

    # Entferne alte Build-Artefakte
    for item in ["dist", "build", f"{APP_NAME}.spec"]:
        if os.path.exists(item):
            print(f"INFO: Entferne '{item}'")
            shutil.rmtree(item) if os.path.isdir(item) else os.remove(item)

    # Baue den PyInstaller-Befehl
    command = [
        'pyinstaller',
        '--noconfirm',
        '--name', APP_NAME,
        '--windowed',
        '--icon', 'assets/icon.ico',
        '--add-data', f'assets{os.pathsep}assets',
        '--paths', SRC_DIR,       # WICHTIG! Sagt PyInstaller, wo sinister_snare liegt.
        '--hidden-import', 'PyQt6.sip',
        ENTRY_POINT
    ]

    print(f"\n>>> Führe aus: {' '.join(command)}\n")

    try:
        process = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
        print("--- PyInstaller-Ausgabe ---")
        print(process.stdout)
        print("--- ENDE ---\n")
        print(">>> Build erfolgreich.")
        print(f">>> EXE liegt in: '{os.path.abspath('dist')}'")
    except subprocess.CalledProcessError as e:
        print("\n!!! Build-Fehler !!!")
        print(e.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n!!! Unerwarteter Fehler: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_application()