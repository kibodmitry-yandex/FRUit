$ErrorActionPreference = 'Stop'
Set-Location F:\FRUit
gh repo create kibodmitry-yandex/FRUit --private --source=. --remote=origin --push `
    --description "FRUit (Folder Restore Utility) - save and restore Windows 11 Explorer windows and tabs"
