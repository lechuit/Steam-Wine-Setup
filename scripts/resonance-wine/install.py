#!/usr/bin/env python3
"""Restore the confirmed FINAL FANTASY RESONANCE settings in NotProton."""

import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time

APP_ID = '3259780'
GAME_NAME = 'FINAL FANTASY RESONANCE'
DLLS = ('msvcp140', 'msvcp140_1', 'msvcp140_2', 'vcruntime140', 'vcruntime140_1')
RETINA_OPTION = 'NOTPROTON_RETINA=0'
STEAM = Path.home() / 'Library/Application Support/Steam'
DATA = STEAM / 'steamapps/compatdata' / APP_ID
PREFIX = DATA / 'pfx'
GAME = STEAM / 'steamapps/common' / GAME_NAME
RUN = STEAM / 'compatibilitytools.d/notproton/run'
REDIST = STEAM / 'steamapps/common/Steamworks Shared/_CommonRedist/vcredist/2022/VC_redist.x64.exe'
SOURCE_ROOT = Path.home() / 'Library/Caches/notproton-free/src'
STEAM_APP = Path('/Applications/Steam.app')
GUARD = Path(__file__).with_name('launcher-guard.sh').read_text().rstrip()
VDF_TOKEN = re.compile(r'"(?:\\.|[^"\\])*"|[{}]')
OPTION = re.compile(r'("LaunchOptions"\s*")((?:\\.|[^"\\])*)(")')
APPS_PATH = ('userlocalconfigstore', 'software', 'valve', 'steam', 'apps')


def vdf_block(source, path):
    stack = []
    matches = []
    previous = None
    for token in VDF_TOKEN.finditer(source):
        if token[0] == '{':
            if previous is None or not previous[0].startswith('"'):
                raise SystemExit('La configuración de Steam contiene un bloque sin nombre.')
            stack.append((previous[0][1:-1].lower(), token.start()))
        elif token[0] == '}':
            if not stack:
                raise SystemExit('La configuración de Steam contiene un cierre de bloque inesperado.')
            if tuple(key for key, _ in stack) == path:
                matches.append((stack[-1][1], token.start()))
            stack.pop()
        previous = token
    if stack or len(matches) > 1:
        raise SystemExit('La configuración de Steam contiene bloques incompletos o duplicados.')
    return matches[0] if matches else None


def ensure_vdf_block(source, path):
    if vdf_block(source, path):
        return source
    if len(path) == 1:
        raise SystemExit('Falta UserLocalConfigStore. Inicia sesión en Steam y vuelve a cerrarlo.')
    source = ensure_vdf_block(source, path[:-1])
    _, end = vdf_block(source, path[:-1])
    line = source.rfind('\n', 0, end) + 1
    indent = source[line:end]
    if indent.strip():
        raise SystemExit('No se encontró una línea segura para agregar el perfil de RESONANCE.')
    child = indent + '\t'
    return source[:line] + f'{child}"{path[-1]}"\n{child}{{\n{child}}}\n' + source[line:]


def settings_file():
    files = []
    matches = []
    for path in (STEAM / 'userdata').glob('*/config/localconfig.vdf'):
        source = path.read_text()
        files.append((path, source))
        if vdf_block(source, APPS_PATH + (APP_ID,)):
            matches.append((path, source))
    candidates = matches or files
    if len(candidates) != 1:
        raise SystemExit('No hay una configuración única de Steam para RESONANCE. Inicia sesión y configura el juego en la cuenta que usarás.')
    return candidates[0]


def with_retina_disabled(source):
    path = APPS_PATH + (APP_ID,)
    source = ensure_vdf_block(source, path)
    start, end = vdf_block(source, path)
    block = source[start:end]
    options = list(OPTION.finditer(block))
    if len(options) > 1:
        raise SystemExit('Las opciones de lanzamiento de RESONANCE están duplicadas.')
    match = options[0] if options else None
    original = match[2] if match else ''
    value = re.sub(r'(?<!\S)NOTPROTON_RETINA=\S+', '', original).strip()
    if '%command%' not in value:
        value = ('%command% ' + value).rstrip()
    value = f'{value} {RETINA_OPTION}'
    if match:
        return source[:start + match.start(2)] + value + source[start + match.end(2):]
    indent = re.search(r'\n([\t ]+)"', block)
    key_indent = indent[1] if indent else '\t'
    closing_line = source.rfind('\n', start, end) + 1
    if closing_line <= start or source[closing_line:end].strip():
        raise SystemExit('No se encontró una línea segura para agregar las opciones de RESONANCE.')
    return source[:closing_line] + f'{key_indent}"LaunchOptions"\t\t"{value}"\n' + source[closing_line:]


