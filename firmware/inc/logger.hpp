#pragma once

// Log type prefixes
#define LOG_TYPE_INFO "[INFO] "
#define LOG_TYPE_WARNING "[WARN] "
#define LOG_TYPE_ERROR "[ERROR]"

// Variadic Macros mapping directly to our unified implementation
#define LOG_INFO(format, ...) printLog(LOG_TYPE_INFO, format, ##__VA_ARGS__)
#define LOG_WARN(format, ...) printLog(LOG_TYPE_WARNING, format, ##__VA_ARGS__)
#define LOG_ERROR(format, ...) printLog(LOG_TYPE_ERROR, format, ##__VA_ARGS__)

void initializeLogging(void);

// Unified internal formatting printing engine
void printLog(const char *logType, const char *format, ...);