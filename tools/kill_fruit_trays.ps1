Get-CimInstance Win32_Process -Filter "Name='pythonw.exe'" |
  Where-Object { $_.CommandLine -match 'fruit' } |
  ForEach-Object { "killing {0}" -f $_.ProcessId; Stop-Process -Id $_.ProcessId -Force }
"done"
