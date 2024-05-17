from apscheduler.schedulers.blocking import BlockingScheduler
from prometheus_client import CollectorRegistry, Counter, Gauge, push_to_gateway
from datetime import datetime
from config import getConfig
from ups_connect import get_device, get_status
import subprocess
import logging


def job():
    config = getConfig()

    for device in config.devices:
        try:
            dev = get_device()
            status = get_status(dev)
            push(status, device)
            if status['ups.utility_fail'] > 0 and status['battery.level'] < 35:
                for host in device['hosts']:
                    halt(host)
        except Exception as e:
            print(e)


def push(status: dict, device: dict):
    config = getConfig()
    registry = CollectorRegistry()
    for k, v in status.items():
        g = Gauge(k.replace('.', '_'), k, registry=registry)
        g.set(v)
    push_to_gateway(
        config.pushgateway['target'], job=config.pushgateway['job']+'_'+device['label'], registry=registry)
    print(datetime.now(), device['label'], status)


def halt(host):
    command = '' if host['password'] is None else 'sshpass -p "{password}" '
    command += 'ssh {username}@{ip} sudo shutdown -h now'.format(**host)
    logging.warning(command)
    subprocess.run(command, shell=True, check=True)


def main():
    # logging.basicConfig(filename='ups.log', level=logging.DEBUG, format='%(asctime)s %(message)s')
    logging.info('start')
    
    sched = BlockingScheduler()
    sched.add_job(job, 'interval', seconds=15, id='ups_job')
    sched.start()


if __name__ == '__main__':
    main()
