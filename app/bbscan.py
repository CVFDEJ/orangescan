#!/usr/bin/python3
# -*- coding: utf-8 -*-

from config import info_db
import os

os.system('rm bbscan.txt')

for each in info_db.keys():
    for i in info_db.smembers(each):
        subdomain = i.split(':')[0]
        with open('bbscan.txt', 'a+') as f:
            f.writelines(subdomain + '\n')
