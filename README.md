# SensorReader

A Python tool for reading JINOU/OEM BLE temperature/humidity sensors

## Usage

```
usage: readsensor.py [-h] [--delay DELAY] [--logfile LOGFILE]
                     [--loglevel {CRITICAL,WARNING,ERROR,INFO,DEBUG}]
                     devices [devices ...]

BTLE JINOU Sensor Reader

positional arguments:
  devices               List of devices to read from by MAC Address

optional arguments:
  -h, --help            show this help message and exit
  --delay DELAY         Delay in seconds between reads, default 60
  --logfile LOGFILE     Name of logfile for output log, "stdout" for stdout
                        (default), or "syslog" for syslog
  --loglevel {CRITICAL,WARNING,ERROR,INFO,DEBUG}
                        Log level to log, default is INFO
```

## Requirements

This script requires Bluez version 5.X to be installed (See http://www.bluez.org/ for the latest version).

pexpect is required and can be installed by running `pip3 install pexpect`.

## Sample Output

```
Oct 17 01:07:53 hostname python3[22232]: [ReadSensor] INFO - Device=EE:DE:C8:AB:CD:EF Temperature=20.7 Humidity=52.3
Oct 17 01:12:53 hostname python3[22232]: [ReadSensor] INFO - Device=EE:DE:C8:AB:CD:EF Temperature=20.7 Humidity=52.2
Oct 17 01:17:53 hostname python3[22232]: [ReadSensor] INFO - Device=EE:DE:C8:AB:CD:EF Temperature=20.7 Humidity=52.4
```