def registry_section(path, key):
    try:
        source = path.read_text(errors='replace')
    except FileNotFoundError:
        return ''
    header = '[' + key.replace('\\', '\\\\') + ']'
    match = re.search(r'^' + re.escape(header) + r'[^\n]*\n(.*?)(?=^\[|\Z)', source, re.M | re.S)
    return match[1] if match else ''


def native_amd64_dll(path):
    # A fresh Wine prefix can advertise VC++ even when it has only built-ins.
    try:
        with path.open('rb') as file:
            header = file.read(4096)
    except FileNotFoundError:
        return False
    if len(header) < 64 or header[:2] != b'MZ':
        return False
    if any(mark in header[:256] for mark in (b'Wine builtin DLL', b'Wine placeholder DLL')):
        return False
    pe_offset = int.from_bytes(header[60:64], 'little')
    return header[pe_offset:pe_offset + 6] == b'PE\0\0\x64\x86'


def runtime_installed():
    section = registry_section(PREFIX / 'system.reg', r'Software\Microsoft\VisualStudio\14.0\VC\Runtimes\x64')
    return '"Installed"=dword:00000001' in section and all(
        native_amd64_dll(PREFIX / 'drive_c/windows/system32' / (name + '.dll')) for name in DLLS
    )


def overrides_installed():
    section = registry_section(PREFIX / 'user.reg', r'Software\Wine\DllOverrides')
    return all(f'"{name}"="native,builtin"' in section.splitlines() for name in DLLS)


def wait_for_registry(check, timeout=40):
    """Wine can persist its registry after the helper process exits."""
    deadline = time.monotonic() + timeout
    while not check():
        if time.monotonic() >= deadline:
            return False
        time.sleep(0.5)
    return True


def require_closed():
    names = subprocess.run(['/bin/ps', '-axo', 'comm='], capture_output=True, text=True, check=True).stdout
    active = {line.strip().replace('\\', '/').rsplit('/', 1)[-1].lower() for line in names.splitlines()}
    if active & {'steam_osx', 'ffrs.exe', 'ffrs-win64-shipping.exe'}:
        raise SystemExit('Cierra Steam completamente y termina RESONANCE antes de instalar.')


