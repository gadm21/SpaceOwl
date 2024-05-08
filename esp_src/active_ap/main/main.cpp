#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "spi_flash_mmap.h"
#include "freertos/event_groups.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_http_server.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "esp_mac.h"
#include "Arduino.h"
#include "esp32-hal-cpu.h" 

#include "lwip/err.h"
#include "lwip/sys.h"

#include "../../_components/nvs_component.h"
#include "../../_components/sd_component.h"
#include "../../_components/csi_component.h"
#include "../../_components/time_component.h"
#include "../../_components/input_component.h"
#include "../../_components/sockets_component.h"

/*
 * The examples use WiFi configuration that you can set via 'idf.py menuconfig'.
 *
 * If you'd rather not, just change the below entries to strings with
 * the config you want - ie #define ESP_WIFI_SSID "mywifissid"
 */
// #define ESP_WIFI_SSID      "BELL623"
// #define ESP_WIFI_PASS      "17DF2DA435F2"
#define ESP_WIFI_SSID      "mywifi"
#define ESP_WIFI_PASS      "mywifipass"
#define MAX_STA_CONN       5

#ifdef CONFIG_WIFI_CHANNEL
#define WIFI_CHANNEL CONFIG_WIFI_CHANNEL
#else
#define WIFI_CHANNEL 11
#endif

#ifdef CONFIG_SHOULD_COLLECT_CSI
#define SHOULD_COLLECT_CSI 1
#else
#define SHOULD_COLLECT_CSI 0
#endif

#ifdef CONFIG_SHOULD_COLLECT_ONLY_LLTF
#define SHOULD_COLLECT_ONLY_LLTF 1
#else
#define SHOULD_COLLECT_ONLY_LLTF 0
#endif

#ifdef CONFIG_SEND_CSI_TO_SERIAL
#define SEND_CSI_TO_SERIAL 1
#else
#define SEND_CSI_TO_SERIAL 0
#endif

#ifdef CONFIG_SEND_CSI_TO_SD
#define SEND_CSI_TO_SD 1
#else
#define SEND_CSI_TO_SD 0
#endif

/* FreeRTOS event group to signal when we are connected*/
static EventGroupHandle_t s_wifi_event_group;

static const char *TAG = "Active CSI collection (AP)";

static void wifi_event_handler(void* arg, esp_event_base_t event_base, int32_t event_id, void* event_data) {
    if (event_id == WIFI_EVENT_AP_STACONNECTED) {
        wifi_event_ap_staconnected_t* event = (wifi_event_ap_staconnected_t*) event_data;
        ESP_LOGI(TAG, "station %s join, AID=%d",
                 "hello", event->aid);
    } else if (event_id == WIFI_EVENT_AP_STADISCONNECTED) {
        wifi_event_ap_stadisconnected_t* event = (wifi_event_ap_stadisconnected_t*) event_data;
        // ESP_LOGI(TAG, "station %s leave, AID=%d",
        //          MAC2STR(event->mac), event->aid);
    }
}


