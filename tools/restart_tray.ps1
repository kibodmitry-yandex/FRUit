$ErrorActionPreference = 'SilentlyContinue'

# Убить все треи FRUit и запустить один свежий, затем показать процессы.
Get-CimInstance Win32_Process -Filter "Name='pythonw.exe'" |
    Where-Object { $_.CommandLine -match 'FRUit' } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
Start-Sleep -Milliseconds 800

Start-Process -FilePath 'F:\FRUit\FRUit.exe'
Start-Sleep -Seconds 3

$p = @(Get-CimInstance Win32_Process -Filter "Name='pythonw.exe'" |
    Where-Object { $_.CommandLine -match 'FRUit' })
"треев FRUit: " + $p.Count
foreach ($x in $p) { "  pid={0} ppid={1}" -f $x.ProcessId, $x.ParentProcessId }
