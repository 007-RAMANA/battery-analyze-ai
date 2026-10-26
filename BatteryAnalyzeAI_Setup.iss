
#define MyAppName "Battery Analyze AI"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Sharp"
#define MyAppExeName "BatteryAnalyzeAI.exe"

[Setup]
AppId={{B7E31C52-9A46-4D11-8C32-5F70A2149D61}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\BatteryAnalyzeAI
DefaultGroupName={#MyAppName}
OutputDir=C:\BatteryAI\installer_output
OutputBaseFilename=BatteryAnalyzeAI_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
UninstallDisplayName={#MyAppName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Files]
Source: "C:\BatteryAI\dist\BatteryAnalyzeAI\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Battery Analyze AI"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\Battery Analyze AI"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch Battery Analyze AI"; Flags: postinstall nowait skipifsilent
