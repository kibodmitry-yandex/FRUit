$ErrorActionPreference = 'SilentlyContinue'
$before = Get-CimInstance Win32_Process -Filter "Name='pythonw.exe'" |
    Where-Object { $_.CommandLine -match 'FRUit' }
foreach ($x in $before) { Stop-Process -Id $x.ProcessId -Force }
"killed: " + (($before.ProcessId) -join ',')
Start-Sleep -Seconds 6
$after = Get-CimInstance Win32_Process -Filter "Name='pythonw.exe'" |
    Where-Object { $_.CommandLine -match 'FRUit' }
"after 6s: " + (($after.ProcessId) -join ',')