void softap_init() {
/**
 * @brief Initializes the Wi-Fi access point (AP) configuration and starts the AP.
 * 
 * This function creates a new event group for managing Wi-Fi events, initializes the network interface,
 * creates the default event loop to manage system events, sets up the default network interface for Wi-Fi AP,
 * initializes the Wi-Fi configuration with default parameters, registers the event handler for Wi-Fi events,
 * and sets up the Wi-Fi access point configuration. It then sets the SSID and password for the AP,
 * sets the Wi-Fi mode to Access Point, and starts the Wi-Fi access point.
 * 
 * @note This function should be called before using the Wi-Fi access point.
 */

    // Create a new event group for managing Wi-Fi events
    s_wifi_event_group = xEventGroupCreate();

    // Initialize the network interface
    ESP_ERROR_CHECK(esp_netif_init());

    // Create the default event loop to manage system events
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    // Set up the default network interface for Wi-Fi access point (AP)
    esp_netif_create_default_wifi_ap();

    // Initialize the Wi-Fi configuration with default parameters
    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));


    // Register the event handler for Wi-Fi events to listen to all event types
    ESP_ERROR_CHECK(esp_event_handler_instance_register(WIFI_EVENT,
                                                        ESP_EVENT_ANY_ID,
                                                        &wifi_event_handler,
                                                        NULL,
                                                        NULL));

    // Create a Wi-Fi access point configuration structure
    wifi_ap_config_t wifi_ap_config = {};
    // Set the Wi-Fi channel for the access point
    wifi_ap_config.channel = WIFI_CHANNEL;
    // Set the authentication mode to WPA/WPA2 with Pre-Shared Key
    wifi_ap_config.authmode = WIFI_AUTH_WPA_WPA2_PSK;
    // Set the maximum number of connections allowed to the access point
    wifi_ap_config.max_connection = MAX_STA_CONN;

    // Create a Wi-Fi configuration structure with the access point configuration
    wifi_config_t wifi_config = {
            .ap = wifi_ap_config,
    };

    // Set the SSID and password for the Wi-Fi access point
    strlcpy((char *) wifi_config.ap.ssid, ESP_WIFI_SSID, sizeof(ESP_WIFI_SSID));
    strlcpy((char *) wifi_config.ap.password, ESP_WIFI_PASS, sizeof(ESP_WIFI_PASS));
    // If no password is provided, set the authentication mode to open (no security)
    if (strlen(ESP_WIFI_PASS) == 0) {
        wifi_config.ap.authmode = WIFI_AUTH_OPEN;
    }

    // Set the Wi-Fi mode to Access Point
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_AP));
    // Set the Wi-Fi configuration to the access point
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_AP, &wifi_config));
    // Start the Wi-Fi access point
    ESP_ERROR_CHECK(esp_wifi_start());

    // Disable Wi-Fi power-saving mode
    esp_wifi_set_ps(WIFI_PS_NONE);

    ESP_LOGI(TAG, "softap_init finished. SSID:%s password:%s", ESP_WIFI_SSID, ESP_WIFI_PASS);
}

void config_print() {
    printf("\n\n\n\n\n\n\n\n");
    printf("-----------------------\n");
    printf("ESP32 CSI Tool Settings\n");
    printf("-----------------------\n");
    printf("PROJECT_NAME: %s\n", "ACTIVE_AP");
    printf("CONFIG_ESPTOOLPY_MONITOR_BAUD: %d\n", CONFIG_ESPTOOLPY_MONITOR_BAUD);
    printf("CONFIG_ESP_CONSOLE_UART_BAUDRATE: %d\n", CONFIG_ESP_CONSOLE_UART_BAUDRATE);
    printf("IDF_VER: %s\n", IDF_VER);
    printf("-----------------------\n");
    printf("WIFI_CHANNEL: %d\n", WIFI_CHANNEL);
    printf("ESP_WIFI_SSID: %s\n", ESP_WIFI_SSID);
    printf("ESP_WIFI_PASSWORD: %s\n", ESP_WIFI_PASS);
    printf("SHOULD_COLLECT_CSI: %d\n", SHOULD_COLLECT_CSI);
    printf("SHOULD_COLLECT_ONLY_LLTF: %d\n", SHOULD_COLLECT_ONLY_LLTF);
    printf("SEND_CSI_TO_SERIAL: %d\n", SEND_CSI_TO_SERIAL);
    printf("SEND_CSI_TO_SD: %d\n", SEND_CSI_TO_SD);
    printf("-----------------------\n");
    printf("\n\n\n\n\n\n\n\n");
}




extern "C" void app_main() {
    config_print();
    nvs_init();
    sd_init();

    // initializes and starts wifi in AP mode
    softap_init(); 
    #if !(SHOULD_COLLECT_CSI)
        printf("CSI will not be collected. Check `idf.py menuconfig  # > ESP32 CSI Tool Config` to enable CSI");
    #endif

    // print the cpu frequency, frequency of the XTAL, the APB clock frequency, the free heap memory, and the number of cores. 
    printf("CPU Freq: %lu MHz\n", getCpuFrequencyMhz());
    // printf("-----------------------\n");

    // // set the cpu frequency to 240 MHz
    setCpuFrequencyMhz(240);

    printf("CPU Freq: %lu MHz\n", getCpuFrequencyMhz());
    // printf("-----------------------\n");


    // initializes CSI (Channel State Information) collection 
    csi_init((char *) "AP");
}
