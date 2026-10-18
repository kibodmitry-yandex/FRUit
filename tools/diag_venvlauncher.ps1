$ErrorActionPreference = 'SilentlyContinue'

function Get-Probe {
    Get-CimInstance Win32_Process -Filter "Name='pythonw.exe'" |
        Where-Object { $_.CommandLine -match 'probe_whoami' }
}

foreach ($x in (Get-Probe)) { Stop-Process -Id $x.ProcessId -Force }
Remove-Item 'F:\FRUit\logs\who.log' -Force
Start-Sleep -Milliseconds 600

Start-Process -FilePath 'F:\FRUit\.venv\Scripts\pythonw.exe' `
    -ArgumentList 'F:\FRUit\tools\probe_whoami.py'
Start-Sleep -Seconds 3

$p = Get-Probe
"processes matching probe_whoami: " + $p.Count
foreach ($x in $p) {
    "  pid={0} ppid={1} exe={2}" -f $x.ProcessId, $x.ParentProcessId, $x.ExecutablePath
}
"--- who.log (кто реально выполнял код) ---"
Get-Content 'F:\FRUit\logs\who.log'
