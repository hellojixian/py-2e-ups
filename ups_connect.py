#!/usr/bin/env python3
import sys, os
import usb.core
import usb.util
import usb.control

VENDOR_ID = 0x0001
PRODUCT_ID = 0x0000

if os.geteuid() != 0:
  print("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")
  sys.exit()

def get_device():
  device = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)

  if device is None:
      raise ValueError('Device not found')

  # Detach the device from the kernel driver, if necessary
  if device.is_kernel_driver_active(0):
      try:
          device.detach_kernel_driver(0)
      except usb.core.USBError as e:
          raise ValueError("Could not detach kernel driver: %s" % str(e))

  # Set the active configuration. With no arguments, the first configuration will be the active one
  device.set_configuration()
  return device

def get_status(device):
  bmRequestType = 0x80
  bRequest = 0x06
  wValue = 0x03  # 高字节为描述符类型（0x03），低字节为描述符索引（0x01）
  wIndex = 0x0409  # Language ID，这里是美国英语
  data_or_wLength = 0x18  # 假定的最大长度
  ret = device.ctrl_transfer(
                  bmRequestType = bmRequestType,
                  bRequest = bRequest,
                  wValue = wValue,
                  wIndex = wIndex,
                  data_or_wLength = data_or_wLength)

  # print(ret)
  res = usb.util.get_string(device, wValue, wIndex)[1:].split(' ')
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
    "ups.utility_fail": int(res[7][0]) == 1,  # 外部供电是否中断是
    "ups.battery_low": int(res[7][1]) == 1,   # 电池是否低电压 快没电了
    "ups.bypass": int(res[7][2]) == 0,        # 是否处于旁路模式
    "ups.failed": int(res[7][3]) == 1,
    "ups.type": int(res[7][4]) == 1,          # 好像永远是1
    "ups.test_in_progress": int(res[7][5]) == 1, # 是否正在测试中
    "ups.shutdown_active": int(res[7][6]) == 1,
    "ups.beeper_status": int(res[7][7]) == 1, # 是否正在蜂鸣报警
  }

def get_battery_level(device):
  bmRequestType = 0x80
  bRequest = 0x06
  wValue = 0x03f3
  wIndex = 0x0409
  data_or_wLength = 0x66
  ret = device.ctrl_transfer(
                  bmRequestType,
                  bRequest,
                  wValue =wValue,
                  wIndex = wIndex,
                  data_or_wLength = data_or_wLength)

  # print(ret)
  res = usb.util.get_string(device, wValue, wIndex)
  res = float(res.replace('BL', ''))
  return res

def ups_test(device):
  bmRequestType = 0x80
  bRequest = 0x06
  wIndex = 0x04
  wValue = 0x0
  langid = 0x0409
  ret = device.ctrl_transfer(
                  bmRequestType,
                  bRequest,
                  wValue =wValue,
                  wIndex = wIndex,
                  data_or_wLength = 0x66,
                  timeout = 1000)

  # print(ret)
  # time.sleep(1)
  try:
    usb.util.get_string(device, wIndex, langid)
  except Exception as e:
    pass
  return True

if __name__ == '__main__':
  dev = get_device()
  status = get_status(dev)
  for k, v in status.items():
    print(f'{k}: {v}')

  # res = ups_test(dev)
  # print(f'ups test res: {res}')