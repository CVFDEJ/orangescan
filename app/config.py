# coding=utf-8
import os

import redis

queue_db = redis.Redis(host='localhost', port=6379, db=0)
domain_db = redis.Redis(host='localhost', port=6379, db=1)
info_db = redis.Redis(host='localhost', port=6379, db=2)
log_db = redis.Redis(host='localhost', port=6379, db=3)

base_dir = os.getcwd()
tool_dir = '%s/app/tool/' % base_dir
log_dir = '%s/app/tool/log' % base_dir
scan_py = '%s/app/tool/scan.py' % base_dir
info_py = '%s/app/tool/info.py' % base_dir
redis_dir = ''
