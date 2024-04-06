# py-2e-ups
Linux driver for 2E DD series ups, using pyusb

## Supportted UPS
- 2E DD2000
- 2E DD1500
- 2E DD850
- 2E DD650

## Installation
need to install pyusb libs
```sh
# because its need to run under root, so here install also need to install to root
sudo pip install -r requirements.txt
```

## Run
You need to have root privillage to access the USB port
```sh
# get ups running status
sudo ./ups_connect.py

# output sample
input.voltage: 237.0
input.voltage_fault: 0.0
input.freqency: 50.0
output.voltage: 238.0
battery.voltage: 27.1
battery.level: 100.0
ups.load: 13.0
ups.temperature: 29.0
ups.utility_fail: False
ups.battery_low: False
ups.bypass: True
ups.failed: False
ups.type: True
ups.test_in_progress: False
ups.shutdown_active: False
ups.beeper_status: False

# trigger ups battery test
sudo ./ups_test.py
```