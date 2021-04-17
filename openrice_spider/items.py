# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst

class OpenriceItemLoader(ItemLoader):
    default_output_processor = TakeFirst()

class OpenriceItem(Item):
    res_uid = Field()
    res_name = Field()
    region_name = Field()
    district_id = Field()
    district_name = Field()
    shorten_url = Field()
    chi_address = Field()
    tel_no = Field()

    primary_food_type = Field()
    secondary_food_type = Field()
    price_range = Field()
    payment_method = Field()

    maplatitude = Field()
    maplongitude = Field()
    opensince = Field()
    is_relocated = Field()
    res_status = Field()

    score_smile = Field()
    score_cry = Field()
    overall_score = Field()
    review_count = Field()
    bookmarked_user_count = Field()

    is_takeaway_enabled = Field()
    earliest_takeaway = Field()
    is_booking_enabled = Field()
    booking_offers = Field()

    spider_date = Field()