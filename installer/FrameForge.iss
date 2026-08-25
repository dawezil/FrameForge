#define MyAppName "FrameForge"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Wesley"
#define MyAppExeName "FrameForge.exe"

[Setup]
AppId={{A1C1B8E1-2C7B-4C3B-9D5B-8A7F3E210001}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\FrameForge
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=Output
OutputBaseFilename=FrameForge-Setup-{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=admin
UninstallDisplayIcon={app}\{#MyAppExeName}

[Files]
Source: "..\dist\FrameForge\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\FrameForge"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\FrameForge"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch FrameForge"; Flags: nowait postinstall skipifsilent
