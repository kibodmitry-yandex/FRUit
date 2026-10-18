$ErrorActionPreference = 'SilentlyContinue'

# Все процессы, чья командная строка упоминает fruit/FRUit — ищем «зомби»-трей.
"PID    PPID   STARTED            NAME      CMDLINE"
"-----  -----  -----------------  --------  -------"
Get-CimInstance Win32_Process |
    Where-Object { $_.CommandLine -match 'fruit' } |
    ForEach-Object {
        $t = $_.CreationDate
        $ts = if ($t) { $t.ToString('HH:mm:ss') } else { '?' }
        "{0,-6} {1,-6} {2,-18} {3,-9} {4}" -f `
            $_.ProcessId, $_.ParentProcessId, $ts, $_.Name, $_.CommandLine
    }
