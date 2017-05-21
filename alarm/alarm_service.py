#!/usr/bin/env python

import logging
import logging.handlers
import argparse
import sys
import RPi.GPIO as io  # import the GPIO library we just installed but call it "io"
import time  # this is only being used as part of the example

# Defaults
LOG_FILENAME = "/tmp/alarm.log"
LOG_LEVEL = logging.INFO  # Could be e.g. "DEBUG" or "WARNING"
LOG_ROTATION = 5  # Keep 5 days worth of logs

# set GPIO mode to BCM
# this takes GPIO number instead of pin number
io.setmode(io.BCM)
 
# enter the number of whatever GPIO pin you're using
door_pin = 23

# Define and parse command line arguments
parser = argparse.ArgumentParser(description="Alarm system service")
parser.add_argument("-l", "--log", help="file to write log to (default '" + LOG_FILENAME + "')")

# If the log file is specified on the command line then override the default
args = parser.parse_args()
if args.log:
        LOG_FILENAME = args.log

# Configure logging to log to a file, making a new file at midnight and keeping the last 5 day's data
# Give the logger a unique name (good practice)
logger = logging.getLogger(__name__)
# Set the log level to LOG_LEVEL
logger.setLevel(LOG_LEVEL)
# Make a handler that writes to a file, making a new file at midnight and keeping 3 backups
handler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="midnight", backupCount=LOG_ROTATION)
# Format each log message like this
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
# Attach the formatter to the handler
handler.setFormatter(formatter)
# Attach the handler to the logger
logger.addHandler(handler)


# Make a class we can use to capture stdout and sterr in the log
class MyLogger(object):
        def __init__(self, logger, level):
                """Needs a logger and a logger level."""
                self.logger = logger
                self.level = level

        def write(self, message):
                # Only log if there is a message (not just a new line)
                if message.rstrip() != "":
                        self.logger.log(self.level, message.rstrip())

# Replace stdout with logging to file at INFO level
sys.stdout = MyLogger(logger, logging.INFO)
# Replace stderr with logging to file at ERROR level
sys.stderr = MyLogger(logger, logging.ERROR)

# use the built-in pull-up resistor
io.setup(door_pin, io.IN, pull_up_down=io.PUD_UP)  # activate input with PullUp
 
# initialize door
door = 0

# Loop forever, running the service:
while True:
    # if the switch is open
    if io.input(door_pin):
        logger.info("Door is open")
        door = 0  # set door to its initial value
        time.sleep(1)  # wait 1 second before the next action
    
    # if the switch is closed and door does not equal 1
    else:
        logger.info("Door is closed")
        door = 1  # set door so that this loop won't act again until the switch has been opened
        time.sleep(1)  # wait 1 second before the next action