def wine(*args):
    env = os.environ.copy()
    env.update(STEAM_COMPAT_APP_ID=APP_ID, SteamAppId=APP_ID, STEAM_COMPAT_DATA_PATH=str(DATA),
               STEAM_COMPAT_CLIENT_INSTALL_PATH=str(STEAM), STEAM_COMPAT_INSTALL_PATH=str(GAME), WINEDEBUG='-all')
    subprocess.run([str(RUN), 'run', *args], env=env, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def backup(path):
    folder = Path.home() / 'Library/Application Support/notproton/config-backups'
    folder.mkdir(mode=0o700, parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
    target = folder / f'{path.name}.before-resonance-{stamp}'
    shutil.copy2(path, target)
    print(f'Copia local: {target}')
    return target


def atomic_text(path, content, validate=False):
    with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, delete=False) as tmp:
        tmp.write(content)
        target = Path(tmp.name)
    try:
        shutil.copymode(path, target)
        if validate:
            subprocess.run(['/bin/sh', '-n', str(target)], check=True)
        target.replace(path)
    finally:
        target.unlink(missing_ok=True)


def with_launcher_guard(source):
    if GUARD in source:
        return source
    anchor = 'prefix_game_running() {\n'
    activate = re.search(r'^  game_pid=\$\(ps -ww -eo pid,args[^\n]*\)$', source, re.M)
    if source.count(anchor) != 1 or not activate or '# BEGIN RESONANCE process detection' in source:
        raise SystemExit('El lanzador de NotProton cambió. Revisa la versión antes de aplicar el perfil.')
    source = source[:activate.start()] + (
        '  game_pid=\n'
        '  if [ "$app_id" = 3259780 ]; then\n'
        '    game_pid=$(resonance_game_pid)\n'
        '  fi\n'
        '  if [ -z "$game_pid" ]; then\n' + '  ' + activate[0] + '\n  fi'
    ) + source[activate.end():]
    return source.replace(anchor, GUARD + '\n\n' + anchor + (
        '  if [ "$app_id" = 3259780 ] && [ -n "$(resonance_game_pid)" ]; then\n'
        '    return 0\n'
        '  fi\n'
    ), 1)


def install_launcher_guard():
    source_path = SOURCE_ROOT / 'dylib/feats/compat_run.sh'
    dylib = STEAM_APP / 'Contents/MacOS/notproton.dylib'
    built = SOURCE_ROOT / 'out/notproton.dylib'
    if not source_path.is_file() or not dylib.is_file():
        raise SystemExit('Falta la compilación local de NotProton. Repara la base antes de aplicar el perfil.')
    source = source_path.read_text()
    revised = with_launcher_guard(source)
    run_source = RUN.read_text()
    if source == revised and run_source == revised and built.is_file() and built.read_bytes() == dylib.read_bytes():
        return
    require_closed()
    original_dylib = backup(dylib)
    backup(source_path)
    backup(RUN)
    print('Actualizando la detección del proceso de RESONANCE…', flush=True)

    def sign():
        for path in (dylib, STEAM_APP / 'Contents/MacOS/steam_osx', STEAM_APP):
            subprocess.run(['/usr/bin/codesign', '-f', '-s', '-', str(path)], check=True, capture_output=True)
        subprocess.run(['/usr/bin/codesign', '--verify', str(STEAM_APP)], check=True, capture_output=True)

    replaced_dylib = False
    try:
        atomic_text(source_path, revised, validate=True)
        subprocess.run(['make', 'all'], cwd=SOURCE_ROOT, check=True)
        require_closed()
        replaced_dylib = True
        shutil.copy2(built, dylib)
        sign()
        atomic_text(RUN, revised, validate=True)
    except (Exception, SystemExit):
        atomic_text(source_path, source)
        if replaced_dylib:
            shutil.copy2(original_dylib, dylib)
            sign()
            atomic_text(RUN, run_source)
        raise


def prepare_runtime():
    if not runtime_installed():
        if not REDIST.is_file():
            raise SystemExit('Falta VC_redist.x64.exe en Steamworks Shared. Instala Steamworks Common Redistributables desde Steam.')
        wine(str(REDIST), '/install', '/quiet', '/norestart', '/log', r'C:\vcredist-resonance-x64.log')
        if not wait_for_registry(runtime_installed):
            raise SystemExit('No se pudo confirmar Visual C++ x64. Revisa vcredist-resonance-x64.log dentro de drive_c.')
    if not overrides_installed():
        backup(PREFIX / 'user.reg')
        keys = '[HKEY_CURRENT_USER\\Software\\Wine\\DllOverrides]\r\n'
        content = 'Windows Registry Editor Version 5.00\r\n\r\n' + keys
        content += ''.join(f'"{name}"="native,builtin"\r\n' for name in DLLS)
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-16', dir=PREFIX / 'drive_c', suffix='.reg') as reg:
            reg.write(content)
            reg.flush()
            wine('reg.exe', 'import', 'C:\\' + Path(reg.name).name)
        if not wait_for_registry(overrides_installed):
            raise SystemExit('Wine aún no guardó las preferencias de bibliotecas. Ejecuta status antes de volver a intentar.')


def install(config, source, revised):
    require_closed()
    prepare_runtime()
    install_launcher_guard()
    require_closed()
    if revised != source:
        if config.read_text() != source:
            raise SystemExit('Steam cambió la configuración durante la instalación. Vuelve a ejecutarla con Steam cerrado.')
        backup(config)
        atomic_text(config, revised)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('status', 'install'))
    action = parser.parse_args().action
    if not (RUN.is_file() and GAME.is_dir()):
        raise SystemExit('Instala NotProton y descarga RESONANCE desde Steam.')
    config, source = settings_file()
    revised = with_retina_disabled(source)
    if action == 'install':
        try:
            install(config, source, revised)
        except subprocess.CalledProcessError as exc:
            raise SystemExit(f'NotProton terminó con código {exc.returncode}. Revisa los registros locales del prefijo.') from None
    current = config.read_text()
    runtime = runtime_installed()
    overrides = overrides_installed()
    retina_disabled = with_retina_disabled(current) == current
    launcher_ready = GUARD in RUN.read_text()
    print('Visual C++ x64:', 'instalado' if runtime else 'pendiente')
    print('Bibliotecas nativas:', 'configuradas' if overrides else 'pendientes')
    print('Retina:', 'desactivado para RESONANCE' if retina_disabled else 'pendiente')
    print('Detección del juego:', 'configurada' if launcher_ready else 'pendiente')
    if action == 'install' and not all((runtime, overrides, retina_disabled, launcher_ready)):
        raise SystemExit('No se pudo verificar toda la configuración. Revisa los ajustes pendientes.')


if __name__ == '__main__':
    main()
