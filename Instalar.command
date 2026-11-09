#!/bin/bash
# Guided Steam and Wine setup with optional game profiles.
set -euo pipefail

root="$(cd "$(dirname "$0")" && pwd)"
profile="$root/scripts/resonance-wine/install.py"
aion_profile="$root/scripts/aion2-wine-gptk/install.py"
mode="${1:---base-only}"
steam_app=/Applications/Steam.app
steam="$HOME/Library/Application Support/Steam"
runner="$HOME/Library/Application Support/notproton/runners/current/bin/wine"
free_runner="$HOME/Library/Application Support/notproton/runners/sikarugir-11/bin/wine"
tool="$steam/compatibilitytools.d/notproton/run"
prefix="$steam/steamapps/compatdata/3259780/pfx"
game="$steam/steamapps/common/FINAL FANTASY RESONANCE/FFRS.exe"
base="$root/vendor/mac-windows-gaming"
bundled_notproton="$root/vendor/notproton"
export PATH="/opt/homebrew/bin:$PATH"

fail() { printf '%s\n' "$*" >&2; exit 1; }
pause() { printf '\n%s\nPulsa Enter para continuar.\n' "$1"; read -r _ || fail 'Vuelve a ejecutar el instalador cuando esté listo.'; }
steam_closed() {
  while /usr/bin/pgrep -x steam_osx >/dev/null; do
    pause 'Sal de Steam completamente desde su menú (⌘Q).'
  done
}
stack_ready() {
  [[ -x "$runner" && "$runner" -ef "$free_runner" && -x "$tool" && -f "$steam_app/Contents/MacOS/notproton.dylib" ]] &&
    /usr/libexec/PlistBuddy -c 'Print :LSEnvironment:DYLD_INSERT_LIBRARIES' "$steam_app/Contents/Info.plist" 2>/dev/null |
      /usr/bin/grep -Fxq "$steam_app/Contents/MacOS/notproton.dylib"
}
steam_url() { /usr/bin/open -b com.valvesoftware.steam "$1"; }

case "$mode" in
  --help|-h) printf 'Uso: bash Instalar.command [--base-only | --resonance | --aion2 | --status]\n'; exit 0 ;;
  --base-only|--resonance|--aion2) ;;
  --status)
    stack_ready && printf 'NotProton: archivos de integración presentes\n' || printf 'NotProton: falta instalar o reparar la integración\n'
    printf '\nRESONANCE:\n'
    python3 "$profile" status || true
    printf '\nAION 2:\n'
    python3 "$aion_profile" status || true
    exit 0 ;;
  *) fail 'Usa --help para ver las opciones.' ;;
esac

[[ "$(uname -m)" == arm64 ]] || fail 'Se necesita un Mac con Apple Silicon y una Terminal ejecutada sin Rosetta.'
version="$(sw_vers -productVersion)"
(( ${version%%.*} >= 15 )) || fail 'Esta compilación de NotProton requiere macOS 15 o posterior.'
[[ -f "$profile" && -f "$base/install.sh" && -f "$bundled_notproton/Makefile" ]] || fail 'Descomprime el ZIP completo antes de abrir el instalador.'
if ! xcrun --find clang >/dev/null 2>&1; then
  xcode-select --install || true
  fail 'Completa la instalación de las herramientas de Apple y vuelve a abrir este instalador.'
fi

if ! stack_ready; then
  if [[ -e "$tool" || -e "$steam_app/Contents/MacOS/notproton.dylib" ]]; then
    fail 'Detecté una instalación de NotProton incompleta o distinta. Revisa la sección de reparación en RESONANCE_WINE.md antes de reemplazarla.'
  fi
  printf '%s\n' 'La instalación descarga Wine 11 e instala Steam, Rosetta, Homebrew y cmake si hacen falta.' \
    'NotProton modifica y vuelve a firmar Steam.app, guarda una copia local y se configura como herramienta predeterminada para juegos de Windows.'
  printf '¿Continuar? [s/N] '
  read -r answer
  [[ "$answer" == s || "$answer" == S ]] || exit 0
  steam_closed
  if [[ ! -d "$steam_app" ]]; then
    bash "$base/install.sh" --no-heroic
    pause 'Inicia sesión en Steam y deja que termine de actualizarse.'
  elif [[ ! -f "$steam/config/config.vdf" ]]; then
    /usr/bin/open -a "$steam_app"
    pause 'Inicia sesión en Steam y deja que termine de actualizarse.'
  fi
  steam_closed
  [[ -f "$steam/config/config.vdf" ]] || fail 'Abre Steam, inicia sesión y vuelve a ejecutar este instalador.'
  bash "$base/install.sh" --no-heroic
  stack_ready || fail 'No se pudo confirmar la instalación de NotProton.'
fi

if [[ "$mode" == --base-only ]]; then
  printf '\nBase de Steam y NotProton lista. Abre Steam y elige un juego de tu biblioteca.\n'
  exit 0
fi

if [[ "$mode" == --aion2 ]]; then
  steam_closed
  python3 "$aion_profile" install
  printf '\nAplica las opciones de Steam de AION2_WINE_GPTK.md y abre el juego desde tu biblioteca.\n'
  exit 0
fi

if [[ ! -f "$game" ]]; then
  steam_url 'steam://install/3259780'
  pause 'Confirma la instalación de FINAL FANTASY RESONANCE en Steam y espera a que termine la descarga.'
  [[ -f "$game" ]] || fail 'El juego aún no está instalado en la biblioteca predeterminada. Completa la descarga y vuelve a ejecutar este instalador.'
fi

if [[ ! -f "$prefix/user.reg" || ! -f "$prefix/system.reg" ]]; then
  steam_url 'steam://rungameid/3259780'
  pause 'Deja que el primer arranque cree el entorno de Wine. Cierra el juego o el aviso de Visual C++ si aparece.'
fi

steam_closed
python3 "$profile" install
printf '\nConfiguración de RESONANCE aplicada. Abre el juego desde tu biblioteca de Steam.\n'
/usr/bin/open -a "$steam_app"
