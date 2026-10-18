# tools — вспомогательные скрипты (в поставку не входят)

Скрипты для отладки и проверки FRUit. Часть — «одноразовые» (`probe_*`,
`check_*`, `smoke_*`, разные `test_*`) и в репозиторий **не** попадают (см.
`.gitignore`); здесь остаются только полезные.

Запускать питоном окружения, из корня FRUit:

```bat
F:\FRUit\.venv\Scripts\python.exe tools\<скрипт>.py
```

## Трей и процессы (PowerShell)

- `restart_tray.ps1` — убить все треи FRUit, поднять один свежий, показать процессы.
- `kill_fruit_trays.ps1` — только убить все треи FRUit.
- `list_pyw.ps1`, `list_fruit_procs.ps1` — список процессов `pythonw.exe` / всех
  процессов, в командной строке которых есть `fruit`.
- `diag_tray.ps1` — диагностика трея.
- `diag_venvlauncher.ps1` — почему при запуске видно два `pythonw.exe`
  (venv-редиректор; см. `launcher\README.md`).

## Данные и проверки (Python)

- `populate_groups.py` — снять текущие окна Проводника и пополнить список
  (с дедупликацией). Пишет в реальное хранилище — это единственное исключение.
- `selftest_fruit.py` — импорт модулей + `save`/`list`/`load`/`delete` снапшота.
- `verify_venv_all.py` — импорт всего пакета, CLI, дедупликация групп, сборка меню.
- `test_groups.py` — проверка дедупликации групп.
- `test_menu_refresh.py` — после снапшота обновляются и меню, и подсказка значка.

> Проверки, которые пишут данные, уводят их в `tools\out\testdata`
> (переменная `FRUIT_DATA`) и **не трогают** `%LOCALAPPDATA%\FRUit`.

## Иконка

- `dump_icon.py` — «текстовый» вид иконки: `B` — банан, `F` — папка, `T` —
  вкладка. Умеет симулировать масштабирование Windows (64→32→16), как в трее:

  ```bat
  F:\FRUit\.venv\Scripts\python.exe tools\dump_icon.py 16 64 chain
  ```

- `make_preview.py` — PNG-превью в разных размерах → `tools\out\preview.png`.
- `render_icon.py` — дополнительные рендеры иконки.
