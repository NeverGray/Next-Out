param(
	[string]$VenvRoot = "C:\venv",
	[string]$EnvName = "next-out-py3.13",
	[string]$PythonVersion = "3.13"
)

$ErrorActionPreference = "Stop"

# Defaults keep the venv outside OneDrive while allowing overrides.
$ProjectRoot = $PSScriptRoot
$VenvPath = Join-Path $VenvRoot $EnvName
$RequirementsPath = Join-Path $ProjectRoot "requirements.txt"

if (-not (Test-Path $RequirementsPath)) {
	throw "requirements.txt not found at: $RequirementsPath"
}

if (-not (Test-Path $VenvPath)) {
	Write-Host "Creating Python $PythonVersion virtual environment at $VenvPath"
	py -$PythonVersion -m venv $VenvPath
} else {
	Write-Host "Using existing virtual environment at $VenvPath"
}

$PythonExe = Join-Path $VenvPath "Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
	throw "Virtual environment python executable not found: $PythonExe"
}

Write-Host "Upgrading pip/setuptools/wheel"
& $PythonExe -m pip install --upgrade pip setuptools wheel

Write-Host "Installing dependencies from $RequirementsPath"
& $PythonExe -m pip install -r $RequirementsPath

Write-Host "Environment ready."
Write-Host "Activate with: & '$VenvPath\Scripts\Activate.ps1'"
