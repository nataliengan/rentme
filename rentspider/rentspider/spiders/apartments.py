# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider, Request, Rule
from scrapy.linkextractors import LinkExtractor
from rentspider.items import ApartmentItem 

class ApartmentsSpider(CrawlSpider):
    name = 'apartments'
    allowed_domains = ['vancouver.craigslist.ca']
    start_urls = [
        'https://vancouver.craigslist.ca/search/bnc/apa?',
        'https://vancouver.craigslist.ca/search/rds/apa?',
        'https://vancouver.craigslist.ca/search/nvn/apa?',
        'https://vancouver.craigslist.ca/search/rch/apa?',
        'https://vancouver.craigslist.ca/search/pml/apa?',
        'https://vancouver.craigslist.ca/search/van/apa?'
    ]
    rules = (
    	Rule(
    		LinkExtractor(allow=(), restrict_xpaths=('//a[@class="result-title hdrlnk"]')),
            follow=True, 
            callback='parse_item'
        ),
    	Rule(
    		LinkExtractor(allow=(), restrict_xpaths=('//a[@class="button next"]')),
            follow=True, 
            callback='parse'
        )
    )

    def parse_item(self, response):
        item = ApartmentItem()

        # item['url'] = response.request.url
        item['price'] = response.xpath('//span/span[@class="price"]/text()').extract_first()
        item['attributes'] = response.xpath('//p[@class="attrgroup"]/span/b/text()').extract()
        item['subattributes'] = response.xpath('//p[@class="attrgroup"]/span/text()').extract()
        item['neighborhood'] = response.xpath('//span/small/text()').extract_first()
        item['location'] = response.xpath('//a[contains(@href, "https://maps.google.com/")]/@href').extract_first()

        return item
