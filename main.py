from apscheduler.schedulers.blocking import BlockingScheduler
from prometheus_client import CollectorRegistry, Counter, Gauge, push_to_gateway
from datetime import datetime
from config import getConfig
from ups_connect import get_device, get_status
import subprocess

def job():
    config = getConfig()

    for device in config.devices:
        try:
            # dev = get_device(device['vendor_id'], device['product_id'])
            dev = get_device()
            status = get_status(dev)

            # status = {
            #     "input.voltage": 1,
            #     "input.voltage_fault": 1,
            #     "input.freqency": 1,
            #     "output.voltage": 1,
            #     "battery.voltage": 1,
            #     "battery.level": 1,
            #     "ups.load": 1,
            #     "ups.temperature": 1,
            #     "ups.utility_fail": 1,  # 外部供电是否中断是
            #     "ups.battery_low": 1,   # 电池是否低电压 快没电了
            #     "ups.bypass": 1,        # 是否处于旁路模式
            #     "ups.failed": 1,
            #     "ups.type": 1,          # 好像永远是1
            #     "ups.test_in_progress": 1,  # 是否正在测试中
            #     "ups.shutdown_active": 1,
            #     "ups.beeper_status": 1,  # 是否正在蜂鸣报警
            # }

            push(status, device)
            if status['battery.level'] < 10:
                for host in device['hosts']:
                    halt(host)
        except Exception as e:
            print(e)

def push(status: dict, device: dict):
    config = getConfig()
    registry = CollectorRegistry()
    for k, v in status.items():
        g = Gauge(k.replace('.', '_'), k, ['device'], registry=registry)
        g.labels(device=device['label']).set(v)
    push_to_gateway(config.pushgateway['target'], job=config.pushgateway['job'], registry=registry)
    print(datetime.now(), device['label'], status)


def halt(host):
    command = '' if host['password'] is None else 'sshpass -p "{password}" '
    command += 'ssh {username}@{ip} sudo shutdown -h now'
    print(command.format(**host))
    # subprocess.run(command, shell=True, check=True)

def main():
    sched = BlockingScheduler()
    sched.add_job(job, 'interval', seconds=15, id='ups_job')
    sched.start() 

if __name__ == '__main__':
    main()
