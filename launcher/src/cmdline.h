#ifndef PMC_CMDLINE_H
#define PMC_CMDLINE_H

#include <stddef.h>
#include <wchar.h>

/*
 * Appends one argument to a command line, always wrapped in double quotes,
 * escaped so that CommandLineToArgvW and the Microsoft C runtime parse it
 * back unchanged:
 *
 *   - backslashes are literal unless they precede a double quote;
 *   - backslashes before a double quote (or the closing quote) are doubled;
 *   - a double quote inside the argument becomes \".
 *
 * cmd holds `capacity` characters and is kept NUL-terminated. Returns 0 if
 * the argument does not fit; cmd is then partially written but terminated.
 */
int cmdline_append_quoted(wchar_t *cmd, size_t capacity, size_t *len,
                          const wchar_t *arg);

/* Appends a single character. Returns 0 if it does not fit. */
int cmdline_append_char(wchar_t *cmd, size_t capacity, size_t *len, wchar_t ch);

#endif
