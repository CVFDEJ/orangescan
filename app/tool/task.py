#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import time

from app import config


def getInfo():
    for domain in config.log_db.keys():
        if config.log_db.get(domain)==0:
            os.system('python %s %s&' % (config.infopy, str(domain, 'utf-8')))
            print ('getInfoing of %s......' % str(domain,'utf-8'))
        elif not config.info_db.exists(domain):
            config.log_db.set(domain, 0)
            os.system('python %s %s&' % (config.infopy, str(domain, 'utf-8')))
            print ('getInfoing of %s......' % str(domain,'utf-8'))
            time.sleep(2)
        else:
            pass


def getSubdomain():
    for task in config.queue_db.keys():
        if not config.log_db.exists(task):
            config.log_db.set(task, -1)
        elif config.log_db.get(task) == '-1':
            if int(os.popen('ps -h|grep scan.py|wc -l').read()) < 6:
                os.system('python %s %s&' % (config.scanpy, str(task, 'utf-8')))
            else:
                pass
        elif config.log_db.get(task) == '0':
            config.queue_db.delete(task)
        elif config.log_db.get(task) == '1':
            config.queue_db.delete(task)
        else:
            pass


if __name__ == '__main__':
    getInfo()
