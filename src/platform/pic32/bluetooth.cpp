#include "bluetooth.h"
#include "gpio.h"
#include "util/log.h"

using openxc::gpio::GpioValue;
using openxc::gpio::getGpioValue;

#if defined(FLEETCARMA)

    #define BLUETOOTH_SUPPORT

    #define BLUETOOTH_ENABLE_PORT                0
    #define BLUETOOTH_ENABLE_PIN_POLARITY        1    // drive high == power on
    #define BLUETOOTH_ENABLE_PIN                32    // PORTE BIT5 (RE5)

    #define BLUETOOTH_STATUS_PORT                0
    #define BLUETOOTH_STATUS_PIN_POLARITY        1    // high == connected
    #define BLUETOOTH_STATUS_PIN                58     // PORTB BIT4 (RB4)

#endif

bool bluetoothConnected() {
    GpioValue value;
    bool status;

    #if defined(BLUETOOTH_SUPPORT)
    value = getGpioValue(BLUETOOTH_STATUS_PORT, BLUETOOTH_STATUS_PIN);
    switch(value) {
        case GPIO_VALUE_HIGH:
            status = BLUETOOTH_STATUS_PIN_POLARITY ? true : false;
            break;
        case GPIO_VALUE_LOW:
            status = BLUETOOTH_STATUS_PIN_POLARITY ? false : true;
            break;
         default:
            status = false;
            break;
    }
    #else
    status = false;
    #endif

    return status;
}

void openxc::bluetooth::setBluetoothStatus(bool enabled) {
    GpioValue value;

    #if defined(BLUETOOTH_SUPPORT)
    value = BLUETOOTH_ENABLE_PIN_POLARITY ? enabled : !enabled;

    debug("Turning Bluetooth %s", enabled ? "on" : "off");
    setGpioValue(BLUETOOTH_ENABLE_PORT, BLUETOOTH_ENABLE_PIN, value);
    #endif
}

void openxc::bluetooth::initializeBluetooth() {
    #if defined(BLUETOOTH_SUPPORT)
    debug("Initializing Bluetooth...");

    // initialize bluetooth enable and status pins
    setGpioDirection(BLUETOOTH_ENABLE_PORT, BLUETOOTH_ENABLE_PIN, GPIO_DIRECTION_OUTPUT);
    setGpioDirection(BLUETOOTH_STATUS_PORT, BLUETOOTH_STATUS_PIN, GPIO_DIRECTION_INPUT);

    // enable bluetooth board
    setBluetoothStatus(true);

    debug("Done.");
    #endif
}

void openxc::bluetooth::deinitializeBluetooth() {
    #if defined(BLUETOOTH_SUPPORT)
    // disable bluetooth board
    setBluetoothStatus(false);
    #endif
}