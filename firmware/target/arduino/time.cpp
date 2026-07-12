#include "time.h"
#include <Arduino.h>

void sleepMilliseconds(int milliseconds)
{
    delay(milliseconds);
}

void sleepSeconds(int seconds)
{
    sleepMilliseconds(seconds * 1000UL);
}
