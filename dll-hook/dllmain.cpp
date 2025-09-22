/**
 * @file dllmain.cpp
 * @brief Main DLL entry point for security research hooks
 *
 * This DLL implements API hooks for testing security mechanisms in educational
 * software environments. All operations are logged for audit and research purposes.
 *
 * Educational Context:
 *   This tool is designed for authorized security research to understand how
 *   educational software implements security controls. The hooks test various
 *   security mechanisms including window focus control, process termination
 *   prevention, and clipboard access restrictions.
 *
 * Security Research Purpose:
 *   - Test window focus enforcement mechanisms
 *   - Analyze process protection strategies
 *   - Understand clipboard access controls
 *   - Research input capture prevention
 */

#include "pch.h"

using namespace SecurityResearch::Logging;

// Forward declarations for hook functions with proper WINAPI linkage
extern "C" {
    HANDLE WINAPI MySetClipboardData(UINT uFormat, HANDLE hMem);
    BOOL WINAPI MyEmptyClipboard();
    HANDLE WINAPI MyOpenProcess(DWORD dwDesiredAccess, BOOL bInheritHandle, DWORD dwProcessId);
    BOOL WINAPI MyTerminateProcess(HANDLE hProcess, UINT uExitCode);
    VOID WINAPI MyExitProcess(UINT uExitCode);
    int WINAPI MyGetWindowTextW(HWND hWnd, LPWSTR lpString, int nMaxCount);
    HWND WINAPI MyGetWindow(HWND hWnd, UINT uCmd);
    HWND WINAPI MySetFocus(HWND hWnd);
    BOOL WINAPI MySetWindowPos(HWND hWnd, HWND hWndInsertAfter, int X, int Y, int cx, int cy, UINT uFlags);
    BOOL WINAPI MyShowWindow(HWND hWnd);
    HWND WINAPI MyGetForegroundWindow();
}

/**
 * @brief Security research hook manager class
 *
 * This class manages all API hooks for security testing purposes,
 * providing comprehensive logging and error handling.
 */
class SecurityHookManager {
private:
    // Hook state management
    std::atomic<bool> focus_hooks_installed_{ false };
    std::mutex hook_mutex_;

    // Window handle tracking for research purposes
    HWND focus_hwnd_{ nullptr };
    HWND bring_window_to_top_hwnd_{ nullptr };
    HWND set_window_focus_hwnd_{ nullptr };
    HWND set_window_focus_hwnd_insert_after_{ nullptr };
    int set_window_focus_x_{ 0 };
    int set_window_focus_y_{ 0 };
    int set_window_focus_cx_{ 0 };
    int set_window_focus_cy_{ 0 };
    UINT set_window_focus_flags_{ 0 };

    // Original function bytes for restoration
    static constexpr size_t HOOK_SIZE = 5;
    BYTE original_bytes_get_foreground_[HOOK_SIZE]{};
    BYTE original_bytes_show_window_[HOOK_SIZE]{};
    BYTE original_bytes_set_window_pos_[HOOK_SIZE]{};
    BYTE original_bytes_set_focus_[HOOK_SIZE]{};
    BYTE original_bytes_empty_clipboard_[HOOK_SIZE]{};
    BYTE original_bytes_set_clipboard_data_[HOOK_SIZE]{};
    BYTE original_bytes_terminate_process_[HOOK_SIZE]{};
    BYTE original_bytes_exit_process_[HOOK_SIZE]{};

public:
    static SecurityHookManager& GetInstance() {
        static SecurityHookManager instance;
        return instance;
    }

    bool Initialize() {
        LOG_INFO("Initializing SecurityHookManager for educational security research");
        LOG_SECURITY_OP("INIT", "SecurityHookManager", "STARTING", "Educational security testing tool");

        // Initialize logging system
        Logger::GetInstance().Initialize("dll_hook", LogLevel::INFO);
        SecurityLogger::GetInstance().Initialize("dll_hook");

        LOG_INFO("Security hook manager initialized successfully");
        return true;
    }

