# Windows Tweaker PowerShell Launcher
# Scans for venv and activates, then runs the app as a module

$venvDirs = @('.venv', 'venv', 'env')
$venvFound = $false
foreach ($dir in $venvDirs) {
    $activatePath = Join-Path $dir 'Scripts\Activate.ps1'
    if (Test-Path $activatePath) {
        Write-Host "Activating virtual environment: $dir"
        & $activatePath
        $venvFound = $true
        break
    }
}
if (-not $venvFound) {
    Write-Host "No virtual environment found (.venv, venv, env)."
    exit 1
}

Write-Host "Launching Windows Tweaker..."
python -m windows11_tweaker.main
