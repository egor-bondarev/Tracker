# Acer startup: Windows → WSL2 → Docker

This runbook records the setup that was configured manually and verified after a reboot on November 18, 2026. The files were reconstructed from the setup history. Use the local configuration of the Windows host.

- Use the Windows account that owns the WSL distribution.
- The examples use an Ubuntu WSL2 distribution with NAT networking.
- Use the Windows LAN IPv4 address reserved through DHCP. The examples use a documentation address.
- API: TCP ports 8000 and 8001. Web interface: TCP port 8080. Wi-Fi profile: Private.
- Docker starts through systemd, and the containers have restart policies.

## Recovery after power changes and resume

After AC power was disconnected, Ubuntu and KeepAlive were found stopped. Both tasks were configured to prevent startup on battery power and stop when switching to battery power. Clear both battery restrictions and add an event trigger to the port forwarding task. The script starts KeepAlive when needed and updates the forwarding rules. HTTP errors do not trigger recovery.

Starting the task when AC power is connected was verified on Acer. Manual resume from hibernation was also verified before port 8080 was added.

## Setup

Run the commands in the same elevated PowerShell session under the Windows account that owns the distribution. Replace the example address and set the distribution name to match the output of wsl --list --verbose. Copy `Update-WslPorts.ps1` from the repository to `C:\ProgramData\AcerHomelab\Update-WslPorts.ps1`. Create the directory if needed.

```powershell
$windowsUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$lanAddress = "192.0.2.10"
$distribution = "Ubuntu-24.04"

New-Item -ItemType Directory -Path C:\ProgramData\AcerHomelab -Force
```

Back up the existing script before replacing it. Restrict write access to the directory and script to trusted users because the task runs the script with elevated privileges. The commands below are for initial setup. If the tasks already exist, inspect their settings before making changes.

### Keep WSL running

```powershell
$action = New-ScheduledTaskAction `
    -Execute "$env:SystemRoot\System32\wsl.exe" `
    -Argument "-d ""$distribution"" --exec sleep infinity"
$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal `
    -UserId $windowsUser -LogonType S4U -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable -ExecutionTimeLimit ([TimeSpan]::Zero) `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)
Register-ScheduledTask -TaskName "Acer-WSL-KeepAlive" `
    -Action $action -Trigger $trigger -Principal $principal -Settings $settings
Start-ScheduledTask -TaskName "Acer-WSL-KeepAlive"
```

S4U does not store a password and limits access to Windows network resources. Starting before user sign-in was verified on this Acer. The expected KeepAlive state is `Running`, with result code `267009` (`0x41301`, task is running).

### Port forwarding

```powershell
$portAction = New-ScheduledTaskAction `
    -Execute "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File C:\ProgramData\AcerHomelab\Update-WslPorts.ps1 -ListenAddress $lanAddress -Distribution ""$distribution"""
$trigger = New-ScheduledTaskTrigger -AtStartup
$trigger.Delay = "PT30S"
$principal = New-ScheduledTaskPrincipal `
    -UserId $windowsUser -LogonType S4U -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 5) `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)
Register-ScheduledTask -TaskName "Acer-WSL-Ports" `
    -Action $portAction -Trigger $trigger -Principal $principal -Settings $settings
Start-ScheduledTask -TaskName "Acer-WSL-Ports"
```

The expected state is `Ready`, with `LastTaskResult = 0`. The script updates the portproxy rules for TCP ports 8000, 8001, and 8080. If Windows is not listening on the LAN address, the script restarts IP Helper. This briefly interrupts other port forwarding rules managed by IP Helper.

### Event trigger for Acer-WSL-Ports

In the task properties, keep the **At startup** trigger and add **On an event → Custom → New Event Filter → XML → Edit query manually**. Paste the following query.

```xml
<QueryList>
  <Query Id="0" Path="System">
    <Select Path="System">
      *[System[Provider[@Name='Microsoft-Windows-Kernel-Power'] and EventID=105]
        and EventData[Data[@Name='AcOnline']='true']]
    </Select>
    <Select Path="System">
      *[System[(Provider[@Name='Microsoft-Windows-Power-Troubleshooter'] and EventID=1)
        or (Provider[@Name='Microsoft-Windows-Kernel-Power'] and (EventID=107 or EventID=507))]]
    </Select>
  </Query>
</QueryList>
```

Set a **30-second delay** on the new trigger. On the **Settings** tab, select **Do not start a new instance** if the task is already running. For existing tasks, check the **Conditions** tab to make sure both battery restrictions are cleared.

To verify the trigger, disconnect and reconnect AC power while Windows is running. After about a minute, check the last run time of `Acer-WSL-Ports`, confirm that its result is `0`, and verify that both APIs respond from the Mac. Repeat the check separately after resuming from sleep or hibernation.

### Firewall

Create these rules once.

```powershell
New-NetFirewallRule -Name "Tracker-API-LAN" `
    -DisplayName "Tracker API from LAN" -Direction Inbound -Action Allow `
    -Protocol TCP -LocalPort 8000,8001 -LocalAddress $lanAddress `
    -RemoteAddress LocalSubnet -Profile Private

New-NetFirewallRule -Name "Tracker-Web-LAN" `
    -DisplayName "Tracker Web from LAN" -Direction Inbound -Action Allow `
    -Protocol TCP -LocalPort 8080 -LocalAddress $lanAddress `
    -RemoteAddress LocalSubnet -Profile Private
