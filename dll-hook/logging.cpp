/**
 * @file logging.cpp
 * @brief Implementation of logging infrastructure for C++ components
 */

#include "pch.h"
#include "logging.h"
#include <filesystem>

namespace SecurityResearch {
    namespace Logging {

        // Static member definitions
        std::unique_ptr<Logger> Logger::instance_ = nullptr;
        std::mutex Logger::instance_mutex_;

        std::unique_ptr<SecurityLogger> SecurityLogger::instance_ = nullptr;
        std::mutex SecurityLogger::instance_mutex_;

        // Logger implementation
        Logger::Logger()
            : current_level_(LogLevel::INFO)
            , console_enabled_(true)
            , file_enabled_(true) {
        }

        Logger& Logger::GetInstance() {
            std::lock_guard<std::mutex> lock(instance_mutex_);
            if (!instance_) {
                instance_ = std::unique_ptr<Logger>(new Logger());
            }
            return *instance_;
        }

        void Logger::Initialize(const std::string& module_name,
            LogLevel log_level,
            bool enable_console,
            bool enable_file) {
            std::lock_guard<std::mutex> lock(log_mutex_);

            current_level_ = log_level;
            console_enabled_ = enable_console;
            file_enabled_ = enable_file;

            if (file_enabled_) {
                // Create logs directory
                std::filesystem::create_directories("logs");

                // Open log file
                std::string log_filename = "logs/" + module_name + "_cpp.log";
                log_file_.open(log_filename, std::ios::app);

                if (log_file_.is_open()) {
                    LogMessage(LogLevel::INFO, __FILE__, __LINE__, __FUNCTION__,
                        "C++ logging initialized for module: " + module_name);
                }
            }

            LogMessage(LogLevel::INFO, __FILE__, __LINE__, __FUNCTION__,
                "Security research logging system started - authorized use only");
        }

        void Logger::LogMessage(LogLevel level,
            const char* file,
            int line,
            const char* function,
            const std::string& message) {
            if (level < current_level_) {
                return;
            }

            std::lock_guard<std::mutex> lock(log_mutex_);

            // Create formatted message
            std::ostringstream oss;
            oss << GetCurrentTimestamp()
                << " [" << LogLevelToString(level) << "] "
                << std::filesystem::path(file).filename().string() << ":" << line
                << " (" << function << ")"
                << " (PID:" << GetCurrentProcessId()
                << " TID:" << GetCurrentThreadId() << ") - "
                << message;

            std::string formatted_message = oss.str();

            // Console output
            if (console_enabled_) {
                OutputDebugStringA((formatted_message + "\n").c_str());
            }

            // File output
            if (file_enabled_ && log_file_.is_open()) {
                log_file_ << formatted_message << std::endl;
                log_file_.flush();
            }
        }

        void Logger::LogException(const char* file,
            int line,
            const char* function,
            const std::string& context,
            const std::exception& exception) {
            std::ostringstream oss;
            oss << "EXCEPTION in " << context << ": " << exception.what();

            LogMessage(LogLevel::ERR, file, line, function, oss.str());

            // Also log to security logger for audit trail
            SecurityLogger::GetInstance().LogSecurityOperation(
                "EXCEPTION", context, "FAILED", exception.what());
        }

        const char* Logger::LogLevelToString(LogLevel level) {
            switch (level) {
            case LogLevel::DEBUG: return "DEBUG";
            case LogLevel::INFO: return "INFO";
            case LogLevel::WARNING: return "WARNING";
            case LogLevel::ERR: return "ERROR";
            case LogLevel::CRITICAL: return "CRITICAL";
            default: return "UNKNOWN";
            }
        }

        void Logger::Flush() {
            std::lock_guard<std::mutex> lock(log_mutex_);
            if (log_file_.is_open()) {
                log_file_.flush();
            }
        }

        Logger::~Logger() {
            if (log_file_.is_open()) {
                LogMessage(LogLevel::INFO, __FILE__, __LINE__, __FUNCTION__,
                    "C++ logging system shutting down");
                log_file_.close();
            }
        }

        // Utility function implementations
        std::string GetCurrentTimestamp() {
            auto now = std::chrono::system_clock::now();
            auto time_t = std::chrono::system_clock::to_time_t(now);
            auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(
                now.time_since_epoch()) % 1000;

            std::ostringstream oss;
            oss << std::put_time(std::localtime(&time_t), "%Y-%m-%d %H:%M:%S")
                << "." << std::setfill('0') << std::setw(3) << ms.count();

            return oss.str();
        }

        // SecurityLogger implementation
        SecurityLogger::SecurityLogger() {
        }

        SecurityLogger& SecurityLogger::GetInstance() {
            std::lock_guard<std::mutex> lock(instance_mutex_);
            if (!instance_) {
                instance_ = std::unique_ptr<SecurityLogger>(new SecurityLogger());
            }
            return *instance_;
        }

        void SecurityLogger::Initialize(const std::string& module_name) {
            std::lock_guard<std::mutex> lock(log_mutex_);

            // Create logs directory
            std::filesystem::create_directories("logs");

            // Open security audit log file
            std::string log_filename = "logs/security_audit_" + module_name + ".log";
            security_log_.open(log_filename, std::ios::app);

            if (security_log_.is_open()) {
                security_log_ << GetCurrentTimestamp()
                    << " [SECURITY_AUDIT] Security logging initialized for: "
                    << module_name
                    << " (PID:" << GetCurrentProcessId() << ")" << std::endl;
                security_log_.flush();
            }
        }

        void SecurityLogger::LogSecurityOperation(const std::string& operation,
            const std::string& target,
            const std::string& result,
            const std::string& details) {
            std::lock_guard<std::mutex> lock(log_mutex_);

            if (security_log_.is_open()) {
                security_log_ << GetCurrentTimestamp()
                    << " [SECURITY_OP] Operation: " << operation
                    << " | Target: " << target
                    << " | Result: " << result
                    << " | Details: " << details
                    << " | PID: " << GetCurrentProcessId()
                    << " | TID: " << GetCurrentThreadId() << std::endl;
                security_log_.flush();
            }
        }

        void SecurityLogger::LogAPIHook(const std::string& api_name,
            const std::string& module_name,
            bool success,
            const std::string& details) {
            std::ostringstream details_stream;
            details_stream << "API: " << api_name
                << " | Module: " << module_name
                << " | " << details;

            LogSecurityOperation("API_HOOK",
                api_name,
                success ? "SUCCESS" : "FAILED",
                details_stream.str());
        }

        void SecurityLogger::LogProcessOperation(DWORD process_id,
            const std::string& operation,
            bool success,
            const std::string& details) {
            std::ostringstream target_stream;
            target_stream << "PID_" << process_id;

            std::ostringstream details_stream;
            details_stream << "Process Operation: " << operation << " | " << details;

            LogSecurityOperation("PROCESS_OP",
                target_stream.str(),
                success ? "SUCCESS" : "FAILED",
                details_stream.str());
        }

        SecurityLogger::~SecurityLogger() {
            if (security_log_.is_open()) {
                security_log_ << GetCurrentTimestamp()
                    << " [SECURITY_AUDIT] Security logging session ended" << std::endl;
                security_log_.close();
            }
        }

    } // namespace Logging
} // namespace SecurityResearch
