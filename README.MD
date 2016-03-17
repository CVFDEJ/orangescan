#OrangeScan

##依赖
```
pip3 install -r requirements.txt
pip install redis
apt-get install redis-server或者brew install redis
```
##配置

因为某接口备份dump.rdb,需要配置app/config.py中的redis_dir

##启动
```
redis-server
python3 run.py 80
```
##常见问题

 - 无法解析域名

```
/etc/init.d/networking restart
```
 - 数据存储问题
 
 由于数据存储在Redis中,请安全启动Redis,并定时备份