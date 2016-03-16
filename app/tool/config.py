#!/usr/bin/python
# -*- coding: utf-8 -*-

import redis

queue_db = redis.Redis(host='localhost', port=6379, db=0)
domain_db = redis.Redis(host='localhost', port=6379, db=1)
info_db = redis.Redis(host='localhost', port=6379, db=2)
log_db = redis.Redis(host='localhost', port=6379, db=3)

scanpy_dir = 'subDomains-Xscan/'
log_dir = '../log'

