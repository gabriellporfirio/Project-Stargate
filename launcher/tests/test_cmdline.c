/* Host-side tests for the launcher's argument quoting. */
#include <stdio.h>
#include <wchar.h>

#include "cmdline.h"

static int failures;

static void expect_quoted(const wchar_t *arg, const wchar_t *expected)
{
    wchar_t cmd[256];
    size_t len = 0;
    cmd[0] = L'\0';
    if (!cmdline_append_quoted(cmd, 256, &len, arg) || wcscmp(cmd, expected) != 0 ||
        len != wcslen(expected)) {
        fwprintf(stderr, L"FAIL: [%ls] -> [%ls], expected [%ls]\n", arg, cmd, expected);
        ++failures;
    }
}

static void test_quoting(void)
{
    expect_quoted(L"plain", L"\"plain\"");
    expect_quoted(L"", L"\"\"");
    expect_quoted(L"C:\\Program Files\\Pixel\\_runtime\\python.exe",
                  L"\"C:\\Program Files\\Pixel\\_runtime\\python.exe\"");
    /* Backslashes are literal unless they precede a quote. */
    expect_quoted(L"\\\\server\\share\\clip.mp4", L"\"\\\\server\\share\\clip.mp4\"");
    /* A trailing backslash is doubled so it does not escape the closing quote. */
    expect_quoted(L"C:\\Media\\", L"\"C:\\Media\\\\\"");
    expect_quoted(L"C:\\Media\\\\", L"\"C:\\Media\\\\\\\\\"");
    /* Embedded quotes, with and without preceding backslashes. */
    expect_quoted(L"say \"hi\"", L"\"say \\\"hi\\\"\"");
    expect_quoted(L"a\\\"b", L"\"a\\\\\\\"b\"");
    /* Non-ASCII file names pass through untouched. */
    expect_quoted(L"Caf\u00e9 \u2014 menu.pdf", L"\"Caf\u00e9 \u2014 menu.pdf\"");
}

static void test_building_a_command(void)
{
    wchar_t cmd[256];
    size_t len = 0;
    const wchar_t *expected = L"\"pythonw.exe\" \"app.py\" \"C:\\Media\" \"my clip.mp4\"";
    int ok = cmdline_append_quoted(cmd, 256, &len, L"pythonw.exe") &&
             cmdline_append_char(cmd, 256, &len, L' ') &&
             cmdline_append_quoted(cmd, 256, &len, L"app.py") &&
             cmdline_append_char(cmd, 256, &len, L' ') &&
             cmdline_append_quoted(cmd, 256, &len, L"C:\\Media") &&
             cmdline_append_char(cmd, 256, &len, L' ') &&
             cmdline_append_quoted(cmd, 256, &len, L"my clip.mp4");
    if (!ok || wcscmp(cmd, expected) != 0) {
        fwprintf(stderr, L"FAIL: built [%ls], expected [%ls]\n", cmd, expected);
        ++failures;
    }
}

static void test_capacity(void)
{
    /* "abcd" needs 6 characters plus the terminator. */
    wchar_t cmd[7];
    size_t len = 0;
    if (!cmdline_append_quoted(cmd, 7, &len, L"abcd") || wcscmp(cmd, L"\"abcd\"") != 0) {
        fwprintf(stderr, L"FAIL: exact fit was rejected\n");
        ++failures;
    }
    len = 0;
    if (cmdline_append_quoted(cmd, 6, &len, L"abcd") || cmd[len] != L'\0' || len >= 6) {
        fwprintf(stderr, L"FAIL: overflow was not reported or left cmd unterminated\n");
        ++failures;
    }
    len = 0;
    if (cmdline_append_quoted(cmd, 1, &len, L"") || len != 0) {
        fwprintf(stderr, L"FAIL: no room for the opening quote was not reported\n");
        ++failures;
    }
}

int main(void)
{
    test_quoting();
    test_building_a_command();
    test_capacity();
    if (failures) {
        fprintf(stderr, "%d failure(s)\n", failures);
        return 1;
    }
    puts("cmdline: all tests passed");
    return 0;
}
