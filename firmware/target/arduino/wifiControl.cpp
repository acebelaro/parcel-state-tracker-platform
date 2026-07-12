#include "wifiControl.hpp"
#include "logger.hpp"
#include "time.hpp"
#include <Arduino.h>
#include <WiFiS3.h>

#define WIFI_CONNECTING_TIMEOUT_SECONDS 20
#define WIFI_IP_STATUS_CHECK_DURATION_SECOND 5
#define WIFI_IP_ADDRESS_GET_TIMEOUT_SECONDS 60
#define POST_TARGET "POST /api/v1/ingest HTTP/1.1"
#define RESPONSE_MAX_LEN 200

static tWifiStatus wifiStatus = WIFI_STATUS_UNINITIALIZED;
static char response[RESPONSE_MAX_LEN] = "";

static void connectToWifi(void);
static void waitForProperIpAddress(void);
static int readResponse(WiFiClient *client);

void initializeWifi(void)
{
    // Check if the onboard ESP32 Wi-Fi module is responding
    if (WiFi.status() == WL_NO_MODULE)
    {
        LOG_ERROR("Wi-Fi module communication failed!");
    }
    else
    {
        String fv = WiFi.firmwareVersion();
        LOG_INFO("Wifi Version: %s", fv.c_str());

        connectToWifi();

        if (WIFI_STATUS_CONNECTION_FAILED != wifiStatus)
        {
            waitForProperIpAddress();
        }
    }
}

tWifiDataSendStatus sendData(float temperatureCelcius, float roll, float pitch)
{
    tWifiDataSendStatus sendDataResult = WIFI_DATA_SEND_FAILED;
    WiFiClient client;

    // Build the dynamic JSON string format layout
    String jsonPayload = String("{") +
                         "\"courier_id\":" + String("\"") + String(COURIER_ID) + String("\"") + String(",") +
                         "\"device_id\":" + String("\"") + String(DEVICE_ID) + String("\"") + String(",") +
                         "\"temperature_celsius\":" + String(temperatureCelcius, 2) + String(",") +
                         "\"pitch\":" + String(pitch, 2) + String(",") +
                         "\"roll\":" + String(roll, 2) +
                         String("}");

    // Target pointer for transmission measurements
    const char *rawPayload = jsonPayload.c_str();
    LOG_INFO("Sending '%s'...", rawPayload);

    if (client.connect(SERVICE_INGEST_TARGET_IP, SERVICE_INGEST_TARGET_PORT))
    {
        int payloadLength = strlen(rawPayload);

        client.println(POST_TARGET);
        client.print("Host: ");
        client.print(SERVICE_INGEST_TARGET_IP);
        client.print(":");
        client.println(SERVICE_INGEST_TARGET_PORT);

        client.println("Content-Type: application/json");
        client.println("Connection: close");
        client.print("Content-Length: ");
        client.println(payloadLength);
        client.println(); // Header terminal boundary break

        // Deliver the raw string packet
        client.print(rawPayload);

        readResponse(&client);

        client.stop();
        LOG_INFO("Transmission finalized with response %s", response);
        sendDataResult = WIFI_DATA_SEND_SUCCESS;
    }

    return sendDataResult;
}

tWifiStatus getWifiStatus(void)
{
    return wifiStatus;
}

static void connectToWifi(void)
{
    LOG_INFO("Connecting to %s...", WIFI_SSID);
    WiFi.begin(WIFI_SSID, WIFI_PASS);

    int connectionTimeoutCounter = 0;
    while (WiFi.status() != WL_CONNECTED)
    {
        sleepSeconds(1);
        LOG_INFO("Waiting for connection...");
        connectionTimeoutCounter++;

        if (connectionTimeoutCounter > WIFI_CONNECTING_TIMEOUT_SECONDS)
        {
            LOG_ERROR("Connection timed out! Check your password in app_config.yaml.");
            wifiStatus = WIFI_STATUS_CONNECTION_FAILED;
            break;
        }
    }
}

static void waitForProperIpAddress(void)
{
    int securityTimeout = 0;
    int waitTimeSeconds = 0;

    while (WiFi.localIP()[0] == 0 && waitTimeSeconds < WIFI_IP_ADDRESS_GET_TIMEOUT_SECONDS)
    {
        while (WiFi.localIP()[0] == 0)
        {
            sleepSeconds(1);
            waitTimeSeconds++;
            securityTimeout++;

            // Safety exit: If it drops data for 15 seconds, force a firmware re-query
            if (securityTimeout > WIFI_IP_STATUS_CHECK_DURATION_SECOND)
            {
                LOG_INFO("Status check...");
                WiFi.status(); // Explicitly calls the firmware layer to poke the stack
                securityTimeout = 0;
            }
        }
    }

    IPAddress ip = WiFi.localIP();
    if (ip[0] != 0)
    {
        LOG_INFO("Connected to %s with IP %d.%d.%d.%d", WIFI_SSID, ip[0], ip[1], ip[2], ip[3]);
        wifiStatus = WIFI_STATUS_CONNECTED;
    }
    else
    {
        LOG_ERROR("Unable to acquire proper IP address!");
        wifiStatus = WIFI_STATUS_CONNECTION_FAILED;
    }
}

static int readResponse(WiFiClient *client)
{
    // Capture response verification
    unsigned long timeout = millis();
    int index = 0;
    while (client->connected() && millis() - timeout < 5000)
    {
        while (client->available())
        {
            char c = client->read();
            timeout = millis();
            if (index < RESPONSE_MAX_LEN)
            {
                response[index++] = c;
            }
        }
    }
    if (index < RESPONSE_MAX_LEN)
    {
        response[index++] = '\0';
    }
    return 1;
}