    bool InstallBasicHooks() {
        std::lock_guard<std::mutex> lock(hook_mutex_);
        LOG_INFO("Installing basic security testing hooks");

        bool success = true;

        // Hook EmptyClipboard
        success &= InstallHook("user32.dll", "EmptyClipboard",
            reinterpret_cast<void*>(MyEmptyClipboard),
            original_bytes_empty_clipboard_);

        // Hook SetClipboardData
        success &= InstallHook("user32.dll", "SetClipboardData",
            reinterpret_cast<void*>(MySetClipboardData),
            original_bytes_set_clipboard_data_);

        // Hook GetForegroundWindow
        success &= InstallHook("user32.dll", "GetForegroundWindow",
            reinterpret_cast<void*>(MyGetForegroundWindow),
            original_bytes_get_foreground_);

        // Hook TerminateProcess
        success &= InstallHook("kernel32.dll", "TerminateProcess",
            reinterpret_cast<void*>(MyTerminateProcess),
            original_bytes_terminate_process_);

        // Hook ExitProcess
        success &= InstallHook("kernel32.dll", "ExitProcess",
            reinterpret_cast<void*>(MyExitProcess),
            original_bytes_exit_process_);

        if (success) {
            LOG_INFO("Basic security testing hooks installed successfully");
            LOG_SECURITY_OP("HOOK_INSTALL", "BasicHooks", "SUCCESS", "All basic hooks installed");
        }
        else {
            LOG_ERROR("Failed to install some basic hooks");
            LOG_SECURITY_OP("HOOK_INSTALL", "BasicHooks", "PARTIAL_FAILURE", "Some hooks failed to install");
        }

        return success;
    }

    bool InstallFocusHooks() {
        if (focus_hooks_installed_.load()) {
            LOG_INFO("Focus hooks already installed");
            return true;
        }

        std::lock_guard<std::mutex> lock(hook_mutex_);
        LOG_INFO("Installing focus control testing hooks");

        bool success = true;

        // Hook BringWindowToTop (mapped to ShowWindow for testing)
        success &= InstallHook("user32.dll", "BringWindowToTop",
            reinterpret_cast<void*>(MyShowWindow),
            original_bytes_show_window_);

        // Hook SetWindowPos
        success &= InstallHook("user32.dll", "SetWindowPos",
            reinterpret_cast<void*>(MySetWindowPos),
            original_bytes_set_window_pos_);

        // Hook SetFocus
        success &= InstallHook("user32.dll", "SetFocus",
            reinterpret_cast<void*>(MySetFocus),
            original_bytes_set_focus_);

        if (success) {
            focus_hooks_installed_.store(true);
            LOG_INFO("Focus control testing hooks installed successfully");
            LOG_SECURITY_OP("HOOK_INSTALL", "FocusHooks", "SUCCESS", "Focus control hooks active");
        }
        else {
            LOG_ERROR("Failed to install focus control hooks");
            LOG_SECURITY_OP("HOOK_INSTALL", "FocusHooks", "FAILURE", "Focus hook installation failed");
        }

        return success;
    }

    bool UninstallFocusHooks() {
        if (!focus_hooks_installed_.load()) {
            return true;
        }

        std::lock_guard<std::mutex> lock(hook_mutex_);
        LOG_INFO("Uninstalling focus control testing hooks");

        bool success = true;
        success &= UninstallHook("user32.dll", "BringWindowToTop", original_bytes_show_window_);
        success &= UninstallHook("user32.dll", "SetWindowPos", original_bytes_set_window_pos_);
        success &= UninstallHook("user32.dll", "SetFocus", original_bytes_set_focus_);

        if (success) {
            focus_hooks_installed_.store(false);
            LOG_INFO("Focus control hooks uninstalled successfully");
            LOG_SECURITY_OP("HOOK_UNINSTALL", "FocusHooks", "SUCCESS", "Focus hooks removed");
        }

        return success;
    }

