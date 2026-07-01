; Inno Setup script for J.A.R.V.I.S.
; Build dist\JARVIS first (build_exe.bat), then compile this with the
; Inno Setup Compiler (ISCC.exe) -- or just run build_installer.bat.

#define MyAppName "J.A.R.V.I.S."
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Home Lab"
#define MyAppExeName "JARVIS.exe"

[Setup]
AppId={{4C3B8B0A-6F2E-4B6A-9C3E-JARVIS000001}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\JARVIS
DefaultGroupName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
DisableProgramGroupPage=yes
OutputDir=installer_output
OutputBaseFilename=JARVIS-Setup
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Files]
; Everything except config.yaml is safe to overwrite on every install/update.
Source: "dist\JARVIS\*"; DestDir: "{app}"; Excludes: "config.yaml"; Flags: ignoreversion recursesubdirs createallsubdirs
; config.yaml is only placed on first install so upgrades never clobber your edits.
Source: "dist\JARVIS\config.yaml"; DestDir: "{app}"; Flags: onlyifdoesntexist

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName} now"; Flags: nowait postinstall skipifsilent

; Chat history / memory / personality live in %APPDATA%\JARVIS (see
; jarvis/config.py) and are intentionally left alone by the uninstaller.
