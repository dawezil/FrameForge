# FrameForge Installer Build

## Requirements

- Windows 10/11 64-bit
- Python 3.12+ recommended
- Inno Setup 6
- Internet access on the build PC (the build script downloads FFmpeg)

## Build

From the project directory:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\build_installer.ps1
```

The script creates/uses `.venv`, installs the build dependencies, downloads
the Windows FFmpeg Essentials build, builds FrameForge with PyInstaller,
and stages the application in `dist\FrameForge\`.

The staging folder contains:

```text
dist\FrameForge\
├── FrameForge.exe
├── ffmpeg.exe
├── ffprobe.exe
└── assets\
```

## Compile the installer

Open `installer\FrameForge.iss` in Inno Setup Compiler and select **Compile**.

The installer is created in:

```text
installer\Output\FrameForge-Setup-1.0.0.exe
```

Generated build folders and installer output are intentionally ignored by Git.
