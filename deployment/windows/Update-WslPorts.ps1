# Run elevated, under the Windows account that owns the WSL distribution.
param(
    [Parameter(Mandatory = $true)]
    [string]$ListenAddress,

    [string]$Distribution = "Ubuntu-24.04"
)

$ErrorActionPreference = "Stop"
$listenIp = $null
if ($ListenAddress -notmatch '^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$' -or
    -not [System.Net.IPAddress]::TryParse($ListenAddress, [ref]$listenIp) -or
    $listenIp.AddressFamily -ne [System.Net.Sockets.AddressFamily]::InterNetwork -or
    $listenIp.Equals([System.Net.IPAddress]::Any)) {
    throw "Specify a concrete Windows LAN IPv4 address in ListenAddress."
}
$ListenAddress = $listenIp.IPAddressToString

$keepAlive = Get-ScheduledTask -TaskName "Acer-WSL-KeepAlive"
if ($keepAlive.State -ne "Running") {
    Start-ScheduledTask -TaskName "Acer-WSL-KeepAlive"
}

$wsl = "$env:SystemRoot\System32\wsl.exe"
$netsh = "$env:SystemRoot\System32\netsh.exe"
$ports = 8000, 8001, 8080

$wslIp = $null
for ($attempt = 1; $attempt -le 30; $attempt++) {
    $output = & $wsl -d $Distribution --exec hostname -I
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

foreach ($port in $ports) {
    & $netsh interface portproxy add v4tov4 `
        listenaddress=$ListenAddress listenport=$port `
        connectaddress=$wslIp connectport=$port
    if ($LASTEXITCODE -ne 0) { throw "Could not configure port $port." }
}
Write-Output "Forwarding ports $($ports -join ", ") to $wslIp"

function Test-TrackerListeners {
    $listeners = @(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue)
    foreach ($port in $ports) {
        $match = $listeners | Where-Object {
            $_.LocalAddress -eq $ListenAddress -and $_.LocalPort -eq $port
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
Write-Output "Tracker LAN listeners are active."
