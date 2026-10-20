[English](README.md) · [Русский](README.ru.md) · [中文](README.zh.md)

# FRUit — Folder Restore Utility

**F**older **R**estore **U**tility (for **E**xplorer navigation) — a Windows 11
tool that saves Explorer windows with tabs and brings them back.

Tired of reopening a dozen folders after every reboot — or worse, after an
`explorer.exe` crash? Windows' own restore is unreliable and never works after
a crash. FRUit remembers the layout and restores it: one group, one window, or
everything at once.

## Features

- **Snapshot of windows and tabs** via `IShellWindows`; every tab is stored
  by its unique address.
- **Geometry and window state** (position, size, normal/maximized) restored
  through `GetWindowPlacement` / `SetWindowPos`.
- **Tray icon** (a folder with a banana): saved tab groups (🗂, by first tab)
  and single windows (🗀). Each entry has a submenu — composition (grey,
  read-only), *Restore*, *✕ Delete* — plus *Restore all*.
- **No duplicates:** an identical set of tabs is never saved twice, and if a
  layout is already open, its window is just brought to the front instead of
  being opened again.
- **Hotkeys:** `Ctrl+Alt+S` — snapshot, `Ctrl+Alt+R` — restore all.
- **Quiet tray** — no console window; all errors go to `logs\fruit.log`
  (rotated at 1 MB).
- **Thin `FRUit.exe` launcher** — runs the current Python code with its own
  environment; no rebuild after code changes.
- **CLI with named snapshots** — layouts as work/home profiles.

## Install

Requirements: Windows 11 and internet access (for Python and pip).

**Easiest way:**

1. Download the repository as a ZIP (*Code → Download ZIP*) or clone it:
   `git clone https://github.com/kibodmitry-yandex/FRUit.git`
2. Double-click **`install.bat`**: it finds Python 3.9+ (installs it silently
   via winget if missing), creates `.venv` and installs the dependencies.
3. Start **`FRUit.exe`** — the tray icon appears.

Manual alternative:

```bat
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

`FRUit.exe` uses the repository's own `.venv`, so keep the folder in place.

## Usage

### Tray (main mode)

Double-click `FRUit.exe` — a folder icon with a banana appears in the system
tray (no console). Right-click → menu:

```
Take snapshot                      ← save current windows/tabs (no duplicates)
Restore all                        ← open everything from the list
────────────────────────────────────
🗂 Projects (5 tabs)   ┐ composition of the group (grey, read-only):
        • src • docs   │ what exactly "Restore" will open;
        • tests • media┘ for a single window — its full path
        ────────────────────────
        Restore
        ✕ Delete🗀 Downloads
        • C:\Users\me\Downloads
        ────────────────────────
        Restore
        ✕ Delete
────────────────────────────────────
Data folder
Exit
```

The tray menu is currently in Russian:

| Menu item | Meaning |
|---|---|
| Сделать снапшот | Take snapshot |
| Восстановить все | Restore all |
| Восстановить | Restore |
| ✕ Удалить | ✕ Delete |
| Папка данных | Data folder |
| Выход | Exit |

Global hotkeys: `Ctrl+Alt+S` — snapshot, `Ctrl+Alt+R` — restore all.
Saved layouts live in `%LOCALAPPDATA%\FRUit\groups.json`.

### Command line (named snapshots)

```bat
FRUit.exe save work                      :: save current layout as "work"
FRUit.exe list                           :: list snapshots
FRUit.exe restore work                   :: restore (tabs are grouped into windows)
FRUit.exe restore work --no-tabs         :: more reliable: every folder in its own window
FRUit.exe restore latest                 :: restore the newest snapshot
FRUit.exe delete work                    :: delete a snapshot
```

Data: `%LOCALAPPDATA%\FRUit` — `snapshots\*.json` (named snapshots) and
`groups.json` (tray list); override the folder with `FRUIT_DATA`.
`FRUIT_HOME` is something else: the folder containing the `fruit` package,
used by the launcher.

## How it works

- Windows and tabs are enumerated with `IShellWindows` (tabs are grouped by
  window handle).
- The first tab opens via `explorer.exe`; the rest are added by invoking the
  *Add New Tab* button (UI Automation) and navigated with
  `IWebBrowser2.Navigate`.
- If a tab cannot be added, the folder opens as a **separate window**
  (fallback) — no folder is ever lost.
- Geometry: `GetWindowPlacement` / `SetWindowPos`.

Windows 11 implements Explorer tabs inside XAML/WinUI and exposes no official
API for them ([Microsoft Learn](https://learn.microsoft.com/en-us/answers/questions/5852400/)),
hence UI Automation plus the fallback.

## Limitations

- **Tabs via UI Automation.** If the button or navigation is unavailable, the
  layout is restored with separate windows: close, but complete.
- **No icons on menu items** (Win32/pystray) — groups and windows are marked
  with glyphs 🗂 / 🗀.
- **A menu row is a single click zone.** A click on an entry opens its
  submenu, so *Restore* lives inside it rather than on the row itself.
- **Virtual folders** (This PC, Quick Access, Recycle Bin) have no file path
  and are skipped with a warning; only `CabinetWClass` windows are handled.
- **`&` in folder names** is doubled in menu text (the Win32 mnemonic rule).

## Development

- `launcher\` — thin exe source (`FruitLauncher.cs`), `build_launcher.bat`
  (system `csc.exe`) and the icon generator `make_icon.py`.
- `tools\` — dev and test scripts; not part of the distribution.
- Icon: `launcher\logo.png` → `python launcher\make_icon.py` rebuilds
  `fruit.ico` / `fruit.png` (frames 16…256 px). Without the PNG the icon is
  drawn by Pillow code, so nothing breaks.

## License

MIT — see [LICENSE](LICENSE).
