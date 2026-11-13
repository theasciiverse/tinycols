# Changes from upstream

This is the Asciiverse edition of TinyCols, Rigel Di Scala's jewel
matching game for the Unix terminal (C and ncurses, 2022 on,
BSD-3-Clause), from his repository github.com/zedr/tinycols (the
`upstream` remote), at `main` `9ad7a26` (2026-09-01, after release
0.8.6). The `asciiverse` branch carries the changes below.

## Code

- **Links ncurses after the sources** (Makefile). The libraries came
  before the objects on the link line, so with `--as-needed`, the default
  on Debian and Ubuntu, every curses symbol was left undefined and the
  build failed. `NCURSES` defaults to `-lncursesw`, and the program sets
  the locale, so the frame is drawn with Unicode box lines in a UTF-8
  terminal.
- **Scores in 32 bits.** `game_score_t` was 16 bits and wrapped at 65535.
- **Centred.** The well and its panel sit in the middle of the terminal
  and follow a resize; `draw_frame` now honours its offset (it drew the
  well's box from the corner of the screen whatever the offset).
- **A best score for each class** (novice, amateur, pro), shown in the
  panel and kept in the state folder: `$XDG_STATE_HOME/tinycols/best`,
  else `~/.local/state/tinycols/best` (`~/Library/Application
  Support/tinycols` on macOS, `%LOCALAPPDATA%\tinycols` on Windows).
- **The end of a game is shown in the game.** Game over writes the score
  (and "new best!") over the well, with r to play again and q to quit,
  where it used to close after a second and print the score after
  leaving the screen. The final score is still printed on the way out.
- **The keys are listed** under the panel.

## Packaging

- `asciiverse/package.sh` builds the program and packs
  `dist/tinycols-<target>.tar.gz` (`.zip` on Windows) with LICENSE,
  README.md and this file.
- `.github/workflows/release.yml` (after Galaxis'): Linux x86-64 and
  ARM64 built in Alpine with ncurses linked statically, macOS x86-64 and
  ARM64 against the system ncurses, Windows x86-64 cross-built with MinGW
  against PDCurses; SHA256SUMS; runs on `*-av.*` tags.
- `asciiverse/record.sh` and `asciiverse/drive.py` record
  `asciiverse/tinycols.cast`, the 100x30 catalog preview: the driver reads
  the well from the pane, tries every column and turn of each piece with
  the game's own matching rules (chains included), and plays the best.
