#!/usr/bin/python3
# -*- coding: utf-8 -*-

from app import config
import os
import time

def getInfo():
    for domain in config.log_db.keys():
        if config.log_db.get(domain)==0:
            os.system('python /root/scan/info.py %s&' % str(domain,'utf-8'))
            print ('getInfoing of %s......' % str(domain,'utf-8'))
        elif not config.info_db.exists(domain):
            config.log_db.set(domain, 0)
            os.system('python /root/scan/info.py %s&' % str(domain,'utf-8'))
            print ('getInfoing of %s......' % str(domain,'utf-8'))
            time.sleep(2)
        else:
            pass


def getSubdomain():
    for task in config.queue_db.keys():
        if not config.log_db.exists(task):
            config.log_db.set(task, -1)
        elif config.log_db.get(task) == '-1':
            if int(os.popen('ps -h|grep subDomains-Xscan|wc -l').read()) < 6:
                os.system('python /usr/local/share/subDomains-Xscan/run.py %s&' % str(task,'utf-8'))
            else:
                pass
        elif config.log_db.get(task) == '0':
            config.queue_db.delete(task)
        elif config.log_db.get(task) == '1':
            config.queue_db.delete(task)
        else:
            pass


if __name__ == '__main__':
    # while config.queue_db.dbsize() > 0:
    #     getSubdomain()
    getInfo()
    # if config.info_dev_db.dbsize() >= config.info_db.dbsize():
    #     config.info_db.flushdb()

    # log_db -1 = 未扫描过子域名 0 = 扫描过子域名但未扫描详细信息 1 = 扫描过详细信息
