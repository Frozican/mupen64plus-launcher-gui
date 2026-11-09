#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$HOME/.local/src/mupen64plus-build"
PREFIX="/usr/local"
JOBS="$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 2)"

if [[ $EUID -eq 0 ]]; then
  echo 'Please run as your normal user, not with sudo.'
  exit 1
fi
if ! command -v apt-get >/dev/null; then
  echo 'This installer currently supports Ubuntu/Debian (apt).'
  exit 1
fi

printf '\n==> Installing build dependencies...\n'
sudo apt-get update
sudo apt-get install -y \
  build-essential git pkg-config make gcc g++ nasm zlib1g-dev libpng-dev \
  libfreetype-dev libsdl2-dev libglu1-mesa-dev libgl-dev libboost-dev \
  libboost-filesystem-dev libminizip-dev libsamplerate0-dev libspeexdsp-dev \
  libreadline-dev python3 python3-tk

mkdir -p "$SRC"

# All upstream repositories use the official mupen64plus GitHub organization.
# Clone once; subsequent installer runs reuse the checked-out source trees.
repos=(
  mupen64plus-core
  mupen64plus-audio-sdl
  mupen64plus-input-sdl
  mupen64plus-rsp-hle
  mupen64plus-video-rice
  mupen64plus-ui-console
)
for repo in "${repos[@]}"; do
  dir="$SRC/$repo"
  if [[ -d "$dir/.git" ]]; then
    echo "==> Source already present: $repo"
  else
    echo "==> Cloning official source: $repo"
    rm -rf "$dir"
    git clone --depth 1 --branch master "https://github.com/mupen64plus/${repo}.git" "$dir"
  fi
done

build_install_plugin() {
  local repo="$1"; shift
  echo "==> Building and installing $repo"
  make -C "$SRC/$repo/projects/unix" all -j"$JOBS" OPTFLAGS=-O2 "$@"
  sudo make -C "$SRC/$repo/projects/unix" install PREFIX="$PREFIX"
}

# The core's Unix makefile lives in projects/unix. Vulkan is disabled because
# it is not needed for this baseline build and may not be installed on Pi OS.
echo '==> Building Mupen64Plus core (Vulkan disabled)'
make -C "$SRC/mupen64plus-core/projects/unix" all -j"$JOBS" VULKAN=0 OPTFLAGS=-O2
sudo make -C "$SRC/mupen64plus-core/projects/unix" install PREFIX="$PREFIX"

build_install_plugin mupen64plus-audio-sdl
build_install_plugin mupen64plus-input-sdl
build_install_plugin mupen64plus-rsp-hle
build_install_plugin mupen64plus-video-rice
build_install_plugin mupen64plus-ui-console

sudo ldconfig
mkdir -p "$HOME/.local/share/applications" "$HOME/.config/mupen64plus-gui"
cat > "$HOME/.local/share/applications/mupen64plus-gui.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Mupen64Plus Launcher
Comment=Launch Nintendo 64 games with Mupen64Plus
Exec=python3 "$ROOT/app.py"
Terminal=false
Categories=Game;Emulator;
EOF
chmod +x "$ROOT/app.py"

printf '\n==> INSTALLATION COMPLETE\n'
echo "Launch with: python3 \"$ROOT/app.py\""
echo 'Plugin settings: open Settings / Plugins to choose Video, Audio, Input and RSP libraries.'
echo 'Installed baseline plugins: Rice video, SDL audio, SDL input and HLE RSP.'
echo "Source trees are stored in: $SRC"