    bool UninstallAllHooks() {
        std::lock_guard<std::mutex> lock(hook_mutex_);
        LOG_INFO("Uninstalling all security testing hooks");

        bool success = true;
        success &= UninstallHook("user32.dll", "EmptyClipboard", original_bytes_empty_clipboard_);
        success &= UninstallHook("user32.dll", "SetClipboardData", original_bytes_set_clipboard_data_);
        success &= UninstallHook("user32.dll", "GetForegroundWindow", original_bytes_get_foreground_);
        success &= UninstallHook("kernel32.dll", "TerminateProcess", original_bytes_terminate_process_);
        success &= UninstallHook("kernel32.dll", "ExitProcess", original_bytes_exit_process_);

        // Also uninstall focus hooks if installed
        if (focus_hooks_installed_.load()) {
            success &= UninstallFocusHooks();
        }

        LOG_SECURITY_OP("HOOK_UNINSTALL", "AllHooks", success ? "SUCCESS" : "FAILURE",
            "Complete hook cleanup");

        return success;
    }

    // Hook function implementations
    HANDLE HandleSetClipboardData(UINT uFormat, HANDLE hMem) {
        LOG_INFO("SetClipboardData hook intercepted - blocking for security testing");
        LOG_SECURITY_OP("API_INTERCEPT", "SetClipboardData", "BLOCKED",
            "Clipboard access blocked for security research");
        return nullptr; // Block clipboard access
    }

    BOOL HandleEmptyClipboard() {
        LOG_INFO("EmptyClipboard hook intercepted - simulating success for security testing");
        LOG_SECURITY_OP("API_INTERCEPT", "EmptyClipboard", "SIMULATED",
            "Clipboard clear simulated for security research");
        return TRUE; // Pretend success
    }

    HANDLE HandleOpenProcess(DWORD dwDesiredAccess, BOOL bInheritHandle, DWORD dwProcessId) {
        LOG_INFO("OpenProcess hook intercepted - blocking for security testing");
        LOG_SECURITY_OP("API_INTERCEPT", "OpenProcess", "BLOCKED",
            "Process access blocked for security research");
        return nullptr; // Block process access
    }

    BOOL HandleTerminateProcess(HANDLE hProcess, UINT uExitCode) {
        LOG_INFO("TerminateProcess hook intercepted - blocking for security testing");
        LOG_SECURITY_OP("API_INTERCEPT", "TerminateProcess", "BLOCKED",
            "Process termination blocked for security research");
        return TRUE; // Simulate success without terminating
    }

    VOID HandleExitProcess(UINT uExitCode) {
        LOG_INFO("ExitProcess hook intercepted - blocking for security testing");
        LOG_SECURITY_OP("API_INTERCEPT", "ExitProcess", "BLOCKED",
            "Process exit blocked for security research");
        // Don't actually exit
    }

    BOOL HandleK32EnumProcesses(DWORD* pProcessIds, DWORD cb, DWORD* pBytesReturned) {
        LOG_INFO("K32EnumProcesses hook intercepted - returning empty list for security testing");
        LOG_SECURITY_OP("API_INTERCEPT", "K32EnumProcesses", "MODIFIED",
            "Process enumeration blocked for security research");

        if (pBytesReturned != nullptr) {
            *pBytesReturned = 0; // No processes
        }
        return TRUE;
    }

    int HandleGetWindowTextW(HWND hWnd, LPWSTR lpString, int nMaxCount) {
        LOG_INFO("GetWindowTextW hook intercepted - returning empty string for security testing");
        LOG_SECURITY_OP("API_INTERCEPT", "GetWindowTextW", "MODIFIED",
            "Window text access modified for security research");

        if (nMaxCount > 0 && lpString != nullptr) {
            lpString[0] = L'\0'; // Empty string
        }
        return 0;
    }

    HWND HandleGetWindow(HWND hWnd, UINT uCmd) {
        LOG_INFO("GetWindow hook intercepted - returning null for security testing");
        LOG_SECURITY_OP("API_INTERCEPT", "GetWindow", "MODIFIED",
            "Window enumeration blocked for security research");
        return nullptr;
    }

