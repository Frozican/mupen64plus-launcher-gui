#!/usr/bin/env python3
"""Detect the OS and install the official Mupen64Plus bundle."""
import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import urllib.request
import zipfile
from pathlib import Path

VERSION = "2.6.0"
RELEASE_URL = f"https://github.com/mupen64plus/mupen64plus-core/releases/download/{VERSION}"
APP_NAME = "Mupen64PlusLauncher"


def data_dir():
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share"))
    return base / APP_NAME


def os_label():
    system = platform.system()
    machine = platform.machine()
    if system == "Windows":
        return f"Windows {platform.release()} ({machine})"
    if system == "Darwin":
        return f"macOS {platform.mac_ver()[0] or platform.release()} ({machine})"
    if system == "Linux":
        return f"Linux ({machine})"
    return f"{system} ({machine})"


def safe_target(root, member_name):
    target = (root / member_name).resolve()
    base = root.resolve()
    if target != base and base not in target.parents:
        raise RuntimeError(f"Unsafe path in downloaded archive: {member_name}")
    return target


def extract_zip(archive, destination):
    with zipfile.ZipFile(archive) as bundle:
        for item in bundle.infolist():
            safe_target(destination, item.filename)
        bundle.extractall(destination)


def extract_tar(archive, destination):
    with tarfile.open(archive, "r:gz") as bundle:
        for item in bundle.getmembers():
            target = safe_target(destination, item.name)
            if item.issym() or item.islnk():
                safe_target(target.parent, item.linkname)
        bundle.extractall(destination)


def download_bundle(filename, archive_type):
    root = data_dir() / "emulator"
    archive = data_dir() / filename
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)
    url = f"{RELEASE_URL}/{filename}"
    print(f"\nDownloading official Mupen64Plus {VERSION} bundle:\n{url}")
    request = urllib.request.Request(url, headers={"User-Agent": "Mupen64Plus-Launcher-Installer"})
    with urllib.request.urlopen(request, timeout=60) as response, archive.open("wb") as output:
        total = int(response.headers.get("Content-Length", "0") or 0)
        downloaded = 0
        while True:
            block = response.read(256 * 1024)
            if not block:
                break
            output.write(block)
            downloaded += len(block)
            if total:
                print(f"\rDownload: {downloaded * 100 // total}%", end="", flush=True)
    print("\nExtracting emulator and plugins...")
    if archive_type == "zip":
        extract_zip(archive, root)
    else:
        extract_tar(archive, root)
    archive.unlink(missing_ok=True)
    names = ("mupen64plus-ui-console.exe", "mupen64plus.exe") if os.name == "nt" else ("mupen64plus",)
    for name in names:
        matches = list(root.rglob(name))
        if matches:
            executable = matches[0]
            if os.name != "nt":
                executable.chmod(executable.stat().st_mode | 0o111)
            return executable
    raise RuntimeError("The archive was extracted, but the Mupen64Plus executable could not be found.")


def install_windows():
    if platform.machine().lower() not in {"amd64", "x86_64", "x64"}:
        raise RuntimeError("The official Windows 2.6.0 bundle is available for x64 only.")
    executable = download_bundle(f"mupen64plus-bundle-win64-{VERSION}.zip", "zip")
    print("\nIf Windows reports a missing VCRUNTIME/MSVCP DLL, install the Microsoft Visual C++ 2015–2022 x64 runtime.")
    return executable


def install_macos():
    if platform.machine().lower() in {"arm64", "aarch64"}:
        brew = shutil.which("brew")
        if not brew:
            raise RuntimeError("Apple Silicon detected. Install Homebrew from https://brew.sh and run this installer again.")
        subprocess.run([brew, "install", "mupen64plus"], check=True)
        executable = shutil.which("mupen64plus")
        if not executable:
            raise RuntimeError("Homebrew finished, but mupen64plus was not found on PATH.")
        return Path(executable)
    return download_bundle(f"mupen64plus-bundle-osx-{VERSION}.zip", "zip")


def install_linux():
    machine = platform.machine().lower()
    if machine in {"aarch64", "arm64", "armv7l", "armv6l"}:
        # The upstream prebuilt Linux archive is x86-64. Build natively on ARM instead.
        if not Path("/etc/debian_version").exists() or not shutil.which("apt-get"):
            raise RuntimeError("ARM Linux currently uses the included Ubuntu/Debian source-build script (setup_linux.sh).")
        script = Path(__file__).resolve().with_name("setup_linux.sh")
        if not script.is_file():
            raise RuntimeError("setup_linux.sh is missing; cannot build the ARM Linux version.")
        subprocess.run(["bash", str(script)], check=True)
        executable = shutil.which("mupen64plus")
        if not executable:
            raise RuntimeError("The build completed, but mupen64plus was not found on PATH.")
        return Path(executable)
    if machine not in {"x86_64", "amd64"}:
        raise RuntimeError(f"No official prebuilt Linux bundle is available for this CPU architecture: {machine}")
    return download_bundle(f"mupen64plus-bundle-linux64-{VERSION}.tar.gz", "tar")


def main():
    detected = os_label()
    print("Mupen64Plus Launcher — Cross-platform setup")
    print("\nDetected operating system:")
    print(f"  {detected}")
    answer = input("Is this your operating system? Continue with installation? [yes/no]: ").strip().lower()
    if answer not in {"yes", "y"}:
        print("Installation cancelled. No changes were made.")
        return 0

    system = platform.system()
    if system == "Windows":
        executable = install_windows()
    elif system == "Darwin":
        executable = install_macos()
    elif system == "Linux":
        executable = install_linux()
    else:
        print(f"Unsupported operating system: {system}", file=sys.stderr)
        return 1

    root = data_dir()
    root.mkdir(parents=True, exist_ok=True)
    info = {
        "version": VERSION,
        "os": system,
        "emulator_executable": str(executable.resolve()),
        "emulator_root": str(executable.parent.resolve()),
    }
    (root / "install.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
    print("\nINSTALLATION COMPLETE")
    print(f"Emulator: {executable}")
    print("\nStart the graphical launcher with:")
    print(f'  "{sys.executable}" "{Path(__file__).resolve().with_name("app.py")}"')
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as error:
        print(f"\nAn installation command failed (exit code {error.returncode}).", file=sys.stderr)
        raise SystemExit(error.returncode or 1)
    except Exception as error:
        print(f"\nInstallation failed: {error}", file=sys.stderr)
        raise SystemExit(1)
