#!/usr/bin/env python3
import sys, os
from ups_connect import ups_test, get_device

if os.geteuid() != 0:
  print("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")
  sys.exit()

if __name__ == '__main__':
  # check if current user is not root then print error message and exit
  dev = get_device()
  ups_test(dev)