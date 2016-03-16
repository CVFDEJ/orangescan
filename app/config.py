# coding=utf-8
import redis

queue_db = redis.Redis(host='localhost', port=6379, db=0)
domain_db = redis.Redis(host='localhost', port=6379, db=1)
info_db = redis.Redis(host='localhost', port=6379, db=2)
log_db = redis.Redis(host='localhost', port=6379, db=3)
# log_db -1 = 未扫描过子域名 0 = 扫描过子域名但未扫描详细信息 1 = 扫描过详细信息

base_dir = '/Users/orange/Dropbox/OrangeScan/OrangeScan/app'
scan_dir = '%s/tool/' % base_dir
scanpy = '%s/tool/scan.py' % base_dir
infopy = '%s/tool/info.py' % base_dir
log_dir = '%s/log' % base_dir
