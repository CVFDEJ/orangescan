#!/usr/bin/python
# -*- coding: utf-8 -*-

from config import info_db

for each in info_db.keys():
    for i in info_db.smembers(each):
        subdomain = i.split(':')[0]
        with open('%s/bbscan.txt', 'a+') as f:
            f.writelines(subdomain + '\n')
