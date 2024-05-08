#ifndef ESP32_CSI_CSI_COMPONENT_H
#define ESP32_CSI_CSI_COMPONENT_H

#include "time_component.h"
#include "math.h"
#include <sstream>
#include <iostream>

char *project_type;

#define CSI_RAW 1
#define CSI_AMPLITUDE 0
#define CSI_PHASE 0

#define CSI_TYPE CSI_RAW

SemaphoreHandle_t mutex = xSemaphoreCreateMutex();

void _wifi_csi_cb(void *ctx, wifi_csi_info_t *data) {
    xSemaphoreTake(mutex, portMAX_DELAY);
    
    // print the received data 
    
    
    
    std::stringstream ss;

    wifi_csi_info_t d = data[0];
    
    char mac[20] = {0};
    sprintf(mac, "%02X:%02X:%02X:%02X:%02X:%02X", d.mac[0], d.mac[1], d.mac[2], d.mac[3], d.mac[4], d.mac[5]);

    ss << "CSI_DATA,"
       << project_type << ","
       << mac << ","
       // https://github.com/espressif/esp-idf/blob/9d0ca60398481a44861542638cfdc1949bb6f312/components/esp_wifi/include/esp_wifi_types.h#L314
       << d.rx_ctrl.rssi << ","
       << d.rx_ctrl.rate << ","
       << d.rx_ctrl.sig_mode << ","
       << d.rx_ctrl.mcs << ","
       << d.rx_ctrl.cwb << ","
       << d.rx_ctrl.smoothing << ","
       << d.rx_ctrl.not_sounding << ","
       << d.rx_ctrl.aggregation << ","
       << d.rx_ctrl.stbc << ","
       << d.rx_ctrl.fec_coding << ","
       << d.rx_ctrl.sgi << ","
       << d.rx_ctrl.noise_floor << ","
       << d.rx_ctrl.ampdu_cnt << ","
       << d.rx_ctrl.channel << ","
       << d.rx_ctrl.secondary_channel << ","
       << d.rx_ctrl.timestamp << ","
       << d.rx_ctrl.ant << ","
       << d.rx_ctrl.sig_len << ","
       << d.rx_ctrl.rx_state << ","
       << real_time_set << ","
       << get_steady_clock_timestamp() << ","
       << data->len << ",[";

#if CONFIG_SHOULD_COLLECT_ONLY_LLTF
    int data_len = 128;
#else
    int data_len = data->len;
#endif

int8_t *my_ptr;
#if CSI_RAW
    my_ptr = data->buf;
    for (int i = 0; i < data_len; i++) {
        ss << (int) my_ptr[i] << " ";
    }
#endif
#if CSI_AMPLITUDE
    my_ptr = data->buf;
    for (int i = 0; i < data_len / 2; i++) {
        ss << (int) sqrt(pow(my_ptr[i * 2], 2) + pow(my_ptr[(i * 2) + 1], 2)) << " ";
    }
#endif
#if CSI_PHASE
    my_ptr = data->buf;
    for (int i = 0; i < data_len / 2; i++) {
        ss << (int) atan2(my_ptr[i*2], my_ptr[(i*2)+1]) << " ";
    }
#endif
    ss << "]\n";

    printf(ss.str().c_str());
    fflush(stdout);
    vTaskDelay(0);
    xSemaphoreGive(mutex);
}

void _print_csi_csv_header() {
    char *header_str = (char *) "type,role,mac,rssi,rate,sig_mode,mcs,bandwidth,smoothing,not_sounding,aggregation,stbc,fec_coding,sgi,noise_floor,ampdu_cnt,channel,secondary_channel,local_timestamp,ant,sig_len,rx_state,real_time_set,real_timestamp,len,CSI_DATA\n";
    outprintf(header_str);
}


// Initializes the CSI (Channel State Information) collection with optional configuration based on compile-time flags.
void csi_init(char *type) {
    project_type = type;

    // The following code block will only be included if CONFIG_SHOULD_COLLECT_CSI is defined.
    #ifdef CONFIG_SHOULD_COLLECT_CSI

        // Enable CSI (Channel State Information) collection in ESP Wi-Fi.
        // This is the main step to start gathering CSI data.
        ESP_ERROR_CHECK(esp_wifi_set_csi(1)); // `1` to enable, `0` to disable.

        // @See: https://github.com/espressif/esp-idf/blob/master/components/esp_wifi/include/esp_wifi_types.h#L401
        wifi_csi_config_t configuration_csi; // Structure to hold the CSI configuration.
        configuration_csi.lltf_en = 1; // Enable Long Training Field (LTF) information.
        configuration_csi.htltf_en = 1; // Enable High Throughput Long Training Field (HT-LTF).
        configuration_csi.stbc_htltf2_en = 1; // Enable Space-Time Block Coding HT-LTF2 (second part).
        configuration_csi.ltf_merge_en = 1; // Merge different LTFs into a single CSI frame.
        // Channel filter setting; if disabled (0), all data is captured.
        configuration_csi.channel_filter_en = 0; 
        // Manual scaling for CSI values; set to `0` for default behavior.
        configuration_csi.manu_scale = 0;

        // Apply the CSI configuration to the ESP Wi-Fi system.
        ESP_ERROR_CHECK(esp_wifi_set_csi_config(&configuration_csi));
        // Register a callback function to handle received CSI data.
        // This function will be called whenever CSI data is collected.
        ESP_ERROR_CHECK(esp_wifi_set_csi_rx_cb(&_wifi_csi_cb, NULL));

        _print_csi_csv_header();
    #endif
}

#endif //ESP32_CSI_CSI_COMPONENT_H
