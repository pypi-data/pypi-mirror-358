#ifndef LOGGER_HPP_
#define LOGGER_HPP_

#include <string>
#include <fstream>
#include <iostream>
#include <mutex>
#include <memory>
#include <chrono>
#include <iomanip>
#include <ctime>
#include <sstream>

namespace cyborg {

// Enum representing the severity level of a log message.
enum LogLevel {
    #ifdef DEBUG
    Debug,      // Detailed debug information (only included in debug builds)
    #endif
    Info,       // General information about program execution
    Warning,    // Something unexpected, but not necessarily an error
    Error,      // A recoverable error has occurred
    Critical    // A severe error that may cause program termination
};

class Logger {
public:
    // Returns a singleton instance of the logger
    static Logger& Instance() {
        static Logger instance;
        return instance;
    }

    // Configures the logger with a log level, output type, and optional file path
    void Configure(LogLevel level, bool to_file, const std::string& file_path = "") {
        std::lock_guard<std::mutex> lock(log_mutex_);
        current_level_ = level;
        to_file_ = to_file;

        if (to_file_) {
            if (file_stream_.is_open()) {
                file_stream_.close();
            }
            file_stream_.open(file_path, std::ios::out | std::ios::app);
            if (!file_stream_) {
                std::cerr << "[Logger] Failed to open log file: " << file_path << std::endl;
                to_file_ = false;
            }
        }
    }

    // Logging interface functions for each severity level
    void Debug(const std::string& msg) {
#ifdef DEBUG
        Log(LogLevel::Debug, msg);
#endif
    }
    void Info(const std::string& msg) {
        Log(LogLevel::Info, msg);
    }
    void Warning(const std::string& msg) {
        Log(LogLevel::Warning, msg);
    }
    void Error(const std::string& msg) {
        Log(LogLevel::Error, msg);
    }
    void Critical(const std::string& msg) {
        Log(LogLevel::Critical, msg);
    }

private:
    Logger() = default;
    ~Logger() {
        if (file_stream_.is_open()) {
            file_stream_.close();
        }
    }

    Logger(const Logger&) = delete;
    Logger& operator=(const Logger&) = delete;

    // Core function that handles formatting and outputting the log message
    void Log(LogLevel level, const std::string& msg) {
        if (level < current_level_) return;

        auto now = std::chrono::system_clock::now();
        auto time = std::chrono::system_clock::to_time_t(now);

        std::ostringstream out;
        out << "[" << std::put_time(std::localtime(&time), "%Y-%m-%d %H:%M:%S") << "]";
        out << "[" << LogLevelToString(level) << "] " << msg << std::endl;

        std::lock_guard<std::mutex> lock(log_mutex_);

        if (to_file_ && file_stream_.is_open()) {
            file_stream_ << out.str();
            file_stream_.flush();
        } else {
            if (level >= LogLevel::Error) {
                std::cerr << out.str();
            } else {
                std::cout << out.str();
            }
        }
    }

    // Converts LogLevel enum to string label
    std::string LogLevelToString(LogLevel level) {
        switch (level) {
            #ifdef DEBUG
            case LogLevel::Debug: return "DEBUG";
            #endif
            case LogLevel::Info: return "INFO";
            case LogLevel::Warning: return "WARNING";
            case LogLevel::Error: return "ERROR";
            case LogLevel::Critical: return "CRITICAL";
            default: return "UNKNOWN";
        }
    }

    LogLevel current_level_ = LogLevel::Error;
    bool to_file_ = false;
    std::ofstream file_stream_;
    std::mutex log_mutex_;
};

}  // namespace cyborg

#endif  // LOGGER_HPP_
