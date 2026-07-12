#pragma once

typedef enum
{
    WIFI_STATUS_UNINITIALIZED,
    WIFI_STATUS_CONNECTED,
    WIFI_STATUS_CONNECTION_FAILED,
} tWifiStatus;

typedef enum
{
    WIFI_DATA_SEND_SUCCESS,
    WIFI_DATA_SEND_FAILED,
} tWifiDataSendStatus;

void initializeWifi(void);
tWifiDataSendStatus sendData(float temperatureCelcius, float roll, float pitch);
tWifiStatus getWifiStatus(void);