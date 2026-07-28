# Hardware

## Supported Device

VibeStick v0.1.2 targets M5Stack StickS3.

The project does not currently claim support for other devices because the UI layout, front button behavior, microphone path, speaker path, PMIC battery reads, and screen size are all written around StickS3.

## Hardware Used

- Screen: LVGL UI on the StickS3 display.
- Blue front button: push-to-talk recording.
- Side button: provider switching.
- Microphone: StickS3 microphone captured as 16 kHz / 16-bit / mono PCM.
- Speaker: ES8311 / I2S playback for generated agent status tones.
- Wi-Fi: HTTP communication with the Mac bridge on a 2.4 GHz Wi-Fi network. StickS3 / ESP32-S3 does not support 5 GHz Wi-Fi.
- USB-C: flashing and serial monitor.
- Battery / USB power: local M5PM1 PMIC reads for the battery UI, USB detection, power hold, and speaker amplifier enable.

The firmware uses one StickS3-specific PMIC path in `firmware/sticks3/src/vibe_board.c`. Power hold, LDO/speaker setup, battery level, charging, and USB power detection stay in that driver so display behavior does not fight another power stack.

## Firmware Configuration

Install ESP-IDF v5.5.x once before building or flashing firmware. Follow Espressif's [ESP-IDF v5.5.1 ESP32-S3 guide](https://docs.espressif.com/projects/esp-idf/en/v5.5.1/esp32s3/get-started/index.html), or use:

```sh
mkdir -p ~/esp && cd ~/esp
git clone -b v5.5.1 --recursive https://github.com/espressif/esp-idf.git
cd esp-idf && ./install.sh esp32s3
```

Create a local secrets header:

```sh
cp firmware/sticks3/include/vibe_stick_secrets.example.h firmware/sticks3/include/vibe_stick_secrets.h
```

Edit:

```c
#define VIBE_STICK_WIFI_SSID "your-wifi"
#define VIBE_STICK_WIFI_PASSWORD "your-password"
#define VIBE_STICK_BRIDGE_HOST "192.168.1.10"
#define VIBE_STICK_BRIDGE_PORT 8765
#define VIBE_STICK_BRIDGE_TOKEN "paste-generated-token-here"
```

Do not commit `vibe_stick_secrets.h`.

The Wi-Fi network must be 2.4 GHz. If the SSID is a combined 2.4/5 GHz network and the StickS3 cannot connect, create or select a dedicated 2.4 GHz SSID.

## Flashing

Load ESP-IDF into every new terminal before running `idf.py`:

```sh
. $HOME/esp/esp-idf/export.sh
```

Adjust the path if ESP-IDF is installed elsewhere. If you see `command not found: idf.py`, this shell has not loaded ESP-IDF yet.

From the firmware directory:

```sh
cd firmware/sticks3
idf.py build flash monitor
```

If automatic flashing fails, put the StickS3 into download mode and retry:

1. Plug the StickS3 into the Mac with a USB-C data cable.
2. Long-press the side power button until the blue LED double-blinks and the screen turns off.
3. Run `ls /dev/cu.*` to find the serial port.
4. Retry `idf.py -p <port> build flash`.
5. After flashing, short-press the power button to wake the screen. The blue LED should turn off and the VibeStick home screen should appear.

## Runtime Network

The StickS3 talks to the Mac bridge by HTTP. The Mac bridge should listen on `0.0.0.0:8765` when the device is on the same Wi-Fi network.
