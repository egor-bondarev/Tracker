# Автозапуск Acer: Windows → WSL2 → Docker

Здесь сохранена настройка, введённая вручную и проверенная пользователем после
перезагрузки 18 ноября 2026 года. Файлы восстановлены по истории настройки, а не
выгружены с Acer. Они привязаны к конкретному ноутбуку:

- Windows: `laptop-ah1r7pkt\bo098`, учётная запись владеет дистрибутивом;
- Ubuntu: `Ubuntu-24.04`, пользователь `egor`, сеть NAT;
- домашний адрес Windows: `192.168.0.38`, закреплён в DHCP;
- API: TCP 8000 и 8001, профиль Wi-Fi Private;
- Docker включён в systemd, контейнеры имеют restart policy.

## Восстановление после смены питания и пробуждения

После отключения зарядки Ubuntu и KeepAlive оказались остановлены. У обоих
заданий действовал запрет запуска и продолжения работы от батареи. Снимите
эти ограничения и добавьте триггер событий к заданию портов. Скрипт запускает
KeepAlive при необходимости и обновляет перенаправления. Ошибки HTTP не
участвуют в запуске восстановления.

Запуск по подключению зарядки проверен на Acer. Восстановление после сна и
гибернации требует отдельной проверки на ноутбуке.

## Установка

Выполнять в PowerShell от администратора под указанной учётной записью Windows.
Сначала скопировать `Update-WslPorts.ps1` из репозитория в
`C:\ProgramData\AcerHomelab\Update-WslPorts.ps1`. Создать каталог при необходимости:

```powershell
New-Item -ItemType Directory -Path C:\ProgramData\AcerHomelab -Force
```

Не заменять рабочий скрипт без сохранения резервной копии. Каталог и скрипт должны
быть недоступны для изменения недоверенным пользователям: задание запускает их
с повышенными правами. Команды ниже предназначены для первоначального создания;
если задания уже существуют, сначала проверить их, а не создавать повторно.

### Удержание WSL

```powershell
$action = New-ScheduledTaskAction `
    -Execute "$env:SystemRoot\System32\wsl.exe" `
    -Argument "-d Ubuntu-24.04 -u egor --exec sleep infinity"
$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal `
    -UserId "laptop-ah1r7pkt\bo098" -LogonType S4U -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable -ExecutionTimeLimit ([TimeSpan]::Zero) `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)
Register-ScheduledTask -TaskName "Acer-WSL-KeepAlive" `
    -Action $action -Trigger $trigger -Principal $principal -Settings $settings
Start-ScheduledTask -TaskName "Acer-WSL-KeepAlive"
```

Режим S4U не сохраняет пароль и имеет ограничения доступа к сетевым ресурсам
Windows. Работа до входа пользователя проверена на этом Acer. Для задания
KeepAlive ожидается `Running`, код `267009` (`0x41301`: выполняется).

### Перенаправление портов

```powershell
$action = New-ScheduledTaskAction `
    -Execute "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File C:\ProgramData\AcerHomelab\Update-WslPorts.ps1"
$trigger = New-ScheduledTaskTrigger -AtStartup
$trigger.Delay = "PT30S"
$principal = New-ScheduledTaskPrincipal `
    -UserId "laptop-ah1r7pkt\bo098" -LogonType S4U -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 5) `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)
Register-ScheduledTask -TaskName "Acer-WSL-Ports" `
    -Action $action -Trigger $trigger -Principal $principal -Settings $settings
Start-ScheduledTask -TaskName "Acer-WSL-Ports"
```

Ожидается `Ready`, `LastTaskResult = 0`. Скрипт обновляет два portproxy-правила и,
если слушателей на домашнем IP нет, перезапускает IP Helper. Это кратковременно
затрагивает и другие перенаправления, обслуживаемые IP Helper.

### Триггер событий Acer-WSL-Ports

В свойствах задания сохраните триггер **При запуске** и добавьте **При событии →
Настраиваемый → Создать фильтр событий → XML → Изменить запрос вручную**.
Вставьте запрос:

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

В новом триггере поставьте задержку **30 секунд**. На вкладке **Параметры**
выберите **Не запускать новый экземпляр**, если задание уже выполняется. Для
ранее созданных заданий проверьте на вкладке **Условия**, что оба ограничения
работы от батареи сняты.

Для проверки отключите и снова подключите зарядку при работающей Windows.
Примерно через минуту проверьте время последнего запуска `Acer-WSL-Ports`, код
результата `0` и ответы обоих API с Mac. Повторите проверку отдельно после
выхода из сна или гибернации.

### Брандмауэр

Создать один раз:

```powershell
New-NetFirewallRule -Name "Tracker-API-LAN" `
    -DisplayName "Tracker API from LAN" -Direction Inbound -Action Allow `
    -Protocol TCP -LocalPort 8000,8001 -LocalAddress 192.168.0.38 `
    -RemoteAddress LocalSubnet -Profile Private
```

## Проверка после перезагрузки

Подождать 2–3 минуты, не входить в Windows и не запускать WSL вручную.
На Mac проверить HTTP 200:

```bash
curl --connect-timeout 5 --max-time 10 -sS -o /dev/null -w 'Record: %{http_code}\n' http://192.168.0.38:8000/openapi.json
curl --connect-timeout 5 --max-time 10 -sS -o /dev/null -w 'Analytic: %{http_code}\n' http://192.168.0.38:8001/openapi.json
```

При сбое сначала сохранить состояние, не перезапуская службы:

```powershell
Get-ScheduledTask -TaskName "Acer-WSL-KeepAlive","Acer-WSL-Ports" |
    Select-Object TaskName, State
Get-ScheduledTaskInfo -TaskName "Acer-WSL-Ports" |
    Select-Object LastRunTime, LastTaskResult
wsl --list --verbose
netsh interface portproxy show v4tov4
Get-NetTCPConnection -State Listen -LocalPort 8000,8001 -ErrorAction SilentlyContinue
```

Далее сравнить фактический IP Ubuntu с portproxy и проверить контейнеры/API.
Вызов команды внутри WSL может запустить остановленный дистрибутив, поэтому
сначала следует записать результат `wsl --list --verbose`.
