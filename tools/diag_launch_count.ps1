$ErrorActionPreference = 'SilentlyContinue'

function Get-Fru {
    Get-CimInstance Win32_Process -Filter "Name='pythonw.exe'" |
        Where-Object { $_.CommandLine -match 'FRUit' }
}

foreach ($x in (Get-Fru)) { Stop-Process -Id $x.ProcessId -Force }
Start-Sleep -Milliseconds 1200
"before launch: [" + ((Get-Fru).ProcessId -join ',') + "]"

Start-Process -FilePath 'F:\FRUit\FRUit.exe'
Start-Sleep -Seconds 4

$q = Get-Fru
"after launch : [" + (($q.ProcessId) -join ',') + "]"
foreach ($p in $q) {
    "  pid={0} ppid={1}" -f $p.ProcessId, $p.ParentProcessId
}
