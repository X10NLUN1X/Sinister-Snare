; --- Grundlegende Installer-Informationen ---
!define APP_NAME "SinisterSnare"
!define COMP_NAME "X10NLUN1X"
!define VERSION "1.0.0"
!define EXE_NAME "SinisterSnare.exe" ; So wird die .exe nach der Installation heißen

; Name der finalen Installer-Datei
OutFile "${APP_NAME}-Installer-v${VERSION}.exe"

; Standard-Installationsverzeichnis
InstallDir "$PROGRAMFILES\${APP_NAME}"

; Grafisches Interface für den Installer
!include "MUI2.nsh"

; --- Installer-Seiten ---
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; --- Sprachen ---
!insertmacro MUI_LANGUAGE "German"

; --- Installations-Sektion ---
Section "Hauptprogramm" SEC_MAIN

  ; Setzt den Pfad, in den installiert wird
  SetOutPath $INSTDIR

  ; ##################################################################
  ; ### HIER IST DIE WICHTIGSTE ÄNDERUNG ###
  ;
  ; Wir kopieren die EINE von PyInstaller erstellte .exe-Datei.
  ; Wir benennen sie während des Kopiervorgangs in ${EXE_NAME} um.
  ; Passe "dist\run_gui.exe" an, falls deine .exe anders heißt.
  ;
  ; Alte, fehlerhafte Zeile: File "dist\SinisterSnare\*"
  ; ##################################################################
  File /oname=${EXE_NAME} "dist\run_gui.exe"

  ; --- Erstelle Verknüpfungen ---
  ; Startmenü-Verknüpfung
  CreateDirectory "$SMPROGRAMS\${APP_NAME}"
  CreateShortCut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${EXE_NAME}"

  ; Desktop-Verknüpfung (optional, kann auskommentiert werden)
  CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${EXE_NAME}"

  ; --- Schreibe Deinstallations-Informationen in die Registry ---
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayName" "${APP_NAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoRepair" 1

  ; Erstelle den Uninstaller
  WriteUninstaller "$INSTDIR\uninstall.exe"

SectionEnd

; --- Deinstallations-Sektion ---
Section "Uninstall"

  ; Lösche die Haupt-exe
  Delete "$INSTDIR\${EXE_NAME}"

  ; Lösche die Verknüpfungen
  Delete "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk"
  Delete "$DESKTOP\${APP_NAME}.lnk"

  ; Lösche den Startmenü-Ordner (nur wenn er leer ist)
  RMDir "$SMPROGRAMS\${APP_NAME}"

  ; Lösche den Uninstaller selbst
  Delete "$INSTDIR\uninstall.exe"

  ; Lösche das Hauptverzeichnis (nur wenn es leer ist)
  RMDir "$INSTDIR"

  ; Lösche die Registry-Einträge
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"

SectionEnd