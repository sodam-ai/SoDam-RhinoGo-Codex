param(
    [Parameter(Mandatory = $true)][string]$OutputFile,
    [string]$ParametersFile,
    [ValidateRange(1, 3600)][int]$TimeoutSeconds = 120
)
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$rhino = 'C:\Program Files\Rhino 7\System\Rhino.exe'
$script = Join-Path $PSScriptRoot 'run_full_rhino7.py'
if (-not (Test-Path -LiteralPath $rhino)) { throw "Rhino 7 is not installed at $rhino" }
if (-not (Test-Path -LiteralPath $script)) { throw "Runner missing: $script" }
$output = [System.IO.Path]::GetFullPath($OutputFile)
if ([System.IO.Path]::GetExtension($output).ToLowerInvariant() -ne '.3dm') { throw 'OutputFile must end in .3dm' }
if (Test-Path -LiteralPath $output) { throw "Preserving existing model: $output" }
foreach ($suffix in @('.build.json', '.audit.json', '.saved-audit.json')) {
    $report = [System.IO.Path]::ChangeExtension($output, $suffix)
    if (Test-Path -LiteralPath $report) { throw "Preserving existing report: $report" }
}
if (-not (Test-Path -LiteralPath (Split-Path $output -Parent))) { throw 'Output parent directory must already exist' }
$params = ''
if ($ParametersFile) {
    $params = [System.IO.Path]::GetFullPath($ParametersFile)
    if (-not (Test-Path -LiteralPath $params)) { throw "ParametersFile missing: $params" }
}
$python = Join-Path $root '.venv\Scripts\python.exe'
$validator = Join-Path $PSScriptRoot 'validate_live_rhino7_params.py'
if (-not (Test-Path -LiteralPath $python)) { throw "Python environment missing: $python" }
if (-not (Test-Path -LiteralPath $validator)) { throw "Parameter validator missing: $validator" }
$validationArgs = @($validator)
if ($params) { $validationArgs += @('--parameters', $params) }
& $python @validationArgs | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'Rhino 7 parameter validation failed before launch' }
$oldOutput = $env:RHINO7_OUTPUT_3DM
$oldParams = $env:RHINO7_PARAMS_JSON
try {
    $env:RHINO7_OUTPUT_3DM = $output
    $env:RHINO7_PARAMS_JSON = $params
    $rhinoScript = '_-RunPythonScript (' + $script + ')'
    $arguments = '/nosplash /notemplate /runscript="' + $rhinoScript + '"'
    $process = Start-Process -FilePath $rhino -ArgumentList $arguments -PassThru
} finally {
    $env:RHINO7_OUTPUT_3DM = $oldOutput
    $env:RHINO7_PARAMS_JSON = $oldParams
}
$audit = [System.IO.Path]::ChangeExtension($output, '.audit.json')
$limit = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
while ([DateTime]::UtcNow -lt $limit) {
    if (Test-Path -LiteralPath $audit) {
        $report = Get-Content -LiteralPath $audit -Raw | ConvertFrom-Json
        if (-not $report.overall_pass) { throw "Live audit failed: $audit" }
        if (-not (Test-Path -LiteralPath $output)) { throw "Audit exists but model is missing: $output" }
        $python = Join-Path $root '.venv\Scripts\python.exe'
        if (-not (Test-Path -LiteralPath $python)) { throw "Python environment missing: $python" }
        $savedAuditScript = Join-Path $PSScriptRoot 'audit_saved_rhino7.py'
        & $python $savedAuditScript $output | Out-Null
        if ($LASTEXITCODE -ne 0) { throw "Saved model audit failed: $output" }
        $savedAudit = [System.IO.Path]::ChangeExtension($output, '.saved-audit.json')
        [pscustomobject]@{ ProcessId=$process.Id; Model=$output; LiveAudit=$audit; SavedAudit=$savedAudit; Objects=$report.object_count; Passed=$true }
        return
    }
    if ($process.HasExited) { throw "Rhino 7 exited before audit: $($process.ExitCode)" }
    Start-Sleep -Milliseconds 500
}
throw "Timed out waiting for Rhino 7 live audit: $audit"
