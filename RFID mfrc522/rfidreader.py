#!/usr/bin/env python

import time as t
import RPi.GPIO as GPIO
import sys
sys.path.append('/home/pi/MFRC522-python')
from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()

print("Please scan your hostel card")

try:
    #while True:
    id, text = reader.read()
    print(id)
    print(text)
    #t.sleep(3)

finally:
    GPIO.cleanup()
