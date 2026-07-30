param(
    [string]$VenvRoot = "C:\venv",
    [string]$PythonVersion = "3.13",
    [string]$DevEnvName = "next-out-dev-py313",
    [string]$ProdEnvName = "next-out-prod-py313",
    [switch]$Dev,
    [switch]$Prod
)

$ErrorActionPreference = "Stop"

if (-not $Dev -and -not $Prod) {
    $Dev = $true
    $Prod = $true
}

$ProjectRoot = $PSScriptRoot
$DevRequirementsPath = Join-Path $ProjectRoot "requirements.txt"
$ProdRequirementsPath = Join-Path $ProjectRoot "requirements_in_exe.txt"

if (-not (Test-Path $DevRequirementsPath)) {
    throw "Development requirements file not found: $DevRequirementsPath"
}

if (-not (Test-Path $ProdRequirementsPath)) {
    throw "Production requirements file not found: $ProdRequirementsPath"
}

function New-Environment {
    param(
        [string]$EnvName,
        [string]$RequirementsPath,
        [string]$Label
    )

    $VenvPath = Join-Path $VenvRoot $EnvName
    if (-not (Test-Path $VenvPath)) {
        Write-Host "Creating $Label environment at $VenvPath"
        py -$PythonVersion -m venv $VenvPath
    } else {
        Write-Host "Using existing $Label environment at $VenvPath"
    }

    $PythonExe = Join-Path $VenvPath "Scripts\python.exe"
    if (-not (Test-Path $PythonExe)) {
        throw "Python executable not found for ${EnvName}: $PythonExe"
    }

    Write-Host "Upgrading pip/setuptools/wheel for $EnvName"
    & $PythonExe -m pip install --upgrade pip setuptools wheel

    Write-Host "Installing $Label dependencies from $RequirementsPath"
    & $PythonExe -m pip install -r $RequirementsPath

    Write-Host "$Label environment ready."
    Write-Host "Activate with: & '$VenvPath\Scripts\Activate.ps1'"
}

if ($Dev) {
    New-Environment -EnvName $DevEnvName -RequirementsPath $DevRequirementsPath -Label "development"
}

if ($Prod) {
    New-Environment -EnvName $ProdEnvName -RequirementsPath $ProdRequirementsPath -Label "production"
}
