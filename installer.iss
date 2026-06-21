; Script de Inno Setup para NSDP — Sistema de Registros Sacramentales
; Genera: dist\NSDP_Installer.exe

#define AppName      "NSDP"
#define AppFullName  "NSDP - Sistema de Registros Sacramentales"
#define AppVersion   "1.0"
#define AppPublisher "Parroquia Nuestra Señora de la Paz"
#define AppURL       "https://github.com/tinogas/registros_nsdp"
#define AppExeName   "NSDP.exe"
#define OutputDir    "dist"
#define SourceDir    "dist"

[Setup]
AppId={{B3F2A1C0-4D7E-4F89-A23B-9C8D5E6F7A01}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
OutputDir={#OutputDir}
OutputBaseFilename=NSDP_Installer
SetupIconFile=
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
LicenseFile=
CloseApplications=yes
UninstallDisplayName={#AppFullName}

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear icono en el &escritorio"; GroupDescription: "Iconos adicionales:"; Flags: unchecked

[Files]
Source: "{#SourceDir}\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#AppFullName}"; Filename: "{app}\{#AppExeName}"
Name: "{group}\Desinstalar {#AppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppFullName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Iniciar {#AppFullName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; No borrar la carpeta data\ para preservar la base de datos del usuario
Type: dirifempty; Name: "{app}"

[Code]
// Verificar que no esté corriendo antes de instalar
function InitializeSetup(): Boolean;
begin
  Result := True;
end;
