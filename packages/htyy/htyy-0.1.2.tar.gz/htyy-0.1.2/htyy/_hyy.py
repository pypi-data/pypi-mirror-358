"""Empty."""

def C(path):
    setup = """#include <Python.h>
#include <structmember.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <wchar.h>
#include <errno.h>
#if defined(_MSC_VER)
#pragma execution_character_set("utf-8")

/* 平台兼容性预处理 */
#ifdef _WIN32
    #include <windows.h>
    #include <direct.h>
    #include <io.h>
    #include <process.h>
    #include <wincrypt.h>
    #include <sys/stat.h>
    #define PATH_MAX _MAX_PATH
    #define PATH_SEP '\\'
    #define PATH_SEP_STR "\\"
    #define S_ISDIR(mode) (((mode) & S_IFMT) == S_IFDIR)
    #include <pdh.h>
    #include <pdhmsg.h>
    #pragma comment(lib, "pdh.lib")
    #include <direct.h>
    #define CHDIR _chdir
#else
    #define PATH_SEP '/'
    #define PATH_SEP_STR "/"
    #include <dirent.h>
    #include <sys/stat.h>
    #include <sys/types.h>
    #include <unistd.h>
    #include <sys/wait.h>
    #include <sys/utsname.h>
    #include <sys/resource.h>
    #include <sys/ioctl.h>
    #include <termios.h>
    #include <pwd.h>
    #include <grp.h>
    #include <sys/mman.h>
    #include <fcntl.h>
    #include <utime.h>
    #include <time.h>
    #include <sys/time.h>
    #include <unistd.h>
    #define CHDIR chdir
#endif

/* 统一错误处理宏 */
#define SET_OS_ERROR() do { PyErr_SetFromErrno(PyExc_OSError); } while(0)
#define SET_WIN_ERROR() do { PyErr_SetFromWindowsErr(GetLastError()); } while(0)

/***********************
 * 文件系统操作实现
 ***********************/

// mkdir
static PyObject* pyos_mkdir(PyObject* self, PyObject* args) {
    const char* path;
    int mode = 0777;
    if (!PyArg_ParseTuple(args, "s|i", &path, &mode)) return NULL;

#ifdef _WIN32
    if (_mkdir(path) != 0) {
#else
    if (mkdir(path, mode) != 0) {
#endif
        SET_OS_ERROR();
        return NULL;
    }
    Py_RETURN_NONE;
}

static PyObject* pyos_listdir(PyObject* self, PyObject* args) {
    const char* path;
    if (!PyArg_ParseTuple(args, "s", &path)) return NULL;

    PyObject* result = PyList_New(0);

#ifdef _WIN32
    // Windows 宽字符实现
    WIN32_FIND_DATAW findData;
    HANDLE hFind;
    wchar_t wpath[MAX_PATH];
    wchar_t searchPath[MAX_PATH];

    // 转换路径为宽字符
    if (MultiByteToWideChar(CP_UTF8, 0, path, -1, wpath, MAX_PATH) == 0) {
        PyErr_SetFromWindowsErr(GetLastError());
        return NULL;
    }

    // 构造搜索路径
    wcscpy_s(searchPath, MAX_PATH, wpath);
    wcscat_s(searchPath, MAX_PATH, L"\\*");

    hFind = FindFirstFileW(searchPath, &findData);
    if (hFind == INVALID_HANDLE_VALUE) {
        PyErr_SetFromWindowsErr(GetLastError());
        return NULL;
    }

    do {
        if (wcscmp(findData.cFileName, L".") != 0 && 
            wcscmp(findData.cFileName, L"..") != 0) {
            // 转换宽字符文件名回UTF-8
            char utf8Name[MAX_PATH];
            WideCharToMultiByte(CP_UTF8, 0, findData.cFileName, -1,
                               utf8Name, MAX_PATH, NULL, NULL);
            PyList_Append(result, PyUnicode_FromString(utf8Name));
        }
    } while (FindNextFileW(hFind, &findData));

    FindClose(hFind);
#else
    DIR* dir = opendir(path);
    if (!dir) {
        SET_OS_ERROR();
        return NULL;
    }

    struct dirent* entry;
    while ((entry = readdir(dir))) {
        if (strcmp(entry->d_name, ".") && strcmp(entry->d_name, "..")) {
            PyList_Append(result, PyUnicode_FromString(entry->d_name));
        }
    }
    closedir(dir);
#endif

    return result;
}

/***********************
 * 进程管理实现
 ***********************/

// fork (POSIX only)
#ifndef _WIN32
static PyObject* pyos_fork(PyObject* self) {
    pid_t pid = fork();
    if (pid == -1) {
        SET_OS_ERROR();
        return NULL;
    }
    return PyLong_FromLong(pid);
}

// execv (POSIX only)
static PyObject* pyos_execv(PyObject* self, PyObject* args) {
    const char *path;
    PyObject *py_args;
    char **argv;
    int i, argc;
    
    if (!PyArg_ParseTuple(args, "sO!", &path, &PyList_Type, &py_args)) 
        return NULL;
    
    argc = PyList_Size(py_args);
    argv = (char **)PyMem_Malloc((argc + 1) * sizeof(char *));
    if (!argv) return PyErr_NoMemory();
    
    for (i = 0; i < argc; i++) {
        PyObject *item = PyList_GetItem(py_args, i);
        argv[i] = PyUnicode_AsUTF8(item);
        if (!argv[i]) {
            PyMem_Free(argv);
            return NULL;
        }
    }
    argv[argc] = NULL;
    
    execv(path, argv);
    PyMem_Free(argv);
    SET_OS_ERROR();
    return NULL;
}
#endif

// getpid
static PyObject* pyos_getpid(PyObject* self) {
#ifdef _WIN32
    return PyLong_FromLong(GetCurrentProcessId());
#else
    return PyLong_FromLong(getpid());
#endif
}

/***********************
 * 系统信息实现
 ***********************/

// cpu_count
static PyObject* pyos_cpu_count(PyObject* self) {
#ifdef _WIN32
    SYSTEM_INFO sysInfo;
    GetSystemInfo(&sysInfo);
    return PyLong_FromLong(sysInfo.dwNumberOfProcessors);
#else
    long count = sysconf(_SC_NPROCESSORS_ONLN);
    if (count == -1) {
        SET_OS_ERROR();
        return NULL;
    }
    return PyLong_FromLong(count);
#endif
}

static PyObject* pyos_sysconf(PyObject* self, PyObject* args) {
    int name;
    if (!PyArg_ParseTuple(args, "i", &name)) return NULL;

    long ret;
#ifdef _WIN32
    // Windows自定义系统参数常量
    #define SC_PAGESIZE 29
    #define SC_NPROCESSORS_ONLN 39
    
    SYSTEM_INFO si;
    GetSystemInfo(&si);
    
    switch(name) {
        case SC_PAGESIZE:
            ret = si.dwPageSize;
            break;
        case SC_NPROCESSORS_ONLN:
            ret = si.dwNumberOfProcessors;
            break;
        default:
            PyErr_SetString(PyExc_ValueError, "Unsupported sysconf parameter");
            return NULL;
    }
#else
    // POSIX标准实现
    errno = 0;
    ret = sysconf(name);
    if (errno != 0) {
        PyErr_SetFromErrno(PyExc_OSError);
        return NULL;
    }
#endif
    return PyLong_FromLong(ret);
}

/***********************
 * 时间函数实现
 ***********************/

// clock_gettime
static PyObject* pyos_clock_gettime(PyObject* self, PyObject* args) {
    int clk_id;
    struct timespec ts;
    
    if (!PyArg_ParseTuple(args, "i", &clk_id)) return NULL;

#ifdef _WIN32
    if (clk_id == 0) { // CLOCK_REALTIME
        GetSystemTimePreciseAsFileTime((LPFILETIME)&ts);
        ts.tv_sec = (long)((*(int64_t*)&ts) / 10000000 - 11644473600LL);
        ts.tv_nsec = (long)((*(int64_t*)&ts) % 10000000 * 100);
    } else {
        LARGE_INTEGER freq, counter;
        QueryPerformanceFrequency(&freq);
        QueryPerformanceCounter(&counter);
        ts.tv_sec = counter.QuadPart / freq.QuadPart;
        ts.tv_nsec = (long)((counter.QuadPart % freq.QuadPart) * 1e9 / freq.QuadPart);
    }
#else
    if (clock_gettime(clk_id, &ts) != 0) {
        SET_OS_ERROR();
        return NULL;
    }
#endif
    return Py_BuildValue("(dd)", (double)ts.tv_sec, (double)ts.tv_nsec);
}

/***********************
 * 文件操作补充实现
 ***********************/

// fsync
static PyObject* pyos_fsync(PyObject* self, PyObject* args) {
    int fd;
    if (!PyArg_ParseTuple(args, "i", &fd)) return NULL;

#ifdef _WIN32
    HANDLE hFile = (HANDLE)_get_osfhandle(fd);
    if (hFile == INVALID_HANDLE_VALUE) {
        SET_WIN_ERROR();
        return NULL;
    }
    if (!FlushFileBuffers(hFile)) {
        SET_WIN_ERROR();
        return NULL;
    }
#else
    if (fsync(fd) == -1) {
        SET_OS_ERROR();
        return NULL;
    }
#endif
    Py_RETURN_NONE;
}

// umask
static PyObject* pyos_umask(PyObject* self, PyObject* args) {
    int mask;
    if (!PyArg_ParseTuple(args, "i", &mask)) return NULL;

#ifndef _WIN32
    mode_t old_mask = umask((mode_t)mask);
    return PyLong_FromLong((long)old_mask);
#else
    // Windows没有真正的umask实现
    unsigned int old_mask = _umask(mask);
    return PyLong_FromLong(old_mask);
#endif
}

/***********************
 * 进程管理补充实现
 ***********************/

// system
static PyObject* pyos_system(PyObject* self, PyObject* args) {
    const char* command;
    if (!PyArg_ParseTuple(args, "s", &command)) return NULL;
    int ret = system(command);
    return PyLong_FromLong(ret);
}

// kill (POSIX)
#ifndef _WIN32
static PyObject* pyos_kill(PyObject* self, PyObject* args) {
    int pid, sig;
    if (!PyArg_ParseTuple(args, "ii", &pid, &sig)) return NULL;
    
    if (kill(pid, sig) == -1) {
        SET_OS_ERROR();
        return NULL;
    }
    Py_RETURN_NONE;
}
#endif

/***********************
 * 系统信息补充实现
 ***********************/

// pathconf
static PyObject* pyos_pathconf(PyObject* self, PyObject* args) {
    const char* path;
    int name;
    if (!PyArg_ParseTuple(args, "si", &path, &name)) return NULL;

#ifndef _WIN32
    errno = 0;
    long ret = pathconf(path, name);
    if (errno != 0) {
        SET_OS_ERROR();
        return NULL;
    }
    return PyLong_FromLong(ret);
#else
    PyErr_SetString(PyExc_NotImplementedError, "pathconf not supported on Windows");
    return NULL;
#endif
}

/***********************
 * 用户/权限补充实现
 ***********************/

// getlogin
static PyObject* pyos_getlogin(PyObject* self) {
#ifdef _WIN32
    char username[256];
    DWORD size = sizeof(username);
    if (!GetUserNameA(username, &size)) {
        SET_WIN_ERROR();
        return NULL;
    }
    return PyUnicode_FromString(username);
#else
    char* login = getlogin();
    if (!login) {
        SET_OS_ERROR();
        return NULL;
    }
    return PyUnicode_FromString(login);
#endif
}

// getpriority (POSIX)
#ifndef _WIN32
static PyObject* pyos_getpriority(PyObject* self, PyObject* args) {
    int which, who;
    if (!PyArg_ParseTuple(args, "ii", &which, &who)) return NULL;

    errno = 0;
    int prio = getpriority(which, who);
    if (prio == -1 && errno != 0) {
        SET_OS_ERROR();
        return NULL;
    }
    return PyLong_FromLong(prio);
}

// setpriority (POSIX)
static PyObject* pyos_setpriority(PyObject* self, PyObject* args) {
    int which, who, prio;
    if (!PyArg_ParseTuple(args, "iii", &which, &who, &prio)) return NULL;

    if (setpriority(which, who, prio) == -1) {
        SET_OS_ERROR();
        return NULL;
    }
    Py_RETURN_NONE;
}
#endif

/***********************
 * 内存管理补充实现
 ***********************/

// munlock
static PyObject* pyos_munlock(PyObject* self, PyObject* args) {
    void* addr;
    Py_ssize_t len;
    if (!PyArg_ParseTuple(args, "y#", &addr, &len)) return NULL;

#ifdef _WIN32
    if (!VirtualUnlock(addr, len)) {
        SET_WIN_ERROR();
        return NULL;
    }
#else
    if (munlock(addr, len) != 0) {
        SET_OS_ERROR();
        return NULL;
    }
#endif
    Py_RETURN_NONE;
}

/***********************
 * Windows专用实现
 ***********************/

#ifdef _WIN32
// get_osfhandle
static PyObject* pyos_get_osfhandle(PyObject* self, PyObject* args) {
    int fd;
    if (!PyArg_ParseTuple(args, "i", &fd)) return NULL;

    intptr_t handle = _get_osfhandle(fd);
    if (handle == -1) {
        SET_OS_ERROR();
        return NULL;
    }
    return PyLong_FromLongLong(handle);
}

// set_inheritable
static PyObject* pyos_set_inheritable(PyObject* self, PyObject* args) {
    int fd, inheritable;
    if (!PyArg_ParseTuple(args, "ip", &fd, &inheritable)) return NULL;

    if (!SetHandleInformation((HANDLE)_get_osfhandle(fd), 
                              HANDLE_FLAG_INHERIT, 
                              inheritable ? HANDLE_FLAG_INHERIT : 0)) {
        SET_WIN_ERROR();
        return NULL;
    }
    Py_RETURN_NONE;
}
#endif

/***********************
 * 其他补充实现
 ***********************/

// strerror
static PyObject* pyos_strerror(PyObject* self, PyObject* args) {
    int errnum;
    if (!PyArg_ParseTuple(args, "i", &errnum)) return NULL;

#ifdef _WIN32
    LPSTR buffer = NULL;
    DWORD flags = FORMAT_MESSAGE_ALLOCATE_BUFFER | 
                  FORMAT_MESSAGE_FROM_SYSTEM |
                  FORMAT_MESSAGE_IGNORE_INSERTS;
    
    DWORD size = FormatMessageA(
        flags,
        NULL,
        errnum,
        0,
        (LPSTR)&buffer,
        0,
        NULL
    );

    if (size == 0) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to format message");
        return NULL;
    }

    PyObject* result = PyUnicode_FromString(buffer);
    LocalFree(buffer);
    return result;
#else
    return PyUnicode_FromString(strerror(errnum));
#endif
}

/***********************
 * 安全随机数生成实现
 ***********************/

 static PyObject* pyos_urandom(PyObject* self, PyObject* args) {
    int size;
    if (!PyArg_ParseTuple(args, "i", &size)) return NULL;

    if (size <= 0) {
        PyErr_SetString(PyExc_ValueError, "Size must be positive");
        return NULL;
    }

    unsigned char* buffer = (unsigned char*)PyMem_Malloc(size);
    if (!buffer) return PyErr_NoMemory();

#ifdef _WIN32
    HCRYPTPROV hProv = 0;
    if (!CryptAcquireContext(&hProv, NULL, NULL, PROV_RSA_FULL, CRYPT_VERIFYCONTEXT)) {
        PyMem_Free(buffer);
        SET_WIN_ERROR();
        return NULL;
    }
    if (!CryptGenRandom(hProv, size, buffer)) {
        CryptReleaseContext(hProv, 0);
        PyMem_Free(buffer);
        SET_WIN_ERROR();
        return NULL;
    }
    CryptReleaseContext(hProv, 0);
#else
    int fd = open("/dev/urandom", O_RDONLY);
    if (fd == -1) {
        PyMem_Free(buffer);
        SET_OS_ERROR();
        return NULL;
    }
    ssize_t read_bytes = read(fd, buffer, size);
    close(fd);
    if (read_bytes != size) {
        PyMem_Free(buffer);
        PyErr_SetString(PyExc_OSError, "Failed to read enough random bytes");
        return NULL;
    }
#endif

    PyObject* result = PyBytes_FromStringAndSize((const char*)buffer, size);
    PyMem_Free(buffer);
    return result;
}

/***********************
 * 进程优先级管理实现 (POSIX)
 ***********************/

#ifndef _WIN32
static PyObject* pyos_getpriority(PyObject* self, PyObject* args) {
    int which, who;
    if (!PyArg_ParseTuple(args, "ii", &which, &who)) return NULL;

    errno = 0;
    int prio = getpriority(which, who);
    if (errno != 0 && prio == -1) {
        SET_OS_ERROR();
        return NULL;
    }
    return PyLong_FromLong(prio);
}

static PyObject* pyos_setpriority(PyObject* self, PyObject* args) {
    int which, who, prio;
    if (!PyArg_ParseTuple(args, "iii", &which, &who, &prio)) return NULL;

    if (setpriority(which, who, prio) == -1) {
        SET_OS_ERROR();
        return NULL;
    }
    Py_RETURN_NONE;
}
#endif

/***********************
 * 用户信息获取实现
 ***********************/

static PyObject* pyos_getuid(PyObject* self) {
#ifdef _WIN32
    HANDLE hToken;
    DWORD dwSize = 0;
    TOKEN_USER* tokenUser = NULL;
    DWORD uid = 0;

    if (!OpenProcessToken(GetCurrentProcess(), TOKEN_QUERY, &hToken)) {
        SET_WIN_ERROR();
        return NULL;
    }

    if (!GetTokenInformation(hToken, TokenUser, NULL, 0, &dwSize)) {
        if (GetLastError() != ERROR_INSUFFICIENT_BUFFER) {
            CloseHandle(hToken);
            SET_WIN_ERROR();
            return NULL;
        }
    }

    tokenUser = (TOKEN_USER*)PyMem_Malloc(dwSize);
    if (!tokenUser) {
        CloseHandle(hToken);
        return PyErr_NoMemory();
    }

    if (!GetTokenInformation(hToken, TokenUser, tokenUser, dwSize, &dwSize)) {
        PyMem_Free(tokenUser);
        CloseHandle(hToken);
        SET_WIN_ERROR();
        return NULL;
    }

    // 修改getuid实现中的SID处理
    PSID sid = tokenUser->User.Sid;
    DWORD sidSize = GetLengthSid(sid);
    PSID pSid = PyMem_Malloc(sidSize);
    CopySid(sidSize, pSid, sid);
    DWORD subAuthCount = *GetSidSubAuthorityCount(pSid);
    uid = *GetSidSubAuthority(pSid, subAuthCount-1);
    PyMem_Free(pSid);
    CloseHandle(hToken);
    return PyLong_FromLong(uid);
#else
    return PyLong_FromUid(getuid());
#endif
}

/***********************
 * 系统负载获取实现
 ***********************/

static PyObject* pyos_getloadavg(PyObject* self) {
#ifndef _WIN32
    double loadavg[3];
    if (getloadavg(loadavg, 3) == -1) {
        SET_OS_ERROR();
        return NULL;
    }
    return Py_BuildValue("(ddd)", loadavg[0], loadavg[1], loadavg[2]);
#else
    // Windows实现需要PDH库
    PDH_HQUERY query;
    PDH_HCOUNTER counter;
    PDH_FMT_COUNTERVALUE value;
    PDH_STATUS status;

    if ((status = PdhOpenQuery(NULL, 0, &query)) != ERROR_SUCCESS ||
        (status = PdhAddEnglishCounter(query, "\\System\\Processor Queue Length", 0, &counter)) != ERROR_SUCCESS ||
        (status = PdhCollectQueryData(query)) != ERROR_SUCCESS ||
        (status = PdhGetFormattedCounterValue(counter, PDH_FMT_DOUBLE, NULL, &value)) != ERROR_SUCCESS) {
        PdhCloseQuery(query);
        PyErr_SetString(PyExc_OSError, "Failed to get system load");
        return NULL;
    }

    double load = value.doubleValue;
    PdhCloseQuery(query);
    return Py_BuildValue("(ddd)", load, load, load); // Windows返回近似值
#endif
}

/***********************
 * 终端尺寸获取实现
 ***********************/

static PyObject* pyos_terminal_size(PyObject* self) {
#ifdef _WIN32
    CONSOLE_SCREEN_BUFFER_INFO csbi;
    if (!GetConsoleScreenBufferInfo(GetStdHandle(STD_OUTPUT_HANDLE), &csbi)) {
        SET_WIN_ERROR();
        return NULL;
    }
    return Py_BuildValue("(ii)",
        csbi.srWindow.Bottom - csbi.srWindow.Top + 1,
        csbi.srWindow.Right - csbi.srWindow.Left + 1);
#else
    struct winsize ws;
    if (ioctl(STDOUT_FILENO, TIOCGWINSZ, &ws) == -1) {
        SET_OS_ERROR();
        return NULL;
    }
    return Py_BuildValue("(ii)", ws.ws_row, ws.ws_col);
#endif
}

/***********************
 * 内存锁定实现
 ***********************/

static PyObject* pyos_mlock(PyObject* self, PyObject* args) {
    void* addr;
    Py_ssize_t len;
    if (!PyArg_ParseTuple(args, "y#", &addr, &len)) return NULL;

#ifdef _WIN32
    if (!VirtualLock(addr, len)) {
        SET_WIN_ERROR();
        return NULL;
    }
#else
    if (mlock(addr, len) != 0) {
        SET_OS_ERROR();
        return NULL;
    }
#endif
    Py_RETURN_NONE;
}

// 将 Python 对象转为系统路径（兼容 str/bytes，自动处理 Unicode）
static int PyObject_ToSysPath(PyObject *obj, void **path) {
    #if defined(_WIN32)
        // Windows 使用宽字符
        if (PyUnicode_Check(obj)) {
            *path = (wchar_t*)PyUnicode_AsWideCharString(obj, NULL);
            return (*path != NULL) ? 0 : -1;
        } else if (PyBytes_Check(obj)) {
            // 将 bytes 路径解码为宽字符（假设是 UTF-8）
            const char *bytes_path = PyBytes_AsString(obj);
            int wlen = MultiByteToWideChar(CP_UTF8, 0, bytes_path, -1, NULL, 0);
            wchar_t *wpath = (wchar_t*)PyMem_Malloc(wlen * sizeof(wchar_t));
            if (!wpath) {
                PyErr_NoMemory();
                return -1;
            }
            MultiByteToWideChar(CP_UTF8, 0, bytes_path, -1, wpath, wlen);
            *path = wpath;
            return 0;
        } else {
            PyErr_SetString(PyExc_TypeError, "path must be str or bytes");
            return -1;
        }
    #else
        // Unix 使用 UTF-8
        if (PyBytes_Check(obj)) {
            *path = PyBytes_AsString(obj);
            return 0;
        } else if (PyUnicode_Check(obj)) {
            *path = PyUnicode_EncodeFSDefault(obj);
            return (*path != NULL) ? 0 : -1;
        } else {
            PyErr_SetString(PyExc_TypeError, "path must be str or bytes");
            return -1;
        }
    #endif
    }
    
    // 释放路径内存
    static void PySysPath_Free(void *path) {
    #if defined(_WIN32)
        PyMem_Free((wchar_t*)path);
    #else
        if (!PyBytes_Check(path)) {
            Py_DECREF((PyObject*)path);
        }
    #endif
    }

static PyObject* pyos_makedirs(PyObject *self, PyObject *args) {
    PyObject *path_obj;
    int exist_ok = 0;
    void *sys_path;

    if (!PyArg_ParseTuple(args, "O|p", &path_obj, &exist_ok)) return NULL;

    if (PyObject_ToSysPath(path_obj, &sys_path) < 0) return NULL;

#ifdef _WIN32
    const wchar_t *path = (const wchar_t*)sys_path;
#else
    const char *path = (const char*)sys_path;
#endif

    // 递归创建目录（简化版）
    for (size_t i = 0; path[i]; ++i) {
        if (path[i] == PATH_SEP) {
#ifdef _WIN32
            wchar_t tmp = path[i];
            ((wchar_t*)path)[i] = L'\0';
            _wmkdir(path);
            ((wchar_t*)path)[i] = tmp;
#else
            char tmp = path[i];
            ((char*)path)[i] = '\0';
            mkdir(path, 0755);
            ((char*)path)[i] = tmp;
#endif
        }
    }

    // 创建最后一层目录
    int ret =
#ifdef _WIN32
        _wmkdir(path);
#else
        mkdir(path, 0755);
#endif

    PySysPath_Free(sys_path);

    if (ret != 0 && !(exist_ok && errno == EEXIST)) {
        PyErr_SetFromErrnoWithFilename(PyExc_OSError, path);
        return NULL;
    }

    Py_RETURN_NONE;
}

static PyObject* pyos_getcwd(PyObject *self, PyObject *args) {
    #if defined(_WIN32)
        wchar_t buffer[MAX_PATH];
        if (_wgetcwd(buffer, MAX_PATH) == NULL) {
            PyErr_SetFromErrno(PyExc_OSError);
            return NULL;
        }
        return PyUnicode_FromWideChar(buffer, -1);
    #else
        char buffer[4096];
        if (getcwd(buffer, sizeof(buffer)) == NULL) {
            PyErr_SetFromErrno(PyExc_OSError);
            return NULL;
        }
        return PyUnicode_DecodeFSDefault(buffer);
    #endif
    }

static PyObject* pyos_chdir(PyObject *self, PyObject *args) {
        PyObject *path_obj;
        void *sys_path;
    
        if (!PyArg_ParseTuple(args, "O", &path_obj)) return NULL;
    
        if (PyObject_ToSysPath(path_obj, &sys_path) < 0) return NULL;
    
    #ifdef _WIN32
        int ret = _wchdir((const wchar_t*)sys_path);
    #else
        int ret = chdir((const char*)sys_path);
    #endif
    
        PySysPath_Free(sys_path);
    
        if (ret != 0) {
            PyErr_SetFromErrnoWithFilename(PyExc_OSError, (const char*)path_obj);
            return NULL;
        }
    
        Py_RETURN_NONE;
    }


/************************
 * 完整方法表
 ***********************/
static PyMethodDef PyOSMethods[] = {
    // 文件操作
    {"mkdir", pyos_mkdir, METH_VARARGS, "Create directory"},
    {"listdir", pyos_listdir, METH_VARARGS, "List directory contents"},
    {"fsync", pyos_fsync, METH_VARARGS, "Synchronize file state"},
    {"umask", pyos_umask, METH_VARARGS, "Set file creation mask"},
    {"chdir", pyos_chdir, METH_VARARGS, ""},
    {"makedirs", pyos_makedirs, METH_VARARGS, ""},
    {"getcwd", pyos_getcwd, METH_VARARGS, ""},

    // 进程管理
    {"getpid", (PyCFunction)pyos_getpid, METH_NOARGS, "Get process ID"},
    {"system", pyos_system, METH_VARARGS, "Execute shell command"},
    #ifndef _WIN32
    {"fork", (PyCFunction)pyos_fork, METH_NOARGS, "Create child process"},
    {"execv", pyos_execv, METH_VARARGS, "Execute new program"},
    {"setsid", (PyCFunction)pyos_setsid, METH_NOARGS, "Create session"},
    {"kill", pyos_kill, METH_VARARGS, "Send signal to process"},
    #endif

    // 系统信息
    {"cpu_count", (PyCFunction)pyos_cpu_count, METH_NOARGS, "Get CPU core count"},
    {"sysconf", pyos_sysconf, METH_VARARGS, "Get system configuration"},
    {"pathconf", pyos_pathconf, METH_VARARGS, "Get path configuration"},
    {"getloadavg", (PyCFunction)pyos_getloadavg, METH_NOARGS, "Get system load averages"},
    {"terminal_size", (PyCFunction)pyos_terminal_size, METH_NOARGS, "Get terminal dimensions"},

    // 用户/权限
    {"getuid", (PyCFunction)pyos_getuid, METH_NOARGS, "Get user ID"},
    {"getlogin", (PyCFunction)pyos_getlogin, METH_NOARGS, "Get login name"},
    #ifndef _WIN32
    {"getpriority", pyos_getpriority, METH_VARARGS, "Get process priority"},
    {"setpriority", pyos_setpriority, METH_VARARGS, "Set process priority"},
    #endif

    // 时间/随机数
    {"clock_gettime", pyos_clock_gettime, METH_VARARGS, "Get precise time"},
    {"urandom", pyos_urandom, METH_VARARGS, "Generate secure random bytes"},

    // 内存管理
    {"mlock", pyos_mlock, METH_VARARGS, "Lock memory pages"},
    {"munlock", pyos_munlock, METH_VARARGS, "Unlock memory pages"},

    // 错误处理
    {"strerror", pyos_strerror, METH_VARARGS, "Get error message string"},

    // Windows专用
    #ifdef _WIN32
    {"get_osfhandle", pyos_get_osfhandle, METH_VARARGS, "Get Windows file handle"},
    {"set_inheritable", pyos_set_inheritable, METH_VARARGS, "Set handle inheritable"},
    #endif

    {NULL, NULL, 0, NULL}  // 结束标记
};

/***********************
 * 模块初始化
 ***********************/
static struct PyModuleDef pyosmodule = {
    PyModuleDef_HEAD_INIT,
    "pyos",
    "Advanced OS Interface Module",
    -1,
    PyOSMethods
};

PyMODINIT_FUNC PyInit_pyos(void) {
    PyObject *m = PyModule_Create(&pyosmodule);
    if (m == NULL) return NULL;

    // 添加系统常量
    PyModule_AddIntConstant(m, "SC_PAGESIZE", 
    #ifdef _SC_PAGESIZE
        _SC_PAGESIZE
    #else
        4096  // Windows默认页大小
    #endif
    );

    PyModule_AddIntConstant(m, "CLOCK_REALTIME", 0);
    PyModule_AddIntConstant(m, "CLOCK_MONOTONIC", 1);

    // 添加错误代码
    PyModule_AddIntConstant(m, "ENOENT", ENOENT);
    PyModule_AddIntConstant(m, "EACCES", EACCES);
    PyModule_AddIntConstant(m, "ENOMEM", ENOMEM);

    return m;
}
#endif"""

    with open(path + "pyos.c", "w") as f:
        f.write(setup)

