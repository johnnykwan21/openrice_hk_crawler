# openrice_hk_crawler
Scraping restaurant data from [OpenRice HK](https://www.openrice.com/zh/hongkong) using Scrapy. 

## Installation of libraries
``` bash
$ pip install -r requirements.txt
```

## Example usage

``` bash
$ scrapy crawl openrice_spider
``` 

## Output

``` bash
Full site scrapping data will be output in JSON with the following format:
restaurant_data_{spider date}_{spider start time}
e.g. restaurant_data_20210417_1942
``` 
