/*
 * Stand-in for python.exe / pythonw.exe in the launcher behaviour tests.
 *
 * Writes what it was started with to report.txt next to itself (UTF-8,
 * one key=value per line) and exits with the code in FAKE_EXIT.
 */
#ifndef UNICODE
#define UNICODE
#endif
#include <windows.h>
#include <shellapi.h>
#include <stdio.h>
#include <wchar.h>

static wchar_t buffer[32768];
static FILE *report;

static void write_line(const wchar_t *key, const wchar_t *value)
{
    static char utf8[4 * 32768];
    fprintf(report, "%ls=", key);
    int size = WideCharToMultiByte(CP_UTF8, 0, value, -1, utf8, sizeof utf8, NULL, NULL);
    fwrite(utf8, 1, size > 0 ? (size_t)size - 1 : 0, report);
    fputc('\n', report);
}

int wmain(void)
{
    wchar_t exe[MAX_PATH], path[MAX_PATH], key[32];
    GetModuleFileNameW(NULL, exe, MAX_PATH);
    wcscpy(path, exe);
    wcscpy(wcsrchr(path, L'\\') + 1, L"report.txt");
    report = _wfopen(path, L"wb");
    if (report == NULL)
        return 99;

    write_line(L"interpreter", wcsrchr(exe, L'\\') + 1);
    int argc = 0;
    wchar_t **argv = CommandLineToArgvW(GetCommandLineW(), &argc);
    for (int i = 0; i < argc; ++i) {
        swprintf(key, 32, L"argv%d", i);
        write_line(key, argv[i]);
    }
    GetCurrentDirectoryW(32768, buffer);
    write_line(L"cwd", buffer);

    static const wchar_t *const names[] = {L"PYTHONHOME", L"PYTHONNOUSERSITE", L"PYTHONPATH",
                                           L"PYTHONUTF8", L"TCL_LIBRARY",      L"TK_LIBRARY",
                                           L"PATH"};
    for (size_t i = 0; i < sizeof names / sizeof names[0]; ++i) {
        if (GetEnvironmentVariableW(names[i], buffer, 32768))
            write_line(names[i], buffer);
    }
    fclose(report);

    return GetEnvironmentVariableW(L"FAKE_EXIT", buffer, 32768) ? _wtoi(buffer) : 0;
}
