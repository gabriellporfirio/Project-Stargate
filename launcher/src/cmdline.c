#include "cmdline.h"

int cmdline_append_char(wchar_t *cmd, size_t capacity, size_t *len, wchar_t ch)
{
    if (*len + 1 >= capacity)
        return 0;
    cmd[(*len)++] = ch;
    cmd[*len] = L'\0';
    return 1;
}

static int append_repeated(wchar_t *cmd, size_t capacity, size_t *len,
                           wchar_t ch, size_t count)
{
    while (count--) {
        if (!cmdline_append_char(cmd, capacity, len, ch))
            return 0;
    }
    return 1;
}

int cmdline_append_quoted(wchar_t *cmd, size_t capacity, size_t *len,
                          const wchar_t *arg)
{
    if (!cmdline_append_char(cmd, capacity, len, L'"'))
        return 0;
    for (const wchar_t *p = arg;; ++p) {
        size_t backslashes = 0;
        while (*p == L'\\') {
            ++backslashes;
            ++p;
        }
        if (*p == L'\0') {
            /* Keep the closing quote from being escaped. */
            if (!append_repeated(cmd, capacity, len, L'\\', backslashes * 2))
                return 0;
            break;
        }
        if (*p == L'"') {
            if (!append_repeated(cmd, capacity, len, L'\\', backslashes * 2 + 1) ||
                !cmdline_append_char(cmd, capacity, len, L'"'))
                return 0;
        } else {
            if (!append_repeated(cmd, capacity, len, L'\\', backslashes) ||
                !cmdline_append_char(cmd, capacity, len, *p))
                return 0;
        }
    }
    return cmdline_append_char(cmd, capacity, len, L'"');
}
