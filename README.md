# AngelTune

**AngelTune** is an unofficial Tower Unite configuration editor made by **Angel**.

Cute on the outside, suspiciously organized on the inside. :3

AngelTune is built to make editing `Game.ini` and `GameUserSettings.ini` easier, more readable, and reversible without manually digging through config files.

> **Steam:** `AngelNeedsSupervision`  
> Come say hi if you want - I do not bite... probably. ♡

## What AngelTune does

AngelTune focuses on known Tower Unite configuration values and provides a GUI for things such as:

- HUD styles and HUD colors
- display and resolution settings
- graphics and camera options
- sound and volume controls
- Text Hat presets, colors, symbols, and randomization
- gameplay, workshop, canvas, condo, privacy, and profile settings
- presets and Share Packs
- favorites and improved search
- automatic and manual backups
- backup history and selected-backup restore
- changes preview
- undo since load
- reset current tab
- config health checks
- read-only quest progress information
- AngelTune dashboard and quick actions

## Safety scope

AngelTune edits known values in:

- `Game.ini`
- `GameUserSettings.ini`

AngelTune does **not** inject into Tower Unite, patch game executables, modify game packages, or use memory editing.

Automatic backups are created before successful writes.

Even so, config changes are used at your own risk. Game updates can overwrite settings, unusual values can behave unexpectedly, and you should keep your own backup of important configuration files.

## Random Text Hat

Random Text Hat monitoring is **off by default**.

AngelTune only checks whether Tower Unite is running while the Random Text Hat option is explicitly enabled and AngelTune itself remains open. When the option is disabled, no process polling is scheduled.

## Installation

### Normal users

1. Download `AngelTune_v2.4_Windows.zip` from the release.
2. Extract the ZIP.
3. Run `AngelTune.exe`.
4. Windows SmartScreen may show an **Unknown publisher** warning because AngelTune is not code-signed.

No Python installation is required for the compiled EXE.

### Building from source

Requirements:

- Windows
- Python 3
- PyInstaller

Run:

```bat
build_exe.bat
```

The resulting executable will be created at:

```text
dist\AngelTune.exe
```

## Windows SmartScreen / antivirus

AngelTune is currently not digitally code-signed.

Small PyInstaller applications can sometimes trigger SmartScreen or antivirus warnings, especially when they are new and have little download reputation. If you publish AngelTune publicly, provide the source code and SHA-256 checksum alongside the release so users can verify what they downloaded.

## Presets and backups

AngelTune stores its own files in the Tower Unite config directory:

```text
AngelTune_Backups\
AngelTune_Presets\
```

Older `TowerUniteConfigTool_Backups` and `TowerUniteConfigTool_Presets` folders remain supported for compatibility.

## About

**Creator:** Angel  
**Status:** officially unofficial  
**Original:** yep, this is the one ♡

AngelTune is not affiliated with PixelTail Games, Valve, or Steam.
