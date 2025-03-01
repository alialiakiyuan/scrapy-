# url_distribution.py
import random

def random_distribution(urls, num_spiders):
    spider_tasks = [[] for _ in range(num_spiders)]
    for url in urls:
        spider_id = random.randint(0, num_spiders - 1)
        spider_tasks[spider_id].append(url)
    return spider_tasks

def round_robin_distribution(urls, num_spiders):
    spider_tasks = [[] for _ in range(num_spiders)]
    index = 0
    for url in urls:
        spider_tasks[index % num_spiders].append(url)
        index += 1
    return spider_tasks