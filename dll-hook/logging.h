/**
 * @file logging.h
 * @brief Comprehensive logging infrastructure for C++ components
 *
 * This header provides standardized logging for all C++ modules in the
 * UpadtedMethod security research project. All logging includes timestamps,
 * process/thread IDs, and supports both console and file output.
 *
 * Educational Context:
 *   This logging system ensures complete audit trails for all security
 *   research activities, supporting responsible and transparent testing.
 */

#pragma once

#include <windows.h>
#include <fstream>
#include <sstream>
#include <chrono>
#include <iomanip>
#include <string>
#include <mutex>
#include <memory>

namespace SecurityResearch {
    namespace Logging {

        /**
         * @brief Log levels for filtering messages
         */
        enum class LogLevel {
            DEBUG = 0,
            INFO = 1,
            WARNING = 2,
            ERR = 3,
            CRITICAL = 4
        };

        /**
         * @brief Thread-safe logger implementation
         */
        class Logger {
        private:
            static std::unique_ptr<Logger> instance_;
            static std::mutex instance_mutex_;

            std::mutex log_mutex_;
            std::ofstream log_file_;
            LogLevel current_level_;
            bool console_enabled_;
            bool file_enabled_;

            Logger();

        public:
            /**
             * @brief Get singleton logger instance
             */
            static Logger& GetInstance();

            /**
             * @brief Initialize logging system
             * @param module_name Name of the module for log file naming
             * @param log_level Minimum log level to output
             * @param enable_console Enable console output
             * @param enable_file Enable file output
             */
            void Initialize(const std::string& module_name,
                LogLevel log_level = LogLevel::INFO,
                bool enable_console = true,
                bool enable_file = true);

            /**
             * @brief Log a message with full context
             * @param level Log level
             * @param file Source file name
             * @param line Line number
             * @param function Function name
             * @param message Log message
             */
            void LogMessage(LogLevel level,
                const char* file,
                int line,
                const char* function,
                const std::string& message);

            /**
             * @brief Log an exception with full context
             * @param file Source file name
             * @param line Line number
             * @param function Function name
             * @param context Description of what was being done
             * @param exception Exception details
             */
            void LogException(const char* file,
                int line,
                const char* function,
                const std::string& context,
                const std::exception& exception);

            /**
             * @brief Get string representation of log level
             */
            static const char* LogLevelToString(LogLevel level);

            /**
             * @brief Flush all pending log messages
             */
            void Flush();

            ~Logger();
        };

        /**
         * @brief Get current timestamp as formatted string
         */
        std::string GetCurrentTimestamp();

        /**
         * @brief Security-specific logger for audit trails
         */
        class SecurityLogger {
        private:
            static std::unique_ptr<SecurityLogger> instance_;
            static std::mutex instance_mutex_;

            std::mutex log_mutex_;
            std::ofstream security_log_;

            SecurityLogger();

        public:
            static SecurityLogger& GetInstance();

            void Initialize(const std::string& module_name);

            /**
             * @brief Log security-related operations
             */
            void LogSecurityOperation(const std::string& operation,
                const std::string& target,
                const std::string& result,
                const std::string& details = "");

            /**
             * @brief Log API hooking activities
             */
            void LogAPIHook(const std::string& api_name,
                const std::string& module_name,
                bool success,
                const std::string& details = "");

            /**
             * @brief Log process manipulation activities
             */
            void LogProcessOperation(DWORD process_id,
                const std::string& operation,
                bool success,
                const std::string& details = "");

            ~SecurityLogger();
        };

        // Convenience macros for easy logging
#define LOG_DEBUG(msg) \
    SecurityResearch::Logging::Logger::GetInstance().LogMessage(\
        SecurityResearch::Logging::LogLevel::DEBUG, __FILE__, __LINE__, __FUNCTION__, msg)

#define LOG_INFO(msg) \
    SecurityResearch::Logging::Logger::GetInstance().LogMessage(\
        SecurityResearch::Logging::LogLevel::INFO, __FILE__, __LINE__, __FUNCTION__, msg)

#define LOG_WARNING(msg) \
    SecurityResearch::Logging::Logger::GetInstance().LogMessage(\
        SecurityResearch::Logging::LogLevel::WARNING, __FILE__, __LINE__, __FUNCTION__, msg)

#define LOG_ERROR(msg) \
    SecurityResearch::Logging::Logger::GetInstance().LogMessage(\
        SecurityResearch::Logging::LogLevel::ERR, __FILE__, __LINE__, __FUNCTION__, msg)

#define LOG_CRITICAL(msg) \
    SecurityResearch::Logging::Logger::GetInstance().LogMessage(\
        SecurityResearch::Logging::LogLevel::CRITICAL, __FILE__, __LINE__, __FUNCTION__, msg)

#define LOG_EXCEPTION(context, ex) \
    SecurityResearch::Logging::Logger::GetInstance().LogException(\
        __FILE__, __LINE__, __FUNCTION__, context, ex)

// Security logging macros
#define LOG_SECURITY_OP(op, target, result, details) \
    SecurityResearch::Logging::SecurityLogger::GetInstance().LogSecurityOperation(op, target, result, details)

#define LOG_API_HOOK(api, module, success, details) \
    SecurityResearch::Logging::SecurityLogger::GetInstance().LogAPIHook(api, module, success, details)

#define LOG_PROCESS_OP(pid, op, success, details) \
    SecurityResearch::Logging::SecurityLogger::GetInstance().LogProcessOperation(pid, op, success, details)

// Performance logging macro
#define LOG_PERFORMANCE(operation) \
    auto start_time = std::chrono::high_resolution_clock::now(); \
    LOG_DEBUG("Starting operation: " + std::string(operation)); \
    auto performance_guard = [&]() { \
        auto end_time = std::chrono::high_resolution_clock::now(); \
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time); \
        LOG_INFO("Operation '" + std::string(operation) + "' completed in " + std::to_string(duration.count()) + "ms"); \
    }; \
    std::unique_ptr<void, decltype(performance_guard)> perf_logger(reinterpret_cast<void*>(1), performance_guard);

    } // namespace Logging
} // namespace SecurityResearch
