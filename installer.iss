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
SetupIconFile=assets\logo_parroquia.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
WizardImageFile=assets\logo_parroquia.png
WizardSmallImageFile=assets\logo_parroquia.png
PrivilegesRequired=admin
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
LicenseFile=
CloseApplications=yes
UninstallDisplayName={#AppFullName}
UninstallDisplayIcon={app}\{#AppExeName}
AppCopyright=Parroquia Nuestra Señora de la Paz, Hermosillo, Sonora

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear icono en el &escritorio"; GroupDescription: "Iconos adicionales:"; Flags: unchecked

[Dirs]
; Dar permisos de escritura a todos los usuarios en la carpeta data
; (necesario para que la app pueda crear/modificar la base de datos)
Name: "{app}\data"; Permissions: users-full
Name: "{app}\data\backups"; Permissions: users-full
Name: "{app}\data\excel_backup"; Permissions: users-full

[Files]
; Ejecutable principal (PyInstaller one-file bundle)
Source: "{#SourceDir}\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Configuración inicial de la parroquia (no sobreescribir si ya existe)
Source: "data\iglesia.json"; DestDir: "{app}\data"; Flags: onlyifdoesntexist

[Icons]
Name: "{group}\{#AppFullName}"; Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\{#AppExeName}"
Name: "{group}\Desinstalar {#AppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppFullName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Iniciar {#AppFullName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Preservar la base de datos y datos del usuario al desinstalar
Type: dirifempty; Name: "{app}\data\backups"
Type: dirifempty; Name: "{app}\data\excel_backup"
Type: dirifempty; Name: "{app}\data"
Type: dirifempty; Name: "{app}"

[Code]
function InitializeSetup(): Boolean;
var
  running: Boolean;
begin
  running := False;
  if CheckForMutexes('NSDP_APP_MUTEX') then begin
    MsgBox('La aplicación NSDP está en ejecución. Ciérrela antes de continuar con la instalación.', mbError, MB_OK);
    running := True;
  end;
  Result := not running;
end;
