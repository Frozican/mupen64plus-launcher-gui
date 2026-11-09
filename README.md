# Mupen64Plus Launcher

A cross-platform Tkinter desktop frontend for Mupen64Plus. Browse your N64 ROM folder, launch games, and select the Video / GFX, Audio, Input and RSP plugins separately.

## Requirements

- Python 3.9 or newer
- Tkinter (included with the standard Windows and macOS Python installers; on some Linux distributions install the python3-tk package)
- Internet connection for the first emulator installation

## Quick installation

Extract the project folder first. Run the installer for your operating system from that folder. The Python installer detects the OS and CPU architecture, displays the detected system, and asks for confirmation before it changes anything.

### Windows 10 / 11 (x64)

Double-click install_windows.bat or run:

~~~bat
py -3 install.py
~~~

The installer downloads the official Mupen64Plus 2.6.0 Windows x64 bundle and extracts the emulator and its standard plugins into your local application data directory. If Windows reports a missing VCRUNTIME or MSVCP DLL, install the Microsoft Visual C++ 2015–2022 x64 runtime.

### macOS

Run bash install_macos.command or:

~~~bash
python3 install.py
~~~

- Apple Silicon (arm64): installs Mupen64Plus through Homebrew. Homebrew must already be installed.
- Intel (x86_64): downloads the official Mupen64Plus 2.6.0 macOS bundle.

### Linux

Run:

~~~bash
bash install_linux.sh
~~~

- x86-64: downloads the official Mupen64Plus 2.6.0 Linux 64-bit bundle into your user data directory.
- ARM / ARM64: on Ubuntu or Debian (including Raspberry Pi OS), the installer invokes setup_linux.sh to build Mupen64Plus natively from the official source repositories. This build step installs system packages and uses sudo when needed.
- Other Linux architectures or distributions may require installing Mupen64Plus and its plugins with the distribution's package manager.

The official binary bundles are published by the Mupen64Plus project: https://github.com/mupen64plus/mupen64plus-core/releases/tag/2.6.0

## Start the launcher

From the project folder:

- Windows: double-click run_windows.bat or run py -3 app.py.
- macOS: run bash run_macos.command or python3 app.py.
- Linux: run bash run_linux.sh or python3 app.py.

## Plugin settings

Open **Settings / Plugins**. Each subsystem has its own selector:

- Video / GFX
- Audio
- Input
- RSP

The launcher searches the downloaded emulator bundle and common system plugin directories for platform-appropriate libraries (.dll on Windows, .dylib / .so on macOS, and .so on Linux). You can select a discovered plugin, use Browse… to select another compatible library, or keep Use emulator default.

Fullscreen preference, selected plugins, ROM folder and extra command-line arguments are saved between launches. Configuration is stored in the user's normal application-data location for each operating system.

## Supported ROM formats

.z64, .n64, .v64 and .zip.

This project is a frontend and does not include ROM files. Use your own legally obtained game dumps.

## Platform notes

The launcher UI is Python/Tkinter-based. The included installer supports Windows x64, macOS Intel and Apple Silicon, Linux x86-64, and ARM Linux on Debian/Ubuntu. The official prebuilt Windows/Linux/macOS x64 bundles are version 2.6.0; Apple Silicon uses Homebrew, and ARM Linux builds from source. The project has not yet been runtime-tested on every operating system, so please report platform-specific errors.