```

On a host with API access already configured, create only the web firewall rule if it
is missing. When upgrading an existing task, use the port forwarding section above
to define $portAction, then apply the new action after copying the updated script
so the task passes the local address. Existing event triggers are preserved.

```powershell
Set-ScheduledTask -TaskName "Acer-WSL-Ports" -Action $portAction
Start-ScheduledTask -TaskName "Acer-WSL-Ports"
```

Once the web container is running, open the host's LAN address on port 8080 from the Mac.

## Verify after a reboot

Wait two to three minutes before checking from the Mac. Leave Windows at the sign-in screen and let the scheduled tasks start WSL. Replace the example IP with the host LAN address. Both requests should return HTTP 200.

```bash
curl --connect-timeout 5 --max-time 10 -sS -o /dev/null -w 'Record: %{http_code}\n' http://192.0.2.10:8000/openapi.json
curl --connect-timeout 5 --max-time 10 -sS -o /dev/null -w 'Analytic: %{http_code}\n' http://192.0.2.10:8001/openapi.json
```

If the requests fail, capture the current state before restarting any services.

```powershell
Get-ScheduledTask -TaskName "Acer-WSL-KeepAlive","Acer-WSL-Ports" |
    Select-Object TaskName, State
Get-ScheduledTaskInfo -TaskName "Acer-WSL-Ports" |
    Select-Object LastRunTime, LastTaskResult
wsl --list --verbose
netsh interface portproxy show v4tov4
Get-NetTCPConnection -State Listen -LocalPort 8000,8001 -ErrorAction SilentlyContinue
```

Compare Ubuntu’s current IP address with the portproxy rules and check the containers and APIs. Running a command inside WSL may start a stopped distribution. Record the output of `wsl --list --verbose` first.


### Optional homelab dashboard access

Run the dashboard as a separate Compose project. Set
`DASHBOARD_BIND_ADDRESS=0.0.0.0` in a local `.env` beside
`dashboard/compose.yml` so Windows can reach the published port inside WSL.
Keep the default dashboard port, TCP 8088.

Install the current port forwarding script and add `-IncludeDashboard` to the
existing `Acer-WSL-Ports` action arguments. Use `Set-ScheduledTask -Action` to
keep the existing boot and event triggers. The action must still pass
`-ListenAddress` and the correct WSL distribution name. Create a firewall rule
for the dashboard from the private LAN.

```powershell
New-NetFirewallRule -Name "Homelab-Dashboard-LAN" `
    -DisplayName "Homelab dashboard from LAN" -Direction Inbound -Action Allow `
    -Protocol TCP -LocalPort 8088 -LocalAddress $lanAddress `
    -RemoteAddress LocalSubnet -Profile Private

Start-ScheduledTask -TaskName "Acer-WSL-Ports"
```

From another LAN device, open the Windows LAN address on port 8088 at
`/dashboard` and run the Tracker check.

### Dashboard metrics on demand

The dashboard shows the last saved sample when opened. Its refresh buttons
request a fresh sample for Windows, WSL, or Docker independently. There is no
periodic collection or browser polling.

Set these paths in the dashboard's local Compose `.env` on a default WSL
installation, alongside the existing bind address:

```dotenv
DASHBOARD_WINDOWS_METRICS_DIR=/mnt/c/ProgramData/AcerHomelab/metrics
DASHBOARD_WSL_METRICS_DIR=/var/lib/homelab-metrics
DASHBOARD_CONTROL_DIR=/run/homelab-metrics
```

In elevated PowerShell, install `Write-HostMetrics.ps1` in
`C:\ProgramData\AcerHomelab\collectors`. Restrict write access to the collector
and metrics directories to Administrators and SYSTEM. Allow the Windows account
that owns the WSL distribution to read the metrics directory.

Register the Windows collector without triggers. Re-registering this way
replaces any previous startup or recurring triggers:

```powershell
$metricsAction = New-ScheduledTaskAction `
    -Execute "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" `
    -Argument "-NoProfile -NonInteractive -ExecutionPolicy Bypass -File C:\ProgramData\AcerHomelab\collectors\Write-HostMetrics.ps1"
$principal = New-ScheduledTaskPrincipal -UserId SYSTEM -LogonType ServiceAccount
$settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Seconds 40) `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName "Acer-HostMetrics" -Action $metricsAction `
    -Principal $principal -Settings $settings -Force
```

In Ubuntu, run the following from the dashboard checkout. When upgrading an
existing installation, disable the previous `homelab-metrics.timer` first:

```bash
sudo systemctl disable --now homelab-metrics.timer
sudo install -D -m 0644 deployment/wsl/collect_metrics.py /usr/local/libexec/homelab-collect-metrics.py
sudo install -m 0644 deployment/wsl/homelab-metrics.socket deployment/wsl/homelab-metrics@.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now homelab-metrics.socket
sudo docker compose -f dashboard/compose.yml --env-file dashboard/.env up -d --build
```

On a new installation, skip the first command when the old timer is absent.
Systemd starts a short-lived collector only when a refresh request reaches its
local socket. The dashboard mounts the snapshots and socket directory
read-only. The only accepted requests are fixed collection commands. The
dashboard has no Docker socket mount.
