# Write a read-only dashboard snapshot. No system or container actions are taken.
$ErrorActionPreference = "Stop"
$folder = Join-Path $env:ProgramData 'AcerHomelab\metrics'
$path = Join-Path $folder 'windows.json'
$pending = Join-Path $folder "windows.$PID.tmp"
$backup = "$pending.bak"

$os = Get-CimInstance Win32_OperatingSystem
$cpu = Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average
$disk = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='$env:SystemDrive'"
$snapshot = @{
    collected_at = [DateTime]::UtcNow.ToString('o')
    cpu_percent = $cpu.Average
    memory_total_bytes = [long]$os.TotalVisibleMemorySize * 1024
    memory_available_bytes = [long]$os.FreePhysicalMemory * 1024
    disk_name = $disk.DeviceID
    disk_total_bytes = [long]$disk.Size
    disk_free_bytes = [long]$disk.FreeSpace
}
New-Item -Path $folder -ItemType Directory -Force | Out-Null
try {
    [IO.File]::WriteAllText($pending, ($snapshot | ConvertTo-Json -Compress))
    if ([IO.File]::Exists($path)) {
        [IO.File]::Replace($pending, $path, $backup)
    } else {
        [IO.File]::Move($pending, $path)
    }
} finally {
    if ([IO.File]::Exists($pending)) { [IO.File]::Delete($pending) }
    if ([IO.File]::Exists($backup)) { [IO.File]::Delete($backup) }
}
