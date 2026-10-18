Get-CimInstance Win32_Process -Filter "Name='pythonw.exe'" |
  ForEach-Object { "{0}  {1}" -f $_.ProcessId, $_.CommandLine }
