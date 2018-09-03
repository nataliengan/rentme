# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider, Spider, Request, Rule
from scrapy.linkextractors import LinkExtractor
from rentspider.items import RoomItem 

class RoomsSpider(CrawlSpider):
    name = 'rooms'
    allowed_domains = ['vancouver.craigslist.ca']
    start_urls = ['http://https://vancouver.craigslist.ca/search/roo?/']
    rules = (
    	Rule(
    		LinkExtractor(allow=(), restrict_xpaths=('//a[@class="result-title hdrlnk"]')),
            follow=True, 
            callback='parse'
        ),
    	Rule(
    		LinkExtractor(allow=(), restrict_xpaths=('//a[contains(@class, "button next")]')),
            follow=True, 
            callback='parse'
        )
    )

    def parse(self, response):
        pass
