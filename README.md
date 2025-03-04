字节跳动青训营分布式爬虫项目
此爬虫项目基于 Scrapy 框架，利用 Redis 进行任务状态管理和代理 IP 存储，结合 HDFS 存储种子 URL，
实现从(https://quotes.toscrape.com/)网页抓取名言和作者信息，并具备代理 IP 验证、Redis 连接测试等功能

scrapy爬虫版本：2.6.3
hadoop版本：3.3.0
flink版本：1.13.6
redis版本：3.2.12

运行步骤
1 start-all.sh启动hadoop
2 进入flink文件夹./bin/yarn-session.sh -n 2 -tm 1024 -s 2启动flink
3 sudo systemctl status redis启动redis
4 进入项目根目录python3 init_redis_queue.py初始化redis队列
5 python3 run_spiders.py 

