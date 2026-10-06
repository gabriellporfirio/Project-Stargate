/*
 * Pixel Media Checker launcher.
 *
 * Starts the desktop app with the embedded Python runtime, from the folder
 * that contains this executable:
 *
 *   Pixel Media Checker.exe
 *   _runtime\pythonw.exe     runs the app without a console window
 *   _app\app.py
 *
 * Python runs with _app as its working directory, in an environment that
 * ignores any other Python on the machine. The launcher waits for it and
 * returns its exit code. Launcher failures show a message box and return
 * one of the EXIT_* codes below.
 */
#ifndef UNICODE
#define UNICODE
#endif
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <shellapi.h>
#include <stdarg.h>
#include <stdlib.h>
#include <wchar.h>

#include "cmdline.h"

#define APP_TITLE L"Pixel Media Checker"
#define PATH_CAPACITY 32768
#define COMMAND_CAPACITY 131072
#define MESSAGE_CAPACITY 1024

enum {
    EXIT_NO_LOCATION = 10,
    EXIT_NO_FOLDER = 11,
    EXIT_PATH_TOO_LONG = 12,
    EXIT_INCOMPLETE = 13,
    EXIT_NO_MEMORY = 14,
    EXIT_COMMAND_TOO_LONG = 15,
    EXIT_START_FAILED = 16,
};

static wchar_t module_path[PATH_CAPACITY];
static wchar_t base_dir[PATH_CAPACITY];
static wchar_t runtime_dir[PATH_CAPACITY];
static wchar_t app_dir[PATH_CAPACITY];
static wchar_t script_path[PATH_CAPACITY];
static wchar_t python_path[PATH_CAPACITY];
static wchar_t env_value[PATH_CAPACITY];
static wchar_t old_path[PATH_CAPACITY];

static int fail(const wchar_t *message, int code)
{
    MessageBoxW(NULL, message, APP_TITLE, MB_ICONERROR | MB_SETFOREGROUND);
    return code;
}

/*
 * Concatenates the NULL-terminated list of strings into dst. Returns 0 if the
 * result was truncated; dst is always NUL-terminated.
 */
static int concat(wchar_t *dst, size_t capacity, ...)
{
    size_t used = 0;
    int fits = 1;
    va_list parts;
    va_start(parts, capacity);
    for (const wchar_t *part; (part = va_arg(parts, const wchar_t *)) != NULL;) {
        for (; *part; ++part) {
            if (used + 1 >= capacity) {
                fits = 0;
                break;
            }
            dst[used++] = *part;
        }
        if (!fits)
            break;
    }
    va_end(parts);
    dst[used] = L'\0';
    return fits;
}

static int is_file(const wchar_t *path)
{
    /* INVALID_FILE_ATTRIBUTES has the directory bit set, so this rejects both. */
    return (GetFileAttributesW(path) & FILE_ATTRIBUTE_DIRECTORY) == 0;
}

static void prepare_environment(const wchar_t *runtime)
{
    SetEnvironmentVariableW(L"PYTHONHOME", runtime);
    SetEnvironmentVariableW(L"PYTHONNOUSERSITE", L"1");
    SetEnvironmentVariableW(L"PYTHONPATH", NULL);
    SetEnvironmentVariableW(L"PYTHONUTF8", L"1");

    if (concat(env_value, PATH_CAPACITY, runtime, L"\\tcl\\tcl8.6", NULL))
        SetEnvironmentVariableW(L"TCL_LIBRARY", env_value);
    if (concat(env_value, PATH_CAPACITY, runtime, L"\\tcl\\tk8.6", NULL))
        SetEnvironmentVariableW(L"TK_LIBRARY", env_value);

    /* Put the runtime's own DLLs first so a system-wide Python cannot shadow them. */
    DWORD length = GetEnvironmentVariableW(L"PATH", old_path, PATH_CAPACITY);
    if (length == 0 || length >= PATH_CAPACITY)
        old_path[0] = L'\0';
    concat(env_value, PATH_CAPACITY, runtime, L";", runtime, L"\\DLLs;", old_path, NULL);
    SetEnvironmentVariableW(L"PATH", env_value);
}

