#if defined(TARGET_ARDUINO)

#include <Arduino.h>
#pragma message "TARGET is ARDUINO"

#else

#error "TARGET NOT DEFINED!"

#endif