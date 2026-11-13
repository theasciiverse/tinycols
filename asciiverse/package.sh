#!/bin/sh
# Builds tinycols with the Asciiverse changes and packs
# dist/tinycols-<target>.tar.gz (.zip for Windows) for av: the program at
# the top, with LICENSE, README.md and PATCHES.md.
#
#   CC=cc CURSES_LIBS=-lncursesw asciiverse/package.sh x86_64-unknown-linux-musl
#
# CC, CFLAGS, LDFLAGS, CPPFLAGS and CURSES_LIBS as usual.
set -eu
cd "$(dirname "$0")/.."
target="$1"
case "$target" in *windows*) exe=.exe ;; *) exe= ;; esac
${CC:-cc} ${CFLAGS:--O2} ${CPPFLAGS:-} -std=gnu99 -Wall -Iinclude ${LDFLAGS:-} \
  -o "tinycols$exe" src/main.c src/gfx.c src/tinycols/*.c src/queue.c \
  ${CURSES_LIBS:--lncursesw}
stage=stage/tinycols
rm -rf "$stage" && mkdir -p "$stage" dist
cp "tinycols$exe" LICENSE README.md PATCHES.md "$stage/"
if [ -n "$exe" ]; then
  (cd "$stage" && zip -qr "../../dist/tinycols-$target.zip" .)
else
  tar -czf "dist/tinycols-$target.tar.gz" -C "$stage" .
fi
ls dist