int WINAPI wWinMain(HINSTANCE instance, HINSTANCE previous, PWSTR command_line, int show)
{
    (void)instance;
    (void)previous;
    (void)command_line;
    (void)show;

    SetProcessDPIAware();

    DWORD length = GetModuleFileNameW(NULL, module_path, PATH_CAPACITY);
    if (length == 0 || length >= PATH_CAPACITY)
        return fail(L"The application location could not be resolved.", EXIT_NO_LOCATION);

    wcsncpy(base_dir, module_path, PATH_CAPACITY - 1);
    base_dir[PATH_CAPACITY - 1] = L'\0';
    wchar_t *separator = wcsrchr(base_dir, L'\\');
    if (separator == NULL)
        return fail(L"The application folder could not be resolved.", EXIT_NO_FOLDER);
    *separator = L'\0';

    if (!concat(runtime_dir, PATH_CAPACITY, base_dir, L"\\_runtime", NULL) ||
        !concat(app_dir, PATH_CAPACITY, base_dir, L"\\_app", NULL) ||
        !concat(script_path, PATH_CAPACITY, app_dir, L"\\app.py", NULL))
        return fail(L"The portable application path is too long.", EXIT_PATH_TOO_LONG);

    int argc = 0;
    wchar_t **argv = CommandLineToArgvW(GetCommandLineW(), &argc);

    if (!concat(python_path, PATH_CAPACITY, runtime_dir, L"\\pythonw.exe", NULL) ||
        !is_file(python_path) || !is_file(script_path)) {
        if (argv != NULL)
            LocalFree(argv);
        return fail(L"This portable build is incomplete. Keep 'Pixel Media Checker.exe', "
                    L"'_app' and '_runtime' together in the extracted folder.",
                    EXIT_INCOMPLETE);
    }

    wchar_t *command = calloc(COMMAND_CAPACITY, sizeof *command);
    if (command == NULL) {
        if (argv != NULL)
            LocalFree(argv);
        return fail(L"Windows could not allocate enough memory to launch the app.",
                    EXIT_NO_MEMORY);
    }

    /* "pythonw.exe" "...\_app\app.py" followed by every argument passed to us,
       such as a file dropped onto the launcher. */
    size_t used = 0;
    int fits = cmdline_append_quoted(command, COMMAND_CAPACITY, &used, python_path) &&
               cmdline_append_char(command, COMMAND_CAPACITY, &used, L' ') &&
               cmdline_append_quoted(command, COMMAND_CAPACITY, &used, script_path);
    for (int i = 1; fits && argv != NULL && i < argc; ++i) {
        fits = cmdline_append_char(command, COMMAND_CAPACITY, &used, L' ') &&
               cmdline_append_quoted(command, COMMAND_CAPACITY, &used, argv[i]);
    }
    if (!fits) {
        free(command);
        if (argv != NULL)
            LocalFree(argv);
        return fail(L"The launch command is too long.", EXIT_COMMAND_TOO_LONG);
    }

    prepare_environment(runtime_dir);

    STARTUPINFOW startup = {0};
    startup.cb = sizeof startup;
    PROCESS_INFORMATION process = {0};
    BOOL started = CreateProcessW(python_path, command, NULL, NULL, FALSE,
                                  CREATE_UNICODE_ENVIRONMENT, NULL, app_dir, &startup,
                                  &process);
    DWORD error = started ? ERROR_SUCCESS : GetLastError();
    free(command);
    if (argv != NULL)
        LocalFree(argv);

    if (!started) {
        wchar_t message[MESSAGE_CAPACITY];
        swprintf(message, MESSAGE_CAPACITY,
                 L"The embedded Python runtime could not start.\n\nWindows error: %lu",
                 (unsigned long)error);
        return fail(message, EXIT_START_FAILED);
    }

    WaitForSingleObject(process.hProcess, INFINITE);
    DWORD exit_code = 0;
    GetExitCodeProcess(process.hProcess, &exit_code);
    CloseHandle(process.hThread);
    CloseHandle(process.hProcess);
    return (int)exit_code;
}
