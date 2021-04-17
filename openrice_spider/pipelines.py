# -*- coding: utf-8 -*-
import codecs
from datetime import datetime

from scrapy.exporters import JsonItemExporter

class OpenriceRestaurantPipeline(object):
    def __init__(self):
        super().__init__()
        file_name_prefix = 'restaurant_data'
        spider_date = datetime.now().strftime('%Y%m%d')
        start_time = datetime.today().strftime("%H%M")
        file_name = "_".join([file_name_prefix, str(spider_date), str(start_time)])
        self.file = codecs.open(filename="{}.json".format(file_name), mode="wb")
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()
        self.shorten_url_list = set()

    def process_item(self, item, spider):
        if item['shorten_url'] in self.shorten_url_list:
            pass
        else:
            self.shorten_url_list.add(item['shorten_url'])
            self.exporter.export_item(item)
            print("\n**** Scrapped: " + str(len(self.shorten_url_list)) + " restaurant ****")
            print (item)

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()