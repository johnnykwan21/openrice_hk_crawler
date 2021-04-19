# openrice_hk_crawler
Scraping restaurant data from [OpenRice HK](https://www.openrice.com/zh/hongkong) using Scrapy, for later on F&B analysis project

## Installation of libraries
``` bash
$ pip install -r requirements.txt
```

## Example usage

``` bash
$ scrapy crawl openrice_spider
``` 

## Output
Full site scrapping data will be output in JSON with the following format:

``` bash
restaurant_data_{spider date}_{spider start time}
e.g. restaurant_data_20210417_1942
``` 

## Proxy configuration
To Enable proxies rotation, simply unhash the following row in setting.py with a proxy_list file in txt format

``` bash
# # Proxy List
# DOWNLOADER_MIDDLEWARES = {
#     'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
#     'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
# }
# ROTATING_PROXY_LIST_PATH = 'proxy_list.txt'
``` 
