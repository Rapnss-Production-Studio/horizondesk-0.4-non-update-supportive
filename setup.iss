[Setup]
AppName=Horizon Desk
AppVersion=0.2
AppPublisher=Rapnss Production Studio
AppPublisherURL=https://horizondesk.com
AppSupportURL=https://horizondesk.com
AppUpdatesURL=https://horizondesk.com
DefaultDirName={autopf}\HorizonDesk
DisableProgramGroupPage=yes
OutputBaseFilename=HorizonDesk_v0.2_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile={#SourcePath}\sample-gui\public\logo.ico
UninstallDisplayIcon={app}\HorizonDesk.exe

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Ship the compiled PyInstaller bundle — NO raw .py files
Source: "{#SourcePath}\dist\HorizonDesk\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Plugins folder — kept editable/extensible by the user
Source: "{#SourcePath}\plugins\*"; DestDir: "{app}\plugins"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Launch HorizonDesk.exe directly — no VBScript wrapper needed
Name: "{autoprograms}\Horizon Desk"; Filename: "{app}\HorizonDesk.exe"; IconFilename: "{app}\HorizonDesk.exe"
Name: "{autodesktop}\Horizon Desk"; Filename: "{app}\HorizonDesk.exe"; Tasks: desktopicon; IconFilename: "{app}\HorizonDesk.exe"

[Run]
Filename: "{app}\HorizonDesk.exe"; Description: "{cm:LaunchProgram,Horizon Desk}"; Flags: nowait postinstall skipifsilent