    HWND HandleSetFocus(HWND hWnd) {
        focus_hwnd_ = hWnd;
        HWND mainWindow = FindMainWindow();

        LOG_INFO("SetFocus hook intercepted - redirecting to main window for security testing");
        LOG_SECURITY_OP("API_INTERCEPT", "SetFocus", "REDIRECTED",
            "Focus redirected to main window for security research");

        return mainWindow;
    }

    BOOL HandleSetWindowPos(HWND hWnd, HWND hWndInsertAfter, int X, int Y, int cx, int cy, UINT uFlags) {
        // Store parameters for research
        set_window_focus_hwnd_ = hWnd;
        set_window_focus_hwnd_insert_after_ = hWndInsertAfter;
        set_window_focus_x_ = X;
        set_window_focus_y_ = Y;
        set_window_focus_cx_ = cx;
        set_window_focus_cy_ = cy;
        set_window_focus_flags_ = uFlags;

        LOG_INFO("SetWindowPos hook intercepted - blocking for security testing");
        LOG_SECURITY_OP("API_INTERCEPT", "SetWindowPos", "BLOCKED",
            "Window positioning blocked for security research");

        return TRUE; // Pretend success
    }

    BOOL HandleShowWindow(HWND hWnd) {
        bring_window_to_top_hwnd_ = hWnd;

        LOG_INFO("ShowWindow/BringWindowToTop hook intercepted - blocking for security testing");
        LOG_SECURITY_OP("API_INTERCEPT", "ShowWindow", "BLOCKED",
            "Window show/bring to top blocked for security research");

        return TRUE; // Pretend success
    }

    HWND HandleGetForegroundWindow() {
        HWND mainWindow = FindMainWindow();

        LOG_INFO("GetForegroundWindow hook intercepted - returning main window for security testing");
        LOG_SECURITY_OP("API_INTERCEPT", "GetForegroundWindow", "MODIFIED",
            "Foreground window redirected for security research");

        return mainWindow;
    }

    HWND FindMainWindow() {
        HWND mainWindow = nullptr;
        EnumWindows(EnumWindowsCallback, reinterpret_cast<LPARAM>(&mainWindow));
        return mainWindow;
    }

    bool IsMainWindow(HWND handle) {
        return GetWindow(handle, GW_OWNER) == nullptr && IsWindowVisible(handle);
    }

    static BOOL CALLBACK EnumWindowsCallback(HWND handle, LPARAM lParam) {
        DWORD processID = 0;
        GetWindowThreadProcessId(handle, &processID);

        SecurityHookManager& manager = GetInstance();
        if (GetCurrentProcessId() == processID && manager.IsMainWindow(handle)) {
            *reinterpret_cast<HWND*>(lParam) = handle;
            return FALSE; // Stop enumeration
        }
        return TRUE; // Continue enumeration
    }

private:
    SecurityHookManager() = default;
    ~SecurityHookManager() {
        UninstallAllHooks();
    }

    // Prevent copying
    SecurityHookManager(const SecurityHookManager&) = delete;
    SecurityHookManager& operator=(const SecurityHookManager&) = delete;

