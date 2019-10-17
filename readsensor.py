import pexpect
import threading
import logging
from logging.handlers import SysLogHandler
import struct
import time
import sys
import argparse

class SensorWorker(threading.Thread):
    '''
    Thread that reads the sensor
    '''

    def __init__(self, device, delay, logger):
        super().__init__()
        self.killed = False
        self.device = device
        self.delay = delay
        self.logger = logger
        # Counter for number of failed attampts in a row
        self.failed = 0

    def run(self):
        self.logger.info('Thread for device {} and delay {} started'.format(self.device, self.delay))
        try:
            gatt = pexpect.spawn("gatttool -b " + self.device+ " -I")
            gatt.sendline("connect")
            gatt.expect("Connection successful")
        except Exception as e:
            self.logger.critical('Could not connect to device {}'.format(self.device))
            self.killed = True
        while not self.killed:
            try:
                gatt.sendline("char-read-hnd 23")
                gatt.expect("Characteristic value/descriptor: ")
                gatt.expect("\r\n")
                data = (gatt.before).decode('UTF-8').split(' ')
                # Convert data to useful form
                temp = int(data[1],16) + float(int(data[2],16))/10
                humidity = int(data[4],16) + float(int(data[5],16))/10
                if data[0] == '01':
                    temp = -temp
                self.logger.info('Device={} Temperature={} Humidity={}'.format(self.device, temp, humidity))
                self.failed = 0
            except pexpect.exceptions.TIMEOUT:
                self.logger.info('Could not read from device {}'.format(self.device))
                self.failed += 1
                if self.failed > 5:
                    self.logger.error('Too many read failures in a row for device {}, exiting'.format(self.device))
                    self.killed = True
            except Exception as e:
                self.logger.critical('Exception for device {}: {}'.format(self.device, e))
                self.killed = True
            finally:
                time.sleep(self.delay)
        self.logger.info('Stop message received, stopping thread for device {}'.format(self.device))



def main():

    readers = []
    
    # Add parser
    parser = argparse.ArgumentParser(description='BTLE JINOU Sensor Reader')
    parser.add_argument('devices', nargs='+', help='List of devices to read from by MAC Address')
    parser.add_argument('--delay', type=int, help='Delay in seconds between reads, default 60', default=60)
    parser.add_argument('--logfile', help='Name of logfile for output log, "stdout" for stdout (default), or "syslog" for syslog', default='stdout')
    parser.add_argument('--loglevel', choices=['CRITICAL','WARNING','ERROR','INFO','DEBUG'], help='Log level to log, default is INFO', default='INFO')
    args = parser.parse_args()

    #Sanity check for args
    if len(args.devices) == 0:
        print('Must include at least one device to monitor')
        sys.exit(1)

    logger = logging.getLogger('sensorreader')
    if args.logfile == 'stdout':
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s [ReadSensor] %(levelname)s - %(message)s')
    elif args.logfile == 'syslog':
        handler = SysLogHandler(address='/dev/log')
        formatter = logging.Formatter('[ReadSensor] %(levelname)s - %(message)s')
    else:
        handler = logging.FileHandler(args.logfile)
        formatter = logging.Formatter('%(asctime)s [ReadSensor] %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.setLevel(args.loglevel)

    # Create threads for reading devices
    for device in args.devices:
        logger.info('Starting up thread for device {}'.format(device))
        reader = SensorWorker(device, args.delay, logger)
        readers.append(reader)
        reader.setDaemon(True)
        reader.start()

    while True:
        try:
            thread_running = False
            for reader in readers:
                reader.join(1)
                if not reader.killed:
                    thread_running = True
            if not thread_running:
                logger.info('All threads stopped, exiting...')
                sys.exit(0)
        except KeyboardInterrupt:
            logger.info('Ctrl-C received, stopping threads')
            for reader in readers:
                reader.killed = True
            sys.exit(0)

if __name__ == '__main__':
    main()
