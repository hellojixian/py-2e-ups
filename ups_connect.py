#!/usr/bin/env python3
import sys, os, platform
import usb.core
import usb.util
import usb.control
import usb.backend.libusb1
import sys, os, time

VENDOR_ID = 0x0001
PRODUCT_ID = 0x0000

if platform.system() == 'Windows':
  import sys
  sys.exit("Windows is not supported")

if os.geteuid() != 0:
  print("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")
  sys.exit()

def get_device():
  backend = usb.backend.libusb1.get_backend()
  device = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID, backend=backend)

  if device is None:
    sys.exit('UPS Device not found')

  # Detach the device from the kernel driver, if necessary
  if device.is_kernel_driver_active(0):
      try:
          device.detach_kernel_driver(0)
      except usb.core.USBError as e:
          raise ValueError("Could not detach kernel driver: %s" % str(e))

  # Set the active configuration. With no arguments, the first configuration will be the active one
  device.set_configuration()
  return device

def get_string(ret):
  # Combine the hex values into a single string
  hex_list = [format(x, '02x') for x in ret]
  hex_str = ''.join(hex_list)
  bytes_obj = bytes.fromhex(hex_str)
  string = bytes_obj.decode('utf-16le').strip()[1:]
  return string

def _run_cmd(device, cmd):
  bmRequestType = cmd[0]
  bRequest = cmd[1]
  wValue = cmd[2]
  wIndex = cmd[3]
  data_or_wLength = cmd[4]
  ret = device.ctrl_transfer(
                  bmRequestType = bmRequestType,
                  bRequest = bRequest,
                  wValue = wValue,
                  wIndex = wIndex,
                  data_or_wLength = data_or_wLength)
  time.sleep(0.5)
  return get_string(ret)

def init_device(device):
  cmd_lists = [
    [0x80, 0x06, 0x0300, 0x0000, 0x0066],
    [0x80, 0x06, 0x0301, 0x0409, 0x0066],
  ]
  for cmd in cmd_lists:
    r = _run_cmd(device, cmd)
  return

def get_status(device):
  res = _run_cmd(device, [0x80, 0x06, 0x0303, 0x0409, 0x0066])
  res = res[1:].split(' ')

  while float(res[2]) == 0.0:
    res = _run_cmd(device, [0x80, 0x06, 0x0303, 0x0409, 0x0066])
    res = res[1:].split(' ')
    time.sleep(1)

  battery_level = get_battery_level(device)
  return {
    "input.voltage": float(res[0]),
    "input.voltage_fault": float(res[1]),
    "input.freqency": float(res[4]),
    "output.voltage": float(res[2]),
    "battery.voltage": float(res[5]),
    "battery.level": float(battery_level),
    "ups.load": float(res[3]),
    "ups.temperature": res[6],
    "ups.utility_fail": int(res[7][0]),  # 外部供电是否中断是
    "ups.battery_low": int(res[7][1]),   # 电池是否低电压 快没电了
    "ups.bypass": 0 if int(res[7][2]) == 1 else 1,        # 是否处于旁路模式
    "ups.failed": int(res[7][3]),
    "ups.type": int(res[7][4]),          # 好像永远是1
    "ups.test_in_progress": int(res[7][5]), # 是否正在测试中
    "ups.shutdown_active": int(res[7][6]),
    "ups.beeper_status": int(res[7][7]), # 是否正在蜂鸣报警
  }

def get_battery_level(device):
  res = _run_cmd(device,[0x80, 0x06, 0x03f3, 0x0409, 0x0066])
  res = float(res.replace('BL', ''))
  return res

def ups_test(device):
  res = _run_cmd(device,[0x80, 0x06, 0x0304, 0x0409, 0x0066])
  print(res)
  return res

if __name__ == '__main__':
  import time
  dev = get_device()
  # init_device(dev)
  status = get_status(dev)
  for k, v in status.items():
      print(f'{k}: {v}')

  # res = ups_test(dev)
  # print(f'ups test res: {res}')