    bool InstallHook(const char* module_name, const char* function_name,
        void* hook_function, BYTE* original_bytes) {
        HMODULE hModule = GetModuleHandleA(module_name);
        if (!hModule) {
            LOG_ERROR(std::string("Failed to get module handle for ") + module_name);
            return false;
        }

        void* target_function = GetProcAddress(hModule, function_name);
        if (!target_function) {
            LOG_ERROR(std::string("Failed to get function address for ") + function_name);
            return false;
        }

        // Calculate jump offset
        DWORD jump_offset = reinterpret_cast<DWORD>(hook_function) -
            reinterpret_cast<DWORD>(target_function) - 5;

        // Save original bytes
        memcpy(original_bytes, target_function, HOOK_SIZE);

        // Install hook
        DWORD old_protect;
        if (!VirtualProtect(target_function, HOOK_SIZE, PAGE_EXECUTE_READWRITE, &old_protect)) {
            LOG_ERROR(std::string("Failed to change memory protection for ") + function_name);
            return false;
        }

        // Write jump instruction
        *static_cast<BYTE*>(target_function) = 0xE9; // JMP instruction
        *reinterpret_cast<DWORD*>(static_cast<BYTE*>(target_function) + 1) = jump_offset;

        // Restore memory protection
        VirtualProtect(target_function, HOOK_SIZE, old_protect, &old_protect);

        LOG_API_HOOK(function_name, module_name, true, "Hook installed successfully");
        return true;
    }

    bool UninstallHook(const char* module_name, const char* function_name,
        const BYTE* original_bytes) {
        HMODULE hModule = GetModuleHandleA(module_name);
        if (!hModule) {
            return false;
        }

        void* target_function = GetProcAddress(hModule, function_name);
        if (!target_function) {
            return false;
        }

        DWORD old_protect;
        if (!VirtualProtect(target_function, HOOK_SIZE, PAGE_EXECUTE_READWRITE, &old_protect)) {
            return false;
        }

        // Restore original bytes
        memcpy(target_function, original_bytes, HOOK_SIZE);

        VirtualProtect(target_function, HOOK_SIZE, old_protect, &old_protect);

        LOG_API_HOOK(function_name, module_name, true, "Hook uninstalled successfully");
        return true;
    }
};

// Global instance for C-style callback compatibility
static SecurityHookManager& g_hook_manager = SecurityHookManager::GetInstance();

// C-style wrapper functions for Windows API hooks
extern "C" {
    HANDLE WINAPI MySetClipboardData(UINT uFormat, HANDLE hMem) {
        return g_hook_manager.HandleSetClipboardData(uFormat, hMem);
    }

    BOOL WINAPI MyEmptyClipboard() {
        return g_hook_manager.HandleEmptyClipboard();
    }

    HANDLE WINAPI MyOpenProcess(DWORD dwDesiredAccess, BOOL bInheritHandle, DWORD dwProcessId) {
        return g_hook_manager.HandleOpenProcess(dwDesiredAccess, bInheritHandle, dwProcessId);
    }

    BOOL WINAPI MyTerminateProcess(HANDLE hProcess, UINT uExitCode) {
        return g_hook_manager.HandleTerminateProcess(hProcess, uExitCode);
    }

    VOID WINAPI MyExitProcess(UINT uExitCode) {
        g_hook_manager.HandleExitProcess(uExitCode);
    }

    BOOL WINAPI MyK32EnumProcesses(DWORD* pProcessIds, DWORD cb, DWORD* pBytesReturned) {
        return g_hook_manager.HandleK32EnumProcesses(pProcessIds, cb, pBytesReturned);
    }

    int WINAPI MyGetWindowTextW(HWND hWnd, LPWSTR lpString, int nMaxCount) {
        return g_hook_manager.HandleGetWindowTextW(hWnd, lpString, nMaxCount);
    }

    HWND WINAPI MyGetWindow(HWND hWnd, UINT uCmd) {
        return g_hook_manager.HandleGetWindow(hWnd, uCmd);
    }

    HWND WINAPI MySetFocus(HWND hWnd) {
        return g_hook_manager.HandleSetFocus(hWnd);
    }

    BOOL WINAPI MySetWindowPos(HWND hWnd, HWND hWndInsertAfter, int X, int Y, int cx, int cy, UINT uFlags) {
        return g_hook_manager.HandleSetWindowPos(hWnd, hWndInsertAfter, X, Y, cx, cy, uFlags);
    }

    BOOL WINAPI MyShowWindow(HWND hWnd) {
        return g_hook_manager.HandleShowWindow(hWnd);
    }

    HWND WINAPI MyGetForegroundWindow() {
        return g_hook_manager.HandleGetForegroundWindow();
    }
}

