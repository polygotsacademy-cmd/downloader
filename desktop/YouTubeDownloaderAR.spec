# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller configuration for a single-file Windows build.

Place vendor/ffmpeg.exe (and optionally vendor/ffprobe.exe) before building
if FFmpeg should be embedded in the generated executable.
"""
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

project_dir = Path(SPECPATH)
vendor_dir = project_dir / "vendor"

hiddenimports = collect_submodules("yt_dlp")
datas = collect_data_files("yt_dlp")
binaries = []

# Files are unpacked beside the application code inside the one-file bundle.
for executable_name in ("ffmpeg.exe", "ffprobe.exe"):
    executable_path = vendor_dir / executable_name
    if executable_path.is_file():
        binaries.append((str(executable_path), "."))

analysis = Analysis(
    [str(project_dir / "app.py")],
    pathex=[str(project_dir)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(analysis.pure)

executable = EXE(
    pyz,
    analysis.scripts,
    analysis.binaries,
    analysis.datas,
    [],
    name="YouTubeDownloaderAR",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
