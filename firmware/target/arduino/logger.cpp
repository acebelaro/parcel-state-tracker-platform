#include "logger.hpp"
#include "Arduino.h"

void initializeLogging(void)
{
    Serial.begin(115200);
    while (!Serial)
        delay(10);
}

void printLog(const char *logType, const char *format, ...)
{
    char buffer[128]; // Adjust size based on how long your strings are

    va_list args;
    va_start(args, format);
    vsnprintf(buffer, sizeof(buffer), format, args);
    va_end(args);

    Serial.print(logType);
    Serial.print(" ");
    Serial.println(buffer);
}
