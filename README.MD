#OrangeScan

![](https://raw.githubusercontent.com/0xbug/OrangeScan/master/demo.gif)


##依赖
```
pip3 install -r requirements.txt
pip2 install redis
apt-get install redis-server或者brew install redis
```

##启动
```
redis-server
python3 run.py 80
```
##Tips:
 - popclip
![ ](http://7xod3k.com1.z0.glb.clouddn.com/eucmgflkkpqgetysszptqrtgxblwapho)

 - Alfred 设置

![ ](http://7xod3k.com1.z0.glb.clouddn.com/dwfrsoqudcclrucdaqtvikovuzkejvfe)

##常见问题

 - 无法解析域名

```
/etc/init.d/networking restart
```
 - 数据存储问题

 由于数据存储在Redis中,请安全启动Redis,并定时备份
 - 其他问题?

 请提交到Issues,或乌云社区留言
