param(
    [string]$OutputDir = (Join-Path (Split-Path $PSScriptRoot -Parent) 'work\first-run')
)
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$python = Join-Path $root '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    throw "Python environment missing. Run: py -3.12 -m venv .venv; .\.venv\Scripts\python.exe -m pip install -r requirements.txt"
}
if (Test-Path -LiteralPath $OutputDir) {
    if ((Get-ChildItem -LiteralPath $OutputDir -Force | Measure-Object).Count -gt 0) {
        throw "Output directory is not empty: $OutputDir"
    }
} else {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}
$model = Join-Path $OutputDir 'pavilion-rhino7.3dm'
& $python (Join-Path $PSScriptRoot 'generate_rhino7_model.py') $model
if ($LASTEXITCODE -ne 0) { throw 'Generation failed' }
& $python (Join-Path $PSScriptRoot 'inspect_rhino7_model.py') $model
if ($LASTEXITCODE -ne 0) { throw 'Saved-model audit failed' }
Write-Output "Verified: $model"
