#!/bin/bash
# Copy the packaged NotProton source into a local build checkout.
set -euo pipefail

source_dir="${1:?Falta la carpeta de código de NotProton}"
destination="${2:?Falta la carpeta de compilación}"
expected_tree=a8f5d932c97ea6efa65111a742db87f7d5938be2
[[ -f "$source_dir/LICENSE" && -f "$source_dir/Makefile" && ! -e "$source_dir/.git" ]] ||
  { printf '%s\n' 'Falta la copia de NotProton del ZIP.' >&2; exit 1; }

parent="$(dirname "$destination")"
mkdir -p "$parent"
stage="$(mktemp -d "$parent/.notproton-src.XXXXXX")"
trap '/bin/rm -r -- "$stage"' EXIT

/usr/bin/ditto "$source_dir" "$stage"
git -C "$stage" init -q
git -C "$stage" -c core.autocrlf=false add -f -- .
[[ "$(git -C "$stage" write-tree)" == "$expected_tree" ]] ||
  { printf '%s\n' 'El código de NotProton no coincide con la revisión del paquete. Vuelve a descomprimir el ZIP completo.' >&2; exit 1; }

# Keep any previous checkout and user diagnostics rather than overwriting them.
if [[ -e "$destination" ]]; then
  backup="$(mktemp -d "$parent/src-backup.XXXXXX")"
  mv "$destination" "$backup/src"
  if ! mv "$stage" "$destination"; then
    mv "$backup/src" "$destination"
    exit 1
  fi
  printf 'Copia de compilación anterior: %s\n' "$backup/src"
else
  mv "$stage" "$destination"
fi
trap - EXIT