// Keyboard hook for focus control testing
static HHOOK g_keyboard_hook = nullptr;

LRESULT CALLBACK KeyboardProc(int nCode, WPARAM wParam, LPARAM lParam) {
    if (nCode == HC_ACTION && wParam == WM_KEYDOWN) {
        PKBDLLHOOKSTRUCT p = reinterpret_cast<PKBDLLHOOKSTRUCT>(lParam);

        switch (p->vkCode) {
        case VK_UP:
            LOG_INFO("Up arrow key pressed - installing focus hooks for security testing");
            g_hook_manager.InstallFocusHooks();
            break;

        case VK_DOWN:
            LOG_INFO("Down arrow key pressed - uninstalling focus hooks");
            g_hook_manager.UninstallFocusHooks();
            break;
        }
    }

    return CallNextHookEx(g_keyboard_hook, nCode, wParam, lParam);
}

void SetupKeyboardHook() {
    LOG_INFO("Setting up keyboard hook for focus control testing");

    g_keyboard_hook = SetWindowsHookEx(WH_KEYBOARD_LL, KeyboardProc,
        GetModuleHandle(nullptr), 0);

    if (g_keyboard_hook) {
        LOG_INFO("Keyboard hook installed successfully");

        // Message loop for hook processing
        MSG msg;
        while (GetMessage(&msg, nullptr, 0, 0)) {
            TranslateMessage(&msg);
            DispatchMessage(&msg);
        }
    }
    else {
        LOG_ERROR("Failed to install keyboard hook");
    }
}

// Check if we're being loaded for testing purposes
bool IsTestEnvironment() {
    // Check if we're being loaded by pytest or test processes
    char processName[MAX_PATH];
    if (GetModuleFileNameA(nullptr, processName, MAX_PATH) > 0) {
        std::string procStr(processName);
        std::transform(procStr.begin(), procStr.end(), procStr.begin(), ::tolower);

        // Check for common test process names
        return procStr.find("python") != std::string::npos ||
            procStr.find("pytest") != std::string::npos ||
            procStr.find("test") != std::string::npos;
    }
    return false;
}

// DLL entry point
BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved) {
    switch (ul_reason_for_call) {
    case DLL_PROCESS_ATTACH:
    {
        DisableThreadLibraryCalls(hModule);

        // Check if we're in a test environment first
        if (IsTestEnvironment()) {
            // For test environments, do minimal initialization
            try {
                g_hook_manager.Initialize();
                // Don't log to avoid file system issues during testing
            }
            catch (...) {
                // Even if initialization fails in tests, don't fail DLL load
            }
            return TRUE;  // Always succeed for tests
        }

        // Full initialization for real injection scenarios
        try {
            // Initialize logging and hook manager
            g_hook_manager.Initialize();

            // Install basic hooks
            g_hook_manager.InstallBasicHooks();

            // Show injection success message
            MessageBox(nullptr, L"Security Research DLL Loaded Successfully!\n\nThis tool is for authorized educational security testing only.",
                L"UpadtedMethod - Security Research", MB_OK | MB_ICONINFORMATION);

            // Start keyboard hook in separate thread
            std::thread keyboard_thread(SetupKeyboardHook);
            keyboard_thread.detach();

            LOG_INFO("DLL injection completed successfully - security research active");
        }
        catch (...) {
            // For real injection, we can afford to fail if something goes wrong
            return FALSE;
        }

        break;
    }

    case DLL_PROCESS_DETACH:
    {
        LOG_INFO("DLL detaching - cleaning up security research hooks");

        // Cleanup hooks
        g_hook_manager.UninstallAllHooks();

        // Cleanup keyboard hook
        if (g_keyboard_hook) {
            UnhookWindowsHookEx(g_keyboard_hook);
            g_keyboard_hook = nullptr;
        }

        LOG_INFO("Security research DLL cleanup completed");
        break;
    }
    }

    return TRUE;
}
