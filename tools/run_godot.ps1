param([switch]$Editor)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$enginePath = Join-Path $projectRoot '.tools\godot\Godot_v4.7.2-stable_win64.exe'
$projectPath = Join-Path $projectRoot 'godot'
if (-not (Test-Path -LiteralPath $enginePath)) {
    Write-Host 'Primero ejecuta Preparar-Godot.cmd desde la carpeta del proyecto'
    exit 1
}
$mutexName = if ($Editor) { 'Local\ElCaminoSQL-Godot-Editor' } else { 'Local\ElCaminoSQL-Godot-Juego' }
$mutex = [System.Threading.Mutex]::new($false, $mutexName)
$acquired = $false
try {
    try { $acquired = $mutex.WaitOne(0) }
    catch [System.Threading.AbandonedMutexException] { $acquired = $true }
    if (-not $acquired) {
        Write-Host 'Ya hay una instancia abierta'
        exit 0
    }
    $arguments = @('--path', ('"' + $projectPath + '"'))
    if ($Editor) { $arguments += '--editor' }
    $process = Start-Process -FilePath $enginePath -ArgumentList $arguments -PassThru
    $process.WaitForExit()
    exit $process.ExitCode
} finally {
    if ($acquired) { $mutex.ReleaseMutex() }
    $mutex.Dispose()
}
