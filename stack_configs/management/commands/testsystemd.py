#!/usr/bin/python
import logging


LOGGER = logging.getLogger(__name__)
from time import sleep
 
try:
    while True:
        print ("Hello World")
        sleep(5)
except KeyboardInterrupt:
    LOGGER.info("Stopping...")