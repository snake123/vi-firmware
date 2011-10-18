#!/usr/bin/env python

import sys
import string
import serial
import datetime
from operator import itemgetter

MAX_BYTES = 10 * 1000 * 10 * 1

STARTING_MESSAGE_SIZE = 20
ENDING_MESSAGE_SIZE = 100
MESSAGE_SIZE_STEP = 20

BAUD = 1152000

class SerialDevice(object):
    def __init__(self, device="/dev/ttyUSB1", baud=115200):
        self.device = serial.Serial(device, baud, timeout=10)
        self.device.flushInput()
        self.message_size = -1

    def initialize_message_size(self, message_size):
        self.message_size = message_size
        self.device.write(bytearray([self.message_size / MESSAGE_SIZE_STEP]))
        self.device.flushOutput()
        print "Message size switched to %d bytes" % self.message_size
        self.bytes_received = 0

    def read(self):
        data = self.device.read(self.message_size)

        self.bytes_received += self.message_size
        if self.bytes_received % (1000 * 10) == 0:
            print "Received %d kilobytes so far..." % (
                    self.bytes_received / 1000),
            sys.stdout.flush()
            print "\r",
        return data

    def total_time(self, elapsed_time):
        return "Reading %s KB in %s byte chunks took %s" % (
                self.bytes_received / 1000, self.message_size, elapsed_time)

    def throughput(self, elapsed_time):
        return (self.bytes_received / 1000 /
                max(1, elapsed_time.seconds + elapsed_time.microseconds /
                    1000000.0))

def run_benchmark(serial_device, message_size, total_bytes=MAX_BYTES):
    serial_device.initialize_message_size(message_size)

    data = serial_device.read()
    starting_time = datetime.datetime.now()

    while data is not None and serial_device.bytes_received < MAX_BYTES:
        data = serial_device.read()
        for character in string.ascii_lowercase[:message_size]:
            if character not in data:
                print "Corruption detection on line: %s" % data

    print
    print "Finished receiving."

    elapsed_time = datetime.datetime.now() - starting_time
    throughput = serial_device.throughput(elapsed_time)
    print serial_device.total_time(elapsed_time)
    print "The effective throughput for %d byte messages is %d KB/s" % (
                message_size, throughput)
    return throughput


def main():
    device = SerialDevice(baud=BAUD)
    results = {}
    for message_size in range(STARTING_MESSAGE_SIZE, ENDING_MESSAGE_SIZE + 1,
            MESSAGE_SIZE_STEP):
        results[message_size] = run_benchmark(device, message_size)

    print
    results = [(key, "%d byte messages -> %d KB/s" % (key, value))
            for key, value in results.iteritems()]

    for result in sorted(results, key=itemgetter(0)):
        print result[1]

if __name__ == '__main__':
    main();