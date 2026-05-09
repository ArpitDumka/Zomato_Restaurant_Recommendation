# Run everything implemented so far from repo root (Windows).
# Usage:
#   .\run.ps1           -> venv, install phase1, run health + status
#   .\run.ps1 -Spike    -> regenerate phase0/DatasetSpikeReport.md (network)
#   .\run.ps1 -Web      -> venv, install phase2 + phase1[web], serve http://127.0.0.1:8000/
#   .\run.ps1 -Surface   -> venv, install phases 2-6, serve Phase 6 at http://127.0.0.1:8765/
#   .\run.ps1 -Streamlit -> venv, install phases 2-6 + root requirements.txt, Streamlit at http://127.0.0.1:8501/

param(
    [switch] $Spike,
    [switch] $Web,
    [switch] $Surface,
    [switch] $Streamlit
)

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
Set-Location $Root

function Import-DotEnvFile {
    param([Parameter(Mandatory)][string]$Path)
    if (-not (Test-Path $Path)) { return }
    Get-Content -Path $Path -Encoding utf8 | ForEach-Object {
        $line = $_.Trim()
        if ($line -eq "" -or $line.StartsWith("#")) { return }
        $i = $line.IndexOf("=")
        if ($i -lt 1) { return }
        $key = $line.Substring(0, $i).Trim()
        $val = $line.Substring($i + 1).Trim()
        if ($val.StartsWith('"') -and $val.EndsWith('"') -and $val.Length -ge 2) {
            $val = $val.Substring(1, $val.Length - 2)
        }
        if ($key -and $val) { Set-Item -Path "Env:$key" -Value $val }
    }
}

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Error "Python not found on PATH. Install Python 3.11+ and retry."
}

if ($Spike) {
    & $python.Source -m pip install -q -r (Join-Path $Root "phase0\requirements.txt")
    & $python.Source (Join-Path $Root "phase0\dataset_spike.py")
    exit $LASTEXITCODE
}

if ($Surface) {
    $venvPy = Join-Path $Root ".venv\Scripts\python.exe"
    if (-not (Test-Path $venvPy)) {
        Write-Host "Creating .venv in repo root..."
        & $python.Source -m venv (Join-Path $Root ".venv")
        $venvPy = Join-Path $Root ".venv\Scripts\python.exe"
    }
    & $venvPy -m pip install -q -U pip
    & $venvPy -m pip install -q -e (Join-Path $Root "phase2")
    & $venvPy -m pip install -q -e (Join-Path $Root "phase3")
    & $venvPy -m pip install -q -e (Join-Path $Root "phase4")
    & $venvPy -m pip install -q -e (Join-Path $Root "phase5")
    Set-Location (Join-Path $Root "phase6")
    & $venvPy -m pip install -q -e .
    Set-Location $Root
    # Env: phase6\.env is the source of truth for Surface. phase5\.env is optional (e.g. dev); phase6 overrides same keys.
    $phase5Env = Join-Path $Root "phase5\.env"
    $phase6Env = Join-Path $Root "phase6\.env"
    if (Test-Path $phase5Env) {
        Import-DotEnvFile -Path $phase5Env
        Write-Host "Loaded phase5\.env (optional; keys can be overridden by phase6\.env)."
    }
    if (Test-Path $phase6Env) {
        Import-DotEnvFile -Path $phase6Env
        Write-Host "Loaded phase6\.env (GROQ_API_KEY / OPENAI_API_KEY / HF_TOKEN when set)."
    }
    Write-Host "Phase 6 UI: http://127.0.0.1:8765/ - put LLM keys in phase6\.env; HF_TOKEN optional for Hub"
    & $venvPy -m zomato_surface --host 127.0.0.1 --port 8765
    exit $LASTEXITCODE
}

if ($Streamlit) {
    $venvPy = Join-Path $Root ".venv\Scripts\python.exe"
    if (-not (Test-Path $venvPy)) {
        Write-Host "Creating .venv in repo root..."
        & $python.Source -m venv (Join-Path $Root ".venv")
        $venvPy = Join-Path $Root ".venv\Scripts\python.exe"
    }
    & $venvPy -m pip install -q -U pip
    & $venvPy -m pip install -q -e (Join-Path $Root "phase2")
    & $venvPy -m pip install -q -e (Join-Path $Root "phase3")
    & $venvPy -m pip install -q -e (Join-Path $Root "phase4")
    & $venvPy -m pip install -q -e (Join-Path $Root "phase5")
    Set-Location (Join-Path $Root "phase6")
    & $venvPy -m pip install -q -e .
    Set-Location $Root
    & $venvPy -m pip install -q -r (Join-Path $Root "requirements.txt")
    $phase5Env = Join-Path $Root "phase5\.env"
    $phase6Env = Join-Path $Root "phase6\.env"
    if (Test-Path $phase5Env) {
        Import-DotEnvFile -Path $phase5Env
        Write-Host "Loaded phase5\.env (optional; keys can be overridden by phase6\.env)."
    }
    if (Test-Path $phase6Env) {
        Import-DotEnvFile -Path $phase6Env
        Write-Host "Loaded phase6\.env (GROQ_API_KEY / OPENAI_API_KEY / HF_TOKEN when set)."
    }
    Write-Host "Phase 7 Streamlit: http://127.0.0.1:8501/ (stop with Ctrl+C)"
    $credDir = Join-Path $env:USERPROFILE ".streamlit"
    if (-not (Test-Path $credDir)) {
        New-Item -ItemType Directory -Path $credDir -Force | Out-Null
    }
    $credFile = Join-Path $credDir "credentials.toml"
    if (-not (Test-Path $credFile)) {
        @"
[general]
email = ""
"@ | Set-Content -Path $credFile -Encoding utf8
    }
    $env:STREAMLIT_BROWSER_GATHER_USAGE_STATS = "false"
    # First Streamlit run may prompt for email on stdin; pipe blank line so non-interactive shells still start.
    "" | & $venvPy -m streamlit run (Join-Path $Root "streamlit_app.py") --server.address 127.0.0.1 --server.port 8501 --browser.gatherUsageStats false
    exit $LASTEXITCODE
}

if ($Web) {
    $venvPy = Join-Path $Root ".venv\Scripts\python.exe"
    if (-not (Test-Path $venvPy)) {
        Write-Host "Creating .venv in repo root..."
        & $python.Source -m venv (Join-Path $Root ".venv")
        $venvPy = Join-Path $Root ".venv\Scripts\python.exe"
    }
    $phase2 = Join-Path $Root "phase2"
    & $venvPy -m pip install -q -U pip
    & $venvPy -m pip install -q -e $phase2
    Set-Location (Join-Path $Root "phase1")
    & $venvPy -m pip install -q -e ".[web]"
    Set-Location $Root
    Write-Host "Starting web UI at http://127.0.0.1:8000/"
    & $venvPy -m zomato_recommend serve --host 127.0.0.1 --port 8000
    exit $LASTEXITCODE
}

$venvPy = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPy)) {
    Write-Host "Creating .venv in repo root..."
    & $python.Source -m venv (Join-Path $Root ".venv")
}

$phase1 = Join-Path $Root "phase1"
& $venvPy -m pip install -q -U pip
# Plain editable install (no dev extras - avoids PowerShell bracket parsing on .[web] style extras)
& $venvPy -m pip install -q -e $phase1
& $venvPy -m zomato_recommend
