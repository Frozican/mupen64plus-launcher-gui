# Mupen64Plus Launcher

A lightweight Tkinter desktop launcher for Mupen64Plus. It includes ROM browsing and configurable plugin selection for **Video / GFX, Audio, Input and RSP**.

## Install on Ubuntu / Debian (including Raspberry Pi 4, ARM64)

1. Extract this ZIP.
2. Open a terminal in the extracted `Mupen64Plus-GUI` directory.
3. Run:

   ```bash
   chmod +x setup_linux.sh
   ./setup_linux.sh
   ```

The installer installs the required build dependencies, then clones the official Mupen64Plus repositories into `~/.local/src/mupen64plus-build/`. It builds and installs the core, standard plugins and console frontend from those local source checkouts. **The installer does not use a pre-existing Mupen64Plus source folder on your computer.** An internet connection is required for the first clone; subsequent runs reuse the existing source trees.

Vulkan is disabled for the core build to avoid requiring Vulkan development headers. The installer uses the normal system prefix (`/usr/local`) and asks for your sudo password when installing dependencies and compiled components.

Start the launcher with:

```bash
python3 app.py
```

## Plugin settings

Open **Settings / Plugins** in the launcher. Each subsystem has its own selector:

- Video / GFX
- Audio
- Input
- RSP

The selectors scan the standard Mupen64Plus plugin directories. Choose an installed `.so` library for a subsystem, use **Browse…** to select a different plugin library, or leave it on **Use emulator default**. The selections, fullscreen preference and extra command-line arguments are saved in `~/.config/mupen64plus-gui/settings.json` and reused on the next launch.

The initial build provides Rice video, SDL audio, SDL input and HLE RSP. Additional compatible plugins can be installed separately and selected in the same settings window.

## Official source repositories cloned by the installer

All source code is cloned from the official `mupen64plus` GitHub organization, using each repository's `master` branch:

- `mupen64plus/mupen64plus-core`
- `mupen64plus/mupen64plus-audio-sdl`
- `mupen64plus/mupen64plus-input-sdl`
- `mupen64plus/mupen64plus-rsp-hle`
- `mupen64plus/mupen64plus-video-rice`
- `mupen64plus/mupen64plus-ui-console`

## Notes

- Supported installer target: Ubuntu / Debian Linux on ARM64 or x86-64.
- ROM formats scanned: `.z64`, `.n64`, `.v64`, `.zip`.
- This is a frontend; it does not include ROM files.
- Windows and macOS installers are not included in this Linux-focused package.
