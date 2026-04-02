# Interface Map

## Core Interfaces

- CM4 `USB2` -> modem USB
- CM4 `PCIe` -> optional 5G modem path for later spin
- CM4 `I2S` -> audio codec / DAC
- CM4 `I2C1` -> touch controller, ambient light sensor, accelerometer, fuel gauge
- CM4 `SPI0` -> OLED / e-paper display
- CM4 `UART0` -> modem AT channel / debug
- CM4 `CSI0` -> camera module
- CM4 `GPIO` -> wake, hook, mute, fingerprint interrupt, PMIC status

## Power Rails

- `VBUS_IN` 5V from USB-C
- `VSOLAR_IN` 5-6V solar trickle input
- `VBAT_SYS` 3.0-4.2V battery rail
- `VSYS_5V` boosted system rail
- `VDD_3V3`
- `VDD_1V8_SENSORS`

## Audio Path

- Digital mic -> I2S/PCM capture
- AI TTS / call audio -> codec / amp -> speaker
- Optional 3.5 mm or USB-C digital headset support

## Imaging Path

- CSI camera -> local capture service
- Captured media -> local upload queue
- Online: cloud vision / OCR analysis
- Offline: metadata and thumbnail cache, deferred cloud analysis after sync
