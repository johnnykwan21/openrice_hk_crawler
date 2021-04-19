# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class OpenriceItem(scrapy.Item):
    spider_date = scrapy.Field()

    res_uid = scrapy.Field()
    res_name = scrapy.Field()
    region_name = scrapy.Field()
    district_id = scrapy.Field()
    district_name = scrapy.Field()
    shorten_url = scrapy.Field()
    chi_address = scrapy.Field()
    tel_no = scrapy.Field()

    primary_food_type = scrapy.Field()
    secondary_food_type = scrapy.Field()
    price_range = scrapy.Field()
    payment_method = scrapy.Field()

    maplatitude = scrapy.Field()
    maplongitude = scrapy.Field()
    opensince = scrapy.Field()
    is_relocated = scrapy.Field()
    res_status = scrapy.Field()

    score_smile = scrapy.Field()
    score_cry = scrapy.Field()
    overall_score = scrapy.Field()
    review_count = scrapy.Field()
    bookmarked_user_count = scrapy.Field()

    is_takeaway_enabled = scrapy.Field()
    earliest_takeaway = scrapy.Field()
    is_booking_enabled = scrapy.Field()
    booking_offers = scrapy.Field()
