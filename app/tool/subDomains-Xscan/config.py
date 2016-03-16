import redis

base_dir = '/usr/local/share/subDomains-Xscan/'
domain_db = redis.Redis(host='localhost', port=6379, db=0)
ip_db = redis.Redis(host='localhost', port=6379, db=4)
queue_db = redis.Redis(host='localhost', port=6379, db=5)
log_db = redis.Redis(host='localhost', port=6379, db=7)
test_db = redis.Redis(host='localhost', port=6379, db=8)


dns_servers = []

if not queue_db.exists('domain:new:totals'):
    queue_db.set('domain:new:totals', 0)
