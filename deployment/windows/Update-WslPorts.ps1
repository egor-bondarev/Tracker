# Acer configuration verified after a Windows restart on 2026-11-18.
# Run elevated, under the Windows account that owns Ubuntu-24.04.
$ErrorActionPreference = "Stop"

$keepAlive = Get-ScheduledTask -TaskName "Acer-WSL-KeepAlive"
if ($keepAlive.State -ne "Running") {
    Start-ScheduledTask -TaskName "Acer-WSL-KeepAlive"
}

$wsl = "$env:SystemRoot\System32\wsl.exe"
$netsh = "$env:SystemRoot\System32\netsh.exe"

$wslIp = $null
for ($attempt = 1; $attempt -le 30; $attempt++) {
    $output = & $wsl -d Ubuntu-24.04 --exec hostname -I
    if ($LASTEXITCODE -eq 0) {
        $candidate = (($output -join " ").Trim() -split "\s+")[0]
        $parsed = $null
        if ([System.Net.IPAddress]::TryParse($candidate, [ref]$parsed)) {
            if ($parsed.AddressFamily -eq [System.Net.Sockets.AddressFamily]::InterNetwork) {
                $wslIp = $candidate
                break
            }
        }
    }
    Start-Sleep -Seconds 5
}
if (-not $wslIp) { throw "Could not determine the Ubuntu IPv4 address." }

foreach ($port in 8000, 8001) {
    & $netsh interface portproxy add v4tov4 `
        listenaddress=192.168.0.38 listenport=$port `
        connectaddress=$wslIp connectport=$port
    if ($LASTEXITCODE -ne 0) { throw "Could not configure port $port." }
}
Write-Output "Forwarding ports 8000 and 8001 to $wslIp"

function Test-TrackerListeners {
    $listeners = @(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue)
    foreach ($port in 8000, 8001) {
        $match = $listeners | Where-Object {
            $_.LocalAddress -eq "192.168.0.38" -and $_.LocalPort -eq $port
        }
        if (-not $match) { return $false }
    }
    return $true
}
Start-Sleep -Seconds 3
if (-not (Test-TrackerListeners)) {
    Write-Output "LAN listeners missing; restarting IP Helper."
    Restart-Service iphlpsvc -ErrorAction Stop
    for ($attempt = 1; $attempt -le 15; $attempt++) {
        Start-Sleep -Seconds 2
        if (Test-TrackerListeners) { break }
    }
}
if (-not (Test-TrackerListeners)) { throw "Tracker LAN listeners are still missing." }
Write-Output "Both Tracker LAN listeners are active."
