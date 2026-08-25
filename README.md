FrameForge 1.0.0

FrameForge is a Windows desktop application for converting videos and
multiple images into animated GIF files.

BUILDING

**========**

1. Run build_installer.ps1 from the project folder.

2. The script creates/uses the project's Python virtual environment.

3. The script installs PyInstaller and the project requirements on the
   BUILD PC.

4. The script downloads the Windows FFmpeg Essentials build on the BUILD PC.

5. PyInstaller builds the FrameForge application.

6. The script stages the finished application under:

   dist\\FrameForge\\

7. Open installer\\FrameForge.iss in Inno Setup Compiler.

8. Press Compile in Inno Setup.

The final installer is:

installer\\Output\\FrameForge-Setup-1.0.0.exe

TARGET PC

**=========**

The installed FrameForge application does NOT require:

- Python
- pip
- PySide6
- a separate FFmpeg installation
- a separate FFprobe installation
- an Internet connection for first-run setup

FFmpeg and FFprobe are included with the application.

BUNDLED RESOURCES

**=================**

dist\\FrameForge\\FrameForge.exe

dist\\FrameForge\\ffmpeg.exe

dist\\FrameForge\\ffprobe.exe

APPLICATION

**==========**

FrameForge supports video-to-GIF conversion and multiple-image-to-GIF
conversion, with preview, video start/end selection, output settings,
drag-and-drop media input, and conversion progress reporting.

IMPORTANT

**=========**

FrameForge includes FFmpeg and FFprobe from the Windows FFmpeg build used
by the build process. FFmpeg and its included components remain subject
to their respective licenses.

Review the FFmpeg license and the license of any third-party component
before redistributing FrameForge commercially.

Users are responsible for ensuring that they have the necessary rights
to process the media they convert.

Copyright (c) 2026 Wesley.

See LICENSE for the FrameForge software license.
