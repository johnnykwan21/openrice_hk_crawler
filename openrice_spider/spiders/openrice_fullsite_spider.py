'''
Run with $scrapy crawl openrice_spider
'''

# -*- coding: utf-8 -*-
import scrapy
import re
import json
from datetime import date
from ..items import OpenriceItem

class RiceSpider(scrapy.Spider):
    name = 'openrice_spider'
    allowed_domains = ['openrice.com']
    start_urls = ['https://www.openrice.com/zh/hongkong/restaurants']
    base_url = 'https://www.openrice.com'

    api_url_prefix = '/api/pois?uiLang=zh&uiCity=hongkong&'
    api_url_suffix = '&page=1'

    district_id_list = [] # 地區
    district_id_to_exclude = ['districtId=1999', 'districtId=2999', 'districtId=3999', 'districtId=4999']
    food_id_list = []  # 食品 / 餐廳類型 (sub-cat + cat-group) & 菜式 (cuisine)
    price_range_id_list = list(range(1, 6))
    sort_method_list = ['ConsumeAsc', 'ConsumeDesc']

    id_regex = '(?<=data-param=")(.*)(?=. data-toggle)'
    totalpage_limitation = 17

    # Get district ids (districtId)
    def parse(self, response):
        for district in response.css('#or-route-sr1-filters-landmark-tab-district > section > div > div > div > div > div.btn'):
            district_id = re.search(self.id_regex, district.get()).group()

            if district_id not in self.district_id_list and district_id not in self.district_id_to_exclude:
                self.district_id_list.append(district_id)
        yield from self.parse_food_sub_cat_ids(response)

    # Get food sub-category ids (amenityId, dishId)
    def parse_food_sub_cat_ids(self, response):
        category_response = response.css('#or-route-sr1-filters-dish > div.modal-dialog > div > div.modal-body.or-scrollbar > section.or-section-container > div > div')

        for sub_category_id in category_response.css('div > div.flex-wrap.js-flex-wrap > div.btn'):
            sub_category_id = re.search(self.id_regex, sub_category_id.get()).group()
            if sub_category_id not in self.food_id_list and 'categoryGroupId' not in sub_category_id:
                self.food_id_list.append(sub_category_id)

        # Get food category without sub-category
        for category_id in category_response.css('fieldset'):
            category_id = re.search(self.id_regex, category_id.get()).group()
            if category_id not in self.food_id_list:
                self.food_id_list.append(category_id)

        yield from self.parse_cuisine_ids(response)

    def parse_cuisine_ids(self, response):
        cuisine_response = response.css('#or-route-sr1-filters-cuisine > div.modal-dialog > div > div.modal-body.or-scrollbar > section.or-section-container > div > div')
        # Get all cuisine ids (cuisineId)
        for cuisine_id in cuisine_response.css('div > div.flex-wrap.js-flex-wrap > div.btn'):
            cuisine_id = re.search(self.id_regex, cuisine_id.get()).group()

            if cuisine_id not in self.food_id_list and 'categoryGroupId' not in cuisine_id:
                self.food_id_list.append(cuisine_id)

        # Get the the remaining cuisine-group ids
        for cuisine_groupid in cuisine_response.css('fieldset'):
            cuisine_groupid = re.search(self.id_regex, cuisine_groupid.get()).group()
            if cuisine_groupid not in self.food_id_list:
                self.food_id_list.append(cuisine_groupid)

        yield from self.search_with_food_cat()

    # Level 1 Query (Search by Food Cat)
    def search_with_food_cat(self):
        for food_cat in self.food_id_list:
            url = ''.join((self.base_url, self.api_url_prefix, '&', str(food_cat),
                           '&sortBy=', str(self.sort_method_list[0]), self.api_url_suffix))
            yield scrapy.Request(url, callback=self.total_page_checker,
                                 meta={'food_cat': food_cat, 'query_level': 1})

    def total_page_checker(self, response):
        data = json.loads(response.text)
        totalPage = data['totalPage']
        query_level = response.meta['query_level']

        # Check if level 1 query excessed query limit -> query_level: 2
        if query_level == 1:

            if totalPage == self.totalpage_limitation:
                food_cat = response.meta['food_cat']
                yield from self.search_with_food_cat_and_district(food_cat)
            else:
                yield from self.parse_res_url(response)

        # Check if level 2 query excessed query limit -> query_level: 3
        if query_level == 2:
            if totalPage == self.totalpage_limitation:
                food_cat = response.meta['food_cat']
                district_id = response.meta['district_id']
                yield from self.search_with_and_food_cat_and_district_price_range(food_cat, district_id)
            else:
                yield from self.parse_res_url(response)

    # Level 2 Query (Search by Food Cat, District)
    def search_with_food_cat_and_district(self, food_cat):
        for district_id in self.district_id_list:
            url = ''.join(( self.base_url, self.api_url_prefix, '&', str(food_cat), '&', str(district_id),
                    '&sortBy=', str(self.sort_method_list[0]), self.api_url_suffix ))
            yield scrapy.Request(url, callback=self.total_page_checker,
                                 meta={'food_cat': food_cat, 'district_id': district_id, 'query_level': 2})

    # Level 3 Query (Search by Food Cat, District, Price Range)
    def search_with_and_food_cat_and_district_price_range(self, food_cat, district_id):
        for price_range in self.price_range_id_list:
            url = ''.join((self.base_url, self.api_url_prefix, '&', str(food_cat), '&', str(district_id),
                    '&', str(price_range), '&sortBy=', str(self.sort_method_list[0]), self.api_url_suffix))
            yield scrapy.Request(url, callback=self.parse_res_url)

    # Get every restaurant data in every page (Breakdown by district, food-category, price-range, sort-method)
    def parse_res_url(self, response):
        data = json.loads(response.text)
        totalPage = data['totalPage']
        results = data['searchResult']['paginationResult']['results']
        result_size = len(results)
        res_data = OpenriceItem()
        # Check if any result in response page
        if result_size != 0:
            # Get data of each restaurant
            for res in results:
                res_data['spider_date'] = date.today().strftime("%Y/%m/%d")
                res_data['region_name'] = res['regionName']
                res_data['district_id'] = res['district']['districtId']
                res_data['district_name'] = res['district']['name']

                try:
                    res_uid = res['poiId']
                except KeyError:
                    res_uid = None
                res_data['res_uid'] = res['poiId']
                res_data['res_name'] = res['nameUI']
                res_data['shorten_url'] = res['shortenUrl']

                try:
                    chi_address = res['address'].strip()
                except KeyError:
                    chi_address = None
                res_data['chi_address'] = chi_address

                tel_no_list = []
                for tel_no in res['phones']:
                    tel_no_list.append(tel_no.replace(" ", "").replace("-", ""))
                tel_no = ",".join(tel_no_list)
                res_data['tel_no'] = tel_no

                food_type_list = []
                for food_type in res['categories']:
                    if food_type['categoryTypeId'] == 1:
                        res_data['primary_food_type'] = food_type['callName']
                    else:
                        food_type_list.append(food_type['callName'])
                secondary_food_type = ",".join(food_type_list)
                res_data['secondary_food_type'] = secondary_food_type
                
                res_data['price_range'] = res['priceUI']

                try:
                    payment_method = str(res['paymentIds']).replace('[', '').replace(']', '')
                except KeyError:
                    payment_method = None
                res_data['payment_method'] = payment_method

                res_data['maplatitude'] = res['mapLatitude']
                res_data['maplongitude'] = res['mapLongitude']

                try:
                    opensince = res['openSince']
                except KeyError:
                    opensince = None
                res_data['opensince'] = opensince


                if res['moveToId'] != 0:
                    isrelocated = True
                else:
                    isrelocated = False
                res_data['is_relocated'] = isrelocated


                res_data['res_status'] = res['statusText']
                res_data['score_smile'] = int(res['scoreSmile'])
                res_data['score_cry'] = int(res['scoreCry'])

                try:
                    overall_score = res['scoreOverall']
                except KeyError:
                    overall_score = None
                res_data['overall_score'] = overall_score

                try:
                    reviewcount = res['reviewCount']
                except KeyError:
                    reviewcount = None
                res_data['review_count'] = reviewcount

                try:
                    bookmarkedUserCount = res['bookmarkedUserCount']
                except KeyError:
                    bookmarkedUserCount = None
                res_data['bookmarked_user_count'] = bookmarkedUserCount

                try:
                    is_takeaway_enabled = res['takeAwayInfo']['isEnableRemark']
                except KeyError:
                    is_takeaway_enabled = None
                res_data['is_takeaway_enabled'] = is_takeaway_enabled

                try:
                    earliest_takeaway = res['takeAwayInfo']['infoDisplay']
                except KeyError:
                    earliest_takeaway = None
                res_data['earliest_takeaway'] = earliest_takeaway

                try:
                    if res['tmBookingWidget']['isBookingDisabled'] == False:
                        is_booking_enabled = True
                    elif res['tmBookingWidget']['isBookingDisabled'] == True:
                        is_booking_enabled = False
                except KeyError:
                    is_booking_enabled = None
                res_data['is_booking_enabled'] = is_booking_enabled

                bookingOffers_list = []
                try:
                    for bookingOffers in res['bookingOffers']:
                        bookingOffers_list.append(bookingOffers['title'])
                    bookingoffers = ",".join(bookingOffers_list)
                except KeyError:
                    bookingoffers = None
                res_data['booking_offers'] = bookingoffers

                yield res_data
                
        else:
            pass

        # Page pagination
        try:
            next_page_no = data['desktopPagination']['next']['page']
            next_page_url_prefix = re.match('(^(.*?)(?=&page=))', response.url).group(1)
            next_page_url = ''.join(( next_page_url_prefix, '&page=', str(next_page_no) ))
            yield scrapy.Request(next_page_url, callback=self.parse_res_url)
        except KeyError:
            pass

        # Loop the page again in descending order while totalpage excessed limit
        if totalPage == self.totalpage_limitation and self.sort_method_list[0] in response.url:
            url = response.url.replace(self.sort_method_list[0], self.sort_method_list[1])
            yield scrapy.Request(url, callback=self.parse_res_url)
