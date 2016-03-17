#OrangeScan
##依赖
```
pip3 install -r requirements.txt
pip install redis
apt-get install redis-server或者brew install redis
```
##配置

修改app/tool/config.py和app/config.py中的base_dir

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