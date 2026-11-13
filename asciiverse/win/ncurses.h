/* Windows builds use PDCurses, whose header is curses.h: this stands in
 * for ncurses.h there (-Iasciiverse/win in the release workflow). */
#include <curses.h>
